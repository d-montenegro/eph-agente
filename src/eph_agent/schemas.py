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
