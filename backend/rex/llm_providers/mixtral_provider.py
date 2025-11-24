"""
Mixtral Provider
Support for Mistral AI's Mixtral models (8x7B, 8x22B)
Highly cost-effective open-source alternative to GPT-4
"""

import logging
from typing import List, Dict, Any, Optional
import os

from .llama_provider import LlamaProvider  # Reuse Llama infrastructure
from .base_provider import ModelInfo, ModelCapability

logger = logging.getLogger(__name__)


class MixtralProvider(LlamaProvider):
    """
    Mixtral provider (extends LlamaProvider since backends are similar).

    Mixtral-8x7B: Matches GPT-3.5, costs ~1/10th
    Mixtral-8x22B: Approaching GPT-4, costs ~1/5th
    """

    def __init__(self, config: Dict[str, Any]):
        # Override models before calling parent init
        super().__init__(config)

        self.models = {
            "mixtral-8x7b": ModelInfo(
                name="mixtral-8x7b",
                provider="mixtral",
                capabilities=[ModelCapability.CHAT, ModelCapability.FINE_TUNING],
                cost_per_1k_input_tokens=0.0006,  # $0.60 per 1M (via Together AI)
                cost_per_1k_output_tokens=0.0006,
                context_window=32768,
                supports_fine_tuning=True,
                supports_local_deployment=True,
            ),
            "mixtral-8x22b": ModelInfo(
                name="mixtral-8x22b",
                provider="mixtral",
                capabilities=[ModelCapability.CHAT, ModelCapability.FINE_TUNING],
                cost_per_1k_input_tokens=0.0012,  # $1.20 per 1M
                cost_per_1k_output_tokens=0.0012,
                context_window=65536,
                supports_fine_tuning=True,
                supports_local_deployment=True,
            ),
        }

    def _get_default_model(self) -> str:
        """Default model is Mixtral-8x7B (best balance of cost/performance)"""
        return "mixtral-8x7b"


# Factory function
def create_mixtral_provider(
    backend: str = "together",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> MixtralProvider:
    """
    Create Mixtral provider instance.

    Args:
        backend: Backend to use (together, replicate, vllm, ollama)
        api_key: API key for cloud backends
        base_url: Base URL for local backends
    """
    return MixtralProvider({
        "backend": backend,
        "api_key": api_key,
        "base_url": base_url,
    })
