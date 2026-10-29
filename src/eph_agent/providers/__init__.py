"""Proveedores de modelos compatibles con OpenAI."""

from eph_agent.providers.base import (
    LLMProvider,
    Message,
    ModelInfo,
    ModelTurn,
    ProviderAuthError,
    ProviderError,
    ProviderHealth,
    ProviderUnreachable,
    ToolCall,
    ToolDefinition,
)
from eph_agent.providers.openai_compatible import OpenAICompatibleProvider
from eph_agent.providers.registry import (
    ProviderProfile,
    ProviderRegistry,
    ProviderRegistryError,
)

__all__ = [
    "LLMProvider",
    "Message",
    "ModelInfo",
    "ModelTurn",
    "OpenAICompatibleProvider",
    "ProviderAuthError",
    "ProviderError",
    "ProviderHealth",
    "ProviderProfile",
    "ProviderRegistry",
    "ProviderRegistryError",
    "ProviderUnreachable",
    "ToolCall",
    "ToolDefinition",
]
