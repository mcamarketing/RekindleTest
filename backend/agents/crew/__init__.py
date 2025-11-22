"""
REX Special Forces - CrewAI Agent Modules

Production-grade AI agents built on CrewAI framework.
Each agent is deterministic-first with LLM assistance only where necessary.

Agents:
- ReviverAgent: Dead lead reactivation and qualification
- DeliverabilityAgent: Domain health monitoring and rotation
- PersonalizerAgent: Message personalization and timing optimization
- ICPIntelligenceAgent: ICP extraction and lead scoring
- ScraperAgent: Data enrichment and research
- OutreachAgent: Multi-channel message delivery
- AnalyticsAgent: Performance tracking and optimization
- SpecialForcesCoordinator: Crew-level orchestration

Author: RekindlePro Engineering
Version: 1.0.0
"""

__version__ = "1.0.0"

# Import agents
from .base_agent import BaseAgent, MissionContext, AgentResult
from .reviver_agent import ReviverAgent
from .deliverability_agent import DeliverabilityAgent
from .personalizer_agent import PersonalizerAgent
from .icp_intelligence_agent import ICPIntelligenceAgent
from .scraper_agent import ScraperAgent
from .outreach_agent import OutreachAgent
from .analytics_agent import AnalyticsAgent
from .special_forces_coordinator import SpecialForcesCoordinator

# Agent registry for dynamic loading
AGENT_REGISTRY = {
    'ReviverAgent': ReviverAgent,
    'DeliverabilityAgent': DeliverabilityAgent,
    'PersonalizerAgent': PersonalizerAgent,
    'ICPIntelligenceAgent': ICPIntelligenceAgent,
    'ScraperAgent': ScraperAgent,
    'OutreachAgent': OutreachAgent,
    'AnalyticsAgent': AnalyticsAgent,
    'SpecialForcesCoordinator': SpecialForcesCoordinator,
}


def register_agent(agent_class):
    """Decorator to register agents in the global registry"""
    AGENT_REGISTRY[agent_class.__name__] = agent_class
    return agent_class


def get_agent(agent_name: str):
    """Get agent class by name"""
    return AGENT_REGISTRY.get(agent_name)


__all__ = [
    "BaseAgent",
    "MissionContext",
    "AgentResult",
    "ReviverAgent",
    "DeliverabilityAgent",
    "PersonalizerAgent",
    "ICPIntelligenceAgent",
    "ScraperAgent",
    "OutreachAgent",
    "AnalyticsAgent",
    "SpecialForcesCoordinator",
    "AGENT_REGISTRY",
    "register_agent",
    "get_agent",
]
