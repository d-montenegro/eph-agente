"""Contrato de proveedores de modelos y tipos de mensajes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class ProviderError(RuntimeError):
    """Error de proveedor seguro para mostrar al cliente."""


class ProviderUnreachable(ProviderError):
    """No se pudo conectar con el servidor del modelo."""


class ProviderAuthError(ProviderError):
    """El servidor rechazó la credencial."""


class ModelNotFound(ProviderError):
    """El modelo configurado no existe en el servidor."""


@dataclass(frozen=True, slots=True)
class ModelInfo:
    id: str


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_openai(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Message:
    role: str
    content: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)

    def to_openai(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.tool_call_id:
            payload["tool_call_id"] = self.tool_call_id
        if self.tool_calls:
            payload["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": _json_arguments(call.arguments),
                    },
                }
                for call in self.tool_calls
            ]
        return payload


def _json_arguments(arguments: dict[str, Any]) -> str:
    import json

    return json.dumps(arguments, ensure_ascii=False)


@dataclass(frozen=True, slots=True)
class ModelTurn:
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    ok: bool
    status: str
    latency_ms: float
    models: list[str] = field(default_factory=list)
    detail: str | None = None
    tools_supported: bool | None = None


class LLMProvider(Protocol):
    """Contrato que consume el loop del agente."""

    async def health(self) -> ProviderHealth: ...

    async def list_models(self) -> list[str]: ...

    async def complete_with_tools(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
        *,
        model: str,
        temperature: float,
    ) -> ModelTurn: ...
