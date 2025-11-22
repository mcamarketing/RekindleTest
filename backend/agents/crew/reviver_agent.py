"""
ReviverAgent - Dead Lead Reactivation Specialist

Analyzes cold leads, scores reactivation probability, and executes multi-channel
reactivation campaigns with personalized outreach strategies.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .base_agent import BaseAgent, MissionContext, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class LeadScore:
    """Lead reactivation score"""
    lead_id: str
    reactivation_probability: float  # 0.0 - 1.0
    engagement_score: float
    days_since_last_contact: int
    recommended_strategy: str
    recommended_channels: List[str]
    personalization_hooks: Dict[str, Any]
    skip_reason: Optional[str] = None


class ReviverAgent(BaseAgent):
    """
    Specialized agent for reactivating dead/dormant leads.

    Capabilities:
    - Lead scoring and prioritization
    - Multi-channel reactivation strategy
    - Personalized outreach generation
    - Engagement tracking
    - Win-back offer optimization
    """

    def __init__(self, supabase, redis_client=None, openai_api_key=None):
        super().__init__(
            agent_name="ReviverAgent",
            supabase=supabase,
            redis_client=redis_client,
            openai_api_key=openai_api_key
        )

        # Reactivation thresholds
        self.MIN_REACTIVATION_SCORE = 0.3
        self.DEAD_LEAD_THRESHOLD_DAYS = 365
        self.HIGH_VALUE_THRESHOLD = 1000  # USD

    async def handle_mission(self, context: MissionContext) -> AgentResult:
        """Execute lead reactivation mission"""
        logger.info(f"ReviverAgent starting mission {context.mission_id}")

        # Step 1: Fetch and analyze leads
        leads = await self._fetch_leads(context)
        logger.info(f"Fetched {len(leads)} leads for reactivation")

        # Step 2: Score each lead
        scored_leads = await self._score_leads(leads)
        logger.info(f"Scored {len(scored_leads)} leads")

        # Step 3: Filter out unrecoverable leads
        recoverable_leads = self._filter_recoverable_leads(scored_leads)
        logger.info(f"Filtered to {len(recoverable_leads)} recoverable leads")

        # Step 4: Generate reactivation strategies
        strategies = await self._generate_reactivation_strategies(recoverable_leads)

        # Step 5: Execute outreach (or queue for execution)
        execution_results = await self._execute_reactivation(strategies, context)

        # Build result
        result_data = {
            'total_leads_analyzed': len(leads),
            'recoverable_leads': len(recoverable_leads),
            'leads_activated': execution_results['leads_activated'],
            'campaigns_created': execution_results['campaigns_created'],
            'estimated_revenue_potential': execution_results['estimated_revenue'],
            'strategies_by_type': execution_results['strategies_by_type'],
        }

        success = execution_results['leads_activated'] > 0

        return AgentResult(
            success=success,
            data=result_data,
            message=f"Reactivated {execution_results['leads_activated']} leads via {execution_results['campaigns_created']} campaigns"
        )

    async def _fetch_leads(self, context: MissionContext) -> List[Dict[str, Any]]:
        """Fetch dead/dormant leads from database"""
        # Get lead IDs from context or fetch all dormant leads
        lead_ids = context.custom_params.get('lead_ids', [])

        if lead_ids:
            # Fetch specific leads
            result = self.db.table('leads')\
                .select('*')\
                .in_('id', lead_ids)\
                .execute()
        else:
            # Fetch all dormant leads for user
            cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()

            result = self.db.table('leads')\
                .select('*')\
                .eq('user_id', context.user_id)\
                .eq('status', 'cold')\
                .lt('last_contact_at', cutoff_date)\
                .execute()

        return result.data if result.data else []

    async def _score_leads(self, leads: List[Dict[str, Any]]) -> List[LeadScore]:
        """Score each lead for reactivation probability"""
        scored_leads = []

        for lead in leads:
            score = await self._calculate_lead_score(lead)
            scored_leads.append(score)

        return scored_leads

    async def _calculate_lead_score(self, lead: Dict[str, Any]) -> LeadScore:
        """Calculate reactivation probability for a single lead"""
        # Parse dates
        last_contact = lead.get('last_contact_at')
        if last_contact:
            last_contact_dt = datetime.fromisoformat(last_contact.replace('Z', '+00:00'))
            days_since_contact = (datetime.utcnow() - last_contact_dt.replace(tzinfo=None)).days
        else:
            days_since_contact = 999

        # Get engagement metrics
        open_rate = lead.get('email_open_rate', 0.0)
        click_rate = lead.get('email_click_rate', 0.0)
        reply_rate = lead.get('reply_rate', 0.0)
        deal_value = lead.get('estimated_deal_value', 0)

        # Calculate engagement score (0-1)
        engagement_score = (
            (open_rate * 0.3) +
            (click_rate * 0.3) +
            (reply_rate * 0.4)
        )

        # Calculate reactivation probability
        # Factors: recency, engagement, deal value, industry fit
        recency_score = max(0, 1 - (days_since_contact / 365))
        value_score = min(1.0, deal_value / 10000) if deal_value > 0 else 0.1

        reactivation_probability = (
            (recency_score * 0.4) +
            (engagement_score * 0.4) +
            (value_score * 0.2)
        )

        # Determine recommended strategy
        if reactivation_probability >= 0.7:
            strategy = 'aggressive_multi_channel'
            channels = ['email', 'sms', 'linkedin']
        elif reactivation_probability >= 0.5:
            strategy = 'standard_email_sequence'
            channels = ['email', 'linkedin']
        elif reactivation_probability >= 0.3:
            strategy = 'soft_touch_email'
            channels = ['email']
        else:
            strategy = 'skip'
            channels = []

        # Extract personalization hooks
        personalization_hooks = {
            'company': lead.get('company'),
            'industry': lead.get('industry'),
            'job_title': lead.get('job_title'),
            'pain_points': lead.get('pain_points', []),
            'previous_engagement': {
                'last_topic': lead.get('last_email_topic'),
                'last_campaign': lead.get('last_campaign_name'),
            }
        }

        # Skip reason if applicable
        skip_reason = None
        if days_since_contact > self.DEAD_LEAD_THRESHOLD_DAYS:
            skip_reason = 'too_old'
        elif engagement_score < 0.05:
            skip_reason = 'no_historical_engagement'

        return LeadScore(
            lead_id=lead['id'],
            reactivation_probability=reactivation_probability,
            engagement_score=engagement_score,
            days_since_last_contact=days_since_contact,
            recommended_strategy=strategy,
            recommended_channels=channels,
            personalization_hooks=personalization_hooks,
            skip_reason=skip_reason
        )

    def _filter_recoverable_leads(self, scored_leads: List[LeadScore]) -> List[LeadScore]:
        """Filter out leads that shouldn't be reactivated"""
        recoverable = []

        for lead_score in scored_leads:
            # Skip if probability too low
            if lead_score.reactivation_probability < self.MIN_REACTIVATION_SCORE:
                logger.debug(
                    f"Skipping lead {lead_score.lead_id}: "
                    f"probability {lead_score.reactivation_probability:.2f} < {self.MIN_REACTIVATION_SCORE}"
                )
                continue

            # Skip if has skip reason
            if lead_score.skip_reason:
                logger.debug(f"Skipping lead {lead_score.lead_id}: {lead_score.skip_reason}")
                continue

            # Skip if recommended strategy is 'skip'
            if lead_score.recommended_strategy == 'skip':
                continue

            recoverable.append(lead_score)

        return recoverable

    async def _generate_reactivation_strategies(
        self,
        leads: List[LeadScore]
    ) -> List[Dict[str, Any]]:
        """Generate personalized reactivation strategies for each lead"""
        strategies = []

        for lead_score in leads:
            strategy = {
                'lead_id': lead_score.lead_id,
                'strategy_type': lead_score.recommended_strategy,
                'channels': lead_score.recommended_channels,
                'reactivation_probability': lead_score.reactivation_probability,
                'sequence': await self._build_outreach_sequence(lead_score),
                'personalization': lead_score.personalization_hooks,
            }

            strategies.append(strategy)

        return strategies

    async def _build_outreach_sequence(self, lead_score: LeadScore) -> List[Dict[str, Any]]:
        """Build multi-touch outreach sequence"""
        sequence = []

        if lead_score.recommended_strategy == 'aggressive_multi_channel':
            # Day 0: Email with value proposition
            sequence.append({
                'day': 0,
                'channel': 'email',
                'template': 'winback_value_proposition',
                'subject_line': 'We\'ve made improvements you asked for',
            })

            # Day 2: LinkedIn connection request
            sequence.append({
                'day': 2,
                'channel': 'linkedin',
                'template': 'linkedin_reconnect',
            })

            # Day 4: SMS (if phone number available)
            sequence.append({
                'day': 4,
                'channel': 'sms',
                'template': 'quick_check_in',
            })

            # Day 7: Email with case study
            sequence.append({
                'day': 7,
                'channel': 'email',
                'template': 'customer_success_story',
                'subject_line': 'How [similar company] achieved [result]',
            })

        elif lead_score.recommended_strategy == 'standard_email_sequence':
            # Day 0: Soft reintroduction
            sequence.append({
                'day': 0,
                'channel': 'email',
                'template': 'soft_reintroduction',
                'subject_line': 'Quick question about [company]',
            })

            # Day 5: Value-focused follow-up
            sequence.append({
                'day': 5,
                'channel': 'email',
                'template': 'value_follow_up',
                'subject_line': 'New feature: [relevant feature]',
            })

        elif lead_score.recommended_strategy == 'soft_touch_email':
            # Single touchpoint
            sequence.append({
                'day': 0,
                'channel': 'email',
                'template': 'soft_touch',
                'subject_line': 'Checking in',
            })

        return sequence

    async def _execute_reactivation(
        self,
        strategies: List[Dict[str, Any]],
        context: MissionContext
    ) -> Dict[str, Any]:
        """Execute reactivation campaigns"""
        campaigns_created = 0
        leads_activated = 0
        estimated_revenue = 0.0
        strategies_by_type = {}

        for strategy in strategies:
            # Count strategies by type
            strategy_type = strategy['strategy_type']
            strategies_by_type[strategy_type] = strategies_by_type.get(strategy_type, 0) + 1

            # Create campaign entry in database
            campaign_data = {
                'user_id': context.user_id,
                'name': f"Reactivation - {strategy['lead_id'][:8]}",
                'type': 'lead_reactivation',
                'status': 'active',
                'lead_ids': [strategy['lead_id']],
                'sequence': strategy['sequence'],
                'created_at': datetime.utcnow().isoformat(),
            }

            try:
                result = self.db.table('campaigns').insert(campaign_data).execute()

                if result.data:
                    campaigns_created += 1
                    leads_activated += 1

                    # Estimate revenue based on reactivation probability and deal value
                    # This would be more sophisticated in production
                    estimated_revenue += strategy['reactivation_probability'] * 1000

                    # Update lead status
                    self.db.table('leads').update({
                        'status': 'reactivating',
                        'last_contact_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat(),
                    }).eq('id', strategy['lead_id']).execute()

            except Exception as e:
                logger.error(f"Failed to create campaign for lead {strategy['lead_id']}: {e}")
                continue

        return {
            'leads_activated': leads_activated,
            'campaigns_created': campaigns_created,
            'estimated_revenue': estimated_revenue,
            'strategies_by_type': strategies_by_type,
        }
