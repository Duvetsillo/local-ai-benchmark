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

    def pack(self, **_kwargs):
        self.packed = True

    def pack_forget(self):
        self.packed = False


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


def test_focus_section_updates_active_navigation_and_view():
    client = object.__new__(desktop.AetherionDesktopClient)
    dashboard = _Widget()
    models = _Widget()
    client.dashboard_view = dashboard
    client.views = {"dashboard": dashboard, "models": models}
    client.section_var = SimpleNamespace(set=lambda value: setattr(client, "section_label", value))
    client.section_description = SimpleNamespace(set=lambda value: setattr(client, "section_copy", value))
    client.nav_buttons = {"dashboard": _Widget(), "models": _Widget()}
    client.nav_indicators = {"dashboard": _Widget(), "models": _Widget()}

    client.focus_section("models")

    assert client.active_view == "models"
    assert client.section_label == "MODEL LIBRARY"
    assert client.section_copy == "Explore your collection and discover your next model."
    assert client.nav_buttons["models"].options["fg"] == desktop.COLORS["text"]
    assert client.nav_buttons["dashboard"].options["fg"] == desktop.COLORS["muted"]
    assert client.nav_indicators["models"].options["bg"] == desktop.COLORS["accent"]
    assert client.nav_indicators["dashboard"].options["bg"] == desktop.COLORS["surface"]
    assert dashboard.packed is False
    assert models.packed is True


def test_model_fit_summary_explains_estimated_runability():
    client = object.__new__(desktop.AetherionDesktopClient)

    assert client.model_fit_summary("DIRECT RUN: YES · GPU\nVRAM: sufficient") == "LIKELY TO RUN · GPU"
    assert client.model_fit_summary("DIRECT RUN: YES · CPU fallback") == "LIKELY TO RUN · CPU fallback"
    assert client.model_fit_summary("DIRECT RUN: YES · CPU") == "LIKELY TO RUN · CPU"
    assert client.model_fit_summary("DIRECT RUN: NO · Install llama-cpp-python for GGUF") == "NOT READY · required runtime missing"
    assert client.model_fit_summary("DIRECT RUN: NO\nRAM: insufficient") == "NOT RECOMMENDED · available RAM is below estimate"
    assert client.model_fit_summary("DIRECT RUN: UNKNOWN · Model size unavailable") == "CANNOT CONFIRM · model size unavailable"


def test_download_hardware_assessment_checks_ram_and_vram_fit():
    client = object.__new__(desktop.AetherionDesktopClient)
    one_gb_model = 1024 ** 3

    compatible, color = client.assess_download_hardware(
        one_gb_model,
        {
            "memory": {"available_gb": 4.0},
            "gpu": [{"vram_gb": 4.0}],
        },
    )
    assert "LIKELY COMPATIBLE" in compatible
    assert "GPU and RAM" in compatible
    assert color == "#9BE0B5"

    cpu_fallback, color = client.assess_download_hardware(
        one_gb_model,
        {
            "memory": {"available_gb": 4.0},
            "gpu": [{"vram_gb": 1.0}],
        },
    )
    assert "CPU fallback is expected" in cpu_fallback
    assert color == "#F2C879"

    insufficient_ram, color = client.assess_download_hardware(
        2 * one_gb_model,
        {
            "memory": {"available_gb": 2.0},
            "gpu": [{"vram_gb": 16.0}],
        },
    )
    assert "NOT RECOMMENDED" in insufficient_ram
    assert "RAM: ~2.5 GB needed, 2.0 GB available." in insufficient_ram
    assert color == "#FF9292"


def test_download_hardware_assessment_reports_unknown_telemetry():
    client = object.__new__(desktop.AetherionDesktopClient)
    assessment, color = client.assess_download_hardware(
        1024 ** 3,
        {"memory": {"available_gb": 8.0}, "gpu": []},
    )
    assert "LIKELY TO RUN ON CPU" in assessment
    assert "GPU fit is unknown" in assessment
    assert color == "#F2C879"

    unknown_ram, color = client.assess_download_hardware(
        1024 ** 3,
        {"memory": {"available_gb": None}, "gpu": [{"vram_gb": 8.0}]},
    )
    assert "FIT UNKNOWN" in unknown_ram
    assert color == "#F2C879"


def test_remote_model_size_reads_content_length_from_head(monkeypatch):
    class Response:
        headers = {"Content-Length": str(3 * 1024 ** 3)}
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    captured = {}

    def fake_urlopen(request, timeout):
        captured["method"] = request.get_method()
        return Response()

    monkeypatch.setattr(desktop, "urlopen", fake_urlopen)

    assert desktop._remote_model_size("https://models.example/model.gguf") == 3 * 1024 ** 3
    assert captured["method"] == "HEAD"


def test_remote_model_size_falls_back_to_range_request(monkeypatch):
    class Response:
        def __init__(self, headers, status):
            self.headers = headers
            self.status = status

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    methods = []

    def fake_urlopen(request, timeout):
        method = request.get_method()
        methods.append(method)
        if method == "HEAD":
            return Response({}, 200)
        return Response({"Content-Range": "bytes 0-0/2147483648"}, 206)

    monkeypatch.setattr(desktop, "urlopen", fake_urlopen)

    assert desktop._remote_model_size("https://models.example/model.gguf") == 2 * 1024 ** 3
    assert methods == ["HEAD", "GET"]


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
