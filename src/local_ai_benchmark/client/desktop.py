from __future__ import annotations

import importlib.util
import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from urllib.request import urlretrieve
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
    from local_ai_benchmark.client.storage import LocalResultStore
    from local_ai_benchmark.engine import BenchmarkEngine
    from local_ai_benchmark.models import BenchmarkResult, ModelInfo
    from local_ai_benchmark.providers import LlamaCppProvider, OllamaProvider, ProviderRouter
    from local_ai_benchmark.tasks import TASKS
else:
    from .core import ClientRunRecord, generate_run_id
    from .hardware import detect_hardware
    from .storage import LocalResultStore
    from ..engine import BenchmarkEngine
    from ..models import BenchmarkResult, ModelInfo
    from ..providers import LlamaCppProvider, OllamaProvider, ProviderRouter
    from ..tasks import TASKS


TASK_SUITE_DESCRIPTIONS = {
    "All tasks": "Runs general, coding, math, JSON, and Spanish-language checks.",
    "general": "Checks concise factual explanation and instruction following.",
    "coding": "Checks whether the model returns valid Python code for a concrete task.",
    "math": "Checks exact arithmetic and resistance to unnecessary explanation.",
    "json": "Checks strict JSON formatting and schema compliance.",
    "spanish": "Checks Spanish comprehension and concise instruction following.",
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
    """Desktop interface for discovering local Ollama models and benchmarking them."""

    def __init__(self, root: tk.Tk | None = None, base_dir: str | Path | None = None):
        self.root = root or tk.Tk()
        self.root.title("AETHERION Client")
        self.root.geometry("1040x760")
        self.root.minsize(820, 620)
        self.root.configure(bg="#050505")
        self.session = DesktopSession.create(base_dir)
        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.models: dict[str, ModelInfo] = {}
        self.recommended_model_name: str | None = None
        self.busy = False
        self.closing = False
        self.brand_phase = 0
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self.process_events)
        self.animate_brand_mark()
        self.root.after(200, self.refresh_dependency_status)
        self.refresh_models()

    def build_ui(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Aetherion.TCombobox",
            fieldbackground="#111111",
            background="#111111",
            foreground="#E8E8E8",
            arrowcolor="#B8B8B8",
            bordercolor="#3A3A3A",
            lightcolor="#3A3A3A",
            darkcolor="#3A3A3A",
            padding=(10, 9),
        )
        style.map(
            "Aetherion.TCombobox",
            fieldbackground=[("readonly", "#111111"), ("disabled", "#0B0B0B")],
            foreground=[("readonly", "#E8E8E8"), ("disabled", "#777777")],
            selectbackground=[("readonly", "#2B2B2B")],
        )
        style.configure("Aetherion.Vertical.TScrollbar", background="#252525", troughcolor="#0A0A0A", bordercolor="#0A0A0A", arrowcolor="#999999")
        style.configure("Aetherion.Horizontal.TProgressbar", troughcolor="#242424", background="#B8B8B8", bordercolor="#242424", lightcolor="#B8B8B8", darkcolor="#B8B8B8")

        self.root.configure(bg="#050505")
        self.container = tk.Frame(self.root, bg="#0B0B0B")
        self.container.pack(fill="both", expand=True, padx=26, pady=22)

        header = tk.Frame(self.container, bg="#0B0B0B")
        header.pack(fill="x", pady=(0, 20))
        self.brand_mark = tk.Canvas(header, width=58, height=58, bg="#0B0B0B", bd=0, highlightthickness=0)
        self.brand_mark.pack(side="left", padx=(0, 14))
        self.brand_mark.create_oval(5, 5, 53, 53, outline="#8A8A8A", width=1)
        self.brand_orbit = self.brand_mark.create_arc(9, 9, 49, 49, start=15, extent=118, outline="#E0E0E0", width=1, style="arc")
        self.brand_mark.create_oval(12, 12, 46, 46, outline="#343434", width=1)
        self.brand_mark.create_line(29, 12, 29, 46, fill="#4A4A4A", width=1)
        self.brand_mark.create_line(12, 29, 46, 29, fill="#4A4A4A", width=1)
        self.brand_mark.create_polygon(
            29, 14, 33, 25, 44, 29, 33, 33, 29, 44, 25, 33, 14, 29, 25, 25,
            fill="#AFAFAF",
            outline="#F2F2F2",
            width=1,
        )
        self.brand_mark.create_oval(26, 26, 32, 32, fill="#F2F2F2", outline="")

        brand_copy = tk.Frame(header, bg="#0B0B0B")
        brand_copy.pack(side="left", anchor="center")
        tk.Label(brand_copy, text="AETHERION", bg="#0B0B0B", fg="#EEEEEE", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(brand_copy, text="LOCAL MODEL BENCHMARK  /  PRIVATE BY DESIGN", bg="#0B0B0B", fg="#999999", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        self.status_var = tk.StringVar(value="CONNECTING TO LOCAL RUNTIMES")
        self.status = tk.Label(
            header,
            textvariable=self.status_var,
            bg="#171717",
            fg="#C8C8C8",
            font=("Segoe UI", 9, "bold"),
            padx=13,
            pady=8,
            highlightbackground="#3A3A3A",
            highlightthickness=1,
        )
        self.status.pack(anchor="center", side="right")

        content = tk.Frame(self.container, bg="#0B0B0B")
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, minsize=310)
        content.grid_rowconfigure(0, weight=1)
        self.left = tk.Frame(content, bg="#0B0B0B")
        self.left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.right = tk.Frame(content, bg="#141414", highlightbackground="#373737", highlightthickness=1, width=310)
        self.right.grid(row=0, column=1, sticky="nsew")
        self.right.grid_propagate(False)
        tk.Frame(self.right, bg="#B8B8B8", height=2).pack(fill="x")
        controls = tk.Frame(self.right, bg="#141414")
        controls.pack(fill="both", expand=True, padx=20, pady=20)

        hardware_panel = self.create_glass_panel(self.left)
        hardware_panel.pack(fill="x", pady=(0, 16))
        hardware_content = tk.Frame(hardware_panel, bg="#111111")
        hardware_content.pack(fill="x", padx=16, pady=15)
        tk.Label(hardware_content, text="LIVE SYSTEM PROFILE", bg="#111111", fg="#B8B8B8", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(hardware_content, text="Measured on this device", bg="#111111", fg="#777777", font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 7))
        self.hardware_text = tk.Text(hardware_content, height=4, bg="#111111", fg="#D8D8D8", bd=0, wrap="word", padx=0, pady=4, font=("Consolas", 9), selectbackground="#2B2B2B")
        self.hardware_text.pack(fill="x")
        self.hardware_text.insert("end", self.format_hardware(self.session.hardware))
        self.hardware_text.configure(state="disabled")

        output_panel = self.create_glass_panel(self.left)
        output_panel.pack(fill="both", expand=True)
        output_content = tk.Frame(output_panel, bg="#111111")
        output_content.pack(fill="both", expand=True, padx=16, pady=15)
        output_header = tk.Frame(output_content, bg="#111111")
        output_header.pack(fill="x", pady=(0, 10))
        tk.Label(output_header, text="BENCHMARK TRACE", bg="#111111", fg="#B8B8B8", font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(output_header, text="LOCAL RESULTS", bg="#111111", fg="#777777", font=("Segoe UI", 8, "bold")).pack(side="right")
        output_frame = tk.Frame(output_content, bg="#080808", highlightbackground="#303030", highlightthickness=1)
        output_frame.pack(fill="both", expand=True)
        self.output = tk.Text(output_frame, bg="#080808", fg="#D8D8D8", insertbackground="#F0F0F0", bd=0, wrap="word", padx=13, pady=12, font=("Consolas", 9), state="disabled", selectbackground="#2B2B2B")
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output.yview, style="Aetherion.Vertical.TScrollbar")
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.output.tag_configure("good", foreground="#9AE4BA")
        self.output.tag_configure("bad", foreground="#FF9D9D")
        self.output.tag_configure("muted", foreground="#91A1AF")
        self.append_output("Choose a local model and run a benchmark. Results stay on this device.\n", "muted")

        tk.Label(controls, text="RUN CONFIGURATION", bg="#141414", fg="#B8B8B8", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 20))
        tk.Label(controls, text="MODEL", bg="#141414", fg="#A0A0A0", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.model_var = tk.StringVar()
        self.model_menu = ttk.Combobox(controls, textvariable=self.model_var, state="disabled", style="Aetherion.TCombobox")
        self.model_menu.pack(fill="x", pady=(7, 18))
        self.model_menu.bind("<<ComboboxSelected>>", lambda _event: self.update_model_details())
        self.model_details = tk.Label(
            controls,
            text="No model selected",
            bg="#141414",
            fg="#777777",
            justify="left",
            anchor="w",
            wraplength=270,
            font=("Segoe UI", 8),
            padx=1,
        )
        self.model_details.pack(anchor="w", fill="x", pady=(0, 16))

        tk.Label(controls, text="GGUF MODEL FOLDER", bg="#141414", fg="#A0A0A0", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        model_path_frame = tk.Frame(controls, bg="#141414")
        model_path_frame.pack(fill="x", pady=(7, 18))
        self.model_path_var = tk.StringVar(value=str(self.session.gguf_provider.models_dir))
        self.model_path_entry = tk.Entry(
            model_path_frame,
            textvariable=self.model_path_var,
            bg="#111111",
            fg="#D8D8D8",
            insertbackground="#F0F0F0",
            relief="flat",
            highlightbackground="#3A3A3A",
            highlightthickness=1,
            font=("Segoe UI", 8),
        )
        self.model_path_entry.pack(side="left", fill="x", expand=True, ipady=7)
        tk.Button(
            model_path_frame,
            text="...",
            command=self.browse_model_folder,
            bg="#242424",
            fg="#D8D8D8",
            activebackground="#363636",
            activeforeground="#FFFFFF",
            relief="flat",
            highlightbackground="#3A3A3A",
            highlightthickness=1,
            width=3,
            cursor="hand2",
        ).pack(side="right", padx=(7, 0), ipady=5)

        self.requirements_label = tk.Label(
            controls,
            text="Checking requirements...",
            bg="#141414",
            fg="#8C8C8C",
            justify="left",
            anchor="w",
            wraplength=270,
            font=("Consolas", 8),
            padx=1,
        )
        self.requirements_label.pack(anchor="w", fill="x", pady=(0, 8))
        self.install_requirements_button = tk.Button(
            controls,
            text="DOWNLOAD MISSING INSTALLERS",
            command=self.download_missing_dependencies,
            bg="#242424",
            fg="#D8D8D8",
            activebackground="#363636",
            activeforeground="#FFFFFF",
            relief="flat",
            highlightbackground="#3A3A3A",
            highlightthickness=1,
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=8,
            cursor="hand2",
        )
        self.install_requirements_button.pack(fill="x", pady=(0, 18))

        tk.Label(controls, text="TASK SUITE", bg="#141414", fg="#A0A0A0", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.category_var = tk.StringVar(value="All tasks")
        categories = list(dict.fromkeys(task.category for task in TASKS))
        self.category_menu = ttk.Combobox(controls, textvariable=self.category_var, values=["All tasks", *categories], state="readonly", style="Aetherion.TCombobox")
        self.category_menu.pack(fill="x", pady=(7, 22))
        self.category_menu.bind("<<ComboboxSelected>>", lambda _event: self.update_suite_details())
        self.suite_details = tk.Label(
            controls,
            text=TASK_SUITE_DESCRIPTIONS["All tasks"],
            bg="#141414",
            fg="#777777",
            justify="left",
            anchor="w",
            wraplength=270,
            font=("Segoe UI", 8),
            padx=1,
        )
        self.suite_details.pack(anchor="w", fill="x", pady=(0, 14))

        self.refresh_button = tk.Button(controls, text="REFRESH MODEL LIST", command=self.refresh_models, bg="#202020", fg="#D8D8D8", activebackground="#303030", activeforeground="#FFFFFF", font=("Segoe UI", 9, "bold"), relief="flat", highlightbackground="#424242", highlightthickness=1, padx=12, pady=11, cursor="hand2")
        self.refresh_button.pack(fill="x")
        self.run_button = tk.Button(controls, text="RUN BENCHMARK", command=self.run_selected_benchmark, bg="#C8C8C8", fg="#0B0B0B", activebackground="#F0F0F0", activeforeground="#0B0B0B", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=13, cursor="hand2", state="disabled")
        self.run_button.pack(fill="x", pady=(10, 0))
        self.result_status = tk.Label(controls, text="Waiting for local runtimes", bg="#141414", fg="#999999", justify="left", anchor="w", wraplength=270, font=("Segoe UI", 9), padx=1, pady=8)
        self.result_status.pack(anchor="w", fill="x", pady=(14, 10))
        self.progress = ttk.Progressbar(controls, mode="determinate", maximum=100, value=0, style="Aetherion.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 5))
        self.progress_text = tk.Label(controls, text="Ready to benchmark", bg="#141414", fg="#777777", anchor="w", font=("Segoe UI", 8))
        self.progress_text.pack(anchor="w", fill="x", pady=(0, 12))
        self.run_metrics = tk.Label(
            controls,
            text="NO RUN YET\nComplete a benchmark to see its summary.",
            bg="#141414",
            fg="#8C8C8C",
            justify="left",
            anchor="w",
            wraplength=270,
            font=("Consolas", 8),
            padx=1,
            pady=8,
        )
        self.run_metrics.pack(anchor="w", fill="x", pady=(0, 10))
        tk.Frame(controls, bg="#2C3944", height=1).pack(fill="x", pady=(2, 13))
        self.open_results_button = tk.Button(controls, text="OPEN RESULTS FOLDER", command=self.open_results_folder, bg="#171717", fg="#C8C8C8", activebackground="#2A2A2A", activeforeground="#FFFFFF", font=("Segoe UI", 8, "bold"), relief="flat", highlightbackground="#3A3A3A", highlightthickness=1, padx=12, pady=10, cursor="hand2")
        self.open_results_button.pack(fill="x", side="bottom")

    @staticmethod
    def create_glass_panel(parent: tk.Widget) -> tk.Frame:
        panel = tk.Frame(parent, bg="#111111", highlightbackground="#363636", highlightthickness=1, bd=0)
        tk.Frame(panel, bg="#777777", height=1).pack(fill="x")
        return panel

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
        self.model_details.configure(
            text=f"{model.provider.upper()}  ·  {size}\n{quantization}{digest_text}\n{recommendation}\n{runability}",
            fg="#A8A8A8",
        )

    def update_suite_details(self) -> None:
        suite = self.category_var.get()
        self.suite_details.configure(text=TASK_SUITE_DESCRIPTIONS.get(suite, "Runs the selected local validation tasks."))

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
        self.requirements_label.configure(text=text, fg="#C8C8C8" if not missing else "#A8A8A8")
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
                self.requirements_label.configure(text="Downloading Ollama installer...", fg="#B8B8B8")

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
            self.requirements_label.configure(text="Installing llama-cpp-python...", fg="#B8B8B8")

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
                fg="#B8B8B8",
            )

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
        self.result_status.configure(text="Checking local model runtimes on this computer…", fg="#B8B8B8")
        self.progress.configure(value=0)
        self.progress_text.configure(text="Checking local model runtimes")

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
        assessment = self.assess_model(model)
        if assessment.startswith("DIRECT RUN: NO"):
            self.status_var.set("MODEL NOT READY")
            self.result_status.configure(text=assessment, fg="#FF9D9D")
            self.append_output(f"\nModel cannot run on this machine:\n{assessment}\n", "bad")
            return
        category = None if self.category_var.get() == "All tasks" else self.category_var.get()
        self.busy = True
        self.refresh_button.configure(state="disabled")
        self.run_button.configure(state="disabled")
        self.model_menu.configure(state="disabled")
        self.category_menu.configure(state="disabled")
        self.status_var.set("BENCHMARK RUNNING")
        self.result_status.configure(text=f"Running {category or 'all'} tasks on {model_name}…", fg="#B8B8B8")
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
                    runtime=model.provider,
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
                models.sort(key=self.model_recommendation_key)
                self.models = {model.name: model for model in models}
                names = list(self.models)
                self.recommended_model_name = names[0] if names else None
                self.model_menu.configure(values=names, state="readonly" if names else "disabled")
                if names:
                    self.model_var.set(names[0])
                    self.update_model_details()
                    runtimes = ", ".join(sorted({model.provider.upper() for model in models}))
                    self.status_var.set(f"{runtimes} READY · {len(names)} MODEL(S)")
                    self.result_status.configure(text="Model list refreshed. Select a task suite and run it.", fg="#91E2B2")
                    self.progress_text.configure(text=f"{len(names)} local model(s) ready")
                    self.run_button.configure(state="normal")
                elif error:
                    self.model_var.set("")
                    self.status_var.set("LOCAL RUNTIMES UNAVAILABLE")
                    self.result_status.configure(text="No local model runtime is responding. Check Ollama or the GGUF runtime. " + error, fg="#FF9D9D")
                    self.progress_text.configure(text="Connection unavailable")
                    self.append_output("No local model runtime responded.\n" + error + "\n", "bad")
                else:
                    self.model_var.set("")
                    self.status_var.set("NO LOCAL MODELS")
                    self.result_status.configure(text="No local models were found. Install an Ollama model or place a GGUF model in the local models folder.", fg="#B8B8B8")
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
                color = "#91E2B2" if status == "complete" else "#FF9D9D" if status == "failed" else "#B8B8B8"
                self.status_var.set(f"RUN {status.upper()}")
                self.result_status.configure(text=f"{summary['passed_checks']} passed · {summary['failed_checks']} failed · {summary['errors']} errors\nSaved locally: {record_path}", fg=color)
                self.progress.configure(value=100)
                self.progress_text.configure(text="Benchmark complete")
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
                    fg="#C8C8C8" if status == "complete" else "#A8A8A8",
                )
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
                self.progress_text.configure(text="Benchmark stopped with an error")
                self.run_metrics.configure(text="RUN FAILED\nReview the benchmark trace for details.", fg="#FF9D9D")
                self.append_output(f"\nBenchmark could not finish: {payload}\n", "bad")
                self.busy = False
                self.refresh_button.configure(state="normal")
                self.model_menu.configure(state="readonly" if self.models else "disabled")
                self.category_menu.configure(state="readonly")
                self.run_button.configure(state="normal" if self.models else "disabled")
            elif event == "dependencies":
                self.requirements_label.configure(text=str(payload), fg="#91E2B2")
                self.refresh_dependency_status()
            elif event == "dependencies_error":
                self.requirements_label.configure(text=f"Runtime installation failed\n{payload}", fg="#FF9D9D")
                self.install_requirements_button.configure(state="normal")
            elif event == "installer_downloaded":
                installer_path = Path(str(payload))
                self.requirements_label.configure(
                    text=f"Ollama installer downloaded\n{installer_path}",
                    fg="#91E2B2",
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
                        self.requirements_label.configure(text=f"Ollama installer launched\n{installer_path}", fg="#91E2B2")
                    except OSError as exc:
                        self.requirements_label.configure(text=f"Could not launch installer\n{exc}", fg="#FF9D9D")
            elif event == "installer_download_error":
                self.requirements_label.configure(text=f"Installer download failed\n{payload}", fg="#FF9D9D")
                self.install_requirements_button.configure(state="normal", text="RETRY DOWNLOAD")
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
        if self.closing:
            return
        if self.busy and not messagebox.askyesno(
            "Benchmark in progress",
            "A benchmark is still running. Close the client anyway?",
            parent=self.root,
        ):
            return
        self.closing = True
        self.root.destroy()


def launch_desktop_app() -> None:
    root = tk.Tk()
    AetherionDesktopClient(root)
    root.mainloop()


if __name__ == "__main__":
    launch_desktop_app()
