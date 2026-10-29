from pathlib import Path

import pytest

from eph_agent.config import DatabaseBackend, DatabaseSettings


def test_defaults_to_local_sqlite() -> None:
    settings = DatabaseSettings.from_env({})

    assert settings.backend is DatabaseBackend.SQLITE
    assert settings.url == "sqlite:///eph.sqlite"
    assert settings.sql_dialect == "sqlite"
    assert settings.is_remote is False


def test_resolves_relative_sqlite_path(tmp_path: Path) -> None:
    settings = DatabaseSettings.from_env(
        {"EPH_DATABASE_BACKEND": "sqlite", "EPH_DATABASE_URL": "sqlite:///data/eph.sqlite"}
    )

    assert settings.sqlite_path(tmp_path) == (tmp_path / "data/eph.sqlite").resolve()


def test_resolves_absolute_sqlite_path() -> None:
    settings = DatabaseSettings.from_env(
        {"EPH_DATABASE_BACKEND": "sqlite", "EPH_DATABASE_URL": "sqlite:////tmp/eph.sqlite"}
    )

    assert settings.sqlite_path(Path("/tmp/project")) == Path("/tmp/eph.sqlite")


def test_default_sqlite_path_is_relative_to_project(tmp_path: Path) -> None:
    settings = DatabaseSettings.from_env({})

    assert settings.sqlite_path(tmp_path) == (tmp_path / "eph.sqlite").resolve()


def test_accepts_postgresql_connection_string() -> None:
    settings = DatabaseSettings.from_env(
        {
            "EPH_DATABASE_BACKEND": "postgresql",
            "EPH_DATABASE_URL": "postgresql://user:secret@example.test/eph",
        }
    )

    assert settings.backend is DatabaseBackend.POSTGRESQL
    assert settings.sql_dialect == "postgres"
    assert settings.is_remote is True


def test_accepts_cloudflare_d1_identifier() -> None:
    settings = DatabaseSettings.from_env(
        {
            "EPH_DATABASE_BACKEND": "cloudflare_d1",
            "EPH_DATABASE_URL": "d1://account-id/database-id",
        }
    )

    assert settings.backend is DatabaseBackend.CLOUDFLARE_D1
    assert settings.sql_dialect == "sqlite"


@pytest.mark.parametrize(
    ("backend", "url"),
    [
        ("sqlite", "postgresql://host/eph"),
        ("postgresql", "sqlite:///eph.sqlite"),
        ("cloudflare_d1", "https://api.cloudflare.com/database"),
        ("desconocido", "sqlite:///eph.sqlite"),
    ],
)
def test_rejects_incompatible_backend_and_url(backend: str, url: str) -> None:
    with pytest.raises(ValueError):
        DatabaseSettings.from_env({"EPH_DATABASE_BACKEND": backend, "EPH_DATABASE_URL": url})
