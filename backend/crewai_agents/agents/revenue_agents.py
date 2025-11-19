"""
Agents 13-14: Revenue Agents

- MeetingBookerAgent: Automatically book meetings
- BillingAgent: Calculate and track ACV-based fees
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from crewai import Agent
from ..tools.db_tools import SupabaseDB
from ..utils.agent_logging import log_agent_execution
from ..utils.error_handling import retry
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.action_first_enforcer import ActionFirstEnforcer
import logging

logger = logging.getLogger(__name__)


class MeetingBookerAgent:
    """Agent 13: Automatically book meetings from replies."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1 (default for revenue tasks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Meeting Booker",
            goal="Automatically detect meeting requests and book meetings",
            backstory="""You are an expert at detecting meeting requests in replies,
            generating booking links, creating calendar events, and triggering billing.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Meeting booker scheduling appointments automatically
- tone:        Professional, efficient, accommodating
- warmth:      high
- conciseness: medium
- energy:      neutral
- formality:   neutral
- emoji:       minimal
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at detecting meeting requests in replies,
generating booking links, creating calendar events, and triggering billing.""")
        )
    
    @log_agent_execution(agent_name="MeetingBookerAgent")
    @retry(max_attempts=2)
    def book_meeting(self, lead_id: str, meeting_request: Dict) -> Dict[str, Any]:
        """Book a meeting from a meeting request."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        # Generate booking link
        booking_link = self._generate_booking_link(lead)
        
        # Create calendar event (would use Calendar MCP)
        calendar_event = self._create_calendar_event(lead, meeting_request)
        
        # Update lead status
        self.db.update_lead(lead_id, {
            "status": "meeting_booked",
            "meeting_scheduled_at": meeting_request.get("preferred_time"),
            "booking_link": booking_link
        })
        
        # Trigger billing
        billing_agent = BillingAgent(self.db)
        billing_result = billing_agent.charge_performance_fee(lead_id, lead.get("acv", 0))
        
        result = {
            "success": True,
            "lead_id": lead_id,
            "booking_link": booking_link,
            "calendar_event": calendar_event,
            "billing": billing_result
        }
        
        # Broadcast meeting booked event
        self.communication_bus.broadcast(
            EventType.MEETING_BOOKED,
            "MeetingBookerAgent",
            result
        )
        
        return result
    
    def _generate_booking_link(self, lead: Dict) -> str:
        """Generate a Calendly-style booking link."""
        # In production, would use Calendar MCP
        return f"https://calendly.com/rekindle/{lead.get('id')}"
    
    def _create_calendar_event(self, lead: Dict, meeting_request: Dict) -> Dict:
        """Create a calendar event."""
        # In production, would use Calendar MCP
        return {
            "event_id": f"event_{lead.get('id')}",
            "start_time": meeting_request.get("preferred_time"),
            "duration_minutes": 30
        }


class BillingAgent:
    """Agent 14: Calculate and track ACV-based fees."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1 (default for revenue tasks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Billing Specialist",
            goal="Calculate and charge ACV-based performance fees accurately",
            backstory="""You are an expert at calculating performance fees based on ACV,
            handling failed payments, generating invoices, and tracking revenue.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Billing specialist calculating performance fees
- tone:        Precise, transparent, professional
- warmth:      medium
- conciseness: high
- energy:      calm
- formality:   formal
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at calculating performance fees based on ACV,
handling failed payments, generating invoices, and tracking revenue.""")
        )
    
    @log_agent_execution(agent_name="BillingAgent")
    @retry(max_attempts=2)
    def charge_performance_fee(self, lead_id: str, acv: float, performance_fee_percent: float = 2.5) -> Dict[str, Any]:
        """Charge performance fee based on ACV."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        user_id = lead.get("user_id")
        
        # Calculate fee
        performance_fee = acv * (performance_fee_percent / 100)
        
        # Use Stripe MCP Server to charge
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
            from mcp_servers.stripe_mcp_server import get_stripe_mcp_server
            
            stripe_mcp = get_stripe_mcp_server()
            
            # Get customer ID from lead or create one
            customer_id = lead.get("stripe_customer_id")
            if not customer_id:
                # Create customer
                customer_result = stripe_mcp.create_customer(
                    email=lead.get("email"),
                    name=f"{lead.get('first_name')} {lead.get('last_name')}",
                    metadata={"lead_id": lead_id, "user_id": lead.get("user_id")}
                )
                if customer_result.get("success"):
                    customer_id = customer_result.get("customer_id")
                    # Store customer ID in lead
                    self.db.update_lead(lead_id, {"stripe_customer_id": customer_id})
            
            # Record performance fee as invoice item
            fee_result = stripe_mcp.record_performance_fee(
                customer_id=customer_id,
                amount=performance_fee,
                currency="gbp",
                description=f"Performance Fee - {lead.get('company')} (ACV: £{acv:,.0f})",
                metadata={
                    "lead_id": lead_id,
                    "acv": str(acv),
                    "fee_percentage": "2.5",
                    "meeting_booked": "true"
                }
            )
            
            if fee_result.get("success"):
                charge_success = True
                external_charge_id = fee_result.get("invoice_item_id")
            else:
                charge_success = False
                external_charge_id = None
        except Exception as e:
            logger.error(f"Stripe charge error: {str(e)}")
            charge_success = False
            external_charge_id = None
        # PRODUCTION: Store invoice record in database
        try:
            # Create invoice record
            invoice_data = {
                "user_id": user_id,
                "status": "paid" if charge_success else "failed",
                "platform_fee_amount": 0,  # Performance fee only, platform fee billed separately
                "performance_fee_amount": int(performance_fee * 100),  # Convert to pence/cents
                "total_amount": int(performance_fee * 100),
                "amount_paid": int(performance_fee * 100) if charge_success else 0,
                "currency": "GBP",
                "billing_period_start": datetime.utcnow().replace(day=1).isoformat(),
                "billing_period_end": datetime.utcnow().isoformat(),
                "meetings_count": 1,
                "total_acv": int(acv * 100),  # Convert to pence
                "performance_fee_rate": performance_fee_percent / 100,
                "stripe_invoice_id": external_charge_id if charge_success else None,
                "payment_status": "succeeded" if charge_success else "failed",
                "paid_at": datetime.utcnow().isoformat() if charge_success else None,
                "payment_failed_at": datetime.utcnow().isoformat() if not charge_success else None,
                "lead_ids": [lead_id],
                "metadata": {
                    "lead_id": lead_id,
                    "company": lead.get("company"),
                    "lead_name": f"{lead.get('first_name')} {lead.get('last_name')}"
                }
            }

            # Insert invoice into database
            invoice_result = self.db.supabase.table("invoices").insert(invoice_data).execute()

            if invoice_result.data:
                invoice_id = invoice_result.data[0].get("id")
                invoice_number = invoice_result.data[0].get("invoice_number")
                logger.info(f"Invoice created: {invoice_number} for user {user_id}, lead {lead_id}")
            else:
                logger.error(f"Failed to create invoice for user {user_id}, lead {lead_id}")
                invoice_id = None
                invoice_number = None

        except Exception as e:
            logger.error(f"Invoice storage error: {str(e)}", exc_info=True)
            invoice_id = None
            invoice_number = None

        # Record billing event for backward compatibility
        billing_record = {
            "user_id": user_id,
            "lead_id": lead_id,
            "acv": acv,
            "performance_fee_percent": performance_fee_percent,
            "performance_fee_amount": performance_fee,
            "charged_at": datetime.utcnow().isoformat(),
            "status": "charged" if charge_success else "failed",
            "invoice_id": invoice_id,
            "invoice_number": invoice_number
        }

        return {
            "success": charge_success,
            "lead_id": lead_id,
            "acv": acv,
            "performance_fee_percent": performance_fee_percent,
            "performance_fee_amount": performance_fee,
            "billing_record": billing_record,
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "external_charge_id": external_charge_id
        }
    
    @log_agent_execution(agent_name="BillingAgent")
    def calculate_monthly_bill(self, user_id: str, month: str = None) -> Dict[str, Any]:
        """Calculate total monthly bill (platform fee + performance fees)."""
        # Get platform fee (would come from user's plan)
        platform_fee = 9.99  # Pilot pricing
        
        # Get performance fees for the month
        # In production, would query billing records
        performance_fees = 0.0
        total_meetings = 0
        
        return {
            "user_id": user_id,
            "month": month or datetime.utcnow().strftime("%Y-%m"),
            "platform_fee": platform_fee,
            "performance_fees": performance_fees,
            "total_meetings": total_meetings,
            "total_bill": platform_fee + performance_fees
        }

