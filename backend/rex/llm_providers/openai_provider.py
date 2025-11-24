"""
OpenAI Provider
Wrapper for OpenAI GPT-4 and fine-tuned models
"""

import logging
import time
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import os

from .base_provider import (
    BaseLLMProvider,
    LLMResponse,
    ModelInfo,
    ModelCapability
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4 provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = AsyncOpenAI(api_key=config.get("api_key") or os.getenv("OPENAI_API_KEY"))

        # Model catalog
        self.models = {
            "gpt-4o": ModelInfo(
                name="gpt-4o",
                provider="openai",
                capabilities=[ModelCapability.CHAT, ModelCapability.FINE_TUNING],
                cost_per_1k_input_tokens=0.0025,  # $2.50 per 1M tokens
                cost_per_1k_output_tokens=0.010,  # $10 per 1M tokens
                context_window=128000,
                supports_fine_tuning=True,
                supports_local_deployment=False,
            ),
            "gpt-4o-mini": ModelInfo(
                name="gpt-4o-mini",
                provider="openai",
                capabilities=[ModelCapability.CHAT, ModelCapability.FINE_TUNING],
                cost_per_1k_input_tokens=0.00015,  # $0.15 per 1M tokens
                cost_per_1k_output_tokens=0.0006,  # $0.60 per 1M tokens
                context_window=128000,
                supports_fine_tuning=True,
                supports_local_deployment=False,
            ),
            "gpt-4": ModelInfo(
                name="gpt-4",
                provider="openai",
                capabilities=[ModelCapability.CHAT],
                cost_per_1k_input_tokens=0.03,  # $30 per 1M tokens
                cost_per_1k_output_tokens=0.06,  # $60 per 1M tokens
                context_window=8192,
                supports_fine_tuning=False,
                supports_local_deployment=False,
            ),
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion using OpenAI"""
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Extract tokens
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            # Calculate cost
            cost = self.calculate_cost(model, input_tokens, output_tokens)

            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                provider="openai",
                tokens_used=total_tokens,
                cost=cost,
                latency_ms=latency_ms,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "finish_reason": response.choices[0].finish_reason,
                }
            )

        except Exception as e:
            logger.error(f"OpenAI chat completion failed: {e}", exc_info=True)
            raise

    async def fine_tune(
        self,
        training_file_path: str,
        base_model: str,
        suffix: Optional[str] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Fine-tune a model using OpenAI"""
        try:
            # Upload training file
            with open(training_file_path, "rb") as f:
                file_response = await self.client.files.create(
                    file=f,
                    purpose="fine-tune"
                )

            file_id = file_response.id

            # Create fine-tuning job
            job_params = {
                "training_file": file_id,
                "model": base_model,
            }

            if suffix:
                job_params["suffix"] = suffix

            if hyperparameters:
                job_params["hyperparameters"] = hyperparameters

            job_response = await self.client.fine_tuning.jobs.create(**job_params)

            return {
                "job_id": job_response.id,
                "status": job_response.status,
                "model": base_model,
                "training_file_id": file_id,
                "created_at": job_response.created_at,
            }

        except Exception as e:
            logger.error(f"OpenAI fine-tuning failed: {e}", exc_info=True)
            raise

    async def get_fine_tuning_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of OpenAI fine-tuning job"""
        try:
            job = await self.client.fine_tuning.jobs.retrieve(job_id)

            return {
                "job_id": job.id,
                "status": job.status,
                "model": job.model,
                "fine_tuned_model": job.fine_tuned_model,
                "created_at": job.created_at,
                "finished_at": job.finished_at,
                "trained_tokens": job.trained_tokens,
                "error": job.error,
            }

        except Exception as e:
            logger.error(f"Failed to get fine-tuning status: {e}", exc_info=True)
            raise

    def get_model_info(self, model: str) -> ModelInfo:
        """Get information about an OpenAI model"""
        # Handle fine-tuned models (format: ft:gpt-4:org:suffix:id)
        if model.startswith("ft:"):
            base_model = model.split(":")[1]
            if base_model in self.models:
                info = self.models[base_model]
                # Fine-tuned models have higher inference cost
                return ModelInfo(
                    name=model,
                    provider="openai",
                    capabilities=info.capabilities,
                    cost_per_1k_input_tokens=info.cost_per_1k_input_tokens * 1.5,
                    cost_per_1k_output_tokens=info.cost_per_1k_output_tokens * 1.5,
                    context_window=info.context_window,
                    supports_fine_tuning=False,  # Can't fine-tune a fine-tuned model
                    supports_local_deployment=False,
                )

        return self.models.get(model, self.models["gpt-4o"])

    def list_models(self) -> List[ModelInfo]:
        """List available OpenAI models"""
        return list(self.models.values())

    def _get_default_model(self) -> str:
        """Default model is gpt-4o-mini (cost-effective)"""
        return "gpt-4o-mini"


# Factory function
def create_openai_provider(api_key: Optional[str] = None) -> OpenAIProvider:
    """Create OpenAI provider instance"""
    return OpenAIProvider({"api_key": api_key})
