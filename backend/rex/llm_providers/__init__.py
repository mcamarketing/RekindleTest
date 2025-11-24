"""
LLM Provider Abstraction Layer
Support for multiple LLM backends: OpenAI GPT-4, Llama-3, Mixtral, Mistral, etc.

This enables:
- Model-agnostic training pipeline
- Cost optimization (switch to cheaper models)
- Hybrid routing (GPT-4 for complex, local models for simple)
- Full ownership and customization with open-source models
- Easy migration path as dataset grows
"""

from .base_provider import BaseLLMProvider, LLMResponse, ModelCapability
from .openai_provider import OpenAIProvider
from .llama_provider import LlamaProvider
from .mixtral_provider import MixtralProvider
from .model_router import ModelRouter, RoutingStrategy

__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "ModelCapability",
    "OpenAIProvider",
    "LlamaProvider",
    "MixtralProvider",
    "ModelRouter",
    "RoutingStrategy",
]
