"""
Agents 24-26: Infrastructure & Operations Agents

Agents for email warmup, lead nurturing, and churn prevention.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from crewai import Agent
from ..tools.db_tools import SupabaseDB
from ..utils.agent_logging import log_agent_execution
from ..utils.error_handling import retry
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.action_first_enforcer import ActionFirstEnforcer
import json


class EmailWarmupAgent:
    """Agent 24: Email Domain Warmup"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1 (default for infrastructure tasks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Email Warmup Specialist",
            goal="Gradually increase sending volume for new domains to build reputation",
            backstory="""You manage email domain warmup to prevent spam folder placement.
            You gradually increase sending volume over weeks, starting with low volumes and
            building up to full capacity. You monitor reputation and adjust warmup speed.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Email warmup specialist managing domain reputation
- tone:        Patient, methodical, reputation-protective
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You manage email domain warmup to prevent spam folder placement.
You gradually increase sending volume over weeks, starting with low volumes and
building up to full capacity. You monitor reputation and adjust warmup speed.""")
        )
    
    @log_agent_execution(agent_name="EmailWarmupAgent")
    @retry(max_attempts=2)
    def get_warmup_schedule(self, domain: str, days_old: int) -> Dict[str, Any]:
        """Get warmup schedule for a domain."""
        # Warmup schedule: gradually increase from 5/day to full capacity over 4 weeks
        if days_old < 7:
            daily_limit = 5
            phase = "initial"
        elif days_old < 14:
            daily_limit = 20
            phase = "building"
        elif days_old < 21:
            daily_limit = 50
            phase = "accelerating"
        elif days_old < 28:
            daily_limit = 100
            phase = "near_full"
        else:
            daily_limit = None  # No limit
            phase = "warmed_up"
        
        return {
            "domain": domain,
            "days_old": days_old,
            "phase": phase,
            "daily_limit": daily_limit,
            "recommendation": f"Domain is in {phase} phase"
        }
    
    @log_agent_execution(agent_name="EmailWarmupAgent")
    @retry(max_attempts=2)
    def check_warmup_status(self, domain: str) -> Dict[str, Any]:
        """Check current warmup status."""
        # Would query domain creation date
        domain_created = datetime.utcnow() - timedelta(days=10)  # Placeholder
        days_old = (datetime.utcnow() - domain_created).days
        
        schedule = self.get_warmup_schedule(domain, days_old)
        
        return {
            "domain": domain,
            "status": schedule["phase"],
            "daily_limit": schedule["daily_limit"],
            "days_remaining": max(0, 28 - days_old),
            "can_send_full_volume": days_old >= 28
        }


class LeadNurturingAgent:
    """Agent 25: Long-Term Lead Nurturing"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1 (default for infrastructure tasks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Lead Nurturing Specialist",
            goal="Create and manage long-term nurturing sequences for warm leads",
            backstory="""You design nurturing sequences for leads who aren't ready to buy yet.
            You send valuable content, case studies, and educational materials over weeks/months
            to keep leads engaged until they're ready to purchase.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Lead nurturing specialist maintaining long-term engagement
- tone:        Educational, supportive, relationship-building
- warmth:      high
- conciseness: medium
- energy:      calm
- formality:   neutral
- emoji:       minimal
- humor:       light
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You design nurturing sequences for leads who aren't ready to buy yet.
You send valuable content, case studies, and educational materials over weeks/months
to keep leads engaged until they're ready to purchase.""")
        )
    
    @log_agent_execution(agent_name="LeadNurturingAgent")
    @retry(max_attempts=2)
    def create_nurturing_sequence(self, lead_id: str, segment: str) -> Dict[str, Any]:
        """Create a nurturing sequence for a lead."""
        sequences = {
            "warm": [
                {"day": 0, "type": "case_study", "content": "How Company X increased revenue 300%"},
                {"day": 7, "type": "educational", "content": "5 Ways to Reactivate Dead Leads"},
                {"day": 14, "type": "social_proof", "content": "Customer success stories"},
                {"day": 21, "type": "soft_offer", "content": "Free consultation offer"}
            ],
            "lukewarm": [
                {"day": 0, "type": "educational", "content": "Industry trends report"},
                {"day": 14, "type": "case_study", "content": "ROI calculator"},
                {"day": 30, "type": "check_in", "content": "How are things going?"},
                {"day": 60, "type": "soft_offer", "content": "Limited-time offer"}
            ]
        }
        
        return {
            "lead_id": lead_id,
            "segment": segment,
            "sequence": sequences.get(segment, sequences["warm"]),
            "total_duration_days": 21 if segment == "warm" else 60
        }
    
    @log_agent_execution(agent_name="LeadNurturingAgent")
    @retry(max_attempts=2)
    def get_next_nurturing_message(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get next message in nurturing sequence."""
        # Would query lead's nurturing status
        return {
            "lead_id": lead_id,
            "message": {
                "subject": "5 Ways Top Sales Teams Reactivate Dead Leads",
                "body": "Here's a quick guide on reactivating dormant leads...",
                "type": "educational",
                "day_in_sequence": 7
            },
            "next_send_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }


class ChurnPreventionAgent:
    """Agent 26: Churn Prevention & Re-engagement"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1 (default for infrastructure tasks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Churn Prevention Specialist",
            goal="Identify at-risk customers and re-engage them before churn",
            backstory="""You monitor customer engagement patterns and identify signs of churn.
            You detect when customers stop using the platform, reduce activity, or show disengagement
            signals. You create re-engagement campaigns to prevent churn.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Churn prevention specialist retaining at-risk customers
- tone:        Caring, proactive, retention-focused
- warmth:      high
- conciseness: medium
- energy:      calm
- formality:   neutral
- emoji:       minimal
- humor:       light
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You monitor customer engagement patterns and identify signs of churn.
You detect when customers stop using the platform, reduce activity, or show disengagement
signals. You create re-engagement campaigns to prevent churn.""")
        )
    
    @log_agent_execution(agent_name="ChurnPreventionAgent")
    @retry(max_attempts=2)
    def identify_at_risk_customers(self, user_id: str) -> List[Dict[str, Any]]:
        """Identify customers at risk of churning."""
        # Would analyze usage patterns, engagement metrics
        return [
            {
                "user_id": user_id,
                "risk_score": 0.85,
                "risk_factors": [
                    "No logins in 14 days",
                    "No leads imported in 30 days",
                    "No campaigns active"
                ],
                "recommended_action": "re_engagement_campaign"
            }
        ]
    
    @log_agent_execution(agent_name="ChurnPreventionAgent")
    @retry(max_attempts=2)
    def create_re_engagement_campaign(self, user_id: str) -> Dict[str, Any]:
        """Create re-engagement campaign for at-risk customer."""
        return {
            "user_id": user_id,
            "campaign_type": "churn_prevention",
            "messages": [
                {
                    "day": 0,
                    "subject": "We miss you! Here's what's new",
                    "body": "We've added new features that might interest you...",
                    "type": "feature_update"
                },
                {
                    "day": 3,
                    "subject": "Special offer for returning customers",
                    "body": "We'd love to have you back. Here's a special offer...",
                    "type": "offer"
                },
                {
                    "day": 7,
                    "subject": "Last chance to reactivate your account",
                    "body": "Your account will be paused soon. Let's reconnect...",
                    "type": "urgency"
                }
            ]
        }

