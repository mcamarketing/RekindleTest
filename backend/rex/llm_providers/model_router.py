"""
Model Router
Intelligent routing between multiple LLM providers based on:
- Cost optimization
- Latency requirements
- Task complexity
- Model performance history

Enables hybrid approach: GPT-4 for complex, Llama/Mixtral for simple
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

from .base_provider import BaseLLMProvider, LLMResponse, ModelInfo

logger = logging.getLogger(__name__)


class RoutingStrategy(str, Enum):
    """Routing strategies"""
    CHEAPEST = "cheapest"  # Always use cheapest model
    FASTEST = "fastest"  # Always use fastest (local) model
    BEST_QUALITY = "best_quality"  # Always use highest quality (GPT-4)
    SMART = "smart"  # Intelligent routing based on task complexity
    AB_TEST = "ab_test"  # A/B test between models


@dataclass
class RoutingRule:
    """Rule for routing decision"""
    condition: str  # "task_type", "complexity", "cost_limit"
    value: Any
    provider: str
    model: str


class ModelRouter:
    """
    Routes LLM requests to optimal provider/model.

    Usage:
        router = ModelRouter(providers=[openai, llama, mixtral])

        # Automatic routing
        response = await router.route(
            messages=[...],
            strategy=RoutingStrategy.SMART
        )

        # Explicit model selection
        response = await router.route(
            messages=[...],
            provider="llama",
            model="llama-3.1-8b"
        )
    """

    def __init__(
        self,
        providers: Dict[str, BaseLLMProvider],
        default_strategy: RoutingStrategy = RoutingStrategy.SMART,
    ):
        self.providers = providers  # {"openai": OpenAIProvider(), "llama": LlamaProvider()}
        self.default_strategy = default_strategy

        # Performance tracking
        self.performance_history = {}  # {model_id: {latency_avg, cost_avg, success_rate}}

        # Routing rules (can be customized)
        self.rules = self._init_default_rules()

    def _init_default_rules(self) -> List[RoutingRule]:
        """Initialize default routing rules"""
        return [
            # Simple tasks → Cheapest model
            RoutingRule(
                condition="task_type",
                value="simple",
                provider="mixtral",
                model="mixtral-8x7b"
            ),
            # Complex tasks → Best quality
            RoutingRule(
                condition="task_type",
                value="complex",
                provider="openai",
                model="gpt-4o"
            ),
            # Sentiment analysis → Fast local model
            RoutingRule(
                condition="task_type",
                value="sentiment",
                provider="llama",
                model="llama-3.1-8b"
            ),
        ]

    async def route(
        self,
        messages: List[Dict[str, str]],
        strategy: Optional[RoutingStrategy] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        task_type: str = "general",
        **kwargs
    ) -> LLMResponse:
        """
        Route request to optimal model.

        Args:
            messages: Chat messages
            strategy: Routing strategy (default: self.default_strategy)
            provider: Explicit provider (bypasses routing)
            model: Explicit model (bypasses routing)
            task_type: Task type hint ("simple", "complex", "sentiment")
            **kwargs: Additional parameters passed to provider

        Returns:
            LLMResponse from selected model
        """
        strategy = strategy or self.default_strategy

        # Explicit selection bypasses routing
        if provider and model:
            return await self._execute(provider, model, messages, **kwargs)

        # Route based on strategy
        if strategy == RoutingStrategy.CHEAPEST:
            provider, model = self._route_cheapest()
        elif strategy == RoutingStrategy.FASTEST:
            provider, model = self._route_fastest()
        elif strategy == RoutingStrategy.BEST_QUALITY:
            provider, model = self._route_best_quality()
        elif strategy == RoutingStrategy.SMART:
            provider, model = self._route_smart(messages, task_type)
        elif strategy == RoutingStrategy.AB_TEST:
            provider, model = self._route_ab_test()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        logger.info(f"Routing to: {provider}/{model} (strategy={strategy})")

        # Execute request
        response = await self._execute(provider, model, messages, **kwargs)

        # Track performance
        self._track_performance(provider, model, response)

        return response

    def _route_cheapest(self) -> tuple[str, str]:
        """Route to cheapest model"""
        cheapest_cost = float("inf")
        cheapest_provider = None
        cheapest_model = None

        for provider_name, provider in self.providers.items():
            for model_info in provider.list_models():
                # Average input/output cost
                avg_cost = (
                    model_info.cost_per_1k_input_tokens + model_info.cost_per_1k_output_tokens
                ) / 2

                if avg_cost < cheapest_cost:
                    cheapest_cost = avg_cost
                    cheapest_provider = provider_name
                    cheapest_model = model_info.name

        return cheapest_provider, cheapest_model

    def _route_fastest(self) -> tuple[str, str]:
        """Route to fastest (local) model"""
        # Prioritize local deployments (vLLM, Ollama)
        for provider_name, provider in self.providers.items():
            for model_info in provider.list_models():
                if model_info.supports_local_deployment:
                    return provider_name, model_info.name

        # Fallback to fastest cloud model
        return self._route_cheapest()

    def _route_best_quality(self) -> tuple[str, str]:
        """Route to highest quality model"""
        # For now, hardcode GPT-4o as best quality
        # In future, track quality from performance history
        if "openai" in self.providers:
            return "openai", "gpt-4o"

        # Fallback to largest available model
        return self._route_largest_model()

    def _route_largest_model(self) -> tuple[str, str]:
        """Route to largest available model"""
        largest_size = 0
        largest_provider = None
        largest_model = None

        for provider_name, provider in self.providers.items():
            for model_info in provider.list_models():
                # Use context window as proxy for model size
                if model_info.context_window > largest_size:
                    largest_size = model_info.context_window
                    largest_provider = provider_name
                    largest_model = model_info.name

        return largest_provider, largest_model

    def _route_smart(self, messages: List[Dict[str, str]], task_type: str) -> tuple[str, str]:
        """
        Intelligent routing based on task complexity.

        Heuristics:
        - Long messages (>1000 chars) → GPT-4 (complex)
        - Short messages (<200 chars) → Mixtral (simple)
        - Sentiment/classification → Llama (fast, cheap)
        - Multi-turn conversation → GPT-4 (context understanding)
        """
        # Task type hints
        if task_type == "sentiment":
            return "llama", "llama-3.1-8b"  # Fast and cheap for classification

        if task_type == "simple":
            return "mixtral", "mixtral-8x7b"  # Good balance

        if task_type == "complex":
            return "openai", "gpt-4o"  # Best quality

        # Analyze message complexity
        total_chars = sum(len(m["content"]) for m in messages)
        num_turns = len([m for m in messages if m["role"] == "user"])

        # Complex: Long messages or multi-turn
        if total_chars > 1000 or num_turns > 3:
            return "openai", "gpt-4o"

        # Simple: Short single message
        if total_chars < 200 and num_turns == 1:
            return "mixtral", "mixtral-8x7b"

        # Medium: Default to cost-effective
        return "llama", "llama-3.1-70b"  # Good performance, lower cost

    def _route_ab_test(self) -> tuple[str, str]:
        """
        A/B test routing: Randomly split traffic between models.

        Useful for comparing model performance in production.
        """
        import random

        # Get all available models
        available = []
        for provider_name, provider in self.providers.items():
            for model_info in provider.list_models():
                available.append((provider_name, model_info.name))

        # Random selection
        return random.choice(available)

    async def _execute(
        self,
        provider_name: str,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Execute request on selected provider/model"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider not found: {provider_name}")

        provider = self.providers[provider_name]

        return await provider.chat_completion(
            messages=messages,
            model=model,
            **kwargs
        )

    def _track_performance(self, provider: str, model: str, response: LLMResponse):
        """Track performance metrics for routing optimization"""
        model_id = f"{provider}/{model}"

        if model_id not in self.performance_history:
            self.performance_history[model_id] = {
                "latency_samples": [],
                "cost_samples": [],
                "success_count": 0,
                "failure_count": 0,
            }

        history = self.performance_history[model_id]
        history["latency_samples"].append(response.latency_ms)
        history["cost_samples"].append(response.cost)
        history["success_count"] += 1

        # Keep only recent samples (last 100)
        if len(history["latency_samples"]) > 100:
            history["latency_samples"] = history["latency_samples"][-100:]
            history["cost_samples"] = history["cost_samples"][-100:]

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all models"""
        report = {}

        for model_id, history in self.performance_history.items():
            if history["latency_samples"]:
                report[model_id] = {
                    "avg_latency_ms": sum(history["latency_samples"]) / len(history["latency_samples"]),
                    "avg_cost": sum(history["cost_samples"]) / len(history["cost_samples"]),
                    "success_rate": (
                        history["success_count"] / (history["success_count"] + history["failure_count"])
                        if history["success_count"] + history["failure_count"] > 0
                        else 0
                    ),
                    "total_requests": history["success_count"] + history["failure_count"],
                }

        return report

    def add_rule(self, rule: RoutingRule):
        """Add custom routing rule"""
        self.rules.append(rule)

    def list_available_models(self) -> Dict[str, List[ModelInfo]]:
        """List all available models across providers"""
        available = {}

        for provider_name, provider in self.providers.items():
            available[provider_name] = provider.list_models()

        return available


# Factory function
def create_model_router(
    providers: Dict[str, BaseLLMProvider],
    default_strategy: RoutingStrategy = RoutingStrategy.SMART,
) -> ModelRouter:
    """
    Create ModelRouter instance.

    Args:
        providers: Dict of provider name → provider instance
        default_strategy: Default routing strategy

    Example:
        router = create_model_router({
            "openai": OpenAIProvider({...}),
            "llama": LlamaProvider({...}),
            "mixtral": MixtralProvider({...}),
        })
    """
    return ModelRouter(providers, default_strategy)
