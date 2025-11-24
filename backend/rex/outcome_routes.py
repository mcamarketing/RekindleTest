"""
Outcome Tracking API Routes
Part of: Flywheel Architecture - Data Capture Pipeline

Provides REST API endpoints for:
- Tracking message outcomes
- Updating delivery/engagement status
- Querying performance metrics
- Exporting training data
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
import logging

from .outcome_tracker import OutcomeTracker, TrainingLabel
from .agent_outcome_integration import AgentOutcomeIntegration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/outcomes", tags=["outcomes"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class MessageSentRequest(BaseModel):
    """Request to track a sent message"""
    organization_id: str
    campaign_id: str
    lead_id: str
    channel: str = Field(..., description="email, linkedin, or sms")
    message_body: str
    agent_decisions: Dict[str, Any]
    subject_line: Optional[str] = None
    sequence_step: int = 1
    lead_context: Optional[Dict[str, Any]] = None


class DeliveryUpdateRequest(BaseModel):
    """Update delivery status"""
    outcome_id: str
    delivered: bool
    delivered_at: Optional[datetime] = None
    bounce_reason: Optional[str] = None


class EngagementUpdateRequest(BaseModel):
    """Update engagement (open/click)"""
    outcome_id: str
    event_type: str = Field(..., description="opened, clicked")
    timestamp: Optional[datetime] = None


class ReplyReceivedRequest(BaseModel):
    """Track reply received"""
    outcome_id: str
    reply_text: str
    replied_at: Optional[datetime] = None


class MeetingBookedRequest(BaseModel):
    """Track meeting booked"""
    outcome_id: str
    booked_at: Optional[datetime] = None


class DealClosedRequest(BaseModel):
    """Track deal closed"""
    outcome_id: str
    deal_value: float
    closed_at: Optional[datetime] = None


class OutcomeResponse(BaseModel):
    """Response after creating/updating outcome"""
    outcome_id: str
    status: str
    message: str


class PerformanceMetrics(BaseModel):
    """Campaign performance metrics"""
    campaign_id: str
    total_sent: int
    delivered: int
    opened: int
    clicked: int
    replied: int
    meetings_booked: int
    deals_closed: int
    total_revenue: float
    delivery_rate: float
    open_rate: float
    reply_rate: float
    meeting_rate: float
    close_rate: float


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_outcome_tracker(supabase=None) -> OutcomeTracker:
    """Dependency injection for OutcomeTracker"""
    from ..crewai_agents.tools.db_tools import SupabaseDB
    if not supabase:
        db = SupabaseDB()
        supabase = db.supabase
    return OutcomeTracker(supabase)


def get_agent_integration(supabase=None) -> AgentOutcomeIntegration:
    """Dependency injection for AgentOutcomeIntegration"""
    from ..crewai_agents.tools.db_tools import SupabaseDB
    import os
    if not supabase:
        db = SupabaseDB()
        supabase = db.supabase
    openai_key = os.getenv("OPENAI_API_KEY")
    return AgentOutcomeIntegration(supabase, openai_key)


# ============================================================================
# ENDPOINTS - TRACKING
# ============================================================================

@router.post("/track/message", response_model=OutcomeResponse)
async def track_message_sent(
    request: MessageSentRequest,
    tracker: OutcomeTracker = Depends(get_outcome_tracker)
):
    """
    Track a message sent to a lead.

    This is called by agents after sending a message to capture:
    - Message content and metadata
    - Agent decisions that led to this message
    - Lead context for pattern learning

    Returns outcome_id for later status updates.
    """
    try:
        outcome_id = await tracker.track_message_sent(
            organization_id=UUID(request.organization_id),
            campaign_id=UUID(request.campaign_id),
            lead_id=UUID(request.lead_id),
            channel=request.channel,
            message_body=request.message_body,
            agent_decisions=request.agent_decisions,
            subject_line=request.subject_line,
            sequence_step=request.sequence_step,
            lead_context=request.lead_context
        )

        return OutcomeResponse(
            outcome_id=str(outcome_id),
            status="success",
            message="Message tracked successfully"
        )
    except Exception as e:
        logger.error(f"Failed to track message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/delivery", response_model=OutcomeResponse)
async def track_delivery(
    request: DeliveryUpdateRequest,
    tracker: OutcomeTracker = Depends(get_outcome_tracker)
):
    """Update delivery status (called by webhooks)"""
    try:
        await tracker.track_delivery(
            outcome_id=UUID(request.outcome_id),
            delivered=request.delivered,
            delivered_at=request.delivered_at,
            bounce_reason=request.bounce_reason
        )

        return OutcomeResponse(
            outcome_id=request.outcome_id,
            status="success",
            message="Delivery status updated"
        )
    except Exception as e:
        logger.error(f"Failed to track delivery: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/engagement", response_model=OutcomeResponse)
async def track_engagement(
    request: EngagementUpdateRequest,
    tracker: OutcomeTracker = Depends(get_outcome_tracker)
):
    """Update engagement (open/click) - called by webhooks"""
    try:
        if request.event_type == "opened":
            await tracker.track_opened(
                outcome_id=UUID(request.outcome_id),
                opened_at=request.timestamp
            )
        elif request.event_type == "clicked":
            await tracker.track_clicked(
                outcome_id=UUID(request.outcome_id),
                clicked_at=request.timestamp
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event_type: {request.event_type}"
            )

        return OutcomeResponse(
            outcome_id=request.outcome_id,
            status="success",
            message=f"Engagement {request.event_type} tracked"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to track engagement: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/reply", response_model=OutcomeResponse)
async def track_reply(
    request: ReplyReceivedRequest,
    integration: AgentOutcomeIntegration = Depends(get_agent_integration),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Track reply received from lead.

    Automatically analyzes sentiment and classifies reply.
    This is critical for training data labeling.
    """
    try:
        # Process reply asynchronously to analyze sentiment
        analysis = await integration.process_reply(
            outcome_id=UUID(request.outcome_id),
            reply_text=request.reply_text,
            replied_at=request.replied_at
        )

        return OutcomeResponse(
            outcome_id=request.outcome_id,
            status="success",
            message=f"Reply tracked (sentiment: {analysis['sentiment_label']})"
        )
    except Exception as e:
        logger.error(f"Failed to track reply: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/meeting", response_model=OutcomeResponse)
async def track_meeting_booked(
    request: MeetingBookedRequest,
    tracker: OutcomeTracker = Depends(get_outcome_tracker)
):
    """Track meeting booked (high-value outcome)"""
    try:
        await tracker.track_meeting_booked(
            outcome_id=UUID(request.outcome_id),
            booked_at=request.booked_at
        )

        return OutcomeResponse(
            outcome_id=request.outcome_id,
            status="success",
            message="Meeting booked tracked"
        )
    except Exception as e:
        logger.error(f"Failed to track meeting: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/deal", response_model=OutcomeResponse)
async def track_deal_closed(
    request: DealClosedRequest,
    tracker: OutcomeTracker = Depends(get_outcome_tracker)
):
    """Track deal closed (highest-value outcome)"""
    try:
        await tracker.track_deal_closed(
            outcome_id=UUID(request.outcome_id),
            deal_value=request.deal_value,
            closed_at=request.closed_at
        )

        return OutcomeResponse(
            outcome_id=request.outcome_id,
            status="success",
            message=f"Deal closed tracked (${request.deal_value})"
        )
    except Exception as e:
        logger.error(f"Failed to track deal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS - ANALYTICS
# ============================================================================

@router.get("/campaign/{campaign_id}/performance", response_model=PerformanceMetrics)
async def get_campaign_performance(
    campaign_id: str,
    tracker: OutcomeTracker = Depends(get_outcome_tracker)
):
    """
    Get performance metrics for a campaign.

    Returns:
    - Counts (sent, delivered, opened, etc.)
    - Rates (delivery %, open %, reply %, etc.)
    - Revenue metrics
    """
    try:
        outcomes = await tracker.get_campaign_outcomes(UUID(campaign_id), limit=10000)

        # Calculate metrics
        total_sent = len(outcomes)
        delivered = sum(1 for o in outcomes if o.get("delivered"))
        opened = sum(1 for o in outcomes if o.get("opened"))
        clicked = sum(1 for o in outcomes if o.get("clicked"))
        replied = sum(1 for o in outcomes if o.get("replied"))
        meetings_booked = sum(1 for o in outcomes if o.get("meeting_booked"))
        deals_closed = sum(1 for o in outcomes if o.get("deal_closed"))
        total_revenue = sum(float(o.get("deal_value", 0)) for o in outcomes if o.get("deal_closed"))

        # Calculate rates
        delivery_rate = delivered / total_sent if total_sent > 0 else 0
        open_rate = opened / total_sent if total_sent > 0 else 0
        reply_rate = replied / total_sent if total_sent > 0 else 0
        meeting_rate = meetings_booked / total_sent if total_sent > 0 else 0
        close_rate = deals_closed / total_sent if total_sent > 0 else 0

        return PerformanceMetrics(
            campaign_id=campaign_id,
            total_sent=total_sent,
            delivered=delivered,
            opened=opened,
            clicked=clicked,
            replied=replied,
            meetings_booked=meetings_booked,
            deals_closed=deals_closed,
            total_revenue=total_revenue,
            delivery_rate=delivery_rate,
            open_rate=open_rate,
            reply_rate=reply_rate,
            meeting_rate=meeting_rate,
            close_rate=close_rate
        )
    except Exception as e:
        logger.error(f"Failed to get campaign performance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-strategies/{campaign_id}")
async def get_agent_strategies(
    campaign_id: str,
    integration: AgentOutcomeIntegration = Depends(get_agent_integration)
):
    """
    Get agent strategy performance breakdown for a campaign.

    Shows which frameworks, tones, and agent decisions
    performed best for this specific campaign.
    """
    try:
        performance = await integration.get_agent_performance(UUID(campaign_id))
        return performance
    except Exception as e:
        logger.error(f"Failed to get agent strategies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/winning-strategies/{organization_id}")
async def get_winning_strategies(
    organization_id: str,
    metric: str = "reply_rate",
    min_samples: int = 10,
    integration: AgentOutcomeIntegration = Depends(get_agent_integration)
):
    """
    Get top-performing strategies across all campaigns for an organization.

    This is what agents use to learn and improve their decisions.

    Args:
        organization_id: Organization to analyze
        metric: What to optimize for (reply_rate, meeting_rate, close_rate)
        min_samples: Minimum messages required to be considered
    """
    try:
        strategies = await integration.get_winning_strategies(
            organization_id=UUID(organization_id),
            metric=metric,
            min_samples=min_samples
        )
        return {"strategies": strategies, "metric": metric}
    except Exception as e:
        logger.error(f"Failed to get winning strategies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS - TRAINING DATA
# ============================================================================

@router.get("/training-data/{organization_id}")
async def get_training_data(
    organization_id: str,
    limit: int = 1000,
    tracker: OutcomeTracker = Depends(get_outcome_tracker)
):
    """
    Get training-ready outcome data for fine-tuning.

    Returns labeled examples ready for GPT-4 fine-tuning pipeline.
    Only includes outcomes that have been labeled and marked for training.
    """
    try:
        data = await tracker.get_training_ready_outcomes(
            organization_id=UUID(organization_id),
            limit=limit
        )

        return {
            "organization_id": organization_id,
            "count": len(data),
            "outcomes": data
        }
    except Exception as e:
        logger.error(f"Failed to get training data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-for-training/{outcome_id}")
async def mark_for_training(
    outcome_id: str,
    label: str,
    weight: float = 1.0,
    tracker: OutcomeTracker = Depends(get_outcome_tracker)
):
    """
    Manually mark an outcome for training (quality control).

    Used by data labeling UI to curate high-quality training examples.
    """
    try:
        # Validate label
        try:
            training_label = TrainingLabel(label)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid label. Must be one of: {[l.value for l in TrainingLabel]}"
            )

        await tracker.mark_for_training(
            outcome_id=UUID(outcome_id),
            training_label=training_label,
            training_weight=weight
        )

        return {
            "outcome_id": outcome_id,
            "status": "success",
            "message": f"Marked for training with label: {label}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark for training: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """Outcome tracking API health check"""
    return {
        "status": "healthy",
        "service": "outcome-tracking",
        "timestamp": datetime.utcnow().isoformat()
    }
