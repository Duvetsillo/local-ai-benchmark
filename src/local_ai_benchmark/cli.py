import argparse
import json

from .engine import BenchmarkEngine
from .hardware import profile_hardware
from .providers import OllamaProvider, ProviderError
from .web import serve_dashboard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="local-ai", description="Benchmark local AI models on your hardware")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("system", help="show detected hardware")
    discover = subparsers.add_parser("discover", help="list models installed in Ollama")
    discover.add_argument("--endpoint", default="http://127.0.0.1:11434")
    run = subparsers.add_parser("run", help="run the deterministic MVP task suite")
    run.add_argument("--model", required=True)
    run.add_argument("--category")
    run.add_argument("--endpoint", default="http://127.0.0.1:11434")
    run.add_argument("--results-dir", default="results")
    run.add_argument("--offline", action="store_true", help="allow only loopback provider endpoints")
    dashboard = subparsers.add_parser("dashboard", help="start the local web dashboard")
    dashboard.add_argument("--host", default="127.0.0.1")
    dashboard.add_argument("--port", type=int, default=8765)
    dashboard.add_argument("--endpoint", default="http://127.0.0.1:11434")
    dashboard.add_argument("--results-dir", default="results")
    integration = subparsers.add_parser("integration-api", help="start the licensed loopback API for external clients")
    integration.add_argument("--port", type=int, default=8766)
    integration.add_argument("--node", action="append", default=[], help="explicit additional Ollama node: name=http://host:11434")
    integration.add_argument("--results-dir", default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "integration-api":
        from .integration import serve_integration
        serve_integration(args.port, args.node, args.results_dir)
        return
    if args.command == "system":
        print(json.dumps(profile_hardware().to_dict(), indent=2, ensure_ascii=False))
        return
    if args.command == "dashboard":
        serve_dashboard(args.host, args.port, args.endpoint, args.results_dir)
        return
    provider = OllamaProvider(args.endpoint)
    if args.command == "discover":
        try:
            print(json.dumps([model.to_dict() for model in provider.discover()], indent=2, ensure_ascii=False))
        except ProviderError as exc:
            raise SystemExit(
                f"{exc}\nStart Ollama for Windows or run 'ollama serve' in PowerShell, "
                "then retry."
            ) from exc
        return
    if args.offline and not any(host in provider.endpoint for host in ("127.0.0.1", "localhost", "::1")):
        raise SystemExit("--offline only permits loopback provider endpoints")
    results = BenchmarkEngine(provider, args.results_dir).run(args.model, args.category)
    print(json.dumps([result.to_dict() for result in results], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
