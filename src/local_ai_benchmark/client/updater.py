from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class UpdateStatus:
    current_version: str
    latest_version: str | None = None
    available: bool = False
    notes: str | None = None


class UpdateChecker:
    def __init__(self, current_version: str = "0.1.0", state_path: str | Path = "results/client/update-state.json"):
        self.current_version = current_version
        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def check(self) -> UpdateStatus:
        saved = {}
        if self.state_path.exists():
            try:
                saved = json.loads(self.state_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                saved = {}

        latest_version = saved.get("latest_version")
        available = bool(latest_version and latest_version != self.current_version)
        return UpdateStatus(
            current_version=self.current_version,
            latest_version=latest_version,
            available=available,
            notes="NEW VERSION AVAILABLE" if available else None,
        )

    def save(self, latest_version: str) -> None:
        self.state_path.write_text(json.dumps({"latest_version": latest_version}, indent=2), encoding="utf-8")
