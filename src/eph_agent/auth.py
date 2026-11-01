"""Autenticación local: usuarios con hash PBKDF2, sesión y bloqueo de IPs."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from eph_agent.paths import repo_root

PBKDF2_ITERATIONS = 260_000
ALGORITHM = "pbkdf2_sha256"


class AuthConfigError(ValueError):
    """La configuración de usuarios no es válida."""


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(
    password: str,
    *,
    iterations: int = PBKDF2_ITERATIONS,
    salt: bytes | None = None,
) -> str:
    if not password:
        raise ValueError("La contraseña no puede estar vacía")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{ALGORITHM}${iterations}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, digest_text = encoded.split("$")
        if algorithm != ALGORITHM:
            return False
        iterations = int(iterations_text)
        salt = _b64decode(salt_text)
        expected = _b64decode(digest_text)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(candidate, expected)
    except (ValueError, TypeError):
        return False


@dataclass(slots=True)
class UserStore:
    users: dict[str, str]

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> UserStore:
        values = os.environ if env is None else env
        raw_path = values.get("EPH_USERS_FILE")
        path = Path(raw_path) if raw_path else repo_root() / "config" / "users.yml"
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except OSError as error:
            raise AuthConfigError(f"No se pudo leer {path}: {error}") from error

        raw_users = data.get("users") if isinstance(data, dict) else None
        if not isinstance(raw_users, dict) or not raw_users:
            raise AuthConfigError(f"{path} debe declarar 'users'")

        users: dict[str, str] = {}
        for username, spec in raw_users.items():
            encoded = spec.get("password_hash") if isinstance(spec, dict) else spec
            if not encoded:
                raise AuthConfigError(f"El usuario {username!r} no tiene password_hash")
            users[str(username)] = str(encoded)
        return cls(users)

    def has_user(self, username: str) -> bool:
        return username in self.users

    def verify(self, username: str, password: str) -> bool:
        encoded = self.users.get(username)
        return bool(encoded and verify_password(password, encoded))


def auth_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return values.get("EPH_AUTH_ENABLED", "0").lower() in {"1", "true", "yes", "on"}


def blocked_ips(env: Mapping[str, str] | None = None) -> frozenset[str]:
    values = os.environ if env is None else env
    return frozenset(
        item.strip() for item in values.get("EPH_BLOCKED_IPS", "").split(",") if item.strip()
    )


@dataclass
class LoginThrottle:
    max_failures: int = 10
    window_seconds: float = 300
    block_seconds: float = 600
    _failures: dict[str, list[float]] = field(default_factory=dict)
    _blocked_until: dict[str, float] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def is_blocked(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            until = self._blocked_until.get(key)
            if until is None:
                return False
            if until <= now:
                self._blocked_until.pop(key, None)
                return False
            return True

    def record_failure(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            attempts = [
                stamp for stamp in self._failures.get(key, []) if now - stamp <= self.window_seconds
            ]
            attempts.append(now)
            if len(attempts) >= self.max_failures:
                self._blocked_until[key] = now + self.block_seconds
                attempts = []
            self._failures[key] = attempts

    def reset(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)
            self._blocked_until.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._failures.clear()
            self._blocked_until.clear()
