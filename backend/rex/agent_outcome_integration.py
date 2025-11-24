"""
Agent-Outcome Integration
Part of: Flywheel Architecture - Agent Intelligence Loop

Integrates outcome tracking with Rex agent workflows:
- Captures agent decisions when messages are sent
- Updates outcomes when replies are received
- Feeds learning back into agent strategies

This layer sits between agents and the outcome tracker,
ensuring every agent decision → outcome chain is captured for training.
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from supabase import Client

from .outcome_tracker import OutcomeTracker
from .sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)


class AgentOutcomeIntegration:
    """
    Integration layer between Rex agents and outcome tracking.

    Usage in agent workflows:
        # In PersonalizerAgent after message is personalized
        integration = AgentOutcomeIntegration(supabase)

        outcome_id = await integration.track_agent_message(
            organization_id=org_id,
            campaign_id=campaign_id,
            lead_id=lead_id,
            message_body=personalized_message,
            agent_decisions={
                'PersonalizerAgent': {
                    'framework': 'PAS',
                    'tone': 'professional',
                    'personalization_applied': ['first_name', 'company', 'pain_point']
                },
                'CopywriterAgent': {
                    'subject_line': subject,
                    'hooks_used': ['curiosity', 'social_proof']
                }
            },
            lead_context={...}
        )

        # Store outcome_id with message for later tracking
    """

    def __init__(self, supabase: Client, openai_api_key: Optional[str] = None):
        self.tracker = OutcomeTracker(supabase)
        self.sentiment_analyzer = SentimentAnalyzer(openai_api_key)
        self.supabase = supabase

    async def track_agent_message(
        self,
        organization_id: UUID,
        campaign_id: UUID,
        lead_id: UUID,
        channel: str,
        message_body: str,
        agent_decisions: Dict[str, Any],
        subject_line: Optional[str] = None,
        sequence_step: int = 1,
        lead_context: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """
        Track a message sent by agents and capture all decision context.

        This is the main entry point for capturing agent decisions.

        Args:
            organization_id: Organization sending message
            campaign_id: Campaign this message belongs to
            lead_id: Lead receiving message
            channel: 'email', 'linkedin', or 'sms'
            message_body: The final message text
            agent_decisions: Dict of all agent decisions that went into this message
                Example:
                {
                    'PersonalizerAgent': {
                        'framework': 'PAS',
                        'tone': 'professional',
                        'personalization_applied': ['first_name', 'company']
                    },
                    'CopywriterAgent': {
                        'subject_line': 'Transform your sales process',
                        'hooks_used': ['curiosity', 'social_proof'],
                        'cta': 'book_meeting'
                    },
                    'DeliverabilityAgent': {
                        'domain_selected': 'team@rekindle.io',
                        'send_time': '2025-01-23T14:30:00Z',
                        'warmup_score': 0.85
                    }
                }
            subject_line: Email subject (if channel is email)
            sequence_step: Position in sequence (1, 2, 3...)
            lead_context: Lead metadata for pattern learning

        Returns:
            outcome_id: UUID of created outcome_label record
        """
        try:
            # Extract framework and tone from agent decisions
            framework = None
            tone = None

            if 'PersonalizerAgent' in agent_decisions:
                framework = agent_decisions['PersonalizerAgent'].get('framework')
                tone = agent_decisions['PersonalizerAgent'].get('tone')

            # Get ICP score if available
            icp_score = None
            if 'ICPIntelligenceAgent' in agent_decisions:
                icp_score = agent_decisions['ICPIntelligenceAgent'].get('icp_score')
            elif lead_context and 'icp_score' in lead_context:
                icp_score = lead_context['icp_score']

            # Track message with outcome tracker
            outcome_id = await self.tracker.track_message_sent(
                organization_id=organization_id,
                campaign_id=campaign_id,
                lead_id=lead_id,
                channel=channel,
                message_body=message_body,
                agent_decisions=agent_decisions,  # Full decision log
                subject_line=subject_line,
                framework=framework,
                tone=tone,
                sequence_step=sequence_step,
                lead_context=lead_context,
                icp_score=icp_score,
            )

            logger.info(
                f"Tracked agent message: outcome_id={outcome_id}, "
                f"agents={list(agent_decisions.keys())}, framework={framework}"
            )

            return outcome_id

        except Exception as e:
            logger.error(f"Failed to track agent message: {e}", exc_info=True)
            raise

    async def process_reply(
        self,
        outcome_id: UUID,
        reply_text: str,
        replied_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Process a lead reply: analyze sentiment and update outcome.

        Args:
            outcome_id: ID of outcome_label to update
            reply_text: The lead's reply text
            replied_at: When reply was received

        Returns:
            Sentiment analysis results
        """
        try:
            # Get original message context for better analysis
            outcome = await self.supabase.table("outcome_labels").select(
                "message_body, subject_line, lead_industry, lead_role"
            ).eq("id", str(outcome_id)).execute()

            original_message = None
            context = None

            if outcome.data:
                outcome_data = outcome.data[0]
                original_message = outcome_data.get("message_body")
                context = {
                    "industry": outcome_data.get("lead_industry"),
                    "role": outcome_data.get("lead_role"),
                }

            # Analyze reply sentiment
            analysis = await self.sentiment_analyzer.analyze_reply(
                reply_text=reply_text,
                original_message=original_message,
                context=context,
            )

            # Update outcome with sentiment analysis
            await self.tracker.track_reply(
                outcome_id=outcome_id,
                reply_text=reply_text,
                replied_at=replied_at,
                sentiment_score=analysis["sentiment_score"],
                sentiment_label=analysis["sentiment_label"],
                objection_type=(
                    analysis["objection_type"]
                    if analysis["objection_detected"]
                    else None
                ),
                interest_signal=analysis["interest_signal"],
            )

            logger.info(
                f"Processed reply for outcome_id={outcome_id}: "
                f"sentiment={analysis['sentiment_label']}, interest={analysis['interest_signal']}"
            )

            return analysis

        except Exception as e:
            logger.error(f"Failed to process reply: {e}", exc_info=True)
            raise

    async def get_agent_performance(
        self, campaign_id: UUID, agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for agent decisions in a campaign.

        Useful for agents to learn from their past decisions.

        Args:
            campaign_id: Campaign to analyze
            agent_name: Specific agent (None = all agents)

        Returns:
            Performance breakdown by agent strategy
        """
        try:
            # Get all outcomes for campaign
            outcomes = await self.tracker.get_campaign_outcomes(campaign_id, limit=1000)

            # Analyze by agent strategy
            strategy_performance = {}

            for outcome in outcomes:
                agent_decisions = outcome.get("agent_decisions", {})

                if agent_name and agent_name not in agent_decisions:
                    continue

                # Get strategy key (e.g., framework, tone, etc.)
                framework = outcome.get("framework", "unknown")
                tone = outcome.get("tone", "unknown")
                strategy_key = f"{framework}_{tone}"

                if strategy_key not in strategy_performance:
                    strategy_performance[strategy_key] = {
                        "total_sent": 0,
                        "delivered": 0,
                        "opened": 0,
                        "replied": 0,
                        "positive_replies": 0,
                        "meetings_booked": 0,
                        "deals_closed": 0,
                        "total_revenue": 0.0,
                        "framework": framework,
                        "tone": tone,
                    }

                stats = strategy_performance[strategy_key]
                stats["total_sent"] += 1

                if outcome.get("delivered"):
                    stats["delivered"] += 1
                if outcome.get("opened"):
                    stats["opened"] += 1
                if outcome.get("replied"):
                    stats["replied"] += 1
                if outcome.get("reply_sentiment_score", 0) > 0.3:
                    stats["positive_replies"] += 1
                if outcome.get("meeting_booked"):
                    stats["meetings_booked"] += 1
                if outcome.get("deal_closed"):
                    stats["deals_closed"] += 1
                    stats["total_revenue"] += float(outcome.get("deal_value", 0))

            # Calculate rates
            for strategy_key, stats in strategy_performance.items():
                sent = stats["total_sent"]
                if sent > 0:
                    stats["delivery_rate"] = stats["delivered"] / sent
                    stats["open_rate"] = stats["opened"] / sent
                    stats["reply_rate"] = stats["replied"] / sent
                    stats["positive_reply_rate"] = stats["positive_replies"] / sent
                    stats["meeting_rate"] = stats["meetings_booked"] / sent
                    stats["close_rate"] = stats["deals_closed"] / sent
                    stats["avg_deal_value"] = (
                        stats["total_revenue"] / stats["deals_closed"]
                        if stats["deals_closed"] > 0
                        else 0
                    )

            return {
                "campaign_id": str(campaign_id),
                "agent_name": agent_name or "all",
                "total_outcomes": len(outcomes),
                "strategy_performance": strategy_performance,
            }

        except Exception as e:
            logger.error(f"Failed to get agent performance: {e}", exc_info=True)
            return {}

    async def get_winning_strategies(
        self,
        organization_id: UUID,
        metric: str = "reply_rate",
        min_samples: int = 10,
    ) -> list[Dict[str, Any]]:
        """
        Get top-performing strategies across all campaigns for an organization.

        This is what agents use to learn and improve.

        Args:
            organization_id: Organization to analyze
            metric: What to optimize for ('reply_rate', 'meeting_rate', 'close_rate')
            min_samples: Minimum number of messages required to be considered

        Returns:
            List of winning strategies sorted by performance
        """
        try:
            # Query all outcomes for organization
            outcomes = await self.supabase.table("outcome_labels").select("*").eq(
                "organization_id", str(organization_id)
            ).execute()

            # Group by strategy
            strategy_stats = {}

            for outcome in outcomes.data:
                framework = outcome.get("framework", "unknown")
                tone = outcome.get("tone", "unknown")
                industry = outcome.get("lead_industry", "unknown")

                # Strategy key includes industry for better learning
                strategy_key = f"{framework}_{tone}_{industry}"

                if strategy_key not in strategy_stats:
                    strategy_stats[strategy_key] = {
                        "framework": framework,
                        "tone": tone,
                        "industry": industry,
                        "total": 0,
                        "replied": 0,
                        "meetings": 0,
                        "deals": 0,
                        "revenue": 0.0,
                    }

                stats = strategy_stats[strategy_key]
                stats["total"] += 1

                if outcome.get("replied"):
                    stats["replied"] += 1
                if outcome.get("meeting_booked"):
                    stats["meetings"] += 1
                if outcome.get("deal_closed"):
                    stats["deals"] += 1
                    stats["revenue"] += float(outcome.get("deal_value", 0))

            # Calculate rates and filter by min_samples
            winning_strategies = []

            for strategy_key, stats in strategy_stats.items():
                if stats["total"] < min_samples:
                    continue

                stats["reply_rate"] = stats["replied"] / stats["total"]
                stats["meeting_rate"] = stats["meetings"] / stats["total"]
                stats["close_rate"] = stats["deals"] / stats["total"]
                stats["avg_revenue"] = (
                    stats["revenue"] / stats["deals"] if stats["deals"] > 0 else 0
                )

                winning_strategies.append(stats)

            # Sort by chosen metric
            winning_strategies.sort(key=lambda x: x.get(metric, 0), reverse=True)

            logger.info(
                f"Found {len(winning_strategies)} winning strategies for org {organization_id}"
            )

            return winning_strategies[:10]  # Top 10

        except Exception as e:
            logger.error(f"Failed to get winning strategies: {e}", exc_info=True)
            return []


# Factory function
def create_agent_outcome_integration(
    supabase: Client, openai_api_key: Optional[str] = None
) -> AgentOutcomeIntegration:
    """Create AgentOutcomeIntegration instance"""
    return AgentOutcomeIntegration(supabase, openai_api_key)
