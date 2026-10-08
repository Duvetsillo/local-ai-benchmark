import datetime as dt
import hashlib
import sqlite3

import pytest
from fastapi import HTTPException

from server import app as license_service


@pytest.fixture
def seeded_user(tmp_path, monkeypatch):
    monkeypatch.setattr(license_service, "DB_PATH", tmp_path / "license.sqlite3")
    monkeypatch.setattr(
        license_service, "OFFLINE_SIGNING_KEY_PATH", tmp_path / "offline-signing.pem"
    )
    license_service.init_db()
    now = license_service.utc_now()
    with license_service.db() as connection:
        connection.execute(
            """
            INSERT INTO licenses(license_id,key_hash,machine_id,plan,issued_at,expires_at,created_at)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                "a" * 32,
                "b" * 64,
                "C" * 32,
                "duration",
                license_service.iso(now),
                license_service.iso(now + dt.timedelta(days=30)),
                license_service.iso(now),
            ),
        )
        cursor = connection.execute(
            """
            INSERT INTO users(username,username_norm,password_hash,license_id,created_at)
            VALUES(?,?,?,?,?)
            """,
            (
                "test-user",
                "test-user",
                license_service.password_hasher.hash("initial-password-123"),
                "a" * 32,
                license_service.iso(now),
            ),
        )
    return cursor.lastrowid


def test_temporary_password_is_one_time_and_requires_change_before_sign_in(seeded_user):
    response = license_service.create_temporary_password(seeded_user)
    with license_service.db() as connection:
        row = connection.execute(
            "SELECT password_hash,password_change_required FROM users WHERE id=?",
            (seeded_user,),
        ).fetchone()
    assert response["temporary_password"]
    assert license_service.password_hasher.verify(
        row["password_hash"], response["temporary_password"]
    )
    assert row["password_change_required"] == 1
    listed_user = license_service.list_users()["users"][0]
    assert listed_user["password_change_required"] is True
    assert "password_hash" not in listed_user

    result = license_service.login(
        license_service.LoginRequest(
            username="test-user",
            password=response["temporary_password"],
            machine_id="c" * 32,
        ),
        None,
    )
    assert result == {"password_change_required": True}
    with license_service.db() as connection:
        assert connection.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 0


def test_temporary_password_change_rejects_wrong_password_and_allows_new_device(seeded_user):
    response = license_service.create_temporary_password(seeded_user)
    request = license_service.TemporaryPasswordChangeRequest(
        username="test-user",
        temporary_password="wrong-temporary-password",
        new_password="replacement-password-123",
    )
    with pytest.raises(HTTPException) as caught:
        license_service.change_temporary_password(request)
    assert caught.value.status_code == 401

    request.temporary_password = response["temporary_password"]
    license_service.change_temporary_password(request)
    result = license_service.login(
        license_service.LoginRequest(
            username="test-user",
            password="replacement-password-123",
            machine_id="c" * 32,
        ),
        None,
    )
    assert result["session_token"]
    with license_service.db() as connection:
        row = connection.execute(
            """
            SELECT u.password_change_required,l.machine_id
            FROM users u JOIN licenses l ON l.license_id=u.license_id WHERE u.id=?
            """,
            (seeded_user,),
        ).fetchone()
    assert row["password_change_required"] == 0
    assert row["machine_id"] == "C" * 32


def test_temporary_password_must_be_replaced_with_a_different_value(seeded_user):
    response = license_service.create_temporary_password(seeded_user)
    request = license_service.TemporaryPasswordChangeRequest(
        username="test-user",
        temporary_password=response["temporary_password"],
        new_password=response["temporary_password"],
    )
    with pytest.raises(HTTPException) as caught:
        license_service.change_temporary_password(request)
    assert caught.value.status_code == 422


def test_admin_set_password_requires_change_and_revokes_sessions(seeded_user):
    with license_service.db() as connection:
        connection.execute(
            "INSERT INTO sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
            (
                hashlib.sha256(b"session-token").hexdigest(),
                seeded_user,
                license_service.iso(license_service.utc_now()),
                license_service.iso(license_service.utc_now() + dt.timedelta(days=1)),
            ),
        )

    license_service.set_user_password(
        seeded_user,
        license_service.AdminPasswordRequest(password="administrator-set-password"),
    )
    with license_service.db() as connection:
        row = connection.execute(
            """
            SELECT u.password_hash,u.password_change_required,s.revoked_at
            FROM users u JOIN sessions s ON s.user_id=u.id WHERE u.id=?
            """,
            (seeded_user,),
        ).fetchone()
    assert license_service.password_hasher.verify(
        row["password_hash"], "administrator-set-password"
    )
    assert row["password_change_required"] == 1
    assert row["revoked_at"] is not None


def test_unlink_revokes_sessions_and_next_login_binds_new_device(seeded_user):
    now = license_service.utc_now()
    with license_service.db() as connection:
        connection.execute(
            "INSERT INTO sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
            (
                hashlib.sha256(b"session-token").hexdigest(),
                seeded_user,
                license_service.iso(now),
                license_service.iso(now + dt.timedelta(days=1)),
            ),
        )

    license_service.unlink_user_device(seeded_user)
    with license_service.db() as connection:
        row = connection.execute(
            """
            SELECT l.machine_id,s.revoked_at
            FROM licenses l JOIN users u ON u.license_id=l.license_id
            JOIN sessions s ON s.user_id=u.id WHERE u.id=?
            """,
            (seeded_user,),
        ).fetchone()
    assert row["machine_id"] == ""
    assert row["revoked_at"] is not None

    result = license_service.login(
        license_service.LoginRequest(
            username="test-user",
            password="initial-password-123",
            machine_id="d" * 32,
        ),
        None,
    )
    assert result["session_token"]
    with license_service.db() as connection:
        assert connection.execute(
            "SELECT machine_id FROM licenses WHERE license_id=?", ("a" * 32,)
        ).fetchone()["machine_id"] == "D" * 32


def test_admin_account_routes_are_exposed():
    routes = {
        (route.path, method)
        for route in license_service.app.routes
        for method in getattr(route, "methods", set())
    }
    assert ("/v1/admin/users/{user_id}/password", "POST") in routes
    assert ("/v1/admin/users/{user_id}/temporary-password", "POST") in routes
    assert ("/v1/admin/users/{user_id}/unlink-device", "POST") in routes
    assert ("/v1/auth/change-temporary-password", "POST") in routes


def test_existing_account_database_gets_password_change_flag(tmp_path, monkeypatch):
    database_path = tmp_path / "legacy.sqlite3"
    monkeypatch.setattr(license_service, "DB_PATH", database_path)
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE licenses (
                license_id TEXT PRIMARY KEY,
                key_hash TEXT NOT NULL UNIQUE,
                machine_id TEXT NOT NULL,
                plan TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                expires_at TEXT,
                enabled INTEGER NOT NULL DEFAULT 1,
                claimed_by INTEGER,
                created_at TEXT NOT NULL
            );
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                username_norm TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                license_id TEXT NOT NULL UNIQUE REFERENCES licenses(license_id),
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login_at TEXT
            );
            INSERT INTO licenses VALUES(
                'a','b','C','trial','2026-10-07T00:00:00Z',NULL,1,NULL,'2026-10-07T00:00:00Z'
            );
            INSERT INTO users(username,username_norm,password_hash,license_id,created_at)
            VALUES('legacy-user','legacy-user','hash','a','2026-10-07T00:00:00Z');
            """
        )

    license_service.init_db()
    with license_service.db() as connection:
        row = connection.execute(
            "SELECT password_change_required FROM users WHERE username_norm='legacy-user'"
        ).fetchone()
    assert row["password_change_required"] == 0
