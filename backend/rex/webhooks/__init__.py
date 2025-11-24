"""
Webhooks for Outcome Tracking
Part of: Flywheel Architecture - Data Capture Infrastructure

Captures real-time events from:
- SendGrid (email delivery, opens, clicks, replies)
- Twilio (SMS delivery, replies)
- CRM integrations (deals closed, opportunities created)
"""

from .sendgrid_webhook import router as sendgrid_router
from .crm_webhook import router as crm_router

__all__ = ["sendgrid_router", "crm_router"]
