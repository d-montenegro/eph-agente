"""API HTTP mínima sobre las herramientas del agente."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import Depends, FastAPI, HTTPException

from eph_agent.config import DatabaseSettings
from eph_agent.database import (
    DatabaseAdapter,
    DatabaseError,
    QueryExecutionError,
    QueryTimeoutError,
    create_database_adapter,
)
from eph_agent.schemas import (
    DescribeTableRequest,
    ExecuteSQLRequest,
    HealthResponse,
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
