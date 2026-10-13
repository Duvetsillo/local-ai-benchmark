# Contributing

Thanks for helping improve Local AI Benchmark.

## Development setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e ".[dev,system,desktop]" -r server/requirements.txt
py -m pytest -q
```

On Linux and macOS, use `python3` and activate `.venv/bin/activate` instead.

The full suite includes the desktop UI and license server tests, so install both
sets of dependencies. On Ubuntu, install the Qt runtime libraries first:

```bash
sudo apt-get update
sudo apt-get install -y libegl1 libopengl0
```

CI runs the desktop tests with `QT_QPA_PLATFORM=offscreen`; no display, live
license credentials, GPU, or Ollama server is required.

## Guidelines

- Keep providers local-first and do not add telemetry.
- Never invent unavailable measurements; use `null`.
- Keep tests independent of a GPU, Ollama, or downloaded models.
- Do not commit files from `results/`.
- Add or update tests with behavior changes.
