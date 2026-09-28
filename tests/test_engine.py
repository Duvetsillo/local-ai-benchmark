import json

from local_ai_benchmark.engine import BenchmarkEngine
from local_ai_benchmark.models import HardwareProfile
from local_ai_benchmark.providers import Generation


class FakeProvider:
    name = "ollama"

    def generate(self, model, prompt, temperature, context):
        return Generation(
            text="888",
            first_token_seconds=0.1,
            total_seconds=1.0,
            usage={"eval_count": 3, "eval_duration": 1_000_000_000},
        )


def test_engine_reports_progress_and_persists_real_results(tmp_path, monkeypatch):
    hardware = HardwareProfile("Windows 11", "AMD64", {}, {}, []).to_dict()
    monkeypatch.setattr("local_ai_benchmark.engine.profile_hardware", lambda: HardwareProfile("Windows 11", "AMD64", {}, {}, []))
    monkeypatch.setattr("local_ai_benchmark.engine._resource_snapshot", lambda: {"cpu_percent": 10.0, "ram_used_bytes": 1024})
    progress = []

    engine = BenchmarkEngine(FakeProvider(), tmp_path)
    results = engine.run("test-model", "math", progress_callback=lambda index, total, result: progress.append((index, total, result)))

    assert len(results) == 1
    assert results[0].passed is True
    assert results[0].metrics["tokens_per_second"] == 3.0
    assert progress == [(1, 1, results[0])]
    assert engine.last_result_path is not None
    assert json.loads(engine.last_result_path.read_text(encoding="utf-8"))["results"][0]["response"] == "888"