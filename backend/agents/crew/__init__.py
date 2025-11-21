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

# Agent registry for dynamic loading
AGENT_REGISTRY = {}


def register_agent(agent_class):
    """Decorator to register agents in the global registry"""
    AGENT_REGISTRY[agent_class.__name__] = agent_class
    return agent_class


def get_agent(agent_name: str):
    """Get agent class by name"""
    return AGENT_REGISTRY.get(agent_name)


__all__ = [
    "AGENT_REGISTRY",
    "register_agent",
    "get_agent",
]
