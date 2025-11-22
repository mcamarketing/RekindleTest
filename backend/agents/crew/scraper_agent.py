"""
ScraperAgent - Data Enrichment & Research Specialist

Enriches lead data by fetching company information, contact details, social profiles,
and relevant business intelligence from external APIs and public sources.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
import hashlib
import json

from .base_agent import BaseAgent, MissionContext, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class EnrichmentResult:
    """Result of data enrichment for a single lead"""
    lead_id: str
    source: str  # clearbit, linkedin, apollo, manual
    data_enriched: Dict[str, Any]
    confidence_score: float
    fields_updated: List[str]
    cached: bool


class ScraperAgent(BaseAgent):
    """
    Specialized agent for data enrichment and research.

    Capabilities:
    - Company data enrichment (size, industry, revenue, tech stack)
    - Contact information validation and enrichment
    - Social profile discovery (LinkedIn, Twitter, etc.)
    - Business intelligence gathering
    - Data validation and deduplication
    - Intelligent caching to minimize API costs
    """

    def __init__(self, supabase, redis_client=None, openai_api_key=None):
        super().__init__(
            agent_name="ScraperAgent",
            supabase=supabase,
            redis_client=redis_client,
            openai_api_key=openai_api_key
        )

        # Enrichment configuration
        self.ENRICHMENT_SOURCES = {
            'clearbit': {'enabled': True, 'priority': 1, 'cost_per_call': 0.01},
            'apollo': {'enabled': True, 'priority': 2, 'cost_per_call': 0.005},
            'linkedin': {'enabled': True, 'priority': 3, 'cost_per_call': 0.02},
            'hunter': {'enabled': True, 'priority': 4, 'cost_per_call': 0.003},
        }

        self.CACHE_TTL = 30 * 24 * 60 * 60  # 30 days for enriched data

    async def handle_mission(self, context: MissionContext) -> AgentResult:
        """Execute data enrichment mission"""
        logger.info(f"ScraperAgent starting mission {context.mission_id}")

        # Get enrichment parameters
        lead_ids = context.custom_params.get('lead_ids', [])
        enrichment_fields = context.custom_params.get('fields', ['all'])
        force_refresh = context.custom_params.get('force_refresh', False)
        max_cost = context.custom_params.get('max_cost', 10.0)  # USD

        # Step 1: Fetch leads to enrich
        leads = await self._fetch_leads(lead_ids, context.user_id)
        logger.info(f"Enriching {len(leads)} leads")

        # Step 2: Prioritize leads by enrichment value
        prioritized_leads = self._prioritize_leads(leads, enrichment_fields)

        # Step 3: Enrich each lead with cost tracking
        enrichment_results = []
        total_cost = 0.0

        for lead in prioritized_leads:
            if total_cost >= max_cost:
                logger.warning(f"Reached max cost budget ${max_cost}, stopping enrichment")
                break

            result = await self._enrich_lead(
                lead=lead,
                enrichment_fields=enrichment_fields,
                force_refresh=force_refresh,
                remaining_budget=max_cost - total_cost
            )

            enrichment_results.append(result)
            total_cost += self._calculate_enrichment_cost(result)

        # Step 4: Update leads in database
        updated_count = await self._update_enriched_leads(enrichment_results)

        # Step 5: Generate data quality report
        quality_report = await self._generate_quality_report(enrichment_results)

        # Build result
        result_data = {
            'leads_enriched': len(enrichment_results),
            'leads_updated': updated_count,
            'total_cost': round(total_cost, 2),
            'cache_hit_rate': self._calculate_cache_hit_rate(enrichment_results),
            'fields_enriched': self._count_fields_enriched(enrichment_results),
            'sources_used': self._count_sources_used(enrichment_results),
            'quality_report': quality_report,
        }

        success = updated_count > 0

        return AgentResult(
            success=success,
            data=result_data,
            message=f"Enriched {len(enrichment_results)} leads, updated {updated_count} records (${total_cost:.2f} cost)"
        )

    async def _fetch_leads(self, lead_ids: List[str], user_id: str) -> List[Dict[str, Any]]:
        """Fetch leads for enrichment"""
        if lead_ids:
            # Fetch specific leads
            result = self.db.table('leads')\
                .select('*')\
                .eq('user_id', user_id)\
                .in_('id', lead_ids)\
                .execute()
        else:
            # Fetch leads needing enrichment
            result = self.db.table('leads')\
                .select('*')\
                .eq('user_id', user_id)\
                .or_('company.is.null,industry.is.null,company_size.is.null')\
                .limit(100)\
                .execute()

        return result.data if result.data else []

    def _prioritize_leads(
        self,
        leads: List[Dict[str, Any]],
        enrichment_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Prioritize leads by enrichment value"""
        def enrichment_priority(lead: Dict[str, Any]) -> float:
            score = 0.0

            # High value leads get priority
            deal_value = lead.get('estimated_deal_value', 0)
            score += min(deal_value / 10000, 1.0) * 0.3

            # Leads with more missing data get priority
            missing_critical_fields = 0
            critical_fields = ['company', 'industry', 'company_size', 'job_title']
            for field in critical_fields:
                if not lead.get(field):
                    missing_critical_fields += 1

            score += (missing_critical_fields / len(critical_fields)) * 0.5

            # Leads in active campaigns get priority
            if lead.get('status') in ['active', 'qualified']:
                score += 0.2

            return score

        return sorted(leads, key=enrichment_priority, reverse=True)

    async def _enrich_lead(
        self,
        lead: Dict[str, Any],
        enrichment_fields: List[str],
        force_refresh: bool,
        remaining_budget: float
    ) -> EnrichmentResult:
        """Enrich a single lead with external data"""
        lead_id = lead['id']

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = await self._get_cached_enrichment(lead)
            if cached_data:
                logger.info(f"Using cached enrichment for lead {lead_id}")
                return EnrichmentResult(
                    lead_id=lead_id,
                    source=cached_data['source'],
                    data_enriched=cached_data['data'],
                    confidence_score=cached_data['confidence'],
                    fields_updated=cached_data['fields_updated'],
                    cached=True
                )

        # Determine best enrichment source based on available data and budget
        enrichment_source = self._select_enrichment_source(lead, remaining_budget)

        if not enrichment_source:
            logger.warning(f"No suitable enrichment source for lead {lead_id}")
            return EnrichmentResult(
                lead_id=lead_id,
                source='none',
                data_enriched={},
                confidence_score=0.0,
                fields_updated=[],
                cached=False
            )

        # Fetch enrichment data from selected source
        enriched_data = await self._fetch_from_source(
            lead=lead,
            source=enrichment_source,
            fields=enrichment_fields
        )

        # Validate and merge enriched data
        validated_data = self._validate_enriched_data(enriched_data, lead)

        # Determine which fields were updated
        fields_updated = list(validated_data.keys())

        # Calculate confidence score
        confidence_score = self._calculate_confidence(validated_data, enrichment_source)

        # Cache the enrichment result
        await self._cache_enrichment(lead_id, {
            'source': enrichment_source,
            'data': validated_data,
            'confidence': confidence_score,
            'fields_updated': fields_updated,
            'timestamp': datetime.utcnow().isoformat(),
        })

        return EnrichmentResult(
            lead_id=lead_id,
            source=enrichment_source,
            data_enriched=validated_data,
            confidence_score=confidence_score,
            fields_updated=fields_updated,
            cached=False
        )

    def _select_enrichment_source(self, lead: Dict[str, Any], budget: float) -> Optional[str]:
        """Select best enrichment source based on available data and budget"""
        # Check what data we have to work with
        has_email = bool(lead.get('email'))
        has_company = bool(lead.get('company'))
        has_domain = bool(lead.get('company_domain'))

        # Sort sources by priority
        sorted_sources = sorted(
            self.ENRICHMENT_SOURCES.items(),
            key=lambda x: x[1]['priority']
        )

        for source_name, config in sorted_sources:
            if not config['enabled']:
                continue

            # Check if we can afford this source
            if config['cost_per_call'] > budget:
                continue

            # Check if we have required data for this source
            if source_name == 'clearbit':
                if has_email or has_domain:
                    return source_name
            elif source_name == 'apollo':
                if has_company or has_email:
                    return source_name
            elif source_name == 'linkedin':
                if has_company and lead.get('first_name') and lead.get('last_name'):
                    return source_name
            elif source_name == 'hunter':
                if has_domain or has_company:
                    return source_name

        return None

    async def _fetch_from_source(
        self,
        lead: Dict[str, Any],
        source: str,
        fields: List[str]
    ) -> Dict[str, Any]:
        """Fetch enrichment data from external source"""
        # In production, this would call actual APIs
        # For now, return simulated enrichment data

        logger.info(f"Fetching enrichment from {source} for lead {lead['id']}")

        # Simulate API call with deterministic fallback
        enriched_data = {}

        if source == 'clearbit':
            enriched_data = await self._fetch_clearbit_data(lead)
        elif source == 'apollo':
            enriched_data = await self._fetch_apollo_data(lead)
        elif source == 'linkedin':
            enriched_data = await self._fetch_linkedin_data(lead)
        elif source == 'hunter':
            enriched_data = await self._fetch_hunter_data(lead)

        return enriched_data

    async def _fetch_clearbit_data(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from Clearbit API (simulated)"""
        # TODO: Implement actual Clearbit API integration
        # For now, return simulated data based on available lead info

        company = lead.get('company', '')
        email = lead.get('email', '')

        if not company and not email:
            return {}

        # Simulated enrichment data
        return {
            'company_size': 150,
            'industry': 'Software',
            'company_revenue': 5000000,
            'company_description': f'{company} provides innovative software solutions',
            'tech_stack': ['React', 'Python', 'AWS'],
            'company_location': 'San Francisco, CA',
            'social_profiles': {
                'linkedin': f'https://linkedin.com/company/{company.lower().replace(" ", "-")}',
                'twitter': f'https://twitter.com/{company.lower().replace(" ", "")}',
            }
        }

    async def _fetch_apollo_data(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from Apollo API (simulated)"""
        # TODO: Implement actual Apollo API integration

        return {
            'job_title': lead.get('job_title') or 'VP of Sales',
            'job_seniority': 'VP',
            'department': 'Sales',
            'phone': '+1-555-0100',
            'direct_dial_confidence': 0.85,
        }

    async def _fetch_linkedin_data(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from LinkedIn (simulated)"""
        # TODO: Implement actual LinkedIn scraping (via official API or tools)

        return {
            'linkedin_url': f'https://linkedin.com/in/{lead.get("first_name", "").lower()}-{lead.get("last_name", "").lower()}',
            'headline': f'{lead.get("job_title", "Professional")} at {lead.get("company", "Company")}',
            'skills': ['Sales', 'Business Development', 'SaaS'],
            'education': ['MBA', 'Business Administration'],
        }

    async def _fetch_hunter_data(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from Hunter.io (simulated)"""
        # TODO: Implement actual Hunter API integration

        company_domain = lead.get('company_domain', '')
        if not company_domain and lead.get('company'):
            company_domain = f'{lead["company"].lower().replace(" ", "")}.com'

        return {
            'email_pattern': '{first}.{last}@' + company_domain,
            'email_confidence': 0.9,
            'company_domain': company_domain,
        }

    def _validate_enriched_data(
        self,
        enriched_data: Dict[str, Any],
        original_lead: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and clean enriched data"""
        validated = {}

        # Validate company_size
        if 'company_size' in enriched_data:
            company_size = enriched_data['company_size']
            if isinstance(company_size, int) and 1 <= company_size <= 1000000:
                validated['company_size'] = company_size

        # Validate industry
        if 'industry' in enriched_data:
            industry = enriched_data['industry']
            if isinstance(industry, str) and len(industry) > 0:
                validated['industry'] = industry

        # Validate phone
        if 'phone' in enriched_data:
            phone = enriched_data['phone']
            if isinstance(phone, str) and len(phone) >= 10:
                validated['phone'] = phone

        # Validate URLs
        for url_field in ['linkedin_url', 'company_domain']:
            if url_field in enriched_data:
                url = enriched_data[url_field]
                if isinstance(url, str) and (url.startswith('http') or '.' in url):
                    validated[url_field] = url

        # Validate numeric fields
        for numeric_field in ['company_revenue', 'email_confidence', 'direct_dial_confidence']:
            if numeric_field in enriched_data:
                value = enriched_data[numeric_field]
                if isinstance(value, (int, float)) and value >= 0:
                    validated[numeric_field] = value

        # Validate arrays
        for array_field in ['tech_stack', 'skills', 'education']:
            if array_field in enriched_data:
                arr = enriched_data[array_field]
                if isinstance(arr, list):
                    validated[array_field] = arr

        # Validate nested objects
        for object_field in ['social_profiles']:
            if object_field in enriched_data:
                obj = enriched_data[object_field]
                if isinstance(obj, dict):
                    validated[object_field] = obj

        # Copy over any other string fields
        for key, value in enriched_data.items():
            if key not in validated and isinstance(value, str) and len(value) > 0:
                validated[key] = value

        return validated

    def _calculate_confidence(self, data: Dict[str, Any], source: str) -> float:
        """Calculate confidence score for enriched data"""
        confidence = 0.0

        # Base confidence by source
        source_confidence = {
            'clearbit': 0.9,
            'apollo': 0.85,
            'linkedin': 0.95,
            'hunter': 0.8,
        }

        confidence = source_confidence.get(source, 0.5)

        # Adjust based on number of fields enriched
        fields_count = len(data)
        if fields_count >= 5:
            confidence += 0.05
        elif fields_count <= 2:
            confidence -= 0.1

        # Clamp to 0-1 range
        return max(0.0, min(1.0, confidence))

    async def _get_cached_enrichment(self, lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached enrichment data"""
        if not self.redis:
            return None

        cache_key = self._generate_cache_key(lead['id'])

        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Failed to get cached enrichment: {e}")

        return None

    async def _cache_enrichment(self, lead_id: str, data: Dict[str, Any]) -> None:
        """Cache enrichment data"""
        if not self.redis:
            return

        cache_key = self._generate_cache_key(lead_id)

        try:
            self.redis.setex(
                cache_key,
                self.CACHE_TTL,
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Failed to cache enrichment: {e}")

    def _generate_cache_key(self, lead_id: str) -> str:
        """Generate cache key for lead enrichment"""
        return f"scraper:enrichment:{lead_id}"

    def _calculate_enrichment_cost(self, result: EnrichmentResult) -> float:
        """Calculate cost of enrichment"""
        if result.cached:
            return 0.0

        source_config = self.ENRICHMENT_SOURCES.get(result.source, {})
        return source_config.get('cost_per_call', 0.0)

    async def _update_enriched_leads(
        self,
        enrichment_results: List[EnrichmentResult]
    ) -> int:
        """Update leads with enriched data"""
        updated_count = 0

        for result in enrichment_results:
            if not result.data_enriched:
                continue

            try:
                # Update lead in database
                update_data = {
                    **result.data_enriched,
                    'enrichment_source': result.source,
                    'enrichment_confidence': result.confidence_score,
                    'last_enriched_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                }

                self.db.table('leads').update(update_data).eq('id', result.lead_id).execute()

                updated_count += 1

            except Exception as e:
                logger.error(f"Failed to update lead {result.lead_id}: {e}")

        return updated_count

    async def _generate_quality_report(
        self,
        enrichment_results: List[EnrichmentResult]
    ) -> Dict[str, Any]:
        """Generate data quality report"""
        if not enrichment_results:
            return {}

        total_fields = sum(len(r.fields_updated) for r in enrichment_results)
        avg_confidence = sum(r.confidence_score for r in enrichment_results) / len(enrichment_results)

        return {
            'total_fields_enriched': total_fields,
            'average_confidence': round(avg_confidence, 2),
            'enrichment_completeness': round(total_fields / (len(enrichment_results) * 10), 2),  # Assume 10 possible fields
            'sources_breakdown': self._count_sources_used(enrichment_results),
        }

    def _calculate_cache_hit_rate(self, enrichment_results: List[EnrichmentResult]) -> float:
        """Calculate cache hit rate"""
        if not enrichment_results:
            return 0.0

        cached_count = sum(1 for r in enrichment_results if r.cached)
        return round(cached_count / len(enrichment_results), 2)

    def _count_fields_enriched(self, enrichment_results: List[EnrichmentResult]) -> Dict[str, int]:
        """Count fields enriched across all leads"""
        field_counts = {}

        for result in enrichment_results:
            for field in result.fields_updated:
                field_counts[field] = field_counts.get(field, 0) + 1

        return field_counts

    def _count_sources_used(self, enrichment_results: List[EnrichmentResult]) -> Dict[str, int]:
        """Count enrichment sources used"""
        source_counts = {}

        for result in enrichment_results:
            source = result.source
            source_counts[source] = source_counts.get(source, 0) + 1

        return source_counts
