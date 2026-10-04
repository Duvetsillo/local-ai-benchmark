# Local AI Benchmark

A practical project for answering one question:

> Which local model fits my hardware and workload best?

Local AI Benchmark profiles your machine, discovers local models available through Ollama, runs a small deterministic task suite, and stores reproducible JSON results. The goal is to help you choose the right model for your hardware without relying on cloud services.

## Why this project exists

The project is designed for local AI benchmarking and model selection. It focuses on:

- measuring local hardware characteristics,
- detecting installed Ollama models,
- running deterministic tasks,
- checking whether a model responds correctly,
- comparing expected speed and quality against a local machine profile.

This is not a chatbot, and it is not a cloud evaluation platform. It is a local decision tool.

## Features

- Hardware profiling for CPU, RAM, and NVIDIA GPU telemetry
- Local model discovery via Ollama
- Estimated model fit guidance that indicates whether a model is likely to run with GPU or CPU, or whether a runtime or more memory is needed
- In-client GGUF model downloads from the catalog or a direct external HTTPS `.gguf` URL to the selected local model folder
- Download preflight estimates local RAM and GPU VRAM fit using the remote model file size when the host exposes it
- Deterministic validation tasks for math, JSON, coding, and general prompts
- Reproducible result output in JSON
- Local dashboard for quick review
- Privacy-first behavior with no cloud telemetry

## Requirements

- Python 3.11 or newer
- A local Ollama installation
- Optional: `psutil` for more complete memory and CPU telemetry
- Optional: `nvidia-smi` for GPU telemetry

## Quick start

### Desktop client (Windows)

The current desktop UI uses native Qt 6 / PySide6 with bundled Inter typography, SVG icons and Windows per-monitor DPI scaling. See [the native Studio redesign](docs/native-studio/README.md) for architecture, verification and build details. To run from source, install `python -m pip install -e ".[desktop]"` and launch `python -m local_ai_benchmark.client`.

1. Install and start [Ollama](https://ollama.com/download).
2. Download and open `downloads/Aetherion-Client.exe`.
3. Select an installed model and task suite, then choose **Run Benchmark**.
4. Open the results folder from the client to review the saved JSON files.

If Ollama has no models yet, run `ollama pull <model>` in PowerShell and refresh the model list. The benchmark and its result files stay on the user's computer. The client contacts the configured license service only for account authentication and entitlement refresh.

### License activation

New users must use a signed license key to create an account and choose a username/password. The account is claimed against one key and one computer. Returning users sign in with their credentials; they do not need another key. Aetherion License Manager lists accounts, allows suspending/reactivating them, and adds renewal days to the existing entitlement after payment. Passwords are stored by the service as Argon2id hashes.

The benchmark and files remain local. A compact online account/entitlement service manages users and expiry. After successful sign-in the client keeps an encrypted, server-signed session pass with a maximum seven-day offline window for the same Windows user and machine. The **SIGN OUT** action revokes the online session and deletes the offline pass. The service is implemented under `server/` and uses Docker Compose with Caddy for HTTPS; deployment remains configurable until a domain/VPS address is selected. See [`server/README.md`](server/README.md), `tools/README-License-Manager.md`, and `tools/Aetherion-License-Manager.ps1`.

The owner initializes the signing authority once using **Create authority** in the separate Windows Forms app. Its private key is protected with Windows DPAPI under `%LOCALAPPDATA%\Aetherion\licensing\signing_key.dpapi`; only its public key is embedded in Aetherion. Build the release client after setting the public key and the service endpoint. New keys are synced to the service before an account can claim them. Previously issued keys can be registered through **Sync existing key** after signature verification. The manager's VPS URL and admin token are saved encrypted for the current Windows account.

Windows may show a SmartScreen warning for locally built executables that are not code-signed. The release build disables UPX compression and includes Windows version metadata to reduce heuristic false positives, but a trusted publisher signature is still required to remove the warning reliably. Release builds should be signed with an Authenticode certificate before distribution.

To sign a release automatically, set `AETHERION_CERTIFICATE` to the certificate file before running `python build_client.py`. Set `AETHERION_SIGNTOOL` when `signtool.exe` is not on `PATH`; use `AETHERION_CERTIFICATE_PASSWORD` only as a temporary environment variable when the certificate requires a password. Never commit certificate files or passwords.

### Run without Ollama

Ollama is optional. Install the GGUF runtime extra with `python -m pip install -e ".[llama]"`, then place `.gguf` models in `%LOCALAPPDATA%\Aetherion\results\models`. The desktop client discovers Ollama and GGUF models together and uses the available local runtime. GPU acceleration depends on the installed `llama-cpp-python` build; CPU execution remains available as a fallback.

The desktop client also lets users choose a custom GGUF folder. After selecting a model, it reports whether the current machine can run it directly, whether it will use GPU or CPU fallback, and which runtime dependency is missing when direct execution is unavailable.

### 1) Create and activate a virtual environment

#### Windows PowerShell

```powershell
cd path\to\local-ai-benchmark
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
cd path/to/local-ai-benchmark
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install the project

```bash
python -m pip install -e ".[dev,system]"
```

### 3) Check the hardware profile

```bash
python -m local_ai_benchmark system
```

### 4) Discover installed models

```bash
python -m local_ai_benchmark discover
```

### 5) Run a benchmark

```bash
python -m local_ai_benchmark run --model qwen3:4b
python -m local_ai_benchmark run --category math --model qwen3:4b
```

### 6) Start the local dashboard

```bash
python -m local_ai_benchmark dashboard --port 8765
```

Then open:

```text
http://127.0.0.1:8765
```

## CLI usage

```bash
python -m local_ai_benchmark --help
```

Available commands:

- `system`: show the detected hardware profile
- `discover`: list models available in Ollama
- `run`: execute the benchmark tasks for a selected model
- `dashboard`: start the local dashboard

## Ollama setup

If Ollama is installed locally, the expected runtime API is:

```text
http://127.0.0.1:11434
```

Typical checks:

```powershell
ollama list
ollama serve
curl http://127.0.0.1:11434/api/tags
```

If the Ollama application is already running, do not start a second `ollama serve` process.

## Troubleshooting

### `local-ai` is not recognized

Use the module entrypoint instead:

```bash
python -m local_ai_benchmark --help
```

This is more reliable in Windows terminals, VS Code terminals, and fresh virtual environments.

### Ollama is not reachable

Check that the local service is running and that the API is available at `http://127.0.0.1:11434`.

### No GPU telemetry appears

This can happen if:

- `nvidia-smi` is not available,
- the machine does not expose the field,
- or the platform does not provide GPU telemetry.

Missing telemetry is reported as `null`, never invented.

## Privacy and data handling

- Prompts and responses are sent only to the configured local provider.
- No cloud API calls are made by this project.
- No telemetry or automatic uploads are included.
- Generated benchmark files may contain hardware details and model outputs, so review before sharing them.

The repository ignores benchmark output in Git to keep generated local data out of version control.

## Project structure

```text
local-ai-benchmark/
├── README.md
├── pyproject.toml
├── src/
│   └── local_ai_benchmark/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── engine.py
│       ├── hardware.py
│       ├── models.py
│       ├── providers.py
│       ├── tasks.py
│       ├── web.py
│       └── web/
├── tests/
├── results/
├── .gitignore
└── LICENSE
```

## Architecture

```text
CLI
  -> BenchmarkEngine
  -> OllamaProvider
  -> HardwareProfiler
  -> Task validation
  -> JSON results and dashboard
```

## Roadmap

1. MVP: local hardware profiling, model discovery, benchmark tasks, JSON output
2. Richer task scoring and model comparison
3. More validation categories and benchmarking rules
4. SQLite history and comparisons across runs
5. Improved reporting and dashboard UX

## License

This project is distributed under the MIT License.

## Contributing

Contributions are welcome. If you want to improve task design, hardware detection, or dashboard UX, open a pull request with a focused change set and a clear description.
