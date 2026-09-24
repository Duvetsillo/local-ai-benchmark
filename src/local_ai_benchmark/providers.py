import json
import time
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from .models import ModelInfo


@dataclass
class Generation:
    text: str
    first_token_seconds: float | None
    total_seconds: float
    usage: dict


class ProviderError(RuntimeError):
    pass


class OllamaProvider:
    name = "ollama"

    def __init__(self, endpoint: str = "http://127.0.0.1:11434", timeout: int = 120):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout

    def _request(self, path: str, payload: dict | None = None) -> object:
        data = json.dumps(payload).encode() if payload is not None else None
        request = Request(self.endpoint + path, data=data, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode())
        except (OSError, URLError, json.JSONDecodeError) as exc:
            raise ProviderError(f"Ollama request failed: {exc}") from exc

    def discover(self) -> list[ModelInfo]:
        data = self._request("/api/tags")
        return [ModelInfo(name=item["name"], provider=self.name,
                          size_bytes=item.get("size"), details=item.get("details", {}))
                for item in data.get("models", [])]

    def generate(self, model: str, prompt: str, temperature: float = 0.0,
                 context: int = 4096) -> Generation:
        request = Request(self.endpoint + "/api/generate", data=json.dumps({
            "model": model, "prompt": prompt, "stream": True,
            "options": {"temperature": temperature, "num_ctx": context},
        }).encode(), headers={"Content-Type": "application/json"})
        started = time.perf_counter()
        first_token = None
        chunks: list[str] = []
        usage: dict = {}
        try:
            with urlopen(request, timeout=self.timeout) as response:
                for raw_line in response:
                    if not raw_line.strip():
                        continue
                    item = json.loads(raw_line)
                    text = item.get("response", "")
                    if text and first_token is None:
                        first_token = time.perf_counter() - started
                    chunks.append(text)
                    usage.update({key: value for key, value in item.items()
                                  if key.endswith("_duration") or key.endswith("_count")})
        except (OSError, URLError, json.JSONDecodeError) as exc:
            raise ProviderError(f"Ollama generation failed: {exc}") from exc
        return Generation("".join(chunks), first_token, time.perf_counter() - started, usage)
