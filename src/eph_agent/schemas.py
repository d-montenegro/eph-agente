"""Modelos de entrada y salida de las herramientas y la API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DescribeTableRequest(BaseModel):
    nombre: str = Field(min_length=1, description="Nombre de la vista: personas u hogares")


class ExecuteSQLRequest(BaseModel):
    query: str = Field(min_length=1, description="Una única consulta SELECT de lectura")


class ColumnMetadata(BaseModel):
    column: str
    source_column: str | None = None
    description: str
    type: str
    possible_values: list[Any] | None = None
    null_meaning: str | None = None
    universe: str | None = None
    weight: str | None = None
    synonyms: list[str] = Field(default_factory=list)
    notes: str | None = None


class TableDescription(BaseModel):
    view: str
    columns: list[ColumnMetadata]


class ViewSummary(BaseModel):
    view: str
    source_table: str
    description: str
    period: dict[str, int]


class SchemaResponse(BaseModel):
    views: list[ViewSummary]


class QueryResultResponse(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    truncated: bool
    sql: str
    elapsed_ms: float


class HealthResponse(BaseModel):
    status: str
    backend: str
    dialect: str
    views: list[str]


class ProviderProfilePublic(BaseModel):
    name: str
    base_url: str
    model: str
    api_mode: str
    timeout_seconds: float
    max_retries: int
    enabled: bool
    hosted: bool
    api_key_env: str | None = None
    has_api_key: bool


class ProvidersResponse(BaseModel):
    mode: str
    selected: str | None = None
    profiles: list[ProviderProfilePublic]


class ProviderTestRequest(BaseModel):
    profile: str | None = None
    base_url: str | None = None
    model: str | None = None
    api_key_env: str | None = None
    check_tools: bool = False


class ProviderHealthResponse(BaseModel):
    ok: bool
    status: str
    latency_ms: float
    models: list[str] = Field(default_factory=list)
    detail: str | None = None
    tools_supported: bool | None = None


class ProviderSelectRequest(BaseModel):
    profile: str = Field(min_length=1)


class AgentAskRequest(BaseModel):
    question: str = Field(min_length=1)
    profile: str | None = None


class ProjectResponse(BaseModel):
    markdown: str
