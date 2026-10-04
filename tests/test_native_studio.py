"""Native UI/service regression checks; no live accounts, models or user files are used."""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from local_ai_benchmark.client.qt import controller as adapter
from local_ai_benchmark.client.qt.app import StudioWindow, initialize_application
from local_ai_benchmark.client.qt.components import Button, Sheet
from local_ai_benchmark.models import ModelInfo
from local_ai_benchmark.providers import Generation, ProviderCancelled, ProviderRouter


@pytest.fixture(scope="module")
def app():
    return initialize_application()


@pytest.fixture
def controller(app, tmp_path):
    c = adapter.StudioController(tmp_path)
    c.preferences["reduce_motion"] = True
    c.session.hardware = {
        "cpu": {"model": "Test CPU", "cores": 8, "threads": 16},
        "memory": {"total_gb": 32, "available_gb": 20},
        "gpu": [{"name": "Test GPU", "vram_gb": 8, "free_vram_gb": 6}],
    }
    c.auth_session = SimpleNamespace(
        username="Test fixture",
        plan="studio",
        offline=False,
        offline_until=dt.datetime.now(dt.UTC) + dt.timedelta(days=1),
        session_token=None,
    )
    yield c
    c.close()


def wait_until(app, predicate, timeout=5000):
    for _ in range(timeout // 10):
        app.processEvents()
        if predicate():
            return
        QTest.qWait(10)
    raise AssertionError("Worker did not complete within the test timeout")


class FixtureProvider:
    name = "ollama"

    def discover(self):
        return [
            ModelInfo("fixture:1b", "ollama", 1024**3, {"quantization_level": "Q4_K_M"})
        ]

    def generate(self, model, prompt, temperature=0, context=4096, stop_event=None):
        if stop_event and stop_event.is_set():
            raise ProviderCancelled("Stopped")
        return Generation("888", 0.05, 0.1, {"eval_count": 2})


def set_provider(controller, provider):
    controller.session.provider = ProviderRouter([provider])
    controller.session.engine.provider = controller.session.provider


def test_discovery_benchmark_and_saved_report_use_existing_engine(
    app, controller, monkeypatch
):
    monkeypatch.setattr(
        "local_ai_benchmark.engine.profile_hardware",
        lambda: SimpleNamespace(to_dict=lambda: {"gpus": []}),
    )
    monkeypatch.setattr(
        "local_ai_benchmark.engine._resource_snapshot",
        lambda: {"cpu_percent": 1, "ram_used_bytes": 1024},
    )
    set_provider(controller, FixtureProvider())
    controller.refresh_models()
    wait_until(app, lambda: not controller.busy)
    assert controller.recommended_model_name == "fixture:1b"
    controller.run("fixture:1b", "math", 0.2, 2048)
    wait_until(app, lambda: not controller.busy)
    assert controller.run_status == "complete"
    assert controller.run_summary["passed_checks"] == 1
    assert controller.records[0]["notes"]["context"] == 2048
    assert controller.records[0]["notes"]["temperature"] == 0.2
    assert Path(controller.records[0]["notes"]["benchmark_results_file"]).is_file()


def test_stop_propagates_to_provider_and_saves_stopped_record(
    app, controller, monkeypatch
):
    import threading

    started = threading.Event()

    class Blocking(FixtureProvider):
        def generate(self, model, prompt, temperature=0, context=4096, stop_event=None):
            started.set()
            stop_event.wait(3)
            raise ProviderCancelled("Stopped")

    monkeypatch.setattr(
        "local_ai_benchmark.engine.profile_hardware",
        lambda: SimpleNamespace(to_dict=lambda: {"gpus": []}),
    )
    monkeypatch.setattr(
        "local_ai_benchmark.engine._resource_snapshot",
        lambda: {"cpu_percent": 0, "ram_used_bytes": 0},
    )
    set_provider(controller, Blocking())
    controller.refresh_models()
    wait_until(app, lambda: not controller.busy)
    controller.run("fixture:1b", "math")
    wait_until(app, started.is_set)
    controller.stop()
    wait_until(app, lambda: not controller.busy)
    assert controller.run_status == "stopped"
    assert controller.records[0]["notes"]["stopped_by_user"] is True
    assert controller.records[0]["result"]["task_count"] == 0


def test_expired_access_cannot_run(app, controller, monkeypatch):
    cleared = []
    monkeypatch.setattr(adapter, "clear_cached_session", lambda: cleared.append(True))
    controller.models = {"fixture:1b": FixtureProvider().discover()[0]}
    controller.auth_session.offline_until = dt.datetime.now(dt.UTC) - dt.timedelta(
        seconds=1
    )
    controller.run("fixture:1b", "math")
    assert controller.auth_session is None
    assert controller.busy is False
    assert cleared == [True]


def test_stale_account_response_does_not_restore_signed_out_access(app, controller):
    old_session = controller.auth_session
    controller.auth_session = None
    controller.auth_epoch = 2
    controller.events.put(("auth", True, (1, old_session)))
    controller._drain()
    assert controller.auth_session is None


@pytest.mark.parametrize("mode", ["login", "register"])
def test_account_forms_keep_existing_service_contract(
    app, controller, monkeypatch, mode
):
    calls = []
    session = controller.auth_session

    class Service:
        def __init__(self, url):
            assert url == "https://accounts.example"

        def login(self, username, password, machine):
            calls.append(("login", username, password, machine))
            return session

        def register(self, username, password, key, machine):
            calls.append(("register", username, password, key, machine))
            return session

    monkeypatch.setattr(adapter, "AccountService", Service)
    monkeypatch.setattr(adapter, "save_service_url", lambda url: url)
    monkeypatch.setattr(adapter, "machine_fingerprint", lambda: "fixture-machine")
    controller.auth_session = None
    values = {
        "username": " test-user ",
        "password": "fixture-password",
        "confirm": "fixture-password",
        "license_key": " fixture-key ",
    }
    controller.authenticate(mode, values, "https://accounts.example")
    wait_until(app, lambda: "auth" not in controller.pending)
    assert controller.auth_session is session
    assert calls[0][0] == mode
    assert calls[0][1] == "test-user"
    assert calls[0][-1] == "fixture-machine"
    if mode == "register":
        assert calls[0][-2] == "fixture-key"


def test_registration_validation_does_not_send_incomplete_credentials(
    app, controller, monkeypatch
):
    errors = []
    controller.auth_feedback.connect(lambda text, failed: errors.append((text, failed)))
    monkeypatch.setattr(adapter, "save_service_url", lambda value: value)
    controller.authenticate(
        "register",
        {
            "username": "test",
            "password": "short",
            "confirm": "short",
            "license_key": "test",
        },
        "https://accounts.example",
    )
    assert not controller.pending
    assert errors[-1][1] is True
    assert "12 characters" in errors[-1][0]


def test_unknown_memory_does_not_recommend_a_model(app, controller):
    controller.session.hardware["memory"] = {}
    set_provider(controller, FixtureProvider())
    controller.refresh_models()
    wait_until(app, lambda: not controller.busy)
    assert controller.recommended_model_name is None


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/model.gguf",
        "https://example.com/model.exe",
        "https://user:secret@example.com/model.gguf",
        "https://example.com/bad%3Aname.gguf",
    ],
)
def test_download_rejects_invalid_url_and_file_names(url):
    with pytest.raises(ValueError):
        adapter.download_name(url)


def test_download_is_atomic_and_keeps_existing_files(app, controller, monkeypatch):
    import io

    class Response(io.BytesIO):
        def __init__(self, content):
            super().__init__(content)
            self.headers = {"Content-Length": "4"}

    monkeypatch.setattr(adapter, "urlopen", lambda *_args, **_kwargs: Response(b"GGUF"))
    controller.download("https://models.example/fixture.gguf")
    wait_until(app, lambda: "download" not in controller.pending)
    target = controller.session.gguf_provider.models_dir / "fixture.gguf"
    assert target.read_bytes() == b"GGUF"
    assert not target.with_suffix(".gguf.part").exists()
    notices = []
    controller.download_event.connect(
        lambda event, payload: notices.append((event, payload))
    )
    controller.download("https://models.example/fixture.gguf")
    assert notices[-1][0] == "error"
    assert target.read_bytes() == b"GGUF"


def test_preferences_and_custom_folder_survive_restart(app, controller, monkeypatch):
    monkeypatch.setattr(controller, "refresh_models", lambda: None)
    target = controller.session.results_dir / "custom-models"
    target.mkdir()
    controller.set_model_folder(target)
    controller.save_preference("reduce_motion", True)
    restored = adapter.StudioController(controller.session.results_dir)
    assert restored.preferences["reduce_motion"] is True
    assert restored.session.gguf_provider.models_dir == target
    restored.close()


@pytest.fixture
def window(app, controller, monkeypatch):
    monkeypatch.setattr(controller, "refresh_models", lambda: None)
    monkeypatch.setattr(controller, "refresh_hardware", lambda: None)
    controller.models = {m.name: m for m in FixtureProvider().discover()}
    controller.recommended_model_name = "fixture:1b"
    w = StudioWindow(controller)
    w.setMinimumSize(920, 640)
    w.resize(1440, 940)
    w.show()
    app.processEvents()
    yield w
    w._allow_close = True
    w.close()
    w.deleteLater()
    app.processEvents()


def test_navigation_search_prepare_and_keyboard_activation(app, window):
    QTest.keyClick(window, Qt.Key_2, Qt.ControlModifier)
    app.processEvents()
    assert window.active_view == "models"
    models = window.pages["models"]
    models.search.setText("not-installed")
    app.processEvents()
    assert "0 models shown" in models.summary.text()
    models.search.clear()
    window.prepare_model("fixture:1b")
    assert window.active_view == "benchmarks"
    assert window.pages["benchmarks"].model.currentText() == "fixture:1b"
    called = []
    button = Button("Keyboard action", callback=lambda: called.append(True))
    button.show()
    button.setFocus()
    QTest.keyClick(button, Qt.Key_Return)
    assert called == [True]
    button.close()


@pytest.mark.parametrize(
    "width,height", [(920, 640), (1040, 740), (1440, 940), (1920, 1080), (2560, 1440)]
)
def test_resizable_pages_do_not_overflow_horizontal_viewport(
    app, window, width, height
):
    window.resize(width, height)
    app.processEvents()
    for key, page in window.pages.items():
        window.navigate(key)
        app.processEvents()
        viewport = window.page_areas[key].viewport()
        assert page.width() <= viewport.width() + 2, (
            key,
            page.width(),
            viewport.width(),
        )


def test_modal_escape_and_records_filter_sort(app, window):
    c = window.controller
    c.records = [
        {
            "benchmark": "Slow",
            "status": "complete",
            "created_at": "2026-10-01T12:00:00+00:00",
            "result": {"average_tokens_per_second": 2, "passed_checks": 1},
        },
        {
            "benchmark": "Fast",
            "status": "partial",
            "created_at": "2026-10-02T12:00:00+00:00",
            "result": {"average_tokens_per_second": 10, "passed_checks": 2},
        },
    ]
    page = window.pages["results"]
    page.refresh()
    page.order.setCurrentText("Fastest first")
    assert page.table.item(0, 0).text() == "Fast"
    page.search.setText("Slow")
    assert page.table.rowCount() == 1
    assert page.table.item(0, 0).text() == "Slow"
    sheet = Sheet(window, "Modal keyboard test")
    sheet.show()
    app.processEvents()
    QTest.keyClick(sheet, Qt.Key_Escape)
    assert not sheet.isVisible()


def test_unbroken_model_and_cpu_names_do_not_expand_pages(app, window):
    c = window.controller
    name = "custom/" + "X" * 240
    c.models = {name: ModelInfo(name, "ollama", 1024**3)}
    c.recommended_model_name = name
    c.session.hardware["cpu"]["model"] = "X" * 180
    window.refresh("models")
    window.resize(1040, 740)
    for key in ("workspace", "models", "benchmarks"):
        window.navigate(key)
        app.processEvents()
        assert (
            window.pages[key].width() <= window.page_areas[key].viewport().width() + 2
        )


def test_fit_labels_follow_hardware_updates_without_losing_focus(app, window):
    library = window.pages["models"]
    model_row = library.rows.itemAt(0).widget()
    model_row.action.setFocus()
    window.controller.session.hardware["memory"]["available_gb"] = 0.5
    window.refresh("hardware")
    app.processEvents()
    assert "NOT RECOMMENDED" in model_row.fit_label.text()
    assert library.rows.itemAt(0).widget() is model_row
    home_row = window.pages["workspace"].model_rows.itemAt(0).widget()
    assert "NOT RECOMMENDED" in home_row.fit_label.text()


def test_no_model_or_access_placeholder_enables_real_benchmark(
    app, controller, monkeypatch
):
    monkeypatch.setattr(controller, "refresh_hardware", lambda: None)
    monkeypatch.setattr(controller, "refresh_models", lambda: None)
    controller.models = {}
    controller.auth_session = None
    window = StudioWindow(controller)
    window.show()
    app.processEvents()
    assert window.gate_stack.currentIndex() == 0
    window.navigate("benchmarks")
    assert window.gate_stack.currentIndex() == 0
    assert not window.pages["benchmarks"].run_button.isEnabled()
    window.close()
