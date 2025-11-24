"""
Training Orchestrator
Manages the complete weekly LLM retraining cycle

Flow:
1. Export training data from outcome_labels
2. Format as GPT-4 training examples (JSONL)
3. Upload to OpenAI
4. Start fine-tuning job
5. Monitor progress
6. Register new model in model_registry
7. (Optional) Deploy with A/B test
8. Track performance

This runs weekly via cron job or manual trigger.
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from uuid import UUID
from supabase import Client

from .data_formatter import OutcomeDataFormatter
from .model_trainer import GPT4ModelTrainer
from .model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class TrainingOrchestrator:
    """Orchestrates the complete model training and deployment cycle"""

    def __init__(
        self,
        supabase: Client,
        openai_api_key: Optional[str] = None,
        output_dir: str = "./training_data",
    ):
        self.supabase = supabase
        self.formatter = OutcomeDataFormatter(supabase)
        self.trainer = GPT4ModelTrainer(openai_api_key)
        self.registry = ModelRegistry(supabase)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def run_training_cycle(
        self,
        organization_id: Optional[UUID] = None,
        model_version: Optional[str] = None,
        min_quality_score: float = 0.6,
        deploy_immediately: bool = False,
        ab_test_percentage: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Execute complete training cycle: export → format → train → register → (deploy).

        Args:
            organization_id: Train org-specific model (None = global model)
            model_version: Version string (e.g., "v2.1.0", auto-generated if None)
            min_quality_score: Minimum quality threshold for training examples
            deploy_immediately: Deploy model immediately after training
            ab_test_percentage: If deploying, what % traffic for A/B test

        Returns:
            {
                "status": "success" | "failed",
                "model_id": "ft:gpt-4:...",
                "model_version": "v2.1.0",
                "registry_id": "uuid",
                "training_stats": {...},
                "training_duration_seconds": 1234,
                "deployed": True/False
            }
        """
        cycle_start = datetime.utcnow()

        try:
            logger.info("=" * 80)
            logger.info("Starting LLM Training Cycle")
            logger.info(f"Organization: {organization_id or 'GLOBAL'}")
            logger.info(f"Min quality score: {min_quality_score}")
            logger.info("=" * 80)

            # STEP 1: Check if we have enough training data
            stats = await self.formatter.get_training_stats(
                organization_id=str(organization_id) if organization_id else None
            )

            logger.info(f"Training data stats: {stats}")

            if stats.get("total_examples", 0) < 50:
                raise ValueError(
                    f"Insufficient training data: {stats.get('total_examples', 0)} examples "
                    "(minimum 50 required)"
                )

            # STEP 2: Export and format training data
            logger.info("Step 1/6: Exporting training data...")

            training_file = self.output_dir / f"training_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jsonl"

            examples_count = await self.formatter.export_to_jsonl(
                output_path=str(training_file),
                organization_id=str(organization_id) if organization_id else None,
                min_quality_score=min_quality_score,
                include_negative_examples=True,
            )

            logger.info(f"Exported {examples_count} training examples to {training_file}")

            if examples_count < 50:
                raise ValueError(f"Only {examples_count} examples exported (minimum 50)")

            # STEP 3: Generate model version if not provided
            if not model_version:
                model_version = await self._generate_version()

            logger.info(f"Model version: {model_version}")

            # STEP 4: Upload and train
            logger.info("Step 2/6: Uploading training data to OpenAI...")

            model_suffix = self._generate_suffix(organization_id, model_version)

            training_result = await self.trainer.full_training_cycle(
                training_file_path=str(training_file),
                model_suffix=model_suffix,
                wait_for_completion=True,  # Wait for training to finish
            )

            logger.info(
                f"Training complete! Model: {training_result['model_id']}, "
                f"Status: {training_result['status']}"
            )

            # STEP 5: Register model
            logger.info("Step 3/6: Registering model in registry...")

            training_stats = {
                "training_file_id": training_result["training_file_id"],
                "validation_file_id": training_result.get("validation_file_id"),
                "trained_tokens": training_result.get("trained_tokens"),
                "training_examples_count": examples_count,
                "positive_examples": stats.get("positive_examples"),
                "negative_examples": stats.get("negative_examples"),
                "deals_in_training": stats.get("deals_closed"),
                "model_suffix": model_suffix,
            }

            registry_id = await self.registry.register_model(
                model_id=training_result["model_id"],
                model_version=model_version,
                base_model=self.trainer.base_model,
                fine_tuning_job_id=training_result["job_id"],
                training_stats=training_stats,
                organization_id=organization_id,
                description=f"Model trained on {examples_count} examples from {stats.get('total_examples')} total outcomes",
            )

            logger.info(f"Model registered: {registry_id}")

            # STEP 6: (Optional) Deploy model
            deployed = False
            if deploy_immediately:
                logger.info("Step 4/6: Deploying model...")

                await self._deploy_with_ab_test(
                    new_model_id=registry_id,
                    organization_id=organization_id,
                    variant_traffic=ab_test_percentage,
                )

                deployed = True
                logger.info(f"Model deployed with {ab_test_percentage}% traffic for A/B test")

            # STEP 7: Test model
            logger.info("Step 5/6: Testing model...")

            test_result = await self._test_model(training_result["model_id"])

            logger.info(f"Model test result: {test_result[:200]}...")

            # STEP 8: Calculate cycle duration
            cycle_end = datetime.utcnow()
            duration_seconds = int((cycle_end - cycle_start).total_seconds())

            # Update registry with training duration
            await self.supabase.table("model_registry").update({
                "training_duration_seconds": duration_seconds
            }).eq("id", str(registry_id)).execute()

            logger.info("=" * 80)
            logger.info("Training Cycle Complete!")
            logger.info(f"Model: {training_result['model_id']}")
            logger.info(f"Version: {model_version}")
            logger.info(f"Registry ID: {registry_id}")
            logger.info(f"Duration: {duration_seconds}s ({duration_seconds // 60}m)")
            logger.info(f"Deployed: {deployed}")
            logger.info("=" * 80)

            return {
                "status": "success",
                "model_id": training_result["model_id"],
                "model_version": model_version,
                "registry_id": str(registry_id),
                "job_id": training_result["job_id"],
                "training_stats": training_stats,
                "training_duration_seconds": duration_seconds,
                "deployed": deployed,
                "training_file": str(training_file),
            }

        except Exception as e:
            logger.error(f"Training cycle failed: {e}", exc_info=True)

            return {
                "status": "failed",
                "error": str(e),
                "training_duration_seconds": int((datetime.utcnow() - cycle_start).total_seconds()),
            }

    async def _generate_version(self) -> str:
        """Generate next semantic version (v2.1.0 → v2.2.0)"""
        try:
            # Get latest version
            result = self.supabase.table("model_registry").select("model_version").order(
                "created_at", desc=True
            ).limit(1).execute()

            if not result.data:
                return "v1.0.0"  # First version

            latest_version = result.data[0]["model_version"]

            # Parse version (v2.1.0 → [2, 1, 0])
            parts = latest_version.lstrip("v").split(".")
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

            # Increment minor version (weekly releases)
            minor += 1

            return f"v{major}.{minor}.{patch}"

        except Exception as e:
            logger.error(f"Failed to generate version: {e}", exc_info=True)
            return f"v2.{datetime.utcnow().strftime('%Y%m%d')}.0"

    def _generate_suffix(self, organization_id: Optional[UUID], version: str) -> str:
        """Generate OpenAI model suffix (e.g., 'rekindle-v2-1-0')"""
        version_clean = version.lstrip("v").replace(".", "-")

        if organization_id:
            return f"rekindle-org-{version_clean}"
        else:
            return f"rekindle-{version_clean}"

    async def _deploy_with_ab_test(
        self,
        new_model_id: UUID,
        organization_id: Optional[UUID],
        variant_traffic: float = 10.0,
    ) -> None:
        """Deploy new model with A/B test against current production"""
        try:
            # Get current production model
            current_model = await self.registry.get_latest_deployed_model(organization_id)

            if current_model:
                # Set up A/B test: current (90%) vs new (10%)
                control_traffic = 100.0 - variant_traffic

                await self.registry.setup_ab_test(
                    control_model_id=UUID(current_model["id"]),
                    variant_model_id=new_model_id,
                    control_traffic=control_traffic,
                    variant_traffic=variant_traffic,
                )

                logger.info(
                    f"A/B test: current model ({control_traffic}%) vs "
                    f"new model ({variant_traffic}%)"
                )
            else:
                # No current model, deploy at 100%
                await self.registry.deploy_model(
                    registry_id=new_model_id,
                    traffic_percentage=100.0,
                    ab_test_group="control",
                )

                logger.info("Deployed as first model at 100% traffic")

        except Exception as e:
            logger.error(f"Failed to deploy with A/B test: {e}", exc_info=True)
            raise

    async def _test_model(self, model_id: str) -> str:
        """Test model with sample prompt"""
        try:
            test_prompt = (
                "Write a personalized outreach message with the following requirements:\n\n"
                "**Lead Context:**\n"
                "- Industry: SaaS\n"
                "- Role: VP of Sales\n"
                "- Seniority: Executive\n"
                "- Company size: 150 employees\n"
                "- ICP match: 85%\n\n"
                "**Requirements:**\n"
                "- Framework: PAS (Problem-Agitate-Solution)\n"
                "- Tone: professional\n"
                "- Channel: email\n"
                "- Sequence step: 1\n\n"
                "**Instructions:**\n"
                "- Personalize based on their industry, role, and pain points\n"
                "- Keep it concise (150-200 words)\n"
                "- Focus on value, not features\n"
                "- Include a clear call-to-action"
            )

            system_prompt = (
                "You are an expert B2B sales copywriter. Write highly effective, "
                "personalized outreach messages that generate replies and book meetings."
            )

            result = await self.trainer.test_model(
                model_id=model_id,
                test_prompt=test_prompt,
                system_prompt=system_prompt,
            )

            return result

        except Exception as e:
            logger.error(f"Model test failed: {e}", exc_info=True)
            return f"Test failed: {str(e)}"

    async def schedule_weekly_training(
        self,
        organization_id: Optional[UUID] = None,
        min_quality_score: float = 0.6,
        deploy_immediately: bool = False,
    ) -> Dict[str, Any]:
        """
        Schedule weekly training (call this from cron job).

        This should run every Monday at 2am UTC.
        """
        logger.info("=" * 80)
        logger.info("WEEKLY TRAINING SCHEDULER")
        logger.info(f"Scheduled time: {datetime.utcnow().isoformat()}")
        logger.info("=" * 80)

        return await self.run_training_cycle(
            organization_id=organization_id,
            min_quality_score=min_quality_score,
            deploy_immediately=deploy_immediately,
            ab_test_percentage=10.0,  # Start conservative with 10% A/B test
        )

    async def promote_ab_test_winner(
        self, organization_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Promote A/B test winner to 100% traffic.

        Call this after 1 week of A/B testing to analyze results and promote winner.
        """
        try:
            # Get deployed models
            deployed = await self.registry.get_deployed_models(organization_id)

            if len(deployed) < 2:
                raise ValueError("Need at least 2 deployed models for A/B test")

            # Find control and variant
            control = next((m for m in deployed if m.get("ab_test_group") == "control"), None)
            variant = next((m for m in deployed if m.get("ab_test_group") == "variant_a"), None)

            if not control or not variant:
                raise ValueError("Could not find control and variant models")

            # Compare performance
            control_score = self._calculate_performance_score(control)
            variant_score = self._calculate_performance_score(variant)

            logger.info(f"Control score: {control_score:.4f}")
            logger.info(f"Variant score: {variant_score:.4f}")

            # Determine winner
            if variant_score > control_score:
                winner_id = UUID(variant["id"])
                loser_id = UUID(control["id"])
                winner_name = "variant"
            else:
                winner_id = UUID(control["id"])
                loser_id = UUID(variant["id"])
                winner_name = "control"

            # Promote winner to 100%
            await self.registry.deploy_model(
                registry_id=winner_id,
                traffic_percentage=100.0,
                ab_test_group="control",  # Winner becomes new control
            )

            # Archive loser
            await self.registry.archive_model(loser_id)

            improvement = ((variant_score - control_score) / control_score * 100) if control_score > 0 else 0

            logger.info(
                f"A/B test complete: {winner_name} wins "
                f"({improvement:+.2f}% improvement)"
            )

            return {
                "winner": winner_name,
                "winner_id": str(winner_id),
                "improvement_percentage": improvement,
                "control_score": control_score,
                "variant_score": variant_score,
            }

        except Exception as e:
            logger.error(f"Failed to promote A/B test winner: {e}", exc_info=True)
            raise

    def _calculate_performance_score(self, model: Dict[str, Any]) -> float:
        """
        Calculate weighted performance score.

        Weights:
        - Close rate: 50% (most important)
        - Meeting rate: 30%
        - Reply rate: 20%
        """
        close_rate = model.get("close_rate", 0) or 0
        meeting_rate = model.get("meeting_rate", 0) or 0
        reply_rate = model.get("reply_rate", 0) or 0

        score = (
            close_rate * 0.5 +
            meeting_rate * 0.3 +
            reply_rate * 0.2
        )

        return score


# Factory function
def create_training_orchestrator(
    supabase: Client,
    openai_api_key: Optional[str] = None,
    output_dir: str = "./training_data",
) -> TrainingOrchestrator:
    """Create TrainingOrchestrator instance"""
    return TrainingOrchestrator(supabase, openai_api_key, output_dir)
