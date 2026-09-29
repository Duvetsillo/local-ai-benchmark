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
    from local_ai_benchmark.client.storage import LocalResultStore
    from local_ai_benchmark.engine import BenchmarkEngine
    from local_ai_benchmark.models import BenchmarkResult, ModelInfo
    from local_ai_benchmark.providers import LlamaCppProvider, OllamaProvider, ProviderRouter
    from local_ai_benchmark.tasks import TASKS
    from local_ai_benchmark.client.theme import COLORS, FONTS, configure_ttk
else:
    from .core import ClientRunRecord, generate_run_id
    from .hardware import detect_hardware
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
        self.root.geometry("1180x820")
        self.root.minsize(960, 700)
        self.root.configure(bg="#080B10")
        self.session = DesktopSession.create(base_dir)
        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.models: dict[str, ModelInfo] = {}
        self.recommended_model_name: str | None = None
        self.download_window: tk.Toplevel | None = None
        self.download_progress: ttk.Progressbar | None = None
        self.download_status: tk.Label | None = None
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
        configure_ttk(style)

        self.root.configure(bg=COLORS["canvas"])
        self.container = tk.Frame(self.root, bg=COLORS["shell"])
        self.container.pack(fill="both", expand=True, padx=32, pady=26)

        self.shell = tk.Frame(self.container, bg=COLORS["shell"])
        self.shell.pack(fill="both", expand=True)
        self.create_sidebar(self.shell)
        self.workspace = tk.Frame(self.shell, bg=COLORS["shell"])
        self.workspace.pack(side="left", fill="both", expand=True, padx=(24, 0))

        header = tk.Frame(self.workspace, bg=COLORS["shell"])
        header.pack(fill="x", pady=(0, 26))
        self.brand_mark = tk.Canvas(header, width=58, height=58, bg=COLORS["shell"], bd=0, highlightthickness=0)
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

        brand_copy = tk.Frame(header, bg=COLORS["shell"])
        brand_copy.pack(side="left", anchor="center")
        tk.Label(brand_copy, text="AETHERION", bg=COLORS["shell"], fg=COLORS["text"], font=FONTS["display"]).pack(anchor="w")
        tk.Label(brand_copy, text="LOCAL MODEL BENCHMARK  /  PRIVATE BY DESIGN", bg=COLORS["shell"], fg=COLORS["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        self.section_var = tk.StringVar(value="DASHBOARD")
        tk.Label(header, textvariable=self.section_var, bg=COLORS["shell"], fg=COLORS["quiet"], font=("Segoe UI", 8, "bold"), padx=42).pack(side="left", anchor="center")
        self.status_var = tk.StringVar(value="CONNECTING TO LOCAL RUNTIMES")
        self.status = tk.Label(
            header,
            textvariable=self.status_var,
            bg=COLORS["surface_elevated"],
            fg=COLORS["text_soft"],
            font=("Segoe UI", 9, "bold"),
            padx=13,
            pady=8,
            highlightbackground=COLORS["line_strong"],
            highlightthickness=1,
        )
        self.status.pack(anchor="center", side="right")

        self.view_stack = tk.Frame(self.workspace, bg=COLORS["shell"])
        self.view_stack.pack(fill="both", expand=True)
        self.dashboard_view = tk.Frame(self.view_stack, bg=COLORS["shell"])
        self.dashboard_view.pack(fill="both", expand=True)
        content = tk.Frame(self.dashboard_view, bg="#0D1117")
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, minsize=360)
        content.grid_rowconfigure(0, weight=1)
        self.left = tk.Frame(content, bg="#0D1117")
        self.left.grid(row=0, column=0, sticky="nsew", padx=(0, 22))
        self.right = tk.Frame(content, bg="#171F29", highlightbackground="#35485B", highlightthickness=1, width=360)
        self.right.grid(row=0, column=1, sticky="nsew")
        self.right.grid_propagate(False)
        tk.Frame(self.right, bg="#67E8C5", height=2).pack(fill="x")
        controls = tk.Frame(self.right, bg="#171F29")
        controls.pack(fill="both", expand=True, padx=24, pady=24)

        overview_panel = tk.Frame(self.left, bg=COLORS["surface"], highlightbackground=COLORS["line"], highlightthickness=1)
        overview_panel.pack(fill="x", pady=(0, 16))
        overview_panel.grid_columnconfigure((0, 1, 2), weight=1)
        overview_values = [
            ("runtime_metric", "RUNTIME", "Scanning local providers"),
            ("models_metric", "MODELS", "Waiting for discovery"),
            ("last_run_metric", "LAST RUN", "No benchmark yet"),
        ]
        self.overview_vars: dict[str, tk.StringVar] = {}
        for column, (key, label, value) in enumerate(overview_values):
            cell = tk.Frame(overview_panel, bg=COLORS["surface"])
            cell.grid(row=0, column=column, sticky="nsew", padx=(16 if column == 0 else 8, 8 if column < 2 else 16), pady=14)
            tk.Label(cell, text=label, bg=COLORS["surface"], fg=COLORS["quiet"], font=("Segoe UI", 7, "bold")).pack(anchor="w")
            variable = tk.StringVar(value=value)
            self.overview_vars[key] = variable
            tk.Label(cell, textvariable=variable, bg=COLORS["surface"], fg=COLORS["text_soft"], font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w", pady=(6, 0))

        hardware_panel = self.create_glass_panel(self.left)
        hardware_panel.pack(fill="x", pady=(0, 16))
        hardware_content = tk.Frame(hardware_panel, bg="#131A22")
        hardware_content.pack(fill="x", padx=16, pady=15)
        tk.Label(hardware_content, text="LIVE SYSTEM PROFILE", bg="#131A22", fg="#67E8C5", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(hardware_content, text="Measured on this device", bg="#131A22", fg="#708196", font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 7))
        self.hardware_text = tk.Text(hardware_content, height=4, bg="#131A22", fg="#D9E4EE", bd=0, wrap="word", padx=0, pady=4, font=("Consolas", 9), selectbackground="#2B2B2B")
        self.hardware_text.pack(fill="x")
        self.hardware_text.insert("end", self.format_hardware(self.session.hardware))
        self.hardware_text.configure(state="disabled")

        output_panel = self.create_glass_panel(self.left)
        output_panel.pack(fill="both", expand=True)
        output_content = tk.Frame(output_panel, bg="#131A22")
        output_content.pack(fill="both", expand=True, padx=16, pady=15)
        output_header = tk.Frame(output_content, bg="#131A22")
        output_header.pack(fill="x", pady=(0, 10))
        tk.Label(output_header, text="BENCHMARK TRACE", bg="#131A22", fg="#67E8C5", font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(output_header, text="LOCAL RESULTS", bg="#131A22", fg="#708196", font=("Segoe UI", 8, "bold")).pack(side="right")
        output_frame = tk.Frame(output_content, bg="#080808", highlightbackground="#283747", highlightthickness=1)
        output_frame.pack(fill="both", expand=True)
        self.output = tk.Text(output_frame, bg="#080808", fg="#D9E4EE", insertbackground="#F0F0F0", bd=0, wrap="word", padx=13, pady=12, font=("Consolas", 9), state="disabled", selectbackground="#2B2B2B")
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output.yview, style="Aetherion.Vertical.TScrollbar")
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.output.tag_configure("good", foreground="#9AE4BA")
        self.output.tag_configure("bad", foreground="#FF9D9D")
        self.output.tag_configure("muted", foreground="#91A1AF")
        self.append_output("Choose a local model and run a benchmark. Results stay on this device.\n", "muted")

        tk.Label(controls, text="RUN CONFIGURATION", bg="#171F29", fg="#67E8C5", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 20))
        tk.Label(controls, text="MODEL", bg="#171F29", fg="#91A0B2", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.model_var = tk.StringVar()
        self.model_menu = ttk.Combobox(controls, textvariable=self.model_var, state="disabled", style="Aetherion.TCombobox")
        self.model_menu.pack(fill="x", pady=(7, 18))
        self.model_menu.bind("<<ComboboxSelected>>", lambda _event: self.update_model_details())
        self.model_details = tk.Label(
            controls,
            text="No model selected",
            bg="#171F29",
            fg="#708196",
            justify="left",
            anchor="w",
            wraplength=310,
            font=("Segoe UI", 8),
            padx=1,
        )
        self.model_details.pack(anchor="w", fill="x", pady=(0, 16))

        tk.Label(controls, text="GGUF MODEL FOLDER", bg="#171F29", fg="#91A0B2", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        model_path_frame = tk.Frame(controls, bg="#171F29")
        model_path_frame.pack(fill="x", pady=(7, 18))
        self.model_path_var = tk.StringVar(value=str(self.session.gguf_provider.models_dir))
        self.model_path_entry = tk.Entry(
            model_path_frame,
            textvariable=self.model_path_var,
            bg="#131A22",
            fg="#D9E4EE",
            insertbackground="#F0F0F0",
            relief="flat",
            highlightbackground="#35485B",
            highlightthickness=1,
            font=("Segoe UI", 8),
        )
        self.model_path_entry.pack(side="left", fill="x", expand=True, ipady=7)
        tk.Button(
            model_path_frame,
            text="...",
            command=self.browse_model_folder,
            bg="#253444",
            fg="#D9E4EE",
            activebackground="#35485B",
            activeforeground="#FFFFFF",
            relief="flat",
            highlightbackground="#35485B",
            highlightthickness=1,
            width=3,
            cursor="hand2",
        ).pack(side="right", padx=(7, 0), ipady=5)

        self.requirements_label = tk.Label(
            controls,
            text="Checking requirements...",
            bg="#171F29",
            fg="#91A0B2",
            justify="left",
            anchor="w",
            wraplength=310,
            font=("Consolas", 8),
            padx=1,
        )
        self.requirements_label.pack(anchor="w", fill="x", pady=(0, 8))
        self.install_requirements_button = tk.Button(
            controls,
            text="DOWNLOAD MISSING INSTALLERS",
            command=self.download_missing_dependencies,
            bg="#253444",
            fg="#D9E4EE",
            activebackground="#35485B",
            activeforeground="#FFFFFF",
            relief="flat",
            highlightbackground="#35485B",
            highlightthickness=1,
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=8,
            cursor="hand2",
        )
        self.install_requirements_button.pack(fill="x", pady=(0, 18))
        self.download_model_button = tk.Button(
            controls,
            text="DOWNLOAD A GGUF MODEL",
            command=self.open_model_downloader,
            bg="#1C2733",
            fg="#67E8C5",
            activebackground="#2A2A2A",
            activeforeground="#FFFFFF",
            relief="flat",
            highlightbackground="#35485B",
            highlightthickness=1,
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=8,
            cursor="hand2",
        )
        self.download_model_button.pack(fill="x", pady=(0, 18))

        tk.Label(controls, text="TASK SUITE", bg="#171F29", fg="#91A0B2", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.category_var = tk.StringVar(value="All tasks")
        categories = list(dict.fromkeys(task.category for task in TASKS))
        self.category_menu = ttk.Combobox(controls, textvariable=self.category_var, values=["All tasks", *categories], state="readonly", style="Aetherion.TCombobox")
        self.category_menu.pack(fill="x", pady=(7, 22))
        self.category_menu.bind("<<ComboboxSelected>>", lambda _event: self.update_suite_details())
        self.suite_details = tk.Label(
            controls,
            text=TASK_SUITE_DESCRIPTIONS["All tasks"],
            bg="#171F29",
            fg="#708196",
            justify="left",
            anchor="w",
            wraplength=270,
            font=("Segoe UI", 8),
            padx=1,
        )
        self.suite_details.pack(anchor="w", fill="x", pady=(0, 14))

        self.refresh_button = tk.Button(controls, text="REFRESH MODEL LIST", command=self.refresh_models, bg="#1C2733", fg="#D9E4EE", activebackground="#283747", activeforeground="#FFFFFF", font=("Segoe UI", 9, "bold"), relief="flat", highlightbackground="#35485B", highlightthickness=1, padx=12, pady=11, cursor="hand2")
        self.refresh_button.pack(fill="x")
        self.run_button = tk.Button(controls, text="RUN BENCHMARK", command=self.run_selected_benchmark, bg="#67E8C5", fg="#0D1117", activebackground="#F0F0F0", activeforeground="#0D1117", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=13, cursor="hand2", state="disabled")
        self.run_button.pack(fill="x", pady=(10, 0))
        self.result_status = tk.Label(controls, text="Waiting for local runtimes", bg="#171F29", fg="#999999", justify="left", anchor="w", wraplength=310, font=("Segoe UI", 9), padx=1, pady=8)
        self.result_status.pack(anchor="w", fill="x", pady=(14, 10))
        self.progress = ttk.Progressbar(controls, mode="determinate", maximum=100, value=0, style="Aetherion.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 5))
        self.progress_text = tk.Label(controls, text="Ready to benchmark", bg="#171F29", fg="#708196", anchor="w", font=("Segoe UI", 8))
        self.progress_text.pack(anchor="w", fill="x", pady=(0, 12))
        self.run_metrics = tk.Label(
            controls,
            text="NO RUN YET\nComplete a benchmark to see its summary.",
            bg="#171F29",
            fg="#91A0B2",
            justify="left",
            anchor="w",
            wraplength=310,
            font=("Consolas", 8),
            padx=1,
            pady=8,
        )
        self.run_metrics.pack(anchor="w", fill="x", pady=(0, 10))
        tk.Frame(controls, bg="#35485B", height=1).pack(fill="x", pady=(2, 13))
        self.open_results_button = tk.Button(controls, text="OPEN RESULTS FOLDER", command=self.open_results_folder, bg="#1C2733", fg="#67E8C5", activebackground="#2A2A2A", activeforeground="#FFFFFF", font=("Segoe UI", 8, "bold"), relief="flat", highlightbackground="#35485B", highlightthickness=1, padx=12, pady=10, cursor="hand2")
        self.open_results_button.pack(fill="x", side="bottom")
        self.views: dict[str, tk.Frame] = {"dashboard": self.dashboard_view}
        self.create_secondary_views()

    def view_header(self, parent: tk.Widget, eyebrow: str, title: str, description: str) -> None:
        header = tk.Frame(parent, bg=COLORS["shell"])
        header.pack(fill="x", pady=(6, 28))
        tk.Label(header, text=eyebrow, bg=COLORS["shell"], fg=COLORS["quiet"], font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(header, text=title, bg=COLORS["shell"], fg=COLORS["text"], font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(7, 5))
        tk.Label(header, text=description, bg=COLORS["shell"], fg=COLORS["muted"], font=("Segoe UI", 9), wraplength=720, justify="left").pack(anchor="w")

    def create_secondary_views(self) -> None:
        models_view = tk.Frame(self.view_stack, bg=COLORS["shell"])
        self.views["models"] = models_view
        self.view_header(models_view, "MODEL CATALOG", "Choose the right local model.", "Review discovered runtimes, model size, format, and hardware fit before starting a benchmark.")
        models_panel = tk.Frame(models_view, bg=COLORS["surface"], highlightbackground=COLORS["line"], highlightthickness=1)
        models_panel.pack(fill="both", expand=True)
        self.model_view_listbox = tk.Listbox(models_panel, bg=COLORS["surface"], fg=COLORS["text_soft"], selectbackground=COLORS["surface_interactive"], selectforeground=COLORS["text"], highlightthickness=0, bd=0, activestyle="none", font=("Segoe UI", 10))
        self.model_view_listbox.pack(fill="both", expand=True, padx=18, pady=18)

        benchmarks_view = tk.Frame(self.view_stack, bg=COLORS["shell"])
        self.views["benchmarks"] = benchmarks_view
        self.view_header(benchmarks_view, "BENCHMARK LAB", "Measure before you decide.", "Select a model and task suite in the Dashboard, then run the controlled local validation from here.")
        benchmark_panel = tk.Frame(benchmarks_view, bg=COLORS["surface"], highlightbackground=COLORS["line"], highlightthickness=1)
        benchmark_panel.pack(fill="x", pady=(0, 18))
        tk.Label(benchmark_panel, text="CURRENT CONFIGURATION", bg=COLORS["surface"], fg=COLORS["quiet"], font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(18, 8))
        self.benchmark_view_config = tk.Label(benchmark_panel, text="No model selected", bg=COLORS["surface"], fg=COLORS["text_soft"], font=("Segoe UI", 12, "bold"), anchor="w")
        self.benchmark_view_config.pack(anchor="w", padx=20, pady=(0, 18))
        tk.Button(benchmark_panel, text="OPEN DASHBOARD CONTROLS", command=lambda: self.focus_section("dashboard"), bg=COLORS["surface_interactive"], fg=COLORS["text_soft"], activebackground="#35485B", activeforeground=COLORS["text"], relief="flat", font=("Segoe UI", 8, "bold"), padx=12, pady=9, cursor="hand2").pack(anchor="w", padx=20, pady=(0, 18))

        results_view = tk.Frame(self.view_stack, bg=COLORS["shell"])
        self.views["results"] = results_view
        self.view_header(results_view, "RESULTS", "Evidence from your machine.", "Every completed run is stored locally and remains available for review.")
        results_panel = tk.Frame(results_view, bg=COLORS["surface"], highlightbackground=COLORS["line"], highlightthickness=1)
        results_panel.pack(fill="both", expand=True)
        self.results_view_text = tk.Text(results_panel, bg=COLORS["surface"], fg=COLORS["text_soft"], bd=0, wrap="word", padx=20, pady=18, font=("Consolas", 9), state="disabled")
        self.results_view_text.pack(fill="both", expand=True)

        hardware_view = tk.Frame(self.view_stack, bg=COLORS["shell"])
        self.views["hardware"] = hardware_view
        self.view_header(hardware_view, "SYSTEM PROFILE", "Know the machine first.", "The runtime uses this profile to explain model fit, memory pressure, and acceleration options.")
        hardware_panel = tk.Frame(hardware_view, bg=COLORS["surface"], highlightbackground=COLORS["line"], highlightthickness=1)
        hardware_panel.pack(fill="x")
        self.hardware_view_text = tk.Text(hardware_panel, height=10, bg=COLORS["surface"], fg=COLORS["text_soft"], bd=0, wrap="word", padx=20, pady=20, font=("Consolas", 10), state="disabled")
        self.hardware_view_text.pack(fill="x")
        self.hardware_view_text.configure(state="normal")
        self.hardware_view_text.insert("end", self.format_hardware(self.session.hardware))
        self.hardware_view_text.configure(state="disabled")

        history_view = tk.Frame(self.view_stack, bg=COLORS["shell"])
        self.views["history"] = history_view
        self.view_header(history_view, "HISTORY", "Your local benchmark trail.", "A quiet record of the decisions and runs already made on this device.")
        history_panel = tk.Frame(history_view, bg=COLORS["surface"], highlightbackground=COLORS["line"], highlightthickness=1)
        history_panel.pack(fill="both", expand=True)
        self.history_view_listbox = tk.Listbox(history_panel, bg=COLORS["surface"], fg=COLORS["text_soft"], selectbackground=COLORS["surface_interactive"], selectforeground=COLORS["text"], highlightthickness=0, bd=0, activestyle="none", font=("Consolas", 9))
        self.history_view_listbox.pack(fill="both", expand=True, padx=18, pady=18)

        settings_view = tk.Frame(self.view_stack, bg=COLORS["shell"])
        self.views["settings"] = settings_view
        self.view_header(settings_view, "SETTINGS", "Keep the workspace local.", "Configure where GGUF models live and inspect the runtimes available to AETHERION.")
        settings_panel = tk.Frame(settings_view, bg=COLORS["surface"], highlightbackground=COLORS["line"], highlightthickness=1)
        settings_panel.pack(fill="x")
        tk.Label(settings_panel, text="MODEL STORAGE", bg=COLORS["surface"], fg=COLORS["quiet"], font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(20, 8))
        tk.Label(settings_panel, textvariable=self.model_path_var, bg=COLORS["surface"], fg=COLORS["text_soft"], font=("Consolas", 9), anchor="w", wraplength=720, justify="left").pack(anchor="w", padx=20, pady=(0, 16))
        tk.Button(settings_panel, text="CHANGE MODEL FOLDER", command=self.browse_model_folder, bg=COLORS["surface_interactive"], fg=COLORS["text_soft"], activebackground="#35485B", activeforeground=COLORS["text"], relief="flat", font=("Segoe UI", 8, "bold"), padx=12, pady=9, cursor="hand2").pack(anchor="w", padx=20, pady=(0, 20))

        self.refresh_model_view()
        self.refresh_results_view()
        self.refresh_history_view()

    def refresh_model_view(self) -> None:
        if not hasattr(self, "model_view_listbox"):
            return
        self.model_view_listbox.delete(0, "end")
        for model in self.models.values():
            self.model_view_listbox.insert("end", f"{model.name}   /   {model.provider.upper()}   /   {self.assess_model(model).replace(chr(10), ' · ')}")

    def refresh_results_view(self) -> None:
        if not hasattr(self, "results_view_text"):
            return
        rows = self.session.store.list()
        text = "\n".join(f"{row.get('created_at', 'UNKNOWN')}  |  {row.get('benchmark', 'UNKNOWN')}  |  {row.get('status', 'UNKNOWN')}" for row in rows[-20:]) or "No benchmark results saved yet."
        self.results_view_text.configure(state="normal")
        self.results_view_text.delete("1.0", "end")
        self.results_view_text.insert("end", text)
        self.results_view_text.configure(state="disabled")

    def refresh_history_view(self) -> None:
        if not hasattr(self, "history_view_listbox"):
            return
        self.history_view_listbox.delete(0, "end")
        rows = self.session.store.list()
        for row in reversed(rows[-20:]):
            self.history_view_listbox.insert("end", f"{row.get('created_at', 'UNKNOWN')}  ·  {row.get('benchmark', 'UNKNOWN')}  ·  {row.get('status', 'UNKNOWN')}")

    def create_sidebar(self, parent: tk.Widget) -> None:
        sidebar = tk.Frame(parent, bg=COLORS["surface"], width=208, highlightbackground=COLORS["line"], highlightthickness=1)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_row = tk.Frame(sidebar, bg=COLORS["surface"])
        logo_row.pack(fill="x", padx=18, pady=(20, 30))
        tk.Label(logo_row, text="A", bg=COLORS["surface"], fg=COLORS["text"], font=("Segoe UI", 20, "bold"), width=2).pack(side="left")
        logo_copy = tk.Frame(logo_row, bg=COLORS["surface"])
        logo_copy.pack(side="left", padx=(6, 0))
        tk.Label(logo_copy, text="AETHERION", bg=COLORS["surface"], fg=COLORS["text"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(logo_copy, text="BEYOND THE KNOWN", bg=COLORS["surface"], fg=COLORS["quiet"], font=("Segoe UI", 6, "bold")).pack(anchor="w", pady=(2, 0))

        self.nav_buttons: dict[str, tk.Button] = {}
        navigation = [
            ("DASHBOARD", "dashboard"),
            ("BENCHMARKS", "benchmarks"),
            ("MODELS", "models"),
            ("RESULTS", "results"),
            ("HARDWARE", "hardware"),
            ("HISTORY", "history"),
            ("SETTINGS", "settings"),
        ]
        tk.Label(sidebar, text="WORKSPACE", bg=COLORS["surface"], fg=COLORS["quiet"], font=("Segoe UI", 7, "bold"), padx=18).pack(anchor="w", pady=(0, 8))
        for label, view in navigation:
            button = tk.Button(
                sidebar,
                text=f"  {label}",
                command=lambda view_name=view: self.focus_section(view_name),
                bg=COLORS["surface"],
                fg=COLORS["muted"],
                activebackground=COLORS["surface_interactive"],
                activeforeground=COLORS["text"],
                relief="flat",
                anchor="w",
                font=("Segoe UI", 8, "bold"),
                padx=14,
                pady=9,
                cursor="hand2",
            )
            button.pack(fill="x", padx=10, pady=1)
            self.nav_buttons[view] = button
        self.nav_buttons["dashboard"].configure(bg=COLORS["surface_interactive"], fg=COLORS["text"])

        sidebar_footer = tk.Frame(sidebar, bg=COLORS["surface"])
        sidebar_footer.pack(side="bottom", fill="x", padx=18, pady=18)
        tk.Frame(sidebar_footer, bg=COLORS["line"], height=1).pack(fill="x", pady=(0, 12))
        tk.Label(sidebar_footer, text="AETHERION CLIENT", bg=COLORS["surface"], fg=COLORS["quiet"], font=("Segoe UI", 7, "bold")).pack(anchor="w")
        tk.Label(sidebar_footer, text="v0.1.0  /  LOCAL-FIRST", bg=COLORS["surface"], fg=COLORS["muted"], font=("Consolas", 7)).pack(anchor="w", pady=(4, 0))

    def focus_section(self, view: str) -> None:
        labels = {
            "dashboard": "DASHBOARD",
            "benchmarks": "BENCHMARKS",
            "models": "MODELS",
            "results": "RESULTS",
            "hardware": "HARDWARE",
            "history": "HISTORY",
            "settings": "SETTINGS",
        }
        self.section_var.set(labels.get(view, "DASHBOARD"))
        for name, button in self.nav_buttons.items():
            active = name == view
            button.configure(
                bg=COLORS["surface_interactive"] if active else COLORS["surface"],
                fg=COLORS["text"] if active else COLORS["muted"],
            )
        for name, frame in self.views.items():
            frame.pack_forget()
        self.views.get(view, self.dashboard_view).pack(fill="both", expand=True)
        targets = {
            "dashboard": self.status,
            "benchmarks": self.run_button,
            "models": self.model_menu,
            "results": self.output,
            "hardware": self.hardware_text,
            "history": self.run_metrics,
            "settings": self.model_path_entry,
        }
        target = targets.get(view)
        if target is not None and view == "dashboard":
            target.focus_set()

    @staticmethod
    def create_glass_panel(parent: tk.Widget) -> tk.Frame:
        panel = tk.Frame(parent, bg="#131A22", highlightbackground="#35485B", highlightthickness=1, bd=0)
        tk.Frame(panel, bg="#708196", height=1).pack(fill="x")
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
        self.requirements_label.configure(text=text, fg="#67E8C5" if not missing else "#A8A8A8")
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
                self.requirements_label.configure(text="Downloading Ollama installer...", fg="#67E8C5")

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
            self.requirements_label.configure(text="Installing llama-cpp-python...", fg="#67E8C5")

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
                fg="#67E8C5",
            )

    def open_model_downloader(self) -> None:
        if self.download_window is not None and self.download_window.winfo_exists():
            self.download_window.focus_force()
            return
        window = tk.Toplevel(self.root)
        self.download_window = window
        window.title("Download local model")
        window.geometry("560x330")
        window.minsize(500, 300)
        window.configure(bg="#131A22")
        window.transient(self.root)

        content = tk.Frame(window, bg="#131A22")
        content.pack(fill="both", expand=True, padx=24, pady=22)
        tk.Label(content, text="MODEL DOWNLOAD", bg="#131A22", fg="#67E8C5", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(content, text="Download a GGUF model directly to your selected model folder.", bg="#131A22", fg="#91A0B2", font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 18))

        tk.Label(content, text="CATALOG", bg="#131A22", fg="#91A0B2", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        catalog_var = tk.StringVar(value=next(iter(MODEL_DOWNLOAD_CATALOG)))
        catalog_menu = ttk.Combobox(content, textvariable=catalog_var, values=list(MODEL_DOWNLOAD_CATALOG), state="readonly", style="Aetherion.TCombobox")
        catalog_menu.pack(fill="x", pady=(7, 14))

        tk.Label(content, text="DOWNLOAD URL", bg="#131A22", fg="#91A0B2", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        url_var = tk.StringVar(value=MODEL_DOWNLOAD_CATALOG[catalog_var.get()])
        url_entry = tk.Entry(content, textvariable=url_var, bg="#0D1117", fg="#D9E4EE", insertbackground="#F0F0F0", relief="flat", highlightbackground="#35485B", highlightthickness=1, font=("Segoe UI", 8))
        url_entry.pack(fill="x", pady=(7, 14), ipady=7)
        catalog_menu.bind("<<ComboboxSelected>>", lambda _event: url_var.set(MODEL_DOWNLOAD_CATALOG[catalog_var.get()]))

        destination = str(self.session.gguf_provider.models_dir)
        tk.Label(content, text=f"DESTINATION  {destination}", bg="#131A22", fg="#708196", font=("Segoe UI", 8)).pack(anchor="w")
        self.download_progress = ttk.Progressbar(content, mode="determinate", maximum=100, value=0, style="Aetherion.Horizontal.TProgressbar")
        self.download_progress.pack(fill="x", pady=(16, 5))
        self.download_status = tk.Label(content, text="Ready to download", bg="#131A22", fg="#91A0B2", anchor="w", font=("Segoe UI", 8))
        self.download_status.pack(fill="x")
        download_button = tk.Button(content, text="DOWNLOAD MODEL", command=lambda: self.download_model(url_var.get(), download_button), bg="#67E8C5", fg="#0D1117", activebackground="#F0F0F0", activeforeground="#0D1117", relief="flat", font=("Segoe UI", 9, "bold"), padx=12, pady=10, cursor="hand2")
        download_button.pack(anchor="e", pady=(14, 0))

    def download_model(self, url: str, button: tk.Button) -> None:
        parsed = urlparse(url.strip())
        filename = Path(unquote(parsed.path)).name
        if parsed.scheme != "https" or not filename.lower().endswith(".gguf"):
            self.download_status.configure(text="Use a valid HTTPS URL ending in .gguf", fg="#FF9D9D")
            return
        target_dir = self.session.gguf_provider.models_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename
        button.configure(state="disabled")
        self.download_progress.configure(value=0)
        self.download_status.configure(text=f"Downloading {filename}...", fg="#67E8C5")

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
        self.refresh_button.configure(state="disabled")
        self.run_button.configure(state="disabled")
        self.model_menu.configure(state="disabled")
        self.status_var.set("LOOKING FOR LOCAL MODELS")
        self.update_overview("runtime_metric", "Scanning providers")
        self.update_overview("models_metric", "Discovering models")
        self.result_status.configure(text="Checking local model runtimes on this computer…", fg="#67E8C5")
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
        self.result_status.configure(text=f"Running {category or 'all'} tasks on {model_name}…", fg="#67E8C5")
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
                    self.update_overview("runtime_metric", "No providers")
                    self.update_overview("models_metric", "0 available")
                    self.result_status.configure(text="No local models were found. Install an Ollama model or place a GGUF model in the local models folder.", fg="#67E8C5")
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
                color = "#91E2B2" if status == "complete" else "#FF9D9D" if status == "failed" else "#67E8C5"
                self.status_var.set(f"RUN {status.upper()}")
                self.update_overview("last_run_metric", f"{status.upper()} · {summary['passed_checks']}/{summary['task_count']}")
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
                    fg="#67E8C5" if status == "complete" else "#A8A8A8",
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
                    self.download_status.configure(text=f"Downloaded: {payload}", fg="#91E2B2")
                self.append_output(f"\nModel downloaded: {payload}\n", "good")
                self.refresh_models()
            elif event == "model_download_error":
                if self.download_status is not None:
                    self.download_status.configure(text=f"Download failed: {payload}", fg="#FF9D9D")
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
