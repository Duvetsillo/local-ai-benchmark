from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from typing import Any

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


def _get_if_available(value: Any) -> Any:
    return value if value not in (None, "", "unknown", "UNKNOWN") else "UNKNOWN"


def _safe_run(command: list[str]) -> str:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, shell=False, timeout=5)
        if completed.returncode != 0:
            return ""
        return completed.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _gpu_details() -> list[dict[str, Any]]:
    gpus: list[dict[str, Any]] = []
    executable = shutil.which("nvidia-smi")
    if executable:
        query = "name,memory.total,driver_version"
        output = _safe_run([executable, f"--query-gpu={query}", "--format=csv,noheader,nounits"])
        for line in output.splitlines():
            values = [part.strip() for part in line.split(",")]
            if not values:
                continue
            if len(values) >= 3:
                gpus.append({
                    "vendor": "NVIDIA",
                    "name": values[0] or "UNKNOWN",
                    "vram_gb": round(float(values[1]) / 1024.0, 2) if values[1].replace(".", "", 1).isdigit() else "UNKNOWN",
                    "driver": values[2] or "UNKNOWN",
                })
    if not gpus:
        output = _safe_run(["system_profiler", "SPDisplaysDataType"])
        if output:
            gpus.append({
                "vendor": "APPLE",
                "name": "Metal GPU",
                "vram_gb": "UNKNOWN",
                "driver": "Metal",
            })
    return gpus or [{"vendor": "UNKNOWN", "name": "UNKNOWN", "vram_gb": "UNKNOWN", "driver": "UNKNOWN"}]


def detect_hardware() -> dict[str, Any]:
    os_name = platform.system() or "UNKNOWN"
    version = platform.release() or "UNKNOWN"
    cpu_model = platform.processor() or "UNKNOWN"
    architecture = platform.machine() or "UNKNOWN"

    process_count = None
    threads = None
    frequency_mhz = None
    if psutil is not None:
        try:
            process_count = psutil.cpu_count(logical=False)
            threads = psutil.cpu_count(logical=True)
            freq = psutil.cpu_freq()
            frequency_mhz = round(freq.current, 2) if freq else None
        except Exception:
            process_count = os.cpu_count() if hasattr(os, "cpu_count") else None
            threads = os.cpu_count()

    ram_total = None
    ram_available = None
    if psutil is not None:
        try:
            mem = psutil.virtual_memory()
            ram_total = round(mem.total / (1024**3), 2)
            ram_available = round(mem.available / (1024**3), 2)
        except Exception:
            ram_total = None
            ram_available = None

    ai_acceleration = {
        "cuda": shutil.which("nvidia-smi") is not None,
        "rocm": shutil.which("rocminfo") is not None,
        "directml": os.name == "nt" and shutil.which("dxdiag") is not None,
        "metal": os_name == "Darwin",
        "other": [],
    }

    return {
        "os": {"name": os_name, "version": version, "architecture": architecture},
        "cpu": {
            "manufacturer": "UNKNOWN",
            "model": cpu_model,
            "cores": process_count,
            "threads": threads,
            "frequency_mhz": frequency_mhz,
        },
        "memory": {
            "total_gb": ram_total,
            "available_gb": ram_available,
        },
        "gpu": _gpu_details(),
        "ai_acceleration": ai_acceleration,
        "storage": {
            "root": os.getcwd(),
            "free_space_gb": "UNKNOWN",
        },
        "status": "SYSTEM READY",
    }
