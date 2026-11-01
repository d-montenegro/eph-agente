"""API HTTP mínima sobre las herramientas del agente."""

from __future__ import annotations

import os
import secrets
from collections.abc import Iterator
from dataclasses import asdict, replace

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from eph_agent.agent import AgentError, AgentService
from eph_agent.answer import AgentAnswer
from eph_agent.auth import (
    AuthConfigError,
    LoginThrottle,
    UserStore,
    auth_enabled,
    blocked_ips,
)
from eph_agent.config import DatabaseSettings
from eph_agent.database import (
    DatabaseAdapter,
    DatabaseError,
    QueryExecutionError,
    QueryTimeoutError,
    create_database_adapter,
)
from eph_agent.paths import repo_root
from eph_agent.providers import (
    Message,
    ProviderError,
    ProviderProfile,
    ProviderRegistry,
    ProviderRegistryError,
    ToolDefinition,
)
from eph_agent.rate_limit import DailyRequestLimiter
from eph_agent.schemas import (
    AgentAskRequest,
    AuthUser,
    CustomProviderRequest,
    DescribeTableRequest,
    ExecuteSQLRequest,
    HealthResponse,
    LoginRequest,
    ProjectResponse,
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
PROJECT_DOC = repo_root() / "docs" / "proyecto.md"
app.state.custom_profiles = {}
app.state.custom_keys = {}
app.state.selected_profile = None
app.state.query_limiter = None

SESSION_SECRET = os.environ.get("EPH_SESSION_SECRET") or secrets.token_urlsafe(32)
LOGIN_THROTTLE = LoginThrottle(
    max_failures=int(os.environ.get("EPH_LOGIN_MAX_FAILURES", "10")),
    window_seconds=float(os.environ.get("EPH_LOGIN_WINDOW_SECONDS", "300")),
    block_seconds=float(os.environ.get("EPH_LOGIN_BLOCK_SECONDS", "600")),
)
PUBLIC_API_PATHS = {
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/me",
    "/api/health",
}


@app.middleware("http")
async def auth_guard(request: Request, call_next):
    client_ip = request.client.host if request.client else "desconocida"
    if client_ip in blocked_ips():
        return JSONResponse({"detail": "IP bloqueada"}, status_code=403)
    if not auth_enabled():
        return await call_next(request)

    path = request.url.path
    if not path.startswith("/api/") or path in PUBLIC_API_PATHS:
        return await call_next(request)

    username = request.session.get("auth_user")
    if not username:
        return JSONResponse({"detail": "No autenticado"}, status_code=401)
    try:
        store = UserStore.from_env()
    except AuthConfigError as error:
        return JSONResponse({"detail": str(error)}, status_code=503)
    if not store.has_user(username):
        request.session.clear()
        return JSONResponse({"detail": "Sesión inválida"}, status_code=401)
    return await call_next(request)


# Debe quedar por fuera del guard para que request.session exista.
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=os.environ.get("EPH_COOKIE_SECURE", "0") == "1",
)


def get_query_limiter() -> DailyRequestLimiter:
    limiter = getattr(app.state, "query_limiter", None)
    configured = DailyRequestLimiter.from_env().limit
    if limiter is None or limiter.limit != configured:
        limiter = DailyRequestLimiter(configured)
        app.state.query_limiter = limiter
    return limiter


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
        registry = ProviderRegistry.from_env()
    except ProviderRegistryError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    for profile in getattr(app.state, "custom_profiles", {}).values():
        try:
            registry.add_profile(profile)
        except ProviderRegistryError:
            continue
    for name, key in getattr(app.state, "custom_keys", {}).items():
        registry.set_runtime_key(name, key)
    return registry


@app.get("/api/health", response_model=HealthResponse)
def health(
    settings: DatabaseSettings = Depends(get_settings),
    adapter: DatabaseAdapter = Depends(get_adapter),
    registry: ProviderRegistry = Depends(get_registry),
) -> HealthResponse:
    try:
        views = [view["view"] for view in adapter.views()]
    except DatabaseError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    try:
        profile = getattr(app.state, "selected_profile", None) or registry.default_profile().name
    except ProviderRegistryError:
        profile = None
    return HealthResponse(
        status="ok",
        backend=settings.backend.value,
        dialect=settings.sql_dialect,
        views=views,
        profile=profile,
    )


@app.get("/api/project", response_model=ProjectResponse)
def project() -> ProjectResponse:
    if not PROJECT_DOC.exists():
        raise HTTPException(status_code=404, detail="No existe docs/proyecto.md")
    return ProjectResponse(markdown=PROJECT_DOC.read_text(encoding="utf-8"))


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
    try:
        allowed, _remaining = get_query_limiter().consume()
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Se alcanzó el límite diario de consultas de la demo. Probá nuevamente mañana.",
        )
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
        debug=request.debug,
    )
    try:
        return await service.ask(request.question)
    except AgentError as error:
        detail = {"message": str(error), "trace": getattr(error, "trace", None)}
        raise HTTPException(status_code=502, detail=detail) from error
    except ProviderError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.post("/api/providers/custom", response_model=ProviderProfilePublic)
def add_custom_provider(
    request: CustomProviderRequest,
    registry: ProviderRegistry = Depends(get_registry),
) -> ProviderProfilePublic:
    if registry.mode != "local":
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten perfiles personalizados en modo local",
        )
    if request.name in registry.profiles:
        raise HTTPException(status_code=400, detail="Ya existe un perfil con ese nombre")

    try:
        profile = ProviderProfile.from_dict(
            request.name,
            {
                "base_url": request.base_url,
                "model": request.model,
                "api_key_env": request.api_key_env,
                "timeout_seconds": request.timeout_seconds,
                "hosted": False,
            },
        )
    except ProviderRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    app.state.custom_profiles[request.name] = profile
    if request.api_key:
        app.state.custom_keys[request.name] = request.api_key
    registry.add_profile(profile)
    if request.api_key:
        registry.set_runtime_key(request.name, request.api_key)
    return ProviderProfilePublic(**profile.public(has_api_key=registry.has_api_key(profile)))


@app.post("/api/auth/login", response_model=AuthUser)
def login(request: LoginRequest, http_request: Request) -> AuthUser:
    if not auth_enabled():
        raise HTTPException(status_code=400, detail="La autenticación está deshabilitada")
    client_ip = http_request.client.host if http_request.client else "desconocida"
    if LOGIN_THROTTLE.is_blocked(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos fallidos; esperá unos minutos",
        )
    try:
        store = UserStore.from_env()
    except AuthConfigError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    if not store.verify(request.username, request.password):
        LOGIN_THROTTLE.record_failure(client_ip)
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    LOGIN_THROTTLE.reset(client_ip)
    http_request.session["auth_user"] = request.username
    return AuthUser(username=request.username)


@app.get("/api/auth/me", response_model=AuthUser)
def me(http_request: Request) -> AuthUser:
    if not auth_enabled():
        return AuthUser(username="demo")
    username = http_request.session.get("auth_user")
    if not username:
        raise HTTPException(status_code=401, detail="No autenticado")
    return AuthUser(username=username)


@app.post("/api/auth/logout")
def logout(http_request: Request) -> dict[str, bool]:
    http_request.session.clear()
    return {"ok": True}


# El mount va al final para no interceptar las rutas /api registradas después.
WEB_DIST = repo_root() / "web" / "dist"
if WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")
