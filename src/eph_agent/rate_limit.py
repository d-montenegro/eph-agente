"""Límite diario simple para proteger el presupuesto de la demo."""

from __future__ import annotations

import os
from datetime import UTC, date, datetime
from threading import Lock


class DailyRequestLimiter:
    """Contador en memoria que se reinicia cada día UTC."""

    def __init__(self, limit: int) -> None:
        if limit < 0:
            raise ValueError("El límite diario no puede ser negativo")
        self.limit = limit
        self._day: date | None = None
        self._count = 0
        self._lock = Lock()

    @classmethod
    def from_env(cls) -> DailyRequestLimiter:
        raw = os.environ.get("EPH_DAILY_QUERY_LIMIT", "20")
        try:
            return cls(int(raw))
        except ValueError as error:
            raise ValueError("EPH_DAILY_QUERY_LIMIT debe ser un entero no negativo") from error

    def consume(self, now: datetime | None = None) -> tuple[bool, int]:
        """Consume una solicitud y devuelve (permitida, restantes). Cero desactiva el límite."""
        if self.limit == 0:
            return True, -1
        current_day = (now or datetime.now(UTC)).date()
        with self._lock:
            if self._day != current_day:
                self._day = current_day
                self._count = 0
            if self._count >= self.limit:
                return False, 0
            self._count += 1
            return True, self.limit - self._count
