"""Licensed loopback API for explicit external benchmark actions.

The transport never accepts an endpoint or executable from its caller. Computation,
scoring, cancellation and persisted measurements belong to BenchmarkEngine.
"""
from __future__ import annotations

import copy
import datetime as dt
import hmac
import json
import math
import os
import re
import secrets
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from .client.auth import AccountService, AuthError, _cache_path, _dpapi, machine_fingerprint
from .engine import BenchmarkEngine
from .providers import OllamaProvider, ProviderError
from .tasks import TASKS, tasks_for

MAX_BODY = 16 * 1024
TERMINAL = {"completed", "stopped", "failed"}


def data_root() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Aetherion"


def token_path() -> Path:
    return data_root() / "integration-token.bin"


def load_integration_token() -> str:
    """Read the local credential in-process; callers must never log its value."""
    token = _dpapi(token_path().read_bytes(), decrypt=True).decode("ascii")
    if len(token) < 32:
        raise ValueError("Invalid integration credential")
    return token


def provision_token() -> str:
    if token_path().exists():
        return load_integration_token()
    token = secrets.token_urlsafe(32)
    path = token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents two launches from changing the caller's secret.
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return load_integration_token()
    with os.fdopen(fd, "wb") as output:
        output.write(_dpapi(token.encode("ascii")))
    return token


class APIError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code = status, code


class LicenseGate:
    """Same cache and account checks as Studio; no new account or bypass mode."""
    def __init__(self):
        self.service = AccountService()
        self.session = None
        self.checked = 0.0
        self.lock = threading.Lock()

    def require(self, force: bool = False):
        with self.lock:
            if not _cache_path().exists():
                self.session = None
            if force or self.session is None or time.monotonic() - self.checked >= 300:
                try:
                    self.session = self.service.restore_cached(machine_fingerprint())
                except (AuthError, OSError, ValueError):
                    self.session = None
                self.checked = time.monotonic()
            if self.session is None or dt.datetime.now(dt.UTC) >= self.session.offline_until:
                raise APIError(403, "license_required", "Inicia sesión en Aetherion Studio en esta PC para autorizar la integración.")
            return self.session


def validate_node_url(value: str) -> str:
    parts = urlparse(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment or parts.path not in {"", "/"}:
        raise ValueError("Node must be an HTTP(S) base URL without credentials, path or query")
    return value.rstrip("/")


def validate_request(body: object) -> dict:
    if not isinstance(body, dict):
        raise APIError(400, "invalid_request", "Expected a JSON object")
    allowed = {"request_id", "node", "model", "category", "temperature", "context", "max_seconds", "confirm"}
    if set(body) - allowed or body.get("confirm") is not True:
        raise APIError(400, "invalid_request", "Only supported fields and explicit confirm=true are accepted")
    try:
        request_id = str(uuid.UUID(body["request_id"]))
    except (KeyError, ValueError, TypeError, AttributeError):
        raise APIError(400, "invalid_request", "request_id must be a UUID") from None
    if not isinstance(body.get("node"), str) or not isinstance(body.get("model"), str) or not 1 <= len(body["model"]) <= 256:
        raise APIError(400, "invalid_request", "node and installed model are required")
    if body.get("category") not in {task.category for task in TASKS}:
        raise APIError(400, "invalid_request", "An explicit supported category is required")
    temperature = body.get("temperature", 0.0)
    context = body.get("context", 4096)
    max_seconds = body.get("max_seconds", 180)
    if type(temperature) not in {int, float} or not math.isfinite(temperature) or not 0 <= temperature <= 2:
        raise APIError(400, "invalid_request", "temperature must be finite and between 0 and 2")
    if type(context) is not int or not 256 <= context <= 8192:
        raise APIError(400, "invalid_request", "context must be an integer between 256 and 8192")
    if type(max_seconds) is not int or not 10 <= max_seconds <= 300:
        raise APIError(400, "invalid_request", "max_seconds must be an integer between 10 and 300")
    return dict(request_id=request_id, node=body["node"], model=body["model"], category=body["category"],
                temperature=float(temperature), context=context, max_seconds=max_seconds, confirm=True)


class BenchmarkJobs:
    def __init__(self, nodes: dict[str, object], results_dir: Path, gate=None, engine_factory=BenchmarkEngine):
        self.nodes, self.results_dir = nodes, Path(results_dir)
        self.gate = gate or LicenseGate()
        self.engine_factory = engine_factory
        self.lock = threading.RLock()
        self.jobs: dict[str, dict] = {}
        self.thread: threading.Thread | None = None
        self.closing = False

    def models(self, node: str) -> dict:
        if node not in self.nodes:
            raise APIError(404, "unknown_node", "Node is not configured")
        try:
            models = [model.to_dict() for model in self.nodes[node].discover()]
            if any(not isinstance(m.get("name"), str) for m in models):
                raise ValueError("Invalid catalog")
            return {"node": node, "models": models}
        except (ProviderError, ValueError, TypeError, AttributeError, KeyError):
            raise APIError(503, "provider_unavailable", "Ollama did not provide a valid model catalog") from None

    def _snapshot(self, job: dict) -> dict:
        return {key: copy.deepcopy(value) for key, value in job.items() if not key.startswith("_")}

    def get(self, job_id: str) -> dict:
        with self.lock:
            if job_id not in self.jobs:
                raise APIError(404, "not_found", "Benchmark job not found in this instance")
            return self._snapshot(self.jobs[job_id])

    def results(self, job_id: str) -> dict:
        with self.lock:
            snapshot = self.get(job_id)
            return {"id": job_id, "status": snapshot["status"], "hardware_scope": "api_host",
                    "results": copy.deepcopy(self.jobs[job_id]["_results"])}

    def _duplicate(self, request: dict) -> dict | None:
        for job in self.jobs.values():
            if job["request_id"] == request["request_id"]:
                if job["_request"] != request:
                    raise APIError(409, "request_id_conflict", "request_id already belongs to a different request")
                return self._snapshot(job)
        return None

    def start(self, body: object) -> tuple[int, dict]:
        request = validate_request(body)
        self.gate.require(force=True)
        with self.lock:
            duplicate = self._duplicate(request)
            if duplicate:
                return 200, duplicate
        catalog = self.models(request["node"])
        if request["model"] not in {m["name"] for m in catalog["models"]}:
            raise APIError(400, "model_not_installed", "Choose a model installed on the selected node")
        with self.lock:
            duplicate = self._duplicate(request)
            if duplicate:
                return 200, duplicate
            if self.closing or any(j["status"] not in TERMINAL for j in self.jobs.values()):
                raise APIError(409, "busy", "This API already has an active benchmark or is shutting down")
            if len(self.jobs) >= 100:
                # Do not evict idempotency keys and accidentally rerun an old request.
                raise APIError(409, "busy", "Instance reached 100 jobs; restart after saving result IDs")
            job_id = str(uuid.uuid4())
            job = {"id": job_id, "request_id": request["request_id"], "node": request["node"],
                   "model": request["model"], "category": request["category"], "status": "queued",
                   "completed": 0, "total": len(tasks_for(request["category"])), "cancel_requested": False,
                   "stop_reason": None, "created_at": dt.datetime.now(dt.UTC).isoformat(), "finished_at": None,
                   "error": None, "result_url": f"/v1/benchmarks/{job_id}/results", "hardware_scope": "api_host",
                   "_request": request, "_stop": threading.Event(), "_results": []}
            self.jobs[job_id] = job
            self.thread = threading.Thread(target=self._run, args=(job_id,), name="aetherion-benchmark")
            self.thread.start()
            return 202, self._snapshot(job)

    def cancel(self, job_id: str, reason: str = "user") -> dict:
        with self.lock:
            self.get(job_id)
            job = self.jobs[job_id]
            if job["status"] not in TERMINAL:
                job["cancel_requested"] = True
                job["stop_reason"] = job["stop_reason"] or reason
                job["status"] = "stopping"
                job["_stop"].set()
            return self._snapshot(job)

    def _run(self, job_id: str):
        with self.lock:
            job = self.jobs[job_id]
            request = job["_request"]
            if job["status"] != "stopping":
                job["status"] = "running"
        timer = threading.Timer(request["max_seconds"], lambda: self.cancel(job_id, "deadline"))
        timer.daemon = True
        timer.start()
        def progress(index, total, result):
            with self.lock:
                job["completed"] = index
                job["_results"].append(result.to_dict())
            try:
                self.gate.require()
            except APIError:
                self.cancel(job_id, "authorization")
        try:
            self.gate.require()
            engine = self.engine_factory(self.nodes[request["node"]], self.results_dir / "integration" / job_id)
            results = engine.run(request["model"], request["category"], request["temperature"], request["context"],
                                 progress_callback=progress, stop_event=job["_stop"])
            with self.lock:
                job["_results"] = [item.to_dict() for item in results]
                job["completed"] = len(results)
                job["status"] = "stopped" if engine.last_run_stopped or job["_stop"].is_set() else "completed"
        except APIError:
            with self.lock:
                job["status"], job["error"] = "failed", "Authorization is no longer valid"
        except Exception:
            with self.lock:
                job["status"], job["error"] = "failed", "Benchmark could not complete; inspect local API diagnostics"
        finally:
            timer.cancel()
            with self.lock:
                job["finished_at"] = dt.datetime.now(dt.UTC).isoformat()
                snapshot = self._snapshot(job)
                snapshot["results"] = copy.deepcopy(job["_results"])
            # Persist even an empty stopped job; engine retains completed task JSON.
            try:
                directory = self.results_dir / "integration" / job_id
                directory.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, delete=False) as out:
                    json.dump(snapshot, out, ensure_ascii=False, indent=2)
                    out.flush()
                    os.fsync(out.fileno())
                    temporary = out.name
                os.replace(temporary, directory / "job.json")
            except OSError:
                with self.lock:
                    job["status"], job["error"] = "failed", "Result persistence failed"

    def close(self):
        with self.lock:
            self.closing = True
            for job_id in self.jobs:
                self.cancel(job_id, "shutdown")
            thread = self.thread
        if thread is not None:
            thread.join()


class IntegrationHandler(BaseHTTPRequestHandler):
    token: str
    jobs: BenchmarkJobs

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def _json(self, status: int, body: object):
        encoded = json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        self.close_connection = True

    def _handle(self):
        if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
            raise APIError(400, "invalid_request", "Use the configured loopback address")
        if not hmac.compare_digest(self.headers.get("Authorization", "").encode(), ("Bearer " + self.token).encode()):
            raise APIError(401, "unauthorized", "Integration credential required")
        if self.headers.get("Origin"):
            raise APIError(403, "unauthorized", "Browser origins are not supported")
        url = urlparse(self.path)
        match = re.fullmatch(r"/v1/benchmarks/([0-9a-f-]{36})(/results|/cancel)?", url.path)
        # Cancellation grants no computation: allow a paired client to stop a job
        # even if its account has expired or signed out in the meantime.
        if match and match[2] == "/cancel" and self.command == "POST":
            return 200, self.jobs.cancel(match[1])
        self.jobs.gate.require()
        if self.command == "GET":
            if url.path == "/v1/nodes":
                return 200, {"nodes": [{"id": n, "provider": "ollama"} for n in self.jobs.nodes],
                             "categories": list(dict.fromkeys(t.category for t in TASKS))}
            if url.path == "/v1/models":
                query = parse_qs(url.query)
                if set(query) - {"node"} or len(query.get("node", [])) != 1:
                    raise APIError(400, "invalid_request", "One node query parameter is required")
                return 200, self.jobs.models(query["node"][0])
            if match and match[2] in {None, "/results"}:
                return 200, self.jobs.results(match[1]) if match[2] else self.jobs.get(match[1])
        elif self.command == "POST" and url.path == "/v1/benchmarks":
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json" or self.headers.get("Transfer-Encoding"):
                raise APIError(400, "invalid_request", "Send a bounded application/json body")
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length > MAX_BODY:
                    raise APIError(413, "payload_too_large", "Maximum request size is 16 KiB")
                if length <= 0:
                    raise ValueError()
                body = json.loads(self.rfile.read(length))
            except (ValueError, UnicodeDecodeError):
                raise APIError(400, "invalid_request", "Invalid JSON body") from None
            return self.jobs.start(body)
        raise APIError(404, "not_found", "Route not found")

    def do_GET(self):
        try:
            status, body = self._handle()
        except APIError as exc:
            status, body = exc.status, {"error": {"code": exc.code, "message": str(exc)}}
        except Exception:
            status, body = 500, {"error": {"code": "internal_error", "message": "API request failed"}}
        self._json(status, body)

    do_POST = do_GET

    def log_message(self, format, *args):
        # Never log URLs/query strings, headers, license cache or model outputs.
        pass


def create_server(jobs: BenchmarkJobs, token: str, port: int = 8766) -> ThreadingHTTPServer:
    if len(token) < 32:
        raise ValueError("Integration token must have at least 32 characters")
    handler = type("ConfiguredIntegrationHandler", (IntegrationHandler,), {"jobs": jobs, "token": token})
    return ThreadingHTTPServer(("127.0.0.1", port), handler)


def serve_integration(port: int = 8766, node_specs: list[str] | None = None, results_dir: str | None = None):
    nodes = {"pc": OllamaProvider(timeout=30)}
    for spec in node_specs or []:
        name, separator, endpoint = spec.partition("=")
        if not separator or not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", name) or name in nodes:
            raise ValueError("Use unique --node name=http://host:port entries")
        nodes[name] = OllamaProvider(validate_node_url(endpoint), timeout=30)
    jobs = BenchmarkJobs(nodes, Path(results_dir) if results_dir else data_root() / "results")
    server = create_server(jobs, provision_token(), port)
    print(f"Aetherion integration API: http://127.0.0.1:{server.server_port} (licensed; no jobs started)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping active benchmark cooperatively…")
    finally:
        server.server_close()
        jobs.close()


class IntegrationClient:
    """Optional thin client for Karen; owns no benchmark logic or account login."""
    def __init__(self, base_url: str = "http://127.0.0.1:8766", token: str | None = None):
        parts = urlparse(base_url)
        if parts.scheme != "http" or parts.hostname != "127.0.0.1" or parts.username or parts.password or parts.path not in {"", "/"} or parts.query or parts.fragment:
            raise ValueError("Integration client only permits the loopback API")
        self.base_url = base_url.rstrip("/")
        self.token = token or load_integration_token()

    def request(self, method: str, path: str, payload: dict | None = None):
        if not path.startswith("/v1/") or "\r" in path or "\n" in path:
            raise ValueError("Invalid integration route")
        body = json.dumps(payload, allow_nan=False).encode() if payload is not None else None
        request = Request(self.base_url + path, data=body, method=method,
                          headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json"})
        with urlopen(request, timeout=45) as response:
            return json.loads(response.read())
