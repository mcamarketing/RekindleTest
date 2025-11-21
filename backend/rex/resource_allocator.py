"""
REX Resource Allocator
Manages agent capacity, domain pools, and API rate limits
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

from .decision_engine import Mission, MissionType

logger = logging.getLogger(__name__)


@dataclass
class ResourceAvailability:
    """Result of resource availability check"""
    available: bool
    allocation: Optional['ResourceAllocation'] = None
    reason: Optional[str] = None


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


class ResourceAllocator:
    """
    Manages resources for mission execution:
    - Agent capacity tracking
    - Domain pool management
    - API rate limit tracking
    """

    # Agent capacity per crew
    AGENT_CAPACITY = {
        'dead_lead_crew': {
            'total': 4,
            'agents': ['researcher', 'writer', 'compliance', 'quality_control']
        },
        'campaign_crew': {
            'total': 8,
            'agents': [
                'researcher', 'lead_scorer', 'writer', 'subject_optimizer',
                'compliance', 'quality_control', 'meeting_booker', 'billing'
            ]
        },
        'auto_icp_crew': {
            'total': 4,
            'agents': ['icp_analyzer', 'lead_sourcer', 'researcher', 'lead_scorer']
        },
        'domain_health_monitor': {
            'total': 3,
            'agents': ['reputation_tracker', 'rotation_coordinator', 'warmup_manager']
        },
        'special_forces_coordinator': {
            'total': 9,
            'agents': ['coordinator', 'priority_queue', 'resource_allocator'] + list(range(6))
        }
    }

    # API rate limits (requests per minute)
    API_LIMITS = {
        'openai': {'limit': 10000, 'cost_per_1k_tokens': 0.01},
        'sendgrid': {'limit': 100, 'cost_per_email': 0.0001},
        'twilio': {'limit': 50, 'cost_per_sms': 0.0075}
    }

    def __init__(self, db, redis):
        self.db = db
        self.redis = redis

        # In-memory resource tracking
        self.agents_in_use: Dict[str, List[str]] = {}  # crew_name -> [mission_ids]
        self.domains_in_use: Dict[str, str] = {}  # domain -> mission_id
        self.api_usage: Dict[str, Dict[str, Any]] = {
            'openai': {'used': 0, 'reset_at': self._get_next_minute()},
            'sendgrid': {'used': 0, 'reset_at': self._get_next_minute()},
            'twilio': {'used': 0, 'reset_at': self._get_next_minute()}
        }

    async def check_availability(self, mission: Mission) -> ResourceAvailability:
        """
        Check if resources are available for mission.
        Returns ResourceAvailability with allocation if available.
        """
        try:
            # Determine required crew
            crew_name = self._get_crew_for_mission(mission.type)

            # Check agent availability
            agents_available = await self._check_agent_availability(crew_name)
            if not agents_available:
                return ResourceAvailability(
                    available=False,
                    reason=f'No agents available in {crew_name}'
                )

            # Check domain availability
            domain = await self._allocate_domain(mission.user_id, mission.campaign_id)
            if not domain:
                return ResourceAvailability(
                    available=False,
                    reason='No domains available'
                )

            # Check API quota
            api_quota = await self._check_api_quota(mission)
            if not api_quota:
                return ResourceAvailability(
                    available=False,
                    reason='API quota exhausted'
                )

            # All resources available - create allocation
            allocation = ResourceAllocation(
                agents={crew_name: self.AGENT_CAPACITY[crew_name]['agents']},
                domains=[domain],
                api_quota=api_quota
            )

            # Reserve resources
            await self._reserve_resources(mission.id, crew_name, domain, api_quota)

            return ResourceAvailability(
                available=True,
                allocation=allocation
            )

        except Exception as e:
            logger.error(f"Error checking resource availability: {e}")
            return ResourceAvailability(
                available=False,
                reason=f'Error: {str(e)}'
            )

    def _get_crew_for_mission(self, mission_type: MissionType) -> str:
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

    async def _check_agent_availability(self, crew_name: str) -> bool:
        """Check if agents in crew are available"""
        # Check in-memory tracking
        missions_using_crew = self.agents_in_use.get(crew_name, [])

        # Allow up to 3 concurrent missions per crew
        return len(missions_using_crew) < 3

    async def _allocate_domain(
        self,
        user_id: str,
        campaign_id: Optional[str]
    ) -> Optional[str]:
        """Allocate domain from pool for campaign"""
        try:
            # First try: allocated domain for this campaign
            if campaign_id:
                result = await self.db.table('rex_domain_pool') \
                    .select('domain') \
                    .eq('user_id', user_id) \
                    .eq('assigned_to_campaign', campaign_id) \
                    .eq('status', 'active') \
                    .limit(1) \
                    .execute()

                if result.data:
                    return result.data[0]['domain']

            # Second try: unassigned custom domains
            result = await self.db.table('rex_domain_pool') \
                .select('domain') \
                .eq('user_id', user_id) \
                .eq('type', 'custom') \
                .eq('status', 'active') \
                .is_('assigned_to_campaign', 'null') \
                .gte('reputation_score', 0.7) \
                .limit(1) \
                .execute()

            if result.data:
                domain = result.data[0]['domain']

                # Assign domain to campaign
                if campaign_id:
                    await self.db.table('rex_domain_pool').update({
                        'assigned_to_campaign': campaign_id,
                        'last_used_at': datetime.utcnow().isoformat()
                    }).eq('domain', domain).execute()

                return domain

            # Third try: prewarmed domains
            result = await self.db.table('rex_domain_pool') \
                .select('domain') \
                .eq('type', 'prewarmed') \
                .eq('status', 'active') \
                .is_('assigned_to_campaign', 'null') \
                .gte('reputation_score', 0.8) \
                .limit(1) \
                .execute()

            if result.data:
                domain = result.data[0]['domain']

                # Assign prewarmed domain to user and campaign
                await self.db.table('rex_domain_pool').update({
                    'user_id': user_id,
                    'assigned_to_campaign': campaign_id,
                    'last_used_at': datetime.utcnow().isoformat()
                }).eq('domain', domain).execute()

                return domain

            return None

        except Exception as e:
            logger.error(f"Error allocating domain: {e}")
            return None

    async def _check_api_quota(self, mission: Mission) -> Optional[Dict[str, int]]:
        """Check and reserve API quota for mission"""
        # Reset usage if needed
        now = datetime.utcnow()
        for api_name, usage in self.api_usage.items():
            if now >= usage['reset_at']:
                usage['used'] = 0
                usage['reset_at'] = self._get_next_minute()

        # Estimate API usage for mission type
        estimates = self._estimate_api_usage(mission.type)

        # Check if within limits
        quota = {}
        for api_name, estimated in estimates.items():
            limit = self.API_LIMITS[api_name]['limit']
            used = self.api_usage[api_name]['used']

            if used + estimated > limit:
                logger.warning(
                    f"API quota exhausted for {api_name}: "
                    f"{used + estimated} > {limit}"
                )
                return None

            quota[api_name] = estimated

        return quota

    def _estimate_api_usage(self, mission_type: MissionType) -> Dict[str, int]:
        """Estimate API usage for mission type"""
        estimates = {
            MissionType.LEAD_REACTIVATION: {
                'openai': 100,  # 100 requests for research + writing
                'sendgrid': 50,  # 50 emails
                'twilio': 10  # 10 SMS
            },
            MissionType.CAMPAIGN_EXECUTION: {
                'openai': 200,
                'sendgrid': 100,
                'twilio': 20
            },
            MissionType.ICP_EXTRACTION: {
                'openai': 50,
                'sendgrid': 0,
                'twilio': 0
            },
            MissionType.DOMAIN_ROTATION: {
                'openai': 0,
                'sendgrid': 0,
                'twilio': 0
            },
            MissionType.PERFORMANCE_OPTIMIZATION: {
                'openai': 30,
                'sendgrid': 0,
                'twilio': 0
            }
        }
        return estimates.get(mission_type, {'openai': 10, 'sendgrid': 0, 'twilio': 0})

    async def _reserve_resources(
        self,
        mission_id: str,
        crew_name: str,
        domain: str,
        api_quota: Dict[str, int]
    ):
        """Reserve resources for mission"""
        # Reserve agents
        if crew_name not in self.agents_in_use:
            self.agents_in_use[crew_name] = []
        self.agents_in_use[crew_name].append(mission_id)

        # Reserve domain
        self.domains_in_use[domain] = mission_id

        # Reserve API quota
        for api_name, amount in api_quota.items():
            self.api_usage[api_name]['used'] += amount

        logger.info(
            f"Reserved resources for mission {mission_id}: "
            f"crew={crew_name}, domain={domain}, api_quota={api_quota}"
        )

    async def release(self, mission_id: str):
        """Release resources after mission completion"""
        try:
            # Release agents
            for crew_name, missions in self.agents_in_use.items():
                if mission_id in missions:
                    missions.remove(mission_id)
                    logger.info(f"Released agents for mission {mission_id} from {crew_name}")

            # Release domain
            domain_to_release = None
            for domain, mid in self.domains_in_use.items():
                if mid == mission_id:
                    domain_to_release = domain
                    break

            if domain_to_release:
                del self.domains_in_use[domain_to_release]
                logger.info(f"Released domain {domain_to_release} for mission {mission_id}")

                # Update domain last_used_at
                await self.db.table('rex_domain_pool').update({
                    'last_used_at': datetime.utcnow().isoformat()
                }).eq('domain', domain_to_release).execute()

            # API quota is reset automatically per minute, no action needed

        except Exception as e:
            logger.error(f"Error releasing resources for mission {mission_id}: {e}")

    async def get_resource_pool(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current resource pool status"""
        try:
            # Agent status
            agents = {}
            for crew_name, capacity in self.AGENT_CAPACITY.items():
                in_use = len(self.agents_in_use.get(crew_name, []))
                agents[crew_name] = {
                    'total': capacity['total'],
                    'available': max(0, 3 - in_use),  # Max 3 concurrent per crew
                    'executing': in_use,
                    'failed': 0  # TODO: Track failed agents
                }

            # Domain status
            domain_query = self.db.table('rex_domain_pool').select('*')
            if user_id:
                domain_query = domain_query.eq('user_id', user_id)

            domain_result = await domain_query.execute()

            domains = {
                'total': len(domain_result.data),
                'active': len([d for d in domain_result.data if d['status'] == 'active']),
                'warming': len([d for d in domain_result.data if d['status'] == 'warming']),
                'rotated': len([d for d in domain_result.data if d['status'] == 'rotated']),
                'custom': len([d for d in domain_result.data if d['type'] == 'custom']),
                'prewarmed': len([d for d in domain_result.data if d['type'] == 'prewarmed'])
            }

            # API limits
            api_limits = {}
            for api_name, limit_info in self.API_LIMITS.items():
                usage = self.api_usage[api_name]
                api_limits[api_name] = {
                    'used': usage['used'],
                    'limit': limit_info['limit'],
                    'reset_at': usage['reset_at'].isoformat()
                }

            return {
                'agents': agents,
                'domains': domains,
                'api_limits': api_limits
            }

        except Exception as e:
            logger.error(f"Error getting resource pool: {e}")
            return {'agents': {}, 'domains': {}, 'api_limits': {}}

    def _get_next_minute(self) -> datetime:
        """Get timestamp for next minute boundary"""
        now = datetime.utcnow()
        return (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
