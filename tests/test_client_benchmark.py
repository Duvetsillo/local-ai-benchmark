from __future__ import annotations

import datetime as dt
import queue
from types import SimpleNamespace

from local_ai_benchmark.client import desktop


class _Widget:
    def __init__(self):
        self.options = {}

    def configure(self, **_kwargs):
        self.options.update(_kwargs)

    config = configure

    def delete(self, *_args):
        pass

    def winfo_exists(self):
        return True


def test_run_selected_benchmark_passes_a_stop_event(monkeypatch):
    captured = {}

    class InlineThread:
        def __init__(self, *, target, daemon):
            self.target = target

        def start(self):
            self.target()

    monkeypatch.setattr(desktop.threading, "Thread", InlineThread)

    class Engine:
        def run(self, model, category, *, progress_callback, stop_event):
            captured["stop_event"] = stop_event
            raise RuntimeError("sentinel")

    client = object.__new__(desktop.AetherionDesktopClient)
    client.auth_session = SimpleNamespace(
        offline_until=dt.datetime.now(dt.UTC) + dt.timedelta(days=1)
    )
    client.model_var = SimpleNamespace(get=lambda: "qwen3:4b")
    client.models = {"qwen3:4b": SimpleNamespace(details={}, provider="ollama")}
    client.busy = False
    client.assess_model = lambda _model: "DIRECT RUN: YES"
    client.category_var = SimpleNamespace(get=lambda: "All tasks")
    client.refresh_button = _Widget()
    client.run_button = _Widget()
    client.stop_button = _Widget()
    client.model_menu = _Widget()
    client.category_menu = _Widget()
    client.status_var = SimpleNamespace(set=lambda _value: None)
    client.result_status = _Widget()
    client.progress = _Widget()
    client.progress_text = _Widget()
    client.output = _Widget()
    client.append_output = lambda *_args: None
    client.session = SimpleNamespace(engine=Engine())
    client.events = queue.Queue()
    client.benchmark_stop_event = None

    client.run_selected_benchmark()

    assert captured["stop_event"] is client.benchmark_stop_event
    assert captured["stop_event"].is_set() is False
    assert client.events.get_nowait() == ("run_error", "sentinel")


def test_model_fit_summary_explains_estimated_runability():
    client = object.__new__(desktop.AetherionDesktopClient)

    assert client.model_fit_summary("DIRECT RUN: YES · GPU\nVRAM: sufficient") == "LIKELY TO RUN · GPU"
    assert client.model_fit_summary("DIRECT RUN: YES · CPU fallback") == "LIKELY TO RUN · CPU fallback"
    assert client.model_fit_summary("DIRECT RUN: YES · CPU") == "LIKELY TO RUN · CPU"
    assert client.model_fit_summary("DIRECT RUN: NO · Install llama-cpp-python for GGUF") == "NOT READY · required runtime missing"
    assert client.model_fit_summary("DIRECT RUN: NO\nRAM: insufficient") == "NOT RECOMMENDED · available RAM is below estimate"
    assert client.model_fit_summary("DIRECT RUN: UNKNOWN · Model size unavailable") == "CANNOT CONFIRM · model size unavailable"


def test_download_model_saves_gguf_to_selected_folder(monkeypatch, tmp_path):
    model_data = b"test model contents"

    class Response:
        headers = {"Content-Length": str(len(model_data))}

        def __init__(self):
            self.sent = False

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _size):
            if self.sent:
                return b""
            self.sent = True
            return model_data

    class InlineThread:
        def __init__(self, *, target, daemon):
            self.target = target

        def start(self):
            self.target()

    monkeypatch.setattr(desktop, "urlopen", lambda *_args, **_kwargs: Response())
    monkeypatch.setattr(desktop.threading, "Thread", InlineThread)
    client = object.__new__(desktop.AetherionDesktopClient)
    client.session = SimpleNamespace(
        gguf_provider=SimpleNamespace(models_dir=tmp_path)
    )
    client.download_status = _Widget()
    client.download_progress = _Widget()
    client.events = queue.Queue()
    button = _Widget()

    client.download_model(
        "https://models.example/test-model.gguf?download=true",
        button,
    )

    assert (tmp_path / "test-model.gguf").read_bytes() == model_data
    assert button.options["state"] == "disabled"
    assert client.events.get_nowait()[0] == "model_download_progress"
    assert client.events.get_nowait() == (
        "model_download_complete",
        str(tmp_path / "test-model.gguf"),
    )


def test_download_button_is_reenabled_after_success_or_failure():
    client = object.__new__(desktop.AetherionDesktopClient)
    client.closing = False
    client.events = queue.Queue()
    client.download_progress = _Widget()
    client.download_status = _Widget()
    client.download_button = _Widget()
    client.root = SimpleNamespace(after=lambda *_args: None)
    client.append_output = lambda *_args: None
    client.refresh_models = lambda: None

    client.events.put(("model_download_complete", "test-model.gguf"))
    client.process_events()
    assert client.download_button.options["state"] == "normal"

    client.download_button.options.clear()
    client.events.put(("model_download_error", "network error"))
    client.process_events()
    assert client.download_button.options["state"] == "normal"
