"""
REX Mission Scheduler
Priority queue-based mission scheduler with lifecycle management
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from .decision_engine import RexDecisionEngine, Mission, MissionState, MissionType

logger = logging.getLogger(__name__)


@dataclass
class ResourceAllocation:
    """Resource allocation for a mission"""
    agents: Dict[str, List[str]]  # crew_name -> agent_names
    domains: List[str]
    api_quota: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'agents': self.agents,
            'domains': self.domains,
            'api_quota': self.api_quota
        }


class MissionScheduler:
    """
    Priority queue-based mission scheduler.
    Handles mission lifecycle from creation to completion.
    """

    SCHEDULER_INTERVAL = 1.0  # Check queue every second
    PROGRESS_MONITOR_INTERVAL = 30.0  # Monitor progress every 30 seconds
    ERROR_RECOVERY_INTERVAL = 60.0  # Check for errors every minute
    MISSION_TIMEOUT_HOURS = 2  # Timeout missions after 2 hours

    def __init__(self, db, redis, decision_engine: RexDecisionEngine, resource_allocator):
        self.db = db
        self.redis = redis
        self.decision_engine = decision_engine
        self.resource_allocator = resource_allocator
        self.running = False

        # Statistics
        self.stats = {
            'missions_scheduled': 0,
            'missions_completed': 0,
            'missions_failed': 0,
            'missions_timeout': 0,
        }

    async def start(self):
        """Start the scheduler loops"""
        logger.info("Starting Rex Mission Scheduler...")
        self.running = True

        # Run all loops concurrently
        await asyncio.gather(
            self._scheduler_loop(),
            self._progress_monitor_loop(),
            self._error_recovery_loop(),
            return_exceptions=True
        )

    async def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping Rex Mission Scheduler...")
        self.running = False

    async def _scheduler_loop(self):
        """Main scheduling loop - assigns queued missions to resources"""
        while self.running:
            try:
                # Fetch queued missions ordered by priority
                missions = await self._fetch_queued_missions()

                for mission in missions:
                    try:
                        # Check resource availability
                        resources = await self.resource_allocator.check_availability(mission)

                        if resources and resources.available:
                            await self._assign_mission(mission, resources.allocation)
                        else:
                            # Mission stays queued - check if needs priority boost
                            await self._check_priority_boost(mission)

                    except Exception as e:
                        logger.error(f"Error processing mission {mission.id}: {e}")
                        await self._log_error(mission.id, str(e))

                await asyncio.sleep(self.SCHEDULER_INTERVAL)

            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(self.SCHEDULER_INTERVAL)

    async def _fetch_queued_missions(self) -> List[Mission]:
        """Fetch queued missions ordered by priority"""
        try:
            result = await self.db.table('rex_missions') \
                .select('*') \
                .eq('state', MissionState.QUEUED.value) \
                .order('priority', desc=True) \
                .order('created_at', desc=False) \
                .limit(10) \
                .execute()

            missions = []
            for data in result.data:
                missions.append(Mission(
                    id=data['id'],
                    type=MissionType(data['type']),
                    state=MissionState(data['state']),
                    priority=data['priority'],
                    user_id=data['user_id'],
                    campaign_id=data.get('campaign_id'),
                    lead_ids=data.get('lead_ids', []),
                    custom_params=data.get('custom_params', {}),
                    created_at=datetime.fromisoformat(data['created_at'])
                ))

            return missions

        except Exception as e:
            logger.error(f"Error fetching queued missions: {e}")
            return []

    async def _assign_mission(self, mission: Mission, resources: ResourceAllocation):
        """Assign mission to crew and allocate resources"""
        try:
            # Determine crew assignment
            crew_name = self._select_crew(mission.type)

            logger.info(
                f"Assigning mission {mission.id} ({mission.type}) "
                f"to crew {crew_name} (priority: {mission.priority})"
            )

            # Update mission state in database
            await self.db.table('rex_missions').update({
                'state': MissionState.ASSIGNED.value,
                'assigned_crew': crew_name,
                'assigned_agents': resources.agents.get(crew_name, []),
                'allocated_resources': resources.to_dict(),
                'assigned_at': datetime.utcnow().isoformat()
            }).eq('id', mission.id).execute()

            # Send assignment message to crew via message bus
            await self._send_mission_message(
                mission_id=mission.id,
                type='mission.assigned',
                recipient=crew_name,
                data={
                    'mission': {
                        'id': mission.id,
                        'type': mission.type.value,
                        'priority': mission.priority,
                        'context': {
                            'campaign_id': mission.campaign_id,
                            'lead_ids': mission.lead_ids,
                            'custom_params': mission.custom_params
                        }
                    },
                    'resources': resources.to_dict()
                }
            )

            # Log assignment
            await self._log_event(
                mission.id,
                'info',
                f'Mission assigned to {crew_name}',
                {'crew': crew_name, 'resources': resources.to_dict()}
            )

            self.stats['missions_scheduled'] += 1

        except Exception as e:
            logger.error(f"Error assigning mission {mission.id}: {e}")
            await self._fail_mission(mission.id, f"Assignment failed: {e}")

    def _select_crew(self, mission_type: MissionType) -> str:
        """Map mission type to crew name"""
        mapping = {
            MissionType.LEAD_REACTIVATION: 'dead_lead_crew',
            MissionType.CAMPAIGN_EXECUTION: 'campaign_crew',
            MissionType.ICP_EXTRACTION: 'auto_icp_crew',
            MissionType.DOMAIN_ROTATION: 'domain_health_monitor',
            MissionType.PERFORMANCE_OPTIMIZATION: 'special_forces_coordinator',
            MissionType.ERROR_RECOVERY: 'special_forces_coordinator'
        }
        return mapping.get(mission_type, 'special_forces_coordinator')

    async def _check_priority_boost(self, mission: Mission):
        """Check if mission needs priority boost due to long queue time"""
        try:
            decision = await self.decision_engine.decide_next_action(
                mission,
                {'action': 'check_priority'}
            )

            if decision.action == 'boost_priority':
                new_priority = decision.params['new_priority']

                await self.db.table('rex_missions').update({
                    'priority': new_priority
                }).eq('id', mission.id).execute()

                logger.info(
                    f"Boosted mission {mission.id} priority: "
                    f"{mission.priority} -> {new_priority}"
                )

        except Exception as e:
            logger.error(f"Error checking priority boost for {mission.id}: {e}")

    async def _progress_monitor_loop(self):
        """Monitor mission progress and handle timeouts"""
        while self.running:
            try:
                # Check for stalled missions
                stalled = await self._fetch_stalled_missions()

                for mission in stalled:
                    logger.warning(f"Mission {mission.id} is stalled - escalating")
                    await self._escalate_mission(mission.id, 'timeout')
                    self.stats['missions_timeout'] += 1

                await asyncio.sleep(self.PROGRESS_MONITOR_INTERVAL)

            except Exception as e:
                logger.error(f"Progress monitor error: {e}")
                await asyncio.sleep(self.PROGRESS_MONITOR_INTERVAL)

    async def _fetch_stalled_missions(self) -> List[Mission]:
        """Fetch missions that have been executing too long"""
        try:
            timeout_threshold = datetime.utcnow() - timedelta(
                hours=self.MISSION_TIMEOUT_HOURS
            )

            result = await self.db.table('rex_missions') \
                .select('*') \
                .in_('state', [
                    MissionState.ASSIGNED.value,
                    MissionState.EXECUTING.value,
                    MissionState.COLLECTING.value
                ]) \
                .lt('assigned_at', timeout_threshold.isoformat()) \
                .execute()

            missions = []
            for data in result.data:
                missions.append(Mission(
                    id=data['id'],
                    type=MissionType(data['type']),
                    state=MissionState(data['state']),
                    priority=data['priority'],
                    user_id=data['user_id'],
                    assigned_crew=data.get('assigned_crew')
                ))

            return missions

        except Exception as e:
            logger.error(f"Error fetching stalled missions: {e}")
            return []

    async def _escalate_mission(self, mission_id: str, reason: str):
        """Escalate mission to ESCALATED state"""
        try:
            await self.db.table('rex_missions').update({
                'state': MissionState.ESCALATED.value,
                'error': {
                    'code': 'mission_escalated',
                    'message': f'Mission escalated: {reason}',
                    'recoverable': False,
                    'retry_count': 0
                },
                'completed_at': datetime.utcnow().isoformat()
            }).eq('id', mission_id).execute()

            await self._log_event(
                mission_id,
                'critical',
                f'Mission escalated: {reason}',
                {'reason': reason}
            )

            # TODO: Send notification to user

        except Exception as e:
            logger.error(f"Error escalating mission {mission_id}: {e}")

    async def _error_recovery_loop(self):
        """Handle failed missions and retry logic"""
        while self.running:
            try:
                failed = await self._fetch_failed_missions()

                for mission in failed:
                    # Get error details
                    result = await self.db.table('rex_missions') \
                        .select('error') \
                        .eq('id', mission.id) \
                        .single() \
                        .execute()

                    error = result.data.get('error', {})

                    # Use decision engine to determine action
                    decision = await self.decision_engine.decide_next_action(
                        mission,
                        {'error': error}
                    )

                    if decision.action == 'retry_mission':
                        await self._retry_mission(mission, decision.params)
                    elif decision.action == 'escalate_error':
                        await self._escalate_mission(mission.id, 'permanent_failure')
                        self.stats['missions_failed'] += 1

                await asyncio.sleep(self.ERROR_RECOVERY_INTERVAL)

            except Exception as e:
                logger.error(f"Error recovery loop error: {e}")
                await asyncio.sleep(self.ERROR_RECOVERY_INTERVAL)

    async def _fetch_failed_missions(self) -> List[Mission]:
        """Fetch missions in FAILED state that need recovery"""
        try:
            result = await self.db.table('rex_missions') \
                .select('*') \
                .eq('state', MissionState.FAILED.value) \
                .limit(5) \
                .execute()

            missions = []
            for data in result.data:
                missions.append(Mission(
                    id=data['id'],
                    type=MissionType(data['type']),
                    state=MissionState(data['state']),
                    priority=data['priority'],
                    user_id=data['user_id']
                ))

            return missions

        except Exception as e:
            logger.error(f"Error fetching failed missions: {e}")
            return []

    async def _retry_mission(self, mission: Mission, retry_params: Dict[str, Any]):
        """Retry a failed mission"""
        try:
            backoff_seconds = retry_params.get('backoff_seconds', 0)

            if backoff_seconds > 0:
                logger.info(f"Waiting {backoff_seconds}s before retrying mission {mission.id}")
                await asyncio.sleep(backoff_seconds)

            # Reset mission to QUEUED state
            await self.db.table('rex_missions').update({
                'state': MissionState.QUEUED.value,
                'error': retry_params.get('error')
            }).eq('id', mission.id).execute()

            await self._log_event(
                mission.id,
                'info',
                f'Mission queued for retry (attempt {retry_params.get("retry_count", 1)})',
                retry_params
            )

        except Exception as e:
            logger.error(f"Error retrying mission {mission.id}: {e}")

    async def _fail_mission(self, mission_id: str, reason: str):
        """Mark mission as permanently failed"""
        try:
            await self.db.table('rex_missions').update({
                'state': MissionState.FAILED.value,
                'error': {
                    'code': 'mission_failed',
                    'message': reason,
                    'recoverable': False,
                    'retry_count': 0
                },
                'completed_at': datetime.utcnow().isoformat()
            }).eq('id', mission_id).execute()

            await self._log_event(
                mission_id,
                'error',
                f'Mission failed: {reason}',
                {'reason': reason}
            )

        except Exception as e:
            logger.error(f"Error failing mission {mission_id}: {e}")

    async def _send_mission_message(
        self,
        mission_id: str,
        type: str,
        recipient: str,
        data: Dict[str, Any]
    ):
        """Send message via Redis pub/sub"""
        try:
            message = {
                'id': f"msg_{datetime.utcnow().timestamp()}",
                'type': type,
                'timestamp': datetime.utcnow().isoformat(),
                'sender': 'rex',
                'recipient': recipient,
                'mission_id': mission_id,
                'data': data
            }

            # Publish to Redis channel
            await self.redis.publish(
                f'rex:messages:{recipient}',
                str(message)
            )

        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def _log_event(
        self,
        mission_id: str,
        level: str,
        message: str,
        context: Dict[str, Any]
    ):
        """Log event to rex_logs table"""
        try:
            # Get user_id from mission
            result = await self.db.table('rex_missions') \
                .select('user_id') \
                .eq('id', mission_id) \
                .single() \
                .execute()

            user_id = result.data.get('user_id')

            await self.db.table('rex_logs').insert({
                'mission_id': mission_id,
                'user_id': user_id,
                'level': level,
                'message': message,
                'context': context,
                'source': 'rex'
            }).execute()

        except Exception as e:
            logger.error(f"Error logging event: {e}")

    async def _log_error(self, mission_id: str, error_message: str):
        """Log error event"""
        await self._log_event(
            mission_id,
            'error',
            error_message,
            {'error': error_message}
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return {
            **self.stats,
            'running': self.running
        }
