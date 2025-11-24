"""
Base LLM Provider Interface
Abstract base class for all LLM providers (OpenAI, Llama, Mixtral, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModelCapability(str, Enum):
    """Model capabilities"""
    CHAT = "chat"  # Chat completion
    FINE_TUNING = "fine_tuning"  # Can be fine-tuned
    EMBEDDINGS = "embeddings"  # Can generate embeddings
    SENTIMENT = "sentiment"  # Sentiment analysis
    CLASSIFICATION = "classification"  # Text classification


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str  # Generated text
    model: str  # Model used
    provider: str  # Provider name (openai, llama, mixtral)
    tokens_used: int  # Total tokens used
    cost: float  # Cost in USD
    latency_ms: int  # Response time in milliseconds
    metadata: Dict[str, Any]  # Additional metadata


@dataclass
class ModelInfo:
    """Model information"""
    name: str
    provider: str
    capabilities: List[ModelCapability]
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    context_window: int
    supports_fine_tuning: bool
    supports_local_deployment: bool


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion.

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            model: Model identifier
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    async def fine_tune(
        self,
        training_file_path: str,
        base_model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fine-tune a model.

        Args:
            training_file_path: Path to training data (JSONL)
            base_model: Base model to fine-tune from
            **kwargs: Provider-specific parameters

        Returns:
            Dict with fine-tuning job details
        """
        pass

    @abstractmethod
    async def get_fine_tuning_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of fine-tuning job"""
        pass

    @abstractmethod
    def get_model_info(self, model: str) -> ModelInfo:
        """Get information about a model"""
        pass

    @abstractmethod
    def list_models(self) -> List[ModelInfo]:
        """List available models"""
        pass

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for token usage"""
        model_info = self.get_model_info(model)

        input_cost = (input_tokens / 1000) * model_info.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * model_info.cost_per_1k_output_tokens

        return input_cost + output_cost

    async def sentiment_analysis(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text.

        Default implementation uses chat completion.
        Providers can override for specialized models.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a sentiment analysis expert. Analyze the text and respond "
                    "with JSON: {\"sentiment\": \"positive\"|\"neutral\"|\"negative\", "
                    "\"score\": -1.0 to 1.0, \"confidence\": 0.0 to 1.0}"
                )
            },
            {"role": "user", "content": f"Analyze this text:\n\n{text}"}
        ]

        response = await self.chat_completion(
            messages=messages,
            model=model or self._get_default_model(),
            temperature=0.3,
            max_tokens=100,
        )

        # Parse JSON from response
        import json
        try:
            sentiment_data = json.loads(response.content)
            return sentiment_data
        except json.JSONDecodeError:
            logger.error(f"Failed to parse sentiment response: {response.content}")
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0
            }

    @abstractmethod
    def _get_default_model(self) -> str:
        """Get default model for this provider"""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider_name})"
