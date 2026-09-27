from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_BENCHMARK_CATALOG: list[dict[str, Any]] = [
    {
        "name": "qwen3:4b",
        "runtime": "Ollama",
        "precision": "FP16",
        "category": "general",
        "version": "1.0.0",
    },
    {
        "name": "qwen3:8b",
        "runtime": "Ollama",
        "precision": "FP16",
        "category": "general",
        "version": "1.0.0",
    },
    {
        "name": "llama3.1:8b",
        "runtime": "Ollama",
        "precision": "Q4_K_M",
        "category": "reasoning",
        "version": "1.0.0",
    },
]


@dataclass
class BenchmarkSpec:
    name: str
    runtime: str
    precision: str
    category: str
    version: str = "1.0.0"

    @classmethod
    def from_catalog(cls, item: dict[str, Any]) -> "BenchmarkSpec":
        return cls(
            name=item["name"],
            runtime=item.get("runtime", "UNKNOWN"),
            precision=item.get("precision", "UNKNOWN"),
            category=item.get("category", "general"),
            version=item.get("version", "1.0.0"),
        )


def get_benchmark_catalog() -> list[BenchmarkSpec]:
    return [BenchmarkSpec.from_catalog(entry) for entry in DEFAULT_BENCHMARK_CATALOG]
