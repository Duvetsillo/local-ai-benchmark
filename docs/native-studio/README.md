# Aetherion Studio — native desktop redesign

The desktop frontend is now Qt 6 / PySide6. This replaces the Tkinter shell, rather than adding another theme to its existing layouts. The Python benchmark and account services remain the integration boundary.

## Architecture audit

The original application combined Tk widgets, rendering, worker queues and service calls in `client/desktop.py` and `client/studio.py`. It already supported Ollama and GGUF discovery, model fit estimates, downloaded GGUF files and size preflight, task suites, cancellation, result summaries, saved JSON, account registration/login, encrypted cached access, runtime installation and folder selection. Hardware, results, history and settings were separate views. CLI and the static website are independent frontends. The updater/API modules contain inactive integration boundaries and were not turned into fictitious live services.

Small Segoe UI fonts (including 7–9 point labels), fixed Canvas coordinates, hardcoded secondary palettes and unsmoothed Tk Canvas primitives made the previous interface inconsistent. There was no explicit DPI setup in its launcher. The audit cannot establish the old executable's DPI awareness on every Windows installation; missing configuration and the Canvas rendering limits were observable in source. Qt provides antialiased text/SVG painting and per-monitor DPI handling without bitmap text or scaling a rendered page.

## Design system

See [DESIGN.md](DESIGN.md). Sidebar navigation owns structure, while each page owns one task. The workspace presents device capabilities first, a recommended model second, and collection/activity third. The benchmark lab exposes a clear Run action and separates configuration from actual execution output. At smaller widths it stacks configuration and execution vertically. Other views remain searchable, keyboard accessible and scrollable.

The new frontend lives in `src/local_ai_benchmark/client/qt/`:

- `tokens.py`: material, color and typography rules.
- `components.py`: native buttons/navigation, vector icons, surfaces, modal sheets, progress/activity indicators, charts and transitions.
- `controller.py`: GUI-thread state with worker threads for blocking services; account expiry, benchmark cancellation, downloads and durable preferences.
- `pages.py`: workspace, library, lab, results, history, hardware, settings and access.
- `app.py`: window, native Windows title bar, command palette, shortcuts and lifecycle.
- `assets/`: local Inter font, Lucide SVGs, brand icon, licenses and the Windows DPI manifest.

The original Tk class remains available to existing regression tests. Its historic launch function redirects to the Qt client. Normal CLI and module entrypoints also launch Qt.

## Run and build

```powershell
python -m pip install -e ".[desktop,dev,installer]"
python -m local_ai_benchmark.client
python -m pytest -q
python -m ruff check src/local_ai_benchmark/client/qt tests/test_native_studio.py tools/verify_native_ui.py
python -m PyInstaller --noconfirm --distpath dist-premium --workpath build/premium Aetherion-Client.spec
```

`python build_client.py` still builds into `dist/` and updates the existing download location. The redesign delivery uses `dist-premium/` so it can be reviewed alongside earlier builds. Inter and icons are bundled and need no network request at runtime.

## Validation and practical limits

The original 39 tests and new native/service regressions cover discovery, benchmark execution/configuration, cancellation, report persistence, access expiry, stale account responses, atomic download behavior, custom folders, keyboard activation, model/record search, sorting, dialogs, long names and window resizing. CI installs the desktop extra and runs Qt in offscreen mode across its existing OS matrix.

`tools/verify_native_ui.py --scale 1.25` verifies seven pages at five logical window sizes, from 920×640 to 2560×1440. It checks output pixel dimensions and absence of horizontal page overflow at 100%, 125%, 150% and 200%. The screenshots explicitly use **UI TEST FIXTURE** data stored only in a temporary directory. They are rendered from the actual implemented widgets. The JSON reports record scale, font and layout checks. These are simulated scale-factor checks, not proof of moving the window between every physical monitor configuration.

Materials use restrained translucent painting and highlights; modal backgrounds are actually blurred once when the dialog opens. Windows DWM supplies supported title-bar backdrop/rounded-corner behavior, with an opaque fallback. This is an adapted Windows material system, not an implementation of Apple's proprietary Liquid Glass renderer. Native title-bar resizing, snapping and system controls are retained.

Inter and Lucide license texts are included with the assets. Qt/PySide retain their upstream licensing terms. GGUF inference still requires `llama-cpp-python`: source installations can install it from Settings; a frozen build must bundle it when built. Ollama inference is available in the standalone build. This limitation existed in the original client and is shown explicitly in Settings rather than hidden by a decorative status.

Online registration/sign-in are exercised with service fixtures, without creating accounts or using invented license keys. The `live-ollama.json` verification report separately records the real local Ollama check and whether a valid saved account was available for the native-client run.

The final Windows executable was launched and its native Studio window was verified. The first packaged run exposed an incompatible `icuuc.dll` selected from the development tools' Poppler directory. The spec now excludes that DLL and its accidentally collected data dependency, allowing Qt to use the Windows system ICU API. The corrected executable launched successfully.

Final local checks: **63 tests passed**, lint passed for the new frontend/tests/tool, all four simulated DPI levels passed, and the authenticated native controller discovered **six real Ollama models**. A real math task on `qwen2:0.5b` completed and saved a report with **0/1 validation checks passed** and **150.85 tokens/s**. That is a model validation failure, not a passing benchmark result; it confirms that the UI preserves the distinction between execution completion and answer correctness. The run used temporary storage, leaving the user's report history untouched.
