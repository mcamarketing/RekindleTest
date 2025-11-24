"""
Outcome Tracker - Data Capture for LLM Training Pipeline
Part of: Flywheel Architecture - Proprietary LLM Brain Loop

Purpose:
- Track every message → outcome chain
- Capture agent decisions and their results
- Feed training data to GPT-4 fine-tuning pipeline

Usage:
    tracker = OutcomeTracker(supabase_client)

    # When message is sent
    outcome_id = await tracker.track_message_sent(
        organization_id=org_id,
        campaign_id=campaign_id,
        lead_id=lead_id,
        message_body=message,
        agent_decisions=agent_log
    )

    # When reply received
    await tracker.track_reply(
        outcome_id=outcome_id,
        reply_text=reply,
        replied_at=datetime.now()
    )

    # When deal closed
    await tracker.track_deal_closed(
        outcome_id=outcome_id,
        deal_value=15000,
        closed_at=datetime.now()
    )
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID
from supabase import Client
from enum import Enum

logger = logging.getLogger(__name__)


class TrainingLabel(str, Enum):
    """Classification for training examples"""
    POSITIVE = "positive_example"  # High engagement, meeting booked, or deal closed
    NEGATIVE = "negative_example"  # Bounced, unsubscribed, or negative reply
    NEUTRAL = "neutral"  # Delivered but no strong signal


class OutcomeTracker:
    """Tracks message outcomes for LLM training pipeline"""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def track_message_sent(
        self,
        organization_id: UUID,
        campaign_id: UUID,
        lead_id: UUID,
        channel: str,
        message_body: str,
        agent_decisions: Dict[str, Any],
        subject_line: Optional[str] = None,
        framework: Optional[str] = None,
        tone: Optional[str] = None,
        sequence_step: int = 1,
        lead_context: Optional[Dict[str, Any]] = None,
        icp_score: Optional[float] = None,
    ) -> UUID:
        """
        Track a sent message and create outcome label entry.

        Args:
            organization_id: Organization sending the message
            campaign_id: Campaign this message belongs to
            lead_id: Lead receiving the message
            channel: 'email', 'linkedin', or 'sms'
            message_body: The actual message text
            agent_decisions: JSON log of all agent decisions (PersonalizerAgent, CopywriterAgent, etc.)
            subject_line: Email subject (if channel is email)
            framework: Copywriting framework used (PAS, AIDA, etc.)
            tone: Tone used (professional, casual, etc.)
            sequence_step: Which step in the sequence (1, 2, 3, etc.)
            lead_context: Industry, role, seniority, company size
            icp_score: Ideal customer profile match score (0.0-1.0)

        Returns:
            UUID of created outcome_label record
        """
        try:
            outcome_data = {
                "organization_id": str(organization_id),
                "campaign_id": str(campaign_id),
                "lead_id": str(lead_id),
                "channel": channel,
                "sequence_step": sequence_step,
                "subject_line": subject_line,
                "message_body": message_body,
                "framework": framework,
                "tone": tone,
                "agent_decisions": agent_decisions,
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "delivered": False,  # Will be updated via webhook
                "icp_score": icp_score,
            }

            # Add lead context if provided
            if lead_context:
                outcome_data.update({
                    "lead_industry": lead_context.get("industry"),
                    "lead_role": lead_context.get("role"),
                    "lead_seniority": lead_context.get("seniority"),
                    "company_size": lead_context.get("company_size"),
                    "company_revenue_range": lead_context.get("revenue_range"),
                    "icp_factors": lead_context.get("icp_factors"),
                })

            result = self.supabase.table("outcome_labels").insert(outcome_data).execute()

            outcome_id = result.data[0]["id"]
            logger.info(
                f"Tracked message sent: outcome_id={outcome_id}, "
                f"campaign_id={campaign_id}, lead_id={lead_id}, channel={channel}"
            )

            return UUID(outcome_id)

        except Exception as e:
            logger.error(f"Failed to track message sent: {e}", exc_info=True)
            raise

    async def track_delivery(
        self,
        outcome_id: UUID,
        delivered: bool,
        delivered_at: Optional[datetime] = None,
        bounce_reason: Optional[str] = None,
    ) -> None:
        """Track message delivery status"""
        try:
            update_data = {
                "delivered": delivered,
                "bounced": not delivered,
            }

            if delivered and delivered_at:
                update_data["delivered_at"] = delivered_at.isoformat()

            if bounce_reason:
                update_data["bounce_reason"] = bounce_reason
                update_data["training_label"] = TrainingLabel.NEGATIVE
                update_data["training_weight"] = 0.5  # Low weight for bounces

            self.supabase.table("outcome_labels").update(update_data).eq(
                "id", str(outcome_id)
            ).execute()

            logger.info(f"Tracked delivery: outcome_id={outcome_id}, delivered={delivered}")

        except Exception as e:
            logger.error(f"Failed to track delivery: {e}", exc_info=True)

    async def track_opened(
        self,
        outcome_id: UUID,
        opened_at: Optional[datetime] = None,
    ) -> None:
        """Track email/message opened"""
        try:
            update_data = {
                "opened": True,
                "opened_at": (opened_at or datetime.now(timezone.utc)).isoformat(),
            }

            # Increment open count
            result = self.supabase.table("outcome_labels").select("open_count").eq(
                "id", str(outcome_id)
            ).execute()

            current_count = result.data[0].get("open_count", 0) if result.data else 0
            update_data["open_count"] = current_count + 1

            self.supabase.table("outcome_labels").update(update_data).eq(
                "id", str(outcome_id)
            ).execute()

            logger.info(f"Tracked open: outcome_id={outcome_id}")

        except Exception as e:
            logger.error(f"Failed to track open: {e}", exc_info=True)

    async def track_clicked(
        self,
        outcome_id: UUID,
        clicked_at: Optional[datetime] = None,
    ) -> None:
        """Track link clicked in message"""
        try:
            update_data = {
                "clicked": True,
                "clicked_at": (clicked_at or datetime.now(timezone.utc)).isoformat(),
            }

            # Increment click count
            result = self.supabase.table("outcome_labels").select("click_count").eq(
                "id", str(outcome_id)
            ).execute()

            current_count = result.data[0].get("click_count", 0) if result.data else 0
            update_data["click_count"] = current_count + 1

            self.supabase.table("outcome_labels").update(update_data).eq(
                "id", str(outcome_id)
            ).execute()

            logger.info(f"Tracked click: outcome_id={outcome_id}")

        except Exception as e:
            logger.error(f"Failed to track click: {e}", exc_info=True)

    async def track_reply(
        self,
        outcome_id: UUID,
        reply_text: str,
        replied_at: Optional[datetime] = None,
        sentiment_score: Optional[float] = None,
        sentiment_label: Optional[str] = None,
        objection_type: Optional[str] = None,
        interest_signal: bool = False,
    ) -> None:
        """
        Track reply received and classify sentiment.

        Args:
            outcome_id: ID of outcome_label to update
            reply_text: The reply text
            replied_at: When reply was received
            sentiment_score: Sentiment score from -1 (negative) to 1 (positive)
            sentiment_label: 'positive', 'neutral', or 'negative'
            objection_type: If objection detected: 'price', 'timing', 'not_interested', etc.
            interest_signal: True if reply shows interest
        """
        try:
            update_data = {
                "replied": True,
                "replied_at": (replied_at or datetime.now(timezone.utc)).isoformat(),
                "reply_text": reply_text,
                "reply_sentiment_score": sentiment_score,
                "reply_sentiment_label": sentiment_label,
                "objection_detected": objection_type is not None,
                "objection_type": objection_type,
                "interest_signal": interest_signal,
            }

            # Determine training label based on reply
            if interest_signal or (sentiment_score and sentiment_score > 0.5):
                update_data["training_label"] = TrainingLabel.POSITIVE
                update_data["training_weight"] = 3.0  # Higher weight for interested replies
            elif objection_type or (sentiment_score and sentiment_score < -0.3):
                update_data["training_label"] = TrainingLabel.NEGATIVE
                update_data["training_weight"] = 2.0  # Learn from objections
            else:
                update_data["training_label"] = TrainingLabel.NEUTRAL
                update_data["training_weight"] = 1.0

            self.supabase.table("outcome_labels").update(update_data).eq(
                "id", str(outcome_id)
            ).execute()

            logger.info(
                f"Tracked reply: outcome_id={outcome_id}, "
                f"sentiment={sentiment_label}, interest={interest_signal}"
            )

        except Exception as e:
            logger.error(f"Failed to track reply: {e}", exc_info=True)

    async def track_meeting_booked(
        self,
        outcome_id: UUID,
        booked_at: Optional[datetime] = None,
    ) -> None:
        """Track meeting booked"""
        try:
            update_data = {
                "meeting_booked": True,
                "meeting_booked_at": (booked_at or datetime.now(timezone.utc)).isoformat(),
                "training_label": TrainingLabel.POSITIVE,
                "training_weight": 5.0,  # High weight for meetings
            }

            self.supabase.table("outcome_labels").update(update_data).eq(
                "id", str(outcome_id)
            ).execute()

            logger.info(f"Tracked meeting booked: outcome_id={outcome_id}")

        except Exception as e:
            logger.error(f"Failed to track meeting booked: {e}", exc_info=True)

    async def track_meeting_completed(
        self,
        outcome_id: UUID,
        completed_at: Optional[datetime] = None,
        no_show: bool = False,
    ) -> None:
        """Track meeting completion or no-show"""
        try:
            update_data = {
                "meeting_completed": not no_show,
                "meeting_no_show": no_show,
            }

            if not no_show:
                update_data["meeting_completed_at"] = (
                    completed_at or datetime.now(timezone.utc)
                ).isoformat()
                update_data["training_weight"] = 7.0  # Even higher weight for completed meetings

            self.supabase.table("outcome_labels").update(update_data).eq(
                "id", str(outcome_id)
            ).execute()

            logger.info(
                f"Tracked meeting completion: outcome_id={outcome_id}, no_show={no_show}"
            )

        except Exception as e:
            logger.error(f"Failed to track meeting completion: {e}", exc_info=True)

    async def track_deal_closed(
        self,
        outcome_id: UUID,
        deal_value: float,
        closed_at: Optional[datetime] = None,
        opportunity_created_at: Optional[datetime] = None,
    ) -> None:
        """
        Track deal closed (highest value outcome).

        Args:
            outcome_id: ID of outcome_label to update
            deal_value: Deal value in dollars
            closed_at: When deal was closed
            opportunity_created_at: When opportunity was first created
        """
        try:
            # Calculate time to close if we have opportunity creation date
            time_to_close_days = None
            if opportunity_created_at and closed_at:
                delta = closed_at - opportunity_created_at
                time_to_close_days = delta.days

            update_data = {
                "deal_closed": True,
                "deal_closed_at": (closed_at or datetime.now(timezone.utc)).isoformat(),
                "deal_value": deal_value,
                "time_to_close_days": time_to_close_days,
                "training_label": TrainingLabel.POSITIVE,
                "training_weight": 10.0,  # Maximum weight for closed deals
                "included_in_training": True,  # Automatically include closed deals
            }

            if opportunity_created_at:
                update_data["opportunity_created"] = True
                update_data["opportunity_created_at"] = opportunity_created_at.isoformat()
                update_data["opportunity_value"] = deal_value

            self.supabase.table("outcome_labels").update(update_data).eq(
                "id", str(outcome_id)
            ).execute()

            logger.info(
                f"Tracked deal closed: outcome_id={outcome_id}, "
                f"value=${deal_value}, time_to_close={time_to_close_days} days"
            )

        except Exception as e:
            logger.error(f"Failed to track deal closed: {e}", exc_info=True)

    async def track_deal_lost(
        self,
        outcome_id: UUID,
        lost_reason: str,
    ) -> None:
        """Track deal lost"""
        try:
            update_data = {
                "deal_lost": True,
                "deal_lost_reason": lost_reason,
                "training_label": TrainingLabel.NEGATIVE,
                "training_weight": 3.0,  # Learn from lost deals
            }

            self.supabase.table("outcome_labels").update(update_data).eq(
                "id", str(outcome_id)
            ).execute()

            logger.info(f"Tracked deal lost: outcome_id={outcome_id}, reason={lost_reason}")

        except Exception as e:
            logger.error(f"Failed to track deal lost: {e}", exc_info=True)

    async def get_outcome_by_message_id(self, message_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve outcome label by message ID"""
        try:
            result = self.supabase.table("outcome_labels").select("*").eq(
                "message_id", str(message_id)
            ).execute()

            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Failed to get outcome by message_id: {e}", exc_info=True)
            return None

    async def get_campaign_outcomes(
        self, campaign_id: UUID, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all outcomes for a campaign"""
        try:
            result = (
                self.supabase.table("outcome_labels")
                .select("*")
                .eq("campaign_id", str(campaign_id))
                .order("sent_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data

        except Exception as e:
            logger.error(f"Failed to get campaign outcomes: {e}", exc_info=True)
            return []

    async def get_training_ready_outcomes(
        self, organization_id: Optional[UUID] = None, limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get outcomes ready for training (high-quality labeled examples).

        Args:
            organization_id: Filter by organization (None = all)
            limit: Maximum number of outcomes to return

        Returns:
            List of outcome labels ready for GPT-4 fine-tuning
        """
        try:
            query = (
                self.supabase.table("training_ready_outcomes")
                .select("*")
                .eq("included_in_training", True)
            )

            if organization_id:
                query = query.eq("organization_id", str(organization_id))

            result = query.order("created_at", desc=True).limit(limit).execute()

            return result.data

        except Exception as e:
            logger.error(f"Failed to get training-ready outcomes: {e}", exc_info=True)
            return []

    async def mark_for_training(
        self, outcome_id: UUID, training_label: TrainingLabel, training_weight: float = 1.0
    ) -> None:
        """Mark an outcome as ready for training (manual curation)"""
        try:
            update_data = {
                "included_in_training": True,
                "training_label": training_label,
                "training_weight": training_weight,
                "labeled_at": datetime.now(timezone.utc).isoformat(),
            }

            self.supabase.table("outcome_labels").update(update_data).eq(
                "id", str(outcome_id)
            ).execute()

            logger.info(
                f"Marked for training: outcome_id={outcome_id}, label={training_label}"
            )

        except Exception as e:
            logger.error(f"Failed to mark for training: {e}", exc_info=True)


# Utility function to create tracker instance
def create_outcome_tracker(supabase: Client) -> OutcomeTracker:
    """Factory function to create OutcomeTracker instance"""
    return OutcomeTracker(supabase)
