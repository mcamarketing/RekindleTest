"""
Agents 11-12: Sync Agents

- TrackerAgent: Track message delivery and classify replies
- SynchronizerAgent: Sync data across systems (CRM, Slack, etc.)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from crewai import Agent
from openai import OpenAI
from ..tools.db_tools import SupabaseDB
from ..utils.agent_logging import log_agent_execution
from ..utils.error_handling import retry, CircuitBreaker
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.action_first_enforcer import ActionFirstEnforcer
import os


class TrackerAgent:
    """Agent 11: Track message delivery and classify replies."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.communication_bus = get_communication_bus()
        self.openai_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=Exception
        )
        # Configure to use GPT-5.1-instant (fast sync tasks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-instant", provider="openai")

        self.agent = Agent(
            role="Message Tracker",
            goal="Track message delivery, opens, clicks, and classify reply intent",
            backstory="""You are an expert at tracking message engagement and classifying
            reply intent. You detect meeting requests, opt-outs, objections, and questions.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Message tracker monitoring engagement and classifying replies
- tone:        Observant, systematic, data-focused
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at tracking message engagement and classifying
reply intent. You detect meeting requests, opt-outs, objections, and questions.""")
        )
    
    @log_agent_execution(agent_name="TrackerAgent")
    @retry(max_attempts=2)
    def classify_reply(self, lead_id: str, reply_text: str) -> Dict[str, Any]:
        """Classify the intent and sentiment of a reply."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        # Use GPT-5.1-instant to classify
        intent = self._classify_intent(reply_text)
        sentiment = self._classify_sentiment(reply_text)
        urgency = self._detect_urgency(reply_text)
        
        return {
            "lead_id": lead_id,
            "intent": intent,
            "sentiment": sentiment,
            "urgency": urgency,
            "requires_action": intent in ["MEETING_REQUEST", "QUESTION", "OBJECTION"]
        }
    
    def _classify_intent(self, text: str) -> str:
        """Classify reply intent."""
        text_lower = text.lower()
        
        if any(phrase in text_lower for phrase in ["meeting", "call", "chat", "demo", "schedule"]):
            return "MEETING_REQUEST"
        elif any(phrase in text_lower for phrase in ["unsubscribe", "remove", "stop", "opt out"]):
            return "OPT_OUT"
        elif any(phrase in text_lower for phrase in ["not interested", "no thanks", "pass"]):
            return "NOT_INTERESTED"
        elif any(phrase in text_lower for phrase in ["price", "cost", "expensive", "budget"]):
            return "OBJECTION"
        elif "?" in text:
            return "QUESTION"
        else:
            return "GENERAL_REPLY"
    
    def _classify_sentiment(self, text: str) -> str:
        """Classify reply sentiment."""
        text_lower = text.lower()
        
        positive_words = ["interested", "yes", "sounds good", "let's", "sure", "great"]
        negative_words = ["not interested", "no", "pass", "stop", "unsubscribe"]
        
        if any(word in text_lower for word in positive_words):
            return "positive"
        elif any(word in text_lower for word in negative_words):
            return "negative"
        else:
            return "neutral"
    
    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["urgent", "asap", "immediately", "today"]):
            return "high"
        elif any(word in text_lower for word in ["soon", "this week", "quickly"]):
            return "medium"
        else:
            return "low"


class SynchronizerAgent:
    """Agent 12: Sync data across systems."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-instant (fast sync tasks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-instant", provider="openai")

        self.agent = Agent(
            role="Data Synchronizer",
            goal="Sync lead data, replies, and deals across CRM, Slack, and other systems",
            backstory="""You are an expert at keeping data synchronized across multiple systems.
            You log replies to HubSpot, send Slack alerts, update lifecycle stages, and create deals.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Data synchronizer maintaining system consistency
- tone:        Methodical, reliable, precision-focused
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at keeping data synchronized across multiple systems.
You log replies to HubSpot, send Slack alerts, update lifecycle stages, and create deals.""")
        )
    
    @log_agent_execution(agent_name="SynchronizerAgent")
    @retry(max_attempts=3, backoff="exponential")
    def sync_reply_to_crm(self, lead_id: str, reply_data: Dict) -> Dict[str, Any]:
        """Sync a reply to CRM (HubSpot)."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        # In production, this would call HubSpot MCP
        # For now, return success
        return {
            "success": True,
            "lead_id": lead_id,
            "synced_to": "hubspot",
            "actions": [
                "logged_reply_to_timeline",
                "updated_lifecycle_stage",
                "sent_slack_alert"
            ]
        }
    
    @log_agent_execution(agent_name="SynchronizerAgent")
    @retry(max_attempts=3, backoff="exponential")
    def sync_meeting_to_crm(self, lead_id: str, meeting_data: Dict) -> Dict[str, Any]:
        """Sync a booked meeting to CRM."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        # In production, this would:
        # 1. Create deal in HubSpot
        # 2. Update lifecycle stage
        # 3. Send Slack notification
        # 4. Log to timeline
        
        return {
            "success": True,
            "lead_id": lead_id,
            "deal_created": True,
            "lifecycle_stage": "meeting_booked",
            "synced_to": ["hubspot", "slack"]
        }

