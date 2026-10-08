from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Literal

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa


APP_VERSION = "1.0.0"
OFFLINE_GRACE_DAYS = 7
SESSION_HOURS = 24 * 30
DB_PATH = Path(os.environ.get("AETHERION_DATABASE_PATH", "/data/aetherion.sqlite3"))
LICENSE_PUBLIC_KEY_N = os.environ.get("AETHERION_LICENSE_PUBLIC_KEY_N", "")
LICENSE_PUBLIC_KEY_E = 65537
ADMIN_TOKEN = os.environ.get("AETHERION_ADMIN_TOKEN", "")
OFFLINE_SIGNING_KEY_PATH = Path(os.environ.get("AETHERION_OFFLINE_SIGNING_KEY", "/data/offline-signing-ed25519.pem"))
password_hasher = PasswordHasher(time_cost=2, memory_cost=19_456, parallelism=1, hash_len=32, salt_len=16)
dummy_password_hash = password_hasher.hash(secrets.token_urlsafe(32))

app = FastAPI(title="Aetherion License Service", version=APP_VERSION, docs_url=None, redoc_url=None)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=12, max_length=128)
    license_key: str = Field(min_length=32, max_length=4096)
    machine_id: str = Field(pattern=r"^[A-Fa-f0-9]{32}$")


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=128)
    machine_id: str = Field(pattern=r"^[A-Fa-f0-9]{32}$")


class LicenseSyncRequest(BaseModel):
    license_key: str = Field(min_length=32, max_length=4096)


class RenewRequest(BaseModel):
    days: int = Field(ge=1, le=3650)


class PlanChangeRequest(BaseModel):
    plan: Literal["trial", "duration", "unlimited"]
    days: int | None = Field(default=None, ge=1, le=3650)


class AdminPasswordRequest(BaseModel):
    password: str = Field(min_length=12, max_length=128)


class TemporaryPasswordChangeRequest(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    temporary_password: str = Field(min_length=12, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)


class BaseResponse(BaseModel):
    ok: bool = True


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(microsecond=0)


def iso(value: dt.datetime | None) -> str | None:
    return value.astimezone(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z") if value else None


def parse_time(value: Any, field: str) -> dt.datetime:
    if not isinstance(value, str):
        raise ValueError(f"Invalid {field}")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Missing timezone for {field}")
    return parsed.astimezone(dt.UTC)


def b64url_decode(value: str) -> bytes:
    if not value or re.fullmatch(r"[A-Za-z0-9_-]+", value) is None:
        raise ValueError("Invalid base64url")
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def verify_license(token: str) -> dict[str, Any]:
    if not LICENSE_PUBLIC_KEY_N:
        raise HTTPException(status_code=503, detail="License verification is not configured")
    parts = token.strip().split(".")
    if len(parts) != 3 or parts[0] != "AETH1":
        raise HTTPException(status_code=400, detail="Invalid license key")
    try:
        payload_bytes = b64url_decode(parts[1])
        signature = b64url_decode(parts[2])
        public_key = rsa.RSAPublicNumbers(LICENSE_PUBLIC_KEY_E, int(LICENSE_PUBLIC_KEY_N, 16)).public_key()
        public_key.verify(signature, payload_bytes,
                           padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.AUTO),
                           hashes.SHA256())
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (InvalidSignature, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(status_code=400, detail="License signature or payload is invalid") from None
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise HTTPException(status_code=400, detail="Unsupported license")
    if payload.get("plan") not in {"trial", "duration", "unlimited"}:
        raise HTTPException(status_code=400, detail="Unsupported license plan")
    if not isinstance(payload.get("license_id"), str) or not re.fullmatch(r"[a-fA-F0-9]{32}", payload["license_id"]):
        raise HTTPException(status_code=400, detail="Invalid license ID")
    if not isinstance(payload.get("machine_id"), str) or not re.fullmatch(r"[A-Fa-f0-9]{32}", payload["machine_id"]):
        raise HTTPException(status_code=400, detail="Invalid license device")
    try:
        issued = parse_time(payload.get("issued_at"), "issued_at")
        expires = None if payload["plan"] == "unlimited" else parse_time(payload.get("expires_at"), "expires_at")
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid license dates") from None
    now = utc_now()
    if issued > now + dt.timedelta(minutes=5) or (expires and expires <= now):
        raise HTTPException(status_code=400, detail="License is not currently valid")
    if expires and expires <= issued:
        raise HTTPException(status_code=400, detail="Invalid license period")
    return {"license_id": payload["license_id"].lower(), "machine_id": payload["machine_id"].upper(),
            "plan": payload["plan"], "issued_at": issued, "expires_at": expires,
            "key_hash": hashlib.sha256(token.strip().encode("utf-8")).hexdigest()}


def get_offline_signer() -> ed25519.Ed25519PrivateKey:
    OFFLINE_SIGNING_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if OFFLINE_SIGNING_KEY_PATH.exists():
        loaded = serialization.load_pem_private_key(OFFLINE_SIGNING_KEY_PATH.read_bytes(), password=None)
        if not isinstance(loaded, ed25519.Ed25519PrivateKey):
            raise RuntimeError("Offline signing key has an unsupported type")
        return loaded
    key = ed25519.Ed25519PrivateKey.generate()
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption())
    fd = os.open(OFFLINE_SIGNING_KEY_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(pem)
        output.flush()
        os.fsync(output.fileno())
    return key


def public_signing_key_b64() -> str:
    raw = get_offline_signer().public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def signed_offline_ticket(user: sqlite3.Row, license_row: sqlite3.Row) -> str:
    now = utc_now()
    license_expiry = parse_time(license_row["expires_at"], "expires_at") if license_row["expires_at"] else None
    offline_until = now + dt.timedelta(days=OFFLINE_GRACE_DAYS)
    if license_expiry is not None:
        offline_until = min(offline_until, license_expiry + dt.timedelta(days=OFFLINE_GRACE_DAYS))
    payload = {"version": 1, "username": user["username"], "license_id": license_row["license_id"],
               "plan": license_row["plan"],
               "machine_id": license_row["machine_id"], "checked_at": iso(now),
               "license_expires_at": iso(license_expiry), "offline_until": iso(offline_until)}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    signature = get_offline_signer().sign(encoded)
    return f"AOFF1.{base64.urlsafe_b64encode(encoded).decode().rstrip('=')}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    with db() as connection:
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS licenses (
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
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            username_norm TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            license_id TEXT NOT NULL UNIQUE REFERENCES licenses(license_id),
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login_at TEXT
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            revoked_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_users_license ON users(license_id);
        """)
        user_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "password_change_required" not in user_columns:
            connection.execute(
                "ALTER TABLE users ADD COLUMN password_change_required INTEGER NOT NULL DEFAULT 0"
            )


@app.on_event("startup")
def startup() -> None:
    if not ADMIN_TOKEN or len(ADMIN_TOKEN) < 32:
        raise RuntimeError("Set AETHERION_ADMIN_TOKEN to a random value of at least 32 characters")
    init_db()
    get_offline_signer()


def require_admin(authorization: str | None = Header(default=None)) -> None:
    expected = f"Bearer {ADMIN_TOKEN}"
    if not authorization or not hmac.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Admin authentication required")


def get_session(authorization: str | None = Header(default=None)) -> tuple[sqlite3.Row, sqlite3.Row]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Sign-in required")
    token = authorization[7:].strip()
    if len(token) < 32:
        raise HTTPException(status_code=401, detail="Session is invalid")
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = iso(utc_now())
    with db() as connection:
        row = connection.execute("""
            SELECT s.expires_at AS session_expires, s.revoked_at, u.*, l.machine_id,
                   l.plan, l.expires_at AS license_expires, l.enabled AS license_enabled, l.license_id
            FROM sessions s JOIN users u ON u.id=s.user_id JOIN licenses l ON l.license_id=u.license_id
            WHERE s.token_hash=?
        """, (token_hash,)).fetchone()
    if row is None or row["revoked_at"] or row["session_expires"] <= now:
        raise HTTPException(status_code=401, detail="Session expired; sign in again")
    if not row["active"] or not row["license_enabled"]:
        raise HTTPException(status_code=403, detail="Account or license is disabled")
    if row["license_expires"] and row["license_expires"] <= now:
        raise HTTPException(status_code=403, detail="Subscription expired")
    return row, row


def session_response(user: sqlite3.Row, license_row: sqlite3.Row, session_token: str | None = None,
                     session_expiry: dt.datetime | None = None) -> dict[str, Any]:
    value = {"username": user["username"], "license_id": license_row["license_id"],
             "plan": license_row["plan"], "expires_at": license_row["expires_at"],
             "offline_ticket": signed_offline_ticket(user, license_row),
             "offline_public_key": public_signing_key_b64(), "offline_grace_days": OFFLINE_GRACE_DAYS}
    if session_token is not None:
        value["session_token"] = session_token
        value["session_expires_at"] = iso(session_expiry)
    return value


def new_session(user: sqlite3.Row, license_row: sqlite3.Row) -> dict[str, Any]:
    token = secrets.token_urlsafe(48)
    now = utc_now()
    expires = now + dt.timedelta(hours=SESSION_HOURS)
    with db() as connection:
        connection.execute("INSERT INTO sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
                           (hashlib.sha256(token.encode()).hexdigest(), user["id"], iso(now), iso(expires)))
        connection.execute("UPDATE users SET last_login_at=? WHERE id=?", (iso(now), user["id"]))
    return session_response(user, license_row, token, expires)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aetherion-license-service", "version": APP_VERSION}


@app.get("/v1/config")
def config() -> dict[str, Any]:
    return {"offline_public_key": public_signing_key_b64(), "offline_grace_days": OFFLINE_GRACE_DAYS,
            "session_hours": SESSION_HOURS, "version": APP_VERSION}


@app.post("/v1/auth/register")
def register(payload: RegisterRequest, request: Request) -> dict[str, Any]:
    username = payload.username.strip()
    username_norm = username.casefold()
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,31}", username) is None:
        raise HTTPException(status_code=422, detail="Username must use 3-32 letters, numbers, dot, underscore, or dash")
    if len(payload.password.encode("utf-8")) < 12:
        raise HTTPException(status_code=422, detail="Password must contain at least 12 UTF-8 bytes")
    license_info = verify_license(payload.license_key)
    if license_info["machine_id"] != payload.machine_id.upper():
        raise HTTPException(status_code=403, detail="License is not for this computer")
    password_hash = password_hasher.hash(payload.password)
    try:
        with db() as connection:
            connection.execute("BEGIN IMMEDIATE")
            license_row = connection.execute("SELECT * FROM licenses WHERE license_id=?", (license_info["license_id"],)).fetchone()
            if license_row is None or not hmac.compare_digest(license_row["key_hash"], license_info["key_hash"]):
                raise HTTPException(status_code=403, detail="This license has not been registered by the owner")
            if not license_row["enabled"] or license_row["claimed_by"] is not None:
                raise HTTPException(status_code=409, detail="This license has already been used or disabled")
            if license_row["machine_id"] != payload.machine_id.upper():
                raise HTTPException(status_code=403, detail="License is not for this computer")
            if license_row["expires_at"] and license_row["expires_at"] <= iso(utc_now()):
                raise HTTPException(status_code=403, detail="License has expired")
            cursor = connection.execute("""
                INSERT INTO users(username,username_norm,password_hash,license_id,created_at)
                VALUES(?,?,?,?,?)
            """, (username, username_norm, password_hash, license_row["license_id"], iso(utc_now())))
            user_id = cursor.lastrowid
            connection.execute("UPDATE licenses SET claimed_by=? WHERE license_id=?", (user_id, license_row["license_id"]))
            user = connection.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            token = secrets.token_urlsafe(48)
            now = utc_now()
            session_expiry = now + dt.timedelta(hours=SESSION_HOURS)
            connection.execute("INSERT INTO sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
                               (hashlib.sha256(token.encode()).hexdigest(), user_id, iso(now), iso(session_expiry)))
            connection.execute("UPDATE users SET last_login_at=? WHERE id=?", (iso(now), user_id))
            return session_response(user, license_row, token, session_expiry)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Username or license is already in use") from None


@app.post("/v1/auth/login")
def login(payload: LoginRequest, request: Request) -> dict[str, Any]:
    username_norm = payload.username.strip().casefold()
    with db() as connection:
        connection.execute("BEGIN IMMEDIATE")
        user = connection.execute("SELECT * FROM users WHERE username_norm=?", (username_norm,)).fetchone()
        if user is None:
            try:
                password_hasher.verify(dummy_password_hash, payload.password)
            except (VerifyMismatchError, VerificationError, InvalidHashError):
                pass
            raise HTTPException(status_code=401, detail="Username or password is incorrect")
        try:
            password_hasher.verify(user["password_hash"], payload.password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            raise HTTPException(status_code=401, detail="Username or password is incorrect") from None
        if not user["active"]:
            raise HTTPException(status_code=403, detail="This account is disabled")
        license_row = connection.execute("SELECT * FROM licenses WHERE license_id=?", (user["license_id"],)).fetchone()
        if license_row is None or not license_row["enabled"]:
            raise HTTPException(status_code=403, detail="License is disabled")
        if license_row["expires_at"] and license_row["expires_at"] <= iso(utc_now()):
            raise HTTPException(status_code=403, detail="Subscription expired")
        if user["password_change_required"]:
            return {"password_change_required": True}
        machine_id = payload.machine_id.upper()
        if not license_row["machine_id"]:
            connection.execute(
                "UPDATE licenses SET machine_id=? WHERE license_id=? AND machine_id=''",
                (machine_id, license_row["license_id"]),
            )
            license_row = connection.execute(
                "SELECT * FROM licenses WHERE license_id=?", (license_row["license_id"],)
            ).fetchone()
        if license_row["machine_id"] != machine_id:
            raise HTTPException(status_code=403, detail="This account is bound to another computer")
        token = secrets.token_urlsafe(48)
        now = utc_now()
        session_expiry = now + dt.timedelta(hours=SESSION_HOURS)
        connection.execute(
            "INSERT INTO sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
            (hashlib.sha256(token.encode()).hexdigest(), user["id"], iso(now), iso(session_expiry)),
        )
        connection.execute("UPDATE users SET last_login_at=? WHERE id=?", (iso(now), user["id"]))
        user = connection.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
    return session_response(user, license_row, token, session_expiry)


@app.post("/v1/auth/change-temporary-password", response_model=BaseResponse)
def change_temporary_password(payload: TemporaryPasswordChangeRequest) -> dict[str, bool]:
    if len(payload.new_password.encode("utf-8")) < 12:
        raise HTTPException(status_code=422, detail="Password must contain at least 12 UTF-8 bytes")
    if hmac.compare_digest(payload.temporary_password, payload.new_password):
        raise HTTPException(status_code=422, detail="Choose a password different from the temporary password")
    username_norm = payload.username.strip().casefold()
    with db() as connection:
        connection.execute("BEGIN IMMEDIATE")
        user = connection.execute(
            "SELECT id,password_hash,password_change_required FROM users WHERE username_norm=?",
            (username_norm,),
        ).fetchone()
        if user is None or not user["password_change_required"]:
            try:
                password_hasher.verify(dummy_password_hash, payload.temporary_password)
            except (VerifyMismatchError, VerificationError, InvalidHashError):
                pass
            raise HTTPException(status_code=401, detail="Temporary password is invalid or no longer active")
        try:
            password_hasher.verify(user["password_hash"], payload.temporary_password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            raise HTTPException(status_code=401, detail="Temporary password is invalid or no longer active") from None
        password_hash = password_hasher.hash(payload.new_password)
        connection.execute(
            "UPDATE users SET password_hash=?,password_change_required=0 WHERE id=?",
            (password_hash, user["id"]),
        )
        connection.execute(
            "UPDATE sessions SET revoked_at=? WHERE user_id=? AND revoked_at IS NULL",
            (iso(utc_now()), user["id"]),
        )
    return {"ok": True}


@app.get("/v1/auth/me")
def me(session: tuple[sqlite3.Row, sqlite3.Row] = Depends(get_session)) -> dict[str, Any]:
    user, _ = session
    with db() as connection:
        fresh_user = connection.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
        license_row = connection.execute("SELECT * FROM licenses WHERE license_id=?", (user["license_id"],)).fetchone()
    return session_response(fresh_user, license_row)


@app.post("/v1/auth/logout", response_model=BaseResponse)
def logout(authorization: str | None = Header(default=None)) -> dict[str, bool]:
    if not authorization or not authorization.startswith("Bearer "):
        return {"ok": True}
    token = authorization[7:].strip()
    if token:
        with db() as connection:
            connection.execute("UPDATE sessions SET revoked_at=? WHERE token_hash=? AND revoked_at IS NULL",
                               (iso(utc_now()), hashlib.sha256(token.encode()).hexdigest()))
    return {"ok": True}


@app.post("/v1/admin/licenses", dependencies=[Depends(require_admin)])
def sync_license(payload: LicenseSyncRequest) -> dict[str, Any]:
    info = verify_license(payload.license_key)
    with db() as connection:
        existing = connection.execute("SELECT * FROM licenses WHERE license_id=?", (info["license_id"],)).fetchone()
        if existing:
            if not hmac.compare_digest(existing["key_hash"], info["key_hash"]):
                raise HTTPException(status_code=409, detail="A different key uses this license ID")
            return {"ok": True, "license_id": existing["license_id"], "claimed": existing["claimed_by"] is not None}
        connection.execute("""
            INSERT INTO licenses(license_id,key_hash,machine_id,plan,issued_at,expires_at,created_at)
            VALUES(?,?,?,?,?,?,?)
        """, (info["license_id"], info["key_hash"], info["machine_id"], info["plan"],
              iso(info["issued_at"]), iso(info["expires_at"]), iso(utc_now())))
    return {"ok": True, "license_id": info["license_id"], "claimed": False}


@app.get("/v1/admin/users", dependencies=[Depends(require_admin)])
def list_users() -> dict[str, Any]:
    with db() as connection:
        rows = connection.execute("""
            SELECT u.id,u.username,u.active,u.created_at,u.last_login_at,l.license_id,l.machine_id,
                   l.plan,l.expires_at,l.enabled AS license_enabled,u.password_change_required
            FROM users u JOIN licenses l ON l.license_id=u.license_id
            ORDER BY u.created_at DESC
        """).fetchall()
    now = utc_now()
    users = []
    for row in rows:
        expiry = parse_time(row["expires_at"], "expires_at") if row["expires_at"] else None
        users.append({"id": row["id"], "username": row["username"], "active": bool(row["active"]),
                      "created_at": row["created_at"], "last_login_at": row["last_login_at"],
                      "license_id": row["license_id"], "machine_id": row["machine_id"],
                      "plan": row["plan"], "expires_at": row["expires_at"],
                      "days_remaining": max(0, (expiry.date() - now.date()).days) if expiry else None,
                      "license_enabled": bool(row["license_enabled"]),
                      "password_change_required": bool(row["password_change_required"])})
    return {"users": users}


@app.post("/v1/admin/users/{user_id}/password", dependencies=[Depends(require_admin)], response_model=BaseResponse)
def set_user_password(user_id: int, payload: AdminPasswordRequest) -> dict[str, bool]:
    if len(payload.password.encode("utf-8")) < 12:
        raise HTTPException(status_code=422, detail="Password must contain at least 12 UTF-8 bytes")
    password_hash = password_hasher.hash(payload.password)
    with db() as connection:
        cursor = connection.execute(
            "UPDATE users SET password_hash=?,password_change_required=1 WHERE id=?",
            (password_hash, user_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        connection.execute(
            "UPDATE sessions SET revoked_at=? WHERE user_id=? AND revoked_at IS NULL",
            (iso(utc_now()), user_id),
        )
    return {"ok": True}


@app.post("/v1/admin/users/{user_id}/temporary-password", dependencies=[Depends(require_admin)])
def create_temporary_password(user_id: int) -> dict[str, Any]:
    temporary_password = secrets.token_urlsafe(24)
    password_hash = password_hasher.hash(temporary_password)
    with db() as connection:
        cursor = connection.execute(
            "UPDATE users SET password_hash=?,password_change_required=1 WHERE id=?",
            (password_hash, user_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        username = connection.execute(
            "SELECT username FROM users WHERE id=?", (user_id,)
        ).fetchone()["username"]
        connection.execute(
            "UPDATE sessions SET revoked_at=? WHERE user_id=? AND revoked_at IS NULL",
            (iso(utc_now()), user_id),
        )
    return {"ok": True, "username": username, "temporary_password": temporary_password}


@app.post("/v1/admin/users/{user_id}/unlink-device", dependencies=[Depends(require_admin)], response_model=BaseResponse)
def unlink_user_device(user_id: int) -> dict[str, bool]:
    with db() as connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT license_id FROM users WHERE id=?", (user_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        connection.execute(
            "UPDATE licenses SET machine_id='' WHERE license_id=?", (row["license_id"],)
        )
        connection.execute(
            "UPDATE sessions SET revoked_at=? WHERE user_id=? AND revoked_at IS NULL",
            (iso(utc_now()), user_id),
        )
    return {"ok": True}


@app.post("/v1/admin/users/{user_id}/renew", dependencies=[Depends(require_admin)])
def renew_user(user_id: int, payload: RenewRequest) -> dict[str, Any]:
    now = utc_now()
    with db() as connection:
        row = connection.execute("""
            SELECT u.username,l.license_id,l.plan,l.expires_at,l.enabled
            FROM users u JOIN licenses l ON l.license_id=u.license_id WHERE u.id=?
        """, (user_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        if row["plan"] == "unlimited" or row["expires_at"] is None:
            raise HTTPException(status_code=409, detail="Unlimited access does not need a renewal")
        old_expiry = parse_time(row["expires_at"], "expires_at")
        new_expiry = max(old_expiry, now) + dt.timedelta(days=payload.days)
        connection.execute("UPDATE licenses SET expires_at=? WHERE license_id=?", (iso(new_expiry), row["license_id"]))
        connection.execute("UPDATE licenses SET enabled=1 WHERE license_id=?", (row["license_id"],))
        connection.execute("UPDATE users SET active=1 WHERE id=?", (user_id,))
    return {"ok": True, "username": row["username"], "license_id": row["license_id"],
            "expires_at": iso(new_expiry), "days_added": payload.days}


@app.patch("/v1/admin/users/{user_id}/plan", dependencies=[Depends(require_admin)])
def change_user_plan(user_id: int, payload: PlanChangeRequest) -> dict[str, Any]:
    if payload.plan == "duration" and payload.days is None:
        raise HTTPException(status_code=422, detail="Duration in days is required for a custom plan")

    now = utc_now()
    days = 7 if payload.plan == "trial" else payload.days
    expires = None if payload.plan == "unlimited" else now + dt.timedelta(days=days)
    with db() as connection:
        row = connection.execute("""
            SELECT u.username,l.license_id
            FROM users u JOIN licenses l ON l.license_id=u.license_id WHERE u.id=?
        """, (user_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        connection.execute(
            "UPDATE licenses SET plan=?,expires_at=? WHERE license_id=?",
            (payload.plan, iso(expires), row["license_id"]),
        )
    return {"ok": True, "username": row["username"], "license_id": row["license_id"],
            "plan": payload.plan, "starts_at": iso(now), "expires_at": iso(expires),
            "days": days}


@app.post("/v1/admin/users/{user_id}/disable", dependencies=[Depends(require_admin)], response_model=BaseResponse)
def disable_user(user_id: int) -> dict[str, bool]:
    with db() as connection:
        cursor = connection.execute("UPDATE users SET active=0 WHERE id=?", (user_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        connection.execute("UPDATE sessions SET revoked_at=? WHERE user_id=? AND revoked_at IS NULL",
                           (iso(utc_now()), user_id))
    return {"ok": True}


@app.post("/v1/admin/users/{user_id}/enable", dependencies=[Depends(require_admin)], response_model=BaseResponse)
def enable_user(user_id: int) -> dict[str, bool]:
    with db() as connection:
        cursor = connection.execute("UPDATE users SET active=1 WHERE id=?", (user_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
