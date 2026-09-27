import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .engine import BenchmarkEngine
from .hardware import profile_hardware
from .providers import OllamaProvider, ProviderError


WEB_DIR = Path(__file__).with_name("web")


def _latest_results(results_dir: str) -> list[dict]:
    files = sorted(Path(results_dir).glob("**/*.json"), reverse=True)
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload.get("results", [])
        except (OSError, json.JSONDecodeError):
            continue
    return []


class DashboardHandler(BaseHTTPRequestHandler):
    provider: OllamaProvider
    results_dir: str

    def _send_json(self, payload: object, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path) -> None:
        if not path.is_file() or path.parent != WEB_DIR:
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "text/plain")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/system":
            self._send_json(profile_hardware().to_dict())
        elif route == "/api/models":
            try:
                self._send_json([model.to_dict() for model in self.provider.discover()])
            except ProviderError as exc:
                self._send_json({"error": str(exc)}, 503)
        elif route == "/api/results":
            self._send_json(_latest_results(self.results_dir))
        else:
            self._send_file(WEB_DIR / ("index.html" if route == "/" else route.lstrip("/")))

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/run":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            model = payload["model"]
            category = payload.get("category") or None
            results = BenchmarkEngine(self.provider, self.results_dir).run(model, category)
            self._send_json([result.to_dict() for result in results])
        except (KeyError, json.JSONDecodeError) as exc:
            self._send_json({"error": f"Invalid benchmark request: {exc}"}, 400)
        except ProviderError as exc:
            self._send_json({"error": str(exc)}, 503)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[dashboard] {format % args}")


def serve_dashboard(host: str = "127.0.0.1", port: int = 8765,
                    endpoint: str = "http://127.0.0.1:11434", results_dir: str = "results") -> None:
    handler = type("ConfiguredDashboardHandler", (DashboardHandler,), {
        "provider": OllamaProvider(endpoint), "results_dir": results_dir,
    })
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Local AI Benchmark dashboard: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()
