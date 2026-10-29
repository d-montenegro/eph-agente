"""Adaptador Cloudflare D1 (experimental, todavía no soportado)."""

from __future__ import annotations

from typing import Any

from eph_agent.database.base import DatabaseError


class D1Adapter:
    """Placeholder explícito: D1 necesita un adaptador HTTP/Worker probado.

    No se marca como soportado hasta pasar el mismo contrato que SQLite y
    PostgreSQL. Falla temprano para no dar una falsa sensación de seguridad.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise DatabaseError(
            "El backend Cloudflare D1 es experimental y todavía no está soportado. "
            "Usá sqlite en local o postgresql en el despliegue."
        )
