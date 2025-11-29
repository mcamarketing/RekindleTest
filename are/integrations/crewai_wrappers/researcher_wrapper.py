"""
CrewAI Researcher Agent Wrapper

Wrapper for the CrewAI ResearcherAgent that provides lead intelligence and enrichment.
Translates ARE requests to CrewAI format and handles responses.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ResearcherAgentWrapper:
    """Wrapper for CrewAI ResearcherAgent"""

    def __init__(self):
        self.agent_name = "ResearcherAgent"
        self.capabilities = ["lead_research", "company_intelligence", "contact_enrichment"]

    async def run(self, task_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Execute research task"""
        logger.info(f"ResearcherAgentWrapper: Processing task {task_data.get('id', 'unknown')}")

        try:
            # Extract task parameters
            lead_id = task_data.get("lead_id")
            company_name = task_data.get("company_name")
            research_focus = task_data.get("focus", "general")

            if not lead_id and not company_name:
                raise ValueError("Either lead_id or company_name must be provided")

            # Prepare research request
            research_request = self._prepare_research_request(task_data)

            # Call CrewAI ResearcherAgent (simulated for now)
            research_results = await self._call_crewai_researcher(research_request)

            # Format results for ARE
            formatted_results = self._format_research_results(research_results, task_data)

            logger.info(f"ResearcherAgentWrapper: Completed research for {lead_id or company_name}")
            return formatted_results

        except Exception as e:
            logger.error(f"ResearcherAgentWrapper failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "capabilities": self.capabilities,
                "timestamp": datetime.now().isoformat()
            }

    def _prepare_research_request(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare research request for CrewAI agent"""
        return {
            "lead_id": task_data.get("lead_id"),
            "company_name": task_data.get("company_name"),
            "research_scope": task_data.get("scope", "comprehensive"),
            "data_sources": task_data.get("data_sources", ["linkedin", "company_website", "news"]),
            "focus_areas": task_data.get("focus_areas", ["company_info", "key_contacts", "recent_news"]),
            "max_results": task_data.get("max_results", 10),
            "freshness_days": task_data.get("freshness_days", 30)
        }

    async def _call_crewai_researcher(self, research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Call the actual CrewAI ResearcherAgent"""
        # This would make an HTTP call to the CrewAI service
        # For now, simulate the response

        await asyncio.sleep(2)  # Simulate API call delay

        # Mock response based on request
        company_name = research_request.get("company_name", "Unknown Company")

        return {
            "company_info": {
                "name": company_name,
                "industry": "Technology",
                "size": "51-200 employees",
                "location": "San Francisco, CA",
                "founded": 2018,
                "funding": "$25M Series A"
            },
            "key_contacts": [
                {
                    "name": "Jane Smith",
                    "title": "VP Sales",
                    "linkedin_url": f"https://linkedin.com/in/jane-smith-{company_name.lower().replace(' ', '-')}",
                    "email": f"jane.smith@{company_name.lower().replace(' ', '')}.com"
                },
                {
                    "name": "John Doe",
                    "title": "CEO",
                    "linkedin_url": f"https://linkedin.com/in/john-doe-{company_name.lower().replace(' ', '-')}",
                    "email": f"john.doe@{company_name.lower().replace(' ', '')}.com"
                }
            ],
            "recent_news": [
                {
                    "title": f"{company_name} Raises $15M in Series A Funding",
                    "date": "2024-01-15",
                    "source": "TechCrunch",
                    "summary": f"Leading B2B SaaS company {company_name} announced $15M in Series A funding."
                }
            ],
            "signals": {
                "hiring": True,
                "funding": True,
                "product_launch": False,
                "expansion": True
            },
            "confidence_score": 0.85,
            "data_freshness_days": 7
        }

    def _format_research_results(self, raw_results: Dict[str, Any], task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format CrewAI results for ARE consumption"""
        return {
            "success": True,
            "agent": self.agent_name,
            "task_id": task_data.get("id"),
            "research_data": {
                "company_intelligence": raw_results.get("company_info", {}),
                "key_contacts": raw_results.get("key_contacts", []),
                "recent_developments": raw_results.get("recent_news", []),
                "trigger_signals": raw_results.get("signals", {}),
                "enrichment_metadata": {
                    "confidence_score": raw_results.get("confidence_score", 0.5),
                    "data_freshness_days": raw_results.get("data_freshness_days", 30),
                    "sources_used": ["linkedin", "company_website", "news_aggregator"],
                    "last_updated": datetime.now().isoformat()
                }
            },
            "insights": self._generate_research_insights(raw_results),
            "next_actions": self._suggest_next_actions(raw_results, task_data),
            "timestamp": datetime.now().isoformat()
        }

    def _generate_research_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from research data"""
        insights = []

        signals = results.get("signals", {})

        if signals.get("funding"):
            insights.append("Company recently raised funding - high buying intent signal")

        if signals.get("hiring"):
            insights.append("Active hiring indicates growth phase - good timing for outreach")

        company_info = results.get("company_info", {})
        industry = company_info.get("industry", "").lower()

        if "saas" in industry or "software" in industry:
            insights.append("SaaS company - focus on product-led growth messaging")

        contacts = results.get("key_contacts", [])
        if len(contacts) > 0:
            titles = [contact.get("title", "") for contact in contacts]
            if any("vp" in title.lower() or "director" in title.lower() for title in titles):
                insights.append("Decision-makers identified - personalize to executive level")

        return insights

    def _suggest_next_actions(self, results: Dict[str, Any], task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest next actions based on research findings"""
        suggestions = []

        signals = results.get("signals", {})

        if signals.get("funding"):
            suggestions.append({
                "action": "prioritize_outreach",
                "reason": "Recent funding indicates high engagement potential",
                "urgency": "high"
            })

        contacts = results.get("key_contacts", [])
        if len(contacts) > 0:
            suggestions.append({
                "action": "personalize_content",
                "reason": f"Found {len(contacts)} key contacts for personalization",
                "urgency": "medium"
            })

        if results.get("confidence_score", 0) < 0.7:
            suggestions.append({
                "action": "gather_more_data",
                "reason": "Research confidence is low - need additional data sources",
                "urgency": "medium"
            })

        return suggestions

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "agent_name": self.agent_name,
            "capabilities": self.capabilities,
            "supported_inputs": ["lead_id", "company_name", "focus_areas", "data_sources"],
            "output_format": "research_data",
            "typical_latency_seconds": 30,
            "confidence_range": [0.6, 0.95]
        }