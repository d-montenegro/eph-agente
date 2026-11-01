from datetime import UTC, datetime, timedelta

import pytest

from eph_agent.rate_limit import DailyRequestLimiter


def test_bloquea_al_superar_el_limite() -> None:
    limiter = DailyRequestLimiter(2)
    now = datetime(2026, 10, 31, tzinfo=UTC)

    assert limiter.consume(now) == (True, 1)
    assert limiter.consume(now) == (True, 0)
    assert limiter.consume(now) == (False, 0)


def test_reinicia_el_contador_al_dia_siguiente() -> None:
    limiter = DailyRequestLimiter(1)
    now = datetime(2026, 10, 31, 23, 59, tzinfo=UTC)

    assert limiter.consume(now)[0] is True
    assert limiter.consume(now)[0] is False
    assert limiter.consume(now + timedelta(minutes=2)) == (True, 0)


def test_cero_desactiva_el_limite() -> None:
    limiter = DailyRequestLimiter(0)
    assert limiter.consume() == (True, -1)


def test_rechaza_configuracion_invalida(monkeypatch) -> None:
    monkeypatch.setenv("EPH_DAILY_QUERY_LIMIT", "muchas")
    with pytest.raises(ValueError, match="entero no negativo"):
        DailyRequestLimiter.from_env()
