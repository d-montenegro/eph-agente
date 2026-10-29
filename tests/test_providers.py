import json

import httpx
import pytest

from eph_agent.providers import (
    Message,
    OpenAICompatibleProvider,
    ProviderAuthError,
    ProviderProfile,
    ProviderRegistry,
    ProviderRegistryError,
    ProviderUnreachable,
    ToolDefinition,
)


def provider(handler, *, model: str = "modelo-1") -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        base_url="http://test/v1",
        model=model,
        api_key="secreto",
        timeout_seconds=5,
        max_retries=0,
        transport=httpx.MockTransport(handler),
    )


def models_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"data": [{"id": "modelo-1"}, {"id": "modelo-2"}]})


async def test_list_models() -> None:
    assert await provider(models_handler).list_models() == ["modelo-1", "modelo-2"]


async def test_health_ok() -> None:
    health = await provider(models_handler).health()

    assert health.ok is True
    assert health.status == "ok"
    assert health.models == ["modelo-1", "modelo-2"]
    assert health.latency_ms >= 0


async def test_health_credencial_invalida() -> None:
    health = await provider(lambda request: httpx.Response(401)).health()

    assert health.ok is False
    assert health.status == "invalid_credentials"


async def test_health_servidor_inalcanzable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sin conexión")

    health = await provider(handler).health()

    assert health.ok is False
    assert health.status == "unreachable"


async def test_health_modelo_inexistente() -> None:
    health = await provider(models_handler, model="otro-modelo").health()

    assert health.ok is False
    assert health.status == "model_not_found"
    assert "otro-modelo" in (health.detail or "")


async def test_complete_with_tools_parsea_argumentos() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call-1",
                                    "type": "function",
                                    "function": {
                                        "name": "ejecutar_sql",
                                        "arguments": json.dumps({"query": "SELECT 1"}),
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
        )

    turn = await provider(handler).complete_with_tools(
        [Message(role="user", content="contá personas")],
        [ToolDefinition(name="ejecutar_sql", description="Ejecuta SQL")],
        model="modelo-1",
        temperature=0,
    )

    assert turn.content is None
    assert len(turn.tool_calls) == 1
    assert turn.tool_calls[0].name == "ejecutar_sql"
    assert turn.tool_calls[0].arguments == {"query": "SELECT 1"}


async def test_list_models_propaga_credencial_invalida() -> None:
    with pytest.raises(ProviderAuthError):
        await provider(lambda request: httpx.Response(403)).list_models()


async def test_error_de_conexion_es_seguro() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sin conexión")

    with pytest.raises(ProviderUnreachable):
        await provider(handler).list_models()


def write_providers(tmp_path, *, mode: str = "local") -> str:
    path = tmp_path / "providers.yml"
    path.write_text(
        json.dumps(
            {
                "mode": mode,
                "allowed_hosts": ["api.permitida.test"],
                "profiles": {
                    "local": {
                        "base_url": "http://127.0.0.1:20128/v1",
                        "model": "auto",
                        "api_key_env": "LOCAL_KEY",
                        "hosted": False,
                    },
                    "remoto": {
                        "base_url": "https://api.permitida.test/v1",
                        "model": "modelo-remoto",
                        "api_key_env": "REMOTE_KEY",
                        "hosted": True,
                    },
                    "otro": {
                        "base_url": "https://otro.test/v1",
                        "model": "modelo-otro",
                        "api_key_env": "OTRO_KEY",
                        "hosted": True,
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return str(path)


def test_registry_local_permite_todos_los_perfiles(tmp_path) -> None:
    registry = ProviderRegistry.from_env(
        {"EPH_PROVIDERS_FILE": write_providers(tmp_path), "EPH_MODE": "local"}
    )

    assert registry.get("local").model == "auto"
    assert registry.get("remoto").base_url == "https://api.permitida.test/v1"


def test_registry_hosted_solo_permite_hosts_de_la_lista(tmp_path) -> None:
    registry = ProviderRegistry.from_env(
        {
            "EPH_PROVIDERS_FILE": write_providers(tmp_path, mode="hosted"),
            "EPH_MODE": "hosted",
            "EPH_ALLOWED_LLM_HOSTS": "api.permitida.test",
        }
    )

    assert registry.get("remoto").name == "remoto"
    with pytest.raises(ProviderRegistryError, match="no está permitido"):
        registry.get("local")
    with pytest.raises(ProviderRegistryError, match="no está permitido"):
        registry.get("otro")


def test_registry_hosted_no_permite_destinos_arbitrarios(tmp_path) -> None:
    registry = ProviderRegistry.from_env(
        {
            "EPH_PROVIDERS_FILE": write_providers(tmp_path, mode="hosted"),
            "EPH_MODE": "hosted",
            "EPH_ALLOWED_LLM_HOSTS": "api.permitida.test",
        }
    )

    with pytest.raises(ProviderRegistryError, match="destinos arbitrarios"):
        registry.create_transient(base_url="http://interno.test/v1", model="x")


def test_registry_nunca_expone_el_valor_de_la_clave(tmp_path) -> None:
    registry = ProviderRegistry.from_env(
        {
            "EPH_PROVIDERS_FILE": write_providers(tmp_path),
            "EPH_MODE": "local",
            "REMOTE_KEY": "clave-super-secreta",
        }
    )

    public = next(item for item in registry.public_profiles() if item["name"] == "remoto")
    assert public["has_api_key"] is True
    assert public["api_key_env"] == "REMOTE_KEY"
    assert "clave-super-secreta" not in json.dumps(registry.public_profiles())


def test_perfil_rechaza_api_mode_desconocido() -> None:
    with pytest.raises(ProviderRegistryError, match="api_mode"):
        ProviderProfile.from_dict(
            "x",
            {"base_url": "http://host/v1", "model": "m", "api_mode": "responses"},
        )
