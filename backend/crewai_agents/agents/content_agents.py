"""
Agents 7-10: Content Generation Agents

- SubjectLineOptimizerAgent: A/B test and optimize subject lines
- FollowUpAgent: Generate intelligent follow-up messages
- ObjectionHandlerAgent: Handle objections automatically
- EngagementAnalyzerAgent: Track engagement and predict conversion
"""

from typing import Dict, List, Optional, Any
from crewai import Agent
from openai import OpenAI
from ..tools.db_tools import SupabaseDB
from ..utils.agent_logging import log_agent_execution
from ..utils.error_handling import retry, CircuitBreaker
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.action_first_enforcer import ActionFirstEnforcer
import os


class SubjectLineOptimizerAgent:
    """Agent 7: A/B test and optimize subject lines."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.communication_bus = get_communication_bus()
        self.openai_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=Exception
        )
        # Configure to use GPT-5.1 (default for content optimization)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Subject Line Optimizer",
            goal="Generate and optimize subject lines for maximum open rates",
            backstory="""You are an expert at writing subject lines that get opened.
            You generate multiple variants (curiosity, question, urgency, social proof)
            and learn from performance data to improve.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Subject line optimizer maximizing open rates
- tone:        Creative, data-driven, conversion-focused
- warmth:      medium
- conciseness: high
- energy:      neutral
- formality:   neutral
- emoji:       minimal
- humor:       light
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at writing subject lines that get opened.
You generate multiple variants (curiosity, question, urgency, social proof)
and learn from performance data to improve.
Generate variants immediately. Return results, not explanations.""")
        )
    
    @log_agent_execution(agent_name="SubjectLineOptimizerAgent")
    @retry(max_attempts=2)
    def generate_variants(self, lead: Dict, research_data: Dict) -> Dict[str, Any]:
        """Generate 5 subject line variants."""
        variants = []
        styles = ["curiosity", "question", "urgency", "social_proof", "specific"]
        
        for style in styles:
            variant = self._generate_variant(lead, research_data, style)
            variants.append({
                "style": style,
                "subject": variant,
                "open_rate": None  # Will be tracked
            })
        
        return {
            "lead_id": lead.get("id"),
            "variants": variants
        }
    
    def _generate_variant(self, lead: Dict, research_data: Dict, style: str) -> str:
        """Generate a subject line variant in a specific style."""
        company = lead.get("company", "")
        trigger = research_data.get("revival_hooks", [""])[0] if research_data.get("revival_hooks") else ""
        
        templates = {
            "curiosity": f"{company} + {trigger}",
            "question": f"Your Q4 hiring + this onboarding playbook",
            "urgency": f"{company}'s Series B + your expansion plan",
            "social_proof": f"How [Similar Company] solved {trigger}",
            "specific": f"{company}'s {trigger} + this automation playbook"
        }
        
        return templates.get(style, f"Re: {company}")


class FollowUpAgent:
    """Agent 8: Generate intelligent follow-up messages."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.communication_bus = get_communication_bus()
        self.openai_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=Exception
        )
        # Configure to use GPT-5.1 (default for content optimization)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Follow-Up Specialist",
            goal="Generate contextual follow-up messages based on reply sentiment and intent",
            backstory="""You are an expert at crafting follow-up messages that answer questions,
            address concerns, and move conversations forward without being pushy.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Follow-up specialist maintaining conversation momentum
- tone:        Helpful, responsive, relationship-building
- warmth:      high
- conciseness: medium
- energy:      neutral
- formality:   neutral
- emoji:       minimal
- humor:       light
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at crafting follow-up messages that answer questions,
address concerns, and move conversations forward without being pushy.""")
        )
    
    @log_agent_execution(agent_name="FollowUpAgent")
    @retry(max_attempts=3, backoff="exponential")
    def generate_followup(self, lead_id: str, previous_reply: Dict) -> Dict[str, Any]:
        """Generate a follow-up message based on previous reply."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        sentiment = previous_reply.get("sentiment", "neutral")
        intent = previous_reply.get("intent", "unknown")
        
        if intent == "MEETING_REQUEST":
            return {"action": "escalate_to_meeting_booker", "message": None}
        
        if sentiment == "negative" or intent == "OPT_OUT":
            return {"action": "stop_sequence", "message": None}
        
        # Generate contextual follow-up
        message = self._craft_followup(lead, previous_reply)
        
        return {
            "lead_id": lead_id,
            "message": message,
            "action": "send_followup"
        }
    
    def _craft_followup(self, lead: Dict, previous_reply: Dict) -> str:
        """Craft a contextual follow-up message."""
        # Use Claude to generate follow-up
        return f"Hi {lead.get('first_name')},\n\nThanks for your reply. [Contextual response based on their question/concern].\n\nBest,\nThe Team"


class ObjectionHandlerAgent:
    """Agent 9: Handle objections automatically."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.communication_bus = get_communication_bus()
        self.openai_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=Exception
        )
        # Configure to use GPT-5.1 (default for content optimization)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Objection Handler",
            goal="Detect and handle common objections automatically",
            backstory="""You are an expert at identifying objection types (price, timing, need, competitor, team)
            and crafting responses that reframe the value proposition and address concerns.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Objection handler addressing concerns diplomatically
- tone:        Empathetic, understanding, value-focused
- warmth:      high
- conciseness: medium
- energy:      calm
- formality:   neutral
- emoji:       minimal
- humor:       light
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at identifying objection types (price, timing, need, competitor, team)
and crafting responses that reframe the value proposition and address concerns.""")
        )
    
    @log_agent_execution(agent_name="ObjectionHandlerAgent")
    @retry(max_attempts=3, backoff="exponential")
    def handle_objection(self, lead_id: str, objection_text: str) -> Dict[str, Any]:
        """Detect objection type and generate response."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        objection_type = self._detect_objection_type(objection_text)
        response = self._generate_response(objection_type, lead, objection_text)
        
        return {
            "lead_id": lead_id,
            "objection_type": objection_type,
            "response": response,
            "escalate_to_human": objection_type == "complex"
        }
    
    def _detect_objection_type(self, text: str) -> str:
        """Detect the type of objection."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["price", "cost", "expensive", "budget"]):
            return "price"
        elif any(word in text_lower for word in ["timing", "not now", "later", "q1"]):
            return "timing"
        elif any(word in text_lower for word in ["competitor", "already using", "alternative"]):
            return "competitor"
        elif any(word in text_lower for word in ["team", "decision", "need to discuss"]):
            return "team"
        elif any(word in text_lower for word in ["not interested", "no need"]):
            return "need"
        else:
            return "complex"
    
    def _generate_response(self, objection_type: str, lead: Dict, objection_text: str) -> str:
        """Generate a response to the objection."""
        responses = {
            "price": f"Hi {lead.get('first_name')},\n\nI understand cost is a concern. Our pricing is performance-based—you only pay 2.5% of ACV when meetings book. That means if a meeting doesn't book, you don't pay. Worth a quick chat to see if the ROI makes sense?\n\nBest,\nThe Team",
            "timing": f"Hi {lead.get('first_name')},\n\nTotally understand timing. When would be a better time? Q1? I can send you a quick playbook in the meantime—no strings attached.\n\nBest,\nThe Team",
            "competitor": f"Hi {lead.get('first_name')},\n\nGot it. If you're ever re-evaluating or hitting limitations, happy to show you how we handle [specific_differentiator]. No pressure.\n\nBest,\nThe Team",
            "team": f"Hi {lead.get('first_name')},\n\nMakes sense to involve the team. Happy to do a quick demo for the decision-makers. When works for them?\n\nBest,\nThe Team",
            "need": f"Hi {lead.get('first_name')},\n\nNo problem. If [specific_pain_point] ever becomes a priority, we're here. Good luck with everything!\n\nBest,\nThe Team",
            "complex": "This requires human review. Escalating to sales team."
        }
        
        return responses.get(objection_type, "Thank you for your feedback. We'll follow up soon.")


class EngagementAnalyzerAgent:
    """Agent 10: Track engagement and predict conversion."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1 (default for content optimization)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Engagement Analyst",
            goal="Analyze lead engagement patterns and predict conversion likelihood",
            backstory="""You are an expert at analyzing engagement data (opens, clicks, replies)
            to calculate engagement scores, predict conversion likelihood, and segment leads
            into hot/warm/cold categories.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Engagement analyst optimizing message performance
- tone:        Analytical, insight-driven, improvement-focused
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at analyzing engagement data (opens, clicks, replies)
to calculate engagement scores, predict conversion likelihood, and segment leads
into hot/warm/cold categories.""")
        )
    
    @log_agent_execution(agent_name="EngagementAnalyzerAgent")
    @retry(max_attempts=2)
    def analyze_engagement(self, lead_id: str) -> Dict[str, Any]:
        """Analyze engagement for a lead."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        # Get message engagement data (would come from messages table)
        opens = 0  # Would query messages table
        clicks = 0
        replies = 0
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(opens, clicks, replies)
        
        # Predict conversion likelihood
        conversion_likelihood = self._predict_conversion(engagement_score, opens, clicks, replies)
        
        # Segment
        if engagement_score >= 70:
            segment = "hot"
        elif engagement_score >= 40:
            segment = "warm"
        else:
            segment = "cold"
        
        # Recommend next action
        next_action = self._recommend_next_action(segment, engagement_score)
        
        return {
            "lead_id": lead_id,
            "engagement_score": engagement_score,
            "conversion_likelihood": conversion_likelihood,
            "segment": segment,
            "next_action": next_action,
            "metrics": {
                "opens": opens,
                "clicks": clicks,
                "replies": replies
            }
        }
    
    def _calculate_engagement_score(self, opens: int, clicks: int, replies: int) -> float:
        """Calculate engagement score 0-100."""
        # Weighted scoring
        score = (opens * 10) + (clicks * 20) + (replies * 50)
        return min(score, 100.0)
    
    def _predict_conversion(self, engagement_score: float, opens: int, clicks: int, replies: int) -> float:
        """Predict conversion likelihood 0-1."""
        if replies > 0:
            return 0.8
        if clicks > 0:
            return 0.5
        if opens > 0:
            return 0.3
        return 0.1
    
    def _recommend_next_action(self, segment: str, engagement_score: float) -> str:
        """Recommend next action based on segment."""
        if segment == "hot":
            return "send_meeting_request"
        elif segment == "warm":
            return "send_value_offer"
        else:
            return "pause_and_wait_for_trigger"

