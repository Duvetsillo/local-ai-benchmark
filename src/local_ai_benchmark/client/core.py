from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


def generate_run_id() -> str:
    timestamp = dt.datetime.now().strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:8].upper()
    return f"AET-{timestamp}-{suffix}"


@dataclass
class ClientRunRecord:
    run_id: str
    benchmark: str
    model_version: str
    runtime: str
    precision: str
    hardware: dict[str, Any]
    result: dict[str, Any]
    status: str = "pending"
    client_version: str = "0.1.0"
    benchmark_version: str = "0.1.0"
    created_at: str = field(default_factory=lambda: dt.datetime.now(dt.UTC).isoformat())
    notes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
