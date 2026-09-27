from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BackendConfig:
    base_url: str | None = None
    api_key: str | None = None
    timeout_seconds: int = 15
    enabled: bool = False


class AetherionAPIClient:
    """Thin, explicit contract to the AETHERION backend.

    This project currently has no backend endpoint implementation in the repository,
    so the client intentionally avoids fake network calls. The API layer remains a
    dedicated integration boundary for when the backend is available.
    """

    def __init__(self, config: BackendConfig | None = None):
        self.config = config or BackendConfig()

    def submit_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.config.enabled or not self.config.base_url:
            raise RuntimeError(
                "AETHERION backend is not configured. Results remain local until the server endpoint is available."
            )
        raise NotImplementedError("Backend endpoint integration is pending the official AETHERION API contract.")

    def check_for_updates(self) -> dict[str, Any]:
        if not self.config.enabled or not self.config.base_url:
            return {"available": False, "reason": "backend_not_configured"}
        raise NotImplementedError("Update endpoint not available until the backend contract is defined.")
