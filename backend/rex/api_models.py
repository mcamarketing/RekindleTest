"""
REX API Models - Pydantic schemas for request/response validation

All API contracts for Rex command, agent webhooks, domain management
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class MissionTypeEnum(str, Enum):
    """Mission types matching database schema"""
    LEAD_REACTIVATION = "lead_reactivation"
    CAMPAIGN_EXECUTION = "campaign_execution"
    ICP_EXTRACTION = "icp_extraction"
    DOMAIN_ROTATION = "domain_rotation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ERROR_RECOVERY = "error_recovery"


class MissionStateEnum(str, Enum):
    """Mission states matching database schema"""
    QUEUED = "queued"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


class DomainWarmupStateEnum(str, Enum):
    """Domain warmup states"""
    COLD = "cold"
    WARMING = "warming"
    WARM = "warm"
    COOLING = "cooling"
    BURNED = "burned"
    RETIRED = "retired"


class InboxStatusEnum(str, Enum):
    """Inbox status values"""
    PENDING_SETUP = "pending_setup"
    ACTIVE = "active"
    WARMING = "warming"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    DELETED = "deleted"


# ============================================================================
# REX COMMAND API
# ============================================================================

class CreateMissionRequest(BaseModel):
    """Request to create a new mission"""
    user_id: str = Field(..., description="User ID who owns this mission")
    type: MissionTypeEnum = Field(..., description="Type of mission to execute")
    priority: int = Field(50, ge=0, le=100, description="Mission priority (0-100)")
    campaign_id: Optional[str] = Field(None, description="Campaign ID if applicable")
    lead_ids: Optional[List[str]] = Field(None, description="Lead IDs to process")
    custom_params: Optional[Dict[str, Any]] = Field(None, description="Additional mission parameters")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "type": "lead_reactivation",
                "priority": 75,
                "campaign_id": "campaign_123",
                "lead_ids": ["lead_1", "lead_2", "lead_3"],
                "custom_params": {
                    "reactivation_strategy": "aggressive",
                    "max_touchpoints": 5
                }
            }
        }


class CreateMissionResponse(BaseModel):
    """Response after mission creation"""
    mission_id: str = Field(..., description="Unique mission ID")
    state: MissionStateEnum = Field(..., description="Current mission state")
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion timestamp")
    message: str = Field("Mission created successfully", description="Response message")

    class Config:
        schema_extra = {
            "example": {
                "mission_id": "mission_abc123",
                "state": "queued",
                "estimated_completion_time": "2025-11-22T15:30:00Z",
                "message": "Mission created successfully"
            }
        }


class MissionStatusRequest(BaseModel):
    """Request to get mission status"""
    mission_id: str = Field(..., description="Mission ID to query")
    include_logs: bool = Field(False, description="Include agent logs in response")
    include_tasks: bool = Field(False, description="Include task details in response")


class MissionStatusResponse(BaseModel):
    """Response with mission status"""
    mission_id: str
    state: MissionStateEnum
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress percentage (0.0-1.0)")
    created_at: datetime
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_crew: Optional[str] = None
    outcome: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    logs: Optional[List[Dict[str, Any]]] = None
    tasks: Optional[List[Dict[str, Any]]] = None


class CancelMissionRequest(BaseModel):
    """Request to cancel a mission"""
    mission_id: str = Field(..., description="Mission ID to cancel")
    reason: Optional[str] = Field(None, description="Reason for cancellation")


class CancelMissionResponse(BaseModel):
    """Response after mission cancellation"""
    mission_id: str
    cancelled: bool
    state: MissionStateEnum
    message: str


# ============================================================================
# AGENT WEBHOOK API
# ============================================================================

class AgentMissionUpdateRequest(BaseModel):
    """Agent update on mission progress"""
    mission_id: str = Field(..., description="Mission ID being worked on")
    agent_name: str = Field(..., description="Name of the agent")
    event_type: str = Field(..., description="Event type (mission_started, mission_progress, etc)")
    progress: Optional[float] = Field(None, ge=0.0, le=1.0, description="Progress percentage")
    data: Optional[Dict[str, Any]] = Field(None, description="Event-specific data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if any")

    @validator('event_type')
    def validate_event_type(cls, v):
        valid_types = [
            'mission_started', 'mission_progress', 'mission_completed',
            'mission_failed', 'mission_error', 'llm_call', 'tool_execution',
            'decision_made', 'resource_allocated', 'domain_rotated', 'api_call'
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid event_type. Must be one of: {', '.join(valid_types)}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "mission_id": "mission_abc123",
                "agent_name": "ReviverAgent",
                "event_type": "mission_progress",
                "progress": 0.45,
                "data": {
                    "leads_processed": 45,
                    "leads_qualified": 12,
                    "current_step": "scoring"
                }
            }
        }


class AgentMissionUpdateResponse(BaseModel):
    """Response to agent update"""
    acknowledged: bool = True
    next_action: Optional[str] = Field(None, description="Next action for agent to take")
    message: str = "Update received"


class AgentStatusRequest(BaseModel):
    """Request agent health status"""
    agent_name: Optional[str] = Field(None, description="Specific agent name, or all if None")
    crew_name: Optional[str] = Field(None, description="Filter by crew name")


class AgentStatusResponse(BaseModel):
    """Agent health status response"""
    agents: Dict[str, Dict[str, Any]] = Field(..., description="Agent status by name")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "agents": {
                    "ReviverAgent": {
                        "status": "idle",
                        "current_mission": None,
                        "missions_handled": 156,
                        "success_rate": 0.94,
                        "avg_duration_ms": 45000,
                        "last_activity": "2025-11-22T14:30:00Z"
                    },
                    "PersonalizerAgent": {
                        "status": "executing",
                        "current_mission": "mission_xyz789",
                        "missions_handled": 203,
                        "success_rate": 0.97,
                        "avg_duration_ms": 12000,
                        "last_activity": "2025-11-22T14:35:00Z"
                    }
                },
                "timestamp": "2025-11-22T14:35:30Z"
            }
        }


# ============================================================================
# DOMAIN MANAGEMENT API
# ============================================================================

class DomainAllocationRequest(BaseModel):
    """Request to allocate a domain for a campaign"""
    user_id: str = Field(..., description="User ID")
    campaign_id: str = Field(..., description="Campaign ID")
    preferred_domain: Optional[str] = Field(None, description="Preferred domain if available")
    min_reputation_score: float = Field(0.7, ge=0.0, le=1.0, description="Minimum reputation score required")


class DomainAllocationResponse(BaseModel):
    """Response with allocated domain"""
    domain: str = Field(..., description="Allocated domain")
    domain_id: str = Field(..., description="Domain database ID")
    reputation_score: float = Field(..., description="Current reputation score")
    warmup_state: DomainWarmupStateEnum = Field(..., description="Warmup state")
    daily_send_limit: int = Field(..., description="Daily send limit")
    emails_sent_today: int = Field(..., description="Emails sent today")
    available_capacity: int = Field(..., description="Remaining capacity today")

    class Config:
        schema_extra = {
            "example": {
                "domain": "mail.example.com",
                "domain_id": "domain_123",
                "reputation_score": 0.92,
                "warmup_state": "warm",
                "daily_send_limit": 300,
                "emails_sent_today": 87,
                "available_capacity": 213
            }
        }


class StartDomainWarmupRequest(BaseModel):
    """Request to start domain warmup"""
    domain: str = Field(..., description="Domain to warm up")
    user_id: str = Field(..., description="User ID who owns the domain")


class StartDomainWarmupResponse(BaseModel):
    """Response after starting warmup"""
    domain: str
    warmup_state: DomainWarmupStateEnum
    warmup_day: int = 1
    target_emails_today: int
    warmup_schedule: List[Dict[str, Any]]
    estimated_completion_date: datetime


class DomainHealthCheckRequest(BaseModel):
    """Request domain health check"""
    domain: str = Field(..., description="Domain to check")


class DomainHealthCheckResponse(BaseModel):
    """Domain health check results"""
    domain: str
    health_status: str = Field(..., description="excellent, good, fair, or poor")
    reputation_score: float
    deliverability_score: float
    bounce_rate: float
    spam_complaint_rate: float
    should_rotate: bool = Field(..., description="Whether domain should be rotated")
    rotation_reason: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)

    class Config:
        schema_extra = {
            "example": {
                "domain": "mail.example.com",
                "health_status": "good",
                "reputation_score": 0.85,
                "deliverability_score": 0.91,
                "bounce_rate": 0.03,
                "spam_complaint_rate": 0.0005,
                "should_rotate": False,
                "rotation_reason": None,
                "recommendations": [
                    "Continue monitoring bounce rate",
                    "Maintain current sending volume"
                ]
            }
        }


class TriggerDomainRotationRequest(BaseModel):
    """Request to rotate a domain"""
    domain: str = Field(..., description="Domain to rotate")
    reason: str = Field(..., description="Reason for rotation")
    immediate: bool = Field(False, description="Whether to rotate immediately or schedule")


class TriggerDomainRotationResponse(BaseModel):
    """Response after triggering rotation"""
    domain: str
    rotated: bool
    new_state: DomainWarmupStateEnum
    replacement_domain: Optional[str] = None
    rotation_mission_id: Optional[str] = None


# ============================================================================
# INBOX MANAGEMENT API
# ============================================================================

class AllocateInboxRequest(BaseModel):
    """Request to allocate inbox for campaign"""
    user_id: str
    campaign_id: str
    preferred_provider: Optional[str] = Field(None, description="sendgrid, gmail, outlook, custom_smtp")


class AllocateInboxResponse(BaseModel):
    """Response with allocated inbox"""
    inbox_id: str
    email_address: str
    provider: str
    status: InboxStatusEnum
    daily_send_limit: int
    emails_sent_today: int
    available_capacity: int


class UpgradeInboxTierRequest(BaseModel):
    """Request to upgrade inbox tier"""
    inbox_id: str
    new_tier: str = Field(..., description="free, starter, pro, enterprise")
    stripe_subscription_id: Optional[str] = None


class UpgradeInboxTierResponse(BaseModel):
    """Response after tier upgrade"""
    inbox_id: str
    new_tier: str
    daily_send_limit: int
    price_per_month: float
    features: Dict[str, Any]


# ============================================================================
# LLM WEBHOOK API
# ============================================================================

class LLMCallbackRequest(BaseModel):
    """Webhook callback from LLM processing"""
    correlation_id: str = Field(..., description="Correlation ID for tracking")
    mission_id: Optional[str] = None
    agent_name: str
    prompt_hash: str = Field(..., description="SHA-256 hash of prompt for audit")
    response: Dict[str, Any] = Field(..., description="LLM response")
    model: str = Field(..., description="Model used (gpt-4, etc)")
    tokens_used: int
    cost_usd: float
    duration_ms: int


class LLMCallbackResponse(BaseModel):
    """Response to LLM callback"""
    acknowledged: bool = True
    logged: bool = True
    message: str = "LLM callback processed"


# ============================================================================
# BULK OPERATIONS
# ============================================================================

class BulkMissionCreateRequest(BaseModel):
    """Create multiple missions in batch"""
    missions: List[CreateMissionRequest] = Field(..., max_items=100, description="Max 100 missions per batch")


class BulkMissionCreateResponse(BaseModel):
    """Response for bulk mission creation"""
    created_count: int
    failed_count: int
    mission_ids: List[str]
    errors: Optional[List[Dict[str, Any]]] = None
