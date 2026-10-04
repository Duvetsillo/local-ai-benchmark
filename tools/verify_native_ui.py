"""Reproducible Qt layout/DPI verification using isolated, explicitly labelled fixtures."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=float, default=1)
    parser.add_argument(
        "--output", type=Path, default=Path("docs/native-studio/verification")
    )
    args = parser.parse_args()
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["QT_SCALE_FACTOR"] = str(args.scale)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from PySide6.QtTest import QTest

    from local_ai_benchmark.client.qt.app import StudioWindow, initialize_application
    from local_ai_benchmark.client.qt.components import Sheet
    from local_ai_benchmark.client.qt.controller import StudioController
    from local_ai_benchmark.client.qt.pages import DownloadSheet
    from local_ai_benchmark.models import ModelInfo

    args.output.mkdir(parents=True, exist_ok=True)
    app = initialize_application()
    with tempfile.TemporaryDirectory() as folder:
        c = StudioController(Path(folder))
        c.refresh_models = lambda: None
        c.refresh_hardware = lambda: None
        c.preferences["reduce_motion"] = True
        c.session.hardware = {
            "cpu": {
                "model": "AMD Ryzen 7 5800X",
                "cores": 8,
                "threads": 16,
                "usage_percent": 12,
            },
            "memory": {"total_gb": 32, "available_gb": 22, "used_percent": 31},
            "gpu": [
                {
                    "name": "NVIDIA GeForce RTX 4060",
                    "vram_gb": 8,
                    "free_vram_gb": 6.8,
                    "usage_percent": 3,
                    "driver": "Test fixture",
                }
            ],
            "os": {"name": "Windows", "version": "11", "architecture": "AMD64"},
            "updated_at": "2026-10-04T18:00:00+00:00",
        }
        c.auth_session = SimpleNamespace(
            username="UI TEST FIXTURE",
            plan="studio",
            offline=False,
            offline_until=dt.datetime.now(dt.UTC) + dt.timedelta(days=1),
        )
        models = [
            ModelInfo(
                "qwen2.5:3b", "ollama", 2 * 1024**3, {"quantization_level": "Q4_K_M"}
            ),
            ModelInfo(
                "llama3.2:3b",
                "ollama",
                int(2.1 * 1024**3),
                {"quantization_level": "Q4_K_M"},
            ),
            ModelInfo(
                "phi-3.5-mini.gguf",
                "gguf",
                int(2.4 * 1024**3),
                {"quantization_level": "Q4_K_M"},
            ),
        ]
        c.models = {model.name: model for model in models}
        c.recommended_model_name = models[0].name
        c.records = [
            {
                "run_id": "TEST-1",
                "benchmark": "qwen2.5:3b",
                "created_at": "2026-10-04T18:00:00+00:00",
                "status": "complete",
                "result": {
                    "task_count": 5,
                    "passed_checks": 4,
                    "average_tokens_per_second": 38.5,
                },
            },
            {
                "run_id": "TEST-2",
                "benchmark": "llama3.2:3b",
                "created_at": "2026-10-04T17:00:00+00:00",
                "status": "complete",
                "result": {
                    "task_count": 5,
                    "passed_checks": 3,
                    "average_tokens_per_second": 31.2,
                },
            },
        ]
        started = time.perf_counter()
        w = StudioWindow(c)
        w.setMinimumSize(920, 640)
        w.resize(1440, 940)
        w.show()
        QTest.qWait(30)
        checks = []
        renders = []
        for width, height in (
            (920, 640),
            (1040, 740),
            (1440, 940),
            (1920, 1080),
            (2560, 1440),
        ):
            w.resize(width, height)
            app.processEvents()
            for key, page in w.pages.items():
                w.navigate(key)
                app.processEvents()
                area = w.page_areas[key]
                assert page.width() <= area.viewport().width() + 2, (
                    width,
                    key,
                    page.width(),
                    area.viewport().width(),
                )
                tick = time.perf_counter()
                image = w.grab()
                renders.append((time.perf_counter() - tick) * 1000)
                assert abs(image.width() - width * args.scale) <= 1
                assert abs(image.height() - height * args.scale) <= 1
                checks.append(
                    {
                        "size": [width, height],
                        "view": key,
                        "physical_pixels": [image.width(), image.height()],
                    }
                )
                if width == 1440:
                    image.save(str(args.output / f"{key}-{args.scale:g}x.png"))
        w.resize(1440, 940)
        w.navigate("workspace")
        dialog = DownloadSheet(w)
        dialog.show()
        app.processEvents()
        dialog.grab().save(str(args.output / f"download-{args.scale:g}x.png"))
        dialog.reject()
        c.auth_session = None
        w.on_auth()
        for mode in ("login", "register"):
            w.auth_page.set_mode(mode)
            app.processEvents()
            w.grab().save(str(args.output / f"auth-{mode}-{args.scale:g}x.png"))
        app.setProperty("reduce_motion", False)
        c.auth_session = SimpleNamespace(
            username="UI TEST FIXTURE",
            plan="studio",
            offline=False,
            offline_until=dt.datetime.now(dt.UTC) + dt.timedelta(days=1),
        )
        w.on_auth()
        for key in ("models", "workspace", "benchmarks", "results"):
            w.navigate(key)
            for _ in range(40):
                QTest.qWait(20)
                if w.page_areas[key].graphicsEffect() is None:
                    break
            assert (
                w.page_areas[key].graphicsEffect() is None
            )  # native text after settling
        sheet = Sheet(w, "Motion verification")
        sheet.show()
        from PySide6.QtWidgets import QGraphicsDropShadowEffect

        for _ in range(40):
            QTest.qWait(20)
            if isinstance(sheet.surface.graphicsEffect(), QGraphicsDropShadowEffect):
                break
        assert isinstance(
            sheet.surface.graphicsEffect(), QGraphicsDropShadowEffect
        )  # ambient shadow restored
        sheet.reject()
        report = {
            "fixture_data": True,
            "scale": args.scale,
            "device_pixel_ratio": w.devicePixelRatioF(),
            "font": app.font().family(),
            "checks": checks,
            "render_ms_median": sorted(renders)[len(renders) // 2],
            "verification_seconds": round(time.perf_counter() - started, 3),
        }
        (args.output / f"report-{args.scale:g}x.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print(
            json.dumps({key: value for key, value in report.items() if key != "checks"})
        )
        w._allow_close = True
        w.close()


if __name__ == "__main__":
    main()
