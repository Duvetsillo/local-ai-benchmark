"""Hardware-fit heuristics retained from the original desktop client."""

from __future__ import annotations

import importlib.util
from typing import Any

from ...models import ModelInfo
from .tokens import COLORS


class AssessmentMixin:
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
        runtime_ready = (
            model.provider == "ollama"
            or importlib.util.find_spec("llama_cpp") is not None
        )
        if not runtime_ready:
            return "DIRECT RUN: NO · Install llama-cpp-python for GGUF"

        if model.size_bytes is None:
            return "DIRECT RUN: UNKNOWN · Model size unavailable"

        model_gb = model.size_bytes / (1024**3)
        required_gb = max(model_gb * 1.25, 1.0)
        available_gb = self.session.hardware.get("memory", {}).get("available_gb")
        if not isinstance(available_gb, (int, float)):
            return "DIRECT RUN: UNKNOWN · Available memory telemetry missing"
        gpus = self.session.hardware.get("gpu", [])
        vram_gb = next(
            (
                gpu.get("free_vram_gb", gpu.get("vram_gb"))
                for gpu in gpus
                if isinstance(gpu.get("free_vram_gb", gpu.get("vram_gb")), (int, float))
            ),
            None,
        )
        vram_text = (
            f"{vram_gb:.1f} GB VRAM (available when reported; otherwise total capacity)"
            if isinstance(vram_gb, (int, float))
            else "VRAM unavailable"
        )

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
        if "memory telemetry" in assessment:
            return "CANNOT CONFIRM · memory telemetry unavailable"
        return "CANNOT CONFIRM · model size unavailable"

    @staticmethod
    def assess_download_hardware(
        size_bytes: int, hardware: dict[str, Any]
    ) -> tuple[str, str]:
        model_gb = size_bytes / (1024**3)
        required_ram_gb = max(model_gb * 1.25, 1.0)
        memory = hardware.get("memory", {})
        available_ram_gb = (
            memory.get("available_gb") if isinstance(memory, dict) else None
        )
        gpus = hardware.get("gpu", [])
        vram_gb = next(
            (
                gpu.get("vram_gb")
                for gpu in gpus
                if isinstance(gpu, dict)
                and isinstance(gpu.get("vram_gb"), (int, float))
            ),
            None,
        )
        ram_text = (
            f"RAM: ~{required_ram_gb:.1f} GB needed, {available_ram_gb:.1f} GB available."
            if isinstance(available_ram_gb, (int, float))
            else f"RAM: ~{required_ram_gb:.1f} GB estimated; available RAM could not be read."
        )
        vram_text = (
            f"GPU: {vram_gb:.1f} GB VRAM detected."
            if isinstance(vram_gb, (int, float))
            else "GPU: VRAM unavailable, so GPU fit cannot be confirmed."
        )

        if not isinstance(available_ram_gb, (int, float)):
            return (
                f"FIT UNKNOWN · Cannot confirm whether this PC can run the model.\n{ram_text}\n{vram_text}",
                COLORS["warning"],
            )
        if available_ram_gb < required_ram_gb:
            return (
                f"NOT RECOMMENDED · Available RAM is below the estimate.\n{ram_text}\n{vram_text}",
                COLORS["error"],
            )
        if isinstance(vram_gb, (int, float)) and model_gb <= vram_gb * 0.9:
            return (
                f"LIKELY COMPATIBLE · Estimated to fit GPU and RAM.\n{ram_text}\n{vram_text}",
                COLORS["success"],
            )
        if isinstance(vram_gb, (int, float)):
            return (
                f"LIKELY TO RUN · RAM appears sufficient; GPU VRAM is too small, so CPU fallback is expected.\n{ram_text}\n{vram_text}",
                COLORS["warning"],
            )
        return (
            f"LIKELY TO RUN ON CPU · RAM appears sufficient; GPU fit is unknown.\n{ram_text}\n{vram_text}",
            COLORS["warning"],
        )
