"""API HTTP mínima sobre las herramientas del agente."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import asdict, replace

from fastapi import Depends, FastAPI, HTTPException

from eph_agent.agent import AgentError, AgentService
from eph_agent.answer import AgentAnswer
from eph_agent.config import DatabaseSettings
from eph_agent.database import (
    DatabaseAdapter,
    DatabaseError,
    QueryExecutionError,
    QueryTimeoutError,
    create_database_adapter,
)
from eph_agent.providers import (
    Message,
    ProviderError,
    ProviderRegistry,
    ProviderRegistryError,
    ToolDefinition,
)
from eph_agent.schemas import (
    AgentAskRequest,
    DescribeTableRequest,
    ExecuteSQLRequest,
    HealthResponse,
    ProviderHealthResponse,
    ProviderProfilePublic,
    ProviderSelectRequest,
    ProvidersResponse,
    ProviderTestRequest,
    QueryResultResponse,
    SchemaResponse,
    TableDescription,
)
from eph_agent.semantic import SemanticLayerError
from eph_agent.sql_guard import SQLGuardError
from eph_agent.tools import describir_tabla, ejecutar_sql

app = FastAPI(title="Agente EPH", version="0.1.0")


def get_settings() -> DatabaseSettings:
    try:
        return DatabaseSettings.from_env()
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


def get_adapter(settings: DatabaseSettings = Depends(get_settings)) -> Iterator[DatabaseAdapter]:
    try:
        adapter = create_database_adapter(settings)
    except DatabaseError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    try:
        yield adapter
    finally:
        adapter.close()


def get_registry() -> ProviderRegistry:
    try:
        return ProviderRegistry.from_env()
    except ProviderRegistryError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/api/health", response_model=HealthResponse)
def health(
    settings: DatabaseSettings = Depends(get_settings),
    adapter: DatabaseAdapter = Depends(get_adapter),
) -> HealthResponse:
    try:
        views = [view["view"] for view in adapter.views()]
    except DatabaseError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return HealthResponse(
        status="ok",
        backend=settings.backend.value,
        dialect=settings.sql_dialect,
        views=views,
    )


@app.get("/api/schema", response_model=SchemaResponse)
def schema(adapter: DatabaseAdapter = Depends(get_adapter)) -> SchemaResponse:
    return SchemaResponse(views=adapter.views())


@app.post("/api/tools/describe-table", response_model=TableDescription)
def describe_table(
    request: DescribeTableRequest,
    adapter: DatabaseAdapter = Depends(get_adapter),
) -> TableDescription:
    try:
        payload = describir_tabla(adapter, request.nombre)
    except SemanticLayerError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return TableDescription(**payload)


@app.post("/api/tools/execute-sql", response_model=QueryResultResponse)
def execute_sql(
    request: ExecuteSQLRequest,
    adapter: DatabaseAdapter = Depends(get_adapter),
) -> QueryResultResponse:
    try:
        result = ejecutar_sql(adapter, request.query)
    except SQLGuardError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except QueryTimeoutError as error:
        raise HTTPException(status_code=408, detail=str(error)) from error
    except QueryExecutionError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except DatabaseError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return QueryResultResponse(
        columns=result.columns,
        rows=result.rows,
        row_count=result.row_count,
        truncated=result.truncated,
        sql=result.sql,
        elapsed_ms=result.elapsed_ms,
    )


@app.get("/api/providers", response_model=ProvidersResponse)
def list_providers(registry: ProviderRegistry = Depends(get_registry)) -> ProvidersResponse:
    return ProvidersResponse(
        mode=registry.mode,
        selected=getattr(app.state, "selected_profile", None),
        profiles=[ProviderProfilePublic(**profile) for profile in registry.public_profiles()],
    )


@app.post("/api/providers/test", response_model=ProviderHealthResponse)
async def test_provider(
    request: ProviderTestRequest,
    registry: ProviderRegistry = Depends(get_registry),
) -> ProviderHealthResponse:
    try:
        if request.profile:
            provider = registry.create(request.profile)
        else:
            if not request.base_url or not request.model:
                raise HTTPException(
                    status_code=400,
                    detail="Indicá un profile o bien base_url y model",
                )
            provider = registry.create_transient(
                base_url=request.base_url,
                model=request.model,
                api_key_env=request.api_key_env,
            )
    except ProviderRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    health = await provider.health()
    if request.check_tools and health.ok:
        try:
            turn = await provider.complete_with_tools(
                [Message(role="user", content="Respondé usando la herramienta ping.")],
                [
                    ToolDefinition(
                        name="ping",
                        description="Herramienta de prueba; no recibe argumentos.",
                        parameters={"type": "object", "properties": {}},
                    )
                ],
                model=provider.model,
                temperature=0.0,
            )
            health = replace(health, tools_supported=bool(turn.tool_calls))
        except ProviderError:
            health = replace(health, tools_supported=False)

    return ProviderHealthResponse(**asdict(health))


@app.post("/api/providers/select", response_model=ProviderProfilePublic)
def select_provider(
    request: ProviderSelectRequest,
    registry: ProviderRegistry = Depends(get_registry),
) -> ProviderProfilePublic:
    try:
        profile = registry.get(request.profile)
    except ProviderRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    app.state.selected_profile = profile.name
    return ProviderProfilePublic(**profile.public(has_api_key=registry.has_api_key(profile)))


@app.post("/api/agent/ask", response_model=AgentAnswer)
async def ask_agent(
    request: AgentAskRequest,
    adapter: DatabaseAdapter = Depends(get_adapter),
    registry: ProviderRegistry = Depends(get_registry),
) -> AgentAnswer:
    selected = request.profile or getattr(app.state, "selected_profile", None)
    try:
        profile = registry.get(selected) if selected else registry.default_profile()
        provider = registry.create(profile.name)
    except ProviderRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    service = AgentService(
        adapter,
        provider,
        model=provider.model,
        profile=profile.name,
    )
    try:
        return await service.ask(request.question)
    except AgentError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except ProviderError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
