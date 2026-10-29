"""Carga y selección de perfiles de modelos sin acoplar el agente."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from eph_agent.paths import repo_root
from eph_agent.providers.base import ProviderError
from eph_agent.providers.openai_compatible import OpenAICompatibleProvider

REPO_ROOT = repo_root()
DEFAULT_PROVIDERS = REPO_ROOT / "config" / "providers.yml"
EXAMPLE_PROVIDERS = REPO_ROOT / "config" / "providers.example.yml"
VALID_MODES = {"local", "hosted"}
VALID_API_MODES = {"chat_completions"}


class ProviderRegistryError(ValueError):
    """Perfil inexistente, deshabilitado o no permitido en este modo."""


@dataclass(frozen=True, slots=True)
class ProviderProfile:
    name: str
    base_url: str
    model: str
    api_mode: str = "chat_completions"
    api_key_env: str | None = None
    timeout_seconds: float = 30.0
    max_retries: int = 1
    enabled: bool = True
    hosted: bool = False

    @classmethod
    def from_dict(cls, name: str, data: Mapping[str, Any]) -> ProviderProfile:
        if not isinstance(data, Mapping):
            raise ProviderRegistryError(f"El perfil {name!r} debe ser un objeto")
        base_url = str(data.get("base_url") or "").strip()
        model = str(data.get("model") or "").strip()
        if not base_url or not model:
            raise ProviderRegistryError(f"El perfil {name!r} necesita base_url y model")
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ProviderRegistryError(f"El perfil {name!r} tiene una base_url inválida")
        api_mode = str(data.get("api_mode") or "chat_completions")
        if api_mode not in VALID_API_MODES:
            supported = ", ".join(sorted(VALID_API_MODES))
            raise ProviderRegistryError(
                f"El perfil {name!r} usa api_mode {api_mode!r}; soportados: {supported}"
            )
        timeout = float(data.get("timeout_seconds", 30))
        if timeout <= 0:
            raise ProviderRegistryError(f"El perfil {name!r} tiene timeout inválido")
        retries = int(data.get("max_retries", 1))
        if retries < 0:
            raise ProviderRegistryError(f"El perfil {name!r} tiene max_retries inválido")
        return cls(
            name=name,
            base_url=base_url,
            model=model,
            api_mode=api_mode,
            api_key_env=data.get("api_key_env"),
            timeout_seconds=timeout,
            max_retries=retries,
            enabled=bool(data.get("enabled", True)),
            hosted=bool(data.get("hosted", False)),
        )

    def public(self, *, has_api_key: bool) -> dict[str, Any]:
        return {
            "name": self.name,
            "base_url": self.base_url,
            "model": self.model,
            "api_mode": self.api_mode,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "enabled": self.enabled,
            "hosted": self.hosted,
            "api_key_env": self.api_key_env,
            "has_api_key": has_api_key,
        }


class ProviderRegistry:
    """Selecciona perfiles y aplica la lista blanca del modo hosted."""

    def __init__(
        self,
        profiles: Mapping[str, ProviderProfile],
        *,
        mode: str = "local",
        allowed_hosts: frozenset[str] = frozenset(),
        env: Mapping[str, str] | None = None,
    ) -> None:
        if mode not in VALID_MODES:
            raise ProviderRegistryError(f"EPH_MODE debe ser local o hosted; recibido {mode!r}")
        self.profiles = dict(profiles)
        self.mode = mode
        self.allowed_hosts = frozenset(host.lower() for host in allowed_hosts)
        self._env = dict(os.environ) if env is None else dict(env)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> ProviderRegistry:
        values = os.environ if env is None else env
        path = Path(values.get("EPH_PROVIDERS_FILE") or _default_path())
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except OSError as error:
            raise ProviderRegistryError(f"No se pudo leer {path}: {error}") from error
        if not isinstance(data, dict) or not data.get("profiles"):
            raise ProviderRegistryError(f"{path} debe declarar 'profiles'")

        mode = str(values.get("EPH_MODE") or data.get("mode") or "local").lower()
        raw_hosts = values.get("EPH_ALLOWED_LLM_HOSTS")
        if raw_hosts is None:
            allowed = frozenset(str(host) for host in data.get("allowed_hosts") or [])
        else:
            allowed = frozenset(part.strip() for part in raw_hosts.split(",") if part.strip())

        profiles = {
            name: ProviderProfile.from_dict(name, spec) for name, spec in data["profiles"].items()
        }
        return cls(profiles, mode=mode, allowed_hosts=allowed, env=values)

    def is_allowed(self, profile: ProviderProfile) -> bool:
        if self.mode != "hosted":
            return True
        if not profile.hosted:
            return False
        host = (urlparse(profile.base_url).hostname or "").lower()
        return bool(host) and host in self.allowed_hosts

    def get(self, name: str) -> ProviderProfile:
        profile = self.profiles.get(name)
        if profile is None:
            raise ProviderRegistryError(
                f"No existe el perfil {name!r}; disponibles: {', '.join(sorted(self.profiles))}"
            )
        if not profile.enabled:
            raise ProviderRegistryError(f"El perfil {name!r} está deshabilitado")
        if not self.is_allowed(profile):
            raise ProviderRegistryError(f"El perfil {name!r} no está permitido en modo {self.mode}")
        return profile

    def has_api_key(self, profile: ProviderProfile) -> bool:
        return bool(profile.api_key_env and self._env.get(profile.api_key_env))

    def default_profile(self) -> ProviderProfile:
        """Perfil preferido: local si está disponible; si no, el primero permitido."""
        local = self.profiles.get("local")
        if local is not None and local.enabled and self.is_allowed(local):
            return local
        candidates = sorted(
            (
                profile
                for profile in self.profiles.values()
                if profile.enabled and self.is_allowed(profile)
            ),
            key=lambda item: item.name,
        )
        if not candidates:
            raise ProviderRegistryError("No hay ningún perfil de modelo habilitado y permitido")
        return candidates[0]

    def public_profiles(self) -> list[dict[str, Any]]:
        return [
            profile.public(has_api_key=self.has_api_key(profile))
            for profile in sorted(self.profiles.values(), key=lambda item: item.name)
            if self.is_allowed(profile)
        ]

    def create(
        self,
        name: str,
        *,
        transport: Any | None = None,
    ) -> OpenAICompatibleProvider:
        return self._build(self.get(name), transport=transport)

    def create_transient(
        self,
        *,
        base_url: str,
        model: str,
        api_key_env: str | None = None,
        timeout_seconds: float = 15.0,
        transport: Any | None = None,
    ) -> OpenAICompatibleProvider:
        if self.mode == "hosted":
            raise ProviderRegistryError(
                "En modo hosted no se permiten destinos arbitrarios; elegí un perfil permitido"
            )
        profile = ProviderProfile.from_dict(
            "custom",
            {
                "base_url": base_url,
                "model": model,
                "api_key_env": api_key_env,
                "timeout_seconds": timeout_seconds,
                "max_retries": 0,
                "hosted": False,
            },
        )
        return self._build(profile, transport=transport)

    def _build(
        self,
        profile: ProviderProfile,
        *,
        transport: Any | None = None,
    ) -> OpenAICompatibleProvider:
        api_key = self._env.get(profile.api_key_env) if profile.api_key_env else None
        try:
            return OpenAICompatibleProvider(
                base_url=profile.base_url,
                model=profile.model,
                api_key=api_key,
                timeout_seconds=profile.timeout_seconds,
                max_retries=profile.max_retries,
                transport=transport,
            )
        except ProviderError as error:  # pragma: no cover - defensa ante cambios futuros
            raise ProviderRegistryError(str(error)) from error


def _default_path() -> Path:
    return DEFAULT_PROVIDERS if DEFAULT_PROVIDERS.exists() else EXAMPLE_PROVIDERS
