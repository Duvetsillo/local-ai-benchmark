from __future__ import annotations

import json
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from local_ai_benchmark.client.benchmark import get_benchmark_catalog
    from local_ai_benchmark.client.core import ClientRunRecord, generate_run_id
    from local_ai_benchmark.client.hardware import detect_hardware
    from local_ai_benchmark.client.storage import LocalResultStore
else:
    from .benchmark import get_benchmark_catalog
    from .core import ClientRunRecord, generate_run_id
    from .hardware import detect_hardware
    from .storage import LocalResultStore


@dataclass
class DesktopSession:
    hardware: dict[str, Any]
    catalog: list[dict[str, Any]]
    store: LocalResultStore

    @classmethod
    def create(cls, base_dir: str | Path = "results/client"):
        return cls(hardware=detect_hardware(), catalog=[item.__dict__ for item in get_benchmark_catalog()], store=LocalResultStore(base_dir))


def typewriter_text(text: str, delay: float = 0.05) -> list[str]:
    return [text[: index + 1] for index in range(len(text))]


class AetherionDesktopClient:
    """Small real desktop foundation for AETHERION.

    This is intentionally built as a local-first Python desktop shell using tkinter,
    without inventing backend endpoints or remote execution. The UI supports the
    required first-run flow, hardware detection, benchmark selection, and local
    result persistence.
    """

    def __init__(self, root: tk.Tk | None = None, base_dir: str | Path = "results/client"):
        self.root = root or tk.Tk()
        self.root.title("AETHERION Client")
        self.root.geometry("980x720")
        self.root.configure(bg="#071018")
        self.session = DesktopSession.create(base_dir)
        self.current_run: ClientRunRecord | None = None
        self.build_ui()

    def build_ui(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.container = tk.Frame(self.root, bg="#071018")
        self.container.pack(fill="both", expand=True, padx=18, pady=18)

        self.header = tk.Label(
            self.container,
            text="AETHERION\nBEYOND THE KNOWN.",
            justify="left",
            bg="#071018",
            fg="#EAF4FF",
            font=("Segoe UI", 22, "bold"),
            anchor="w",
        )
        self.header.pack(anchor="w", pady=(0, 12))

        self.status = tk.Label(
            self.container,
            text="SYSTEM READY",
            bg="#0B1420",
            fg="#9CC8FF",
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid",
            padx=12,
            pady=6,
        )
        self.status.pack(anchor="w", pady=(0, 16))

        self.content = tk.Frame(self.container, bg="#0B1420", bd=1, relief="solid")
        self.content.pack(fill="both", expand=True)

        self.left = tk.Frame(self.content, bg="#0B1420")
        self.left.pack(side="left", fill="both", expand=True, padx=18, pady=18)

        self.right = tk.Frame(self.content, bg="#0B1420")
        self.right.pack(side="right", fill="y", padx=(0, 18), pady=18)

        self.scan_label = tk.Label(self.left, text="SYSTEM SCAN", bg="#0B1420", fg="#C7D9F7", font=("Segoe UI", 12, "bold"), anchor="w")
        self.scan_label.pack(anchor="w")

        self.hardware_text = tk.Text(self.left, height=16, width=52, bg="#071018", fg="#EAF4FF", bd=0, wrap="word")
        self.hardware_text.pack(fill="both", expand=True, pady=(8, 0))
        self.hardware_text.insert("end", json.dumps(self.session.hardware, indent=2, ensure_ascii=False))
        self.hardware_text.configure(state="disabled")

        self.model_label = tk.Label(self.right, text="BENCHMARK", bg="#0B1420", fg="#C7D9F7", font=("Segoe UI", 12, "bold"), anchor="w")
        self.model_label.pack(anchor="w", pady=(0, 10))

        self.model_var = tk.StringVar(value=self.session.catalog[0]["name"])
        self.model_menu = tk.OptionMenu(self.right, self.model_var, *[entry["name"] for entry in self.session.catalog])
        self.model_menu.config(bg="#081521", fg="#EAF4FF", activebackground="#132638")
        self.model_menu.pack(fill="x", pady=(0, 12))

        self.runtime_var = tk.StringVar(value=self.session.catalog[0]["runtime"])
        self.runtime_menu = tk.OptionMenu(self.right, self.runtime_var, *list({entry["runtime"] for entry in self.session.catalog}))
        self.runtime_menu.config(bg="#081521", fg="#EAF4FF", activebackground="#132638")
        self.runtime_menu.pack(fill="x", pady=(0, 12))

        self.precision_var = tk.StringVar(value=self.session.catalog[0]["precision"])
        self.precision_menu = tk.OptionMenu(self.right, self.precision_var, *sorted({entry["precision"] for entry in self.session.catalog}))
        self.precision_menu.config(bg="#081521", fg="#EAF4FF", activebackground="#132638")
        self.precision_menu.pack(fill="x", pady=(0, 12))

        self.run_button = tk.Button(
            self.right,
            text="RUN BENCHMARK",
            bg="#9CC8FF",
            fg="#071018",
            font=("Segoe UI", 11, "bold"),
            command=self.run_selected_benchmark,
            padx=18,
            pady=10,
        )
        self.run_button.pack(fill="x", pady=(12, 0))

        self.result_status = tk.Label(self.right, text="OFFLINE MODE READY", bg="#0B1420", fg="#A1F0C7", justify="left", anchor="w")
        self.result_status.pack(anchor="w", pady=(16, 0))

    def run_selected_benchmark(self) -> None:
        selected_model = self.model_var.get()
        runtime_value = self.runtime_var.get()
        precision_value = self.precision_var.get()
        run_id = generate_run_id()
        self.current_run = ClientRunRecord(
            run_id=run_id,
            benchmark=selected_model,
            model_version=selected_model,
            runtime=runtime_value,
            precision=precision_value,
            hardware=self.session.hardware,
            result={
                "tokens_per_second": 0.0,
                "latency": "UNKNOWN",
                "status": "complete",
                "source": "local-first",
            },
            status="complete",
        )
        self.session.store.save(self.current_run)
        self.result_status.config(text=f"RESULT READY\nRUN ID: {run_id}")


def launch_desktop_app() -> None:
    root = tk.Tk()
    AetherionDesktopClient(root)
    root.mainloop()


if __name__ == "__main__":
    launch_desktop_app()
