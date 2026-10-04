import datetime as dt
import json
import threading
import uuid
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from local_ai_benchmark import integration as api
from local_ai_benchmark.models import HardwareProfile, ModelInfo
from local_ai_benchmark.providers import Generation, ProviderCancelled, ProviderError


class Gate:
    allowed = True
    def require(self, force=False):
        if not self.allowed:
            raise api.APIError(403, "license_required", "license missing")


class Provider:
    name = "ollama"
    calls = 0
    def discover(self):
        return [ModelInfo("installed", "ollama")]
    def generate(self, model, prompt, temperature, context, stop_event=None):
        self.calls += 1
        return Generation("888", 0.01, 0.1, {"eval_count": 1})


class BlockingProvider(Provider):
    entered = None
    def __init__(self):
        self.entered = threading.Event()
    def generate(self, *args, stop_event=None, **kwargs):
        self.calls += 1
        self.entered.set()
        assert stop_event.wait(5), "test did not cancel its worker"
        raise ProviderCancelled("cancelled")


@pytest.fixture(autouse=True)
def no_real_hardware(monkeypatch):
    monkeypatch.setattr("local_ai_benchmark.engine.profile_hardware", lambda: HardwareProfile("test", "test", {}, {}, []))
    monkeypatch.setattr("local_ai_benchmark.engine._resource_snapshot", lambda: {"cpu_percent": None, "ram_used_bytes": None})


def payload(**changes):
    body = dict(request_id=str(uuid.uuid4()), node="pc", model="installed", category="math", confirm=True)
    body.update(changes)
    return body


@pytest.fixture
def http_api(tmp_path):
    provider = BlockingProvider()
    jobs = api.BenchmarkJobs({"pc": provider}, tmp_path, Gate())
    token = "t" * 40
    server = api.create_server(jobs, token, 0)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    def request(method, path, body=None, auth=True, host=None):
        headers = {"Content-Type": "application/json"}
        if auth:
            headers["Authorization"] = "Bearer " + token
        if host:
            headers["Host"] = host
        req = Request(f"http://127.0.0.1:{server.server_port}" + path,
                      data=json.dumps(body).encode() if body is not None else None, headers=headers, method=method)
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())
    yield jobs, provider, request
    jobs.close()
    server.shutdown()
    server.server_close()
    thread.join(5)


def test_http_authorization_and_license_are_both_required(http_api):
    jobs, provider, request = http_api
    assert request("GET", "/v1/nodes", auth=False)[0] == 401
    jobs.gate.allowed = False
    status, response = request("POST", "/v1/benchmarks", payload())
    assert status == 403 and response["error"]["code"] == "license_required"
    assert provider.calls == 0
    assert request("GET", "/v1/models?node=pc")[0] == 403


def test_http_catalog_is_explicit_and_protected_against_rebinding(http_api):
    jobs, provider, request = http_api
    assert request("GET", "/v1/nodes")[1]["nodes"] == [{"id": "pc", "provider": "ollama"}]
    assert request("GET", "/v1/models?node=pc")[1]["models"][0]["name"] == "installed"
    assert request("GET", "/v1/models?node=other")[0] == 404
    assert request("GET", "/v1/models?node=pc&node=other")[0] == 400
    assert request("GET", "/v1/nodes", host="untrusted.example")[0] == 400
    assert provider.calls == 0


def test_http_idempotency_busy_and_cancel_after_license_loss(http_api):
    jobs, provider, request = http_api
    body = payload()
    status, job = request("POST", "/v1/benchmarks", body)
    assert status == 202
    assert provider.entered.wait(3)
    assert request("POST", "/v1/benchmarks", body)[1]["id"] == job["id"]
    assert request("POST", "/v1/benchmarks", {**body, "context": 2048})[1]["error"]["code"] == "request_id_conflict"
    assert request("POST", "/v1/benchmarks", payload())[1]["error"]["code"] == "busy"
    assert request("GET", f'/v1/benchmarks/{job["id"]}')[1]["total"] == 1
    jobs.gate.allowed = False
    assert request("GET", f'/v1/benchmarks/{job["id"]}/results')[0] == 403
    assert request("POST", f'/v1/benchmarks/{job["id"]}/cancel')[0] == 200
    jobs.thread.join(3)
    assert jobs.get(job["id"])["status"] == "stopped"
    assert jobs.results(job["id"])["results"] == []
    assert provider.calls == 1
    assert request("POST", f'/v1/benchmarks/{job["id"]}/cancel')[0] == 200


def test_engine_results_persist_and_retry_does_not_generate_again(tmp_path):
    provider = Provider()
    jobs = api.BenchmarkJobs({"pc": provider}, tmp_path, Gate())
    body = payload()
    status, snapshot = jobs.start(body)
    jobs.thread.join(3)
    assert not jobs.thread.is_alive()
    job = jobs.get(snapshot["id"])
    assert job["status"] == "completed" and job["completed"] == 1
    results = jobs.results(job["id"])["results"]
    assert results[0]["passed"] is True and results[0]["response"] == "888"
    path = tmp_path / "integration" / job["id"] / "job.json"
    assert json.loads(path.read_text())["results"] == results
    # Original engine file is separate from the API job envelope.
    assert list(path.parent.glob("*/run-*.json"))
    assert jobs.start(body)[0] == 200 and provider.calls == 1
    jobs.close()


@pytest.mark.parametrize("change", [
    {"confirm": False}, {"confirm": "true"}, {"category": None}, {"category": "all"},
    {"request_id": "not-uuid"}, {"context": True}, {"context": 9000},
    {"temperature": float("nan")}, {"max_seconds": 500}, {"endpoint": "http://private-service"},
])
def test_invalid_requests_never_run(change, tmp_path):
    provider = Provider()
    jobs = api.BenchmarkJobs({"pc": provider}, tmp_path, Gate())
    with pytest.raises(api.APIError) as caught:
        jobs.start(payload(**change))
    assert caught.value.status == 400 and provider.calls == 0


def test_absent_model_and_invalid_catalog_never_generate(tmp_path):
    provider = Provider()
    jobs = api.BenchmarkJobs({"pc": provider}, tmp_path, Gate())
    with pytest.raises(api.APIError, match="installed"):
        jobs.start(payload(model="download-me"))
    provider.discover = lambda: (_ for _ in ()).throw(ProviderError("bad response"))
    with pytest.raises(api.APIError) as caught:
        jobs.models("pc")
    assert caught.value.status == 503 and provider.calls == 0


def test_license_gate_reuses_existing_session_and_checks_expiry(tmp_path, monkeypatch):
    cache = tmp_path / "cache.bin"
    cache.write_bytes(b"test")
    monkeypatch.setattr(api, "_cache_path", lambda: cache)
    monkeypatch.setattr(api, "machine_fingerprint", lambda: "test-machine")
    gate = api.LicenseGate()
    session = SimpleNamespace(offline_until=dt.datetime.now(dt.UTC) + dt.timedelta(minutes=1))
    calls = []
    gate.service = SimpleNamespace(restore_cached=lambda machine: calls.append(machine) or session)
    assert gate.require() is session
    gate.require()
    assert calls == ["test-machine"]
    gate.require(force=True)
    assert len(calls) == 2
    session.offline_until = dt.datetime.now(dt.UTC) - dt.timedelta(seconds=1)
    with pytest.raises(api.APIError):
        gate.require()
    cache.unlink()
    gate.service = SimpleNamespace(restore_cached=lambda machine: None)
    with pytest.raises(api.APIError):
        gate.require()


def test_token_provisioning_never_rotates_existing_secret(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "token_path", lambda: tmp_path / "paired.bin")
    monkeypatch.setattr(api, "_dpapi", lambda data, decrypt=False: data)
    first = api.provision_token()
    assert len(first) >= 32 and api.provision_token() == first and api.load_integration_token() == first


@pytest.mark.parametrize("url", ["https://user:password@host", "file:///path", "http://host/path", "http://host?x=1"])
def test_node_endpoint_credentials_paths_and_queries_are_rejected(url):
    with pytest.raises(ValueError):
        api.validate_node_url(url)
