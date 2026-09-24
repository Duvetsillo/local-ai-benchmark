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

## MVP

```powershell
py -m pip install -e ".[dev,system]"
local-ai system
local-ai discover
local-ai run --model qwen3:4b
local-ai run --category math --model qwen3:4b
```

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
endpoint. Results are
written below `results/YYYY-MM-DD/` and contain the system profile, request
configuration, raw provider usage when available, and measured metrics.

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
