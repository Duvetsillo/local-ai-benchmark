from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .core import ClientRunRecord


class LocalResultStore:
    def __init__(self, base_dir: str | Path = "results/client"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, record: ClientRunRecord) -> Path:
        target_dir = self.base_dir / record.run_id[:8]
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / f"{record.run_id}.json"
        payload = json.dumps(record.to_dict(), indent=2, ensure_ascii=False)
        temporary_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=target_dir,
                prefix=f".{record.run_id}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = temporary_file.name
                temporary_file.write(payload)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, file_path)
        finally:
            if temporary_path:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass
        return file_path

    def list(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for path in sorted(self.base_dir.glob("**/*.json")):
            try:
                rows.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
        return rows

    def pending_upload(self) -> list[dict[str, Any]]:
        return [item for item in self.list() if item.get("status") in {"pending", "failed"}]
