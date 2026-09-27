from pathlib import Path

from local_ai_benchmark.client.core import ClientRunRecord, generate_run_id
from local_ai_benchmark.client.storage import LocalResultStore


def test_generate_run_id_has_aetherion_prefix():
    run_id = generate_run_id()
    assert run_id.startswith("AET-")
    assert len(run_id) >= 16


def test_local_result_store_persists_record(tmp_path):
    store = LocalResultStore(base_dir=tmp_path)
    record = ClientRunRecord(
        run_id="AET-TEST-0001",
        benchmark="qwen3:4b",
        model_version="qwen3:4b",
        runtime="Ollama",
        precision="fp16",
        hardware={"cpu": "test-cpu"},
        result={"tokens_per_second": 12.5},
        status="complete",
    )

    store.save(record)
    saved = store.list()
    assert len(saved) == 1
    assert saved[0]["run_id"] == "AET-TEST-0001"


def test_default_benchmark_catalog_has_models():
    from local_ai_benchmark.client.benchmark import DEFAULT_BENCHMARK_CATALOG

    assert DEFAULT_BENCHMARK_CATALOG
    assert any(item["name"] for item in DEFAULT_BENCHMARK_CATALOG)
