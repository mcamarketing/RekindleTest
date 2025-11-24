"""
ICPIntelligenceAgent - Ideal Customer Profile Analysis

Analyzes customer data to extract ICP patterns, identifies high-value segments,
and provides data-driven targeting recommendations for campaigns.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict

from .base_agent import BaseAgent, MissionContext, AgentResult
from ...crewai_agents.tools.mcp_db_tools import get_mcp_db_tools

logger = logging.getLogger(__name__)


@dataclass
class ICPProfile:
    """Ideal Customer Profile"""
    profile_name: str
    company_size_range: tuple
    industries: List[str]
    job_titles: List[str]
    common_pain_points: List[str]
    avg_deal_value: float
    conversion_rate: float
    lead_count: int
    characteristics: Dict[str, Any]


class ICPIntelligenceAgent(BaseAgent):
    """
    Specialized agent for ICP extraction and analysis.

    Capabilities:
    - Analyze customer database for patterns
    - Extract common characteristics of best customers
    - Segment leads by ICP fit score
    - Generate targeting recommendations
    - Identify lookalike prospects
    - Track ICP evolution over time
    """

    def __init__(self, supabase, redis_client=None, openai_api_key=None):
        super().__init__(
            agent_name="ICPIntelligenceAgent",
            supabase=supabase,
            redis_client=redis_client,
            openai_api_key=openai_api_key
        )

        # Analysis parameters
        self.MIN_SAMPLE_SIZE = 10
        self.HIGH_VALUE_PERCENTILE = 0.75

        # Initialize MCP DB Tools
        self.mcp_db_tools = get_mcp_db_tools()

    async def handle_mission(self, context: MissionContext) -> AgentResult:
        """Execute ICP analysis mission"""
        logger.info(f"ICPIntelligenceAgent starting mission {context.mission_id}")

        # Step 1: Fetch all leads and customers
        leads = await self._fetch_leads(context)
        customers = await self._fetch_customers(context)

        # Fetch dormant leads using MCP DB Tools
        dormant_leads = self.mcp_db_tools.get_dormant_leads(context.user_id, datetime.utcnow() - timedelta(days=30))

        logger.info(f"Analyzing {len(leads)} leads, {len(customers)} customers, and {len(dormant_leads)} dormant leads")

        # Step 2: Analyze best customers to extract ICP
        icp_profiles = await self._extract_icp_profiles(customers)

        logger.info(f"Extracted {len(icp_profiles)} ICP profiles")

        # Step 3: Score leads against ICP
        scored_leads = await self._score_leads_against_icp(leads, icp_profiles)

        # Step 4: Generate targeting recommendations
        recommendations = await self._generate_targeting_recommendations(
            icp_profiles,
            scored_leads
        )

        # Step 5: Store ICP profiles and scores
        stored_profiles = await self._store_icp_profiles(icp_profiles, context)
        await self._update_lead_icp_scores(scored_leads)

        # Build result
        result_data = {
            'icp_profiles_extracted': len(icp_profiles),
            'leads_scored': len(scored_leads),
            'high_fit_leads': len([l for l in scored_leads if l['icp_score'] >= 0.7]),
            'medium_fit_leads': len([l for l in scored_leads if 0.4 <= l['icp_score'] < 0.7]),
            'low_fit_leads': len([l for l in scored_leads if l['icp_score'] < 0.4]),
            'profiles': [
                {
                    'name': p.profile_name,
                    'lead_count': p.lead_count,
                    'avg_deal_value': p.avg_deal_value,
                    'conversion_rate': p.conversion_rate,
                }
                for p in icp_profiles
            ],
            'recommendations': recommendations,
        }

        success = len(icp_profiles) > 0

        return AgentResult(
            success=success,
            data=result_data,
            message=f"Extracted {len(icp_profiles)} ICP profiles, scored {len(scored_leads)} leads"
        )

    async def _fetch_leads(self, context: MissionContext) -> List[Dict[str, Any]]:
        """Fetch all leads for analysis"""
        result = self.db.table('leads')\
            .select('*')\
            .eq('user_id', context.user_id)\
            .execute()

        return result.data if result.data else []

    async def _fetch_customers(self, context: MissionContext) -> List[Dict[str, Any]]:
        """Fetch paying customers for ICP extraction"""
        result = self.db.table('leads')\
            .select('*')\
            .eq('user_id', context.user_id)\
            .eq('status', 'customer')\
            .execute()

        customers = result.data if result.data else []

        # If not enough customers, return empty to prevent poor analysis
        if len(customers) < self.MIN_SAMPLE_SIZE:
            logger.warning(
                f"Insufficient customer sample size: {len(customers)} < {self.MIN_SAMPLE_SIZE}"
            )
            return []

        return customers

    async def _extract_icp_profiles(
        self,
        customers: List[Dict[str, Any]]
    ) -> List[ICPProfile]:
        """Extract ICP profiles from customer data"""
        if not customers:
            return []

        # Group customers by common characteristics
        profiles = []

        # Strategy 1: Segment by company size
        size_segments = self._segment_by_company_size(customers)

        for size_range, segment_customers in size_segments.items():
            if len(segment_customers) < 3:  # Need minimum 3 for profile
                continue

            profile = self._build_profile_from_segment(
                segment_customers,
                f"Company Size: {size_range[0]}-{size_range[1]} employees"
            )

            profiles.append(profile)

        # Strategy 2: Segment by industry
        industry_segments = self._segment_by_industry(customers)

        for industry, segment_customers in industry_segments.items():
            if len(segment_customers) < 3:
                continue

            # Skip if already covered by size segment
            if len(profiles) > 0 and industry in profiles[0].industries:
                continue

            profile = self._build_profile_from_segment(
                segment_customers,
                f"Industry: {industry}"
            )

            profiles.append(profile)

        return profiles

    def _segment_by_company_size(
        self,
        customers: List[Dict[str, Any]]
    ) -> Dict[tuple, List[Dict[str, Any]]]:
        """Segment customers by company size"""
        segments = defaultdict(list)

        size_ranges = [
            (1, 10),
            (11, 50),
            (51, 200),
            (201, 1000),
            (1001, 10000),
        ]

        for customer in customers:
            company_size = customer.get('company_size', 0)

            for size_range in size_ranges:
                if size_range[0] <= company_size <= size_range[1]:
                    segments[size_range].append(customer)
                    break

        return dict(segments)

    def _segment_by_industry(
        self,
        customers: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Segment customers by industry"""
        segments = defaultdict(list)

        for customer in customers:
            industry = customer.get('industry', 'Unknown')
            segments[industry].append(customer)

        return dict(segments)

    def _build_profile_from_segment(
        self,
        segment: List[Dict[str, Any]],
        profile_name: str
    ) -> ICPProfile:
        """Build ICP profile from customer segment"""
        # Extract common characteristics
        industries = defaultdict(int)
        job_titles = defaultdict(int)
        pain_points = defaultdict(int)
        deal_values = []
        company_sizes = []

        for customer in segment:
            # Count industries
            industry = customer.get('industry')
            if industry:
                industries[industry] += 1

            # Count job titles
            job_title = customer.get('job_title')
            if job_title:
                job_titles[job_title] += 1

            # Count pain points
            for pain_point in customer.get('pain_points', []):
                pain_points[pain_point] += 1

            # Collect metrics
            deal_value = customer.get('deal_value', 0)
            if deal_value > 0:
                deal_values.append(deal_value)

            company_size = customer.get('company_size', 0)
            if company_size > 0:
                company_sizes.append(company_size)

        # Calculate statistics
        avg_deal_value = sum(deal_values) / len(deal_values) if deal_values else 0
        min_company_size = min(company_sizes) if company_sizes else 0
        max_company_size = max(company_sizes) if company_sizes else 0

        # Get top industries (at least 20% of segment)
        min_count = len(segment) * 0.2
        top_industries = [
            industry for industry, count in industries.items()
            if count >= min_count
        ]

        # Get top job titles
        top_job_titles = sorted(job_titles.items(), key=lambda x: x[1], reverse=True)[:5]
        top_job_titles = [title for title, _ in top_job_titles]

        # Get common pain points
        common_pain_points = sorted(pain_points.items(), key=lambda x: x[1], reverse=True)[:3]
        common_pain_points = [pain for pain, _ in common_pain_points]

        # Calculate conversion rate (simplified - would need more data)
        conversion_rate = 0.15  # Placeholder

        return ICPProfile(
            profile_name=profile_name,
            company_size_range=(min_company_size, max_company_size),
            industries=top_industries,
            job_titles=top_job_titles,
            common_pain_points=common_pain_points,
            avg_deal_value=avg_deal_value,
            conversion_rate=conversion_rate,
            lead_count=len(segment),
            characteristics={
                'segment_size': len(segment),
                'industries_distribution': dict(industries),
                'job_titles_distribution': dict(job_titles),
            }
        )

    async def _score_leads_against_icp(
        self,
        leads: List[Dict[str, Any]],
        icp_profiles: List[ICPProfile]
    ) -> List[Dict[str, Any]]:
        """Score each lead against ICP profiles"""
        scored_leads = []

        for lead in leads:
            best_score = 0.0
            best_profile = None

            # Score against each ICP profile
            for profile in icp_profiles:
                score = self._calculate_icp_fit_score(lead, profile)

                if score > best_score:
                    best_score = score
                    best_profile = profile.profile_name

            scored_leads.append({
                'lead_id': lead['id'],
                'icp_score': best_score,
                'best_fit_profile': best_profile,
                'company': lead.get('company'),
                'industry': lead.get('industry'),
            })

        return scored_leads

    def _calculate_icp_fit_score(
        self,
        lead: Dict[str, Any],
        profile: ICPProfile
    ) -> float:
        """Calculate how well a lead fits an ICP profile"""
        score = 0.0
        max_score = 0.0

        # Company size match (weight: 0.25)
        max_score += 0.25
        company_size = lead.get('company_size', 0)
        if profile.company_size_range[0] <= company_size <= profile.company_size_range[1]:
            score += 0.25
        elif company_size > 0:
            # Partial credit if close
            distance = min(
                abs(company_size - profile.company_size_range[0]),
                abs(company_size - profile.company_size_range[1])
            )
            if distance < 50:
                score += 0.15

        # Industry match (weight: 0.30)
        max_score += 0.30
        lead_industry = lead.get('industry')
        if lead_industry in profile.industries:
            score += 0.30

        # Job title match (weight: 0.25)
        max_score += 0.25
        lead_job_title = lead.get('job_title')
        if lead_job_title in profile.job_titles:
            score += 0.25
        elif lead_job_title and any(title_keyword in lead_job_title.lower() for title in profile.job_titles for title_keyword in title.lower().split()):
            score += 0.15

        # Pain point match (weight: 0.20)
        max_score += 0.20
        lead_pain_points = set(lead.get('pain_points', []))
        profile_pain_points = set(profile.common_pain_points)
        if lead_pain_points and profile_pain_points:
            overlap = len(lead_pain_points & profile_pain_points)
            if overlap > 0:
                score += 0.20 * (overlap / len(profile_pain_points))

        # Normalize score
        return score / max_score if max_score > 0 else 0.0

    async def _generate_targeting_recommendations(
        self,
        icp_profiles: List[ICPProfile],
        scored_leads: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable targeting recommendations"""
        recommendations = []

        # Recommendation 1: Focus on high-fit leads
        high_fit_count = len([l for l in scored_leads if l['icp_score'] >= 0.7])
        if high_fit_count > 0:
            recommendations.append({
                'type': 'prioritize_high_fit',
                'description': f'Prioritize {high_fit_count} high-fit leads (ICP score >= 0.7)',
                'action': 'Create dedicated campaign for high-fit leads',
                'expected_impact': 'Higher conversion rate and faster sales cycle',
            })

        # Recommendation 2: Target specific industries
        if icp_profiles:
            top_profile = max(icp_profiles, key=lambda p: p.conversion_rate)
            recommendations.append({
                'type': 'target_industry',
                'description': f'Focus on {", ".join(top_profile.industries)} with {top_profile.company_size_range[0]}-{top_profile.company_size_range[1]} employees',
                'action': f'Build lookalike audience matching {top_profile.profile_name}',
                'expected_impact': f'{top_profile.conversion_rate * 100:.1f}% expected conversion rate',
            })

        # Recommendation 3: Deprioritize low-fit leads
        low_fit_count = len([l for l in scored_leads if l['icp_score'] < 0.3])
        if low_fit_count > 10:
            recommendations.append({
                'type': 'deprioritize_low_fit',
                'description': f'Reduce focus on {low_fit_count} low-fit leads (ICP score < 0.3)',
                'action': 'Move to nurture campaign or archive',
                'expected_impact': 'Improved resource allocation and ROI',
            })

        return recommendations

    async def _store_icp_profiles(
        self,
        profiles: List[ICPProfile],
        context: MissionContext
    ) -> int:
        """Store ICP profiles in database"""
        stored_count = 0

        for profile in profiles:
            try:
                # Store profile data
                profile_data = {
                    'user_id': context.user_id,
                    'profile_name': profile.profile_name,
                    'industries': profile.industries,
                    'job_titles': profile.job_titles,
                    'company_size_min': profile.company_size_range[0],
                    'company_size_max': profile.company_size_range[1],
                    'common_pain_points': profile.common_pain_points,
                    'avg_deal_value': profile.avg_deal_value,
                    'conversion_rate': profile.conversion_rate,
                    'lead_count': profile.lead_count,
                    'created_at': datetime.utcnow().isoformat(),
                }

                # Log to agent_logs for now (would have dedicated table in production)
                self.db.table('agent_logs').insert({
                    'mission_id': context.mission_id,
                    'agent_name': self.agent_name,
                    'event_type': 'custom',
                    'data': {
                        'event': 'icp_profile_extracted',
                        **profile_data
                    }
                }).execute()

                stored_count += 1

            except Exception as e:
                logger.error(f"Failed to store ICP profile {profile.profile_name}: {e}")

        return stored_count

    async def _update_lead_icp_scores(self, scored_leads: List[Dict[str, Any]]) -> None:
        """Update ICP scores in lead records"""
        for scored_lead in scored_leads:
            try:
                self.db.table('leads').update({
                    'icp_score': scored_lead['icp_score'],
                    'icp_profile': scored_lead['best_fit_profile'],
                    'updated_at': datetime.utcnow().isoformat(),
                }).eq('id', scored_lead['lead_id']).execute()

            except Exception as e:
                logger.error(f"Failed to update ICP score for lead {scored_lead['lead_id']}: {e}")
