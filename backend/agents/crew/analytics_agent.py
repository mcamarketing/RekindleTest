"""
AnalyticsAgent - Performance Tracking & Optimization Specialist

Analyzes campaign performance, tracks KPIs, identifies optimization opportunities,
and generates actionable insights for continuous improvement.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

from .base_agent import BaseAgent, MissionContext, AgentResult
from ...crewai_agents.tools.mcp_db_tools import get_mcp_db_tools

logger = logging.getLogger(__name__)


@dataclass
class CampaignMetrics:
    """Campaign performance metrics"""
    campaign_id: str
    campaign_name: str
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_replied: int
    total_bounced: int
    total_unsubscribed: int
    open_rate: float
    click_rate: float
    reply_rate: float
    bounce_rate: float
    conversion_rate: float
    cost_per_lead: float
    roi: float


@dataclass
class OptimizationRecommendation:
    """Actionable optimization recommendation"""
    category: str  # subject_line, send_time, targeting, content
    priority: str  # high, medium, low
    title: str
    description: str
    expected_impact: str
    implementation_effort: str  # low, medium, high
    data_supporting: Dict[str, Any]


class AnalyticsAgent(BaseAgent):
    """
    Specialized agent for performance analytics and optimization.

    Capabilities:
    - Campaign performance tracking and reporting
    - KPI calculation and trend analysis
    - A/B test analysis and winner selection
    - Engagement pattern detection
    - Cohort analysis
    - Predictive analytics for campaign optimization
    - Automated insight generation
    - ROI and attribution tracking
    """

    def __init__(self, supabase, redis_client=None, openai_api_key=None):
        super().__init__(
            agent_name="AnalyticsAgent",
            supabase=supabase,
            redis_client=redis_client,
            openai_api_key=openai_api_key
        )

        # Analytics configuration
        self.KPI_THRESHOLDS = {
            'open_rate': {'excellent': 0.35, 'good': 0.25, 'fair': 0.15, 'poor': 0.10},
            'click_rate': {'excellent': 0.10, 'good': 0.05, 'fair': 0.02, 'poor': 0.01},
            'reply_rate': {'excellent': 0.20, 'good': 0.10, 'fair': 0.05, 'poor': 0.02},
            'bounce_rate': {'excellent': 0.02, 'good': 0.05, 'fair': 0.10, 'poor': 0.15},
        }

        self.MIN_SAMPLE_SIZE_AB_TEST = 30  # Minimum messages for valid A/B test

        # Initialize MCP DB Tools
        self.mcp_db_tools = get_mcp_db_tools()

    async def handle_mission(self, context: MissionContext) -> AgentResult:
        """Execute analytics and optimization mission"""
        logger.info(f"AnalyticsAgent starting mission {context.mission_id}")

        # Get analysis parameters
        campaign_ids = context.custom_params.get('campaign_ids', [])
        time_range_days = context.custom_params.get('time_range_days', 30)
        include_recommendations = context.custom_params.get('include_recommendations', True)
        analyze_ab_tests = context.custom_params.get('analyze_ab_tests', True)

        # Step 1: Fetch campaign data
        campaigns = await self._fetch_campaigns(campaign_ids, context.user_id, time_range_days)
        logger.info(f"Analyzing {len(campaigns)} campaigns")

        # Step 2: Calculate metrics for each campaign
        campaign_metrics = []
        for campaign in campaigns:
            metrics = await self._calculate_campaign_metrics(campaign)
            campaign_metrics.append(metrics)

        # Step 3: Analyze A/B tests if requested
        ab_test_results = []
        if analyze_ab_tests:
            ab_test_results = await self._analyze_ab_tests(campaigns)

        # Step 4: Identify trends and patterns
        trends = await self._identify_trends(campaign_metrics, time_range_days)

        # Step 5: Generate optimization recommendations
        recommendations = []
        if include_recommendations:
            recommendations = await self._generate_recommendations(
                campaign_metrics,
                ab_test_results,
                trends
            )

        # Step 6: Store analytics results
        await self._store_analytics_results(campaign_metrics, recommendations, context)

        # Build result
        result_data = {
            'campaigns_analyzed': len(campaigns),
            'total_messages_sent': sum(m.total_sent for m in campaign_metrics),
            'aggregate_metrics': self._calculate_aggregate_metrics(campaign_metrics),
            'top_performing_campaigns': self._get_top_performers(campaign_metrics, limit=5),
            'underperforming_campaigns': self._get_underperformers(campaign_metrics, limit=5),
            'ab_test_results': ab_test_results,
            'trends': trends,
            'recommendations': [
                {
                    'category': r.category,
                    'priority': r.priority,
                    'title': r.title,
                    'expected_impact': r.expected_impact,
                }
                for r in recommendations
            ],
        }

        success = len(campaign_metrics) > 0

        return AgentResult(
            success=success,
            data=result_data,
            message=f"Analyzed {len(campaigns)} campaigns, generated {len(recommendations)} recommendations"
        )

    async def _fetch_campaigns(
        self,
        campaign_ids: List[str],
        user_id: str,
        time_range_days: int
    ) -> List[Dict[str, Any]]:
        """Fetch campaigns for analysis"""
        cutoff_date = (datetime.utcnow() - timedelta(days=time_range_days)).isoformat()

        query = self.db.table('campaigns').select('*').eq('user_id', user_id)

        if campaign_ids:
            query = query.in_('id', campaign_ids)
        else:
            query = query.gte('created_at', cutoff_date)

        result = query.execute()
        return result.data if result.data else []

    async def _calculate_campaign_metrics(
        self,
        campaign: Dict[str, Any]
    ) -> CampaignMetrics:
        """Calculate comprehensive metrics for a campaign using MCP DB Tools"""
        campaign_id = campaign['id']

        # Use MCP DB Tool for campaign performance
        performance_data = self.mcp_db_tools.get_campaign_performance(campaign_id)

        # Extract metrics from MCP response
        total_sent = performance_data.get('total_sent', 0)
        total_delivered = performance_data.get('total_delivered', 0)
        total_opened = performance_data.get('total_opened', 0)
        total_clicked = performance_data.get('total_clicked', 0)
        total_replied = performance_data.get('total_replied', 0)
        total_bounced = performance_data.get('total_bounced', 0)
        total_unsubscribed = performance_data.get('total_unsubscribed', 0)
        open_rate = performance_data.get('open_rate', 0.0)
        click_rate = performance_data.get('click_rate', 0.0)
        reply_rate = performance_data.get('reply_rate', 0.0)
        bounce_rate = performance_data.get('bounce_rate', 0.0)
        conversion_rate = performance_data.get('conversion_rate', 0.0)
        cost_per_lead = performance_data.get('cost_per_lead', 0.0)
        roi = performance_data.get('roi', 0.0)

        return CampaignMetrics(
            campaign_id=campaign_id,
            campaign_name=campaign.get('name', 'Unnamed Campaign'),
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_opened=total_opened,
            total_clicked=total_clicked,
            total_replied=total_replied,
            total_bounced=total_bounced,
            total_unsubscribed=total_unsubscribed,
            open_rate=round(open_rate, 3),
            click_rate=round(click_rate, 3),
            reply_rate=round(reply_rate, 3),
            bounce_rate=round(bounce_rate, 3),
            conversion_rate=round(conversion_rate, 3),
            cost_per_lead=round(cost_per_lead, 2),
            roi=round(roi, 2),
        )

    async def _fetch_engagement_events(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Fetch all engagement events for a campaign"""
        # Join outreach_messages and engagement_events
        messages_result = self.db.table('outreach_messages')\
            .select('id')\
            .eq('campaign_id', campaign_id)\
            .execute()

        if not messages_result.data:
            return []

        message_ids = [m['id'] for m in messages_result.data]

        events_result = self.db.table('engagement_events')\
            .select('*')\
            .in_('message_id', message_ids)\
            .execute()

        return events_result.data if events_result.data else []

    async def _analyze_ab_tests(
        self,
        campaigns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze A/B test results and determine winners"""
        ab_test_results = []

        for campaign in campaigns:
            # Check if this is an A/B test campaign
            if not campaign.get('is_ab_test'):
                continue

            campaign_id = campaign['id']

            # Fetch messages grouped by variant
            messages_result = self.db.table('outreach_messages')\
                .select('*')\
                .eq('campaign_id', campaign_id)\
                .execute()

            if not messages_result.data:
                continue

            # Group by variant
            variants = defaultdict(list)
            for msg in messages_result.data:
                variant = msg.get('variant', 'A')
                variants[variant].append(msg)

            # Need at least 2 variants
            if len(variants) < 2:
                continue

            # Calculate metrics for each variant
            variant_metrics = {}
            for variant, messages in variants.items():
                # Skip if sample size too small
                if len(messages) < self.MIN_SAMPLE_SIZE_AB_TEST:
                    continue

                message_ids = [m['id'] for m in messages]

                # Fetch engagement events for this variant
                events_result = self.db.table('engagement_events')\
                    .select('*')\
                    .in_('message_id', message_ids)\
                    .execute()

                events = events_result.data if events_result.data else []

                # Calculate variant metrics
                total_sent = len(messages)
                total_opened = len([e for e in events if e['event_type'] == 'opened'])
                total_clicked = len([e for e in events if e['event_type'] == 'clicked'])
                total_replied = len([e for e in events if e['event_type'] == 'replied'])

                variant_metrics[variant] = {
                    'total_sent': total_sent,
                    'open_rate': total_opened / total_sent if total_sent > 0 else 0.0,
                    'click_rate': total_clicked / total_sent if total_sent > 0 else 0.0,
                    'reply_rate': total_replied / total_sent if total_sent > 0 else 0.0,
                }

            # Determine winner based on reply rate (primary KPI)
            if len(variant_metrics) >= 2:
                winner = max(variant_metrics.items(), key=lambda x: x[1]['reply_rate'])

                # Calculate statistical significance (simplified)
                confidence = self._calculate_ab_test_confidence(variant_metrics)

                ab_test_results.append({
                    'campaign_id': campaign_id,
                    'campaign_name': campaign.get('name'),
                    'winner': winner[0],
                    'confidence': confidence,
                    'variant_metrics': variant_metrics,
                    'recommendation': f"Use variant {winner[0]} for future campaigns" if confidence > 0.95 else "Continue testing - not statistically significant",
                })

        return ab_test_results

    def _calculate_ab_test_confidence(self, variant_metrics: Dict[str, Dict[str, Any]]) -> float:
        """Calculate statistical confidence of A/B test (simplified)"""
        # Simplified confidence calculation
        # In production, would use proper statistical tests (t-test, chi-square, etc.)

        if len(variant_metrics) < 2:
            return 0.0

        variants = list(variant_metrics.values())
        variant_a = variants[0]
        variant_b = variants[1]

        # Sample size factor
        total_sample = variant_a['total_sent'] + variant_b['total_sent']
        sample_factor = min(1.0, total_sample / (self.MIN_SAMPLE_SIZE_AB_TEST * 4))

        # Effect size factor
        rate_diff = abs(variant_a['reply_rate'] - variant_b['reply_rate'])
        effect_factor = min(1.0, rate_diff / 0.1)  # 10% difference = max effect

        # Combined confidence (simplified)
        confidence = (sample_factor * 0.5) + (effect_factor * 0.5)

        return round(confidence, 2)

    async def _identify_trends(
        self,
        campaign_metrics: List[CampaignMetrics],
        time_range_days: int
    ) -> Dict[str, Any]:
        """Identify performance trends over time"""
        if not campaign_metrics:
            return {}

        # Calculate aggregate metrics
        avg_open_rate = sum(m.open_rate for m in campaign_metrics) / len(campaign_metrics)
        avg_click_rate = sum(m.click_rate for m in campaign_metrics) / len(campaign_metrics)
        avg_reply_rate = sum(m.reply_rate for m in campaign_metrics) / len(campaign_metrics)
        avg_bounce_rate = sum(m.bounce_rate for m in campaign_metrics) / len(campaign_metrics)

        # Compare to historical averages (would need time-series data in production)
        # For now, use static benchmarks
        benchmarks = {
            'open_rate': 0.25,
            'click_rate': 0.05,
            'reply_rate': 0.10,
            'bounce_rate': 0.05,
        }

        trends = {
            'avg_open_rate': round(avg_open_rate, 3),
            'avg_click_rate': round(avg_click_rate, 3),
            'avg_reply_rate': round(avg_reply_rate, 3),
            'avg_bounce_rate': round(avg_bounce_rate, 3),
            'vs_benchmark': {
                'open_rate': round((avg_open_rate - benchmarks['open_rate']) / benchmarks['open_rate'], 2),
                'click_rate': round((avg_click_rate - benchmarks['click_rate']) / benchmarks['click_rate'], 2),
                'reply_rate': round((avg_reply_rate - benchmarks['reply_rate']) / benchmarks['reply_rate'], 2),
                'bounce_rate': round((avg_bounce_rate - benchmarks['bounce_rate']) / benchmarks['bounce_rate'], 2),
            },
            'trend_direction': self._determine_trend_direction(campaign_metrics),
        }

        return trends

    def _determine_trend_direction(self, campaign_metrics: List[CampaignMetrics]) -> str:
        """Determine overall trend direction"""
        if len(campaign_metrics) < 2:
            return 'insufficient_data'

        # Sort by campaign ID (proxy for time)
        sorted_metrics = sorted(campaign_metrics, key=lambda m: m.campaign_id)

        # Compare first half vs second half
        midpoint = len(sorted_metrics) // 2
        first_half = sorted_metrics[:midpoint]
        second_half = sorted_metrics[midpoint:]

        first_avg = sum(m.reply_rate for m in first_half) / len(first_half)
        second_avg = sum(m.reply_rate for m in second_half) / len(second_half)

        if second_avg > first_avg * 1.1:
            return 'improving'
        elif second_avg < first_avg * 0.9:
            return 'declining'
        else:
            return 'stable'

    async def _generate_recommendations(
        self,
        campaign_metrics: List[CampaignMetrics],
        ab_test_results: List[Dict[str, Any]],
        trends: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """Generate actionable optimization recommendations"""
        recommendations = []

        # Recommendation 1: Low open rates
        low_open_campaigns = [m for m in campaign_metrics if m.open_rate < 0.15]
        if len(low_open_campaigns) > 0:
            recommendations.append(OptimizationRecommendation(
                category='subject_line',
                priority='high',
                title='Improve subject lines for low-open campaigns',
                description=f'{len(low_open_campaigns)} campaigns have open rates below 15%. Test different subject line formulas (question-based, curiosity-driven, personalized).',
                expected_impact='20-40% increase in open rates',
                implementation_effort='low',
                data_supporting={
                    'affected_campaigns': len(low_open_campaigns),
                    'avg_open_rate': round(sum(m.open_rate for m in low_open_campaigns) / len(low_open_campaigns), 3),
                }
            ))

        # Recommendation 2: Low reply rates
        low_reply_campaigns = [m for m in campaign_metrics if m.reply_rate < 0.05]
        if len(low_reply_campaigns) > 0:
            recommendations.append(OptimizationRecommendation(
                category='content',
                priority='high',
                title='Strengthen call-to-action and value proposition',
                description=f'{len(low_reply_campaigns)} campaigns have reply rates below 5%. Review message body for clear value proposition and low-friction CTA.',
                expected_impact='15-30% increase in reply rates',
                implementation_effort='medium',
                data_supporting={
                    'affected_campaigns': len(low_reply_campaigns),
                    'avg_reply_rate': round(sum(m.reply_rate for m in low_reply_campaigns) / len(low_reply_campaigns), 3),
                }
            ))

        # Recommendation 3: High bounce rates
        high_bounce_campaigns = [m for m in campaign_metrics if m.bounce_rate > 0.10]
        if len(high_bounce_campaigns) > 0:
            recommendations.append(OptimizationRecommendation(
                category='targeting',
                priority='critical',
                title='Clean email list and improve data quality',
                description=f'{len(high_bounce_campaigns)} campaigns have bounce rates above 10%. Implement email verification and list cleaning.',
                expected_impact='50-70% reduction in bounce rate',
                implementation_effort='medium',
                data_supporting={
                    'affected_campaigns': len(high_bounce_campaigns),
                    'avg_bounce_rate': round(sum(m.bounce_rate for m in high_bounce_campaigns) / len(high_bounce_campaigns), 3),
                }
            ))

        # Recommendation 4: A/B test winners
        for ab_result in ab_test_results:
            if ab_result['confidence'] > 0.85:
                recommendations.append(OptimizationRecommendation(
                    category='content',
                    priority='medium',
                    title=f"Scale winning variant for {ab_result['campaign_name']}",
                    description=ab_result['recommendation'],
                    expected_impact=f"Maintain {ab_result['variant_metrics'][ab_result['winner']]['reply_rate']:.1%} reply rate",
                    implementation_effort='low',
                    data_supporting=ab_result['variant_metrics']
                ))

        # Recommendation 5: Send time optimization
        avg_open_rate = trends.get('avg_open_rate', 0)
        if avg_open_rate < 0.20:
            recommendations.append(OptimizationRecommendation(
                category='send_time',
                priority='medium',
                title='Test different send times',
                description='Overall open rates suggest send timing may not be optimal. Test sending at 8-10am and 2-4pm local time.',
                expected_impact='10-20% increase in open rates',
                implementation_effort='low',
                data_supporting={'current_avg_open_rate': avg_open_rate}
            ))

        # Sort recommendations by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 4))

        return recommendations

    def _calculate_aggregate_metrics(
        self,
        campaign_metrics: List[CampaignMetrics]
    ) -> Dict[str, Any]:
        """Calculate aggregate metrics across all campaigns"""
        if not campaign_metrics:
            return {}

        total_sent = sum(m.total_sent for m in campaign_metrics)
        total_delivered = sum(m.total_delivered for m in campaign_metrics)
        total_opened = sum(m.total_opened for m in campaign_metrics)
        total_clicked = sum(m.total_clicked for m in campaign_metrics)
        total_replied = sum(m.total_replied for m in campaign_metrics)

        return {
            'total_sent': total_sent,
            'total_delivered': total_delivered,
            'total_opened': total_opened,
            'total_clicked': total_clicked,
            'total_replied': total_replied,
            'aggregate_open_rate': round(total_opened / total_delivered, 3) if total_delivered > 0 else 0.0,
            'aggregate_click_rate': round(total_clicked / total_delivered, 3) if total_delivered > 0 else 0.0,
            'aggregate_reply_rate': round(total_replied / total_delivered, 3) if total_delivered > 0 else 0.0,
        }

    def _get_top_performers(
        self,
        campaign_metrics: List[CampaignMetrics],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top performing campaigns by reply rate"""
        sorted_campaigns = sorted(campaign_metrics, key=lambda m: m.reply_rate, reverse=True)

        return [
            {
                'campaign_id': m.campaign_id,
                'campaign_name': m.campaign_name,
                'reply_rate': m.reply_rate,
                'total_sent': m.total_sent,
                'roi': m.roi,
            }
            for m in sorted_campaigns[:limit]
        ]

    def _get_underperformers(
        self,
        campaign_metrics: List[CampaignMetrics],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get underperforming campaigns by reply rate"""
        sorted_campaigns = sorted(campaign_metrics, key=lambda m: m.reply_rate)

        return [
            {
                'campaign_id': m.campaign_id,
                'campaign_name': m.campaign_name,
                'reply_rate': m.reply_rate,
                'total_sent': m.total_sent,
                'bounce_rate': m.bounce_rate,
            }
            for m in sorted_campaigns[:limit]
        ]

    async def _store_analytics_results(
        self,
        campaign_metrics: List[CampaignMetrics],
        recommendations: List[OptimizationRecommendation],
        context: MissionContext
    ) -> None:
        """Store analytics results in database"""
        # Store in agent_logs for now
        # In production, would have dedicated analytics tables

        try:
            self.db.table('agent_logs').insert({
                'mission_id': context.mission_id,
                'agent_name': self.agent_name,
                'event_type': 'custom',
                'data': {
                    'event': 'analytics_report_generated',
                    'campaigns_analyzed': len(campaign_metrics),
                    'recommendations_count': len(recommendations),
                    'timestamp': datetime.utcnow().isoformat(),
                }
            }).execute()

        except Exception as e:
            logger.error(f"Failed to store analytics results: {e}")
