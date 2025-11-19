"""
Webhook Handlers for External Services

Handles webhooks from:
- SendGrid (email delivery events)
- Twilio (SMS/WhatsApp status callbacks)
- Stripe (payment events)
"""

from fastapi import Request, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import hmac
import hashlib
import json
import logging
from datetime import datetime
from .tools.db_tools import SupabaseDB

logger = logging.getLogger(__name__)
db = SupabaseDB()

# Webhook handlers (no separate app, routes will be mounted to main app)


def verify_sendgrid_signature(payload: str, signature: str, timestamp: str, public_key: str) -> bool:
    """Verify SendGrid webhook signature."""
    try:
        import os
        from sendgrid import SendGridAPIClient
        
        # SendGrid uses HMAC-SHA256
        message = f"{timestamp}{payload}"
        expected_signature = hmac.new(
            public_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"SendGrid signature verification error: {e}")
        return False


def verify_twilio_signature(url: str, params: Dict, signature: str, auth_token: str) -> bool:
    """Verify Twilio webhook signature."""
    try:
        from twilio.request_validator import RequestValidator
        validator = RequestValidator(auth_token)
        return validator.validate(url, params, signature)
    except Exception as e:
        logger.error(f"Twilio signature verification error: {e}")
        return False


async def sendgrid_webhook(request: Request):
    """
    Handle SendGrid webhook events.

    Events: delivered, opened, clicked, bounced, spamreport, unsubscribe

    Security: Signature verification is REQUIRED in production
    """
    try:
        body = await request.body()

        # SECURITY: Verify webhook signature (PRODUCTION REQUIREMENT)
        signature = request.headers.get("X-Twilio-Email-Event-Webhook-Signature")
        timestamp = request.headers.get("X-Twilio-Email-Event-Webhook-Timestamp")
        public_key = os.getenv("SENDGRID_WEBHOOK_VERIFICATION_KEY")

        if not public_key:
            logger.error("SENDGRID_WEBHOOK_VERIFICATION_KEY not configured - rejecting webhook")
            raise HTTPException(
                status_code=503,
                detail="Webhook verification not configured. Set SENDGRID_WEBHOOK_VERIFICATION_KEY."
            )

        if not signature or not timestamp:
            logger.warning("Missing signature or timestamp headers in SendGrid webhook")
            raise HTTPException(status_code=401, detail="Missing authentication headers")

        # Verify signature
        if not verify_sendgrid_signature(body.decode(), signature, timestamp, public_key):
            logger.warning(f"Invalid SendGrid webhook signature from {request.client.host}")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        events = json.loads(body)
        
        processed = 0
        for event in events:
            event_type = event.get("event")
            message_id = event.get("sg_message_id", "").split(".")[0] if event.get("sg_message_id") else None
            email = event.get("email")
            timestamp = event.get("timestamp")
            
            # Extract custom args (lead_id, campaign_id, user_id)
            custom_args = event.get("custom_args", {})
            lead_id = custom_args.get("lead_id")
            campaign_id = custom_args.get("campaign_id")
            user_id = custom_args.get("user_id")
            
            # Update message status in database
            if message_id and lead_id:
                try:
                    # Find message by external_id (SendGrid message ID)
                    message_result = db.supabase.table("messages").select("id").eq("external_id", message_id).maybe_single().execute()
                    
                    if message_result.data:
                        message_db_id = message_result.data["id"]
                        
                        # Update based on event type
                        updates = {
                            "updated_at": datetime.utcnow().isoformat()
                        }
                        
                        if event_type == "delivered":
                            updates["status"] = "delivered"
                            updates["delivered_at"] = datetime.fromtimestamp(timestamp).isoformat() if timestamp else None
                        elif event_type == "opened":
                            updates["open_count"] = db.supabase.rpc("increment", {"table": "messages", "column": "open_count", "id": message_db_id})
                            # Also log to engagement table
                            db.supabase.table("message_engagement").insert({
                                "message_id": message_db_id,
                                "lead_id": lead_id,
                                "event_type": "open",
                                "timestamp": datetime.fromtimestamp(timestamp).isoformat() if timestamp else datetime.utcnow().isoformat()
                            }).execute()
                        elif event_type == "clicked":
                            updates["click_count"] = db.supabase.rpc("increment", {"table": "messages", "column": "click_count", "id": message_db_id})
                            db.supabase.table("message_engagement").insert({
                                "message_id": message_db_id,
                                "lead_id": lead_id,
                                "event_type": "click",
                                "url": event.get("url"),
                                "timestamp": datetime.fromtimestamp(timestamp).isoformat() if timestamp else datetime.utcnow().isoformat()
                            }).execute()
                        elif event_type == "bounced":
                            updates["status"] = "bounced"
                            updates["bounce_reason"] = event.get("reason")
                        elif event_type == "spamreport":
                            updates["status"] = "spam"
                            # Add to suppression list
                            db.supabase.table("suppression_list").upsert({
                                "email": email,
                                "reason": "spam_report",
                                "user_id": user_id
                            }, on_conflict="email").execute()
                        elif event_type == "unsubscribe":
                            updates["status"] = "unsubscribed"
                            db.supabase.table("suppression_list").upsert({
                                "email": email,
                                "reason": "unsubscribe",
                                "user_id": user_id
                            }, on_conflict="email").execute()
                        
                        # Update message
                        db.supabase.table("messages").update(updates).eq("id", message_db_id).execute()
                        processed += 1
                        
                except Exception as e:
                    logger.error(f"Error processing SendGrid event: {e}", exc_info=True)
        
        logger.info(f"Processed {processed} SendGrid webhook events")
        return JSONResponse({"status": "success", "processed": processed})
        
    except Exception as e:
        logger.error(f"SendGrid webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def twilio_webhook(request: Request):
    """
    Handle Twilio webhook events (SMS/WhatsApp status callbacks).
    """
    try:
        form_data = await request.form()
        params = dict(form_data)
        
        # Verify signature
        import os
        signature = request.headers.get("X-Twilio-Signature")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        url = str(request.url)
        
        if auth_token and signature:
            if not verify_twilio_signature(url, params, signature, auth_token):
                raise HTTPException(status_code=401, detail="Invalid Twilio signature")
        
        message_sid = params.get("MessageSid")
        status = params.get("MessageStatus")  # queued, sent, delivered, failed, undelivered
        to_number = params.get("To")
        from_number = params.get("From")
        
        # Extract custom data from MessageSid or lookup
        # Twilio doesn't support custom args like SendGrid, so we need to store mapping
        try:
            # Look up message by external_id (Twilio SID)
            message_result = db.supabase.table("messages").select("id, lead_id, campaign_id, user_id").eq("external_id", message_sid).maybe_single().execute()
            
            if message_result.data:
                message_data = message_result.data
                updates = {
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                if status == "delivered":
                    updates["status"] = "delivered"
                    updates["delivered_at"] = datetime.utcnow().isoformat()
                elif status == "failed" or status == "undelivered":
                    updates["status"] = "failed"
                    updates["error"] = params.get("ErrorMessage", "Delivery failed")
                elif status == "sent":
                    updates["status"] = "sent"
                
                db.supabase.table("messages").update(updates).eq("id", message_data["id"]).execute()
                
                logger.info(f"Updated Twilio message {message_sid} to status {status}")
                return JSONResponse({"status": "success"})
            else:
                logger.warning(f"Twilio message {message_sid} not found in database")
                return JSONResponse({"status": "not_found"})
                
        except Exception as e:
            logger.error(f"Error processing Twilio webhook: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Twilio webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    """
    Handle Stripe webhook events (payments, subscriptions).
    """
    try:
        import os
        import stripe
        
        body = await request.body()
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if not webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not set, skipping signature verification")
            # Parse without verification (not recommended for production)
            event = json.loads(body)
        else:
            try:
                event = stripe.Webhook.construct_event(
                    body, stripe_signature, webhook_secret
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail="Invalid payload")
            except stripe.error.SignatureVerificationError as e:
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        # Handle different event types
        if event_type == "customer.subscription.created":
            # New subscription
            user_id = data.get("metadata", {}).get("user_id")
            subscription_id = data.get("id")
            status = data.get("status")
            
            if user_id:
                db.supabase.table("profiles").update({
                    "stripe_subscription_id": subscription_id,
                    "subscription_status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", user_id).execute()
                
        elif event_type == "customer.subscription.updated":
            # Subscription updated (upgrade/downgrade/cancelled)
            user_id = data.get("metadata", {}).get("user_id")
            status = data.get("status")
            
            if user_id:
                db.supabase.table("profiles").update({
                    "subscription_status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", user_id).execute()
                
        elif event_type == "invoice.payment_succeeded":
            # Payment succeeded
            user_id = data.get("metadata", {}).get("user_id")
            amount = data.get("amount_paid", 0) / 100  # Convert from cents
            
            if user_id:
                # Log payment
                db.supabase.table("payments").insert({
                    "user_id": user_id,
                    "amount": amount,
                    "currency": data.get("currency", "usd"),
                    "stripe_invoice_id": data.get("id"),
                    "status": "succeeded",
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
                
        elif event_type == "invoice.payment_failed":
            # Payment failed
            user_id = data.get("metadata", {}).get("user_id")
            
            if user_id:
                db.supabase.table("profiles").update({
                    "subscription_status": "past_due",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", user_id).execute()
        
        logger.info(f"Processed Stripe webhook: {event_type}")
        return JSONResponse({"status": "success"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Health check for webhooks
async def webhook_health():
    """Health check endpoint for webhook service."""
    return JSONResponse({
        "status": "healthy",
        "service": "webhooks",
        "timestamp": datetime.utcnow().isoformat()
    })

