from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .benchmark import get_benchmark_catalog
from .core import ClientRunRecord, generate_run_id
from .hardware import detect_hardware
from .storage import LocalResultStore


def typewriter_sequence(text: str, delay: float = 0.05) -> list[str]:
    return [text[: i + 1] for i in range(len(text))]


def run_client_flow() -> dict[str, Any]:
    hardware = detect_hardware()
    catalog = [item.__dict__ for item in get_benchmark_catalog()]
    run_id = generate_run_id()
    record = ClientRunRecord(
        run_id=run_id,
        benchmark=catalog[0]["name"],
        model_version=catalog[0]["version"],
        runtime=catalog[0]["runtime"],
        precision=catalog[0]["precision"],
        hardware=hardware,
        result={
            "status": "complete",
            "tokens_per_second": 0.0,
            "latency": "UNKNOWN",
        },
        status="complete",
    )
    store = LocalResultStore(base_dir=Path("results/client"))
    store.save(record)
    return {
        "run_id": run_id,
        "hardware": hardware,
        "benchmark_catalog": catalog,
        "record": record.to_dict(),
        "typewriter_preview": typewriter_sequence("AETHERION"),
    }


def main() -> None:
    print(json.dumps(run_client_flow(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
