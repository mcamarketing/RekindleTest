"""
Context Builder Utility

Builds MessageContext (MCP) from various data sources.
This is the central utility for assembling rich context for agents.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from ..mcp_schemas import (
    MessageContext,
    LeadProfile,
    LeadFirmographics,
    LeadScoring,
    EngagementHistory,
    ResearchData,
    TriggerEvent,
    PainPoint,
    RevivalHook,
    BestPractice,
    Channel,
    Intent,
    LeadTier
)
from ..tools.db_tools import SupabaseDB
from ..utils.rag_system import get_rag_system


class ContextBuilder:
    """
    Builds MessageContext from various sources.
    
    This is the central utility for assembling rich MCP context.
    """
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.rag_system = get_rag_system()
    
    def build_context_for_lead(
        self,
        lead_id: str,
        research_data: Optional[Dict] = None,
        lead_scoring: Optional[Dict] = None,
        campaign_id: Optional[str] = None,
        sequence_number: int = 1,
        total_messages: int = 5,
        channel: Channel = Channel.EMAIL,
        intent: Optional[Intent] = None,
        previous_messages: Optional[List[Dict]] = None
    ) -> MessageContext:
        """
        Build complete MessageContext for a lead.
        
        This is the main method - assembles all data into MCP context.
        """
        # Get lead from database
        lead = self.db.get_lead(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")
        
        # Build lead profile
        lead_profile = self._build_lead_profile(lead)
        
        # Build firmographics
        lead_firmographics = self._build_firmographics(lead)
        
        # Build scoring
        lead_scoring_mcp = self._build_scoring(lead, lead_scoring)
        
        # Build engagement history
        engagement_history = self._build_engagement_history(lead)
        
        # Build research data
        research_data_mcp = self._build_research_data(lead_id, research_data)
        
        # Get best practices from RAG
        best_practices = self._get_best_practices(lead_firmographics, channel)
        
        # Determine intent if not provided
        if not intent:
            intent = self._determine_intent(sequence_number, engagement_history)
        
        # Get ACV
        estimated_acv = self._get_acv(lead)
        
        # Build context
        context = MessageContext(
            lead_id=lead_id,
            lead_profile=lead_profile,
            lead_firmographics=lead_firmographics,
            lead_scoring=lead_scoring_mcp,
            engagement_history=engagement_history,
            research_data=research_data_mcp,
            best_practices=best_practices,
            campaign_id=campaign_id,
            sequence_number=sequence_number,
            total_messages_in_sequence=total_messages,
            previous_messages=previous_messages or [],
            intent=intent,
            channel=channel,
            estimated_acv=estimated_acv,
            urgency_level=self._determine_urgency(research_data_mcp),
            compliance_flags=self._get_compliance_flags(lead)
        )
        
        return context
    
    def _build_lead_profile(self, lead: Dict) -> LeadProfile:
        """Build LeadProfile from lead data."""
        return LeadProfile(
            first_name=lead.get("first_name", ""),
            last_name=lead.get("last_name", ""),
            email=lead.get("email", ""),
            phone=lead.get("phone"),
            job_title=lead.get("job_title"),
            seniority_level=self._extract_seniority(lead.get("job_title", "")),
            department=self._extract_department(lead.get("job_title", "")),
            company=lead.get("company")
        )
    
    def _build_firmographics(self, lead: Dict) -> LeadFirmographics:
        """Build LeadFirmographics from lead data."""
        return LeadFirmographics(
            company_name=lead.get("company", ""),
            industry=lead.get("industry"),
            company_size=lead.get("company_size"),
            revenue_range=lead.get("revenue_range"),
            location=lead.get("location"),
            website=lead.get("website"),
            linkedin_url=lead.get("linkedin_url")
        )
    
    def _build_scoring(self, lead: Dict, scoring_data: Optional[Dict]) -> LeadScoring:
        """Build LeadScoring from lead and scoring data."""
        if scoring_data:
            return LeadScoring(
                overall_score=scoring_data.get("score", 0),
                tier=LeadTier.HOT if scoring_data.get("score", 0) >= 80 else
                     LeadTier.WARM if scoring_data.get("score", 0) >= 60 else LeadTier.COLD,
                recency_score=scoring_data.get("breakdown", {}).get("recency", 50),
                engagement_score=scoring_data.get("breakdown", {}).get("engagement", 50),
                firmographic_score=scoring_data.get("breakdown", {}).get("firmographic", 50),
                job_signals_score=scoring_data.get("breakdown", {}).get("job_signals", 50),
                company_signals_score=scoring_data.get("breakdown", {}).get("company_signals", 50),
                breakdown=scoring_data.get("breakdown", {})
            )
        else:
            # Fallback to lead score
            score = lead.get("lead_score", 0) or 50.0
            return LeadScoring(
                overall_score=score,
                tier=LeadTier.HOT if score >= 80 else LeadTier.WARM if score >= 60 else LeadTier.COLD,
                recency_score=50.0,
                engagement_score=50.0,
                firmographic_score=50.0,
                job_signals_score=50.0,
                company_signals_score=50.0
            )
    
    def _build_engagement_history(self, lead: Dict) -> EngagementHistory:
        """Build EngagementHistory from lead data."""
        last_contact = None
        if lead.get("last_contact_date"):
            try:
                last_contact = datetime.fromisoformat(lead["last_contact_date"].replace("Z", "+00:00"))
            except:
                pass
        
        return EngagementHistory(
            total_messages_sent=lead.get("total_messages_sent", 0) or 0,
            total_replies=lead.get("total_replies", 0) or 0,
            total_opens=lead.get("total_opens", 0) or 0,
            total_clicks=lead.get("total_clicks", 0) or 0,
            last_contact_date=last_contact,
            engagement_score=self._calculate_engagement_score(lead)
        )
    
    def _build_research_data(
        self,
        lead_id: str,
        research_data: Optional[Dict]
    ) -> ResearchData:
        """Build ResearchData from research data dict."""
        if not research_data:
            return ResearchData(lead_id=lead_id)
        
        # Build trigger events
        trigger_events = []
        for hook in research_data.get("revival_hooks", []):
            trigger_events.append(TriggerEvent(
                event_type=hook.get("type", "unknown"),
                event_date=datetime.utcnow(),
                source=hook.get("source", "unknown"),
                confidence=hook.get("confidence", 0.5),
                relevance_score=hook.get("relevance", 0.5),
                details=hook
            ))
        
        # Build pain points
        pain_points = []
        for pp in research_data.get("pain_points", []):
            pain_points.append(PainPoint(
                pain_point=pp.get("description", "") or pp.get("pain_point", ""),
                severity=pp.get("severity", "medium"),
                source=pp.get("source", "unknown"),
                confidence=pp.get("confidence", 0.5),
                context=pp
            ))
        
        # Build revival hooks
        revival_hooks = []
        for hook in research_data.get("revival_hooks", []):
            revival_hooks.append(RevivalHook(
                hook_type=hook.get("type", "unknown"),
                hook_content=hook.get("content", "") or hook.get("description", ""),
                urgency_level=hook.get("urgency", "medium"),
                relevance_score=hook.get("relevance", 0.5),
                source=hook.get("source", "unknown"),
                metadata=hook
            ))
        
        return ResearchData(
            lead_id=lead_id,
            trigger_events=trigger_events,
            pain_points=pain_points,
            revival_hooks=revival_hooks,
            company_news=research_data.get("company_news", []),
            job_postings=research_data.get("job_postings", []),
            linkedin_updates=research_data.get("linkedin_updates", []),
            research_confidence=research_data.get("confidence", 0.5),
            research_sources=research_data.get("sources", [])
        )
    
    def _get_best_practices(
        self,
        firmographics: LeadFirmographics,
        channel: Channel
    ) -> List[BestPractice]:
        """Get best practices from RAG system."""
        context_filters = {}
        if firmographics.industry:
            context_filters["industry"] = firmographics.industry
        if firmographics.company_size:
            context_filters["company_size"] = firmographics.company_size
        
        practices = self.rag_system.retrieve_best_practices(
            category=channel.value,
            context_filters=context_filters,
            limit=3
        )
        
        return practices
    
    def _determine_intent(
        self,
        sequence_number: int,
        engagement_history: EngagementHistory
    ) -> Intent:
        """Determine message intent."""
        if sequence_number == 1:
            if engagement_history.total_messages_sent == 0:
                return Intent.INITIAL_OUTREACH
            else:
                return Intent.RE_ENGAGEMENT
        elif sequence_number >= 4:
            return Intent.MEETING_REQUEST
        else:
            return Intent.FOLLOW_UP
    
    def _determine_urgency(self, research_data: ResearchData) -> str:
        """Determine urgency level from research data."""
        if not research_data.trigger_events:
            return "low"
        
        high_urgency_events = [te for te in research_data.trigger_events if te.urgency_level == "high"]
        if high_urgency_events:
            return "high"
        
        return "medium"
    
    def _get_compliance_flags(self, lead: Dict) -> List[str]:
        """Get compliance flags for lead."""
        flags = []
        
        # Check opt-out status
        if lead.get("status") == "unsubscribed":
            flags.append("unsubscribed")
        
        # Check suppression list
        if lead.get("suppressed"):
            flags.append("suppressed")
        
        return flags
    
    def _get_acv(self, lead: Dict) -> float:
        """Get estimated ACV from lead."""
        custom_fields = lead.get("custom_fields")
        if isinstance(custom_fields, dict):
            return custom_fields.get("acv", 0) or 2500.0
        elif isinstance(custom_fields, str):
            try:
                import json
                parsed = json.loads(custom_fields)
                return parsed.get("acv", 0) or 2500.0
            except:
                pass
        return 2500.0  # Default
    
    def _extract_seniority(self, job_title: str) -> Optional[str]:
        """Extract seniority level from job title."""
        if not job_title:
            return None
        
        title_lower = job_title.lower()
        if any(word in title_lower for word in ["ceo", "founder", "president"]):
            return "executive"
        elif any(word in title_lower for word in ["vp", "vice president", "director"]):
            return "vp"
        elif any(word in title_lower for word in ["manager", "head of"]):
            return "manager"
        return None
    
    def _extract_department(self, job_title: str) -> Optional[str]:
        """Extract department from job title."""
        if not job_title:
            return None
        
        title_lower = job_title.lower()
        if "sales" in title_lower:
            return "sales"
        elif "marketing" in title_lower:
            return "marketing"
        elif "engineering" in title_lower or "tech" in title_lower:
            return "engineering"
        elif "product" in title_lower:
            return "product"
        return None
    
    def _calculate_engagement_score(self, lead: Dict) -> float:
        """Calculate engagement score."""
        total_sent = lead.get("total_messages_sent", 0) or 0
        total_replies = lead.get("total_replies", 0) or 0
        total_opens = lead.get("total_opens", 0) or 0
        
        if total_sent == 0:
            return 0.0
        
        # Simple engagement score
        reply_rate = total_replies / total_sent if total_sent > 0 else 0
        open_rate = total_opens / total_sent if total_sent > 0 else 0
        
        return min((reply_rate * 0.6 + open_rate * 0.4) * 100, 100.0)








