"""
SendGrid Webhook Handler
Captures email delivery events and updates outcome labels

Events tracked:
- delivered: Email successfully delivered
- bounce: Email bounced (hard/soft)
- open: Email opened
- click: Link clicked
- spam_report: Marked as spam

Setup in SendGrid:
1. Go to Settings → Mail Settings → Event Webhook
2. Set HTTP POST URL: https://your-api.com/webhooks/sendgrid
3. Enable events: delivered, bounce, open, click, spam_report
4. Authorization: Basic Auth or custom header
"""

import logging
import hmac
import hashlib
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client
from ..outcome_tracker import OutcomeTracker
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# SendGrid webhook verification (optional but recommended)
SENDGRID_WEBHOOK_SECRET = os.getenv("SENDGRID_WEBHOOK_SECRET", "")


class SendGridEvent(BaseModel):
    """SendGrid event payload"""
    email: str
    event: str
    timestamp: int
    sg_message_id: str
    sg_event_id: str
    campaign_id: str = ""  # Custom arg we'll pass when sending
    outcome_id: str = ""  # Custom arg we'll pass when sending
    bounce_reason: str = ""
    url: str = ""  # For click events
    reason: str = ""  # For bounce/spam events


def verify_sendgrid_signature(payload: bytes, signature: str, timestamp: str) -> bool:
    """
    Verify SendGrid webhook signature for security.

    Args:
        payload: Raw request body
        signature: X-Twilio-Email-Event-Webhook-Signature header
        timestamp: X-Twilio-Email-Event-Webhook-Timestamp header

    Returns:
        True if signature is valid
    """
    if not SENDGRID_WEBHOOK_SECRET:
        logger.warning("SENDGRID_WEBHOOK_SECRET not set, skipping verification")
        return True

    # Construct verification payload
    verification_payload = timestamp + payload.decode('utf-8')

    # Generate HMAC SHA256 signature
    expected_signature = hmac.new(
        SENDGRID_WEBHOOK_SECRET.encode('utf-8'),
        verification_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


@router.post("/sendgrid")
async def sendgrid_webhook(
    request: Request,
    x_twilio_email_event_webhook_signature: str = Header(None),
    x_twilio_email_event_webhook_timestamp: str = Header(None),
):
    """
    Handle SendGrid webhook events.

    SendGrid sends events as JSON array:
    [
        {
            "email": "lead@example.com",
            "event": "delivered",
            "timestamp": 1234567890,
            "sg_message_id": "...",
            "campaign_id": "uuid",
            "outcome_id": "uuid"
        },
        ...
    ]
    """
    try:
        # Get raw body for signature verification
        body = await request.body()

        # Verify signature if configured
        if x_twilio_email_event_webhook_signature and x_twilio_email_event_webhook_timestamp:
            if not verify_sendgrid_signature(
                body,
                x_twilio_email_event_webhook_signature,
                x_twilio_email_event_webhook_timestamp
            ):
                logger.error("Invalid SendGrid webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse events
        events: List[Dict[str, Any]] = await request.json()

        # Initialize Supabase and tracker
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        tracker = OutcomeTracker(supabase)

        # Process each event
        for event_data in events:
            event = SendGridEvent(**event_data)

            # Skip if no outcome_id (not tracked message)
            if not event.outcome_id:
                logger.warning(f"SendGrid event without outcome_id: {event.event}")
                continue

            event_time = datetime.fromtimestamp(event.timestamp)

            # Handle different event types
            if event.event == "delivered":
                await tracker.track_delivery(
                    outcome_id=event.outcome_id,
                    delivered=True,
                    delivered_at=event_time
                )

            elif event.event in ["bounce", "dropped"]:
                await tracker.track_delivery(
                    outcome_id=event.outcome_id,
                    delivered=False,
                    bounce_reason=event.reason or event.bounce_reason
                )

            elif event.event == "open":
                await tracker.track_opened(
                    outcome_id=event.outcome_id,
                    opened_at=event_time
                )

            elif event.event == "click":
                await tracker.track_clicked(
                    outcome_id=event.outcome_id,
                    clicked_at=event_time
                )

            elif event.event in ["spamreport", "unsubscribe"]:
                # Mark as negative training example
                await tracker.track_delivery(
                    outcome_id=event.outcome_id,
                    delivered=True,  # It was delivered, but negative outcome
                    bounce_reason=f"{event.event}: {event.reason}"
                )

            logger.info(
                f"Processed SendGrid event: {event.event} for outcome_id={event.outcome_id}"
            )

        return {"status": "success", "processed": len(events)}

    except Exception as e:
        logger.error(f"SendGrid webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sendgrid/health")
async def sendgrid_webhook_health():
    """Health check for SendGrid webhook endpoint"""
    return {"status": "healthy", "webhook": "sendgrid"}
