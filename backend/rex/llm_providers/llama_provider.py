"""
Llama Provider
Support for Meta's Llama-3 and Llama-3.1 models
Can be hosted locally (vLLM, Ollama) or via cloud (Replicate, Together AI)
"""

import logging
import time
import json
from typing import List, Dict, Any, Optional
import os

from .base_provider import (
    BaseLLMProvider,
    LLMResponse,
    ModelInfo,
    ModelCapability
)

logger = logging.getLogger(__name__)


class LlamaProvider(BaseLLMProvider):
    """
    Llama-3 provider with multiple backend options:
    - Local: vLLM, Ollama
    - Cloud: Replicate, Together AI, Fireworks AI
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.backend = config.get("backend", "replicate")  # replicate, together, vllm, ollama
        self.api_key = config.get("api_key") or os.getenv(f"{self.backend.upper()}_API_KEY")
        self.base_url = config.get("base_url")  # For local deployments

        # Model catalog
        self.models = {
            "llama-3.1-70b": ModelInfo(
                name="llama-3.1-70b",
                provider="llama",
                capabilities=[ModelCapability.CHAT, ModelCapability.FINE_TUNING],
                cost_per_1k_input_tokens=0.0009,  # $0.90 per 1M (via Together AI)
                cost_per_1k_output_tokens=0.0009,
                context_window=128000,
                supports_fine_tuning=True,
                supports_local_deployment=True,
            ),
            "llama-3.1-8b": ModelInfo(
                name="llama-3.1-8b",
                provider="llama",
                capabilities=[ModelCapability.CHAT, ModelCapability.FINE_TUNING],
                cost_per_1k_input_tokens=0.0002,  # $0.20 per 1M
                cost_per_1k_output_tokens=0.0002,
                context_window=128000,
                supports_fine_tuning=True,
                supports_local_deployment=True,
            ),
            "llama-3-70b": ModelInfo(
                name="llama-3-70b",
                provider="llama",
                capabilities=[ModelCapability.CHAT, ModelCapability.FINE_TUNING],
                cost_per_1k_input_tokens=0.0009,
                cost_per_1k_output_tokens=0.0009,
                context_window=8192,
                supports_fine_tuning=True,
                supports_local_deployment=True,
            ),
        }

        # Initialize backend client
        self._init_backend()

    def _init_backend(self):
        """Initialize backend-specific client"""
        if self.backend == "replicate":
            try:
                import replicate
                self.client = replicate
            except ImportError:
                raise ImportError("Install replicate: pip install replicate")

        elif self.backend == "together":
            try:
                import together
                self.client = together.Together(api_key=self.api_key)
            except ImportError:
                raise ImportError("Install together: pip install together")

        elif self.backend == "vllm":
            try:
                from openai import AsyncOpenAI
                # vLLM exposes OpenAI-compatible API
                self.client = AsyncOpenAI(
                    base_url=self.base_url or "http://localhost:8000/v1",
                    api_key="EMPTY"  # vLLM doesn't require API key
                )
            except ImportError:
                raise ImportError("Install openai: pip install openai")

        elif self.backend == "ollama":
            try:
                import ollama
                self.client = ollama
            except ImportError:
                raise ImportError("Install ollama: pip install ollama")

        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion using Llama"""
        start_time = time.time()

        try:
            if self.backend == "replicate":
                response = await self._chat_replicate(messages, model, temperature, max_tokens)
            elif self.backend == "together":
                response = await self._chat_together(messages, model, temperature, max_tokens)
            elif self.backend == "vllm":
                response = await self._chat_vllm(messages, model, temperature, max_tokens)
            elif self.backend == "ollama":
                response = await self._chat_ollama(messages, model, temperature, max_tokens)
            else:
                raise ValueError(f"Unknown backend: {self.backend}")

            latency_ms = int((time.time() - start_time) * 1000)

            return response._replace(latency_ms=latency_ms)

        except Exception as e:
            logger.error(f"Llama chat completion failed: {e}", exc_info=True)
            raise

    async def _chat_replicate(self, messages, model, temperature, max_tokens) -> LLMResponse:
        """Chat via Replicate"""
        # Replicate format
        prompt = self._messages_to_prompt(messages)

        output = await self.client.async_run(
            f"meta/{model}",
            input={
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )

        # Estimate tokens (roughly)
        content = "".join(output)
        input_tokens = len(prompt) // 4
        output_tokens = len(content) // 4
        total_tokens = input_tokens + output_tokens

        cost = self.calculate_cost(model, input_tokens, output_tokens)

        return LLMResponse(
            content=content,
            model=model,
            provider="llama",
            tokens_used=total_tokens,
            cost=cost,
            latency_ms=0,  # Filled by caller
            metadata={
                "backend": "replicate",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }
        )

    async def _chat_together(self, messages, model, temperature, max_tokens) -> LLMResponse:
        """Chat via Together AI"""
        response = await self.client.chat.completions.create(
            model=f"meta-llama/{model}-Instruct",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        cost = self.calculate_cost(model, input_tokens, output_tokens)

        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            provider="llama",
            tokens_used=total_tokens,
            cost=cost,
            latency_ms=0,
            metadata={
                "backend": "together",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }
        )

    async def _chat_vllm(self, messages, model, temperature, max_tokens) -> LLMResponse:
        """Chat via vLLM (local OpenAI-compatible server)"""
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        # Local deployment = $0 cost
        cost = 0.0

        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            provider="llama",
            tokens_used=total_tokens,
            cost=cost,
            latency_ms=0,
            metadata={
                "backend": "vllm",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "local_deployment": True,
            }
        )

    async def _chat_ollama(self, messages, model, temperature, max_tokens) -> LLMResponse:
        """Chat via Ollama (local)"""
        response = await self.client.chat(
            model=model,
            messages=messages,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        )

        content = response["message"]["content"]

        # Estimate tokens
        input_tokens = sum(len(m["content"]) // 4 for m in messages)
        output_tokens = len(content) // 4
        total_tokens = input_tokens + output_tokens

        # Local = $0 cost
        cost = 0.0

        return LLMResponse(
            content=content,
            model=model,
            provider="llama",
            tokens_used=total_tokens,
            cost=cost,
            latency_ms=0,
            metadata={
                "backend": "ollama",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "local_deployment": True,
            }
        )

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to single prompt string (for Replicate)"""
        prompt_parts = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append("Assistant:")

        return "\n\n".join(prompt_parts)

    async def fine_tune(
        self,
        training_file_path: str,
        base_model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fine-tune Llama model.

        For open-source, fine-tuning is done locally or via platforms like:
        - Together AI (managed fine-tuning)
        - Replicate (managed fine-tuning)
        - Local with LoRA/QLoRA (Hugging Face)
        """
        if self.backend in ["together", "replicate"]:
            # Use managed fine-tuning (similar to OpenAI)
            logger.info(f"Fine-tuning {base_model} via {self.backend}")
            # Implementation depends on platform
            raise NotImplementedError(f"Fine-tuning via {self.backend} not yet implemented")

        else:
            # Local fine-tuning requires more setup
            logger.info(f"Local fine-tuning for {base_model}")
            logger.info("Use Hugging Face Transformers + LoRA for local fine-tuning")
            raise NotImplementedError("Local fine-tuning requires Hugging Face integration")

    async def get_fine_tuning_status(self, job_id: str) -> Dict[str, Any]:
        """Get fine-tuning job status"""
        raise NotImplementedError("Fine-tuning status for Llama provider")

    def get_model_info(self, model: str) -> ModelInfo:
        """Get Llama model info"""
        return self.models.get(model, self.models["llama-3.1-8b"])

    def list_models(self) -> List[ModelInfo]:
        """List available Llama models"""
        return list(self.models.values())

    def _get_default_model(self) -> str:
        """Default model is Llama-3.1-8B (fastest, cheapest)"""
        return "llama-3.1-8b"


# Factory function
def create_llama_provider(
    backend: str = "replicate",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> LlamaProvider:
    """
    Create Llama provider instance.

    Args:
        backend: Backend to use (replicate, together, vllm, ollama)
        api_key: API key for cloud backends
        base_url: Base URL for local backends (vLLM)
    """
    return LlamaProvider({
        "backend": backend,
        "api_key": api_key,
        "base_url": base_url,
    })
