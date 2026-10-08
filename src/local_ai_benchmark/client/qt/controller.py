"""Qt state adapter. Providers, authentication and persistence remain Python services."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen, urlretrieve

from PySide6.QtCore import QObject, QTimer, Signal

from ...engine import BenchmarkEngine
from ...providers import LlamaCppProvider, OllamaProvider, ProviderRouter
from ..auth import (
    AccountService,
    AuthError,
    AuthUnavailable,
    PasswordChangeRequired,
    clear_cached_session,
    machine_fingerprint,
    save_service_url,
)
from ..core import ClientRunRecord, generate_run_id
from ..hardware import detect_hardware
from ..storage import LocalResultStore
from .fit import AssessmentMixin


def download_name(url: str) -> str:
    parsed = urlparse(url.strip())
    name = Path(unquote(parsed.path)).name
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or not name.lower().endswith(".gguf")
    ):
        raise ValueError("Use a direct HTTPS URL ending in .gguf.")
    if any(c in name for c in '<>:"/\\|?*') or name in {".gguf", ".."}:
        raise ValueError("The model URL contains an invalid file name.")
    return name


def remote_size(url: str) -> int:
    download_name(url)
    for method, headers in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        try:
            with urlopen(
                Request(url, headers=headers, method=method), timeout=15
            ) as response:
                total = response.headers.get("Content-Range", "").rsplit("/", 1)[-1]
                if total.isdigit() and int(total) > 0:
                    return int(total)
                total = response.headers.get("Content-Length", "")
                if (
                    getattr(response, "status", None) != 206
                    and total.isdigit()
                    and int(total) > 0
                ):
                    return int(total)
        except (OSError, ValueError):
            continue
    raise ValueError(
        "The server did not expose the file size. Fit cannot be estimated."
    )


def summarize(results, stopped: bool) -> tuple[dict, str]:
    generated = [r for r in results if r.error is None]
    rates = [
        r.metrics["tokens_per_second"]
        for r in generated
        if r.metrics.get("tokens_per_second") is not None
    ]
    summary = {
        "task_count": len(results),
        "generated_tasks": len(generated),
        "passed_checks": sum(r.passed is True for r in generated),
        "failed_checks": sum(r.passed is False for r in generated),
        "errors": sum(r.error is not None for r in results),
        "average_tokens_per_second": round(sum(rates) / len(rates), 3)
        if rates
        else None,
    }
    status = (
        "stopped"
        if stopped
        else "failed"
        if not generated
        else "partial"
        if summary["errors"]
        else "complete"
    )
    return summary, status


class StudioController(QObject, AssessmentMixin):
    changed = Signal(str)
    progress = Signal(int, int, object)
    notification = Signal(str, str)
    auth_changed = Signal()
    auth_feedback = Signal(str, bool)
    password_change_required = Signal()
    download_event = Signal(str, object)

    def __init__(self, base_dir: Path | None = None, parent=None):
        super().__init__(parent)
        data = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Aetherion"
        root = Path(base_dir) if base_dir else data / "results"
        self.preferences_path = (root if base_dir else data) / "studio.json"
        try:
            self.preferences = json.loads(
                self.preferences_path.read_text(encoding="utf-8")
            )
            if not isinstance(self.preferences, dict):
                self.preferences = {}
        except (OSError, ValueError):
            self.preferences = {}
        gguf = LlamaCppProvider(self.preferences.get("model_folder") or root / "models")
        provider = ProviderRouter([OllamaProvider(timeout=120), gguf])
        self.session = SimpleNamespace(
            hardware={},
            store=LocalResultStore(root / "client"),
            gguf_provider=gguf,
            provider=provider,
            engine=BenchmarkEngine(provider, root),
            results_dir=root,
        )
        self.models = {}
        self.records = self.session.store.list()
        self.recommended_model_name = None
        self.auth_session = None
        self.account_service = AccountService()
        self.busy = False
        self.status = "Ready to connect"
        self.run_status = "idle"
        self.run_summary = {}
        self.trace = []
        self.pending = set()
        self.events = queue.Queue()
        self.stop_event = threading.Event()
        self.download_stop = threading.Event()
        self.auth_epoch = 0
        self.closed = False
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._drain)
        self.poll_timer.start(40)
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.refresh_hardware)
        self.monitor_timer.setInterval(15000)
        self.license_timer = QTimer(self)
        self.license_timer.timeout.connect(self.refresh_license)
        self.license_timer.start(300000)

    def _work(self, key, function):
        if key in self.pending or self.closed:
            return False
        self.pending.add(key)
        epoch = self.auth_epoch if key in {"auth", "license"} else None

        def execute():
            try:
                self.events.put((key, True, function()))
            except Exception as exc:  # noqa: BLE001 - worker failures must cross the GUI boundary as data
                error = exc if isinstance(exc, PasswordChangeRequired) else str(exc)
                self.events.put(
                    (key, False, (epoch, error) if epoch is not None else str(error))
                )

        threading.Thread(target=execute, daemon=True, name=f"aetherion-{key}").start()
        return True

    def save_preference(self, key, value):
        self.preferences[key] = value
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.preferences_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.preferences, indent=2), encoding="utf-8")
        temporary.replace(self.preferences_path)
        self.changed.emit("preferences")

    def restore(self):
        if "logout" in self.pending:
            self.auth_feedback.emit(
                "Finishing sign out… Please try again shortly.", False
            )
            return
        epoch = self.auth_epoch
        self._work(
            "auth",
            lambda: (epoch, self.account_service.restore_cached(machine_fingerprint())),
        )

    def authenticate(self, mode, values, service_url):
        if "auth" in self.pending or "logout" in self.pending:
            self.auth_feedback.emit("Finishing the previous account request…", False)
            return
        try:
            username, password = values["username"].strip(), values["password"]
            if not username or not password:
                raise AuthError("Enter your username and password.")
            if mode == "register":
                if len(password) < 12:
                    raise AuthError("Use a password with at least 12 characters.")
                if password != values.get("confirm"):
                    raise AuthError("The password confirmation does not match.")
                if not values.get("license_key", "").strip():
                    raise AuthError("A valid license key is required.")
            elif mode == "password_change":
                new_password = values.get("new_password", "")
                if len(new_password.encode("utf-8")) < 12 or len(new_password) > 128:
                    raise AuthError(
                        "Use a new password between 12 and 128 characters and at least 12 UTF-8 bytes."
                    )
                if new_password == password:
                    raise AuthError("Choose a password different from the temporary password.")
                if new_password != values.get("confirm"):
                    raise AuthError("The new password confirmation does not match.")
            self.account_service = AccountService(save_service_url(service_url))
        except (AuthError, KeyError) as exc:
            self.auth_feedback.emit(str(exc), True)
            return
        epoch = self.auth_epoch
        service = self.account_service

        def sign_in():
            if mode == "password_change":
                new_password = values["new_password"]
                service.change_temporary_password(username, password, new_password)
                session = service.login(username, new_password, machine_fingerprint())
            elif mode == "register":
                session = service.register(
                    username,
                    password,
                    values["license_key"].strip(),
                    machine_fingerprint(),
                )
            else:
                session = service.login(username, password, machine_fingerprint())
            return epoch, session

        self._work("auth", sign_in)
        self.auth_feedback.emit("Connecting securely…", False)

    def sign_out(self):
        if self.busy or "auth" in self.pending:
            self.notification.emit(
                "Finish or stop the active operation before signing out.", "warning"
            )
            return
        self.auth_epoch += 1
        session = self.auth_session
        service = self.account_service
        self.auth_session = None
        clear_cached_session()
        self.monitor_timer.stop()
        self.auth_changed.emit()
        self._work("logout", lambda: service.logout(session))

    def refresh_license(self):
        if not self.auth_session:
            return
        epoch, session, service = (
            self.auth_epoch,
            self.auth_session,
            self.account_service,
        )

        def refresh():
            try:
                updated = (
                    service.refresh(session)
                    if session.session_token
                    else service.restore_cached(machine_fingerprint())
                )
                if updated is None:
                    raise AuthError("Session expired. Sign in again.")
                return epoch, updated
            except AuthUnavailable:
                if dt.datetime.now(dt.UTC) < session.offline_until:
                    return epoch, session
                raise AuthError("Offline access ended. Connect and sign in again.")

        self._work("license", refresh)

    def refresh_hardware(self):
        def detect():
            hardware = detect_hardware()
            if os.name == "nt":
                try:
                    import winreg

                    with winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
                    ) as key:
                        hardware["cpu"]["model"] = winreg.QueryValueEx(
                            key, "ProcessorNameString"
                        )[0].strip()
                except OSError:
                    pass
            try:
                import psutil

                hardware["cpu"]["usage_percent"] = psutil.cpu_percent(interval=0.15)
                hardware["memory"]["used_percent"] = psutil.virtual_memory().percent
            except ImportError:
                pass
            executable = shutil.which("nvidia-smi")
            if executable:
                result = subprocess.run(
                    [
                        executable,
                        "--query-gpu=memory.free,utilization.gpu",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                    creationflags=0x08000000 if os.name == "nt" else 0,
                )
                for gpu, line in zip(hardware["gpu"], result.stdout.splitlines()):
                    parts = line.split(",")
                    if len(parts) == 2:
                        try:
                            gpu["free_vram_gb"] = round(float(parts[0]) / 1024, 2)
                            gpu["usage_percent"] = float(parts[1])
                        except ValueError:
                            pass
            hardware["updated_at"] = dt.datetime.now(dt.UTC).isoformat()
            return hardware

        self._work("hardware", detect)

    def refresh_models(self):
        if self.busy:
            return
        self.busy = True
        self.status = "Discovering local models…"
        self._work("models", self.session.provider.discover)
        self.changed.emit("busy")

    def set_model_folder(self, folder):
        if self.busy or "download" in self.pending:
            return
        self.session.gguf_provider.set_models_dir(folder)
        self.save_preference("model_folder", str(folder))
        self.refresh_models()

    def run(self, name, category=None, temperature=0.0, context=4096):
        if self.busy or name not in self.models:
            return
        if (
            self.auth_session is None
            or dt.datetime.now(dt.UTC) >= self.auth_session.offline_until
        ):
            self.auth_session = None
            clear_cached_session()
            self.auth_changed.emit()
            self.auth_feedback.emit("Sign in to run a benchmark.", True)
            return
        model = self.models[name]
        fit = self.assess_model(model)
        if fit.startswith("DIRECT RUN: NO"):
            self.notification.emit(fit, "warning")
            return
        self.stop_event = threading.Event()
        stop = self.stop_event
        hardware = dict(self.session.hardware)
        self.busy = True
        self.run_status = "running"
        self.status = "Benchmark running"
        self.run_summary = {}
        self.trace = [
            f"Model: {name}\nSuite: {category or 'all tasks'}\nTemperature: {temperature} · Context: {context}\n"
        ]
        self.changed.emit("run")

        def execute():
            results = self.session.engine.run(
                name,
                category,
                temperature=temperature,
                context=context,
                progress_callback=lambda i, total, result: self.events.put(
                    ("progress", True, (i, total, result))
                ),
                stop_event=stop,
            )
            summary, status = summarize(results, self.session.engine.last_run_stopped)
            record = ClientRunRecord(
                generate_run_id(),
                name,
                str(model.details.get("digest") or name),
                model.provider,
                str(model.details.get("quantization_level") or "UNKNOWN"),
                hardware,
                summary,
                status=status,
                notes={
                    "benchmark_results_file": str(self.session.engine.last_result_path)
                    if self.session.engine.last_result_path
                    else None,
                    "stopped_by_user": self.session.engine.last_run_stopped,
                    "category": category,
                    "temperature": temperature,
                    "context": context,
                },
            )
            self.session.store.save(record)
            return summary, status

        self._work("run", execute)

    def stop(self):
        self.stop_event.set()
        self.status = "Stopping after the active generation…"
        self.changed.emit("busy")

    def preflight(self, url):
        self._work(
            "preflight",
            lambda: self.assess_download_hardware(
                remote_size(url), self.session.hardware
            ),
        )

    def download(self, url):
        if "download" in self.pending:
            return
        try:
            filename = download_name(url)
        except ValueError as exc:
            self.download_event.emit("error", str(exc))
            return
        target = self.session.gguf_provider.models_dir / filename
        if target.exists():
            self.download_event.emit(
                "error", "This file already exists. Choose another model or folder."
            )
            return
        self.download_stop = threading.Event()
        stop = self.download_stop

        def transfer():
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_suffix(".gguf.part")
            try:
                with (
                    urlopen(
                        Request(url, headers={"User-Agent": "Aetherion-Studio/0.2"}),
                        timeout=30,
                    ) as response,
                    temporary.open("wb") as output,
                ):
                    total, downloaded = (
                        int(response.headers.get("Content-Length") or 0),
                        0,
                    )
                    while chunk := response.read(1024 * 1024):
                        if stop.is_set():
                            raise InterruptedError("Download cancelled.")
                        output.write(chunk)
                        downloaded += len(chunk)
                        self.events.put(
                            ("download_progress", True, (downloaded, total, filename))
                        )
                    if total and downloaded != total:
                        raise OSError("Incomplete download. Please retry.")
                temporary.replace(target)
                return str(target)
            finally:
                temporary.unlink(missing_ok=True)

        self._work("download", transfer)
        self.download_event.emit("started", filename)

    def install_runtime(self, runtime):
        def install():
            if runtime == "Ollama":
                target = (
                    Path.home()
                    / "Downloads"
                    / "Aetherion-Installers"
                    / "OllamaSetup.exe"
                )
                target.parent.mkdir(parents=True, exist_ok=True)
                urlretrieve("https://ollama.com/download/OllamaSetup.exe", target)
                if os.name == "nt":
                    os.startfile(target)
                return (
                    "Ollama installer opened. Finish installation, then refresh models."
                )
            if getattr(sys, "frozen", False):
                raise RuntimeError(
                    "GGUF inference needs a build with llama-cpp-python bundled. Run from source with the llama extra or use Ollama in this build."
                )
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "llama-cpp-python"],
                check=True,
                creationflags=0x08000000 if os.name == "nt" else 0,
            )
            importlib.invalidate_caches()
            return "GGUF runtime installed. Refresh your models."

        self._work("install", install)
        self.notification.emit(f"Preparing {runtime}…", "info")

    def _drain(self):
        if self.closed:
            return
        for _ in range(60):
            try:
                key, ok, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if key not in {"progress", "download_progress"}:
                self.pending.discard(key)
            if key in {"auth", "license"}:
                if payload[0] != self.auth_epoch:
                    continue
                if not ok:
                    if key == "license":
                        self.stop_event.set()
                        self.auth_session = None
                        clear_cached_session()
                        self.auth_changed.emit()
                    if key == "auth" and isinstance(payload[1], PasswordChangeRequired):
                        self.auth_feedback.emit(str(payload[1]), False)
                        self.password_change_required.emit()
                    else:
                        self.auth_feedback.emit(str(payload[1]), True)
                elif payload[0] == self.auth_epoch:
                    self.auth_session = payload[1]
                    self.auth_changed.emit()
                    self.auth_feedback.emit(
                        "Sign in or create an account to continue."
                        if payload[1] is None
                        else "Connected",
                        False,
                    )
                continue
            if key == "hardware":
                if ok:
                    self.session.hardware = payload
                    self.recommended_model_name = next(
                        (
                            m.name
                            for m in sorted(
                                self.models.values(), key=self.model_recommendation_key
                            )
                            if self.assess_model(m).startswith("DIRECT RUN: YES")
                        ),
                        None,
                    )
                    self.changed.emit("hardware")
                continue
            if key == "progress":
                i, total, result = payload
                self.trace.append(
                    f"[{i}/{total}] {result.task} · {'ERROR' if result.error else 'PASS' if result.passed else 'FAIL'}\n{result.error or result.response}\n"
                )
                self.progress.emit(i, total, result)
                continue
            if key in {"preflight", "download", "download_progress"}:
                self.download_event.emit(key if ok else "error", payload)
                if key == "download" and ok:
                    self.refresh_models()
                continue
            if key in {"models", "run"}:
                self.busy = False
                if not ok:
                    self.status = "Operation failed"
                    if key == "run":
                        self.run_status = "failed"
                        self.trace.append(payload)
                    self.notification.emit(payload, "error")
                elif key == "models":
                    ordered = sorted(payload, key=self.model_recommendation_key)
                    self.models = {m.name: m for m in ordered}
                    # A recommendation is only made for a model that passes the fit heuristic.
                    self.recommended_model_name = next(
                        (
                            m.name
                            for m in ordered
                            if self.assess_model(m).startswith("DIRECT RUN: YES")
                        ),
                        None,
                    )
                    self.status = (
                        f"{len(ordered)} local models detected"
                        if ordered
                        else "No local models detected"
                    )
                else:
                    self.run_summary, self.run_status = payload
                    self.status = f"Benchmark {self.run_status}"
                    self.records = self.session.store.list()
                    self.notification.emit(
                        self.status,
                        "success" if self.run_status == "complete" else "warning",
                    )
                self.changed.emit(key)
            elif key == "install":
                self.notification.emit(payload, "success" if ok else "error")
                self.changed.emit("runtimes")
            elif key == "logout":
                self.auth_feedback.emit(
                    "You have signed out. Sign in to continue.", False
                )

    def close(self):
        self.closed = True
        self.stop_event.set()
        self.download_stop.set()
        self.poll_timer.stop()
        self.monitor_timer.stop()
        self.license_timer.stop()
