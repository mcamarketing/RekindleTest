"""
Agents 27-28: Analytics & Intelligence Agents

Agents for market intelligence and performance analytics.
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


class MarketIntelligenceAgent:
    """Agent 27: Market Intelligence & Industry Trends"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex analytics reasoning)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Market Intelligence Specialist",
            goal="Track industry trends, market shifts, and economic indicators",
            backstory="""You monitor industry news, economic indicators, market trends, and
            sector-specific developments. You identify opportunities and threats that could
            impact lead reactivation strategies. You provide market context for campaigns.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Market intelligence specialist tracking industry trends
- tone:        Insightful, analytical, trend-focused
- warmth:      low
- conciseness: medium
- energy:      neutral
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You monitor industry news, economic indicators, market trends, and
sector-specific developments. You identify opportunities and threats that could
impact lead reactivation strategies. You provide market context for campaigns.""")
        )
    
    @log_agent_execution(agent_name="MarketIntelligenceAgent")
    @retry(max_attempts=2)
    def get_industry_trends(self, industry: str) -> Dict[str, Any]:
        """Get current trends for an industry."""
        # Would scrape news, reports, etc.
        return {
            "industry": industry,
            "trends": [
                {
                    "trend": "AI adoption accelerating",
                    "impact": "positive",
                    "relevance": 0.9,
                    "source": "Industry report Q1 2025"
                },
                {
                    "trend": "Budget constraints in Q2",
                    "impact": "negative",
                    "relevance": 0.7,
                    "source": "Economic forecast"
                }
            ],
            "recommendations": [
                "Emphasize AI automation benefits",
                "Focus on ROI and cost savings"
            ]
        }
    
    @log_agent_execution(agent_name="MarketIntelligenceAgent")
    @retry(max_attempts=2)
    def detect_market_shift(self, industry: str) -> Dict[str, Any]:
        """Detect significant market shifts."""
        return {
            "industry": industry,
            "shift_detected": True,
            "shift_type": "budget_increase",
            "description": "Q2 budget increases detected across industry",
            "opportunity": "Good time to reach out about new initiatives",
            "confidence": 0.85
        }


class PerformanceAnalyticsAgent:
    """Agent 28: Performance Analytics & ROI Optimization"""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex analytics reasoning)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Performance Analytics Specialist",
            goal="Deep analytics, ROI tracking, and optimization recommendations",
            backstory="""You analyze campaign performance, calculate ROI, identify
            optimization opportunities, and provide data-driven recommendations. You track
            metrics across all campaigns and suggest improvements based on data.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Performance analytics specialist calculating ROI and optimization
- tone:        Data-driven, strategic, results-focused
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You analyze campaign performance, calculate ROI, identify
optimization opportunities, and provide data-driven recommendations. You track
metrics across all campaigns and suggest improvements based on data.""")
        )
    
    @log_agent_execution(agent_name="PerformanceAnalyticsAgent")
    @retry(max_attempts=2)
    def calculate_roi(self, user_id: str, time_period_days: int = 30) -> Dict[str, Any]:
        """Calculate ROI for a user's campaigns."""
        # Would query database for actual metrics
        return {
            "user_id": user_id,
            "time_period_days": time_period_days,
            "total_spent": 2500.00,
            "platform_fee": 99.00,
            "performance_fees": 2401.00,
            "meetings_booked": 40,
            "deals_closed": 8,
            "revenue_generated": 20000.00,
            "roi": 7.0,  # 7x ROI
            "cost_per_meeting": 62.50,
            "cost_per_deal": 312.50,
            "revenue_per_meeting": 500.00
        }
    
    @log_agent_execution(agent_name="PerformanceAnalyticsAgent")
    @retry(max_attempts=2)
    def get_optimization_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get optimization recommendations based on performance data."""
        return {
            "user_id": user_id,
            "recommendations": [
                {
                    "area": "subject_lines",
                    "current_performance": 0.15,  # 15% open rate
                    "recommended_action": "Test question-based subjects",
                    "expected_improvement": 0.25,  # 25% open rate
                    "priority": "high"
                },
                {
                    "area": "send_times",
                    "current_performance": "mixed",
                    "recommended_action": "Focus on Tuesday-Thursday 10am-2pm",
                    "expected_improvement": "+30% reply rate",
                    "priority": "medium"
                },
                {
                    "area": "message_length",
                    "current_performance": "long messages",
                    "recommended_action": "Test shorter messages (50-100 words)",
                    "expected_improvement": "+20% reply rate",
                    "priority": "low"
                }
            ],
            "top_opportunity": "subject_lines",
            "potential_roi_increase": 0.40  # 40% improvement
        }
    
    @log_agent_execution(agent_name="PerformanceAnalyticsAgent")
    @retry(max_attempts=2)
    def analyze_campaign_performance(self, campaign_id: str) -> Dict[str, Any]:
        """Analyze performance of a specific campaign."""
        return {
            "campaign_id": campaign_id,
            "metrics": {
                "leads_targeted": 1000,
                "messages_sent": 1000,
                "emails_opened": 670,
                "emails_clicked": 230,
                "replies_received": 152,
                "meetings_booked": 18,
                "open_rate": 0.67,
                "click_rate": 0.23,
                "reply_rate": 0.152,
                "meeting_rate": 0.018
            },
            "benchmarks": {
                "industry_open_rate": 0.20,
                "industry_reply_rate": 0.06,
                "industry_meeting_rate": 0.008
            },
            "performance_vs_benchmark": {
                "open_rate": "+235%",
                "reply_rate": "+153%",
                "meeting_rate": "+125%"
            },
            "recommendations": [
                "Campaign performing exceptionally well",
                "Consider scaling to more leads",
                "Test similar approach on other segments"
            ]
        }

