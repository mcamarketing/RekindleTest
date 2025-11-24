"""
Model Registry
Tracks all fine-tuned models, their performance, and deployment status

Manages:
- Model versioning (v1.0.0, v1.1.0, v2.0.0)
- A/B testing (traffic routing between models)
- Performance tracking (reply rates, close rates, revenue)
- Model lifecycle (training → ready → deployed → archived)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
from supabase import Client

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Manages model registry and deployment"""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def register_model(
        self,
        model_id: str,
        model_version: str,
        base_model: str,
        fine_tuning_job_id: str,
        training_stats: Dict[str, Any],
        organization_id: Optional[UUID] = None,
        description: Optional[str] = None,
    ) -> UUID:
        """
        Register a new fine-tuned model.

        Args:
            model_id: OpenAI fine-tuned model ID
            model_version: Semantic version (e.g., "v2.1.0")
            base_model: Base model used
            fine_tuning_job_id: OpenAI job ID
            training_stats: Training statistics (examples count, deals, etc.)
            organization_id: If model is org-specific
            description: Model description

        Returns:
            registry_id: UUID of created model_registry record
        """
        try:
            model_data = {
                "model_id": model_id,
                "model_version": model_version,
                "base_model": base_model,
                "fine_tuning_job_id": fine_tuning_job_id,
                "status": "ready",  # Ready for deployment
                "organization_id": str(organization_id) if organization_id else None,
                "is_global": organization_id is None,
                "description": description,
                **training_stats,
            }

            result = self.supabase.table("model_registry").insert(model_data).execute()

            registry_id = result.data[0]["id"]

            logger.info(
                f"Registered model: {model_version} ({model_id}) with registry_id={registry_id}"
            )

            return UUID(registry_id)

        except Exception as e:
            logger.error(f"Failed to register model: {e}", exc_info=True)
            raise

    async def deploy_model(
        self,
        registry_id: UUID,
        traffic_percentage: float = 100.0,
        ab_test_group: Optional[str] = None,
    ) -> None:
        """
        Deploy a model (mark as deployed and route traffic to it).

        Args:
            registry_id: Model registry ID
            traffic_percentage: Percentage of traffic (0-100)
            ab_test_group: A/B test group name (optional)
        """
        try:
            update_data = {
                "status": "deployed",
                "deployed_at": datetime.utcnow().isoformat(),
                "traffic_percentage": traffic_percentage,
            }

            if ab_test_group:
                update_data["ab_test_group"] = ab_test_group

            self.supabase.table("model_registry").update(update_data).eq(
                "id", str(registry_id)
            ).execute()

            logger.info(
                f"Deployed model {registry_id} with {traffic_percentage}% traffic"
            )

        except Exception as e:
            logger.error(f"Failed to deploy model: {e}", exc_info=True)
            raise

    async def archive_model(self, registry_id: UUID) -> None:
        """Archive a model (remove from deployment)"""
        try:
            update_data = {
                "status": "archived",
                "archived_at": datetime.utcnow().isoformat(),
                "traffic_percentage": 0.0,
            }

            self.supabase.table("model_registry").update(update_data).eq(
                "id", str(registry_id)
            ).execute()

            logger.info(f"Archived model {registry_id}")

        except Exception as e:
            logger.error(f"Failed to archive model: {e}", exc_info=True)
            raise

    async def get_deployed_models(
        self, organization_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all currently deployed models.

        Args:
            organization_id: Filter by organization (None = global models)

        Returns:
            List of deployed models sorted by traffic percentage
        """
        try:
            query = (
                self.supabase.table("active_models")
                .select("*")
                .eq("status", "deployed")
            )

            if organization_id:
                query = query.eq("organization_id", str(organization_id))
            else:
                query = query.is_("organization_id", "null")  # Global models only

            result = query.order("traffic_percentage", desc=True).execute()

            return result.data

        except Exception as e:
            logger.error(f"Failed to get deployed models: {e}", exc_info=True)
            return []

    async def update_model_performance(
        self,
        registry_id: UUID,
        messages_sent: int = 0,
        replies: int = 0,
        meetings_booked: int = 0,
        deals_closed: int = 0,
        revenue: float = 0.0,
    ) -> None:
        """
        Update model performance metrics (called periodically).

        Args:
            registry_id: Model registry ID
            messages_sent: Number of messages sent with this model
            replies: Number of replies received
            meetings_booked: Number of meetings booked
            deals_closed: Number of deals closed
            revenue: Total revenue attributed to this model
        """
        try:
            # Get current metrics
            result = self.supabase.table("model_registry").select(
                "total_messages_sent, total_replies, total_meetings_booked, "
                "total_deals_closed, total_revenue"
            ).eq("id", str(registry_id)).execute()

            current = result.data[0] if result.data else {}

            # Calculate new totals
            new_total_messages = current.get("total_messages_sent", 0) + messages_sent
            new_total_replies = current.get("total_replies", 0) + replies
            new_total_meetings = current.get("total_meetings_booked", 0) + meetings_booked
            new_total_deals = current.get("total_deals_closed", 0) + deals_closed
            new_total_revenue = float(current.get("total_revenue", 0)) + revenue

            # Calculate rates
            reply_rate = (
                new_total_replies / new_total_messages if new_total_messages > 0 else 0
            )
            meeting_rate = (
                new_total_meetings / new_total_messages if new_total_messages > 0 else 0
            )
            close_rate = (
                new_total_deals / new_total_messages if new_total_messages > 0 else 0
            )
            avg_revenue_per_message = (
                new_total_revenue / new_total_messages if new_total_messages > 0 else 0
            )

            # Update model registry
            update_data = {
                "total_messages_sent": new_total_messages,
                "total_replies": new_total_replies,
                "total_meetings_booked": new_total_meetings,
                "total_deals_closed": new_total_deals,
                "total_revenue": new_total_revenue,
                "reply_rate": reply_rate,
                "meeting_rate": meeting_rate,
                "close_rate": close_rate,
                "avg_revenue_per_message": avg_revenue_per_message,
            }

            self.supabase.table("model_registry").update(update_data).eq(
                "id", str(registry_id)
            ).execute()

            logger.info(
                f"Updated performance for model {registry_id}: "
                f"{new_total_messages} messages, {reply_rate:.2%} reply rate"
            )

        except Exception as e:
            logger.error(f"Failed to update model performance: {e}", exc_info=True)

    async def compare_to_baseline(
        self, registry_id: UUID, baseline_model_id: UUID
    ) -> Dict[str, float]:
        """
        Compare model performance to baseline.

        Returns:
            {
                "reply_rate_vs_baseline": +15.5,  # % improvement
                "meeting_rate_vs_baseline": +22.3,
                "close_rate_vs_baseline": +18.7
            }
        """
        try:
            # Get both models
            models_result = self.supabase.table("model_registry").select(
                "id, reply_rate, meeting_rate, close_rate"
            ).in_("id", [str(registry_id), str(baseline_model_id)]).execute()

            if len(models_result.data) != 2:
                raise ValueError("Could not find both models")

            # Find which is which
            current = next(m for m in models_result.data if m["id"] == str(registry_id))
            baseline = next(m for m in models_result.data if m["id"] == str(baseline_model_id))

            # Calculate improvements
            def calc_improvement(current_val, baseline_val):
                if baseline_val == 0:
                    return 0
                return ((current_val - baseline_val) / baseline_val) * 100

            comparison = {
                "reply_rate_vs_baseline": calc_improvement(
                    current.get("reply_rate", 0), baseline.get("reply_rate", 0)
                ),
                "meeting_rate_vs_baseline": calc_improvement(
                    current.get("meeting_rate", 0), baseline.get("meeting_rate", 0)
                ),
                "close_rate_vs_baseline": calc_improvement(
                    current.get("close_rate", 0), baseline.get("close_rate", 0)
                ),
            }

            # Update model with comparison
            self.supabase.table("model_registry").update(comparison).eq(
                "id", str(registry_id)
            ).execute()

            return comparison

        except Exception as e:
            logger.error(f"Failed to compare to baseline: {e}", exc_info=True)
            return {}

    async def get_leaderboard(self, min_samples: int = 100) -> List[Dict[str, Any]]:
        """
        Get model performance leaderboard.

        Args:
            min_samples: Minimum messages sent to be included

        Returns:
            Leaderboard sorted by close rate
        """
        try:
            result = (
                self.supabase.table("model_leaderboard")
                .select("*")
                .gte("total_messages_sent", min_samples)
                .execute()
            )

            return result.data

        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}", exc_info=True)
            return []

    async def setup_ab_test(
        self,
        control_model_id: UUID,
        variant_model_id: UUID,
        control_traffic: float = 90.0,
        variant_traffic: float = 10.0,
    ) -> None:
        """
        Set up A/B test between two models.

        Args:
            control_model_id: Control model (current production)
            variant_model_id: Variant model (new model to test)
            control_traffic: Percentage to control (default 90%)
            variant_traffic: Percentage to variant (default 10%)
        """
        try:
            # Deploy control
            await self.deploy_model(
                registry_id=control_model_id,
                traffic_percentage=control_traffic,
                ab_test_group="control",
            )

            # Deploy variant
            await self.deploy_model(
                registry_id=variant_model_id,
                traffic_percentage=variant_traffic,
                ab_test_group="variant_a",
            )

            logger.info(
                f"A/B test configured: control={control_traffic}%, variant={variant_traffic}%"
            )

        except Exception as e:
            logger.error(f"Failed to setup A/B test: {e}", exc_info=True)
            raise

    async def get_model_by_version(self, model_version: str) -> Optional[Dict[str, Any]]:
        """Get model by version string (e.g., "v2.1.0")"""
        try:
            result = (
                self.supabase.table("model_registry")
                .select("*")
                .eq("model_version", model_version)
                .execute()
            )

            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Failed to get model by version: {e}", exc_info=True)
            return None

    async def get_latest_deployed_model(
        self, organization_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Get the most recently deployed model"""
        try:
            query = (
                self.supabase.table("model_registry")
                .select("*")
                .eq("status", "deployed")
            )

            if organization_id:
                query = query.eq("organization_id", str(organization_id))
            else:
                query = query.is_("organization_id", "null")

            result = query.order("deployed_at", desc=True).limit(1).execute()

            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Failed to get latest deployed model: {e}", exc_info=True)
            return None


# Factory function
def create_model_registry(supabase: Client) -> ModelRegistry:
    """Create ModelRegistry instance"""
    return ModelRegistry(supabase)
