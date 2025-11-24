"""
DeliverabilityAgent - Domain Health & Reputation Manager

Monitors domain reputation, tracks deliverability metrics, triggers domain rotation,
and ensures optimal email sending infrastructure health.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .base_agent import BaseAgent, MissionContext, AgentResult
from ...crewai_agents.tools.mcp_db_tools import get_mcp_db_tools

logger = logging.getLogger(__name__)


@dataclass
class DomainHealthReport:
    """Domain health assessment"""
    domain: str
    health_status: str  # excellent, good, fair, poor, critical
    reputation_score: float
    deliverability_score: float
    bounce_rate: float
    spam_complaint_rate: float
    open_rate: float
    should_rotate: bool
    rotation_reason: Optional[str]
    recommendations: List[str]
    risk_level: str  # low, medium, high, critical


class DeliverabilityAgent(BaseAgent):
    """
    Specialized agent for email deliverability and domain health.

    Capabilities:
    - Domain reputation monitoring
    - Deliverability score calculation
    - Bounce/spam rate tracking
    - Automatic domain rotation
    - Warmup progress monitoring
    - DNS/SPF/DKIM validation
    """

    def __init__(self, supabase, redis_client=None, openai_api_key=None):
        super().__init__(
            agent_name="DeliverabilityAgent",
            supabase=supabase,
            redis_client=redis_client,
            openai_api_key=openai_api_key
        )

        # Health thresholds
        self.REPUTATION_THRESHOLD = 0.7
        self.BOUNCE_RATE_THRESHOLD = 0.05  # 5%
        self.SPAM_RATE_THRESHOLD = 0.001  # 0.1%
        self.MIN_DELIVERABILITY_SCORE = 0.8

        # Initialize MCP DB Tools
        self.mcp_db_tools = get_mcp_db_tools()

    async def handle_mission(self, context: MissionContext) -> AgentResult:
        """Execute domain health monitoring mission"""
        logger.info(f"DeliverabilityAgent starting mission {context.mission_id}")

        # Step 1: Fetch all active domains for user
        domains = await self._fetch_active_domains(context)
        logger.info(f"Monitoring {len(domains)} active domains")

        # Fetch meeting stats using MCP DB Tools
        meeting_stats = self.mcp_db_tools.get_meeting_stats(context.user_id, "30d")

        # Step 2: Check health of each domain
        health_reports = []
        for domain in domains:
            report = await self._check_domain_health(domain)
            health_reports.append(report)

        # Step 3: Identify domains needing rotation
        domains_to_rotate = [r for r in health_reports if r.should_rotate]
        logger.info(f"Found {len(domains_to_rotate)} domains requiring rotation")

        # Step 4: Execute rotations
        rotation_results = await self._execute_domain_rotations(domains_to_rotate, context)

        # Step 5: Update domain warmup progress
        warmup_updates = await self._update_warmup_progress(domains)

        # Build result
        result_data = {
            'total_domains_checked': len(domains),
            'domains_rotated': len(rotation_results['rotated']),
            'domains_healthy': len([r for r in health_reports if r.health_status in ['excellent', 'good']]),
            'domains_at_risk': len([r for r in health_reports if r.risk_level in ['high', 'critical']]),
            'warmup_domains_advanced': warmup_updates['advanced_count'],
            'rotation_details': rotation_results,
            'health_summary': {
                'excellent': len([r for r in health_reports if r.health_status == 'excellent']),
                'good': len([r for r in health_reports if r.health_status == 'good']),
                'fair': len([r for r in health_reports if r.health_status == 'fair']),
                'poor': len([r for r in health_reports if r.health_status == 'poor']),
                'critical': len([r for r in health_reports if r.health_status == 'critical']),
            },
            'meeting_stats': meeting_stats,
        }

        success = len(domains_to_rotate) == len(rotation_results['rotated'])

        return AgentResult(
            success=success,
            data=result_data,
            message=f"Checked {len(domains)} domains, rotated {len(rotation_results['rotated'])}, {len(health_reports) - len(domains_to_rotate)} healthy"
        )

    async def _fetch_active_domains(self, context: MissionContext) -> List[Dict[str, Any]]:
        """Fetch all active domains for monitoring"""
        result = self.db.table('rex_domain_pool')\
            .select('*')\
            .eq('user_id', context.user_id)\
            .eq('status', 'active')\
            .in_('warmup_state', ['warming', 'warm'])\
            .execute()

        return result.data if result.data else []

    async def _check_domain_health(self, domain: Dict[str, Any]) -> DomainHealthReport:
        """Comprehensive health check for a single domain"""
        domain_name = domain['domain']

        # Get metrics
        reputation_score = domain.get('reputation_score', 1.0)
        bounce_rate = domain.get('bounce_rate', 0.0)
        spam_complaint_rate = domain.get('spam_complaint_rate', 0.0)
        open_rate = domain.get('open_rate', 0.0)

        # Calculate deliverability score
        # Formula: weighted combination of metrics
        deliverability_score = (
            (reputation_score * 0.4) +
            (max(0, 1 - (bounce_rate / 0.1)) * 0.3) +  # Normalize bounce rate
            (max(0, 1 - (spam_complaint_rate / 0.01)) * 0.2) +  # Normalize spam rate
            (open_rate * 0.1)
        )

        # Determine health status
        if deliverability_score >= 0.9 and reputation_score >= 0.9:
            health_status = 'excellent'
            risk_level = 'low'
        elif deliverability_score >= 0.8 and reputation_score >= 0.8:
            health_status = 'good'
            risk_level = 'low'
        elif deliverability_score >= 0.7 and reputation_score >= 0.7:
            health_status = 'fair'
            risk_level = 'medium'
        elif deliverability_score >= 0.5:
            health_status = 'poor'
            risk_level = 'high'
        else:
            health_status = 'critical'
            risk_level = 'critical'

        # Determine if rotation needed
        should_rotate = False
        rotation_reason = None

        if reputation_score < self.REPUTATION_THRESHOLD:
            should_rotate = True
            rotation_reason = 'reputation_below_threshold'
        elif bounce_rate > self.BOUNCE_RATE_THRESHOLD:
            should_rotate = True
            rotation_reason = 'high_bounce_rate'
        elif spam_complaint_rate > self.SPAM_RATE_THRESHOLD:
            should_rotate = True
            rotation_reason = 'high_spam_complaints'
        elif deliverability_score < self.MIN_DELIVERABILITY_SCORE:
            should_rotate = True
            rotation_reason = 'low_deliverability_score'

        # Generate recommendations
        recommendations = []

        if bounce_rate > 0.03:
            recommendations.append('Review and clean email list')
            recommendations.append('Implement email verification before sending')

        if spam_complaint_rate > 0.0005:
            recommendations.append('Review email content for spam triggers')
            recommendations.append('Add clear unsubscribe links')

        if open_rate < 0.15:
            recommendations.append('Improve subject line quality')
            recommendations.append('Review send time optimization')

        if reputation_score < 0.85:
            recommendations.append('Reduce sending volume temporarily')
            recommendations.append('Focus on engaged subscribers only')

        if not should_rotate and health_status in ['excellent', 'good']:
            recommendations.append('Maintain current sending practices')
            recommendations.append('Continue monitoring metrics')

        return DomainHealthReport(
            domain=domain_name,
            health_status=health_status,
            reputation_score=reputation_score,
            deliverability_score=deliverability_score,
            bounce_rate=bounce_rate,
            spam_complaint_rate=spam_complaint_rate,
            open_rate=open_rate,
            should_rotate=should_rotate,
            rotation_reason=rotation_reason,
            recommendations=recommendations,
            risk_level=risk_level
        )

    async def _execute_domain_rotations(
        self,
        domains_to_rotate: List[DomainHealthReport],
        context: MissionContext
    ) -> Dict[str, Any]:
        """Execute domain rotations for unhealthy domains"""
        rotated = []
        failed = []

        for domain_report in domains_to_rotate:
            try:
                # Call database function to trigger rotation
                rotation_result = self.db.rpc('trigger_domain_rotation', {
                    'p_domain': domain_report.domain,
                    'p_reason': domain_report.rotation_reason
                }).execute()

                if rotation_result.data:
                    rotated.append({
                        'domain': domain_report.domain,
                        'reason': domain_report.rotation_reason,
                        'rotation_mission_id': rotation_result.data
                    })

                    logger.info(
                        f"Rotated domain {domain_report.domain} "
                        f"(reason: {domain_report.rotation_reason})"
                    )
                else:
                    failed.append({
                        'domain': domain_report.domain,
                        'reason': 'no_replacement_available'
                    })

            except Exception as e:
                logger.error(f"Failed to rotate domain {domain_report.domain}: {e}")
                failed.append({
                    'domain': domain_report.domain,
                    'reason': str(e)
                })

        return {
            'rotated': rotated,
            'failed': failed,
        }

    async def _update_warmup_progress(self, domains: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update warmup progress for warming domains"""
        advanced_count = 0

        for domain in domains:
            if domain.get('warmup_state') != 'warming':
                continue

            warmup_day = domain.get('warmup_day', 0)
            emails_sent_today = domain.get('emails_sent_today', 0)
            warmup_target = domain.get('warmup_target_per_day', 0)

            # Check if ready to advance to next day
            if emails_sent_today >= warmup_target:
                try:
                    # Call database function to advance warmup day
                    self.db.rpc('advance_warmup_day', {
                        'p_domain': domain['domain']
                    }).execute()

                    advanced_count += 1

                    logger.info(
                        f"Advanced warmup for domain {domain['domain']} "
                        f"from day {warmup_day} to day {warmup_day + 1}"
                    )

                except Exception as e:
                    logger.error(f"Failed to advance warmup for {domain['domain']}: {e}")

        return {
            'advanced_count': advanced_count
        }
