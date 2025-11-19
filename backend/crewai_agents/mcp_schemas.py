"""
Model Context Protocol (MCP) Schemas

This file defines the standardized, rich data schemas that allow agents to pass
full context (research, RAG results, user history, intent) between each other
and to external tools.

These schemas are the "language" of the agents - they ensure consistent,
high-quality data flow throughout the system.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# CORE CONTEXT SCHEMAS
# ============================================================================

class LeadTier(str, Enum):
    """Lead scoring tier."""
    HOT = "hot"  # 80-100
    WARM = "warm"  # 60-79
    COLD = "cold"  # 0-59


class Channel(str, Enum):
    """Communication channels."""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    VOICEMAIL = "voicemail"
    LINKEDIN = "linkedin"


class Intent(str, Enum):
    """Message intent classification."""
    INITIAL_OUTREACH = "initial_outreach"
    FOLLOW_UP = "follow_up"
    RE_ENGAGEMENT = "re_engagement"
    VALUE_DELIVERY = "value_delivery"
    MEETING_REQUEST = "meeting_request"
    OBJECTION_HANDLING = "objection_handling"


class TriggerEvent(BaseModel):
    """A trigger event that indicates buying intent."""
    event_type: str = Field(..., description="Type of trigger (funding, hiring, job_change, etc.)")
    event_date: datetime = Field(..., description="When the event occurred")
    source: str = Field(..., description="Source of the event (LinkedIn, news, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional event details")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance to this lead 0-1")


class PainPoint(BaseModel):
    """A pain point identified for the lead."""
    pain_point: str = Field(..., description="Description of the pain point")
    severity: Literal["low", "medium", "high"] = Field(..., description="Severity level")
    source: str = Field(..., description="Where this pain point was identified")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class RevivalHook(BaseModel):
    """A hook that can be used to re-engage a dormant lead."""
    hook_type: str = Field(..., description="Type of hook (trigger_event, pain_point, social_proof, etc.)")
    hook_content: str = Field(..., description="The actual hook content/text")
    urgency_level: Literal["low", "medium", "high"] = Field(..., description="Urgency level")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score 0-1")
    source: str = Field(..., description="Source of the hook")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BestPractice(BaseModel):
    """A best practice from the RAG system."""
    category: str = Field(..., description="Category (email, subject_line, sequence, etc.)")
    content: str = Field(..., description="The best practice content")
    success_score: float = Field(..., ge=0.0, le=100.0, description="Success score 0-100")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context where this worked")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering")


class LeadFirmographics(BaseModel):
    """Firmographic data about the lead's company."""
    company_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None  # e.g., "10-50", "50-200", etc.
    revenue_range: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    technologies: List[str] = Field(default_factory=list, description="Tech stack")
    funding_stage: Optional[str] = None
    funding_amount: Optional[float] = None


class LeadProfile(BaseModel):
    """Profile data about the lead."""
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    seniority_level: Optional[str] = None  # e.g., "VP", "Director", "Manager"
    department: Optional[str] = None
    linkedin_url: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None


class EngagementHistory(BaseModel):
    """Historical engagement data for the lead."""
    total_messages_sent: int = 0
    total_replies: int = 0
    total_opens: int = 0
    total_clicks: int = 0
    last_contact_date: Optional[datetime] = None
    last_reply_date: Optional[datetime] = None
    last_open_date: Optional[datetime] = None
    engagement_score: float = Field(0.0, ge=0.0, le=1.0, description="Overall engagement score")
    preferred_channel: Optional[Channel] = None
    preferred_send_time: Optional[str] = None  # e.g., "09:00", "14:00"
    opt_out_status: bool = False


class LeadScoring(BaseModel):
    """Lead scoring data."""
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall score 0-100")
    tier: LeadTier = Field(..., description="Lead tier")
    recency_score: float = Field(..., ge=0.0, le=100.0)
    engagement_score: float = Field(..., ge=0.0, le=100.0)
    firmographic_score: float = Field(..., ge=0.0, le=100.0)
    job_signals_score: float = Field(..., ge=0.0, le=100.0)
    company_signals_score: float = Field(..., ge=0.0, le=100.0)
    breakdown: Dict[str, float] = Field(default_factory=dict, description="Detailed breakdown")


class ResearchData(BaseModel):
    """Comprehensive research data about the lead."""
    lead_id: str
    researched_at: datetime = Field(default_factory=datetime.utcnow)
    trigger_events: List[TriggerEvent] = Field(default_factory=list, description="Recent trigger events")
    pain_points: List[PainPoint] = Field(default_factory=list, description="Identified pain points")
    revival_hooks: List[RevivalHook] = Field(default_factory=list, description="Available revival hooks")
    company_news: List[Dict[str, Any]] = Field(default_factory=list, description="Recent company news")
    job_postings: List[Dict[str, Any]] = Field(default_factory=list, description="Relevant job postings")
    linkedin_updates: List[Dict[str, Any]] = Field(default_factory=list, description="LinkedIn updates")
    research_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Overall research confidence")
    research_sources: List[str] = Field(default_factory=list, description="Sources used")


class MessageContext(BaseModel):
    """Full context for message generation - THE CORE MCP SCHEMA."""
    # Lead Information
    lead_id: str
    lead_profile: LeadProfile
    lead_firmographics: LeadFirmographics
    lead_scoring: LeadScoring
    engagement_history: EngagementHistory
    
    # Research & Intelligence
    research_data: ResearchData
    
    # RAG & Best Practices
    best_practices: List[BestPractice] = Field(default_factory=list, description="Relevant best practices from RAG")
    
    # Campaign Context
    campaign_id: Optional[str] = None
    sequence_number: int = Field(1, ge=1, le=10, description="Message number in sequence")
    total_messages_in_sequence: int = Field(5, ge=1, le=10, description="Total messages in sequence")
    previous_messages: List[Dict[str, Any]] = Field(default_factory=list, description="Previous messages in sequence")
    
    # Message Intent
    intent: Intent = Field(..., description="Intent of this message")
    channel: Channel = Field(..., description="Channel for this message")
    
    # Brand & Voice
    brand_voice: Dict[str, Any] = Field(default_factory=dict, description="Brand voice guidelines")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    
    # ACV & Business Context
    estimated_acv: float = Field(0.0, ge=0.0, description="Estimated Annual Contract Value")
    deal_stage: Optional[str] = None
    previous_interactions: List[Dict[str, Any]] = Field(default_factory=list, description="Previous interactions")
    
    # Timing & Urgency
    urgency_level: Literal["low", "medium", "high"] = Field("medium", description="Urgency level")
    optimal_send_time: Optional[datetime] = None
    
    # Compliance & Safety
    compliance_flags: List[str] = Field(default_factory=list, description="Compliance flags to consider")
    suppression_list_checked: bool = False
    
    # Metadata
    context_version: str = Field("1.0", description="MCP schema version")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    context_id: Optional[str] = None  # Unique ID for this context instance


class GeneratedMessage(BaseModel):
    """A generated message following MCP standards."""
    message_id: Optional[str] = None
    lead_id: str
    channel: Channel
    intent: Intent
    
    # Message Content
    subject: Optional[str] = None  # For email
    body: str = Field(..., description="Message body")
    html_body: Optional[str] = None  # For email
    text_body: Optional[str] = None  # Plain text version
    
    # Personalization
    personalization_elements: List[str] = Field(default_factory=list, description="Elements that were personalized")
    trigger_references: List[str] = Field(default_factory=list, description="Trigger events referenced")
    pain_point_references: List[str] = Field(default_factory=list, description="Pain points referenced")
    
    # Quality Metrics
    quality_score: float = Field(0.0, ge=0.0, le=100.0, description="Quality score")
    personalization_score: float = Field(0.0, ge=0.0, le=100.0, description="Personalization score")
    compliance_score: float = Field(0.0, ge=0.0, le=100.0, description="Compliance score")
    
    # Context Used
    context_id: Optional[str] = None  # Links back to MessageContext
    best_practices_used: List[str] = Field(default_factory=list, description="Best practice IDs used")
    
    # Scheduling
    scheduled_send_time: Optional[datetime] = None
    priority: Literal["low", "medium", "high"] = Field("medium", description="Send priority")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field("WriterAgent", description="Agent that generated this")
    version: str = Field("1.0", description="Message schema version")


class MessageSequence(BaseModel):
    """A complete message sequence following MCP standards."""
    sequence_id: Optional[str] = None
    lead_id: str
    campaign_id: Optional[str] = None
    user_id: str
    
    # Sequence Configuration
    channels: List[Channel] = Field(..., description="Channels in sequence")
    total_messages: int = Field(..., ge=1, le=10, description="Total messages")
    cadence_days: List[int] = Field(default_factory=list, description="Days between messages")
    
    # Messages
    messages: List[GeneratedMessage] = Field(default_factory=list, description="Generated messages")
    
    # Context Used
    context: MessageContext = Field(..., description="Full context used for generation")
    
    # Quality Metrics
    overall_quality_score: float = Field(0.0, ge=0.0, le=100.0)
    personalization_score: float = Field(0.0, ge=0.0, le=100.0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["draft", "approved", "scheduled", "sending", "completed"] = Field("draft")


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_message_context(context: MessageContext) -> List[str]:
    """
    Validate a MessageContext and return any issues.
    
    Returns empty list if valid, list of error messages if invalid.
    """
    issues = []
    
    # Check required fields
    if not context.lead_id:
        issues.append("lead_id is required")
    
    if not context.research_data.trigger_events and context.intent == Intent.RE_ENGAGEMENT:
        issues.append("Re-engagement intent requires trigger events")
    
    if context.sequence_number > context.total_messages_in_sequence:
        issues.append("sequence_number cannot exceed total_messages_in_sequence")
    
    # Check scoring
    if context.lead_scoring.overall_score < 0 or context.lead_scoring.overall_score > 100:
        issues.append("lead_scoring.overall_score must be between 0 and 100")
    
    # Check engagement history
    if context.engagement_history.opt_out_status:
        issues.append("Lead has opted out - cannot send messages")
    
    return issues


def enrich_context_with_rag(context: MessageContext, rag_results: List[BestPractice]) -> MessageContext:
    """
    Enrich a MessageContext with RAG results.
    
    Filters and ranks best practices by relevance to the context.
    """
    # Filter by category and context
    relevant_practices = []
    
    for practice in rag_results:
        # Match by category
        if practice.category in ["email", "sequence", context.channel.value]:
            relevant_practices.append(practice)
        
        # Match by context (industry, company size, etc.)
        practice_context = practice.context
        if practice_context.get("industry") == context.lead_firmographics.industry:
            relevant_practices.append(practice)
    
    # Sort by success score
    relevant_practices.sort(key=lambda x: x.success_score, reverse=True)
    
    # Take top 3
    context.best_practices = relevant_practices[:3]
    
    return context


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "LeadTier",
    "Channel",
    "Intent",
    
    # Core Schemas
    "TriggerEvent",
    "PainPoint",
    "RevivalHook",
    "BestPractice",
    "LeadFirmographics",
    "LeadProfile",
    "EngagementHistory",
    "LeadScoring",
    "ResearchData",
    
    # Main MCP Schemas
    "MessageContext",
    "GeneratedMessage",
    "MessageSequence",
    
    # Helpers
    "validate_message_context",
    "enrich_context_with_rag",
]


