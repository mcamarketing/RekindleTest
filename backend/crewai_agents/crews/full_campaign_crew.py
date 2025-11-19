"""
Full Campaign Crew

Complete crew for running full campaigns from research to sending to tracking.
All 18 agents work together in this crew.
"""

from typing import Dict, List, Any
from crewai import Agent, Task, Crew
from ..tools.db_tools import SupabaseDB
from ..mcp_schemas import Channel
from ..tools.linkedin_mcp_tools import LinkedInMCPTool
from ..agents.researcher_agents import ResearcherAgent
from ..agents.intelligence_agents import ICPAnalyzerAgent, LeadScorerAgent, LeadSourcerAgent
from ..agents.dead_lead_reactivation_agent import DeadLeadReactivationAgent
from ..agents.master_intelligence_agent import MasterIntelligenceAgent
from ..agents.writer_agents import WriterAgent
from ..agents.content_agents import (
    SubjectLineOptimizerAgent,
    FollowUpAgent,
    ObjectionHandlerAgent,
    EngagementAnalyzerAgent
)
from ..agents.sync_agents import TrackerAgent, SynchronizerAgent
from ..agents.revenue_agents import MeetingBookerAgent, BillingAgent
from ..agents.safety_agents import ComplianceAgent, QualityControlAgent, RateLimitAgent
from ..agents.optimization_agents import (
    ABTestingAgent,
    DomainReputationAgent,
    CalendarIntelligenceAgent,
    CompetitorIntelligenceAgent,
    ContentPersonalizationAgent
)
from ..agents.infrastructure_agents import (
    EmailWarmupAgent,
    LeadNurturingAgent,
    ChurnPreventionAgent
)
from ..agents.analytics_agents import (
    MarketIntelligenceAgent,
    PerformanceAnalyticsAgent
)
from ..utils.agent_logging import log_agent_execution
from ..utils.agent_communication import get_communication_bus, EventType, AgentEvent
from ..utils.monitoring import get_monitor
from ..utils.rag_system import get_rag_system


class FullCampaignCrew:
    """
    Complete crew coordinating all 28 agents for full campaign execution.
    
    Workflow:
    1. LeadScorerAgent scores leads
    2. ResearcherAgent researches high-scoring leads
    3. WriterAgent generates message sequences
    4. SubjectLineOptimizerAgent optimizes subject lines
    5. ComplianceAgent checks compliance
    6. QualityControlAgent checks quality
    7. RateLimitAgent checks rate limits
    8. Messages sent (via email service)
    9. TrackerAgent tracks delivery and engagement
    10. EngagementAnalyzerAgent analyzes engagement
    11. FollowUpAgent generates follow-ups if needed
    12. ObjectionHandlerAgent handles objections
    13. MeetingBookerAgent books meetings
    14. BillingAgent charges fees
    15. SynchronizerAgent syncs to CRM
    """
    
    def __init__(self):
        self.db = SupabaseDB()
        self.linkedin_tool = LinkedInMCPTool()
        self.communication_bus = get_communication_bus()
        self.monitor = get_monitor()
        self.rag_system = get_rag_system()
        
        # Master Intelligence Agent - The Director
        self.master_intelligence = MasterIntelligenceAgent(self.db)
        
        # Subscribe to events
        self.communication_bus.subscribe(
            EventType.LEAD_RESEARCHED,
            self._on_lead_researched
        )
        self.communication_bus.subscribe(
            EventType.MESSAGE_GENERATED,
            self._on_message_generated
        )
        self.communication_bus.subscribe(
            EventType.TRIGGER_DETECTED,
            self._on_trigger_detected
        )
        self.communication_bus.subscribe(
            EventType.MEETING_BOOKED,
            self._on_meeting_booked
        )
        
        # Initialize all 28 agents
        # Core Intelligence (4)
        self.researcher = ResearcherAgent(self.db, self.linkedin_tool)
        self.icp_analyzer = ICPAnalyzerAgent(self.db)
        self.lead_scorer = LeadScorerAgent(self.db)
        self.lead_sourcer = LeadSourcerAgent(self.db, self.linkedin_tool)
        
        # Specialized (1)
        self.dead_reactivation = DeadLeadReactivationAgent(self.db, self.linkedin_tool)
        
        # Content (5)
        self.writer = WriterAgent(self.db)
        self.subject_optimizer = SubjectLineOptimizerAgent(self.db)
        self.followup = FollowUpAgent(self.db)
        self.objection_handler = ObjectionHandlerAgent(self.db)
        self.engagement_analyzer = EngagementAnalyzerAgent(self.db)
        
        # Safety (3)
        self.compliance = ComplianceAgent(self.db)
        self.quality = QualityControlAgent(self.db)
        self.rate_limiter = RateLimitAgent(self.db)
        
        # Sync (2)
        self.tracker = TrackerAgent(self.db)
        self.synchronizer = SynchronizerAgent(self.db)
        
        # Revenue (2)
        self.meeting_booker = MeetingBookerAgent(self.db)
        self.billing = BillingAgent(self.db)
        
        # Optimization (5) - NEW
        self.ab_testing = ABTestingAgent(self.db)
        self.domain_reputation = DomainReputationAgent(self.db)
        self.calendar_intelligence = CalendarIntelligenceAgent(self.db)
        self.competitor_intelligence = CompetitorIntelligenceAgent(self.db)
        self.content_personalization = ContentPersonalizationAgent(self.db)
        
        # Infrastructure (3) - NEW
        self.email_warmup = EmailWarmupAgent(self.db)
        self.lead_nurturing = LeadNurturingAgent(self.db)
        self.churn_prevention = ChurnPreventionAgent(self.db)
        
        # Analytics (2) - NEW
        self.market_intelligence = MarketIntelligenceAgent(self.db)
        self.performance_analytics = PerformanceAnalyticsAgent(self.db)
    
    @log_agent_execution(agent_name="FullCampaignCrew")
    def run_campaign_for_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Run complete campaign workflow for a single lead.
        
        All agents work together in sequence.
        """
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        user_id = lead.get("user_id")
        domain = lead.get("email", "").split("@")[1] if "@" in lead.get("email", "") else ""
        
        workflow_results = {}
        
        # Step 1: Score the lead
        scoring_result = self.lead_scorer.score_lead(lead_id)
        workflow_results["scoring"] = scoring_result
        
        if scoring_result.get("tier") == "cold":
            return {
                "lead_id": lead_id,
                "status": "skipped",
                "reason": "lead_too_cold",
                "score": scoring_result.get("score")
            }
        
        # Step 2: Research the lead
        research_result = self.researcher.research_lead(lead_id)
        workflow_results["research"] = research_result
        
        # Step 3: Get directives from Master Intelligence
        writer_directives = self.master_intelligence.direct_agent_behavior(
            agent_name="WriterAgent",
            context={
                "industry": lead.get("industry"),
                "company_size": lead.get("company_size"),
                "acv_range": self._get_acv_range(lead.get("acv", 0))
            }
        )
        
        # Step 4: Build MCP context
        from ..utils.context_builder import ContextBuilder
        context_builder = ContextBuilder(self.db)
        
        context = context_builder.build_context_for_lead(
            lead_id=lead_id,
            research_data=research_result,
            lead_scoring=scoring_result,
            sequence_number=1,
            total_messages=5,
            channel=Channel.EMAIL
        )
        
        # Enrich with best practices from Master Intelligence
        if writer_directives.get("best_practices"):
            from ..mcp_schemas import BestPractice
            context.best_practices.extend([
                BestPractice(**bp) for bp in writer_directives.get("best_practices", [])
            ])
        
        # Step 5: Generate message sequence using MCP
        sequence_result = self.writer.generate_sequence(context)
        workflow_results["sequence"] = sequence_result.dict() if hasattr(sequence_result, 'dict') else sequence_result
        
        if not sequence_result.messages:
            return {
                "lead_id": lead_id,
                "status": "error",
                "reason": "message_generation_failed"
            }
        
        # Step 6: Optimize subject lines (with intelligence guidance)
        subject_directives = self.master_intelligence.direct_agent_behavior(
            agent_name="SubjectLineOptimizerAgent",
            context={
                "industry": lead.get("industry"),
                "company_size": lead.get("company_size")
            }
        )
        
        # Optimize subject lines for each message
        optimized_messages = []
        for message in sequence_result.messages:
            # Convert GeneratedMessage to dict for subject optimizer (legacy compatibility)
            message_dict = message.dict() if hasattr(message, 'dict') else message
            
            # Optimize subject line
            subject_variants = self.subject_optimizer.generate_variants(lead, research_result)
            if subject_directives.get("best_practices"):
                top_practice = subject_directives["best_practices"][0]
                optimized_subject = self._adapt_subject(top_practice["content"], lead)
            else:
                optimized_subject = subject_variants.get("variants", [{}])[0].get("subject", message.subject)
            
            # Update message subject
            if hasattr(message, 'subject'):
                message.subject = optimized_subject
            optimized_messages.append(message)
        
        workflow_results["optimized_messages"] = [msg.dict() if hasattr(msg, 'dict') else msg for msg in optimized_messages]
        
        # Step 7-9: Safety checks for each message
        approved_messages = []
        for message in optimized_messages:
            # Convert to dict for safety agents (legacy compatibility)
            message_dict = message.dict() if hasattr(message, 'dict') else message
            
            # Compliance check
            compliance_result = self.compliance.check_compliance(lead_id, message_dict)
            if not compliance_result.get("compliant", True):
                continue
            
            # Quality check
            quality_result = self.quality.check_quality(lead_id, message_dict)
            if not quality_result.get("approved", True):
                continue
            
            # Rate limit check
            rate_limit_result = self.rate_limiter.check_rate_limit(user_id, domain)
            if not rate_limit_result.get("can_send", True):
                continue
            
            approved_messages.append(message)  # Keep as GeneratedMessage object
        
        if not approved_messages:
            return {
                "lead_id": lead_id,
                "status": "blocked",
                "reason": "all_messages_failed_safety_checks"
            }
        
        workflow_results["approved_messages"] = len(approved_messages)
        
        # Step 10: Queue messages for sending (via Redis/BullMQ)
        try:
            from ..utils.redis_queue import add_message_job
        except ImportError:
            # Fallback if Redis not available
            add_message_job = lambda x: print(f"Would queue message: {x.get('lead_id')}")
        
        messages_queued = 0
        for message in approved_messages:
            # Determine recipient based on channel
            recipient = lead.get("email")
            if message.channel in [Channel.SMS, Channel.WHATSAPP, Channel.VOICEMAIL]:
                recipient = lead.get("phone") or lead.get("email")
            
            # Add to Redis queue for worker to process
            success = add_message_job({
                "lead_id": message.lead_id,
                "campaign_id": context.campaign_id,
                "user_id": lead.get("user_id"),
                "channel": message.channel.value,
                "to": recipient,
                "from": None,  # Would get from user settings
                "subject": message.subject,
                "body": message.body or message.text_body,
                "html": message.html_body,
                "text": message.text_body or message.body
            })
            
            if success:
                messages_queued += 1
        
        # Update lead status
        self.db.update_lead(lead_id, {
            "status": "campaign_active",
            "messages_queued": messages_queued
        })
        
        # Step 9: Track (would happen after sending)
        # Step 10: Analyze engagement (would happen after opens/clicks)
        
        return {
            "lead_id": lead_id,
            "status": "campaign_started",
            "messages_approved": len(approved_messages),
            "messages_queued": messages_queued,
            "sequence_id": sequence_result.sequence_id if hasattr(sequence_result, 'sequence_id') else None,
            "workflow_results": workflow_results
        }
    
    @log_agent_execution(agent_name="FullCampaignCrew")
    def handle_reply(self, lead_id: str, reply_text: str) -> Dict[str, Any]:
        """
        Handle an inbound reply using multiple agents.
        
        Workflow:
        1. TrackerAgent classifies reply
        2. If meeting request → MeetingBookerAgent
        3. If objection → ObjectionHandlerAgent
        4. If question → FollowUpAgent
        5. If opt-out → ComplianceAgent (suppress)
        6. SynchronizerAgent syncs to CRM
        """
        # Step 1: Classify reply
        classification = self.tracker.classify_reply(lead_id, reply_text)
        
        intent = classification.get("intent")
        sentiment = classification.get("sentiment")
        
        result = {
            "lead_id": lead_id,
            "classification": classification
        }
        
        # Step 2: Route based on intent
        if intent == "MEETING_REQUEST":
            # Book meeting
            meeting_result = self.meeting_booker.book_meeting(lead_id, {
                "preferred_time": None,  # Would extract from reply
                "reply_text": reply_text
            })
            result["action"] = "meeting_booked"
            result["meeting"] = meeting_result
            
            # Sync to CRM
            sync_result = self.synchronizer.sync_meeting_to_crm(lead_id, meeting_result)
            result["crm_sync"] = sync_result
        
        elif intent == "OBJECTION":
            # Handle objection
            objection_result = self.objection_handler.handle_objection(lead_id, reply_text)
            result["action"] = "objection_handled"
            result["objection_response"] = objection_result
            
            if not objection_result.get("escalate_to_human"):
                # Generate follow-up with objection response
                followup_result = self.followup.generate_followup(lead_id, {
                    "sentiment": sentiment,
                    "intent": intent,
                    "text": reply_text
                })
                result["followup"] = followup_result
        
        elif intent == "QUESTION":
            # Generate follow-up answer
            followup_result = self.followup.generate_followup(lead_id, {
                "sentiment": sentiment,
                "intent": intent,
                "text": reply_text
            })
            result["action"] = "followup_generated"
            result["followup"] = followup_result
        
        elif intent == "OPT_OUT":
            # Suppress lead
            self.db.update_lead(lead_id, {"suppressed": True, "status": "opted_out"})
            result["action"] = "lead_suppressed"
        
        else:
            # General reply - sync to CRM
            sync_result = self.synchronizer.sync_reply_to_crm(lead_id, {
                "reply_text": reply_text,
                "sentiment": sentiment,
                "intent": intent
            })
            result["action"] = "reply_synced"
            result["crm_sync"] = sync_result
        
        return result
    
    @log_agent_execution(agent_name="FullCampaignCrew")
    def analyze_and_optimize(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze campaign performance and optimize using EngagementAnalyzerAgent.
        
        This crew method uses EngagementAnalyzerAgent to:
        - Analyze all leads' engagement
        - Identify hot/warm/cold segments
        - Recommend next actions
        - Optimize future campaigns
        """
        # Get all active leads
        # In production, would query leads table
        active_lead_ids = []  # Placeholder
        
        analysis_results = {
            "leads_analyzed": 0,
            "hot_leads": [],
            "warm_leads": [],
            "cold_leads": [],
            "recommendations": []
        }
        
        for lead_id in active_lead_ids:
            engagement_result = self.engagement_analyzer.analyze_engagement(lead_id)
            
            analysis_results["leads_analyzed"] += 1
            
            if engagement_result.get("segment") == "hot":
                analysis_results["hot_leads"].append({
                    "lead_id": lead_id,
                    "engagement_score": engagement_result.get("engagement_score"),
                    "next_action": engagement_result.get("next_action")
                })
            elif engagement_result.get("segment") == "warm":
                analysis_results["warm_leads"].append({
                    "lead_id": lead_id,
                    "engagement_score": engagement_result.get("engagement_score"),
                    "next_action": engagement_result.get("next_action")
                })
            else:
                analysis_results["cold_leads"].append({
                    "lead_id": lead_id,
                    "engagement_score": engagement_result.get("engagement_score"),
                    "next_action": engagement_result.get("next_action")
                })
        
        return analysis_results
    
    def _on_lead_researched(self, event: AgentEvent):
        """Handle lead researched event - can trigger next step."""
        lead_id = event.data.get("lead_id")
        # Could automatically trigger message generation
        pass
    
    def _on_message_generated(self, event: AgentEvent):
        """Handle message generated event - can trigger safety checks."""
        lead_id = event.data.get("lead_id")
        # Could automatically trigger compliance/quality checks
        pass
    
    def _on_trigger_detected(self, event: AgentEvent):
        """Handle trigger detected event - can trigger reactivation."""
        lead_id = event.data.get("lead_id")
        # Could automatically trigger reactivation workflow
        pass
    
    def _on_meeting_booked(self, event: AgentEvent):
        """Handle meeting booked - learn from success."""
        lead_id = event.data.get("lead_id")
        lead = self.db.get_lead(lead_id)
        
        # Get message that led to meeting
        # In production, would query messages table
        
        # Learn from success
        if lead:
            self.master_intelligence.learn_from_outcome(
                category="email",
                content="",  # Would get actual message content
                performance_metrics={
                    "reply_rate": 1.0,  # They replied
                    "meeting_rate": 1.0  # Meeting booked
                },
                context={
                    "industry": lead.get("industry"),
                    "company_size": lead.get("company_size"),
                    "acv_range": self._get_acv_range(lead.get("acv", 0))
                },
                success=True
            )
    
    def _get_acv_range(self, acv: float) -> str:
        """Get ACV range category."""
        if acv < 5000:
            return "low"
        elif acv < 25000:
            return "medium"
        else:
            return "high"
    
    def _adapt_subject(self, best_practice_subject: str, lead: Dict) -> str:
        """Adapt a best practice subject to current lead."""
        # Replace placeholders with lead-specific data
        adapted = best_practice_subject.replace(
            "[COMPANY]", lead.get("company", "")
        )
        return adapted

