from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk
from typing import Any

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from local_ai_benchmark.client.core import ClientRunRecord, generate_run_id
    from local_ai_benchmark.client.hardware import detect_hardware
    from local_ai_benchmark.client.storage import LocalResultStore
    from local_ai_benchmark.engine import BenchmarkEngine
    from local_ai_benchmark.models import BenchmarkResult, ModelInfo
    from local_ai_benchmark.providers import OllamaProvider
    from local_ai_benchmark.tasks import TASKS
else:
    from .core import ClientRunRecord, generate_run_id
    from .hardware import detect_hardware
    from .storage import LocalResultStore
    from ..engine import BenchmarkEngine
    from ..models import BenchmarkResult, ModelInfo
    from ..providers import OllamaProvider
    from ..tasks import TASKS


@dataclass
class DesktopSession:
    hardware: dict[str, Any]
    store: LocalResultStore
    provider: OllamaProvider
    engine: BenchmarkEngine
    results_dir: Path

    @classmethod
    def create(cls, base_dir: str | Path | None = None) -> "DesktopSession":
        if base_dir is None:
            data_root = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Aetherion" / "results"
        else:
            data_root = Path(base_dir)
        provider = OllamaProvider(timeout=120)
        return cls(
            hardware=detect_hardware(),
            store=LocalResultStore(data_root / "client"),
            provider=provider,
            engine=BenchmarkEngine(provider, data_root),
            results_dir=data_root,
        )


class AetherionDesktopClient:
    """Desktop interface for discovering local Ollama models and benchmarking them."""

    def __init__(self, root: tk.Tk | None = None, base_dir: str | Path | None = None):
        self.root = root or tk.Tk()
        self.root.title("AETHERION Client")
        self.root.geometry("1040x760")
        self.root.minsize(820, 620)
        self.root.configure(bg="#071018")
        self.session = DesktopSession.create(base_dir)
        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.models: dict[str, ModelInfo] = {}
        self.busy = False
        self.closing = False
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self.process_events)
        self.refresh_models()

    def build_ui(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Aetherion.TCombobox", fieldbackground="#101923", background="#101923", foreground="#EAF4FF", arrowcolor="#D6B36A")
        style.map("Aetherion.TCombobox", fieldbackground=[("readonly", "#101923")], foreground=[("readonly", "#EAF4FF")])

        self.container = tk.Frame(self.root, bg="#071018")
        self.container.pack(fill="both", expand=True, padx=24, pady=22)

        header = tk.Frame(self.container, bg="#071018")
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="AETHERION", bg="#071018", fg="#F2F4F7", font=("Segoe UI", 25, "bold")).pack(anchor="w")
        tk.Label(header, text="LOCAL MODEL BENCHMARK", bg="#071018", fg="#D6B36A", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        self.status_var = tk.StringVar(value="CONNECTING TO OLLAMA")
        self.status = tk.Label(header, textvariable=self.status_var, bg="#101923", fg="#D6B36A", font=("Segoe UI", 10, "bold"), padx=12, pady=7)
        self.status.pack(anchor="e", side="right", pady=(0, 8))

        content = tk.Frame(self.container, bg="#0B1420", highlightbackground="#263443", highlightthickness=1)
        content.pack(fill="both", expand=True)
        self.left = tk.Frame(content, bg="#0B1420")
        self.left.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.right = tk.Frame(content, bg="#0B1420", width=300)
        self.right.pack(side="right", fill="y", padx=(0, 20), pady=20)
        self.right.pack_propagate(False)

        tk.Label(self.left, text="YOUR SYSTEM", bg="#0B1420", fg="#D6B36A", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.hardware_text = tk.Text(self.left, height=6, bg="#071018", fg="#EAF4FF", bd=0, wrap="word", padx=12, pady=10, font=("Consolas", 10))
        self.hardware_text.pack(fill="x", pady=(8, 18))
        self.hardware_text.insert("end", self.format_hardware(self.session.hardware))
        self.hardware_text.configure(state="disabled")

        tk.Label(self.left, text="RUN OUTPUT", bg="#0B1420", fg="#D6B36A", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        output_frame = tk.Frame(self.left, bg="#071018")
        output_frame.pack(fill="both", expand=True, pady=(8, 0))
        self.output = tk.Text(output_frame, bg="#071018", fg="#EAF4FF", insertbackground="#EAF4FF", bd=0, wrap="word", padx=12, pady=10, font=("Consolas", 9), state="disabled")
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output.yview)
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.output.tag_configure("good", foreground="#91E2B2")
        self.output.tag_configure("bad", foreground="#FF9D9D")
        self.output.tag_configure("muted", foreground="#95A5B5")
        self.append_output("Choose an installed Ollama model and run a benchmark. Results are saved locally.\n", "muted")

        tk.Label(self.right, text="BENCHMARK SETUP", bg="#0B1420", fg="#D6B36A", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 14))
        tk.Label(self.right, text="Installed model", bg="#0B1420", fg="#EAF4FF", font=("Segoe UI", 10)).pack(anchor="w")
        self.model_var = tk.StringVar()
        self.model_menu = ttk.Combobox(self.right, textvariable=self.model_var, state="disabled", style="Aetherion.TCombobox")
        self.model_menu.pack(fill="x", pady=(6, 14))

        tk.Label(self.right, text="Task suite", bg="#0B1420", fg="#EAF4FF", font=("Segoe UI", 10)).pack(anchor="w")
        self.category_var = tk.StringVar(value="All tasks")
        categories = list(dict.fromkeys(task.category for task in TASKS))
        self.category_menu = ttk.Combobox(self.right, textvariable=self.category_var, values=["All tasks", *categories], state="readonly", style="Aetherion.TCombobox")
        self.category_menu.pack(fill="x", pady=(6, 18))

        self.refresh_button = tk.Button(self.right, text="REFRESH MODELS", command=self.refresh_models, bg="#172432", fg="#EAF4FF", activebackground="#26394A", activeforeground="#FFFFFF", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=10)
        self.refresh_button.pack(fill="x")
        self.run_button = tk.Button(self.right, text="RUN BENCHMARK", command=self.run_selected_benchmark, bg="#D6B36A", fg="#101923", activebackground="#E5C989", activeforeground="#101923", font=("Segoe UI", 11, "bold"), relief="flat", padx=12, pady=12, state="disabled")
        self.run_button.pack(fill="x", pady=(10, 0))
        self.result_status = tk.Label(self.right, text="Waiting for Ollama", bg="#0B1420", fg="#95A5B5", justify="left", anchor="w", wraplength=280)
        self.result_status.pack(anchor="w", fill="x", pady=(18, 14))
        self.open_results_button = tk.Button(self.right, text="OPEN RESULTS FOLDER", command=self.open_results_folder, bg="#172432", fg="#EAF4FF", activebackground="#26394A", activeforeground="#FFFFFF", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=9)
        self.open_results_button.pack(fill="x", side="bottom")

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

    def append_output(self, text: str, tag: str | None = None) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", text, tag)
        self.output.see("end")
        self.output.configure(state="disabled")

    def refresh_models(self) -> None:
        if self.busy:
            return
        self.busy = True
        self.refresh_button.configure(state="disabled")
        self.run_button.configure(state="disabled")
        self.model_menu.configure(state="disabled")
        self.status_var.set("LOOKING FOR LOCAL MODELS")
        self.result_status.configure(text="Checking the Ollama service on this computer…", fg="#D6B36A")

        def load_models() -> None:
            try:
                self.events.put(("models", (self.session.provider.discover(), None)))
            except Exception as exc:
                self.events.put(("models", ([], str(exc))))

        threading.Thread(target=load_models, daemon=True).start()

    def run_selected_benchmark(self) -> None:
        model_name = self.model_var.get()
        model = self.models.get(model_name)
        if model is None or self.busy:
            return
        category = None if self.category_var.get() == "All tasks" else self.category_var.get()
        self.busy = True
        self.refresh_button.configure(state="disabled")
        self.run_button.configure(state="disabled")
        self.model_menu.configure(state="disabled")
        self.category_menu.configure(state="disabled")
        self.status_var.set("BENCHMARK RUNNING")
        self.result_status.configure(text=f"Running {category or 'all'} tasks on {model_name}…", fg="#D6B36A")
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
                status = "failed" if not generated else "partial" if summary["errors"] else "complete"
                record = ClientRunRecord(
                    run_id=generate_run_id(),
                    benchmark=model_name,
                    model_version=str(model.details.get("digest") or model_name),
                    runtime="Ollama",
                    precision=str(model.details.get("quantization_level") or "UNKNOWN"),
                    hardware=self.session.hardware,
                    result=summary,
                    status=status,
                    notes={"benchmark_results_file": str(self.session.engine.last_result_path) if self.session.engine.last_result_path else None},
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
                self.models = {model.name: model for model in models}
                names = list(self.models)
                self.model_menu.configure(values=names, state="readonly" if names else "disabled")
                if names:
                    self.model_var.set(names[0])
                    self.status_var.set(f"OLLAMA READY · {len(names)} MODEL(S)")
                    self.result_status.configure(text="Model list refreshed. Select a task suite and run it.", fg="#91E2B2")
                    self.run_button.configure(state="normal")
                elif error:
                    self.model_var.set("")
                    self.status_var.set("OLLAMA NOT CONNECTED")
                    self.result_status.configure(text="Ollama is not responding. Start the Ollama app, then press Refresh Models. " + error, fg="#FF9D9D")
                    self.append_output("Could not reach Ollama at http://127.0.0.1:11434.\n" + error + "\n", "bad")
                else:
                    self.model_var.set("")
                    self.status_var.set("NO MODELS INSTALLED")
                    self.result_status.configure(text="Ollama is running, but no models are installed. Run `ollama pull <model>` and refresh.", fg="#D6B36A")
                self.category_menu.configure(state="readonly")
                self.refresh_button.configure(state="normal")
                self.busy = False
            elif event == "progress":
                index, total, result = payload
                self.show_task_result(index, total, result)
            elif event == "complete":
                summary, status, record_path, result_path = payload
                color = "#91E2B2" if status == "complete" else "#FF9D9D" if status == "failed" else "#D6B36A"
                self.status_var.set(f"RUN {status.upper()}")
                self.result_status.configure(text=f"{summary['passed_checks']} passed · {summary['failed_checks']} failed · {summary['errors']} errors\nSaved locally: {record_path}", fg=color)
                self.append_output(f"\nSummary: {summary['passed_checks']} passed, {summary['failed_checks']} failed, {summary['errors']} errors.\n", "good" if status == "complete" else "bad" if status == "failed" else "muted")
                self.append_output(f"Run record: {record_path}\n")
                if result_path:
                    self.append_output(f"Task results: {result_path}\n", "muted")
                self.busy = False
                self.refresh_button.configure(state="normal")
                self.model_menu.configure(state="readonly" if self.models else "disabled")
                self.category_menu.configure(state="readonly")
                self.run_button.configure(state="normal" if self.models else "disabled")
            elif event == "run_error":
                self.status_var.set("RUN FAILED")
                self.result_status.configure(text=str(payload), fg="#FF9D9D")
                self.append_output(f"\nBenchmark could not finish: {payload}\n", "bad")
                self.busy = False
                self.refresh_button.configure(state="normal")
                self.model_menu.configure(state="readonly" if self.models else "disabled")
                self.category_menu.configure(state="readonly")
                self.run_button.configure(state="normal" if self.models else "disabled")
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

    def open_results_folder(self) -> None:
        self.session.results_dir.mkdir(parents=True, exist_ok=True)
        command = "explorer" if sys.platform == "win32" else "open" if sys.platform == "darwin" else "xdg-open"
        try:
            subprocess.Popen([command, str(self.session.results_dir)])
        except OSError as exc:
            self.result_status.configure(text=f"Could not open results folder: {exc}", fg="#FF9D9D")

    def close(self) -> None:
        self.closing = True
        self.root.destroy()


def launch_desktop_app() -> None:
    root = tk.Tk()
    AetherionDesktopClient(root)
    root.mainloop()


if __name__ == "__main__":
    launch_desktop_app()
