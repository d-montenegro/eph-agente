"""Configuración de infraestructura sin acoplar el dominio a un proveedor."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from urllib.parse import urlparse


class DatabaseBackend(StrEnum):
    """Backends previstos para almacenar y consultar los microdatos."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    CLOUDFLARE_D1 = "cloudflare_d1"


@dataclass(frozen=True, slots=True)
class DatabaseSettings:
    """Configuración validada del backend de datos.

    SQLite es el backend local y reproducible. PostgreSQL es el backend remoto
    recomendado. D1 queda modelado desde el inicio, pero necesita un adaptador
    HTTP/Worker separado antes de poder ejecutar consultas.
    """

    backend: DatabaseBackend
    url: str
    readonly: bool = True

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> DatabaseSettings:
        values = os.environ if env is None else env
        raw_backend = values.get("EPH_DATABASE_BACKEND", DatabaseBackend.SQLITE.value)
        try:
            backend = DatabaseBackend(raw_backend)
        except ValueError as exc:
            choices = ", ".join(item.value for item in DatabaseBackend)
            raise ValueError(
                f"EPH_DATABASE_BACKEND debe ser uno de: {choices}; recibido: {raw_backend!r}"
            ) from exc

        default_url = "sqlite:///eph.sqlite"
        url = values.get("EPH_DATABASE_URL", default_url).strip()
        settings = cls(backend=backend, url=url)
        settings.validate()
        return settings

    def validate(self) -> None:
        if not self.url:
            raise ValueError("EPH_DATABASE_URL no puede estar vacío")

        parsed = urlparse(self.url)
        if self.backend is DatabaseBackend.SQLITE:
            if parsed.scheme != "sqlite":
                raise ValueError("El backend sqlite requiere una URL sqlite:///ruta")
            if not parsed.path:
                raise ValueError("La URL SQLite debe incluir la ruta de la base")
            return

        if self.backend is DatabaseBackend.POSTGRESQL:
            if parsed.scheme not in {"postgres", "postgresql"}:
                raise ValueError(
                    "El backend postgresql requiere una URL postgres:// o postgresql://"
                )
            if not parsed.hostname or not parsed.path.strip("/"):
                raise ValueError("La URL PostgreSQL debe incluir host y nombre de base")
            return

        if parsed.scheme != "d1":
            raise ValueError("El backend cloudflare_d1 requiere d1://<account>/<database>")
        if not parsed.hostname or not parsed.path.strip("/"):
            raise ValueError("La URL D1 debe incluir account ID y database ID")

    def sqlite_path(self, project_root: Path | None = None) -> Path:
        if self.backend is not DatabaseBackend.SQLITE:
            raise ValueError("sqlite_path solo está disponible para el backend sqlite")
        raw_path = urlparse(self.url).path
        # Convención SQLite: sqlite:///ruta es relativa al proyecto y
        # sqlite:////ruta es absoluta (urlparse deja dos barras iniciales).
        if raw_path.startswith("//"):
            return Path(raw_path[1:])
        relative = raw_path.lstrip("/")
        if not relative:
            raise ValueError("La URL SQLite debe incluir la ruta de la base")
        root = Path.cwd() if project_root is None else project_root
        return (root / relative).resolve()

    @property
    def sql_dialect(self) -> str:
        if self.backend is DatabaseBackend.POSTGRESQL:
            return "postgres"
        return "sqlite"

    @property
    def is_remote(self) -> bool:
        return self.backend is not DatabaseBackend.SQLITE
