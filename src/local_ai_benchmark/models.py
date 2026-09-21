from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class HardwareProfile:
    os: str
    architecture: str
    cpu: dict[str, Any]
    ram: dict[str, Any]
    gpus: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ModelInfo:
    name: str
    provider: str
    size_bytes: int | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Task:
    name: str
    category: str
    prompt: str
    validator: str


@dataclass
class BenchmarkResult:
    model: str
    provider: str
    task: str
    category: str
    prompt: str
    temperature: float
    context: int
    response: str
    passed: bool | None
    error: str | None
    hardware: dict[str, Any]
    metrics: dict[str, Any]
    raw_usage: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
