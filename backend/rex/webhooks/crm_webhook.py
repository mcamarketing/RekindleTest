"""
CRM Webhook Handler
Captures revenue outcomes from CRM systems (HubSpot, Salesforce, Pipedrive, etc.)

Events tracked:
- opportunity_created: New deal/opportunity created
- deal_closed_won: Deal closed successfully
- deal_closed_lost: Deal lost
- meeting_completed: Meeting/demo completed

Generic webhook format - adapt to your CRM:
{
    "event": "deal.closed_won",
    "deal_id": "123",
    "deal_value": 15000,
    "closed_at": "2025-01-23T10:00:00Z",
    "contact_email": "lead@example.com",
    "outcome_id": "uuid"  // Pass this when creating CRM deal
}
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client
from ..outcome_tracker import OutcomeTracker
import os
import hmac
import hashlib

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Webhook secret for verification (set in your CRM)
CRM_WEBHOOK_SECRET = os.getenv("CRM_WEBHOOK_SECRET", "")


class CRMDealEvent(BaseModel):
    """Generic CRM deal event"""
    event: str  # 'opportunity.created', 'deal.closed_won', 'deal.closed_lost'
    deal_id: str
    deal_value: Optional[float] = None
    contact_email: Optional[str] = None
    outcome_id: Optional[str] = None  # Link to outcome_labels
    lead_id: Optional[str] = None  # Fallback if no outcome_id
    campaign_id: Optional[str] = None
    closed_at: Optional[str] = None
    created_at: Optional[str] = None
    lost_reason: Optional[str] = None
    pipeline_stage: Optional[str] = None


class CRMMeetingEvent(BaseModel):
    """Meeting/demo event"""
    event: str  # 'meeting.completed', 'meeting.no_show'
    meeting_id: str
    contact_email: str
    outcome_id: Optional[str] = None
    completed_at: Optional[str] = None
    no_show: bool = False


def verify_crm_signature(payload: bytes, signature: str) -> bool:
    """
    Verify CRM webhook signature.

    Adjust this based on your CRM's signature method:
    - HubSpot uses SHA256 HMAC
    - Salesforce uses custom header
    - Pipedrive uses user/pass
    """
    if not CRM_WEBHOOK_SECRET:
        logger.warning("CRM_WEBHOOK_SECRET not set, skipping verification")
        return True

    expected_signature = hmac.new(
        CRM_WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


@router.post("/crm/deals")
async def crm_deal_webhook(
    request: Request,
    x_crm_signature: str = Header(None),
):
    """
    Handle CRM deal events (opportunity created, won, lost).

    Example payload from HubSpot:
    {
        "event": "deal.propertyChange",
        "dealId": 12345,
        "properties": {
            "dealstage": "closedwon",
            "amount": 15000,
            "closedate": "2025-01-23"
        },
        "associatedContacts": ["lead@example.com"]
    }

    We normalize this to our standard format.
    """
    try:
        body = await request.body()

        # Verify signature
        if x_crm_signature:
            if not verify_crm_signature(body, x_crm_signature):
                logger.error("Invalid CRM webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse event
        event_data: Dict[str, Any] = await request.json()

        # Normalize CRM-specific format to our standard
        normalized_event = normalize_crm_event(event_data)

        if not normalized_event:
            logger.warning("Could not normalize CRM event")
            return {"status": "ignored", "reason": "unknown_format"}

        event = CRMDealEvent(**normalized_event)

        # Initialize tracker
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        tracker = OutcomeTracker(supabase)

        # Find outcome_id if not provided
        outcome_id = event.outcome_id
        if not outcome_id and event.lead_id:
            outcome_id = await find_outcome_by_lead(supabase, event.lead_id, event.campaign_id)

        if not outcome_id:
            logger.warning(f"No outcome_id found for deal {event.deal_id}")
            return {"status": "ignored", "reason": "no_outcome_id"}

        # Handle event types
        if event.event in ["opportunity.created", "deal.created"]:
            opportunity_created_at = (
                datetime.fromisoformat(event.created_at) if event.created_at else datetime.now()
            )

            # Update outcome with opportunity data
            await supabase.table("outcome_labels").update({
                "opportunity_created": True,
                "opportunity_created_at": opportunity_created_at.isoformat(),
                "opportunity_value": event.deal_value
            }).eq("id", outcome_id).execute()

            logger.info(f"Tracked opportunity created: outcome_id={outcome_id}, value=${event.deal_value}")

        elif event.event in ["deal.closed_won", "deal.won"]:
            closed_at = (
                datetime.fromisoformat(event.closed_at) if event.closed_at else datetime.now()
            )

            # Get opportunity created date for time-to-close calculation
            outcome = await supabase.table("outcome_labels").select("opportunity_created_at").eq(
                "id", outcome_id
            ).execute()

            opportunity_created_at = None
            if outcome.data and outcome.data[0].get("opportunity_created_at"):
                opportunity_created_at = datetime.fromisoformat(
                    outcome.data[0]["opportunity_created_at"]
                )

            await tracker.track_deal_closed(
                outcome_id=outcome_id,
                deal_value=event.deal_value,
                closed_at=closed_at,
                opportunity_created_at=opportunity_created_at
            )

            logger.info(f"Tracked deal closed won: outcome_id={outcome_id}, value=${event.deal_value}")

        elif event.event in ["deal.closed_lost", "deal.lost"]:
            await tracker.track_deal_lost(
                outcome_id=outcome_id,
                lost_reason=event.lost_reason or "unknown"
            )

            logger.info(f"Tracked deal closed lost: outcome_id={outcome_id}")

        return {"status": "success", "outcome_id": outcome_id}

    except Exception as e:
        logger.error(f"CRM webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crm/meetings")
async def crm_meeting_webhook(
    request: Request,
    x_crm_signature: str = Header(None),
):
    """
    Handle meeting completion events.

    Example: Calendly webhook when meeting is completed
    {
        "event": "invitee.created",
        "payload": {
            "status": "active",
            "email": "lead@example.com",
            "event_start_time": "2025-01-23T14:00:00Z"
        }
    }
    """
    try:
        body = await request.body()

        if x_crm_signature:
            if not verify_crm_signature(body, x_crm_signature):
                raise HTTPException(status_code=401, detail="Invalid signature")

        event_data: Dict[str, Any] = await request.json()

        # Normalize to our format
        normalized = normalize_meeting_event(event_data)
        if not normalized:
            return {"status": "ignored"}

        event = CRMMeetingEvent(**normalized)

        # Initialize tracker
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        tracker = OutcomeTracker(supabase)

        # Find outcome_id by contact email if not provided
        outcome_id = event.outcome_id
        if not outcome_id and event.contact_email:
            outcome_id = await find_outcome_by_email(supabase, event.contact_email)

        if not outcome_id:
            logger.warning(f"No outcome_id found for meeting {event.meeting_id}")
            return {"status": "ignored", "reason": "no_outcome_id"}

        # Track meeting completion
        if event.event in ["meeting.completed", "invitee.created"]:
            completed_at = (
                datetime.fromisoformat(event.completed_at) if event.completed_at else datetime.now()
            )

            if not event.no_show:
                # First mark as booked if not already
                await tracker.track_meeting_booked(outcome_id=outcome_id, booked_at=completed_at)

            # Then mark as completed or no-show
            await tracker.track_meeting_completed(
                outcome_id=outcome_id,
                completed_at=completed_at,
                no_show=event.no_show
            )

            logger.info(
                f"Tracked meeting: outcome_id={outcome_id}, no_show={event.no_show}"
            )

        return {"status": "success", "outcome_id": outcome_id}

    except Exception as e:
        logger.error(f"Meeting webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions

def normalize_crm_event(event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalize CRM-specific event format to our standard.

    Supports:
    - HubSpot
    - Salesforce
    - Pipedrive
    - Generic format
    """
    # Generic format (already normalized)
    if "event" in event_data and "deal_id" in event_data:
        return event_data

    # HubSpot format
    if "dealId" in event_data or "objectId" in event_data:
        return normalize_hubspot_event(event_data)

    # Salesforce format
    if "sobject" in event_data:
        return normalize_salesforce_event(event_data)

    # Pipedrive format
    if "current" in event_data and "previous" in event_data:
        return normalize_pipedrive_event(event_data)

    return None


def normalize_hubspot_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize HubSpot webhook to our format"""
    deal_id = event.get("objectId") or event.get("dealId")
    properties = event.get("properties", {})

    # Determine event type from deal stage
    deal_stage = properties.get("dealstage", "")
    if "closedwon" in deal_stage.lower():
        event_type = "deal.closed_won"
    elif "closedlost" in deal_stage.lower():
        event_type = "deal.closed_lost"
    else:
        event_type = "opportunity.created"

    return {
        "event": event_type,
        "deal_id": str(deal_id),
        "deal_value": properties.get("amount"),
        "closed_at": properties.get("closedate"),
        "created_at": properties.get("createdate"),
        "lost_reason": properties.get("closed_lost_reason"),
        "contact_email": event.get("associatedContacts", [None])[0],
    }


def normalize_salesforce_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Salesforce webhook to our format"""
    sobject = event.get("sobject", {})

    # Map Salesforce Stage to our event type
    stage = sobject.get("StageName", "")
    if "Closed Won" in stage:
        event_type = "deal.closed_won"
    elif "Closed Lost" in stage:
        event_type = "deal.closed_lost"
    else:
        event_type = "opportunity.created"

    return {
        "event": event_type,
        "deal_id": sobject.get("Id"),
        "deal_value": sobject.get("Amount"),
        "closed_at": sobject.get("CloseDate"),
        "created_at": sobject.get("CreatedDate"),
        "lost_reason": sobject.get("Description"),  # Or custom field
    }


def normalize_pipedrive_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Pipedrive webhook to our format"""
    current = event.get("current", {})

    # Determine event from status change
    status = current.get("status", "")
    if status == "won":
        event_type = "deal.closed_won"
    elif status == "lost":
        event_type = "deal.closed_lost"
    else:
        event_type = "opportunity.created"

    return {
        "event": event_type,
        "deal_id": str(current.get("id")),
        "deal_value": current.get("value"),
        "closed_at": current.get("won_time") or current.get("lost_time"),
        "created_at": current.get("add_time"),
        "lost_reason": current.get("lost_reason"),
    }


def normalize_meeting_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize meeting event (Calendly, etc.) to our format"""
    # Calendly format
    if "event" in event and event["event"] == "invitee.created":
        payload = event.get("payload", {})
        return {
            "event": "meeting.completed",
            "meeting_id": payload.get("uri", ""),
            "contact_email": payload.get("email"),
            "completed_at": payload.get("event_start_time"),
            "no_show": payload.get("status") == "canceled"
        }

    # Generic format
    if "event" in event and "meeting_id" in event:
        return event

    return None


async def find_outcome_by_lead(
    supabase: Any, lead_id: str, campaign_id: Optional[str] = None
) -> Optional[str]:
    """Find most recent outcome_id for a lead"""
    query = supabase.table("outcome_labels").select("id").eq("lead_id", lead_id)

    if campaign_id:
        query = query.eq("campaign_id", campaign_id)

    result = query.order("created_at", desc=True).limit(1).execute()

    return result.data[0]["id"] if result.data else None


async def find_outcome_by_email(supabase: Any, email: str) -> Optional[str]:
    """Find outcome by lead email (join through leads table)"""
    # First find lead by email
    lead_result = supabase.table("leads").select("id").eq("email", email).execute()

    if not lead_result.data:
        return None

    lead_id = lead_result.data[0]["id"]

    # Then find most recent outcome for that lead
    return await find_outcome_by_lead(supabase, lead_id)


@router.get("/crm/health")
async def crm_webhook_health():
    """Health check for CRM webhook endpoint"""
    return {"status": "healthy", "webhook": "crm"}
