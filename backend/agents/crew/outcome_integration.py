"""
Outcome Integration Mixin for Agents
Part of: Flywheel Architecture - Agent Intelligence Loop

Provides outcome tracking capabilities to all agents.
Agents can track their decisions and outcomes for continuous learning.
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)


class OutcomeTrackingMixin:
    """
    Mixin to add outcome tracking to any agent.

    Usage:
        class MyAgent(BaseAgent, OutcomeTrackingMixin):
            async def send_message(self, lead, message):
                # Send message
                ...

                # Track outcome
                outcome_id = await self.track_message_outcome(
                    organization_id=org_id,
                    campaign_id=campaign_id,
                    lead_id=lead_id,
                    message_body=message,
                    agent_decisions=self.get_decision_log()
                )

                return outcome_id
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._outcome_integration = None
        self._decision_log = {}

    def _get_outcome_integration(self):
        """Lazy load outcome integration"""
        if self._outcome_integration is None:
            try:
                import sys
                import pathlib
                sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
                from rex.agent_outcome_integration import create_agent_outcome_integration
                import os

                self._outcome_integration = create_agent_outcome_integration(
                    self.supabase,
                    os.getenv("OPENAI_API_KEY")
                )
            except Exception as e:
                logger.error(f"Failed to initialize outcome integration: {e}")
                self._outcome_integration = None

        return self._outcome_integration

    def log_decision(self, decision_type: str, decision_data: Dict[str, Any]):
        """
        Log an agent decision for outcome tracking.

        Example:
            self.log_decision('framework_selected', {
                'framework': 'PAS',
                'confidence': 0.85,
                'alternatives': ['AIDA', 'BAF']
            })
        """
        if self.agent_name not in self._decision_log:
            self._decision_log[self.agent_name] = {}

        self._decision_log[self.agent_name][decision_type] = {
            'data': decision_data,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_decision_log(self) -> Dict[str, Any]:
        """Get all logged decisions for this agent"""
        return self._decision_log.copy()

    def clear_decision_log(self):
        """Clear decision log after tracking"""
        self._decision_log = {}

    async def track_message_outcome(
        self,
        organization_id: UUID,
        campaign_id: UUID,
        lead_id: UUID,
        channel: str,
        message_body: str,
        subject_line: Optional[str] = None,
        sequence_step: int = 1,
        lead_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[UUID]:
        """
        Track a message outcome with agent decision context.

        This should be called after a message is sent to capture:
        - Message content
        - Agent decisions that led to this message
        - Lead context for pattern learning

        Returns:
            outcome_id: UUID of created outcome record (or None if tracking fails)
        """
        integration = self._get_outcome_integration()

        if not integration:
            logger.warning(f"{self.agent_name}: Outcome integration not available, skipping tracking")
            return None

        try:
            # Get agent decisions
            agent_decisions = self.get_decision_log()

            # Track message
            outcome_id = await integration.track_agent_message(
                organization_id=organization_id,
                campaign_id=campaign_id,
                lead_id=lead_id,
                channel=channel,
                message_body=message_body,
                agent_decisions=agent_decisions,
                subject_line=subject_line,
                sequence_step=sequence_step,
                lead_context=lead_context
            )

            logger.info(
                f"{self.agent_name}: Tracked outcome {outcome_id} for lead {lead_id}"
            )

            # Clear decision log after tracking
            self.clear_decision_log()

            return outcome_id

        except Exception as e:
            logger.error(f"{self.agent_name}: Failed to track outcome: {e}", exc_info=True)
            return None

    async def get_winning_strategies(
        self,
        organization_id: UUID,
        metric: str = "reply_rate",
        min_samples: int = 10
    ) -> list:
        """
        Get top-performing strategies for this agent.

        This allows agents to learn from past performance and
        optimize their decisions.

        Args:
            organization_id: Organization to analyze
            metric: What to optimize for (reply_rate, meeting_rate, close_rate)
            min_samples: Minimum messages required

        Returns:
            List of winning strategies sorted by performance
        """
        integration = self._get_outcome_integration()

        if not integration:
            logger.warning(f"{self.agent_name}: Outcome integration not available")
            return []

        try:
            strategies = await integration.get_winning_strategies(
                organization_id=organization_id,
                metric=metric,
                min_samples=min_samples
            )

            logger.info(
                f"{self.agent_name}: Retrieved {len(strategies)} winning strategies "
                f"for metric: {metric}"
            )

            return strategies

        except Exception as e:
            logger.error(f"{self.agent_name}: Failed to get winning strategies: {e}", exc_info=True)
            return []

    async def get_campaign_performance(
        self,
        campaign_id: UUID
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a campaign.

        Useful for agents to understand how well their strategies
        are working for a specific campaign.

        Returns:
            Performance breakdown by strategy
        """
        integration = self._get_outcome_integration()

        if not integration:
            logger.warning(f"{self.agent_name}: Outcome integration not available")
            return {}

        try:
            performance = await integration.get_agent_performance(
                campaign_id=campaign_id,
                agent_name=self.agent_name
            )

            logger.info(
                f"{self.agent_name}: Retrieved campaign performance for {campaign_id}"
            )

            return performance

        except Exception as e:
            logger.error(f"{self.agent_name}: Failed to get campaign performance: {e}", exc_info=True)
            return {}


def with_outcome_tracking(agent_class):
    """
    Decorator to add outcome tracking to an agent class.

    Usage:
        @with_outcome_tracking
        class MyAgent(BaseAgent):
            ...
    """
    class TrackedAgent(agent_class, OutcomeTrackingMixin):
        pass

    TrackedAgent.__name__ = agent_class.__name__
    TrackedAgent.__qualname__ = agent_class.__qualname__

    return TrackedAgent
