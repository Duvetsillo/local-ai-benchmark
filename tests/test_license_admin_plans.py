import datetime as dt

import pytest
from fastapi import HTTPException

from server import app as license_service


@pytest.fixture
def seeded_user(tmp_path, monkeypatch):
    monkeypatch.setattr(license_service, "DB_PATH", tmp_path / "license.sqlite3")
    license_service.init_db()
    issued = license_service.iso(license_service.utc_now())
    with license_service.db() as connection:
        connection.execute(
            """
            INSERT INTO licenses(license_id,key_hash,machine_id,plan,issued_at,expires_at,enabled,created_at)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            ("a" * 32, "b" * 64, "c" * 32, "duration", issued, issued, 0, issued),
        )
        cursor = connection.execute(
            """
            INSERT INTO users(username,username_norm,password_hash,license_id,active,created_at)
            VALUES(?,?,?,?,?,?)
            """,
            ("test-user", "test-user", "not-used", "a" * 32, 0, issued),
        )
    return cursor.lastrowid


def read_access_state():
    with license_service.db() as connection:
        return connection.execute(
            """
            SELECT u.active,l.plan,l.expires_at,l.enabled
            FROM users u JOIN licenses l ON l.license_id=u.license_id
            WHERE u.username_norm=?
            """,
            ("test-user",),
        ).fetchone()


def test_plan_change_is_exposed_as_an_admin_patch_route():
    assert any(
        getattr(route, "path", None) == "/v1/admin/users/{user_id}/plan"
        and "PATCH" in getattr(route, "methods", set())
        for route in license_service.app.routes
    )


def test_trial_plan_starts_a_seven_day_term_and_preserves_disabled_state(seeded_user):
    result = license_service.change_user_plan(
        seeded_user, license_service.PlanChangeRequest(plan="trial")
    )

    state = read_access_state()
    expiry = license_service.parse_time(result["expires_at"], "expires_at")
    starts = license_service.parse_time(result["starts_at"], "starts_at")
    assert result["plan"] == "trial"
    assert expiry == starts + dt.timedelta(days=7)
    assert state["plan"] == "trial"
    assert state["active"] == 0
    assert state["enabled"] == 0


def test_custom_plan_requires_a_duration(seeded_user):
    with pytest.raises(HTTPException) as caught:
        license_service.change_user_plan(
            seeded_user, license_service.PlanChangeRequest(plan="duration")
        )

    assert caught.value.status_code == 422
    assert read_access_state()["plan"] == "duration"


def test_custom_plan_uses_the_selected_number_of_days(seeded_user):
    result = license_service.change_user_plan(
        seeded_user, license_service.PlanChangeRequest(plan="duration", days=45)
    )

    expiry = license_service.parse_time(result["expires_at"], "expires_at")
    starts = license_service.parse_time(result["starts_at"], "starts_at")
    assert result["days"] == 45
    assert expiry == starts + dt.timedelta(days=45)
    assert read_access_state()["plan"] == "duration"


def test_unlimited_plan_clears_expiration(seeded_user):
    result = license_service.change_user_plan(
        seeded_user, license_service.PlanChangeRequest(plan="unlimited")
    )

    assert result["plan"] == "unlimited"
    assert result["expires_at"] is None
    state = read_access_state()
    assert state["plan"] == "unlimited"
    assert state["expires_at"] is None


def test_plan_change_returns_not_found_for_missing_user(tmp_path, monkeypatch):
    monkeypatch.setattr(license_service, "DB_PATH", tmp_path / "license.sqlite3")
    license_service.init_db()

    with pytest.raises(HTTPException) as caught:
        license_service.change_user_plan(
            42, license_service.PlanChangeRequest(plan="unlimited")
        )

    assert caught.value.status_code == 404
