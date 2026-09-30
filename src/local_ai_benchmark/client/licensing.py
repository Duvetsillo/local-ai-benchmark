from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import platform
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

PUBLIC_KEY_N = "cb6ac663a5a211b5a2e3b2d82e0358380943327545aaf96577ceb05d96d18e5e1415ad1307f2b2c7705c0b76482cec5f59f3cb6f540d57848c6e7b3c31c31e74cf2e8c68f29a7f3083f8cce31ec9e60ccd2390713a3ffa0cd47939bb4a5a7d08f386e2820d491a576233f62ac2502016b4579ed4e9a4a8f54a393529db269bcb6eafeb55d95302ca9e233b21b901ea82b00ec40ca46040ef1d2ff32b6702329259ec6eb1eb5d721f0b36a264f54213ec7b43a0398306f2e6b9cc2785a8237bee0ee92a82e3e95470d8622b36fb355803b520c043d27cbbe7906e48ab78b11baad58419ea06218c750ad8428c37502b8d5723d37c3545ba3891d9e18465e234fd"
PUBLIC_KEY_E = 65537
KEY_PREFIX = "AETH1"
TRIAL_DAYS = 7
MAX_LICENSE_DAYS = 3650
_CLOCK_SKEW = dt.timedelta(minutes=5)


class LicenseError(ValueError):
    """A key or local license state cannot authorize this installation."""


@dataclass(frozen=True)
class LicenseStatus:
    valid: bool
    message: str
    plan: str | None = None
    expires_at: dt.datetime | None = None
    license_id: str | None = None
    machine_id: str = ""


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(microsecond=0)


def _isoformat(value: dt.datetime) -> str:
    return value.astimezone(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_time(value: Any, field: str) -> dt.datetime:
    if not isinstance(value, str):
        raise LicenseError(f"La licencia contiene una fecha inválida ({field}).")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LicenseError(f"La licencia contiene una fecha inválida ({field}).") from exc
    if parsed.tzinfo is None:
        raise LicenseError(f"La licencia contiene una fecha sin zona horaria ({field}).")
    return parsed.astimezone(dt.UTC)


def machine_fingerprint() -> str:
    """Return a stable, privacy-preserving identifier for the current machine."""
    system_value = ""
    if sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                system_value = str(winreg.QueryValueEx(key, "MachineGuid")[0])
        except (OSError, ImportError):
            system_value = ""
    elif sys.platform == "darwin":
        system_value = platform.node()
    else:
        for candidate in (Path("/etc/machine-id"), Path("/var/lib/dbus/machine-id")):
            try:
                system_value = candidate.read_text(encoding="utf-8").strip()
                if system_value:
                    break
            except OSError:
                continue
    if not system_value:
        system_value = f"{platform.node()}:{uuid.getnode():012X}"
    digest = hashlib.sha256(b"Aetherion machine license v1\0" + system_value.encode("utf-8")).hexdigest().upper()
    return digest[:32]


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    if not value or any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for char in value):
        raise LicenseError("La clave no tiene un formato válido.")
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, base64.binascii.Error) as exc:
        raise LicenseError("La clave no tiene un formato válido.") from exc


def _canonical_payload(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _verify_rsa_sha256(payload: bytes, signature: bytes) -> bool:
    if not PUBLIC_KEY_N:
        raise LicenseError("Este cliente aún no tiene configurada su clave pública de licencias.")
    try:
        modulus = int(PUBLIC_KEY_N, 16)
    except ValueError as exc:
        raise LicenseError("La clave pública de licencias del cliente no es válida.") from exc
    try:
        public_key = rsa.RSAPublicNumbers(PUBLIC_KEY_E, modulus).public_key()
        public_key.verify(
            signature,
            payload,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.AUTO),
            hashes.SHA256(),
        )
    except (InvalidSignature, ValueError):
        return False
    return True


def decode_license(token: str) -> dict[str, Any]:
    parts = token.strip().split(".")
    if len(parts) != 3 or parts[0] != KEY_PREFIX:
        raise LicenseError("Pega una clave Aetherion completa y válida.")
    payload_bytes = _b64url_decode(parts[1])
    signature = _b64url_decode(parts[2])
    if not _verify_rsa_sha256(payload_bytes, signature):
        raise LicenseError("La firma de la licencia no es válida.")
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LicenseError("El contenido de la licencia no se puede leer.") from exc
    if not isinstance(payload, dict):
        raise LicenseError("El contenido de la licencia no tiene el formato esperado.")
    if payload.get("version") != 1:
        raise LicenseError("La versión de esta licencia no es compatible.")
    if payload.get("plan") not in {"trial", "duration", "unlimited"}:
        raise LicenseError("El tipo de licencia no es compatible.")
    return payload


def _default_data_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") or str(Path.home())
    return Path(root) / "Aetherion"


class LicenseManager:
    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir) if data_dir is not None else _default_data_dir()
        self.state_path = self.data_dir / "license.json"
        self.current_machine_id = machine_fingerprint()

    def _read_state(self) -> dict[str, Any]:
        try:
            value = json.loads(self.state_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise LicenseError("Esta instalación requiere una clave para continuar.") from None
        except (OSError, json.JSONDecodeError) as exc:
            raise LicenseError("No se pudo leer el estado local de la licencia.") from exc
        if not isinstance(value, dict) or not isinstance(value.get("key"), str):
            raise LicenseError("El estado local de la licencia está dañado.")
        return value

    def _write_state(self, state: dict[str, Any]) -> None:
        temporary = self.state_path.with_suffix(".tmp")
        encoded = json.dumps(state, sort_keys=True, indent=2).encode("utf-8")
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with temporary.open("wb") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.state_path)
        except OSError as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise LicenseError("No se pudo guardar la activación local. Revisa los permisos del perfil de usuario.") from exc

    def _validate_payload(self, payload: dict[str, Any], last_seen: Any = None) -> LicenseStatus:
        if payload.get("machine_id") != self.current_machine_id:
            raise LicenseError("Esta clave fue creada para otro equipo.")
        issued_at = _parse_time(payload.get("issued_at"), "issued_at")
        now = _utc_now()
        if now + _CLOCK_SKEW < issued_at:
            raise LicenseError("La fecha del equipo es anterior a la emisión de la licencia.")
        if last_seen is not None:
            previous_time = _parse_time(last_seen, "last_seen")
            if now + _CLOCK_SKEW < previous_time:
                raise LicenseError("El reloj del equipo retrocedió. Corrige la fecha y vuelve a intentarlo.")
        plan = payload["plan"]
        expires_at = None if plan == "unlimited" else _parse_time(payload.get("expires_at"), "expires_at")
        if expires_at is not None and now >= expires_at:
            raise LicenseError("Esta licencia venció. Pega una clave vigente para continuar.")
        return LicenseStatus(
            valid=True,
            message="Licencia activa",
            plan=plan,
            expires_at=expires_at,
            license_id=str(payload.get("license_id", "")),
            machine_id=self.current_machine_id,
        )

    def check(self) -> LicenseStatus:
        state = self._read_state()
        payload = decode_license(state["key"])
        status = self._validate_payload(payload, state.get("last_seen_utc"))
        state["last_seen_utc"] = _isoformat(_utc_now())
        self._write_state(state)
        return status

    def activate(self, token: str) -> LicenseStatus:
        payload = decode_license(token)
        previous_seen: Any = None
        try:
            previous_seen = self._read_state().get("last_seen_utc")
        except LicenseError:
            pass
        status = self._validate_payload(payload, previous_seen)
        self._write_state({"version": 1, "key": token.strip(), "last_seen_utc": _isoformat(_utc_now())})
        return status


# The following helper is used only by the separate administrator utility.
def sign_license(payload: dict[str, Any], private_key: rsa.RSAPrivateKey) -> str:
    payload_bytes = _canonical_payload(payload)
    signature = private_key.sign(
        payload_bytes,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return f"{KEY_PREFIX}.{_b64url_encode(payload_bytes)}.{_b64url_encode(signature)}"
