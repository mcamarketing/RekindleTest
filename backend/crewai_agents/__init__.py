"""
Rekindle CrewAI Agents Package

All 18 agents for lead reactivation and campaign management.
"""

from .agents.researcher_agents import ResearcherAgent
from .agents.intelligence_agents import ICPAnalyzerAgent, LeadScorerAgent, LeadSourcerAgent
from .agents.dead_lead_reactivation_agent import DeadLeadReactivationAgent
from .agents.writer_agents import WriterAgent
from .agents.content_agents import (
    SubjectLineOptimizerAgent,
    FollowUpAgent,
    ObjectionHandlerAgent,
    EngagementAnalyzerAgent
)
from .agents.sync_agents import TrackerAgent, SynchronizerAgent
from .agents.revenue_agents import MeetingBookerAgent, BillingAgent
from .agents.launch_agents import OrchestratorAgent
from .agents.safety_agents import ComplianceAgent, QualityControlAgent, RateLimitAgent
from .tools.db_tools import SupabaseDB
from .tools.linkedin_mcp_tools import LinkedInMCPTool

__all__ = [
    # Research & Intelligence (4)
    "ResearcherAgent",
    "ICPAnalyzerAgent",
    "LeadScorerAgent",
    "LeadSourcerAgent",
    
    # Dead Lead Reactivation (1)
    "DeadLeadReactivationAgent",
    
    # Content Generation (4)
    "WriterAgent",
    "SubjectLineOptimizerAgent",
    "FollowUpAgent",
    "ObjectionHandlerAgent",
    "EngagementAnalyzerAgent",
    
    # Campaign Management (2)
    "TrackerAgent",
    "SynchronizerAgent",
    
    # Revenue & Sync (2)
    "MeetingBookerAgent",
    "BillingAgent",
    
    # Orchestration (1)
    "OrchestratorAgent",
    
    # Safety & Compliance (3)
    "ComplianceAgent",
    "QualityControlAgent",
    "RateLimitAgent",
    
    # Tools
    "SupabaseDB",
    "LinkedInMCPTool"
]









