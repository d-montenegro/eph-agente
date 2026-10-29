"""Proveedor compatible con la API de OpenAI (``/v1/models`` y chat con tools)."""

from __future__ import annotations

import json
from time import perf_counter
from typing import Any

import httpx

from eph_agent.providers.base import (
    Message,
    ModelTurn,
    ProviderAuthError,
    ProviderError,
    ProviderHealth,
    ProviderUnreachable,
    ToolCall,
    ToolDefinition,
)


class OpenAICompatibleProvider:
    """Cliente mínimo; la clave se resuelve fuera y nunca se registra."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str | None = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 1,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)
        self._api_key = api_key
        self._transport = transport

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout_seconds, transport=self._transport
                ) as client:
                    response = await client.request(
                        method, f"{self.base_url}{path}", headers=self._headers(), **kwargs
                    )
                break
            except (httpx.ConnectError, httpx.TimeoutException) as error:
                last_error = error
                if attempt >= self.max_retries:
                    raise ProviderUnreachable(
                        f"No se pudo conectar con {self.base_url}: {error.__class__.__name__}"
                    ) from error
        else:  # pragma: no cover - el bucle siempre hace break o raise
            raise ProviderUnreachable(f"No se pudo conectar con {self.base_url}") from last_error

        if response.status_code in {401, 403}:
            raise ProviderAuthError("El servidor rechazó la credencial (401/403)")
        if response.status_code >= 400:
            detail = response.text[:200].replace("\n", " ")
            raise ProviderError(f"El servidor respondió {response.status_code}: {detail}")
        return response

    async def list_models(self) -> list[str]:
        response = await self._request("GET", "/models")
        try:
            payload = response.json()
        except json.JSONDecodeError as error:
            raise ProviderError("La respuesta de /models no es JSON válido") from error
        items = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(items, list):
            raise ProviderError("La respuesta de /models no tiene la forma esperada")
        return [item["id"] for item in items if isinstance(item, dict) and "id" in item]

    async def health(self) -> ProviderHealth:
        started = perf_counter()
        try:
            models = await self.list_models()
        except ProviderUnreachable as error:
            return ProviderHealth(False, "unreachable", _elapsed(started), detail=str(error))
        except ProviderAuthError as error:
            return ProviderHealth(
                False, "invalid_credentials", _elapsed(started), detail=str(error)
            )
        except ProviderError as error:
            return ProviderHealth(False, "error", _elapsed(started), detail=str(error))
        latency = _elapsed(started)
        if self.model not in models:
            return ProviderHealth(
                False,
                "model_not_found",
                latency,
                models=models,
                detail=f"El modelo {self.model!r} no aparece en /models",
            )
        return ProviderHealth(True, "ok", latency, models=models)

    async def complete_with_tools(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
        *,
        model: str,
        temperature: float = 0.0,
    ) -> ModelTurn:
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": [message.to_openai() for message in messages],
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = [tool.to_openai() for tool in tools]
            payload["tool_choice"] = "auto"

        response = await self._request("POST", "/chat/completions", json=payload)
        try:
            data = response.json()
            message = data["choices"][0]["message"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as error:
            raise ProviderError(
                "La respuesta de /chat/completions no tiene la forma esperada"
            ) from error

        return ModelTurn(
            content=message.get("content"),
            tool_calls=[_parse_tool_call(raw) for raw in message.get("tool_calls") or []],
        )


def _parse_tool_call(raw: dict[str, Any]) -> ToolCall:
    function = raw.get("function") or {}
    arguments = function.get("arguments") or {}
    if isinstance(arguments, str):
        if not arguments.strip():
            parsed: dict[str, Any] = {}
        else:
            try:
                parsed = json.loads(arguments)
            except json.JSONDecodeError as error:
                raise ProviderError(
                    "El modelo devolvió argumentos de herramienta inválidos"
                ) from error
    else:
        parsed = dict(arguments)
    return ToolCall(id=str(raw.get("id", "")), name=str(function.get("name", "")), arguments=parsed)


def _elapsed(started: float) -> float:
    return round((perf_counter() - started) * 1_000, 2)
