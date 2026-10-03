from __future__ import annotations

import importlib.util
import datetime as dt
import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen, urlretrieve
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from local_ai_benchmark.client.core import ClientRunRecord, generate_run_id
    from local_ai_benchmark.client.hardware import detect_hardware
    from local_ai_benchmark.client.auth import AccountService, AuthError, AuthSession, AuthUnavailable, clear_cached_session, get_service_url, machine_fingerprint, save_service_url
    from local_ai_benchmark.client.storage import LocalResultStore
    from local_ai_benchmark.engine import BenchmarkEngine
    from local_ai_benchmark.models import BenchmarkResult, ModelInfo
    from local_ai_benchmark.providers import LlamaCppProvider, OllamaProvider, ProviderRouter
    from local_ai_benchmark.tasks import TASKS
    from local_ai_benchmark.client.theme import COLORS, FONTS, configure_ttk
else:
    from .core import ClientRunRecord, generate_run_id
    from .hardware import detect_hardware
    from .auth import AccountService, AuthError, AuthSession, AuthUnavailable, clear_cached_session, get_service_url, machine_fingerprint, save_service_url
    from .storage import LocalResultStore
    from ..engine import BenchmarkEngine
    from ..models import BenchmarkResult, ModelInfo
    from ..providers import LlamaCppProvider, OllamaProvider, ProviderRouter
    from ..tasks import TASKS
    from .theme import COLORS, FONTS, configure_ttk


TASK_SUITE_DESCRIPTIONS = {
    "All tasks": "Runs general, coding, math, JSON, and Spanish-language checks.",
    "general": "Checks concise factual explanation and instruction following.",
    "coding": "Checks whether the model returns valid Python code for a concrete task.",
    "math": "Checks exact arithmetic and resistance to unnecessary explanation.",
    "json": "Checks strict JSON formatting and schema compliance.",
    "spanish": "Checks Spanish comprehension and concise instruction following.",
}


MODEL_DOWNLOAD_CATALOG = {
    "Qwen2.5 0.5B · Q4_K_M · ultra-light": "https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf?download=true",
    "TinyLlama 1.1B · Q4_K_M · lightweight": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true",
    "Gemma 2 2B · Q4_K_M · compact": "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf?download=true",
    "Qwen2.5 3B · Q4_K_M · general": "https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf?download=true",
    "Llama 3.2 3B · Q4_K_M · popular": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf?download=true",
    "Phi-3.5 Mini · Q4_K_M · reasoning": "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf?download=true",
    "Mistral 7B · Q4_K_M · advanced": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf?download=true",
}


@dataclass
class DesktopSession:
    hardware: dict[str, Any]
    store: LocalResultStore
    gguf_provider: LlamaCppProvider
    provider: ProviderRouter
    engine: BenchmarkEngine
    results_dir: Path

    @classmethod
    def create(cls, base_dir: str | Path | None = None) -> "DesktopSession":
        if base_dir is None:
            data_root = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Aetherion" / "results"
        else:
            data_root = Path(base_dir)
        gguf_provider = LlamaCppProvider(data_root / "models")
        provider = ProviderRouter([OllamaProvider(timeout=120), gguf_provider])
        return cls(
            hardware=detect_hardware(),
            store=LocalResultStore(data_root / "client"),
            gguf_provider=gguf_provider,
            provider=provider,
            engine=BenchmarkEngine(provider, data_root),
            results_dir=data_root,
        )


class AetherionDesktopClient:
    """Desktop interface for discovering local models and benchmarking them."""

    def __init__(self, root: tk.Tk | None = None, base_dir: str | Path | None = None):
        self.root = root or tk.Tk()
        self.root.title("AETHERION Client")
        self.root.geometry("1200x820")
        self.root.minsize(1020, 720)
        self.root.configure(bg="#090D13")
        self.base_dir = base_dir
        self.account_service = AccountService()
        self.auth_session: AuthSession | None = None
        self.account_events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.auth_pending = False
        self.auth_fields: dict[str, tk.Entry] = {}
        self.auth_form: tk.Frame | None = None
        self.auth_mode = "login"
        self.auth_feedback: tk.Label | None = None
        self.auth_submit_button: tk.Button | None = None
        self.auth_url_entry: tk.Entry | None = None
        self.auth_title: tk.Label | None = None
        self.auth_description: tk.Label | None = None
        self.auth_mode_buttons: dict[str, tk.Button] = {}
        self.account_check_inflight = False
        self.license_gate: tk.Frame | None = None
        self.container: tk.Frame | None = None
        self.workspace_ready = False
        self.session: DesktopSession | None = None
        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.models: dict[str, ModelInfo] = {}
        self.recommended_model_name: str | None = None
        self.download_window: tk.Toplevel | None = None
        self.download_progress: ttk.Progressbar | None = None
        self.download_status: tk.Label | None = None
        self.download_button: tk.Button | None = None
        self.busy = False
        self.benchmark_stop_event: threading.Event | None = None
        self.closing = False
        self.brand_phase = 0
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.show_license_gate("Checking for a saved account session…")
        self.root.after(100, self.process_account_events)
        threading.Thread(target=self.restore_saved_session, daemon=True).start()
        self.root.after(300_000, self.check_license_periodically)

    def start_workspace(self) -> None:
        self.license_gate = None
        self.root.geometry("1200x820")
        self.root.minsize(1020, 720)
        if self.container is None:
            self.session = DesktopSession.create(self.base_dir)
            self.build_ui()
            self.workspace_ready = True
            self.root.after(100, self.process_events)
            self.animate_brand_mark()
            self.root.after(200, self.refresh_dependency_status)
            self.refresh_models()
        else:
            self.workspace_ready = True
            self.container.pack(fill="both", expand=True, padx=18, pady=18)

    def show_license_gate(self, message: str) -> None:
        self.workspace_ready = False
        if self.container is not None:
            self.container.pack_forget()
        if self.license_gate is not None and self.license_gate.winfo_exists():
            self.license_gate.destroy()
        self.license_gate = tk.Frame(self.root, bg=COLORS["canvas"])
        self.license_gate.pack(fill="both", expand=True)
        gate = self.license_gate
        self._ambient_backdrop(gate)
        gate.grid_columnconfigure(0, weight=1)
        gate.grid_rowconfigure(0, weight=1)
        card = tk.Frame(gate, bg=COLORS["surface"], highlightbackground=COLORS["line_strong"], highlightthickness=1, bd=0)
        card.grid(row=0, column=0, padx=32, pady=32, sticky="")
        tk.Frame(card, bg=COLORS["accent"], height=3).pack(fill="x")
        body = tk.Frame(card, bg=COLORS["surface"])
        body.pack(fill="both", expand=True, padx=30, pady=24)
        tk.Label(body, text="AETHERION  /  SECURE ACCOUNT", bg=COLORS["surface"], fg=COLORS["accent"], font=FONTS["section"]).pack(anchor="w")
        self.auth_title = tk.Label(body, text="Welcome back", bg=COLORS["surface"], fg=COLORS["text"], font=FONTS["display"])
        self.auth_title.pack(anchor="w", pady=(8, 5))
        self.auth_description = tk.Label(body, text="Your models and benchmark results stay on this device.", bg=COLORS["surface"], fg=COLORS["muted"], font=FONTS["body"], wraplength=620, justify="left")
        self.auth_description.pack(anchor="w", pady=(0, 14))
        tk.Label(body, text="LICENSE SERVICE URL", bg=COLORS["surface"], fg=COLORS["muted"], font=FONTS["section"]).pack(anchor="w")
        self.auth_url_entry = tk.Entry(body, bg=COLORS["surface_elevated"], fg=COLORS["text"], insertbackground=COLORS["accent"], relief="flat", font=FONTS["body"], highlightbackground=COLORS["line"], highlightcolor=COLORS["accent"], highlightthickness=1)
        self._bind_entry_focus(self.auth_url_entry)
        self.auth_url_entry.pack(fill="x", pady=(5, 12), ipady=7)
        self.auth_url_entry.insert(0, get_service_url())
        tk.Label(body, text="THIS DEVICE ID", bg=COLORS["surface"], fg=COLORS["muted"], font=FONTS["section"]).pack(anchor="w")
        device_row = tk.Frame(body, bg=COLORS["surface_elevated"], highlightbackground=COLORS["line_strong"], highlightthickness=1)
        device_row.pack(fill="x", pady=(5, 10))
        device_id = machine_fingerprint()
        tk.Label(device_row, text=device_id, bg=COLORS["surface_elevated"], fg=COLORS["text"], font=FONTS["mono"], padx=12, pady=9, anchor="w").pack(side="left", fill="x", expand=True)
        self._button(device_row, "COPY ID", lambda: self.copy_device_id(device_id)).pack(side="right", padx=6, pady=5)
        tabs = tk.Frame(body, bg=COLORS["surface"])
        tabs.pack(fill="x", pady=(1, 8))
        self.auth_mode_buttons = {
            "login": self._button(tabs, "SIGN IN", lambda: self.render_account_form("login"), primary=True),
            "register": self._button(tabs, "CREATE ACCOUNT", lambda: self.render_account_form("register")),
        }
        self.auth_mode_buttons["login"].pack(side="left", padx=(0, 8))
        self.auth_mode_buttons["register"].pack(side="left")
        self.auth_form = tk.Frame(body, bg=COLORS["surface"])
        self.auth_form.pack(fill="x")
        self.auth_feedback = tk.Label(body, text=message, bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["small"], wraplength=620, justify="left", anchor="w")
        self.auth_feedback.pack(fill="x", pady=(9, 8))
        actions = tk.Frame(body, bg=COLORS["surface"])
        actions.pack(fill="x")
        self.auth_submit_button = self._button(actions, "SIGN IN", self.submit_account_form, primary=True)
        self.auth_submit_button.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._button(actions, "CONTINUE OFFLINE", self.continue_offline).pack(side="left")
        tk.Label(body, text="The benchmark remains local. A protected session grant allows up to 7 days offline on this Windows account and device.", bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["small"], wraplength=620, justify="left").pack(anchor="w", pady=(11, 0))
        self.render_account_form(self.auth_mode)

    def copy_device_id(self, device_id: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(device_id)

    @staticmethod
    def _blend_hex(base: str, tint: str, amount: float) -> str:
        base_rgb = tuple(int(base[index:index + 2], 16) for index in (1, 3, 5))
        tint_rgb = tuple(int(tint[index:index + 2], 16) for index in (1, 3, 5))
        mixed = tuple(round(left + (right - left) * amount) for left, right in zip(base_rgb, tint_rgb))
        return "#" + "".join(f"{channel:02X}" for channel in mixed)

    def _ambient_backdrop(self, parent: tk.Widget) -> tk.Canvas:
        backdrop = tk.Canvas(parent, bg=COLORS["canvas"], bd=0, highlightthickness=0)
        backdrop.place(x=0, y=0, relwidth=1, relheight=1)

        def paint(event: tk.Event) -> None:
            width, height = max(1, event.width), max(1, event.height)
            backdrop.delete("ambient")
            radius = int(max(width, height) * 0.74)
            glows = (
                (int(width * 0.88), int(height * 0.12), COLORS["glow_mint"], 0.42),
                (int(width * 0.08), int(height * 0.92), COLORS["glow_blue"], 0.38),
            )
            for center_x, center_y, color, strength in glows:
                for step in range(24, 0, -1):
                    ring_radius = max(1, int(radius * step / 24))
                    tint = self._blend_hex(COLORS["canvas"], color, (1 - step / 24) * strength)
                    backdrop.create_oval(
                        center_x - ring_radius, center_y - ring_radius,
                        center_x + ring_radius, center_y + ring_radius,
                        fill=tint, outline="", tags="ambient",
                    )

        backdrop.bind("<Configure>", paint, add="+")
        # Canvas.lower() lowers a canvas item and requires a tag/id; use the
        # underlying Tk window command to place this background behind widgets.
        backdrop.tk.call("lower", backdrop._w)
        return backdrop

    @staticmethod
    def _bind_entry_focus(entry: tk.Entry) -> None:
        entry.bind("<FocusIn>", lambda _event: entry.configure(highlightbackground=COLORS["accent"], highlightcolor=COLORS["accent"]))
        entry.bind("<FocusOut>", lambda _event: entry.configure(highlightbackground=COLORS["line"], highlightcolor=COLORS["line"]))

    def render_account_form(self, mode: str) -> None:
        if self.auth_form is None or not self.auth_form.winfo_exists():
            return
        self.auth_mode = mode
        if self.auth_title is not None:
            self.auth_title.configure(text="Welcome back" if mode == "login" else "Create your account")
        if self.auth_description is not None:
            copy = "Your models and benchmark results stay on this device." if mode == "login" else "New accounts need a valid license key and are bound to this device."
            self.auth_description.configure(text=copy)
        for name, button in self.auth_mode_buttons.items():
            active = name == mode
            button.configure(
                bg=COLORS["accent"] if active else COLORS["surface_interactive"],
                fg=COLORS["canvas"] if active else COLORS["text_soft"],
                activebackground=COLORS["accent_hover"] if active else COLORS["line_strong"],
                activeforeground=COLORS["canvas"] if active else COLORS["text"],
            )
            button.bind(
                "<Enter>",
                lambda _event, widget=button, key=name: widget.configure(
                    bg=COLORS["accent_hover"] if key == self.auth_mode else COLORS["line_strong"]
                ),
            )
            button.bind(
                "<Leave>",
                lambda _event, widget=button, key=name: widget.configure(
                    bg=COLORS["accent"] if key == self.auth_mode else COLORS["surface_interactive"]
                ),
            )
        self.auth_fields = {}
        for widget in self.auth_form.winfo_children():
            widget.destroy()
        fields = [("username", "USERNAME", ""), ("password", "PASSWORD", "•")]
        if mode == "register":
            fields.extend([("confirm", "CONFIRM PASSWORD", "•"), ("license_key", "LICENSE KEY", "")])
        for name, label, mask in fields:
            tk.Label(self.auth_form, text=label, bg=COLORS["surface"], fg=COLORS["muted"], font=FONTS["section"]).pack(anchor="w", pady=(5, 3))
            entry = tk.Entry(self.auth_form, bg=COLORS["surface_elevated"], fg=COLORS["text"], insertbackground=COLORS["accent"], relief="flat", font=FONTS["mono"] if name == "license_key" else FONTS["body"], show=mask, highlightbackground=COLORS["line"], highlightcolor=COLORS["accent"], highlightthickness=1)
            self._bind_entry_focus(entry)
            entry.pack(fill="x", ipady=6)
            self.auth_fields[name] = entry
        if self.auth_submit_button is not None and self.auth_submit_button.winfo_exists():
            self.auth_submit_button.configure(text="CREATE ACCOUNT" if mode == "register" else "SIGN IN")

    def submit_account_form(self) -> None:
        if self.auth_pending or self.auth_url_entry is None or self.auth_feedback is None:
            return
        try:
            base_url = save_service_url(self.auth_url_entry.get())
        except AuthError as exc:
            self.auth_feedback.configure(text=str(exc), fg=COLORS["error"])
            return
        values = {name: entry.get() for name, entry in self.auth_fields.items()}
        username = values.get("username", "").strip()
        password = values.get("password", "")
        if not username or not password:
            self.auth_feedback.configure(text="Enter your username and password.", fg=COLORS["error"])
            return
        mode = self.auth_mode
        if mode == "register":
            if len(password) < 12:
                self.auth_feedback.configure(text="Use a password with at least 12 characters.", fg=COLORS["error"])
                return
            if password != values.get("confirm", ""):
                self.auth_feedback.configure(text="The password confirmation does not match.", fg=COLORS["error"])
                return
            if not values.get("license_key", "").strip():
                self.auth_feedback.configure(text="A valid license key is required to create an account.", fg=COLORS["error"])
                return
        service = AccountService(base_url)
        self.auth_pending = True
        self.auth_feedback.configure(text="Connecting securely to the license service…", fg=COLORS["accent"])
        if self.auth_submit_button is not None:
            self.auth_submit_button.configure(state="disabled")
        def authenticate() -> None:
            try:
                if mode == "register":
                    session = service.register(username, password, values["license_key"].strip(), machine_fingerprint())
                else:
                    session = service.login(username, password, machine_fingerprint())
                self.account_events.put(("auth_success", (service, session)))
            except Exception as exc:
                self.account_events.put(("auth_error", str(exc)))
        threading.Thread(target=authenticate, daemon=True).start()

    def restore_saved_session(self) -> None:
        try:
            session = self.account_service.restore_cached(machine_fingerprint())
            self.account_events.put(("restore_session", session))
        except Exception as exc:
            self.account_events.put(("restore_error", str(exc)))

    def continue_offline(self) -> None:
        if self.auth_pending:
            return
        self.auth_pending = True
        if self.auth_feedback is not None:
            self.auth_feedback.configure(text="Checking saved offline access…", fg=COLORS["accent"])
        threading.Thread(target=self.restore_saved_session, daemon=True).start()

    def process_account_events(self) -> None:
        if self.closing:
            return
        while True:
            try:
                event, payload = self.account_events.get_nowait()
            except queue.Empty:
                break
            if event == "auth_success":
                self.account_service, self.auth_session = payload
                self.auth_pending = False
                if self.license_gate is not None and self.license_gate.winfo_exists():
                    self.license_gate.destroy()
                self.license_gate = None
                self.start_workspace()
            elif event in {"auth_error", "restore_error"}:
                self.auth_pending = False
                if self.auth_feedback is not None and self.auth_feedback.winfo_exists():
                    self.auth_feedback.configure(text=str(payload), fg=COLORS["error"])
                if self.auth_submit_button is not None:
                    self.auth_submit_button.configure(state="normal")
            elif event == "restore_session":
                self.auth_pending = False
                if payload is not None:
                    self.auth_session = payload
                    if self.license_gate is not None and self.license_gate.winfo_exists():
                        self.license_gate.destroy()
                    self.license_gate = None
                    self.start_workspace()
                elif self.auth_feedback is not None and self.auth_feedback.winfo_exists():
                    self.auth_feedback.configure(text="Sign in or create an account to use Aetherion.", fg=COLORS["quiet"])
            elif event == "refresh_success":
                self.auth_session = payload
                self.account_check_inflight = False
            elif event == "refresh_unavailable":
                self.account_check_inflight = False
                if self.auth_session is not None and dt.datetime.now(dt.UTC) >= self.auth_session.offline_until:
                    self.account_events.put(("session_expired", "The offline access period ended. Connect and sign in again."))
            elif event == "session_expired":
                self.account_check_inflight = False
                self.auth_session = None
                clear_cached_session()
                self.show_license_gate(str(payload))
            elif event == "signed_out":
                self.auth_session = None
                self.auth_pending = False
                if self.container is not None:
                    self.container.pack_forget()
                self.show_license_gate("You have signed out.")
        self.root.after(100, self.process_account_events)

    def check_license_periodically(self) -> None:
        if self.closing:
            return
        if self.workspace_ready and self.auth_session is not None and not self.account_check_inflight:
            self.account_check_inflight = True
            current_session = self.auth_session
            def refresh_session() -> None:
                try:
                    if current_session.session_token:
                        updated = self.account_service.refresh(current_session)
                    else:
                        updated = self.account_service.restore_cached(machine_fingerprint())
                        if updated is None:
                            raise AuthError("Session expired; sign in again.")
                    self.account_events.put(("refresh_success", updated))
                except AuthUnavailable:
                    self.account_events.put(("refresh_unavailable", None))
                except AuthError as exc:
                    self.account_events.put(("session_expired", str(exc)))
                except OSError:
                    self.account_events.put(("refresh_unavailable", None))
            threading.Thread(target=refresh_session, daemon=True).start()
        self.root.after(300_000, self.check_license_periodically)

    def sign_out(self) -> None:
        if self.busy and not messagebox.askyesno("Benchmark in progress", "Stop the benchmark and sign out?", parent=self.root):
            return
        if self.benchmark_stop_event is not None:
            self.benchmark_stop_event.set()
        service, session = self.account_service, self.auth_session
        self.auth_session = None
        clear_cached_session()
        if self.container is not None:
            self.container.pack_forget()
        self.show_license_gate("You have signed out.")
        threading.Thread(target=lambda: service.logout(session), daemon=True).start()

    def _card(self, parent: tk.Widget, *, accent: bool = False) -> tk.Frame:
        card = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            bd=0,
        )
        if accent:
            tk.Frame(card, bg=COLORS["accent"], height=2).pack(fill="x")
        return card

    def _button(self, parent: tk.Widget, text: str, command: Any, *, primary: bool = False) -> tk.Button:
        bg = COLORS["accent"] if primary else COLORS["surface_interactive"]
        fg = COLORS["canvas"] if primary else COLORS["text_soft"]
        active_bg = COLORS["accent_hover"] if primary else COLORS["line_strong"]
        active_fg = COLORS["canvas"] if primary else COLORS["text"]
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=active_fg,
            disabledforeground=COLORS["quiet"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=10,
            cursor="hand2",
            highlightthickness=0,
        )
        button.bind("<Enter>", lambda _event: button.configure(bg=active_bg))
        button.bind("<Leave>", lambda _event: button.configure(bg=bg))
        return button

    def _field_label(self, parent: tk.Widget, text: str) -> tk.Label:
        return tk.Label(
            parent,
            text=text.upper(),
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=FONTS["section"],
            anchor="w",
        )

    def build_ui(self) -> None:
        style = ttk.Style(self.root)
        configure_ttk(style)

        self.root.configure(bg=COLORS["canvas"])
        self.container = tk.Frame(self.root, bg=COLORS["canvas"])
        self.container.pack(fill="both", expand=True, padx=18, pady=18)
        self.shell = tk.Frame(self.container, bg=COLORS["canvas"])
        self.shell.pack(fill="both", expand=True)

        self.create_sidebar(self.shell)
        self.workspace = tk.Frame(self.shell, bg=COLORS["canvas"])
        self.workspace.pack(side="left", fill="both", expand=True, padx=(18, 0))

        header = tk.Frame(self.workspace, bg=COLORS["canvas"], height=66)
        header.pack(fill="x", pady=(0, 15))
        header.pack_propagate(False)
        tk.Frame(header, bg=COLORS["line"], height=1).pack(side="bottom", fill="x")
        heading = tk.Frame(header, bg=COLORS["canvas"])
        heading.pack(side="left", fill="y", expand=True)
        tk.Label(
            heading,
            text="AETHERION  /  LOCAL MODEL BENCHMARK",
            bg=COLORS["canvas"],
            fg=COLORS["quiet"],
            font=FONTS["section"],
        ).pack(anchor="w", pady=(3, 4))
        self.section_var = tk.StringVar(value="DASHBOARD")
        tk.Label(
            heading,
            textvariable=self.section_var,
            bg=COLORS["canvas"],
            fg=COLORS["text"],
            font=("Segoe UI", 23, "bold"),
        ).pack(anchor="w")
        self.status_var = tk.StringVar(value="CONNECTING TO LOCAL RUNTIMES")
        self.status = tk.Label(
            header,
            textvariable=self.status_var,
            bg=COLORS["surface_elevated"],
            fg=COLORS["text_soft"],
            font=("Segoe UI", 8, "bold"),
            padx=13,
            pady=9,
            highlightbackground=COLORS["line"],
            highlightthickness=1,
        )
        self.status.pack(side="right", anchor="center", padx=(12, 0))

        self.view_stack = tk.Frame(self.workspace, bg=COLORS["canvas"])
        self.view_stack.pack(fill="both", expand=True)
        self.dashboard_view = tk.Frame(self.view_stack, bg=COLORS["canvas"])
        self.dashboard_view.pack(fill="both", expand=True)
        self.views: dict[str, tk.Frame] = {"dashboard": self.dashboard_view}

        self.dashboard_view.grid_columnconfigure(0, weight=1)
        self.dashboard_view.grid_rowconfigure(1, weight=1)

        overview = tk.Frame(self.dashboard_view, bg=COLORS["canvas"])
        overview.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        for column in range(3):
            overview.grid_columnconfigure(column, weight=1, uniform="overview")
        overview_values = [
            ("runtime_metric", "ACTIVE RUNTIME", "Discovering providers"),
            ("models_metric", "LOCAL MODELS", "Scanning this device"),
            ("last_run_metric", "LATEST BENCHMARK", "No run yet"),
        ]
        self.overview_vars: dict[str, tk.StringVar] = {}
        for column, (key, label, value) in enumerate(overview_values):
            card = self._card(overview, accent=True)
            card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 7, 0 if column == 2 else 7))
            body = tk.Frame(card, bg=COLORS["surface"])
            body.pack(fill="both", expand=True, padx=16, pady=12)
            tk.Label(body, text=label, bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["section"]).pack(anchor="w")
            variable = tk.StringVar(value=value)
            self.overview_vars[key] = variable
            tk.Label(
                body,
                textvariable=variable,
                bg=COLORS["surface"],
                fg=COLORS["text"],
                font=("Segoe UI", 12, "bold"),
                anchor="w",
            ).pack(anchor="w", pady=(6, 0))

        content = tk.Frame(self.dashboard_view, bg=COLORS["canvas"])
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=3, minsize=330)
        content.grid_columnconfigure(1, weight=2, minsize=310)
        self.left = tk.Frame(content, bg=COLORS["canvas"])
        self.left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.right = self._card(content, accent=True)
        self.right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        hardware_panel = self._card(self.left)
        hardware_panel.pack(fill="x", pady=(0, 12))
        hardware_content = tk.Frame(hardware_panel, bg=COLORS["surface"])
        hardware_content.pack(fill="x", padx=16, pady=14)
        hardware_heading = tk.Frame(hardware_content, bg=COLORS["surface"])
        hardware_heading.pack(fill="x", pady=(0, 7))
        tk.Label(hardware_heading, text="SYSTEM PROFILE", bg=COLORS["surface"], fg=COLORS["accent"], font=FONTS["section"]).pack(side="left")
        tk.Label(hardware_heading, text="MEASURED ON THIS DEVICE", bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["small"]).pack(side="right")
        self.hardware_text = tk.Text(
            hardware_content,
            height=4,
            bg=COLORS["surface"],
            fg=COLORS["text_soft"],
            bd=0,
            wrap="word",
            padx=0,
            pady=2,
            font=FONTS["mono"],
            selectbackground=COLORS["surface_interactive"],
            selectforeground=COLORS["text"],
            relief="flat",
            highlightthickness=0,
        )
        self.hardware_text.pack(fill="x")
        self.hardware_text.insert("end", self.format_hardware(self.session.hardware))
        self.hardware_text.configure(state="disabled")

        output_panel = self._card(self.left)
        output_panel.pack(fill="both", expand=True)
        output_content = tk.Frame(output_panel, bg=COLORS["surface"])
        output_content.pack(fill="both", expand=True, padx=16, pady=14)
        output_header = tk.Frame(output_content, bg=COLORS["surface"])
        output_header.pack(fill="x", pady=(0, 10))
        tk.Label(output_header, text="BENCHMARK TRACE", bg=COLORS["surface"], fg=COLORS["text"], font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(output_header, text="SAVED LOCALLY", bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["small"]).pack(side="right")
        output_frame = tk.Frame(output_content, bg=COLORS["canvas"], highlightbackground=COLORS["line"], highlightthickness=1)
        output_frame.pack(fill="both", expand=True)
        self.output = tk.Text(
            output_frame,
            bg=COLORS["canvas"],
            fg=COLORS["text_soft"],
            insertbackground=COLORS["accent"],
            bd=0,
            wrap="word",
            padx=14,
            pady=13,
            font=FONTS["mono"],
            state="disabled",
            selectbackground=COLORS["surface_interactive"],
            selectforeground=COLORS["text"],
            relief="flat",
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output.yview, style="Aetherion.Vertical.TScrollbar")
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.output.tag_configure("good", foreground=COLORS["success"])
        self.output.tag_configure("bad", foreground=COLORS["error"])
        self.output.tag_configure("muted", foreground=COLORS["muted"])
        self.append_output("Choose a local model and run a benchmark. Results stay on this device.\n", "muted")

        self.configuration_canvas = tk.Canvas(
            self.right,
            bg=COLORS["surface"],
            bd=0,
            highlightthickness=0,
            yscrollincrement=24,
        )
        self.configuration_scrollbar = ttk.Scrollbar(
            self.right,
            orient="vertical",
            command=self.configuration_canvas.yview,
            style="Aetherion.Vertical.TScrollbar",
        )
        self.configuration_canvas.configure(yscrollcommand=self.configuration_scrollbar.set)
        self.configuration_canvas.pack(side="left", fill="both", expand=True, padx=(14, 0), pady=(14, 10))
        self.configuration_scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=(14, 10))
        controls_outer = tk.Frame(self.configuration_canvas, bg=COLORS["surface"])
        controls = tk.Frame(controls_outer, bg=COLORS["surface"])
        controls.pack(fill="both", expand=True, padx=12, pady=12)
        controls_window = self.configuration_canvas.create_window((0, 0), window=controls_outer, anchor="nw")
        controls_outer.bind(
            "<Configure>",
            lambda _event: self.configuration_canvas.configure(scrollregion=self.configuration_canvas.bbox("all")),
        )
        self.configuration_canvas.bind(
            "<Configure>",
            lambda event: self.configuration_canvas.itemconfigure(controls_window, width=max(1, event.width)),
        )

        def scroll_configuration(event: tk.Event) -> None:
            x0 = self.configuration_canvas.winfo_rootx()
            y0 = self.configuration_canvas.winfo_rooty()
            if x0 <= event.x_root <= x0 + self.configuration_canvas.winfo_width() and y0 <= event.y_root <= y0 + self.configuration_canvas.winfo_height():
                self.configuration_canvas.yview_scroll(int(-event.delta / 120), "units")

        self.root.bind_all("<MouseWheel>", scroll_configuration, add="+")
        tk.Label(controls, text="Run a benchmark", bg=COLORS["surface"], fg=COLORS["text"], font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(
            controls,
            text="Choose a local model and a validation suite.",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=FONTS["body"],
        ).pack(anchor="w", pady=(3, 14))

        self.download_model_button = self._button(
            controls,
            "Download a model",
            self.open_model_downloader,
            primary=True,
        )
        self.download_model_button.pack(fill="x", pady=(0, 5))
        tk.Label(
            controls,
            text="Browse the catalog or use a direct HTTPS link to an external GGUF file.",
            bg=COLORS["surface"],
            fg=COLORS["quiet"],
            justify="left",
            anchor="w",
            wraplength=340,
            font=FONTS["small"],
        ).pack(anchor="w", fill="x", pady=(0, 14))

        self._field_label(controls, "Model").pack(anchor="w")
        self.model_var = tk.StringVar()
        self.model_menu = ttk.Combobox(controls, textvariable=self.model_var, state="disabled", style="Aetherion.TCombobox")
        self.model_menu.pack(fill="x", pady=(6, 8))
        self.model_menu.bind("<<ComboboxSelected>>", lambda _event: self.update_model_details())
        self.model_details = tk.Label(
            controls,
            text="Discovering models on this device…",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            justify="left",
            anchor="w",
            wraplength=340,
            font=FONTS["small"],
            padx=0,
        )
        self.model_details.pack(anchor="w", fill="x", pady=(0, 13))

        self._field_label(controls, "Task suite").pack(anchor="w")
        self.category_var = tk.StringVar(value="All tasks")
        categories = list(dict.fromkeys(task.category for task in TASKS))
        self.category_menu = ttk.Combobox(
            controls,
            textvariable=self.category_var,
            values=["All tasks", *categories],
            state="readonly",
            style="Aetherion.TCombobox",
        )
        self.category_menu.pack(fill="x", pady=(6, 6))
        self.category_menu.bind("<<ComboboxSelected>>", lambda _event: self.update_suite_details())
        self.suite_details = tk.Label(
            controls,
            text=TASK_SUITE_DESCRIPTIONS["All tasks"],
            bg=COLORS["surface"],
            fg=COLORS["quiet"],
            justify="left",
            anchor="w",
            wraplength=340,
            font=FONTS["small"],
        )
        self.suite_details.pack(anchor="w", fill="x", pady=(0, 11))

        self.run_button = self._button(controls, "Run benchmark", self.run_selected_benchmark, primary=True)
        self.run_button.pack(fill="x", pady=(0, 13))
        self.stop_button = self._button(controls, "Stop benchmark", self.stop_benchmark)
        self.stop_button.pack(fill="x", pady=(0, 13))
        self.stop_button.configure(state="disabled")

        separator = tk.Frame(controls, bg=COLORS["line"], height=1)
        separator.pack(fill="x", pady=(0, 11))
        self._field_label(controls, "GGUF model folder").pack(anchor="w")
        model_path_frame = tk.Frame(controls, bg=COLORS["surface"])
        model_path_frame.pack(fill="x", pady=(6, 10))
        self.model_path_var = tk.StringVar(value=str(self.session.gguf_provider.models_dir))
        self.model_path_entry = tk.Entry(
            model_path_frame,
            textvariable=self.model_path_var,
            bg=COLORS["canvas"],
            fg=COLORS["text_soft"],
            insertbackground=COLORS["accent"],
            relief="flat",
            highlightbackground=COLORS["line"],
            highlightcolor=COLORS["accent"],
            highlightthickness=1,
            font=FONTS["small"],
        )
        self.model_path_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 6))
        self._button(model_path_frame, "Browse", self.browse_model_folder).pack(side="right")

        self.requirements_label = tk.Label(
            controls,
            text="Checking local runtimes…",
            bg=COLORS["surface_elevated"],
            fg=COLORS["muted"],
            justify="left",
            anchor="w",
            wraplength=340,
            font=FONTS["mono"],
            padx=10,
            pady=9,
        )
        self.requirements_label.pack(anchor="w", fill="x", pady=(0, 8))

        actions = tk.Frame(controls, bg=COLORS["surface"])
        actions.pack(fill="x")
        actions.grid_columnconfigure(0, weight=1)
        self.install_requirements_button = self._button(actions, "Install runtimes", self.download_missing_dependencies)
        self.install_requirements_button.grid(row=0, column=0, sticky="ew")
        self.refresh_button = self._button(actions, "Refresh models", self.refresh_models)
        self.refresh_button.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        self.result_status = tk.Label(
            controls,
            text="Waiting for local runtimes",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            justify="left",
            anchor="w",
            wraplength=340,
            font=FONTS["small"],
            padx=0,
            pady=6,
        )
        self.result_status.pack(anchor="w", fill="x", pady=(10, 2))
        self.progress = ttk.Progressbar(controls, mode="determinate", maximum=100, value=0, style="Aetherion.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 4))
        self.progress_text = tk.Label(controls, text="Ready to benchmark", bg=COLORS["surface"], fg=COLORS["quiet"], anchor="w", font=FONTS["small"])
        self.progress_text.pack(anchor="w", fill="x")
        self.run_metrics = tk.Label(
            controls,
            text="No run yet · complete a benchmark to see its summary.",
            bg=COLORS["surface_elevated"],
            fg=COLORS["text_soft"],
            justify="left",
            anchor="w",
            wraplength=340,
            font=FONTS["small"],
            padx=10,
            pady=9,
        )
        self.run_metrics.pack(anchor="w", fill="x", pady=(10, 0))

        self.views.update({})
        self.create_secondary_views()
        self.open_results_button = self._button(self.right, "Open results folder", self.open_results_folder)
        self.open_results_button.pack(fill="x", padx=14, pady=(0, 14))

    def view_header(self, parent: tk.Widget, eyebrow: str, title: str, description: str) -> None:
        header = tk.Frame(parent, bg=COLORS["canvas"])
        header.pack(fill="x", pady=(4, 18))
        tk.Label(header, text=eyebrow.upper(), bg=COLORS["canvas"], fg=COLORS["accent"], font=FONTS["section"]).pack(anchor="w")
        tk.Label(header, text=title, bg=COLORS["canvas"], fg=COLORS["text"], font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(5, 4))
        tk.Label(
            header,
            text=description,
            bg=COLORS["canvas"],
            fg=COLORS["muted"],
            font=FONTS["body"],
            wraplength=760,
            justify="left",
        ).pack(anchor="w")

    def create_secondary_views(self) -> None:
        models_view = tk.Frame(self.view_stack, bg=COLORS["canvas"])
        self.views["models"] = models_view
        self.view_header(models_view, "MODEL LIBRARY", "Your local model catalog", "Review available models, runtimes, and hardware fit.")
        models_panel = self._card(models_view)
        models_panel.pack(fill="both", expand=True)
        self.model_view_listbox = tk.Listbox(
            models_panel,
            bg=COLORS["surface"],
            fg=COLORS["text_soft"],
            selectbackground=COLORS["surface_interactive"],
            selectforeground=COLORS["text"],
            highlightthickness=0,
            bd=0,
            activestyle="none",
            font=FONTS["body"],
            relief="flat",
        )
        self.model_view_listbox.pack(fill="both", expand=True, padx=16, pady=14)

        benchmarks_view = tk.Frame(self.view_stack, bg=COLORS["canvas"])
        self.views["benchmarks"] = benchmarks_view
        self.view_header(benchmarks_view, "BENCHMARK LAB", "Measure before you decide", "A controlled local validation, with each result saved on this device.")
        benchmark_panel = self._card(benchmarks_view, accent=True)
        benchmark_panel.pack(fill="x", pady=(0, 12))
        benchmark_body = tk.Frame(benchmark_panel, bg=COLORS["surface"])
        benchmark_body.pack(fill="x", padx=18, pady=16)
        tk.Label(benchmark_body, text="CURRENT CONFIGURATION", bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["section"]).pack(anchor="w")
        self.benchmark_view_config = tk.Label(benchmark_body, text="No model selected", bg=COLORS["surface"], fg=COLORS["text"], font=("Segoe UI", 13, "bold"), anchor="w")
        self.benchmark_view_config.pack(anchor="w", pady=(7, 12))
        self._button(benchmark_body, "Open benchmark controls", lambda: self.focus_section("dashboard")).pack(anchor="w")
        guidance = self._card(benchmarks_view)
        guidance.pack(fill="x")
        tk.Label(
            guidance,
            text="The suite checks general instruction following, code format, arithmetic, JSON, and Spanish comprehension. These checks are signals for comparison, not a universal quality score.",
            bg=COLORS["surface"],
            fg=COLORS["text_soft"],
            justify="left",
            wraplength=760,
            font=FONTS["body"],
            padx=18,
            pady=16,
        ).pack(anchor="w")

        results_view = tk.Frame(self.view_stack, bg=COLORS["canvas"])
        self.views["results"] = results_view
        self.view_header(results_view, "RESULTS", "Evidence from your machine", "Review completed runs stored in your local results folder.")
        results_panel = self._card(results_view)
        results_panel.pack(fill="both", expand=True)
        results_body = tk.Frame(results_panel, bg=COLORS["surface"])
        results_body.pack(fill="both", expand=True, padx=14, pady=14)
        self.results_view_text = tk.Text(
            results_body,
            bg=COLORS["surface"],
            fg=COLORS["text_soft"],
            bd=0,
            wrap="word",
            padx=6,
            pady=6,
            font=FONTS["mono"],
            state="disabled",
            relief="flat",
            highlightthickness=0,
        )
        results_scrollbar = ttk.Scrollbar(results_body, orient="vertical", command=self.results_view_text.yview, style="Aetherion.Vertical.TScrollbar")
        self.results_view_text.configure(yscrollcommand=results_scrollbar.set)
        self.results_view_text.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")

        hardware_view = tk.Frame(self.view_stack, bg=COLORS["canvas"])
        self.views["hardware"] = hardware_view
        self.view_header(hardware_view, "SYSTEM PROFILE", "Know the machine first", "Detected hardware and available telemetry used to contextualize each run.")
        hardware_panel = self._card(hardware_view, accent=True)
        hardware_panel.pack(fill="x")
        self.hardware_view_text = tk.Text(
            hardware_panel,
            height=9,
            bg=COLORS["surface"],
            fg=COLORS["text_soft"],
            bd=0,
            wrap="word",
            padx=18,
            pady=16,
            font=FONTS["mono"],
            state="disabled",
            relief="flat",
            highlightthickness=0,
        )
        self.hardware_view_text.pack(fill="x")
        self.hardware_view_text.configure(state="normal")
        self.hardware_view_text.insert("end", self.format_hardware(self.session.hardware))
        self.hardware_view_text.configure(state="disabled")

        history_view = tk.Frame(self.view_stack, bg=COLORS["canvas"])
        self.views["history"] = history_view
        self.view_header(history_view, "HISTORY", "Your local benchmark trail", "Recent run records, newest first.")
        history_panel = self._card(history_view)
        history_panel.pack(fill="both", expand=True)
        self.history_view_listbox = tk.Listbox(
            history_panel,
            bg=COLORS["surface"],
            fg=COLORS["text_soft"],
            selectbackground=COLORS["surface_interactive"],
            selectforeground=COLORS["text"],
            highlightthickness=0,
            bd=0,
            activestyle="none",
            font=FONTS["mono"],
            relief="flat",
        )
        self.history_view_listbox.pack(fill="both", expand=True, padx=16, pady=14)

        settings_view = tk.Frame(self.view_stack, bg=COLORS["canvas"])
        self.views["settings"] = settings_view
        self.view_header(settings_view, "SETTINGS", "Local workspace", "Manage the folder used to discover GGUF models and inspect local runtime readiness.")
        settings_panel = self._card(settings_view)
        settings_panel.pack(fill="x")
        settings_body = tk.Frame(settings_panel, bg=COLORS["surface"])
        settings_body.pack(fill="x", padx=18, pady=16)
        tk.Label(settings_body, text="MODEL STORAGE", bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["section"]).pack(anchor="w")
        tk.Label(
            settings_body,
            textvariable=self.model_path_var,
            bg=COLORS["surface"],
            fg=COLORS["text_soft"],
            font=FONTS["mono"],
            anchor="w",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(7, 12))
        settings_actions = tk.Frame(settings_body, bg=COLORS["surface"])
        settings_actions.pack(anchor="w")
        self._button(settings_actions, "Change model folder", self.browse_model_folder).pack(side="left", padx=(0, 8))
        self._button(settings_actions, "Open results folder", self.open_results_folder).pack(side="left")

        self.refresh_model_view()
        self.refresh_results_view()
        self.refresh_history_view()

    def refresh_model_view(self) -> None:
        if not hasattr(self, "model_view_listbox"):
            return
        self.model_view_listbox.delete(0, "end")
        if not self.models:
            self.model_view_listbox.insert("end", "No local models discovered yet. Refresh the model list from the dashboard.")
            return
        for model in self.models.values():
            assessment = self.assess_model(model).replace(chr(10), " · ")
            self.model_view_listbox.insert("end", f"{model.name}   |   {model.provider.upper()}   |   {assessment}")

    def refresh_results_view(self) -> None:
        if not hasattr(self, "results_view_text"):
            return
        rows = self.session.store.list()
        text = "\n".join(
            f"{row.get('created_at', 'UNKNOWN')}  |  {row.get('benchmark', 'UNKNOWN')}  |  {row.get('status', 'UNKNOWN')}"
            for row in rows[-20:]
        ) or "No benchmark results saved yet."
        self.results_view_text.configure(state="normal")
        self.results_view_text.delete("1.0", "end")
        self.results_view_text.insert("end", text)
        self.results_view_text.configure(state="disabled")

    def refresh_history_view(self) -> None:
        if not hasattr(self, "history_view_listbox"):
            return
        self.history_view_listbox.delete(0, "end")
        rows = self.session.store.list()
        if not rows:
            self.history_view_listbox.insert("end", "No benchmark runs have been saved yet.")
            return
        for row in reversed(rows[-20:]):
            self.history_view_listbox.insert("end", f"{row.get('created_at', 'UNKNOWN')}  ·  {row.get('benchmark', 'UNKNOWN')}  ·  {row.get('status', 'UNKNOWN')}")

    def create_sidebar(self, parent: tk.Widget) -> None:
        sidebar = tk.Frame(
            parent,
            bg=COLORS["surface"],
            width=196,
            highlightbackground=COLORS["line"],
            highlightthickness=1,
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=COLORS["surface"])
        brand.pack(fill="x", padx=15, pady=(17, 24))
        self.brand_mark = tk.Canvas(brand, width=42, height=42, bg=COLORS["surface"], bd=0, highlightthickness=0)
        self.brand_mark.pack(side="left", padx=(0, 9))
        self.brand_mark.create_oval(4, 4, 38, 38, outline=COLORS["line_strong"], width=1)
        self.brand_orbit = self.brand_mark.create_arc(7, 7, 35, 35, start=15, extent=120, outline=COLORS["accent"], width=2, style="arc")
        self.brand_mark.create_polygon(21, 11, 24, 18, 31, 21, 24, 24, 21, 31, 18, 24, 11, 21, 18, 18, fill=COLORS["text"], outline="")
        logo_copy = tk.Frame(brand, bg=COLORS["surface"])
        logo_copy.pack(side="left", anchor="center")
        tk.Label(logo_copy, text="AETHERION", bg=COLORS["surface"], fg=COLORS["text"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(logo_copy, text="LOCAL MODEL LAB", bg=COLORS["surface"], fg=COLORS["quiet"], font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(3, 0))

        tk.Label(sidebar, text="WORKSPACE", bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["section"], padx=15).pack(anchor="w", pady=(0, 7))
        self.nav_buttons: dict[str, tk.Button] = {}
        navigation = [
            ("Overview", "dashboard", "▦"),
            ("Benchmarks", "benchmarks", "◉"),
            ("Models", "models", "◇"),
            ("Results", "results", "▤"),
            ("Hardware", "hardware", "⌘"),
            ("History", "history", "◷"),
            ("Settings", "settings", "⚙"),
        ]
        for label, view, icon in navigation:
            button = tk.Button(
                sidebar,
                text=f"{icon}   {label}",
                command=lambda view_name=view: self.focus_section(view_name),
                bg=COLORS["surface"],
                fg=COLORS["muted"],
                activebackground=COLORS["surface_interactive"],
                activeforeground=COLORS["text"],
                relief="flat",
                bd=0,
                anchor="w",
                font=("Segoe UI", 9, "bold"),
                padx=14,
                pady=10,
                cursor="hand2",
                highlightthickness=0,
            )
            button.pack(fill="x", padx=8, pady=2)
            self.nav_buttons[view] = button
            button.bind(
                "<Enter>",
                lambda _event, widget=button, view_name=view: widget.configure(
                    bg=COLORS["surface_interactive"] if view_name == self.active_view else COLORS["surface_elevated"],
                    fg=COLORS["text"],
                ),
            )
            button.bind(
                "<Leave>",
                lambda _event, widget=button, view_name=view: widget.configure(
                    bg=COLORS["surface_interactive"] if view_name == self.active_view else COLORS["surface"],
                    fg=COLORS["text"] if view_name == self.active_view else COLORS["muted"],
                ),
            )
        self.nav_buttons["dashboard"].configure(bg=COLORS["surface_interactive"], fg=COLORS["text"])
        self.active_view = "dashboard"

        footer = tk.Frame(sidebar, bg=COLORS["surface"])
        footer.pack(side="bottom", fill="x", padx=14, pady=14)
        tk.Frame(footer, bg=COLORS["line"], height=1).pack(fill="x", pady=(0, 10))
        tk.Label(footer, text="PRIVATE BY DESIGN", bg=COLORS["surface"], fg=COLORS["accent"], font=FONTS["section"]).pack(anchor="w")
        tk.Label(footer, text="Runs and results stay local.", bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["small"]).pack(anchor="w", pady=(4, 0))
        if self.auth_session is not None:
            expiry = self.auth_session.expires_at.strftime("%Y-%m-%d") if self.auth_session.expires_at else "NO EXPIRY"
            account_state = "OFFLINE GRACE" if self.auth_session.offline else self.auth_session.plan.upper()
            tk.Label(footer, text=f"ACCOUNT · {self.auth_session.username.upper()}", bg=COLORS["surface"], fg=COLORS["success"], font=FONTS["section"]).pack(anchor="w", pady=(11, 0))
            tk.Label(footer, text=f"{account_state} · {expiry}", bg=COLORS["surface"], fg=COLORS["quiet"], font=FONTS["small"]).pack(anchor="w", pady=(3, 0))
            self._button(footer, "SIGN OUT", self.sign_out).pack(fill="x", pady=(8, 0))

    def focus_section(self, view: str) -> None:
        labels = {
            "dashboard": "DASHBOARD",
            "benchmarks": "BENCHMARK LAB",
            "models": "MODEL LIBRARY",
            "results": "RESULTS",
            "hardware": "SYSTEM PROFILE",
            "history": "HISTORY",
            "settings": "SETTINGS",
        }
        self.active_view = view
        self.section_var.set(labels.get(view, "DASHBOARD"))
        for name, button in self.nav_buttons.items():
            active = name == view
            button.configure(
                bg=COLORS["surface_interactive"] if active else COLORS["surface"],
                fg=COLORS["text"] if active else COLORS["muted"],
                highlightbackground=COLORS["accent"] if active else COLORS["surface"],
                highlightthickness=1 if active else 0,
            )
        for frame in self.views.values():
            frame.pack_forget()
        self.views.get(view, self.dashboard_view).pack(fill="both", expand=True)

    @staticmethod
    def create_glass_panel(parent: tk.Widget) -> tk.Frame:
        return tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            bd=0,
        )


    def animate_brand_mark(self) -> None:
        if self.closing:
            return
        self.brand_phase = (self.brand_phase + 8) % 360
        self.brand_mark.itemconfigure(self.brand_orbit, start=self.brand_phase)
        self.root.after(90, self.animate_brand_mark)

    @staticmethod
    def format_hardware(hardware: dict[str, Any]) -> str:
        os_info = hardware.get("os", {})
        cpu = hardware.get("cpu", {})
        memory = hardware.get("memory", {})
        gpus = hardware.get("gpu", [])
        gpu = next((item for item in gpus if item.get("name") != "UNKNOWN"), None)
        lines = [
            f"OS       {os_info.get('name', 'UNKNOWN')} {os_info.get('version', '')} ({os_info.get('architecture', 'UNKNOWN')})",
            f"CPU      {cpu.get('model', 'UNKNOWN')} · {cpu.get('cores') or 'N/A'} cores / {cpu.get('threads') or 'N/A'} threads",
            f"MEMORY   {memory.get('total_gb') if memory.get('total_gb') is not None else 'N/A'} GB total · {memory.get('available_gb') if memory.get('available_gb') is not None else 'N/A'} GB available",
            f"GPU      {gpu.get('name', 'Not detected') if gpu else 'Not detected'}",
        ]
        return "\n".join(lines)

    def update_model_details(self) -> None:
        model = self.models.get(self.model_var.get())
        if model is None:
            self.model_details.configure(text="No model selected")
            return
        size = f"{model.size_bytes / (1024 ** 3):.2f} GB" if model.size_bytes else "Size unavailable"
        details = model.details
        quantization = details.get("quantization_level") or details.get("format") or "Precision unavailable"
        digest = details.get("digest")
        digest_text = f" · {digest[:12]}" if digest else ""
        recommendation = "RECOMMENDED FOR THIS HARDWARE" if model.name == self.recommended_model_name else "ALTERNATIVE MODEL"
        runability = self.assess_model(model)
        fit_summary = self.model_fit_summary(runability)
        self.model_details.configure(
            text=f"{model.provider.upper()}  ·  {size}\n{quantization}{digest_text}\n"
                 f"ESTIMATED FIT: {fit_summary}\n{recommendation}\n{runability}",
            fg="#C4CFD9",
        )

    def update_suite_details(self) -> None:
        suite = self.category_var.get()
        self.suite_details.configure(text=TASK_SUITE_DESCRIPTIONS.get(suite, "Runs the selected local validation tasks."))

    def update_overview(self, key: str, value: str) -> None:
        variable = self.overview_vars.get(key)
        if variable is not None:
            variable.set(value)

    def model_recommendation_key(self, model: ModelInfo) -> tuple[int, int]:
        assessment = self.assess_model(model)
        if assessment.startswith("DIRECT RUN: YES · GPU"):
            priority = 0
        elif assessment.startswith("DIRECT RUN: YES"):
            priority = 1
        else:
            priority = 2
        return priority, model.size_bytes or 0

    def assess_model(self, model: ModelInfo) -> str:
        runtime_ready = model.provider == "ollama" or importlib.util.find_spec("llama_cpp") is not None
        if not runtime_ready:
            return "DIRECT RUN: NO · Install llama-cpp-python for GGUF"

        if model.size_bytes is None:
            return "DIRECT RUN: UNKNOWN · Model size unavailable"

        model_gb = model.size_bytes / (1024 ** 3)
        required_gb = max(model_gb * 1.25, 1.0)
        available_gb = self.session.hardware.get("memory", {}).get("available_gb")
        gpus = self.session.hardware.get("gpu", [])
        vram_gb = next(
            (gpu.get("vram_gb") for gpu in gpus if isinstance(gpu.get("vram_gb"), (int, float))),
            None,
        )
        vram_text = f"{vram_gb:.1f} GB VRAM" if isinstance(vram_gb, (int, float)) else "VRAM unavailable"

        if isinstance(available_gb, (int, float)) and available_gb < required_gb:
            return f"DIRECT RUN: NO\nRAM: {available_gb:.1f} GB available / ~{required_gb:.1f} GB needed\nVRAM: {vram_text}"

        if isinstance(vram_gb, (int, float)) and model_gb <= vram_gb * 0.9:
            return f"DIRECT RUN: YES · GPU\nRAM: ~{required_gb:.1f} GB needed\nVRAM: {vram_text} · sufficient"
        if isinstance(vram_gb, (int, float)):
            return f"DIRECT RUN: YES · CPU fallback\nRAM: ~{required_gb:.1f} GB needed\nVRAM: {vram_text} · insufficient for full load"
        return f"DIRECT RUN: YES · CPU\nRAM: ~{required_gb:.1f} GB needed\nVRAM: unavailable"

    @staticmethod
    def model_fit_summary(assessment: str) -> str:
        if assessment.startswith("DIRECT RUN: YES · GPU"):
            return "LIKELY TO RUN · GPU"
        if assessment.startswith("DIRECT RUN: YES · CPU fallback"):
            return "LIKELY TO RUN · CPU fallback"
        if assessment.startswith("DIRECT RUN: YES"):
            return "LIKELY TO RUN · CPU"
        if assessment.startswith("DIRECT RUN: NO"):
            if assessment.startswith("DIRECT RUN: NO ·"):
                return "NOT READY · required runtime missing"
            return "NOT RECOMMENDED · available RAM is below estimate"
        return "CANNOT CONFIRM · model size unavailable"

    def browse_model_folder(self) -> None:
        current_path = Path(self.model_path_var.get())
        initial_dir = current_path if current_path.is_dir() else Path.home()
        selected = filedialog.askdirectory(parent=self.root, initialdir=str(initial_dir), title="Choose GGUF model folder")
        if not selected:
            return
        self.session.gguf_provider.set_models_dir(selected)
        self.model_path_var.set(selected)
        self.refresh_models()

    def dependency_status(self) -> tuple[str, list[str]]:
        ollama_status = "READY" if shutil.which("ollama") else "NOT FOUND"
        llama_status = "READY" if importlib.util.find_spec("llama_cpp") else "NOT FOUND"
        psutil_status = "READY" if importlib.util.find_spec("psutil") else "OPTIONAL"
        missing = []
        if not shutil.which("ollama"):
            missing.append("Ollama")
        if importlib.util.find_spec("llama_cpp") is None:
            missing.append("llama-cpp-python")
        text = f"REQUIREMENTS\nOLLAMA       {ollama_status}\nGGUF RUNTIME {llama_status}\nTELEMETRY    {psutil_status}"
        return text, missing

    def refresh_dependency_status(self) -> None:
        text, missing = self.dependency_status()
        self.requirements_label.configure(text=text, fg="#6DE5C1" if not missing else "#C4CFD9")
        self.install_requirements_button.configure(state="normal" if missing else "disabled")

    def download_missing_dependencies(self) -> None:
        _, missing = self.dependency_status()
        if not missing:
            self.refresh_dependency_status()
            return
        if "Ollama" in missing:
            installer_url = "https://ollama.com/download/OllamaSetup.exe" if sys.platform == "win32" else "https://ollama.com/download"
            installer_dir = Path.home() / "Downloads" / "Aetherion-Installers"
            installer_dir.mkdir(parents=True, exist_ok=True)
            installer_path = installer_dir / "OllamaSetup.exe"
            if sys.platform == "win32":
                self.install_requirements_button.configure(state="disabled")
                self.requirements_label.configure(text="Downloading Ollama installer...", fg="#6DE5C1")

                def download() -> None:
                    try:
                        urlretrieve(installer_url, installer_path)
                        self.events.put(("installer_downloaded", str(installer_path)))
                    except OSError as exc:
                        self.events.put(("installer_download_error", str(exc)))

                threading.Thread(target=download, daemon=True).start()
            else:
                webbrowser.open(installer_url)
        if "llama-cpp-python" in missing and not getattr(sys, "frozen", False):
            self.install_requirements_button.configure(state="disabled")
            self.requirements_label.configure(text="Installing llama-cpp-python...", fg="#6DE5C1")

            def install() -> None:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "llama-cpp-python"], check=True)
                    self.events.put(("dependencies", "llama-cpp-python installed. Restart the client to load it."))
                except (OSError, subprocess.CalledProcessError) as exc:
                    self.events.put(("dependencies_error", str(exc)))

            threading.Thread(target=install, daemon=True).start()
        elif "llama-cpp-python" in missing:
            self.requirements_label.configure(
                text="GGUF runtime is not bundled in this desktop build.\nInstall the matching runtime package before using GGUF models.",
                fg="#6DE5C1",
            )

    def open_model_downloader(self) -> None:
        if self.download_window is not None and self.download_window.winfo_exists():
            self.download_window.focus_force()
            return
        window = tk.Toplevel(self.root)
        self.download_window = window
        window.title("Download a model")
        window.geometry("580x390")
        window.minsize(520, 350)
        window.configure(bg="#121C27")
        window.transient(self.root)

        content = tk.Frame(window, bg="#121C27")
        content.pack(fill="both", expand=True, padx=24, pady=22)
        tk.Label(content, text="DOWNLOAD A MODEL", bg="#121C27", fg="#6DE5C1", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(
            content,
            text="Choose a catalog model or paste a direct HTTPS link to an external .gguf file. The file is saved into your selected model folder.",
            bg="#121C27",
            fg="#94A6B5",
            font=("Segoe UI", 9),
            justify="left",
            wraplength=510,
        ).pack(anchor="w", pady=(5, 16))

        tk.Label(content, text="CATALOG (OPTIONAL)", bg="#121C27", fg="#94A6B5", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        catalog_var = tk.StringVar(value=next(iter(MODEL_DOWNLOAD_CATALOG)))
        catalog_menu = ttk.Combobox(content, textvariable=catalog_var, values=list(MODEL_DOWNLOAD_CATALOG), state="readonly", style="Aetherion.TCombobox")
        catalog_menu.pack(fill="x", pady=(7, 14))

        tk.Label(content, text="MODEL FILE URL (.GGUF)", bg="#121C27", fg="#94A6B5", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        url_var = tk.StringVar(value=MODEL_DOWNLOAD_CATALOG[catalog_var.get()])
        url_entry = tk.Entry(content, textvariable=url_var, bg="#0D141D", fg="#D9E4EE", insertbackground="#F0F0F0", relief="flat", highlightbackground="#344B5D", highlightthickness=1, font=("Segoe UI", 8))
        url_entry.pack(fill="x", pady=(7, 14), ipady=7)
        catalog_menu.bind("<<ComboboxSelected>>", lambda _event: url_var.set(MODEL_DOWNLOAD_CATALOG[catalog_var.get()]))

        destination = str(self.session.gguf_provider.models_dir)
        tk.Label(content, text=f"SAVED TO  {destination}", bg="#121C27", fg="#728393", font=("Segoe UI", 8), wraplength=510, justify="left").pack(anchor="w")
        self.download_progress = ttk.Progressbar(content, mode="determinate", maximum=100, value=0, style="Aetherion.Horizontal.TProgressbar")
        self.download_progress.pack(fill="x", pady=(16, 5))
        self.download_status = tk.Label(content, text="Ready to download", bg="#121C27", fg="#94A6B5", anchor="w", font=("Segoe UI", 8))
        self.download_status.pack(fill="x")
        download_button = tk.Button(content, text="DOWNLOAD MODEL", command=lambda: self.download_model(url_var.get(), download_button), bg="#6DE5C1", fg="#0D141D", activebackground="#F0F0F0", activeforeground="#0D141D", relief="flat", font=("Segoe UI", 9, "bold"), padx=12, pady=10, cursor="hand2")
        download_button.pack(anchor="e", pady=(14, 0))
        self.download_button = download_button

    def download_model(self, url: str, button: tk.Button) -> None:
        parsed = urlparse(url.strip())
        filename = Path(unquote(parsed.path)).name
        if parsed.scheme != "https" or not filename.lower().endswith(".gguf"):
            self.download_status.configure(text="Use a valid HTTPS URL ending in .gguf", fg="#FF9292")
            return
        target_dir = self.session.gguf_provider.models_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename
        button.configure(state="disabled")
        self.download_progress.configure(value=0)
        self.download_status.configure(text=f"Downloading {filename}...", fg="#6DE5C1")

        def run_download() -> None:
            temporary_path = target_path.with_suffix(target_path.suffix + ".part")
            try:
                request = Request(url, headers={"User-Agent": "Aetherion-Client/0.1"})
                with urlopen(request, timeout=30) as response, temporary_path.open("wb") as output:
                    total = int(response.headers.get("Content-Length") or 0)
                    downloaded = 0
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        output.write(chunk)
                        downloaded += len(chunk)
                        self.events.put(("model_download_progress", (downloaded, total, filename)))
                temporary_path.replace(target_path)
                self.events.put(("model_download_complete", str(target_path)))
            except (OSError, ValueError) as exc:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
                self.events.put(("model_download_error", str(exc)))

        threading.Thread(target=run_download, daemon=True).start()

    def append_output(self, text: str, tag: str | None = None) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", text, tag)
        self.output.see("end")
        self.output.configure(state="disabled")

    def refresh_models(self) -> None:
        if self.busy:
            return
        self.busy = True
        stop_event = threading.Event()
        self.benchmark_stop_event = stop_event
        self.refresh_button.configure(state="disabled")
        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.model_menu.configure(state="disabled")
        self.status_var.set("LOOKING FOR LOCAL MODELS")
        self.update_overview("runtime_metric", "Scanning providers")
        self.update_overview("models_metric", "Discovering models")
        self.result_status.configure(text="Checking local model runtimes on this computer…", fg="#6DE5C1")
        self.progress.configure(value=0)
        self.progress_text.configure(text="Checking local model runtimes")

        def load_models() -> None:
            try:
                self.events.put(("models", (self.session.provider.discover(), None)))
            except Exception as exc:
                self.events.put(("models", ([], str(exc))))

        threading.Thread(target=load_models, daemon=True).start()

    def run_selected_benchmark(self) -> None:
        if self.auth_session is None:
            self.show_license_gate("Sign in to continue.")
            return
        if dt.datetime.now(dt.UTC) >= self.auth_session.offline_until:
            self.auth_session = None
            clear_cached_session()
            self.show_license_gate("The offline access period has ended. Connect and sign in again.")
            return
        model_name = self.model_var.get()
        model = self.models.get(model_name)
        if model is None or self.busy:
            return
        assessment = self.assess_model(model)
        if assessment.startswith("DIRECT RUN: NO"):
            self.status_var.set("MODEL NOT READY")
            self.result_status.configure(text=assessment, fg="#FF9292")
            self.append_output(f"\nModel cannot run on this machine:\n{assessment}\n", "bad")
            return
        category = None if self.category_var.get() == "All tasks" else self.category_var.get()
        self.busy = True
        stop_event = threading.Event()
        self.benchmark_stop_event = stop_event
        self.refresh_button.configure(state="disabled")
        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.model_menu.configure(state="disabled")
        self.category_menu.configure(state="disabled")
        self.status_var.set("BENCHMARK RUNNING")
        self.result_status.configure(text=f"Running {category or 'all'} tasks on {model_name}…", fg="#6DE5C1")
        self.progress.configure(value=0)
        self.progress_text.configure(text="Preparing benchmark tasks")
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self.append_output(f"Model: {model_name}\nSuite: {category or 'all tasks'}\n\n", "muted")

        def run() -> None:
            try:
                results = self.session.engine.run(
                    model_name,
                    category,
                    progress_callback=lambda index, total, result: self.events.put(("progress", (index, total, result))),
                    stop_event=stop_event,
                )
                generated = [result for result in results if result.error is None]
                rates = [result.metrics["tokens_per_second"] for result in generated if result.metrics.get("tokens_per_second") is not None]
                summary: dict[str, Any] = {
                    "task_count": len(results),
                    "generated_tasks": len(generated),
                    "passed_checks": sum(result.passed is True for result in generated),
                    "failed_checks": sum(result.passed is False for result in generated),
                    "errors": sum(result.error is not None for result in results),
                    "average_tokens_per_second": round(sum(rates) / len(rates), 3) if rates else None,
                }
                stopped = self.session.engine.last_run_stopped
                status = "stopped" if stopped else "failed" if not generated else "partial" if summary["errors"] else "complete"
                record = ClientRunRecord(
                    run_id=generate_run_id(),
                    benchmark=model_name,
                    model_version=str(model.details.get("digest") or model_name),
                    runtime=model.provider,
                    precision=str(model.details.get("quantization_level") or "UNKNOWN"),
                    hardware=self.session.hardware,
                    result=summary,
                    status=status,
                    notes={"benchmark_results_file": str(self.session.engine.last_result_path) if self.session.engine.last_result_path else None,
                           "stopped_by_user": stopped},
                )
                record_path = self.session.store.save(record)
                self.events.put(("complete", (summary, status, record_path, self.session.engine.last_result_path)))
            except Exception as exc:
                self.events.put(("run_error", str(exc)))

        threading.Thread(target=run, daemon=True).start()

    def process_events(self) -> None:
        if self.closing:
            return
        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "models":
                models, error = payload
                models.sort(key=self.model_recommendation_key)
                self.models = {model.name: model for model in models}
                names = list(self.models)
                self.recommended_model_name = names[0] if names else None
                self.refresh_model_view()
                self.model_menu.configure(values=names, state="readonly" if names else "disabled")
                if names:
                    self.model_var.set(names[0])
                    self.update_model_details()
                    self.benchmark_view_config.configure(text=f"{names[0]}  ·  {self.models[names[0]].provider.upper()}")
                    runtimes = ", ".join(sorted({model.provider.upper() for model in models}))
                    self.status_var.set(f"{runtimes} READY · {len(names)} MODEL(S)")
                    self.update_overview("runtime_metric", runtimes)
                    self.update_overview("models_metric", f"{len(names)} available")
                    self.result_status.configure(text="Model list refreshed. Select a task suite and run it.", fg="#9BE0B5")
                    self.progress_text.configure(text=f"{len(names)} local model(s) ready")
                    self.run_button.configure(state="normal")
                elif error:
                    self.model_var.set("")
                    self.status_var.set("LOCAL RUNTIMES UNAVAILABLE")
                    self.result_status.configure(text="No local model runtime is responding. Check Ollama or the GGUF runtime. " + error, fg="#FF9292")
                    self.progress_text.configure(text="Connection unavailable")
                    self.append_output("No local model runtime responded.\n" + error + "\n", "bad")
                else:
                    self.model_var.set("")
                    self.status_var.set("NO LOCAL MODELS")
                    self.update_overview("runtime_metric", "No providers")
                    self.update_overview("models_metric", "0 available")
                    self.result_status.configure(text="No local models were found. Install an Ollama model or place a GGUF model in the local models folder.", fg="#6DE5C1")
                    self.progress_text.configure(text="No local models detected")
                self.category_menu.configure(state="readonly")
                self.refresh_button.configure(state="normal")
                self.busy = False
            elif event == "progress":
                index, total, result = payload
                self.progress.configure(value=(index / total) * 100 if total else 0)
                self.progress_text.configure(text=f"Task {index} of {total} complete")
                self.show_task_result(index, total, result)
            elif event == "complete":
                summary, status, record_path, result_path = payload
                color = "#9BE0B5" if status == "complete" else "#FF9292" if status == "failed" else "#F2C879" if status == "stopped" else "#6DE5C1"
                self.status_var.set(f"RUN {status.upper()}")
                self.update_overview("last_run_metric", f"{status.upper()} · {summary['passed_checks']}/{summary['task_count']}")
                self.result_status.configure(text=f"{summary['passed_checks']} passed · {summary['failed_checks']} failed · {summary['errors']} errors\nSaved locally: {record_path}", fg=color)
                self.progress.configure(value=100)
                self.progress_text.configure(text="Benchmark stopped" if status == "stopped" else "Benchmark complete")
                average = summary["average_tokens_per_second"]
                average_text = f"{average:.2f} tokens/s" if average is not None else "Unavailable"
                self.run_metrics.configure(
                    text=(
                        f"TASKS       {summary['task_count']}\n"
                        f"PASSED      {summary['passed_checks']}\n"
                        f"FAILED      {summary['failed_checks']}\n"
                        f"ERRORS      {summary['errors']}\n"
                        f"AVG SPEED   {average_text}"
                    ),
                    fg="#6DE5C1" if status == "complete" else "#C4CFD9",
                )
                self.refresh_results_view()
                self.refresh_history_view()
                self.append_output(f"\nSummary: {summary['passed_checks']} passed, {summary['failed_checks']} failed, {summary['errors']} errors.\n", "good" if status == "complete" else "bad" if status == "failed" else "muted")
                self.append_output(f"Run record: {record_path}\n")
                if result_path:
                    self.append_output(f"Task results: {result_path}\n", "muted")
                self.busy = False
                self.refresh_button.configure(state="normal")
                self.model_menu.configure(state="readonly" if self.models else "disabled")
                self.category_menu.configure(state="readonly")
                self.run_button.configure(state="normal" if self.models else "disabled")
                self.stop_button.configure(state="disabled")
                self.benchmark_stop_event = None
            elif event == "run_error":
                self.status_var.set("RUN FAILED")
                self.result_status.configure(text=str(payload), fg="#FF9292")
                self.progress_text.configure(text="Benchmark stopped with an error")
                self.run_metrics.configure(text="RUN FAILED\nReview the benchmark trace for details.", fg="#FF9292")
                self.append_output(f"\nBenchmark could not finish: {payload}\n", "bad")
                self.busy = False
                self.refresh_button.configure(state="normal")
                self.model_menu.configure(state="readonly" if self.models else "disabled")
                self.category_menu.configure(state="readonly")
                self.run_button.configure(state="normal" if self.models else "disabled")
                self.stop_button.configure(state="disabled")
                self.benchmark_stop_event = None
            elif event == "dependencies":
                self.requirements_label.configure(text=str(payload), fg="#9BE0B5")
                self.refresh_dependency_status()
            elif event == "dependencies_error":
                self.requirements_label.configure(text=f"Runtime installation failed\n{payload}", fg="#FF9292")
                self.install_requirements_button.configure(state="normal")
            elif event == "installer_downloaded":
                installer_path = Path(str(payload))
                self.requirements_label.configure(
                    text=f"Ollama installer downloaded\n{installer_path}",
                    fg="#9BE0B5",
                )
                self.install_requirements_button.configure(state="normal", text="DOWNLOAD AGAIN")
                self.append_output(f"\nInstaller ready: {installer_path}\nRun it to install Ollama.\n", "good")
                if messagebox.askyesno(
                    "Install Ollama",
                    "Ollama installer downloaded. Launch it now to install Ollama?",
                    parent=self.root,
                ):
                    try:
                        subprocess.Popen([str(installer_path)], shell=False)
                        self.requirements_label.configure(text=f"Ollama installer launched\n{installer_path}", fg="#9BE0B5")
                    except OSError as exc:
                        self.requirements_label.configure(text=f"Could not launch installer\n{exc}", fg="#FF9292")
            elif event == "installer_download_error":
                self.requirements_label.configure(text=f"Installer download failed\n{payload}", fg="#FF9292")
                self.install_requirements_button.configure(state="normal", text="RETRY DOWNLOAD")
            elif event == "model_download_progress":
                downloaded, total, filename = payload
                if self.download_progress is not None and self.download_status is not None:
                    progress = downloaded / total * 100 if total else 0
                    self.download_progress.configure(value=progress)
                    downloaded_mb = downloaded / (1024 ** 2)
                    total_text = f" / {total / (1024 ** 2):.1f} MB" if total else ""
                    self.download_status.configure(text=f"{filename}: {downloaded_mb:.1f} MB{total_text}")
            elif event == "model_download_complete":
                if self.download_progress is not None and self.download_status is not None:
                    self.download_progress.configure(value=100)
                    self.download_status.configure(text=f"Downloaded: {payload}", fg="#9BE0B5")
                if self.download_button is not None and self.download_button.winfo_exists():
                    self.download_button.configure(state="normal")
                self.append_output(f"\nModel downloaded: {payload}\n", "good")
                self.refresh_models()
            elif event == "model_download_error":
                if self.download_status is not None:
                    self.download_status.configure(text=f"Download failed: {payload}", fg="#FF9292")
                if self.download_button is not None and self.download_button.winfo_exists():
                    self.download_button.configure(state="normal")
        self.root.after(100, self.process_events)

    def show_task_result(self, index: int, total: int, result: BenchmarkResult) -> None:
        prefix = f"[{index}/{total}] {result.category}/{result.task}: "
        if result.error:
            self.append_output(prefix + f"ERROR · {result.error}\n", "bad")
            return
        rate = result.metrics.get("tokens_per_second")
        rate_text = f"{rate:.2f} tokens/s" if rate is not None else "speed unavailable"
        check = "PASS" if result.passed is True else "CHECK FAILED" if result.passed is False else "UNSCORED"
        tag = "good" if result.passed is True else "bad" if result.passed is False else "muted"
        self.append_output(prefix + f"{check} · {rate_text}\n", tag)

    def stop_benchmark(self) -> None:
        if self.benchmark_stop_event is None:
            return
        self.benchmark_stop_event.set()
        self.stop_button.configure(state="disabled")
        self.status_var.set("STOPPING BENCHMARK")
        self.result_status.configure(text="Stopping after the active generation responds…", fg="#F2C879")
        self.progress_text.configure(text="Waiting for the current model stream to stop")
        self.append_output("\nStop requested. The active task will be discarded; completed tasks will be saved.\n", "muted")

    def open_results_folder(self) -> None:
        self.session.results_dir.mkdir(parents=True, exist_ok=True)
        command = "explorer" if sys.platform == "win32" else "open" if sys.platform == "darwin" else "xdg-open"
        try:
            subprocess.Popen([command, str(self.session.results_dir)])
        except OSError as exc:
            self.result_status.configure(text=f"Could not open results folder: {exc}", fg="#FF9292")

    def close(self) -> None:
        if self.closing:
            return
        if self.busy and not messagebox.askyesno(
            "Benchmark in progress",
            "A benchmark is still running. Close the client anyway?",
            parent=self.root,
        ):
            return
        self.closing = True
        if self.benchmark_stop_event is not None:
            self.benchmark_stop_event.set()
        self.root.destroy()


def launch_desktop_app() -> None:
    root = tk.Tk()
    AetherionDesktopClient(root)
    root.mainloop()


if __name__ == "__main__":
    launch_desktop_app()
