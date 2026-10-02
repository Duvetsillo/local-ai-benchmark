from __future__ import annotations

import base64
import ctypes
import datetime as dt
import hashlib
import json
import os
import re
import tempfile
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class AuthError(ValueError):
    """The license account request was rejected by the service."""


class AuthUnavailable(ConnectionError):
    """The license service could not be reached."""


@dataclass(frozen=True)
class AuthSession:
    username: str
    license_id: str
    plan: str
    expires_at: dt.datetime | None
    session_token: str | None
    offline_ticket: str
    offline_public_key: str
    offline_until: dt.datetime
    offline: bool = False


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(microsecond=0)


def _parse_time(value: Any) -> dt.datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise AuthError("El servicio devolvió una fecha de licencia inválida.")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuthError("El servicio devolvió una fecha de licencia inválida.") from exc
    if parsed.tzinfo is None:
        raise AuthError("El servicio devolvió una fecha sin zona horaria.")
    return parsed.astimezone(dt.UTC)


def _data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") or str(Path.home())
    return Path(base) / "Aetherion"


def _service_config_path() -> Path:
    return _data_dir() / "service.json"


def get_service_url() -> str:
    configured = os.environ.get("AETHERION_API_URL", "").strip()
    if configured:
        return configured.rstrip("/")
    default_url = "https://aetherionlbs.duckdns.org"
    try:
        payload = json.loads(_service_config_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default_url
    value = payload.get("url", "") if isinstance(payload, dict) else ""
    return value.strip().rstrip("/") if isinstance(value, str) and value.strip() else default_url


def save_service_url(value: str) -> str:
    url = value.strip().rstrip("/")
    parts = urlparse(url)
    local = parts.hostname in {"localhost", "127.0.0.1", "::1"}
    if parts.scheme != "https" and not (parts.scheme == "http" and local):
        raise AuthError("Usa una dirección HTTPS para el servidor. HTTP solo se permite en localhost.")
    if not parts.netloc or parts.username or parts.password or parts.query or parts.fragment:
        raise AuthError("Escribe la dirección base del servicio, por ejemplo https://licencias.tudominio.com.")
    path = _service_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"url": url}, indent=2), encoding="utf-8")
    return url


def _dpapi(data: bytes, decrypt: bool = False) -> bytes:
    if os.name != "nt":
        return data

    class DataBlob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

    source_buffer = (ctypes.c_byte * len(data)).from_buffer_copy(data)
    source = DataBlob(len(data), ctypes.cast(source_buffer, ctypes.POINTER(ctypes.c_byte)))
    target = DataBlob()
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    if decrypt:
        call = crypt32.CryptUnprotectData
        call.argtypes = [ctypes.POINTER(DataBlob), ctypes.c_void_p, ctypes.c_void_p,
                         ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD,
                         ctypes.POINTER(DataBlob)]
        call.restype = wintypes.BOOL
        ok = call(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target))
    else:
        call = crypt32.CryptProtectData
        call.argtypes = [ctypes.POINTER(DataBlob), wintypes.LPCWSTR, ctypes.c_void_p,
                         ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD,
                         ctypes.POINTER(DataBlob)]
        call.restype = wintypes.BOOL
        ok = call(ctypes.byref(source), "Aetherion account session", None, None, None, 1, ctypes.byref(target))
    if not ok:
        raise OSError(ctypes.get_last_error(), "Windows could not protect the Aetherion session cache")
    try:
        return ctypes.string_at(target.pbData, target.cbData)
    finally:
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        kernel32.LocalFree(target.pbData)


def _cache_path() -> Path:
    return _data_dir() / "account-session.bin"


def _read_cache() -> dict[str, Any] | None:
    try:
        protected = _cache_path().read_bytes()
        value = json.loads(_dpapi(protected, decrypt=True).decode("utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _write_cache(value: dict[str, Any]) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    protected = _dpapi(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    fd, temporary = tempfile.mkstemp(prefix="account-session-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(protected)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def clear_cached_session() -> None:
    try:
        _cache_path().unlink(missing_ok=True)
    except OSError:
        pass


def _decode_offline_ticket(token: str, public_key_b64: str, machine_id: str) -> tuple[dict[str, Any], dt.datetime]:
    parts = token.strip().split(".")
    if len(parts) != 3 or parts[0] != "AOFF1":
        raise AuthError("No hay una sesión offline válida guardada en este equipo.")
    try:
        decode = lambda value: base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        payload_bytes = decode(parts[1])
        signature = decode(parts[2])
        public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64, validate=True))
        public_key.verify(signature, payload_bytes)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, InvalidSignature, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthError("La licencia offline guardada no pudo verificarse.") from exc
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise AuthError("La licencia offline no es compatible.")
    if payload.get("machine_id") != machine_id.upper():
        raise AuthError("La sesión offline pertenece a otro equipo.")
    offline_until = _parse_time(payload.get("offline_until"))
    if offline_until is None or _utc_now() >= offline_until:
        raise AuthError("Se agotó el periodo offline. Conéctate para iniciar sesión y renovar la autorización.")
    expires_at = _parse_time(payload.get("license_expires_at"))
    if expires_at is not None and _utc_now() >= expires_at + dt.timedelta(days=7):
        raise AuthError("La suscripción venció y terminó el periodo offline de gracia.")
    return payload, offline_until


class AccountService:
    def __init__(self, base_url: str | None = None, timeout: float = 10):
        self.base_url = (base_url or get_service_url()).strip().rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None,
                 token: str | None = None) -> dict[str, Any]:
        if not self.base_url:
            raise AuthError("Configura primero la dirección del servidor de licencias.")
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(self.base_url + path, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                value = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("detail", "")
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                detail = ""
            raise AuthError(str(detail) or f"El servidor rechazó la solicitud ({exc.code}).") from None
        except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise AuthUnavailable("No se pudo conectar con el servidor de licencias.") from exc
        if not isinstance(value, dict):
            raise AuthError("El servidor devolvió una respuesta inválida.")
        return value

    @staticmethod
    def _session_from_response(value: dict[str, Any], *, session_token: str | None = None,
                               offline: bool = False) -> AuthSession:
        try:
            expiry = _parse_time(value.get("expires_at"))
            ticket = value["offline_ticket"]
            public_key = value["offline_public_key"]
            payload, offline_until = _decode_offline_ticket(ticket, public_key, machine_fingerprint())
            session = AuthSession(username=str(value["username"]), license_id=str(value["license_id"]),
                                  plan=str(value["plan"]), expires_at=expiry,
                                  session_token=session_token or value.get("session_token"),
                                  offline_ticket=ticket, offline_public_key=public_key,
                                  offline_until=offline_until, offline=offline)
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, AuthError):
                raise
            raise AuthError("El servidor devolvió una sesión incompleta.") from exc
        return session

    def register(self, username: str, password: str, license_key: str, machine_id: str) -> AuthSession:
        value = self._request("POST", "/v1/auth/register", {"username": username, "password": password,
                              "license_key": license_key, "machine_id": machine_id})
        session = self._session_from_response(value)
        _write_cache({"session_token": session.session_token, "offline_ticket": session.offline_ticket,
                      "offline_public_key": session.offline_public_key, "username": session.username,
                      "server_url": self.base_url, "last_seen_utc": _utc_now().isoformat()})
        return session

    def login(self, username: str, password: str, machine_id: str) -> AuthSession:
        value = self._request("POST", "/v1/auth/login", {"username": username, "password": password,
                              "machine_id": machine_id})
        session = self._session_from_response(value)
        _write_cache({"session_token": session.session_token, "offline_ticket": session.offline_ticket,
                      "offline_public_key": session.offline_public_key, "username": session.username,
                      "server_url": self.base_url, "last_seen_utc": _utc_now().isoformat()})
        return session

    def refresh(self, session: AuthSession) -> AuthSession:
        if not session.session_token:
            raise AuthUnavailable("La sesión está en modo offline y no puede sincronizarse ahora.")
        value = self._request("GET", "/v1/auth/me", token=session.session_token)
        refreshed = self._session_from_response(value, session_token=session.session_token)
        _write_cache({"session_token": refreshed.session_token, "offline_ticket": refreshed.offline_ticket,
                      "offline_public_key": refreshed.offline_public_key, "username": refreshed.username,
                      "server_url": self.base_url, "last_seen_utc": _utc_now().isoformat()})
        return refreshed

    def logout(self, session: AuthSession | None) -> None:
        try:
            if session and session.session_token:
                self._request("POST", "/v1/auth/logout", token=session.session_token)
        finally:
            clear_cached_session()

    def restore_cached(self, machine_id: str) -> AuthSession | None:
        cached = _read_cache()
        if not cached:
            return None
        saved_url = str(cached.get("server_url") or self.base_url)
        service = AccountService(saved_url, timeout=self.timeout)
        token = cached.get("session_token")
        if isinstance(token, str) and token:
            try:
                online = service._request("GET", "/v1/auth/me", token=token)
                session = service._session_from_response(online, session_token=token)
                _write_cache({**cached, "offline_ticket": session.offline_ticket,
                              "offline_public_key": session.offline_public_key,
                              "last_seen_utc": _utc_now().isoformat()})
                return session
            except AuthUnavailable:
                pass
            except AuthError:
                clear_cached_session()
                return None
        ticket = cached.get("offline_ticket")
        public_key = cached.get("offline_public_key")
        if not isinstance(ticket, str) or not isinstance(public_key, str):
            clear_cached_session()
            return None
        try:
            payload, offline_until = _decode_offline_ticket(ticket, public_key, machine_id)
            last_seen = _parse_time(cached.get("last_seen_utc"))
            if last_seen and _utc_now() + dt.timedelta(minutes=5) < last_seen:
                raise AuthError("El reloj del equipo retrocedió durante la sesión offline.")
            _write_cache({**cached, "last_seen_utc": _utc_now().isoformat()})
            expiry = _parse_time(payload.get("license_expires_at"))
            return AuthSession(username=str(payload["username"]), license_id=str(payload["license_id"]),
                               plan=str(payload.get("plan", "offline")), expires_at=expiry, session_token=None,
                               offline_ticket=ticket, offline_public_key=public_key,
                               offline_until=offline_until, offline=True)
        except (AuthError, KeyError, TypeError, ValueError):
            return None


def machine_fingerprint() -> str:
    from .licensing import machine_fingerprint as get_fingerprint
    return get_fingerprint()
