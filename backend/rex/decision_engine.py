"""
REX Decision Engine Core
Three-layer decision architecture:
1. State Machine (deterministic, fast)
2. Rule Engine (business logic)
3. LLM Reasoner (complex context-aware decisions)
"""

import json
import logging
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import openai

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class MissionType(str, Enum):
    LEAD_REACTIVATION = "lead_reactivation"
    CAMPAIGN_EXECUTION = "campaign_execution"
    ICP_EXTRACTION = "icp_extraction"
    DOMAIN_ROTATION = "domain_rotation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ERROR_RECOVERY = "error_recovery"


class MissionState(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Mission:
    id: str
    type: MissionType
    state: MissionState
    priority: int
    user_id: str
    campaign_id: Optional[str] = None
    lead_ids: Optional[List[str]] = None
    custom_params: Optional[Dict[str, Any]] = None
    assigned_crew: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Decision:
    action: str
    params: Dict[str, Any] = None
    target_state: Optional[MissionState] = None
    reason: str = ""
    confidence: float = 1.0
    alternatives_considered: List[str] = None
    llm_used: bool = False

    def __post_init__(self):
        if self.params is None:
            self.params = {}
        if self.alternatives_considered is None:
            self.alternatives_considered = []


# ============================================================================
# STATE MACHINE (Layer 1: Deterministic)
# ============================================================================

class StateMachine:
    """Deterministic state transitions"""

    TRANSITIONS = {
        MissionState.QUEUED: [MissionState.ASSIGNED, MissionState.FAILED],
        MissionState.ASSIGNED: [MissionState.EXECUTING, MissionState.FAILED],
        MissionState.EXECUTING: [MissionState.COLLECTING, MissionState.FAILED],
        MissionState.COLLECTING: [MissionState.ANALYZING, MissionState.FAILED],
        MissionState.ANALYZING: [MissionState.OPTIMIZING, MissionState.COMPLETED],
        MissionState.OPTIMIZING: [MissionState.COMPLETED, MissionState.FAILED],
    }

    def can_handle(self, state: MissionState, context: Dict[str, Any]) -> bool:
        """Check if this is a simple state transition"""
        target = context.get('target_state')
        if not target:
            return False

        try:
            target_state = MissionState(target)
            return target_state in self.TRANSITIONS.get(state, [])
        except ValueError:
            return False

    async def decide(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        """Execute deterministic state transition"""
        target_str = context.get('target_state')
        target_state = MissionState(target_str)

        if target_state not in self.TRANSITIONS[mission.state]:
            raise ValueError(
                f"Invalid transition: {mission.state} -> {target_state}"
            )

        logger.info(
            f"State machine: Mission {mission.id} transitioning "
            f"{mission.state} -> {target_state}"
        )

        return Decision(
            action='transition_state',
            target_state=target_state,
            reason='deterministic_state_machine',
            confidence=1.0
        )


# ============================================================================
# RULE ENGINE (Layer 2: Business Logic)
# ============================================================================

class Rule:
    """Base class for business logic rules"""

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        """Check if this rule applies to the mission"""
        raise NotImplementedError

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        """Execute the rule and return a decision"""
        raise NotImplementedError


class DomainRotationRule(Rule):
    """Rotate domain if reputation drops below threshold"""

    REPUTATION_THRESHOLD = 0.7

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.type == MissionType.CAMPAIGN_EXECUTION and
            context.get('domain_reputation') is not None and
            context['domain_reputation'] < self.REPUTATION_THRESHOLD
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        domain = context.get('domain')
        reputation = context['domain_reputation']

        logger.warning(
            f"Domain rotation triggered: {domain} "
            f"(reputation: {reputation:.2f} < {self.REPUTATION_THRESHOLD})"
        )

        return Decision(
            action='rotate_domain',
            params={
                'domain': domain,
                'reason': 'reputation_drop',
                'current_reputation': reputation,
                'threshold': self.REPUTATION_THRESHOLD,
                'replacement_strategy': 'prewarmed_pool'
            },
            reason=f'domain_reputation_below_threshold ({reputation:.2f} < {self.REPUTATION_THRESHOLD})',
            confidence=0.95
        )


class ResourceAllocationRule(Rule):
    """Allocate resources based on mission priority"""

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.state == MissionState.QUEUED and
            context.get('action') == 'allocate_resources'
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        # Check resource availability
        available_resources = context.get('available_resources', {})

        # Prioritize based on mission type and priority
        if mission.priority >= 80:
            # High priority - allocate immediately
            return Decision(
                action='allocate_resources',
                params={'strategy': 'immediate', 'resources': available_resources},
                reason='high_priority_mission',
                confidence=0.9
            )
        elif mission.priority >= 50:
            # Medium priority - standard allocation
            return Decision(
                action='allocate_resources',
                params={'strategy': 'standard', 'resources': available_resources},
                reason='standard_priority_mission',
                confidence=0.85
            )
        else:
            # Low priority - queue if resources constrained
            return Decision(
                action='queue_mission',
                params={'reason': 'low_priority_resource_constraint'},
                reason='low_priority_with_resource_constraint',
                confidence=0.8
            )


class ErrorEscalationRule(Rule):
    """Escalate errors based on severity and retry count"""

    MAX_RETRIES = 3

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return context.get('error') is not None

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        error = context['error']
        retry_count = error.get('retry_count', 0)
        recoverable = error.get('recoverable', False)

        if not recoverable:
            # Non-recoverable error - escalate immediately
            return Decision(
                action='escalate_error',
                params={
                    'error': error,
                    'escalation_reason': 'non_recoverable_error'
                },
                target_state=MissionState.FAILED,
                reason='non_recoverable_error_detected',
                confidence=1.0
            )

        if retry_count < self.MAX_RETRIES:
            # Retry with exponential backoff
            backoff_seconds = 2 ** retry_count
            return Decision(
                action='retry_mission',
                params={
                    'retry_count': retry_count + 1,
                    'backoff_seconds': backoff_seconds,
                    'error': error
                },
                reason=f'recoverable_error_retry_{retry_count + 1}',
                confidence=0.7 - (retry_count * 0.1)
            )
        else:
            # Max retries exceeded - escalate
            return Decision(
                action='escalate_error',
                params={
                    'error': error,
                    'escalation_reason': 'max_retries_exceeded'
                },
                target_state=MissionState.FAILED,
                reason='max_retries_exceeded',
                confidence=0.95
            )


class PriorityBoostRule(Rule):
    """Boost priority for time-sensitive missions"""

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.state == MissionState.QUEUED and
            context.get('action') == 'check_priority'
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        # Check if mission has been queued for too long
        queue_time = datetime.utcnow() - mission.created_at
        queue_hours = queue_time.total_seconds() / 3600

        if queue_hours > 24:
            # Boost priority if queued for over 24 hours
            new_priority = min(mission.priority + 20, 100)
            return Decision(
                action='boost_priority',
                params={
                    'old_priority': mission.priority,
                    'new_priority': new_priority,
                    'reason': 'long_queue_time'
                },
                reason=f'mission_queued_for_{queue_hours:.1f}_hours',
                confidence=0.9
            )

        return Decision(
            action='maintain_priority',
            params={'current_priority': mission.priority},
            reason='queue_time_acceptable',
            confidence=0.8
        )


class IdleOptimizationRule(Rule):
    """Trigger idle optimization when no missions active"""

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            context.get('system_state') == 'idle' and
            context.get('action') == 'optimize_idle'
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        # Identify optimization opportunities
        opportunities = []

        # Check domain warmup needs
        warming_domains = context.get('warming_domains', 0)
        if warming_domains < 2:
            opportunities.append('start_domain_warmup')

        # Check for performance analysis
        last_analysis = context.get('last_performance_analysis')
        if not last_analysis or (datetime.utcnow() - last_analysis).days >= 1:
            opportunities.append('run_performance_analysis')

        return Decision(
            action='idle_optimization',
            params={'opportunities': opportunities},
            reason='system_idle_optimization_triggered',
            confidence=0.75
        )


class BudgetConstraintRule(Rule):
    """Enforce user budget limits and cost controls"""

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            context.get('action') == 'check_budget' or
            context.get('estimated_cost') is not None
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        user_budget = context.get('user_budget', {})
        estimated_cost = context.get('estimated_cost', 0)
        budget_remaining = user_budget.get('remaining', 0)

        # Check if mission would exceed budget
        if estimated_cost > budget_remaining:
            return Decision(
                action='pause_mission',
                params={
                    'reason': 'budget_exceeded',
                    'estimated_cost': estimated_cost,
                    'budget_remaining': budget_remaining,
                    'budget_needed': estimated_cost - budget_remaining
                },
                reason=f'insufficient_budget (need ${estimated_cost:.2f}, have ${budget_remaining:.2f})',
                confidence=1.0
            )

        # Warn if cost > 80% of remaining budget
        if estimated_cost > (budget_remaining * 0.8):
            return Decision(
                action='proceed_with_warning',
                params={
                    'warning': 'approaching_budget_limit',
                    'estimated_cost': estimated_cost,
                    'budget_remaining': budget_remaining,
                    'usage_percentage': (estimated_cost / budget_remaining) * 100
                },
                reason='budget_warning_threshold_exceeded',
                confidence=0.9
            )

        return Decision(
            action='proceed',
            params={'estimated_cost': estimated_cost},
            reason='budget_within_limits',
            confidence=1.0
        )


class RateLimitRule(Rule):
    """Prevent API rate limit violations"""

    # Rate limits (per hour)
    RATE_LIMITS = {
        'openai': 10000,  # tokens per hour
        'sendgrid': 1000,  # emails per hour
        'twilio': 500,    # SMS per hour
    }

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return context.get('api_usage') is not None

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        api_usage = context['api_usage']
        violations = []

        for api, usage in api_usage.items():
            limit = self.RATE_LIMITS.get(api, float('inf'))
            if usage >= limit * 0.9:  # 90% threshold
                violations.append({
                    'api': api,
                    'usage': usage,
                    'limit': limit,
                    'percentage': (usage / limit) * 100
                })

        if violations:
            # Pause mission if any API near limit
            return Decision(
                action='throttle_mission',
                params={
                    'violations': violations,
                    'recommended_delay_seconds': 3600,  # 1 hour
                    'reason': 'rate_limit_protection'
                },
                reason=f'approaching_rate_limits ({len(violations)} APIs)',
                confidence=0.95
            )

        return Decision(
            action='proceed',
            params={'api_usage': api_usage},
            reason='rate_limits_safe',
            confidence=1.0
        )


class DeadLeadThresholdRule(Rule):
    """Skip leads that are too cold or unrecoverable"""

    DEAD_LEAD_THRESHOLD_DAYS = 365
    MIN_ENGAGEMENT_SCORE = 0.1

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.type == MissionType.LEAD_REACTIVATION and
            context.get('lead_analysis') is not None
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        lead_analysis = context['lead_analysis']
        leads_to_skip = []
        leads_to_process = []

        for lead in lead_analysis.get('leads', []):
            days_since_contact = lead.get('days_since_last_contact', 0)
            engagement_score = lead.get('engagement_score', 0)

            if (days_since_contact > self.DEAD_LEAD_THRESHOLD_DAYS or
                engagement_score < self.MIN_ENGAGEMENT_SCORE):
                leads_to_skip.append({
                    'lead_id': lead['id'],
                    'reason': 'too_cold' if days_since_contact > self.DEAD_LEAD_THRESHOLD_DAYS else 'low_engagement',
                    'days_since_contact': days_since_contact,
                    'engagement_score': engagement_score
                })
            else:
                leads_to_process.append(lead['id'])

        return Decision(
            action='filter_leads',
            params={
                'leads_to_process': leads_to_process,
                'leads_to_skip': leads_to_skip,
                'filter_reason': 'cold_lead_threshold'
            },
            reason=f'filtered_out_{len(leads_to_skip)}_dead_leads',
            confidence=0.85
        )


class CampaignTimingRule(Rule):
    """Optimize campaign send times based on historical data"""

    # Best send times (24-hour format)
    OPTIMAL_SEND_HOURS = [9, 10, 11, 14, 15, 16]  # 9-11am, 2-4pm
    AVOID_WEEKENDS = True

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.type == MissionType.CAMPAIGN_EXECUTION and
            context.get('action') == 'schedule_send'
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        scheduled_time = context.get('scheduled_time', datetime.utcnow())

        # Check if weekend
        is_weekend = scheduled_time.weekday() >= 5
        current_hour = scheduled_time.hour

        # Check if optimal time
        is_optimal_time = current_hour in self.OPTIMAL_SEND_HOURS

        if self.AVOID_WEEKENDS and is_weekend:
            # Reschedule to Monday 10am
            days_ahead = 7 - scheduled_time.weekday()
            new_time = scheduled_time + timedelta(days=days_ahead)
            new_time = new_time.replace(hour=10, minute=0, second=0)

            return Decision(
                action='reschedule_campaign',
                params={
                    'original_time': scheduled_time.isoformat(),
                    'new_time': new_time.isoformat(),
                    'reason': 'avoid_weekend'
                },
                reason='weekend_send_avoided',
                confidence=0.9
            )

        if not is_optimal_time:
            # Suggest next optimal time
            next_optimal = None
            for hour in self.OPTIMAL_SEND_HOURS:
                if hour > current_hour:
                    next_optimal = scheduled_time.replace(hour=hour, minute=0, second=0)
                    break

            if not next_optimal:
                # Next day at first optimal hour
                next_optimal = (scheduled_time + timedelta(days=1)).replace(
                    hour=self.OPTIMAL_SEND_HOURS[0], minute=0, second=0
                )

            return Decision(
                action='suggest_reschedule',
                params={
                    'current_time': scheduled_time.isoformat(),
                    'suggested_time': next_optimal.isoformat(),
                    'reason': 'optimize_send_time',
                    'expected_improvement': '15-20% open rate increase'
                },
                reason='suboptimal_send_time',
                confidence=0.75
            )

        return Decision(
            action='proceed',
            params={'scheduled_time': scheduled_time.isoformat()},
            reason='optimal_send_time',
            confidence=0.95
        )


class ABTestAllocationRule(Rule):
    """Allocate leads to A/B test variants"""

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.type == MissionType.CAMPAIGN_EXECUTION and
            context.get('ab_test_config') is not None
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        ab_config = context['ab_test_config']
        total_leads = len(context.get('lead_ids', []))

        # Split leads based on variant weights
        variants = ab_config.get('variants', [])
        allocations = {}

        start_idx = 0
        for variant in variants:
            weight = variant.get('weight', 0.5)
            count = int(total_leads * weight)
            allocations[variant['name']] = {
                'lead_indices': list(range(start_idx, start_idx + count)),
                'count': count,
                'variant_config': variant.get('config', {})
            }
            start_idx += count

        return Decision(
            action='allocate_ab_test',
            params={
                'allocations': allocations,
                'total_leads': total_leads,
                'variants': [v['name'] for v in variants]
            },
            reason='ab_test_allocation',
            confidence=1.0
        )


class DomainWarmupProgressRule(Rule):
    """Enforce domain warmup volume limits"""

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.type == MissionType.CAMPAIGN_EXECUTION and
            context.get('domain_warmup_status') is not None
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        warmup_status = context['domain_warmup_status']
        warmup_state = warmup_status.get('state', 'cold')

        # Only allow full campaigns on warm domains
        if warmup_state != 'warm':
            target_today = warmup_status.get('target_emails_today', 0)
            sent_today = warmup_status.get('emails_sent_today', 0)
            remaining_today = target_today - sent_today

            if remaining_today <= 0:
                return Decision(
                    action='pause_campaign',
                    params={
                        'reason': 'warmup_daily_limit_reached',
                        'warmup_day': warmup_status.get('warmup_day', 0),
                        'target_today': target_today,
                        'sent_today': sent_today
                    },
                    reason='domain_warmup_limit_reached',
                    confidence=1.0
                )

            # Limit campaign to remaining warmup capacity
            return Decision(
                action='limit_campaign_volume',
                params={
                    'max_emails_today': remaining_today,
                    'warmup_state': warmup_state,
                    'reason': 'respect_warmup_schedule'
                },
                reason='domain_warmup_in_progress',
                confidence=0.95
            )

        return Decision(
            action='proceed',
            params={'domain_status': 'warm'},
            reason='domain_fully_warmed',
            confidence=1.0
        )


class PerformanceRegressionRule(Rule):
    """Detect and respond to performance degradation"""

    REGRESSION_THRESHOLD = 0.20  # 20% drop triggers action

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.type == MissionType.PERFORMANCE_OPTIMIZATION or
            context.get('performance_metrics') is not None
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        current_metrics = context.get('performance_metrics', {}).get('current', {})
        baseline_metrics = context.get('performance_metrics', {}).get('baseline', {})

        regressions = []
        for metric, current_value in current_metrics.items():
            baseline_value = baseline_metrics.get(metric, current_value)
            if baseline_value > 0:
                change_pct = (current_value - baseline_value) / baseline_value

                if change_pct < -self.REGRESSION_THRESHOLD:
                    regressions.append({
                        'metric': metric,
                        'current': current_value,
                        'baseline': baseline_value,
                        'change_pct': change_pct * 100
                    })

        if regressions:
            # Performance regression detected - trigger investigation
            return Decision(
                action='investigate_regression',
                params={
                    'regressions': regressions,
                    'investigation_priority': 'high' if len(regressions) > 2 else 'medium',
                    'suggested_actions': [
                        'review_recent_changes',
                        'check_domain_reputation',
                        'analyze_content_quality',
                        'review_send_timing'
                    ]
                },
                reason=f'performance_regression_detected ({len(regressions)} metrics)',
                confidence=0.9
            )

        return Decision(
            action='maintain_course',
            params={'metrics': current_metrics},
            reason='performance_stable',
            confidence=0.85
        )


class RuleEngine:
    """Business logic rules"""

    def __init__(self, db):
        self.db = db
        self.rules: List[Rule] = [
            # Original rules
            DomainRotationRule(db),
            ResourceAllocationRule(db),
            ErrorEscalationRule(db),
            PriorityBoostRule(db),
            IdleOptimizationRule(db),

            # New production-grade rules
            BudgetConstraintRule(db),
            RateLimitRule(db),
            DeadLeadThresholdRule(db),
            CampaignTimingRule(db),
            ABTestAllocationRule(db),
            DomainWarmupProgressRule(db),
            PerformanceRegressionRule(db),
        ]

    def has_matching_rule(self, mission: Mission, context: Dict[str, Any]) -> bool:
        """Check if any rule matches"""
        return any(rule.matches(mission, context) for rule in self.rules)

    async def evaluate(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        """Evaluate rules and return decision"""
        for rule in self.rules:
            if rule.matches(mission, context):
                logger.info(f"Rule matched: {rule.__class__.__name__}")
                return await rule.execute(mission, context)

        raise ValueError("No matching rule found")


# ============================================================================
# LLM REASONER (Layer 3: Complex Context-Aware Decisions)
# ============================================================================

class LLMReasoner:
    """LLM-based complex reasoning for ambiguous decisions with production hardening"""

    SYSTEM_PROMPT = """You are Rex, the autonomous orchestration system for RekindlePro.

CORE IDENTITY:
- You are an AI orchestrator managing 28 specialized AI agents across 4 crews
- Your purpose: Maximize lead reactivation performance with minimal human intervention
- You operate deterministically when possible, use reasoning only for complex decisions

OPERATIONAL CONSTRAINTS:
1. NEVER execute unsafe actions (delete data, external API calls without validation)
2. ALWAYS respect user preferences and approval settings
3. ALWAYS prioritize domain reputation protection
4. NEVER exceed API rate limits (OpenAI, SendGrid, Twilio)
5. ALWAYS log every decision for audit trail

DECISION FRAMEWORK:
When making decisions, evaluate in this order:
1. Is there a deterministic rule? → Apply it immediately
2. Is there sufficient data? → Use data-driven decision
3. Is uncertainty high? → Request human confirmation
4. Is this a novel situation? → Use LLM reasoning with low temperature

OUTPUT FORMAT:
Always respond in structured JSON:
{
  "action": "action_name",
  "params": {...},
  "reason": "clear explanation",
  "confidence": 0.0-1.0,
  "alternatives_considered": ["alt1", "alt2"],
  "requires_approval": false
}

CONFIDENCE THRESHOLDS:
- 0.9-1.0: High confidence, execute immediately
- 0.7-0.89: Medium confidence, proceed with monitoring
- 0.5-0.69: Low confidence, suggest human review
- 0.0-0.49: Very low confidence, require approval

Be concise, technical, and factual. No marketing language."""

    # Confidence threshold for auto-execution
    AUTO_EXECUTE_THRESHOLD = 0.7

    # LLM cache (in-memory for now, should use Redis in production)
    _cache: Dict[str, Decision] = {}

    def __init__(self, api_key: Optional[str] = None, redis_client=None):
        self.api_key = api_key
        self.redis_client = redis_client
        if api_key:
            openai.api_key = api_key

        # Fallback actions for different error types
        self.error_fallbacks = {
            'timeout': 'retry_with_backoff',
            'rate_limit': 'queue_for_later',
            'invalid_response': 'escalate_to_human',
            'api_error': 'use_safe_default',
        }

    async def reason(
        self,
        mission: Mission,
        context: Dict[str, Any],
        use_cache: bool = True
    ) -> Decision:
        """Use LLM to make complex decision with fallback handling"""
        if not self.api_key:
            logger.error("OpenAI API key not configured - cannot use LLM reasoner")
            return self._get_safe_fallback(mission, context, 'no_api_key')

        # Check cache first
        if use_cache:
            cached = await self._get_cached_decision(mission, context)
            if cached:
                logger.info(f"LLM cache hit for mission {mission.id}")
                return cached

        prompt = self._build_prompt(mission, context)
        prompt_hash = self._hash_prompt(prompt)

        logger.info(f"LLM reasoning for mission {mission.id} (prompt_hash: {prompt_hash})")

        # Try with retries and fallbacks
        for attempt in range(3):
            try:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Low temperature for consistency
                    max_tokens=500,
                    timeout=15.0  # 15 second timeout
                )

                content = response.choices[0].message.content

                # Parse and validate response
                decision = self._parse_llm_response(content, mission)

                # Cache successful decision
                if use_cache:
                    await self._cache_decision(mission, context, decision)

                # Log LLM call for audit
                logger.info(
                    f"LLM decision: {decision.action} "
                    f"(confidence: {decision.confidence:.2f}, "
                    f"tokens: {response.usage.total_tokens})"
                )

                return decision

            except openai.error.Timeout as e:
                logger.warning(f"LLM timeout on attempt {attempt + 1}: {e}")
                if attempt < 2:
                    continue
                return self._get_safe_fallback(mission, context, 'timeout')

            except openai.error.RateLimitError as e:
                logger.warning(f"LLM rate limit hit: {e}")
                return self._get_safe_fallback(mission, context, 'rate_limit')

            except openai.error.APIError as e:
                logger.error(f"LLM API error: {e}")
                if attempt < 2:
                    continue
                return self._get_safe_fallback(mission, context, 'api_error')

            except json.JSONDecodeError as e:
                logger.error(f"LLM returned invalid JSON: {e}")
                return self._get_safe_fallback(mission, context, 'invalid_response')

            except Exception as e:
                logger.error(f"Unexpected LLM error: {e}", exc_info=True)
                return self._get_safe_fallback(mission, context, 'unknown_error')

        # If all retries failed
        return self._get_safe_fallback(mission, context, 'max_retries_exceeded')

    def _parse_llm_response(self, content: str, mission: Mission) -> Decision:
        """Parse and validate LLM response"""
        try:
            decision_json = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                decision_json = json.loads(json_match.group(1))
            else:
                raise ValueError("Could not parse LLM response as JSON")

        # Validate required fields
        required_fields = ['action', 'reason', 'confidence']
        for field in required_fields:
            if field not in decision_json:
                raise ValueError(f"LLM response missing required field: {field}")

        # Validate confidence range
        confidence = float(decision_json['confidence'])
        if not (0.0 <= confidence <= 1.0):
            logger.warning(f"Invalid confidence {confidence}, clamping to 0-1 range")
            confidence = max(0.0, min(1.0, confidence))

        # Check if approval required based on confidence
        requires_approval = decision_json.get('requires_approval', False)
        if confidence < self.AUTO_EXECUTE_THRESHOLD:
            requires_approval = True

        decision = Decision(
            action=decision_json['action'],
            params=decision_json.get('params', {}),
            reason=decision_json['reason'],
            confidence=confidence,
            alternatives_considered=decision_json.get('alternatives_considered', []),
            llm_used=True
        )

        # Add approval flag to params
        if requires_approval:
            decision.params['requires_approval'] = True

        return decision

    def _get_safe_fallback(
        self,
        mission: Mission,
        context: Dict[str, Any],
        error_type: str
    ) -> Decision:
        """Get safe fallback decision when LLM fails"""
        fallback_action = self.error_fallbacks.get(error_type, 'escalate_to_human')

        logger.warning(
            f"LLM fallback triggered: {error_type} → {fallback_action} "
            f"for mission {mission.id}"
        )

        return Decision(
            action=fallback_action,
            params={
                'error_type': error_type,
                'mission_id': mission.id,
                'fallback_reason': 'llm_unavailable',
                'requires_approval': True
            },
            reason=f'llm_failed_{error_type}',
            confidence=0.0,
            llm_used=True
        )

    async def _get_cached_decision(
        self,
        mission: Mission,
        context: Dict[str, Any]
    ) -> Optional[Decision]:
        """Get cached decision if available"""
        cache_key = self._get_cache_key(mission, context)

        # Try Redis first
        if self.redis_client:
            try:
                cached_json = await self.redis_client.get(f"llm_decision:{cache_key}")
                if cached_json:
                    cached_data = json.loads(cached_json)
                    return Decision(**cached_data)
            except Exception as e:
                logger.warning(f"Redis cache read failed: {e}")

        # Fallback to in-memory cache
        return self._cache.get(cache_key)

    async def _cache_decision(
        self,
        mission: Mission,
        context: Dict[str, Any],
        decision: Decision
    ) -> None:
        """Cache decision for future use"""
        cache_key = self._get_cache_key(mission, context)

        # Convert decision to dict for caching
        decision_dict = {
            'action': decision.action,
            'params': decision.params,
            'reason': decision.reason,
            'confidence': decision.confidence,
            'alternatives_considered': decision.alternatives_considered,
            'llm_used': decision.llm_used
        }

        # Cache in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"llm_decision:{cache_key}",
                    3600,  # 1 hour TTL
                    json.dumps(decision_dict)
                )
            except Exception as e:
                logger.warning(f"Redis cache write failed: {e}")

        # Also cache in memory
        self._cache[cache_key] = decision

    def _get_cache_key(self, mission: Mission, context: Dict[str, Any]) -> str:
        """Generate cache key for decision"""
        import hashlib

        # Use mission type, state, and sanitized context
        cache_input = {
            'type': mission.type.value,
            'state': mission.state.value,
            'priority': mission.priority,
            'context_hash': self._hash_context(context)
        }

        cache_str = json.dumps(cache_input, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()[:16]

    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Hash context for caching (exclude volatile fields)"""
        import hashlib

        # Exclude timestamps and IDs from hash
        exclude_keys = {'timestamp', 'created_at', 'updated_at', 'id', 'correlation_id'}
        filtered_context = {
            k: v for k, v in context.items()
            if k not in exclude_keys
        }

        context_str = json.dumps(filtered_context, sort_keys=True, default=str)
        return hashlib.sha256(context_str.encode()).hexdigest()[:16]

    def _hash_prompt(self, prompt: str) -> str:
        """Hash prompt for logging"""
        import hashlib
        return hashlib.sha256(prompt.encode()).hexdigest()[:8]

    def _build_prompt(self, mission: Mission, context: Dict[str, Any]) -> str:
        """Build prompt for LLM"""
        # Redact sensitive data from context
        safe_context = self._redact_sensitive_data(context)

        return f"""Mission Context:
ID: {mission.id}
Type: {mission.type.value}
State: {mission.state.value}
Priority: {mission.priority}
User ID: {mission.user_id}

Additional Context:
{json.dumps(safe_context, indent=2, default=str)}

What action should Rex take next? Provide your decision in JSON format."""

    def _redact_sensitive_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Redact PII and sensitive data from context before LLM call"""
        sensitive_keys = {
            'email', 'phone', 'ssn', 'credit_card', 'api_key',
            'password', 'token', 'secret', 'address'
        }

        def redact_dict(d: Dict[str, Any]) -> Dict[str, Any]:
            result = {}
            for k, v in d.items():
                if any(sensitive in k.lower() for sensitive in sensitive_keys):
                    result[k] = '[REDACTED]'
                elif isinstance(v, dict):
                    result[k] = redact_dict(v)
                elif isinstance(v, list):
                    result[k] = [
                        redact_dict(item) if isinstance(item, dict) else item
                        for item in v
                    ]
                else:
                    result[k] = v
            return result

        return redact_dict(context)


# ============================================================================
# REX DECISION ENGINE (Main Orchestrator)
# ============================================================================

class RexDecisionEngine:
    """
    Three-layer decision architecture:
    1. State Machine (deterministic, fast) - 80% of decisions
    2. Rule Engine (business logic) - 15% of decisions
    3. LLM Reasoner (complex decisions) - 5% of decisions
    """

    def __init__(
        self,
        supabase,
        openai_api_key: Optional[str] = None,
        redis_client=None
    ):
        self.db = supabase
        self.redis_client = redis_client
        self.state_machine = StateMachine()
        self.rule_engine = RuleEngine(supabase)
        self.llm_reasoner = LLMReasoner(openai_api_key, redis_client)

        # Enhanced statistics tracking
        self.stats = {
            'state_machine_decisions': 0,
            'rule_engine_decisions': 0,
            'llm_decisions': 0,
            'llm_cache_hits': 0,
            'llm_cache_misses': 0,
            'llm_fallbacks': 0,
            'total_decision_time_ms': 0,
            'decisions_by_rule': {},  # Track which rules are used most
            'decisions_by_confidence': {'high': 0, 'medium': 0, 'low': 0},
        }

        self.decision_history = []  # Store recent decisions for analysis

    async def decide_next_action(
        self,
        mission: Mission,
        context: Dict[str, Any]
    ) -> Decision:
        """
        Main decision entry point with enhanced statistics tracking.
        Routes to appropriate decision layer.
        """
        import time

        start_time = time.time()

        logger.info(
            f"Decision request: Mission {mission.id} ({mission.type}) "
            f"in state {mission.state}"
        )

        decision = None
        decision_layer = None

        # Layer 1: State Machine (deterministic transitions)
        if self.state_machine.can_handle(mission.state, context):
            self.stats['state_machine_decisions'] += 1
            decision = await self.state_machine.decide(mission, context)
            decision_layer = 'state_machine'
            logger.info(f"Decision: State machine → {decision.action}")

        # Layer 2: Rule Engine (business logic)
        elif self.rule_engine.has_matching_rule(mission, context):
            self.stats['rule_engine_decisions'] += 1
            decision = await self.rule_engine.evaluate(mission, context)
            decision_layer = 'rule_engine'

            # Track which rule was used
            rule_name = context.get('matched_rule', 'unknown')
            self.stats['decisions_by_rule'][rule_name] = \
                self.stats['decisions_by_rule'].get(rule_name, 0) + 1

            logger.info(f"Decision: Rule engine → {decision.action}")

        # Layer 3: LLM Reasoner (complex reasoning)
        else:
            logger.info("No deterministic decision found - using LLM reasoner")
            self.stats['llm_decisions'] += 1

            # Check if this was a cache hit
            cache_key = self.llm_reasoner._get_cache_key(mission, context)
            was_cached = cache_key in self.llm_reasoner._cache

            decision = await self.llm_reasoner.reason(mission, context)
            decision_layer = 'llm_reasoner'

            if was_cached:
                self.stats['llm_cache_hits'] += 1
            else:
                self.stats['llm_cache_misses'] += 1

            # Track LLM fallbacks
            if decision.action in ['escalate_to_human', 'use_safe_default']:
                self.stats['llm_fallbacks'] += 1

            logger.info(f"Decision: LLM reasoner → {decision.action}")

        # Track decision time
        duration_ms = int((time.time() - start_time) * 1000)
        self.stats['total_decision_time_ms'] += duration_ms

        # Track confidence distribution
        if decision.confidence >= 0.9:
            self.stats['decisions_by_confidence']['high'] += 1
        elif decision.confidence >= 0.7:
            self.stats['decisions_by_confidence']['medium'] += 1
        else:
            self.stats['decisions_by_confidence']['low'] += 1

        # Store in decision history (keep last 1000)
        self.decision_history.append({
            'mission_id': mission.id,
            'mission_type': mission.type.value,
            'mission_state': mission.state.value,
            'action': decision.action,
            'confidence': decision.confidence,
            'decision_layer': decision_layer,
            'duration_ms': duration_ms,
            'timestamp': datetime.utcnow().isoformat(),
        })

        if len(self.decision_history) > 1000:
            self.decision_history.pop(0)

        # Persist decision to database for audit trail
        await self._log_decision_to_db(mission, decision, decision_layer, duration_ms)

        return decision

    async def _log_decision_to_db(
        self,
        mission: Mission,
        decision: Decision,
        decision_layer: str,
        duration_ms: int
    ) -> None:
        """Log decision to database for audit trail"""
        try:
            self.db.table("agent_logs").insert({
                "mission_id": mission.id,
                "agent_name": "RexDecisionEngine",
                "event_type": "decision_made",
                "data": {
                    "action": decision.action,
                    "params": decision.params,
                    "reason": decision.reason,
                    "confidence": decision.confidence,
                    "decision_layer": decision_layer,
                    "llm_used": decision.llm_used,
                    "alternatives_considered": decision.alternatives_considered,
                },
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log decision to database: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive decision engine statistics"""
        total_decisions = (
            self.stats['state_machine_decisions'] +
            self.stats['rule_engine_decisions'] +
            self.stats['llm_decisions']
        )

        avg_decision_time = (
            (self.stats['total_decision_time_ms'] / total_decisions)
            if total_decisions > 0 else 0
        )

        llm_cache_rate = (
            (self.stats['llm_cache_hits'] /
             (self.stats['llm_cache_hits'] + self.stats['llm_cache_misses']) * 100)
            if (self.stats['llm_cache_hits'] + self.stats['llm_cache_misses']) > 0
            else 0
        )

        return {
            # Core counters
            'total_decisions': total_decisions,
            'state_machine_decisions': self.stats['state_machine_decisions'],
            'rule_engine_decisions': self.stats['rule_engine_decisions'],
            'llm_decisions': self.stats['llm_decisions'],

            # Distribution percentages
            'state_machine_percentage': (
                (self.stats['state_machine_decisions'] / total_decisions * 100)
                if total_decisions > 0 else 0
            ),
            'rule_engine_percentage': (
                (self.stats['rule_engine_decisions'] / total_decisions * 100)
                if total_decisions > 0 else 0
            ),
            'llm_percentage': (
                (self.stats['llm_decisions'] / total_decisions * 100)
                if total_decisions > 0 else 0
            ),

            # Performance metrics
            'avg_decision_time_ms': avg_decision_time,
            'total_decision_time_ms': self.stats['total_decision_time_ms'],

            # LLM metrics
            'llm_cache_hits': self.stats['llm_cache_hits'],
            'llm_cache_misses': self.stats['llm_cache_misses'],
            'llm_cache_hit_rate': llm_cache_rate,
            'llm_fallbacks': self.stats['llm_fallbacks'],

            # Rule usage breakdown
            'decisions_by_rule': self.stats['decisions_by_rule'],
            'top_rules_used': sorted(
                self.stats['decisions_by_rule'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5] if self.stats['decisions_by_rule'] else [],

            # Confidence distribution
            'decisions_by_confidence': self.stats['decisions_by_confidence'],
            'confidence_distribution': {
                'high_pct': (
                    self.stats['decisions_by_confidence']['high'] / total_decisions * 100
                    if total_decisions > 0 else 0
                ),
                'medium_pct': (
                    self.stats['decisions_by_confidence']['medium'] / total_decisions * 100
                    if total_decisions > 0 else 0
                ),
                'low_pct': (
                    self.stats['decisions_by_confidence']['low'] / total_decisions * 100
                    if total_decisions > 0 else 0
                ),
            },
        }

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        return self.decision_history[-limit:]

    def get_decision_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze decision trends over time"""
        from collections import defaultdict

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        recent_decisions = [
            d for d in self.decision_history
            if datetime.fromisoformat(d['timestamp']) >= cutoff_time
        ]

        # Group by hour
        by_hour = defaultdict(lambda: {
            'state_machine': 0,
            'rule_engine': 0,
            'llm_reasoner': 0,
            'total': 0,
            'avg_confidence': [],
            'avg_duration_ms': []
        })

        for decision in recent_decisions:
            hour = datetime.fromisoformat(decision['timestamp']).replace(
                minute=0, second=0, microsecond=0
            ).isoformat()

            by_hour[hour][decision['decision_layer']] += 1
            by_hour[hour]['total'] += 1
            by_hour[hour]['avg_confidence'].append(decision['confidence'])
            by_hour[hour]['avg_duration_ms'].append(decision['duration_ms'])

        # Calculate averages
        trends = {}
        for hour, data in sorted(by_hour.items()):
            trends[hour] = {
                'state_machine': data['state_machine'],
                'rule_engine': data['rule_engine'],
                'llm_reasoner': data['llm_reasoner'],
                'total': data['total'],
                'avg_confidence': (
                    sum(data['avg_confidence']) / len(data['avg_confidence'])
                    if data['avg_confidence'] else 0
                ),
                'avg_duration_ms': (
                    sum(data['avg_duration_ms']) / len(data['avg_duration_ms'])
                    if data['avg_duration_ms'] else 0
                ),
            }

        return {
            'period_hours': hours,
            'total_decisions': len(recent_decisions),
            'trends_by_hour': trends,
        }

    def reset_stats(self) -> None:
        """Reset statistics (useful for testing or periodic resets)"""
        self.stats = {
            'state_machine_decisions': 0,
            'rule_engine_decisions': 0,
            'llm_decisions': 0,
            'llm_cache_hits': 0,
            'llm_cache_misses': 0,
            'llm_fallbacks': 0,
            'total_decision_time_ms': 0,
            'decisions_by_rule': {},
            'decisions_by_confidence': {'high': 0, 'medium': 0, 'low': 0},
        }
        self.decision_history = []
        logger.info("Decision engine statistics reset")
