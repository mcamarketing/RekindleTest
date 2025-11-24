"""
GPT-4 Model Trainer
Manages the weekly model retraining cycle using OpenAI fine-tuning API

Flow:
1. Export training data (via OutcomeDataFormatter)
2. Upload to OpenAI
3. Start fine-tuning job
4. Monitor progress
5. Deploy new model when ready
6. Track performance in model_registry
"""

import logging
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime
from openai import AsyncOpenAI
from pathlib import Path

logger = logging.getLogger(__name__)


class GPT4ModelTrainer:
    """Manages GPT-4 fine-tuning lifecycle"""

    def __init__(self, openai_api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
        self.base_model = "gpt-4o-2024-08-06"  # Latest GPT-4 with fine-tuning support

    async def upload_training_file(self, file_path: str) -> str:
        """
        Upload training data file to OpenAI.

        Args:
            file_path: Path to JSONL file

        Returns:
            file_id: OpenAI file ID
        """
        try:
            logger.info(f"Uploading training file: {file_path}")

            with open(file_path, "rb") as f:
                response = await self.client.files.create(
                    file=f,
                    purpose="fine-tune"
                )

            file_id = response.id
            logger.info(f"File uploaded: {file_id}")

            return file_id

        except Exception as e:
            logger.error(f"Failed to upload training file: {e}", exc_info=True)
            raise

    async def create_fine_tuning_job(
        self,
        training_file_id: str,
        validation_file_id: Optional[str] = None,
        suffix: Optional[str] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a fine-tuning job.

        Args:
            training_file_id: OpenAI file ID for training data
            validation_file_id: OpenAI file ID for validation data (optional)
            suffix: Model name suffix (e.g., "rekindle-v2")
            hyperparameters: Training hyperparameters

        Returns:
            job_id: OpenAI fine-tuning job ID
        """
        try:
            logger.info(f"Creating fine-tuning job for file {training_file_id}")

            # Default hyperparameters
            if hyperparameters is None:
                hyperparameters = {
                    "n_epochs": 3,  # Number of training epochs
                    "batch_size": "auto",  # Auto-select batch size
                    "learning_rate_multiplier": "auto",  # Auto-select learning rate
                }

            # Create job
            job_params = {
                "training_file": training_file_id,
                "model": self.base_model,
                "hyperparameters": hyperparameters,
            }

            if validation_file_id:
                job_params["validation_file"] = validation_file_id

            if suffix:
                job_params["suffix"] = suffix

            response = await self.client.fine_tuning.jobs.create(**job_params)

            job_id = response.id
            logger.info(f"Fine-tuning job created: {job_id}")

            return job_id

        except Exception as e:
            logger.error(f"Failed to create fine-tuning job: {e}", exc_info=True)
            raise

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of fine-tuning job.

        Returns:
            {
                "id": "ftjob-xxx",
                "status": "validating_files" | "queued" | "running" | "succeeded" | "failed" | "cancelled",
                "fine_tuned_model": "ft:gpt-4:org:suffix:id" (if succeeded),
                "created_at": 1234567890,
                "finished_at": 1234567890,
                "trained_tokens": 50000,
                "error": {...} (if failed)
            }
        """
        try:
            response = await self.client.fine_tuning.jobs.retrieve(job_id)

            status = {
                "id": response.id,
                "status": response.status,
                "model": response.model,
                "fine_tuned_model": response.fine_tuned_model,
                "created_at": response.created_at,
                "finished_at": response.finished_at,
                "trained_tokens": response.trained_tokens,
                "error": response.error,
            }

            return status

        except Exception as e:
            logger.error(f"Failed to get job status: {e}", exc_info=True)
            raise

    async def wait_for_completion(
        self,
        job_id: str,
        poll_interval: int = 60,
        max_wait_time: int = 86400,  # 24 hours
    ) -> Dict[str, Any]:
        """
        Wait for fine-tuning job to complete.

        Args:
            job_id: OpenAI fine-tuning job ID
            poll_interval: How often to check status (seconds)
            max_wait_time: Maximum time to wait (seconds)

        Returns:
            Final job status
        """
        try:
            logger.info(f"Waiting for job {job_id} to complete...")

            start_time = time.time()

            while True:
                # Check if max wait time exceeded
                elapsed = time.time() - start_time
                if elapsed > max_wait_time:
                    raise TimeoutError(
                        f"Fine-tuning job {job_id} did not complete within {max_wait_time}s"
                    )

                # Get current status
                status = await self.get_job_status(job_id)

                logger.info(f"Job {job_id} status: {status['status']}")

                # Check if terminal state
                if status["status"] in ["succeeded", "failed", "cancelled"]:
                    return status

                # Wait before next poll
                time.sleep(poll_interval)

        except Exception as e:
            logger.error(f"Error waiting for job completion: {e}", exc_info=True)
            raise

    async def list_fine_tuned_models(self, limit: int = 10) -> list[Dict[str, Any]]:
        """List all fine-tuned models for this organization"""
        try:
            response = await self.client.fine_tuning.jobs.list(limit=limit)

            models = []
            for job in response.data:
                if job.status == "succeeded" and job.fine_tuned_model:
                    models.append({
                        "model_id": job.fine_tuned_model,
                        "base_model": job.model,
                        "job_id": job.id,
                        "created_at": job.created_at,
                        "finished_at": job.finished_at,
                        "trained_tokens": job.trained_tokens,
                    })

            return models

        except Exception as e:
            logger.error(f"Failed to list fine-tuned models: {e}", exc_info=True)
            return []

    async def test_model(
        self,
        model_id: str,
        test_prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Test a fine-tuned model with a sample prompt.

        Args:
            model_id: Fine-tuned model ID (e.g., "ft:gpt-4:org:suffix:id")
            test_prompt: Test prompt
            system_prompt: System prompt (optional)

        Returns:
            Model response
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": test_prompt})

            response = await self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Failed to test model: {e}", exc_info=True)
            raise

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running fine-tuning job"""
        try:
            await self.client.fine_tuning.jobs.cancel(job_id)
            logger.info(f"Cancelled job {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel job: {e}", exc_info=True)
            return False

    async def delete_file(self, file_id: str) -> bool:
        """Delete a training file from OpenAI"""
        try:
            await self.client.files.delete(file_id)
            logger.info(f"Deleted file {file_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file: {e}", exc_info=True)
            return False

    async def full_training_cycle(
        self,
        training_file_path: str,
        validation_file_path: Optional[str] = None,
        model_suffix: Optional[str] = None,
        wait_for_completion: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute complete training cycle: upload → train → wait → return model.

        Args:
            training_file_path: Path to training JSONL
            validation_file_path: Path to validation JSONL (optional)
            model_suffix: Model name suffix
            wait_for_completion: Wait for job to finish (default: True)

        Returns:
            {
                "job_id": "ftjob-xxx",
                "status": "succeeded",
                "model_id": "ft:gpt-4:org:suffix:id",
                "training_file_id": "file-xxx",
                "validation_file_id": "file-xxx",
                "trained_tokens": 50000,
                "created_at": datetime,
                "finished_at": datetime,
            }
        """
        try:
            logger.info("Starting full training cycle...")

            # Step 1: Upload training file
            training_file_id = await self.upload_training_file(training_file_path)

            # Step 2: Upload validation file (optional)
            validation_file_id = None
            if validation_file_path:
                validation_file_id = await self.upload_training_file(validation_file_path)

            # Step 3: Create fine-tuning job
            job_id = await self.create_fine_tuning_job(
                training_file_id=training_file_id,
                validation_file_id=validation_file_id,
                suffix=model_suffix,
            )

            # Step 4: Wait for completion (optional)
            if wait_for_completion:
                final_status = await self.wait_for_completion(job_id)
            else:
                final_status = await self.get_job_status(job_id)

            # Step 5: Return result
            result = {
                "job_id": job_id,
                "status": final_status["status"],
                "model_id": final_status.get("fine_tuned_model"),
                "training_file_id": training_file_id,
                "validation_file_id": validation_file_id,
                "trained_tokens": final_status.get("trained_tokens"),
                "created_at": datetime.fromtimestamp(final_status["created_at"]),
                "finished_at": (
                    datetime.fromtimestamp(final_status["finished_at"])
                    if final_status.get("finished_at")
                    else None
                ),
            }

            logger.info(
                f"Training cycle complete: {result['status']}, model={result['model_id']}"
            )

            return result

        except Exception as e:
            logger.error(f"Full training cycle failed: {e}", exc_info=True)
            raise


# Factory function
def create_gpt4_model_trainer(openai_api_key: Optional[str] = None) -> GPT4ModelTrainer:
    """Create GPT4ModelTrainer instance"""
    return GPT4ModelTrainer(openai_api_key)
