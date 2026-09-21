import datetime as dt
import json
import time
from pathlib import Path

from .hardware import profile_hardware
from .models import BenchmarkResult
from .providers import OllamaProvider, ProviderError
from .tasks import tasks_for, validate


def _token_rate(count: int | None, seconds: float | None) -> float | None:
    return round(count / seconds, 3) if count is not None and seconds else None


def _resource_snapshot() -> dict[str, float | int | None]:
    try:
        import psutil

        memory = psutil.virtual_memory()
        return {"cpu_percent": psutil.cpu_percent(interval=0.1),
                "ram_used_bytes": memory.used}
    except ImportError:
        return {"cpu_percent": None, "ram_used_bytes": None}


class BenchmarkEngine:
    def __init__(self, provider: OllamaProvider, results_dir: str | Path = "results"):
        self.provider = provider
        self.results_dir = Path(results_dir)

    def run(self, model: str, category: str | None = None, temperature: float = 0.0,
            context: int = 4096) -> list[BenchmarkResult]:
        hardware = profile_hardware().to_dict()
        results: list[BenchmarkResult] = []
        for task in tasks_for(category):
            started = time.perf_counter()
            resources_before = _resource_snapshot()
            try:
                generation = self.provider.generate(model, task.prompt, temperature, context)
                resources_after = _resource_snapshot()
                output_tokens = generation.usage.get("eval_count")
                measured_total = generation.total_seconds
                eval_duration = generation.usage.get("eval_duration")
                if eval_duration:
                    measured_total = eval_duration / 1_000_000_000
                metrics = {
                    "time_to_first_token_seconds": generation.first_token_seconds,
                    "total_generation_seconds": round(measured_total, 6),
                    "wall_time_seconds": round(time.perf_counter() - started, 6),
                    "output_tokens": output_tokens,
                    "prompt_tokens": generation.usage.get("prompt_eval_count"),
                    "tokens_per_second": _token_rate(output_tokens, measured_total),
                    "cpu_percent": resources_after["cpu_percent"],
                    "ram_used_bytes": resources_after["ram_used_bytes"],
                    "vram_used_bytes": (hardware["gpus"][0].get("vram_used_mb") * 1024**2
                                        if hardware["gpus"] else None),
                    "temperature_c": (hardware["gpus"][0].get("temperature_c")
                                      if hardware["gpus"] else None),
                    "telemetry_note": "Provider/runtime telemetry only; unavailable fields are null",
                }
                results.append(BenchmarkResult(model, self.provider.name, task.name, task.category,
                                               task.prompt, temperature, context, generation.text,
                                               validate(task, generation.text), None, hardware, metrics,
                                               generation.usage))
            except ProviderError as exc:
                results.append(BenchmarkResult(model, self.provider.name, task.name, task.category,
                                               task.prompt, temperature, context, "", None, str(exc),
                                               hardware, {"wall_time_seconds": round(time.perf_counter() - started, 6),
                                                          "cpu_percent": resources_before["cpu_percent"],
                                                          "ram_used_bytes": resources_before["ram_used_bytes"]}, {}))
        self._write(results, hardware)
        return results

    def _write(self, results: list[BenchmarkResult], hardware: dict) -> Path:
        folder = self.results_dir / dt.date.today().isoformat()
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"run-{dt.datetime.now().strftime('%H%M%S')}.json"
        path.write_text(json.dumps({"schema_version": 1, "created_at": dt.datetime.now(dt.UTC).isoformat(),
                                    "hardware": hardware, "results": [item.to_dict() for item in results]},
                                   indent=2, ensure_ascii=False), encoding="utf-8")
        return path
