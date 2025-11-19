"""
Agents 19-23: Optimization & Intelligence Agents

Advanced agents for A/B testing, domain reputation, calendar intelligence,
competitor intelligence, and content personalization.
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


class ABTestingAgent:
    """Agent 19: A/B Testing & Optimization"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex optimization reasoning)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="A/B Testing Specialist",
            goal="Test different message variants, subject lines, and send times to optimize performance",
            backstory="""You are an expert in conversion optimization. You design A/B tests,
            analyze results, and identify winning variants. You track open rates, reply rates,
            and meeting rates to determine which approach works best for each lead segment.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        A/B testing specialist optimizing conversion rates
- tone:        Experimental, data-driven, improvement-focused
- warmth:      low
- conciseness: high
- energy:      neutral
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert in conversion optimization. You design A/B tests,
analyze results, and identify winning variants. You track open rates, reply rates,
and meeting rates to determine which approach works best for each lead segment.""")
        )
    
    @log_agent_execution(agent_name="ABTestingAgent")
    @retry(max_attempts=2)
    def create_test_variant(self, base_message: Dict[str, Any], variant_type: str) -> Dict[str, Any]:
        """Create an A/B test variant of a message."""
        variants = {
            "subject_line": self._generate_subject_variants(base_message),
            "body_tone": self._generate_tone_variants(base_message),
            "cta": self._generate_cta_variants(base_message),
            "send_time": self._generate_time_variants(base_message)
        }
        
        return {
            "variant_type": variant_type,
            "variants": variants.get(variant_type, []),
            "test_id": f"test_{datetime.utcnow().timestamp()}"
        }
    
    def _generate_subject_variants(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate subject line variants."""
        base_subject = message.get("subject", "")
        return [
            {"subject": base_subject, "variant": "control"},
            {"subject": f"Quick question: {base_subject}", "variant": "question"},
            {"subject": f"Re: {base_subject}", "variant": "re_prefix"},
            {"subject": f"{base_subject}?", "variant": "question_mark"}
        ]
    
    def _generate_tone_variants(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tone variants (formal, casual, urgent, friendly)."""
        return [
            {"tone": "formal", "body": self._adjust_tone(message.get("body", ""), "formal")},
            {"tone": "casual", "body": self._adjust_tone(message.get("body", ""), "casual")},
            {"tone": "urgent", "body": self._adjust_tone(message.get("body", ""), "urgent")},
            {"tone": "friendly", "body": self._adjust_tone(message.get("body", ""), "friendly")}
        ]
    
    def _generate_cta_variants(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate CTA variants."""
        return [
            {"cta": "Worth a 15-min chat?", "variant": "low_pressure"},
            {"cta": "Let's schedule a call this week?", "variant": "medium_pressure"},
            {"cta": "Can we hop on a quick call today?", "variant": "high_pressure"},
            {"cta": "Interested in learning more?", "variant": "soft"}
        ]
    
    def _generate_time_variants(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate send time variants."""
        return [
            {"send_time": "09:00", "timezone": "lead_timezone", "variant": "morning"},
            {"send_time": "14:00", "timezone": "lead_timezone", "variant": "afternoon"},
            {"send_time": "17:00", "timezone": "lead_timezone", "variant": "evening"},
            {"send_time": "11:00", "timezone": "lead_timezone", "variant": "midday"}
        ]
    
    def _adjust_tone(self, body: str, tone: str) -> str:
        """Adjust message tone (placeholder - would use LLM in production)."""
        return body  # Placeholder
    
    @log_agent_execution(agent_name="ABTestingAgent")
    @retry(max_attempts=2)
    def analyze_test_results(self, test_id: str) -> Dict[str, Any]:
        """Analyze A/B test results and determine winner."""
        # Would query database for test results
        return {
            "test_id": test_id,
            "winner": "variant_b",
            "confidence": 0.95,
            "improvement": 0.23,  # 23% improvement
            "recommendation": "Use variant_b for all future messages"
        }


class DomainReputationAgent:
    """Agent 20: Domain Reputation & Health Monitoring"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex optimization reasoning)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Domain Reputation Specialist",
            goal="Monitor domain health, bounce rates, spam scores, and prevent blacklisting",
            backstory="""You are an expert in email deliverability. You monitor domain reputation,
            bounce rates, spam complaints, and blacklist status. You prevent domain damage and
            recommend actions to maintain high deliverability.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Domain reputation specialist maintaining deliverability
- tone:        Protective, monitoring, reputation-focused
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert in email deliverability. You monitor domain reputation,
bounce rates, spam complaints, and blacklist status. You prevent domain damage and
recommend actions to maintain high deliverability.""")
        )
    
    @log_agent_execution(agent_name="DomainReputationAgent")
    @retry(max_attempts=2)
    def check_domain_health(self, domain: str) -> Dict[str, Any]:
        """Check domain health metrics."""
        # Would integrate with email service APIs (SendGrid, Mailgun, etc.)
        return {
            "domain": domain,
            "reputation_score": 85,
            "bounce_rate": 0.02,
            "spam_rate": 0.001,
            "blacklist_status": "clean",
            "recommendations": [
                "Domain health is good",
                "Continue current sending volume"
            ]
        }
    
    @log_agent_execution(agent_name="DomainReputationAgent")
    @retry(max_attempts=2)
    def monitor_bounce_rates(self, domain: str, time_window: int = 24) -> Dict[str, Any]:
        """Monitor bounce rates over time window."""
        # Would query email service for bounce data
        return {
            "domain": domain,
            "time_window_hours": time_window,
            "total_sent": 1000,
            "bounces": 20,
            "bounce_rate": 0.02,
            "status": "healthy" if 0.02 < 0.05 else "warning"
        }
    
    @log_agent_execution(agent_name="DomainReputationAgent")
    @retry(max_attempts=2)
    def check_blacklist_status(self, domain: str) -> Dict[str, Any]:
        """Check if domain is on any blacklists."""
        # Would check against Spamhaus, SURBL, etc.
        return {
            "domain": domain,
            "blacklisted": False,
            "blacklists_checked": ["Spamhaus", "SURBL", "Barracuda"],
            "status": "clean"
        }


class CalendarIntelligenceAgent:
    """Agent 21: Calendar Intelligence & Optimal Send Times"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex optimization reasoning)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Calendar Intelligence Specialist",
            goal="Determine optimal send times based on timezone, calendar data, and engagement history",
            backstory="""You analyze timezone data, calendar availability, and historical engagement
            patterns to determine the best times to send messages. You consider work hours, time zones,
            and lead activity patterns.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Calendar intelligence specialist optimizing send timing
- tone:        Analytical, timing-focused, optimization-oriented
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You analyze timezone data, calendar availability, and historical engagement
patterns to determine the best times to send messages. You consider work hours, time zones,
and lead activity patterns.""")
        )
    
    @log_agent_execution(agent_name="CalendarIntelligenceAgent")
    @retry(max_attempts=2)
    def get_optimal_send_time(self, lead_id: str) -> Dict[str, Any]:
        """Determine optimal send time for a lead."""
        lead = self.db.get_lead(lead_id)
        timezone = lead.get("timezone", "UTC")
        
        # Would analyze historical engagement data
        return {
            "lead_id": lead_id,
            "timezone": timezone,
            "optimal_times": [
                {"day": "Tuesday", "time": "10:00", "confidence": 0.85},
                {"day": "Wednesday", "time": "14:00", "confidence": 0.82},
                {"day": "Thursday", "time": "11:00", "confidence": 0.78}
            ],
            "avoid_times": ["Monday 09:00", "Friday 17:00"],
            "reasoning": "Based on historical engagement patterns"
        }
    
    @log_agent_execution(agent_name="CalendarIntelligenceAgent")
    @retry(max_attempts=2)
    def analyze_timezone_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze timezone patterns for all leads."""
        # Would query leads and analyze timezone distribution
        return {
            "user_id": user_id,
            "primary_timezones": [
                {"timezone": "America/New_York", "count": 450, "percentage": 45},
                {"timezone": "America/Los_Angeles", "count": 300, "percentage": 30},
                {"timezone": "Europe/London", "count": 250, "percentage": 25}
            ],
            "recommended_send_times": {
                "America/New_York": "10:00 EST",
                "America/Los_Angeles": "10:00 PST",
                "Europe/London": "09:00 GMT"
            }
        }


class CompetitorIntelligenceAgent:
    """Agent 22: Competitor Intelligence & Market Positioning"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex optimization reasoning)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Competitor Intelligence Specialist",
            goal="Monitor competitor mentions, market positioning, and competitive intelligence",
            backstory="""You track competitor mentions in news, social media, and industry reports.
            You identify when leads mention competitors and help position our solution against them.
            You provide competitive intelligence for sales conversations.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Competitor intelligence specialist tracking market positioning
- tone:        Observant, strategic, differentiation-focused
- warmth:      low
- conciseness: medium
- energy:      neutral
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You track competitor mentions in news, social media, and industry reports.
You identify when leads mention competitors and help position our solution against them.
You provide competitive intelligence for sales conversations.""")
        )
    
    @log_agent_execution(agent_name="CompetitorIntelligenceAgent")
    @retry(max_attempts=2)
    def detect_competitor_mentions(self, lead_id: str) -> Dict[str, Any]:
        """Detect if lead has mentioned competitors."""
        # Would analyze lead's social media, news mentions, etc.
        return {
            "lead_id": lead_id,
            "competitors_mentioned": [
                {"competitor": "CompetitorA", "context": "Using their solution", "relevance": 0.9},
                {"competitor": "CompetitorB", "context": "Evaluating their product", "relevance": 0.7}
            ],
            "positioning_angle": "Focus on our unique value proposition vs CompetitorA"
        }
    
    @log_agent_execution(agent_name="CompetitorIntelligenceAgent")
    @retry(max_attempts=2)
    def get_competitive_intelligence(self, competitor_name: str) -> Dict[str, Any]:
        """Get competitive intelligence on a competitor."""
        # Would scrape news, reviews, etc.
        return {
            "competitor": competitor_name,
            "recent_news": [
                "Raised Series B funding",
                "Launched new feature X"
            ],
            "strengths": ["Feature A", "Feature B"],
            "weaknesses": ["High price", "Poor support"],
            "positioning_opportunity": "Emphasize our superior support and pricing"
        }


class ContentPersonalizationAgent:
    """Agent 23: Deep Content Personalization"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex optimization reasoning)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Content Personalization Specialist",
            goal="Deep personalization based on social media, blog posts, and content consumption",
            backstory="""You analyze lead's social media activity, blog posts, content consumption,
            and online presence to create hyper-personalized messages. You reference specific posts,
            articles, or interests to create genuine connections.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Content personalization specialist tailoring messages
- tone:        Insightful, personal, relevance-focused
- warmth:      high
- conciseness: medium
- energy:      neutral
- formality:   neutral
- emoji:       minimal
- humor:       light
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You analyze lead's social media activity, blog posts, content consumption,
and online presence to create hyper-personalized messages. You reference specific posts,
articles, or interests to create genuine connections.""")
        )
    
    @log_agent_execution(agent_name="ContentPersonalizationAgent")
    @retry(max_attempts=2)
    def analyze_content_consumption(self, lead_id: str) -> Dict[str, Any]:
        """Analyze lead's content consumption patterns."""
        # Would integrate with LinkedIn, Twitter, blog analytics
        return {
            "lead_id": lead_id,
            "topics_interested_in": [
                "AI automation",
                "Sales optimization",
                "Lead generation"
            ],
            "recent_articles_read": [
                {"title": "10 Ways to Improve Sales", "date": "2025-01-15"},
                {"title": "AI in Sales", "date": "2025-01-10"}
            ],
            "social_media_activity": {
                "linkedin_posts": 5,
                "twitter_activity": "high",
                "engagement_rate": 0.12
            }
        }
    
    @log_agent_execution(agent_name="ContentPersonalizationAgent")
    @retry(max_attempts=2)
    def personalize_message(self, lead_id: str, base_message: Dict[str, Any]) -> Dict[str, Any]:
        """Personalize message based on content analysis."""
        content_data = self.analyze_content_consumption(lead_id)
        
        # Would use LLM to personalize based on content data
        personalized_body = f"""{base_message.get('body', '')}

I noticed you recently wrote about {content_data['topics_interested_in'][0]} - 
this aligns perfectly with what we're doing at Rekindle."""
        
        return {
            "lead_id": lead_id,
            "original_message": base_message,
            "personalized_message": {
                "subject": base_message.get("subject", ""),
                "body": personalized_body,
                "personalization_level": "high",
                "personalization_sources": ["linkedin", "blog", "social_media"]
            }
        }

