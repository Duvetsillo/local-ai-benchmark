import asyncio
import json
import datetime as dt
import hashlib

import pytest
from fastapi import HTTPException

from server import app as service


@pytest.fixture
def account(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "DB_PATH", tmp_path / "presence.sqlite3")
    monkeypatch.setattr(service, "OFFLINE_SIGNING_KEY_PATH", tmp_path / "signer.pem")
    service.init_db()
    now = service.utc_now()
    with service.db() as connection:
        connection.execute(
            "INSERT INTO licenses(license_id,key_hash,machine_id,plan,issued_at,created_at) VALUES(?,?,?,?,?,?)",
            ("a" * 32, "b" * 64, "C" * 32, "unlimited", service.iso(now), service.iso(now)),
        )
        connection.execute(
            "INSERT INTO users(username,username_norm,password_hash,license_id,created_at) VALUES(?,?,?,?,?)",
            ("demo-user", "demo-user", service.password_hasher.hash("demo-password-123"), "a" * 32, service.iso(now)),
        )
    return now


def add_session(now, seen=None, revoked=None, expires=None):
    token = "fixture-session-token-" + "x" * 32
    with service.db() as connection:
        connection.execute(
            "INSERT INTO sessions(token_hash,user_id,created_at,expires_at,last_seen_at,revoked_at) VALUES(?,?,?,?,?,?)",
            (hashlib.sha256(token.encode()).hexdigest(), 1, service.iso(now),
             service.iso(expires or now + dt.timedelta(days=1)), service.iso(seen), service.iso(revoked)),
        )
    return token


@pytest.mark.parametrize("offset,online", [(0, True), (-359, True), (-361, False), (60, False)])
def test_presence_requires_recent_nonfuture_contact(account, offset, online, monkeypatch):
    monkeypatch.setattr(service, "utc_now", lambda: account)
    add_session(account, account + dt.timedelta(seconds=offset))
    result = service.list_users()
    assert result["users"][0]["online"] is online
    assert result["presence_window_seconds"] == 360
    assert "token_hash" not in result["users"][0]


def test_old_session_and_recent_login_do_not_prove_presence(account):
    add_session(account)
    with service.db() as connection:
        connection.execute("UPDATE users SET last_login_at=?", (service.iso(account),))
    assert service.list_users()["users"][0]["online"] is False


@pytest.mark.parametrize("state", ["revoked", "expired", "disabled", "license-disabled", "license-expired", "password-change"])
def test_invalid_access_is_offline(account, state):
    add_session(account, account,
                revoked=account if state == "revoked" else None,
                expires=account - dt.timedelta(seconds=1) if state == "expired" else None)
    with service.db() as connection:
        if state == "disabled":
            connection.execute("UPDATE users SET active=0")
        elif state == "license-disabled":
            connection.execute("UPDATE licenses SET enabled=0")
        elif state == "license-expired":
            connection.execute("UPDATE licenses SET expires_at=?", (service.iso(account - dt.timedelta(seconds=1)),))
        elif state == "password-change":
            connection.execute("UPDATE users SET password_change_required=1")
    assert service.list_users()["users"][0]["online"] is False


def test_authenticated_contact_updates_presence_and_logout_clears_it(account):
    token = add_session(account)
    assert service.list_users()["users"][0]["online"] is False
    service.get_session("Bearer " + token)
    assert service.list_users()["users"][0]["online"] is True
    service.logout("Bearer " + token)
    assert service.list_users()["users"][0]["online"] is False
    with pytest.raises(HTTPException):
        service.get_session("Bearer " + token)


def test_successful_login_records_presence(account):
    service.login(service.LoginRequest(username="demo-user", password="demo-password-123", machine_id="c" * 32), None)
    assert service.list_users()["users"][0]["online"] is True


def test_migration_is_repeatable(account):
    with service.db() as connection:
        connection.execute("ALTER TABLE sessions DROP COLUMN last_seen_at")
    service.init_db()
    service.init_db()
    assert service.list_users()["users"][0]["last_seen_at"] is None


def http_request(method, path, token=None, body=None):
    async def send_request():
        response = []
        headers = [(b"content-type", b"application/json")]
        if token:
            headers.append((b"authorization", ("Bearer " + token).encode()))
        scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
                 "method": method, "scheme": "http", "path": path, "raw_path": path.encode(),
                 "query_string": b"", "root_path": "", "headers": headers,
                 "client": ("127.0.0.1", 12345), "server": ("fixture", 80)}
        async def receive():
            return {"type": "http.request", "body": json.dumps(body).encode() if body else b"", "more_body": False}
        async def send(message):
            response.append(message)
        await service.app(scope, receive, send)
        status = next(item["status"] for item in response if item["type"] == "http.response.start")
        data = b"".join(item.get("body", b"") for item in response if item["type"] == "http.response.body")
        return status, json.loads(data)
    return asyncio.run(send_request())


def test_http_presence_is_admin_only_and_plan_change_preserves_account(account, monkeypatch):
    monkeypatch.setattr(service, "ADMIN_TOKEN", "fixture-admin-" + "x" * 40)
    token = add_session(account)
    assert http_request("GET", "/v1/admin/users")[0] == 401
    assert http_request("GET", "/v1/admin/users", token)[0] == 401
    assert http_request("GET", "/v1/auth/me", token)[0] == 200
    status, result = http_request("GET", "/v1/admin/users", service.ADMIN_TOKEN)
    assert status == 200
    before = result["users"][0]
    assert before["online"] is True
    assert not {"password_hash", "token_hash", "session_token", "admin_token"}.intersection(before)
    changed, _ = http_request("PATCH", "/v1/admin/users/1/plan", service.ADMIN_TOKEN, {"plan": "duration", "days": 45})
    assert changed == 200
    _, result = http_request("GET", "/v1/admin/users", service.ADMIN_TOKEN)
    after = result["users"][0]
    assert after["id"] == before["id"]
    assert after["license_id"] == before["license_id"]
    assert after["plan"] == "duration"
    assert after["active"] is before["active"]
