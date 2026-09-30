import json
import time
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen

from .models import ModelInfo


@dataclass
class Generation:
    text: str
    first_token_seconds: float | None
    total_seconds: float
    usage: dict


class ModelProvider(Protocol):
    name: str

    def generate(self, model: str, prompt: str, temperature: float = 0.0,
                 context: int = 4096, stop_event: threading.Event | None = None) -> Generation: ...


class ProviderError(RuntimeError):
    pass


class ProviderCancelled(ProviderError):
    """Raised when the user stops an active generation."""


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
                 context: int = 4096, stop_event: threading.Event | None = None) -> Generation:
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
                    if stop_event is not None and stop_event.is_set():
                        raise ProviderCancelled("Benchmark stopped by user")
                    if not raw_line.strip():
                        continue
                    item = json.loads(raw_line)
                    text = item.get("response", "")
                    if text and first_token is None:
                        first_token = time.perf_counter() - started
                    chunks.append(text)
                    usage.update({key: value for key, value in item.items()
                                  if key.endswith("_duration") or key.endswith("_count")})
        except ProviderCancelled:
            raise
        except (OSError, URLError, json.JSONDecodeError) as exc:
            raise ProviderError(f"Ollama generation failed: {exc}") from exc
        return Generation("".join(chunks), first_token, time.perf_counter() - started, usage)


class LlamaCppProvider:
    """Optional in-process provider for local GGUF models.

    The llama-cpp-python dependency is loaded only when generation is requested,
    so installations that use Ollama do not need to install it.
    """

    name = "llama.cpp"

    def __init__(self, models_dir: str | Path, n_gpu_layers: int = -1):
        self.models_dir = Path(models_dir)
        self.n_gpu_layers = n_gpu_layers
        self._models: dict[str, Any] = {}

    def set_models_dir(self, models_dir: str | Path) -> None:
        self.models_dir = Path(models_dir)
        self._models.clear()

    def discover(self) -> list[ModelInfo]:
        if not self.models_dir.exists():
            return []
        return [
            ModelInfo(
                name=path.name,
                provider=self.name,
                size_bytes=path.stat().st_size,
                details={"path": str(path), "format": "GGUF"},
            )
            for path in sorted(self.models_dir.glob("*.gguf"))
            if path.is_file()
        ]

    def _load_model(self, model: str) -> Any:
        if model not in self._models:
            try:
                from llama_cpp import Llama
            except ImportError as exc:
                raise ProviderError(
                    "llama-cpp-python is not installed. Install the optional llama runtime to use GGUF models."
                ) from exc
            model_path = self.models_dir / model
            if not model_path.is_file():
                raise ProviderError(f"GGUF model not found: {model_path}")
            try:
                self._models[model] = Llama(
                    model_path=str(model_path),
                    n_ctx=4096,
                    n_gpu_layers=self.n_gpu_layers,
                    verbose=False,
                )
            except Exception as exc:
                raise ProviderError(f"Could not load GGUF model {model}: {exc}") from exc
        return self._models[model]

    def generate(self, model: str, prompt: str, temperature: float = 0.0,
                 context: int = 4096, stop_event: threading.Event | None = None) -> Generation:
        model_instance = self._load_model(model)
        started = time.perf_counter()
        first_token = None
        chunks: list[str] = []
        usage: dict[str, Any] = {}
        try:
            stream = model_instance.create_completion(
                prompt=prompt,
                temperature=temperature,
                max_tokens=-1,
                stream=True,
            )
            for item in stream:
                if stop_event is not None and stop_event.is_set():
                    raise ProviderCancelled("Benchmark stopped by user")
                text = item.get("choices", [{}])[0].get("text", "")
                if text and first_token is None:
                    first_token = time.perf_counter() - started
                chunks.append(text)
                item_usage = item.get("usage") or {}
                if item_usage:
                    usage.update(item_usage)
        except ProviderCancelled:
            raise
        except Exception as exc:
            raise ProviderError(f"GGUF generation failed: {exc}") from exc
        if "completion_tokens" in usage:
            usage["eval_count"] = usage["completion_tokens"]
        if "prompt_tokens" in usage:
            usage["prompt_eval_count"] = usage["prompt_tokens"]
        return Generation("".join(chunks), first_token, time.perf_counter() - started, usage)


class ProviderRouter:
    """Combines available runtimes while keeping model selection explicit."""

    name = "local-runtime"

    def __init__(self, providers: list[ModelProvider]):
        self.providers = providers
        self._model_providers: dict[str, ModelProvider] = {}

    def discover(self) -> list[ModelInfo]:
        models: list[ModelInfo] = []
        self._model_providers.clear()
        for provider in self.providers:
            try:
                discovered = provider.discover()
            except ProviderError:
                continue
            for model in discovered:
                name = model.name
                if name in self._model_providers:
                    name = f"{model.provider}/{name}"
                    model = ModelInfo(name=name, provider=model.provider,
                                      size_bytes=model.size_bytes, details=model.details)
                self._model_providers[name] = provider
                models.append(model)
        return models

    def generate(self, model: str, prompt: str, temperature: float = 0.0,
                 context: int = 4096, stop_event: threading.Event | None = None) -> Generation:
        provider = self._model_providers.get(model)
        if provider is None:
            raise ProviderError("Model list is outdated. Refresh the available local models and try again.")
        actual_model = model.split("/", 1)[1] if "/" in model else model
        if stop_event is None:
            return provider.generate(actual_model, prompt, temperature, context)
        return provider.generate(actual_model, prompt, temperature, context, stop_event=stop_event)
