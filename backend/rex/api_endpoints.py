"""
REX API Endpoints - FastAPI route handlers for Rex command and agent webhooks

All endpoints use Pydantic models from api_models.py for validation.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from supabase import create_client, Client
import os
import redis.asyncio as redis
import json

from .api_models import (
    # Mission Management
    CreateMissionRequest,
    CreateMissionResponse,
    MissionStatusRequest,
    MissionStatusResponse,
    CancelMissionRequest,
    CancelMissionResponse,
    BulkMissionCreateRequest,
    BulkMissionCreateResponse,

    # Agent Webhooks
    AgentMissionUpdateRequest,
    AgentMissionUpdateResponse,
    AgentStatusRequest,
    AgentStatusResponse,

    # Domain Management
    DomainAllocationRequest,
    DomainAllocationResponse,
    StartDomainWarmupRequest,
    StartDomainWarmupResponse,
    DomainHealthCheckRequest,
    DomainHealthCheckResponse,
    TriggerDomainRotationRequest,
    TriggerDomainRotationResponse,

    # Inbox Management
    AllocateInboxRequest,
    AllocateInboxResponse,
    UpgradeInboxTierRequest,
    UpgradeInboxTierResponse,

    # LLM Callbacks
    LLMCallbackRequest,
    LLMCallbackResponse,

    # Enums
    MissionStateEnum,
)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration missing"
        )

    return create_client(supabase_url, supabase_key)


async def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    try:
        client = redis.from_url(redis_url, decode_responses=True)
        await client.ping()
        return client
    except Exception as e:
        # Redis is optional for MVP - log warning and continue
        print(f"Warning: Redis unavailable: {e}")
        return None


# ============================================================================
# ROUTERS
# ============================================================================

rex_router = APIRouter(prefix="/rex", tags=["Rex Command"])
agent_router = APIRouter(prefix="/agents", tags=["Agent Webhooks"])
domain_router = APIRouter(prefix="/domain", tags=["Domain Management"])
inbox_router = APIRouter(prefix="/inbox", tags=["Inbox Management"])
webhook_router = APIRouter(prefix="/webhook", tags=["Webhooks"])


# ============================================================================
# REX COMMAND ENDPOINTS
# ============================================================================

@rex_router.post("/command", response_model=CreateMissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(
    request: CreateMissionRequest,
    db: Client = Depends(get_supabase_client)
) -> CreateMissionResponse:
    """
    Create a new mission for Rex to execute.

    This is the primary endpoint for commanding Rex to perform tasks like:
    - Lead reactivation campaigns
    - ICP extraction from CRM data
    - Domain rotation
    - Performance optimization
    """
    try:
        # Insert mission into database
        mission_data = {
            "user_id": request.user_id,
            "type": request.type.value,
            "state": MissionStateEnum.QUEUED.value,
            "priority": request.priority,
            "campaign_id": request.campaign_id,
            "lead_ids": request.lead_ids,
            "custom_params": request.custom_params or {},
            "created_at": datetime.utcnow().isoformat(),
        }

        result = db.table("rex_missions").insert(mission_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create mission"
            )

        mission = result.data[0]

        # Estimate completion time (rough heuristic based on mission type)
        estimated_hours = {
            "lead_reactivation": 2,
            "campaign_execution": 4,
            "icp_extraction": 1,
            "domain_rotation": 0.5,
            "performance_optimization": 3,
            "error_recovery": 1,
        }

        hours = estimated_hours.get(request.type.value, 2)
        from datetime import timedelta
        estimated_completion = datetime.utcnow() + timedelta(hours=hours)

        # Log mission creation
        db.table("agent_logs").insert({
            "mission_id": mission["id"],
            "agent_name": "RexCommandAPI",
            "event_type": "custom",
            "data": {
                "event": "mission_created",
                "type": request.type.value,
                "priority": request.priority,
            }
        }).execute()

        return CreateMissionResponse(
            mission_id=mission["id"],
            state=MissionStateEnum.QUEUED,
            estimated_completion_time=estimated_completion,
            message=f"Mission created successfully: {request.type.value}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create mission: {str(e)}"
        )


@rex_router.get("/command/{mission_id}", response_model=MissionStatusResponse)
async def get_mission_status(
    mission_id: str,
    include_logs: bool = False,
    include_tasks: bool = False,
    db: Client = Depends(get_supabase_client)
) -> MissionStatusResponse:
    """
    Get the current status of a mission.

    Optionally include agent logs and task details for debugging.
    """
    try:
        # Fetch mission
        result = db.table("rex_missions").select("*").eq("id", mission_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mission not found: {mission_id}"
            )

        mission = result.data[0]

        # Calculate progress based on state
        state_progress_map = {
            "queued": 0.0,
            "assigned": 0.1,
            "executing": 0.3,
            "collecting": 0.5,
            "analyzing": 0.7,
            "optimizing": 0.9,
            "completed": 1.0,
            "failed": 0.0,
        }

        progress = state_progress_map.get(mission["state"], 0.0)

        # Optionally fetch logs
        logs = None
        if include_logs:
            logs_result = db.table("agent_logs")\
                .select("*")\
                .eq("mission_id", mission_id)\
                .order("timestamp", desc=False)\
                .execute()
            logs = logs_result.data if logs_result.data else []

        # Optionally fetch tasks (placeholder - tasks table not yet implemented)
        tasks = None
        if include_tasks:
            tasks = []  # TODO: Implement tasks table and fetch

        return MissionStatusResponse(
            mission_id=mission["id"],
            state=MissionStateEnum(mission["state"]),
            progress=progress,
            created_at=mission["created_at"],
            assigned_at=mission.get("assigned_at"),
            started_at=mission.get("started_at"),
            completed_at=mission.get("completed_at"),
            assigned_crew=mission.get("assigned_crew"),
            outcome=mission.get("outcome"),
            metrics=mission.get("metrics"),
            error=mission.get("error"),
            logs=logs,
            tasks=tasks,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mission status: {str(e)}"
        )


@rex_router.post("/command/{mission_id}/cancel", response_model=CancelMissionResponse)
async def cancel_mission(
    mission_id: str,
    request: CancelMissionRequest,
    db: Client = Depends(get_supabase_client)
) -> CancelMissionResponse:
    """
    Cancel a running or queued mission.
    """
    try:
        # Fetch mission
        result = db.table("rex_missions").select("*").eq("id", mission_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mission not found: {mission_id}"
            )

        mission = result.data[0]
        current_state = mission["state"]

        # Only allow cancellation of queued, assigned, or executing missions
        if current_state in ["completed", "failed"]:
            return CancelMissionResponse(
                mission_id=mission_id,
                cancelled=False,
                state=MissionStateEnum(current_state),
                message=f"Cannot cancel mission in {current_state} state"
            )

        # Update mission state to failed with cancellation reason
        db.table("rex_missions").update({
            "state": "failed",
            "completed_at": datetime.utcnow().isoformat(),
            "error": {
                "code": "CANCELLED",
                "message": request.reason or "Mission cancelled by user"
            }
        }).eq("id", mission_id).execute()

        # Log cancellation
        db.table("agent_logs").insert({
            "mission_id": mission_id,
            "agent_name": "RexCommandAPI",
            "event_type": "custom",
            "data": {
                "event": "mission_cancelled",
                "reason": request.reason,
                "previous_state": current_state,
            }
        }).execute()

        return CancelMissionResponse(
            mission_id=mission_id,
            cancelled=True,
            state=MissionStateEnum.FAILED,
            message=f"Mission cancelled: {request.reason or 'User requested'}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel mission: {str(e)}"
        )


@rex_router.post("/command/bulk", response_model=BulkMissionCreateResponse)
async def bulk_create_missions(
    request: BulkMissionCreateRequest,
    db: Client = Depends(get_supabase_client)
) -> BulkMissionCreateResponse:
    """
    Create multiple missions in a single batch (max 100).
    """
    created_count = 0
    failed_count = 0
    mission_ids = []
    errors = []

    for mission_request in request.missions:
        try:
            # Reuse single mission creation logic
            mission_data = {
                "user_id": mission_request.user_id,
                "type": mission_request.type.value,
                "state": MissionStateEnum.QUEUED.value,
                "priority": mission_request.priority,
                "campaign_id": mission_request.campaign_id,
                "lead_ids": mission_request.lead_ids,
                "custom_params": mission_request.custom_params or {},
                "created_at": datetime.utcnow().isoformat(),
            }

            result = db.table("rex_missions").insert(mission_data).execute()

            if result.data:
                mission_ids.append(result.data[0]["id"])
                created_count += 1
            else:
                failed_count += 1
                errors.append({
                    "type": mission_request.type.value,
                    "error": "Failed to insert mission"
                })

        except Exception as e:
            failed_count += 1
            errors.append({
                "type": mission_request.type.value,
                "error": str(e)
            })

    return BulkMissionCreateResponse(
        created_count=created_count,
        failed_count=failed_count,
        mission_ids=mission_ids,
        errors=errors if errors else None
    )


# ============================================================================
# AGENT WEBHOOK ENDPOINTS
# ============================================================================

@agent_router.post("/mission", response_model=AgentMissionUpdateResponse)
async def agent_mission_update(
    request: AgentMissionUpdateRequest,
    db: Client = Depends(get_supabase_client),
    redis_client: Optional[redis.Redis] = Depends(get_redis_client)
) -> AgentMissionUpdateResponse:
    """
    Webhook for agents to report mission progress.

    Agents call this endpoint to:
    - Report mission started
    - Update progress percentage
    - Report completion or failure
    - Log decisions, LLM calls, tool executions
    """
    try:
        # Log the agent event
        log_data = {
            "mission_id": request.mission_id,
            "agent_name": request.agent_name,
            "event_type": request.event_type,
            "data": request.data or {},
            "error_code": request.error.get("code") if request.error else None,
            "error_message": request.error.get("message") if request.error else None,
            "timestamp": datetime.utcnow().isoformat(),
        }

        db.table("agent_logs").insert(log_data).execute()

        # Update mission state based on event type
        mission_updates = {}

        if request.event_type == "mission_started":
            mission_updates["state"] = "executing"
            mission_updates["started_at"] = datetime.utcnow().isoformat()
            mission_updates["assigned_crew"] = request.agent_name

        elif request.event_type == "mission_progress":
            # Keep state as executing, just update progress in data
            pass

        elif request.event_type == "mission_completed":
            mission_updates["state"] = "completed"
            mission_updates["completed_at"] = datetime.utcnow().isoformat()
            mission_updates["outcome"] = request.data or {}

        elif request.event_type in ["mission_failed", "mission_error"]:
            mission_updates["state"] = "failed"
            mission_updates["completed_at"] = datetime.utcnow().isoformat()
            mission_updates["error"] = request.error or {}

        # Apply updates to mission
        if mission_updates:
            db.table("rex_missions")\
                .update(mission_updates)\
                .eq("id", request.mission_id)\
                .execute()

        # Publish update to Redis pub/sub for real-time UI updates
        if redis_client:
            try:
                await redis_client.publish(
                    f"mission:{request.mission_id}",
                    json.dumps({
                        "event_type": request.event_type,
                        "agent_name": request.agent_name,
                        "progress": request.progress,
                        "data": request.data,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                )
            except Exception as e:
                print(f"Warning: Failed to publish to Redis: {e}")

        return AgentMissionUpdateResponse(
            acknowledged=True,
            next_action=None,  # Could add decision logic here for agent guidance
            message="Update received successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process agent update: {str(e)}"
        )


@agent_router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status(
    agent_name: Optional[str] = None,
    crew_name: Optional[str] = None,
    db: Client = Depends(get_supabase_client)
) -> AgentStatusResponse:
    """
    Get health status of agents.

    Returns statistics like missions handled, success rate, avg duration.
    """
    try:
        # Use the database view/function to get agent activity summary
        # This is a simplified version - full implementation would call the SQL function

        query = db.rpc("get_agent_activity_summary", {
            "p_agent_name": agent_name,
            "p_hours": 24
        })

        result = query.execute()

        # Transform to expected format
        agents = {}
        if result.data:
            for row in result.data:
                agents[row["agent_name"]] = {
                    "status": "idle",  # Would need live tracking
                    "current_mission": None,
                    "missions_handled": row.get("total_missions", 0),
                    "success_rate": row.get("success_rate", 0.0),
                    "avg_duration_ms": row.get("avg_duration_ms", 0),
                    "last_activity": row.get("last_activity"),
                }

        return AgentStatusResponse(
            agents=agents,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        # Fallback if function doesn't exist yet
        return AgentStatusResponse(
            agents={},
            timestamp=datetime.utcnow()
        )


# ============================================================================
# DOMAIN MANAGEMENT ENDPOINTS
# ============================================================================

@domain_router.post("/assign", response_model=DomainAllocationResponse)
async def allocate_domain(
    request: DomainAllocationRequest,
    db: Client = Depends(get_supabase_client)
) -> DomainAllocationResponse:
    """
    Allocate a warmed domain for a campaign.

    Finds the best available domain based on:
    - Warmup state (must be 'warm')
    - Reputation score (meets minimum threshold)
    - Available capacity
    """
    try:
        # Build query for available domains
        query = db.table("rex_domain_pool")\
            .select("*")\
            .eq("warmup_state", "warm")\
            .eq("status", "active")\
            .gte("reputation_score", request.min_reputation_score)\
            .is_("assigned_to_campaign", "null")

        # Filter by user's domains or shared pool
        query = query.or_(f"user_id.eq.{request.user_id},type.eq.prewarmed")

        # Prefer requested domain if available
        if request.preferred_domain:
            query = query.eq("domain", request.preferred_domain)

        # Order by reputation score (best first)
        result = query.order("reputation_score", desc=True).limit(1).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No available warm domains matching criteria"
            )

        domain = result.data[0]

        # Assign domain to campaign
        db.table("rex_domain_pool").update({
            "assigned_to_campaign": request.campaign_id,
            "user_id": request.user_id,
            "last_used_at": datetime.utcnow().isoformat(),
        }).eq("id", domain["id"]).execute()

        # Log allocation
        db.table("agent_logs").insert({
            "agent_name": "DomainAllocationAPI",
            "event_type": "custom",
            "data": {
                "event": "domain_allocated",
                "domain": domain["domain"],
                "campaign_id": request.campaign_id,
            }
        }).execute()

        return DomainAllocationResponse(
            domain=domain["domain"],
            domain_id=domain["id"],
            reputation_score=domain["reputation_score"],
            warmup_state=domain["warmup_state"],
            daily_send_limit=domain["daily_send_limit"],
            emails_sent_today=domain["emails_sent_today"],
            available_capacity=domain["daily_send_limit"] - domain["emails_sent_today"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to allocate domain: {str(e)}"
        )


@domain_router.post("/warmup", response_model=StartDomainWarmupResponse)
async def start_warmup(
    request: StartDomainWarmupRequest,
    db: Client = Depends(get_supabase_client)
) -> StartDomainWarmupResponse:
    """
    Start the warmup process for a cold domain.
    """
    try:
        # Call database function to start warmup
        result = db.rpc("start_domain_warmup", {"p_domain": request.domain}).execute()

        # Fetch updated domain
        domain_result = db.table("rex_domain_pool")\
            .select("*")\
            .eq("domain", request.domain)\
            .single()\
            .execute()

        domain = domain_result.data

        # Calculate completion date (14 days)
        from datetime import timedelta
        estimated_completion = datetime.utcnow() + timedelta(days=14)

        return StartDomainWarmupResponse(
            domain=domain["domain"],
            warmup_state=domain["warmup_state"],
            warmup_day=domain["warmup_day"],
            target_emails_today=domain["warmup_target_per_day"],
            warmup_schedule=domain["warmup_schedule"],
            estimated_completion_date=estimated_completion
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start warmup: {str(e)}"
        )


@domain_router.get("/health/{domain}", response_model=DomainHealthCheckResponse)
async def check_domain_health(
    domain: str,
    db: Client = Depends(get_supabase_client)
) -> DomainHealthCheckResponse:
    """
    Check domain health and get rotation recommendations.
    """
    try:
        # Call database function
        result = db.rpc("check_domain_health", {"p_domain": domain}).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Domain not found: {domain}"
            )

        health = result.data[0]

        # Get domain for additional metrics
        domain_result = db.table("rex_domain_pool")\
            .select("*")\
            .eq("domain", domain)\
            .single()\
            .execute()

        domain_data = domain_result.data

        # Generate recommendations
        recommendations = []
        if health["should_rotate"]:
            recommendations.append(f"Rotate domain due to: {health['rotation_reason']}")
        elif health["health_status"] == "good":
            recommendations.append("Continue monitoring bounce rate")
            recommendations.append("Maintain current sending volume")
        elif health["health_status"] == "fair":
            recommendations.append("Reduce sending volume temporarily")
            recommendations.append("Monitor closely for 48 hours")

        return DomainHealthCheckResponse(
            domain=domain,
            health_status=health["health_status"],
            reputation_score=health["reputation_score"],
            deliverability_score=health["deliverability_score"],
            bounce_rate=domain_data.get("bounce_rate", 0.0),
            spam_complaint_rate=domain_data.get("spam_complaint_rate", 0.0),
            should_rotate=health["should_rotate"],
            rotation_reason=health.get("rotation_reason"),
            recommendations=recommendations
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check domain health: {str(e)}"
        )


@domain_router.post("/rotate", response_model=TriggerDomainRotationResponse)
async def trigger_rotation(
    request: TriggerDomainRotationRequest,
    db: Client = Depends(get_supabase_client)
) -> TriggerDomainRotationResponse:
    """
    Trigger immediate or scheduled domain rotation.
    """
    try:
        # Call database function
        result = db.rpc("trigger_domain_rotation", {
            "p_domain": request.domain,
            "p_reason": request.reason
        }).execute()

        mission_id = result.data if result.data else None

        # Fetch updated domain state
        domain_result = db.table("rex_domain_pool")\
            .select("*")\
            .eq("domain", request.domain)\
            .single()\
            .execute()

        domain = domain_result.data

        # Find replacement domain
        replacement = db.table("rex_domain_pool")\
            .select("domain")\
            .eq("assigned_to_campaign", domain.get("assigned_to_campaign"))\
            .neq("domain", request.domain)\
            .eq("warmup_state", "warm")\
            .limit(1)\
            .execute()

        replacement_domain = replacement.data[0]["domain"] if replacement.data else None

        return TriggerDomainRotationResponse(
            domain=request.domain,
            rotated=True,
            new_state=domain["warmup_state"],
            replacement_domain=replacement_domain,
            rotation_mission_id=mission_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger rotation: {str(e)}"
        )


# ============================================================================
# INBOX MANAGEMENT ENDPOINTS
# ============================================================================

@inbox_router.post("/allocate", response_model=AllocateInboxResponse)
async def allocate_inbox(
    request: AllocateInboxRequest,
    db: Client = Depends(get_supabase_client)
) -> AllocateInboxResponse:
    """
    Allocate an inbox for a campaign.
    """
    try:
        # Call database function
        result = db.rpc("allocate_inbox_for_campaign", {
            "p_user_id": request.user_id,
            "p_campaign_id": request.campaign_id
        }).execute()

        inbox_id = result.data if result.data else None

        if not inbox_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No available inbox for user"
            )

        # Fetch inbox details
        inbox_result = db.table("inbox_management")\
            .select("*")\
            .eq("id", inbox_id)\
            .single()\
            .execute()

        inbox = inbox_result.data

        return AllocateInboxResponse(
            inbox_id=inbox["id"],
            email_address=inbox["email_address"],
            provider=inbox["provider"],
            status=inbox["status"],
            daily_send_limit=inbox["daily_send_limit"],
            emails_sent_today=inbox["emails_sent_today"],
            available_capacity=inbox["daily_send_limit"] - inbox["emails_sent_today"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to allocate inbox: {str(e)}"
        )


@inbox_router.post("/upgrade", response_model=UpgradeInboxTierResponse)
async def upgrade_inbox(
    request: UpgradeInboxTierRequest,
    db: Client = Depends(get_supabase_client)
) -> UpgradeInboxTierResponse:
    """
    Upgrade an inbox to a higher billing tier.
    """
    try:
        # Call database function
        db.rpc("upgrade_inbox_tier", {
            "p_inbox_id": request.inbox_id,
            "p_new_tier": request.new_tier,
            "p_stripe_subscription_id": request.stripe_subscription_id
        }).execute()

        # Get tier limits
        limits_result = db.rpc("get_inbox_tier_limits", {
            "p_tier": request.new_tier
        }).execute()

        limits = limits_result.data[0] if limits_result.data else {}

        return UpgradeInboxTierResponse(
            inbox_id=request.inbox_id,
            new_tier=request.new_tier,
            daily_send_limit=limits.get("daily_send_limit", 50),
            price_per_month=float(limits.get("price_per_month", 0.0)),
            features=limits.get("features", {})
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade inbox: {str(e)}"
        )


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@webhook_router.post("/llm", response_model=LLMCallbackResponse)
async def llm_callback(
    request: LLMCallbackRequest,
    db: Client = Depends(get_supabase_client)
) -> LLMCallbackResponse:
    """
    Webhook for async LLM processing callbacks.

    Used when LLM calls are made asynchronously and results are posted back.
    """
    try:
        # Log LLM call for audit trail
        db.table("agent_logs").insert({
            "mission_id": request.mission_id,
            "agent_name": request.agent_name,
            "event_type": "llm_call",
            "correlation_id": request.correlation_id,
            "data": {
                "model": request.model,
                "prompt_hash": request.prompt_hash,
                "tokens_used": request.tokens_used,
                "cost_usd": request.cost_usd,
                "duration_ms": request.duration_ms,
                "response": request.response,
            },
            "duration_ms": request.duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }).execute()

        return LLMCallbackResponse(
            acknowledged=True,
            logged=True,
            message="LLM callback logged successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process LLM callback: {str(e)}"
        )
