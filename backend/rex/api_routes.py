"""
REX API Routes
FastAPI routes for Rex autonomous orchestration system
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from .decision_engine import RexDecisionEngine, Mission, MissionType, MissionState
from .scheduler import MissionScheduler
from .resource_allocator import ResourceAllocator
from .analytics_engine import AnalyticsEngine
from .message_bus import MessageBus

logger = logging.getLogger(__name__)

# Create router
rex_router = APIRouter(prefix="/api/rex", tags=["rex"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CreateMissionRequest(BaseModel):
    type: str = Field(..., description="Mission type")
    priority: int = Field(50, ge=0, le=100, description="Priority 0-100")
    campaign_id: Optional[str] = None
    lead_ids: Optional[List[str]] = None
    custom_params: Optional[Dict[str, Any]] = None


class CreateMissionResponse(BaseModel):
    mission_id: str
    estimated_duration_ms: int
    assigned_crew: Optional[str] = None


class MissionDetailsResponse(BaseModel):
    mission: Dict[str, Any]
    tasks: List[Dict[str, Any]]
    progress: float
    logs: List[Dict[str, Any]]


class CancelMissionResponse(BaseModel):
    cancelled: bool
    state: str


class RexStatusResponse(BaseModel):
    status: str  # 'operational' | 'degraded' | 'error'
    uptime_ms: int
    missions: Dict[str, int]
    resources: Dict[str, Any]
    analytics: Dict[str, Any]


class AgentStatusResponse(BaseModel):
    agents: Dict[str, Dict[str, Any]]


class RestartAgentResponse(BaseModel):
    restarted: bool
    new_status: str


class DomainPoolResponse(BaseModel):
    domains: List[Dict[str, Any]]
    summary: Dict[str, int]


class RotateDomainRequest(BaseModel):
    domain: str
    reason: str
    immediate: bool = False


class RotateDomainResponse(BaseModel):
    rotated: bool
    replacement_domain: Optional[str] = None
    warmup_eta_hours: Optional[int] = None


class AddDomainRequest(BaseModel):
    domain: str
    type: str  # 'custom' | 'prewarmed'
    verify: bool = True


class AddDomainResponse(BaseModel):
    added: bool
    verification_status: Optional[str] = None
    dns_records: Optional[List[Dict[str, Any]]] = None


class AnalyticsResponse(BaseModel):
    current: Dict[str, Any]
    history: List[Dict[str, Any]]
    trends: Dict[str, List[Any]]


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

# Global instances (initialized by main server)
_scheduler: Optional[MissionScheduler] = None
_resource_allocator: Optional[ResourceAllocator] = None
_analytics_engine: Optional[AnalyticsEngine] = None
_message_bus: Optional[MessageBus] = None
_decision_engine: Optional[RexDecisionEngine] = None
_db = None
_redis = None
_start_time = datetime.utcnow()


def init_rex_system(db, redis, openai_api_key: Optional[str] = None):
    """Initialize Rex system components"""
    global _scheduler, _resource_allocator, _analytics_engine, _message_bus, _decision_engine, _db, _redis

    _db = db
    _redis = redis

    # Initialize components
    _decision_engine = RexDecisionEngine(db, openai_api_key)
    _resource_allocator = ResourceAllocator(db, redis)
    _analytics_engine = AnalyticsEngine(db, redis)
    _message_bus = MessageBus(redis)
    _scheduler = MissionScheduler(
        db=db,
        redis=redis,
        decision_engine=_decision_engine,
        resource_allocator=_resource_allocator,
        message_bus=_message_bus
    )

    logger.info("Rex system initialized")


async def start_rex_system():
    """Start Rex system background tasks"""
    if not _scheduler or not _analytics_engine or not _message_bus:
        raise RuntimeError("Rex system not initialized - call init_rex_system() first")

    # Start all components
    await _message_bus.start()
    # Note: scheduler.start() and analytics_engine.start() run as background tasks
    # They should be started with asyncio.create_task() in the main server

    logger.info("Rex system started")


def get_scheduler() -> MissionScheduler:
    if not _scheduler:
        raise HTTPException(status_code=500, detail="Rex system not initialized")
    return _scheduler


def get_resource_allocator() -> ResourceAllocator:
    if not _resource_allocator:
        raise HTTPException(status_code=500, detail="Rex system not initialized")
    return _resource_allocator


def get_analytics_engine() -> AnalyticsEngine:
    if not _analytics_engine:
        raise HTTPException(status_code=500, detail="Rex system not initialized")
    return _analytics_engine


def get_message_bus() -> MessageBus:
    if not _message_bus:
        raise HTTPException(status_code=500, detail="Rex system not initialized")
    return _message_bus


def get_db():
    if not _db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return _db


# ============================================================================
# API ROUTES
# ============================================================================

@rex_router.get("/status", response_model=RexStatusResponse)
async def get_rex_status(
    analytics: AnalyticsEngine = Depends(get_analytics_engine),
    resource_allocator: ResourceAllocator = Depends(get_resource_allocator),
    db = Depends(get_db)
):
    """Get Rex system status"""
    try:
        # Calculate uptime
        uptime_ms = int((datetime.utcnow() - _start_time).total_seconds() * 1000)

        # Get mission counts
        result = await db.table('rex_missions').select('state', count='exact').execute()
        mission_counts = {}
        for row in result.data:
            mission_counts[row['state']] = mission_counts.get(row['state'], 0) + 1

        # Get active missions
        active = sum(
            mission_counts.get(state, 0)
            for state in ['assigned', 'executing', 'collecting', 'analyzing', 'optimizing']
        )

        # Get 24h completed/failed
        one_day_ago = (datetime.utcnow() - timedelta(days=1)).isoformat()
        recent = await db.table('rex_missions') \
            .select('state') \
            .gte('completed_at', one_day_ago) \
            .execute()

        completed_24h = len([m for m in recent.data if m['state'] == 'completed'])
        failed_24h = len([m for m in recent.data if m['state'] == 'failed'])

        # Get resource pool
        resources = await resource_allocator.get_resource_pool()

        # Get current analytics
        current_analytics = await analytics.generate_snapshot()

        # Determine system status
        success_rate = completed_24h / (completed_24h + failed_24h) if (completed_24h + failed_24h) > 0 else 1.0
        status = 'operational'
        if success_rate < 0.8:
            status = 'degraded'
        if success_rate < 0.5 or failed_24h > 20:
            status = 'error'

        return RexStatusResponse(
            status=status,
            uptime_ms=uptime_ms,
            missions={
                'active': active,
                'queued': mission_counts.get('queued', 0),
                'completed_24h': completed_24h,
                'failed_24h': failed_24h
            },
            resources=resources,
            analytics=current_analytics.to_dict()
        )

    except Exception as e:
        logger.error(f"Error getting Rex status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rex_router.post("/missions", response_model=CreateMissionResponse)
async def create_mission(
    request: CreateMissionRequest,
    user_id: str,  # TODO: Extract from JWT token
    scheduler: MissionScheduler = Depends(get_scheduler),
    db = Depends(get_db)
):
    """Create new mission"""
    try:
        # Validate mission type
        try:
            mission_type = MissionType(request.type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid mission type: {request.type}")

        # Create mission in database
        mission_data = {
            'user_id': user_id,
            'type': mission_type.value,
            'state': MissionState.QUEUED.value,
            'priority': request.priority,
            'campaign_id': request.campaign_id,
            'lead_ids': request.lead_ids,
            'custom_params': request.custom_params,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        result = await db.table('rex_missions').insert(mission_data).execute()
        mission_id = result.data[0]['id']

        logger.info(f"Mission created: {mission_id} (type: {mission_type}, priority: {request.priority})")

        # Estimate duration based on mission type
        duration_estimates = {
            MissionType.LEAD_REACTIVATION: 180000,  # 3 minutes
            MissionType.CAMPAIGN_EXECUTION: 300000,  # 5 minutes
            MissionType.ICP_EXTRACTION: 120000,  # 2 minutes
            MissionType.DOMAIN_ROTATION: 60000,  # 1 minute
            MissionType.PERFORMANCE_OPTIMIZATION: 240000,  # 4 minutes
            MissionType.ERROR_RECOVERY: 120000  # 2 minutes
        }

        return CreateMissionResponse(
            mission_id=mission_id,
            estimated_duration_ms=duration_estimates.get(mission_type, 180000),
            assigned_crew=None  # Will be assigned by scheduler
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating mission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rex_router.get("/missions/{mission_id}", response_model=MissionDetailsResponse)
async def get_mission_details(
    mission_id: str,
    db = Depends(get_db)
):
    """Get detailed mission information"""
    try:
        # Get mission
        mission_result = await db.table('rex_missions') \
            .select('*') \
            .eq('id', mission_id) \
            .limit(1) \
            .execute()

        if not mission_result.data:
            raise HTTPException(status_code=404, detail=f"Mission not found: {mission_id}")

        mission = mission_result.data[0]

        # Get tasks
        tasks_result = await db.table('rex_tasks') \
            .select('*') \
            .eq('mission_id', mission_id) \
            .execute()

        tasks = tasks_result.data

        # Calculate progress
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t['state'] == 'completed'])
        progress = completed_tasks / total_tasks if total_tasks > 0 else 0.0

        # Get logs
        logs_result = await db.table('rex_logs') \
            .select('*') \
            .eq('mission_id', mission_id) \
            .order('created_at', desc=False) \
            .limit(100) \
            .execute()

        logs = logs_result.data

        return MissionDetailsResponse(
            mission=mission,
            tasks=tasks,
            progress=progress,
            logs=logs
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mission details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rex_router.post("/missions/{mission_id}/cancel", response_model=CancelMissionResponse)
async def cancel_mission(
    mission_id: str,
    scheduler: MissionScheduler = Depends(get_scheduler),
    db = Depends(get_db)
):
    """Cancel a mission"""
    try:
        # Get current mission state
        result = await db.table('rex_missions') \
            .select('state') \
            .eq('id', mission_id) \
            .limit(1) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Mission not found: {mission_id}")

        current_state = result.data[0]['state']

        # Can only cancel queued or assigned missions
        if current_state not in ['queued', 'assigned']:
            return CancelMissionResponse(
                cancelled=False,
                state=current_state
            )

        # Update mission state
        await db.table('rex_missions').update({
            'state': 'failed',
            'error': {'code': 'cancelled', 'message': 'Mission cancelled by user', 'recoverable': False, 'retry_count': 0},
            'completed_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', mission_id).execute()

        logger.info(f"Mission cancelled: {mission_id}")

        return CancelMissionResponse(
            cancelled=True,
            state='failed'
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling mission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rex_router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    hours: int = 24,
    analytics: AnalyticsEngine = Depends(get_analytics_engine)
):
    """Get analytics data"""
    try:
        # Get current snapshot
        current = await analytics.generate_snapshot()

        # Get history
        history = await analytics.get_snapshot_history(hours=hours)

        # Get trends
        trends = await analytics.get_trends(hours=hours)

        return AnalyticsResponse(
            current=current.to_dict(),
            history=history,
            trends={
                'missions_per_hour': trends.missions_per_hour,
                'success_rate': trends.success_rate,
                'avg_duration_ms': trends.avg_duration_ms
            }
        )

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rex_router.get("/agents/status", response_model=AgentStatusResponse)
async def get_agent_status(
    db = Depends(get_db)
):
    """Get agent status across all crews"""
    try:
        # Get all tasks grouped by agent
        tasks = await db.table('rex_tasks') \
            .select('agent_name, state, duration_ms, completed_at') \
            .execute()

        agent_stats: Dict[str, Dict[str, Any]] = {}

        for task in tasks.data:
            agent = task['agent_name']
            if agent not in agent_stats:
                agent_stats[agent] = {
                    'status': 'idle',
                    'current_task': None,
                    'last_execution_at': None,
                    'success_count': 0,
                    'total_count': 0,
                    'durations': []
                }

            stats = agent_stats[agent]
            stats['total_count'] += 1

            if task['state'] == 'executing':
                stats['status'] = 'executing'
                stats['current_task'] = task.get('id')
            elif task['state'] == 'failed':
                stats['status'] = 'failed'
            elif task['state'] == 'completed':
                stats['success_count'] += 1

            if task.get('completed_at'):
                if not stats['last_execution_at'] or task['completed_at'] > stats['last_execution_at']:
                    stats['last_execution_at'] = task['completed_at']

            if task.get('duration_ms'):
                stats['durations'].append(task['duration_ms'])

        # Calculate final metrics
        result = {}
        for agent, stats in agent_stats.items():
            result[agent] = {
                'status': stats['status'],
                'current_task': stats['current_task'],
                'last_execution_at': stats['last_execution_at'],
                'success_rate': stats['success_count'] / stats['total_count'] if stats['total_count'] > 0 else 0.0,
                'avg_duration_ms': sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
            }

        return AgentStatusResponse(agents=result)

    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rex_router.get("/domains", response_model=DomainPoolResponse)
async def get_domain_pool(
    user_id: Optional[str] = None,
    resource_allocator: ResourceAllocator = Depends(get_resource_allocator),
    db = Depends(get_db)
):
    """Get domain pool status"""
    try:
        # Get domains
        query = db.table('rex_domain_pool').select('*')
        if user_id:
            query = query.eq('user_id', user_id)

        result = await query.execute()
        domains = result.data

        # Calculate health for each domain
        domain_list = []
        for domain in domains:
            health = {
                'domain': domain['domain'],
                'reputation_score': domain['reputation_score'],
                'status': 'healthy' if domain['reputation_score'] >= 0.8 else 'degraded' if domain['reputation_score'] >= 0.7 else 'critical',
                'metrics': {
                    'emails_sent_24h': domain.get('emails_sent_today', 0),
                    'bounce_rate': domain.get('bounce_rate', 0),
                    'spam_complaint_rate': domain.get('spam_complaint_rate', 0),
                    'open_rate': domain.get('open_rate', 0)
                },
                'rotation_threshold': 0.7,
                'rotation_recommended': domain['reputation_score'] < 0.7
            }

            domain_list.append({
                'domain': domain['domain'],
                'type': domain['type'],
                'status': domain['status'],
                'health': health,
                'assigned_to': domain.get('assigned_to_campaign')
            })

        # Summary
        summary = {
            'total': len(domains),
            'active': len([d for d in domains if d['status'] == 'active']),
            'warming': len([d for d in domains if d['status'] == 'warming']),
            'rotated': len([d for d in domains if d['status'] == 'rotated'])
        }

        return DomainPoolResponse(
            domains=domain_list,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error getting domain pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rex_router.post("/domains/rotate", response_model=RotateDomainResponse)
async def rotate_domain(
    request: RotateDomainRequest,
    db = Depends(get_db)
):
    """Rotate a domain"""
    try:
        # Mark domain as rotated
        await db.table('rex_domain_pool').update({
            'status': 'rotated',
            'rotated_at': datetime.utcnow().isoformat(),
            'rotation_reason': request.reason,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('domain', request.domain).execute()

        # TODO: Implement replacement domain allocation logic
        # For now, return basic response

        logger.info(f"Domain rotated: {request.domain} (reason: {request.reason})")

        return RotateDomainResponse(
            rotated=True,
            replacement_domain=None,
            warmup_eta_hours=None
        )

    except Exception as e:
        logger.error(f"Error rotating domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rex_router.post("/domains/add", response_model=AddDomainResponse)
async def add_domain(
    request: AddDomainRequest,
    user_id: str,  # TODO: Extract from JWT token
    db = Depends(get_db)
):
    """Add a new domain to the pool"""
    try:
        # Check if domain already exists
        existing = await db.table('rex_domain_pool') \
            .select('id') \
            .eq('domain', request.domain) \
            .limit(1) \
            .execute()

        if existing.data:
            raise HTTPException(status_code=400, detail=f"Domain already exists: {request.domain}")

        # Add domain
        domain_data = {
            'user_id': user_id,
            'domain': request.domain,
            'type': request.type,
            'status': 'pending_verification' if request.verify else 'warming',
            'reputation_score': 0.5,  # Start at 50% until verified
            'emails_sent_today': 0,
            'emails_sent_total': 0,
            'bounce_rate': 0.0,
            'spam_complaint_rate': 0.0,
            'open_rate': 0.0,
            'warmup_progress': 0.0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        await db.table('rex_domain_pool').insert(domain_data).execute()

        logger.info(f"Domain added: {request.domain} (type: {request.type})")

        return AddDomainResponse(
            added=True,
            verification_status='pending' if request.verify else None,
            dns_records=None  # TODO: Return required DNS records
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))
