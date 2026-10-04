import json
import os
import platform
import shutil
import subprocess
from typing import Any

from .models import HardwareProfile


def _bytes_to_gb(value: int | float | None) -> float | None:
    return round(value / (1024**3), 2) if value is not None else None


def _memory() -> dict[str, Any]:
    try:
        import psutil

        memory = psutil.virtual_memory()
        return {"total_bytes": memory.total, "available_bytes": memory.available,
                "used_bytes": memory.used, "total_gb": _bytes_to_gb(memory.total),
                "available_gb": _bytes_to_gb(memory.available),
                "used_gb": _bytes_to_gb(memory.used)}
    except ImportError:
        return {"total_bytes": None, "available_bytes": None, "used_bytes": None,
                "total_gb": None, "available_gb": None, "used_gb": None}


def _nvidia_gpus() -> list[dict[str, Any]]:
    executable = shutil.which("nvidia-smi")
    if not executable:
        return []
    query = "name,memory.total,memory.used,utilization.gpu,temperature.gpu,power.draw"
    try:
        completed = subprocess.run(
            [executable, f"--query-gpu={query}", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=3, check=True,
            creationflags=0x08000000 if os.name == "nt" else 0,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    gpus = []
    fields = ["name", "vram_total_mb", "vram_used_mb", "utilization_percent",
              "temperature_c", "power_w"]
    for line in completed.stdout.splitlines():
        values = [value.strip() for value in line.split(",")]
        if len(values) != len(fields):
            continue
        gpu: dict[str, Any] = {"vendor": "NVIDIA"}
        for field, value in zip(fields, values):
            try:
                gpu[field] = float(value) if field != "name" else value
            except ValueError:
                gpu[field] = None
        gpus.append(gpu)
    return gpus


def profile_hardware() -> HardwareProfile:
    cpu_count = None
    logical_count = None
    frequency = None
    try:
        import psutil

        cpu_count = psutil.cpu_count(logical=False)
        logical_count = psutil.cpu_count(logical=True)
        frequency = psutil.cpu_freq().current if psutil.cpu_freq() else None
    except ImportError:
        logical_count = __import__("os").cpu_count()
    return HardwareProfile(
        os=f"{platform.system()} {platform.release()}",
        architecture=platform.machine(),
        cpu={"manufacturer": platform.processor(), "model": platform.processor(),
             "cores": cpu_count, "threads": logical_count, "frequency_mhz": frequency},
        ram=_memory(),
        gpus=_nvidia_gpus(),
    )


def print_profile(profile: HardwareProfile) -> str:
    return json.dumps(profile.to_dict(), indent=2, ensure_ascii=False)
