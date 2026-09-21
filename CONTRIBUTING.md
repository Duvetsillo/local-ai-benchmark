# Contributing

Thanks for helping improve Local AI Benchmark.

## Development setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e ".[dev,system]"
py -m pytest -q
```

On Linux and macOS, use `python3` and activate `.venv/bin/activate` instead.

## Guidelines

- Keep providers local-first and do not add telemetry.
- Never invent unavailable measurements; use `null`.
- Keep tests independent of a GPU, Ollama, or downloaded models.
- Do not commit files from `results/`.
- Add or update tests with behavior changes.
