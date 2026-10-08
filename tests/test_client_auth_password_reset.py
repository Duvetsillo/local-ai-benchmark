import pytest

from local_ai_benchmark.client.auth import (
    AccountService,
    PasswordChangeRequired,
)


def test_login_surfaces_temporary_password_requirement(monkeypatch):
    service = AccountService("https://licenses.example")
    requests = []

    def request(method, path, payload=None, token=None):
        requests.append((method, path, payload, token))
        return {"password_change_required": True}

    monkeypatch.setattr(service, "_request", request)
    with pytest.raises(PasswordChangeRequired):
        service.login("test-user", "temporary-password", "A" * 32)

    assert requests == [
        (
            "POST",
            "/v1/auth/login",
            {
                "username": "test-user",
                "password": "temporary-password",
                "machine_id": "A" * 32,
            },
            None,
        )
    ]


def test_temporary_password_change_sends_only_supplied_credentials(monkeypatch):
    service = AccountService("https://licenses.example")
    requests = []

    def request(method, path, payload=None, token=None):
        requests.append((method, path, payload, token))
        return {"ok": True}

    monkeypatch.setattr(service, "_request", request)
    service.change_temporary_password(
        "test-user", "temporary-password", "replacement-password"
    )

    assert requests == [
        (
            "POST",
            "/v1/auth/change-temporary-password",
            {
                "username": "test-user",
                "temporary_password": "temporary-password",
                "new_password": "replacement-password",
            },
            None,
        )
    ]
