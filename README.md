# Local AI Benchmark

Local AI Benchmark answers a practical question with measured data:

> Which of my local models fits my hardware and my workload best?

It is deliberately not a chatbot or an Ollama frontend. The first MVP is a
CLI that profiles the machine, discovers installed Ollama models, runs a small
deterministic task suite, and stores reproducible JSON results.

## Research and differentiation

| Existing solution | What it does well | Boundary this project targets |
| --- | --- | --- |
| `llama.cpp` / `llama-bench` | Runtime throughput and backend benchmarking | Does not choose among a user's installed models by workload |
| `LLMPerf` | API load and latency testing | Archived; primarily API/load focused, not local hardware recommendations |
| `lm-evaluation-harness` | Large academic task and quality evaluation suite | Broad evaluation framework, not a lightweight local resource-aware decision tool |
| Ollama / LM Studio | Local inference and model management | Providers, not an evidence-based personal model selector |

Our differentiator is the join between a captured system profile, provider
telemetry, deterministic task validators, and recommendations constrained by
the measured machine. Unsupported telemetry is represented as `null`, never
invented.

## Install for everyone

Requires Python 3.11 or newer and a local Ollama installation. The benchmark
itself is cross-platform; NVIDIA telemetry is optional and currently uses
`nvidia-smi` when available. No GPU is required to run the tests.

### Windows PowerShell

```powershell
git clone https://github.com/YOUR_USER/local-ai-benchmark.git
cd local-ai-benchmark
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e ".[system]"
```

### Linux or macOS

```bash
git clone https://github.com/YOUR_USER/local-ai-benchmark.git
cd local-ai-benchmark
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[system]"
```

The `system` extra enables RAM/CPU telemetry through `psutil`. Without it,
the benchmark still runs and reports unavailable resource fields as `null`.
## MVP

```powershell
py -m pip install -e ".[dev,system]"
local-ai system
local-ai discover
local-ai run --model qwen3:4b
local-ai run --category math --model qwen3:4b
local-ai discover
local-ai run --model qwen3:4b
local-ai run --category math --model qwen3:4b
local-ai dashboard --port 8765

Open `http://127.0.0.1:8765` for the local dashboard. For development and CI,
install `.[dev,system]` to include pytest.
On Windows, Ollama's application and `ollama.exe` use a local API at
`http://127.0.0.1:11434`; this is the local Ollama instance, not a cloud
server. Start or test it from PowerShell:

```powershell
ollama list
ollama serve
curl http://127.0.0.1:11434/api/tags
```

If the Ollama Windows application is already running, do not start a second
`ollama serve` process. The API must be available at that endpoint for
discovery and benchmark runs. Use `--endpoint` to point at another local
endpoint. Results are written below `results/YYYY-MM-DD/` and contain the
system profile, request configuration, raw provider usage when available, and
measured metrics.

## Privacy and publishing results

Prompts and responses are sent only to the configured local provider. The
project has no telemetry, analytics, cloud API calls, or automatic uploads.
Generated benchmark files are ignored by Git because they can contain system
hardware details and model responses. Share a result only after reviewing and
anonymizing it yourself.

## Support matrix

| Capability | Windows | Linux | macOS |
| --- | --- | --- | --- |
| CLI and tests | Yes | Yes | Yes |
| Ollama provider | Yes | Yes | Yes |
| CPU/RAM metrics | With `psutil` | With `psutil` | With `psutil` |
| NVIDIA metrics | With `nvidia-smi` | With `nvidia-smi` | Usually unavailable |
| AMD/Intel GPU metrics | Not yet | Not yet | Not yet |

Hardware fields that the operating system or provider cannot expose are
reported as `null`, never estimated.

## Architecture

```text
CLI -> BenchmarkEngine -> ProviderAdapter (Ollama today)
                    -> HardwareProfiler
                    -> TaskSuite + validators
                    -> JSON Storage
```

The provider interface is intentionally small so llama.cpp and OpenAI-compatible
local servers can be added without coupling the engine to Ollama.

## Offline and privacy

The MVP makes no cloud requests and sends prompts only to the configured local
provider. `--offline` rejects non-loopback endpoints. No telemetry or
analytics are included.

## Roadmap

1. MVP: hardware, Ollama discovery, controlled generation, metrics, JSON, CLI.
2. Task scoring, comparison, and hardware-aware recommendations.
3. Custom tasks, SQLite history, regression detection, Markdown/HTML reports.
4. llama.cpp and OpenAI-compatible adapters, then a local dashboard.
