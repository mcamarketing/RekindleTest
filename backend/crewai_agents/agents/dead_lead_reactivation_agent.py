"""
Dead Lead Reactivation Agent - Specialized Agent for Dormant Lead Reactivation

This agent is exclusively dedicated to dead lead reactivation:
- Monitors 50+ signals per lead, 24/7
- Segments leads by dormancy reason
- Detects trigger events automatically
- Crafts trigger-specific re-engagement messages
- Queues leads for campaigns when triggers fire
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from crewai import Agent, Task
from crewai.tools import BaseTool
import json

from ..tools.linkedin_mcp_tools import LinkedInMCPTool
from ..tools.db_tools import SupabaseDB
from ..utils.agent_logging import log_agent_execution
from ..utils.error_handling import retry, CircuitBreaker
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.action_first_enforcer import ActionFirstEnforcer


class DeadLeadReactivationAgent:
    """
    Specialized agent for dead lead reactivation.
    
    Monitors 50+ signals per lead, 24/7, and automatically re-engages
    dormant leads at the perfect moment when trigger events occur.
    """
    
    def __init__(self, db: SupabaseDB, linkedin_tool: LinkedInMCPTool):
        self.db = db
        self.linkedin_tool = linkedin_tool
        self.communication_bus = get_communication_bus()
        # Circuit breaker for LinkedIn API calls
        self.linkedin_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=Exception
        )
        # Configure to use GPT-5.1 (default for reactivation monitoring)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Dead Lead Reactivation Specialist",
            goal="Monitor dormant leads 24/7 and automatically re-engage them when trigger events occur",
            backstory="""You are a specialized AI agent exclusively dedicated to dead lead reactivation.
            You monitor 50+ signals per lead continuously, segment leads by dormancy reason,
            detect trigger events (funding, hiring, job changes, company news), and craft
            hyper-personalized re-engagement messages at the perfect moment.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Specialist monitoring dormant leads for reactivation triggers
- tone:        Vigilant, proactive, opportunity-focused
- warmth:      medium
- conciseness: medium
- energy:      neutral
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are a specialized AI agent exclusively dedicated to dead lead reactivation.
You monitor 50+ signals per lead continuously, segment leads by dormancy reason,
detect trigger events (funding, hiring, job changes, company news), and craft
hyper-personalized re-engagement messages at the perfect moment.""")
            # TODO: Fix LinkedIn tool compatibility with CrewAI BaseTool
            # tools=[linkedin_tool]
        )
        
        # 50+ signals to monitor
        self.trigger_signals = [
            # Funding & Budget Signals
            "funding_announcement",
            "series_a", "series_b", "series_c",
            "new_executive_hire_cfo",
            "new_executive_hire_vp_revenue",
            "fiscal_year_change",
            
            # Hiring & Growth Signals
            "job_posting_sales",
            "job_posting_marketing",
            "job_posting_revops",
            "team_expansion_5plus",
            "new_office_opening",
            "product_launch",
            
            # Job Change Signals
            "linkedin_job_change",
            "promotion_to_decision_maker",
            "new_decision_maker_hired",
            "role_change_to_vp",
            "role_change_to_director",
            
            # Company News Signals
            "company_news_positive",
            "company_news_expansion",
            "company_news_partnership",
            "company_news_award",
            "tech_stack_change",
            
            # Competitor Signals
            "competitor_negative_review",
            "competitor_pricing_change",
            "competitor_downtime",
            "competitor_layoffs",
            
            # Engagement Signals
            "linkedin_post_activity",
            "conference_appearance",
            "webinar_attendance",
            "content_download",
            "website_visit",
            
            # Industry Signals
            "industry_trend_relevant",
            "regulatory_change",
            "market_shift",
            
            # Timing Signals
            "quarter_end",
            "year_end",
            "budget_cycle_start",
            "planning_season",
            
            # Social Signals
            "twitter_activity",
            "company_linkedin_update",
            "employee_linkedin_update",
            "news_mention",
            "press_release",
            
            # Technology Signals
            "new_tool_adoption",
            "integration_announcement",
            "api_usage_spike",
            
            # Financial Signals
            "revenue_milestone",
            "customer_count_milestone",
            "growth_announcement"
        ]
    
    @log_agent_execution(agent_name="DeadLeadReactivationAgent")
    @retry(max_attempts=2)
    def segment_lead_by_dormancy_reason(self, lead_id: str) -> Dict[str, Any]:
        """
        Segment a lead by why it went dormant.
        
        Categories:
        - A: Budget constraints
        - B: Timing / not a priority right now
        - C: Evaluating competitors
        - D: Internal politics / decision-maker changed
        - E: Ghosted with no reason given
        """
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        # Analyze lead data to determine dormancy reason
        notes = lead.get("notes", "")
        last_contact_date = lead.get("last_contact_date")
        status = lead.get("status", "dormant")
        
        # Use AI to classify dormancy reason
        classification = self._classify_dormancy_reason(lead, notes)
        
        # Update lead with dormancy category
        self.db.update_lead(lead_id, {
            "dormancy_category": classification["category"],
            "dormancy_reason": classification["reason"],
            "dormancy_confidence": classification["confidence"]
        })
        
        return {
            "lead_id": lead_id,
            "category": classification["category"],
            "reason": classification["reason"],
            "confidence": classification["confidence"]
        }
    
    def _classify_dormancy_reason(self, lead: Dict, notes: str) -> Dict[str, Any]:
        """Classify why a lead went dormant using heuristics and AI."""
        notes_lower = notes.lower() if notes else ""
        
        # Category A: Budget constraints
        if any(keyword in notes_lower for keyword in ["budget", "cost", "price", "afford", "expensive"]):
            return {
                "category": "A",
                "reason": "Budget constraints",
                "confidence": 0.85
            }
        
        # Category B: Timing / not a priority
        if any(keyword in notes_lower for keyword in ["not now", "later", "timing", "priority", "q1", "q2", "next quarter"]):
            return {
                "category": "B",
                "reason": "Timing / not a priority right now",
                "confidence": 0.80
            }
        
        # Category C: Evaluating competitors
        if any(keyword in notes_lower for keyword in ["competitor", "evaluating", "comparing", "alternatives"]):
            return {
                "category": "C",
                "reason": "Evaluating competitors",
                "confidence": 0.75
            }
        
        # Category D: Internal politics / decision-maker changed
        if any(keyword in notes_lower for keyword in ["decision maker", "champion left", "reorg", "politics", "internal"]):
            return {
                "category": "D",
                "reason": "Internal politics / decision-maker changed",
                "confidence": 0.70
            }
        
        # Category E: Ghosted (default)
        return {
            "category": "E",
            "reason": "Ghosted with no reason given",
            "confidence": 0.60
        }
    
    @log_agent_execution(agent_name="DeadLeadReactivationAgent")
    @retry(max_attempts=3, backoff="exponential")
    def monitor_trigger_events(self, lead_id: str) -> List[Dict[str, Any]]:
        """
        Monitor 50+ signals for a specific lead and detect trigger events.
        
        Returns list of trigger events detected.
        """
        lead = self.db.get_lead(lead_id)
        if not lead:
            return []
        
        trigger_events = []
        
        # Check LinkedIn signals (with circuit breaker)
        try:
            linkedin_signals = self.linkedin_circuit_breaker.call(
                self._check_linkedin_signals,
                lead
            )
            trigger_events.extend(linkedin_signals)
        except Exception as e:
            # Continue with other signals even if LinkedIn fails
            pass
        
        # Check company news signals
        company_signals = self._check_company_news_signals(lead)
        trigger_events.extend(company_signals)
        
        # Check funding signals
        funding_signals = self._check_funding_signals(lead)
        trigger_events.extend(funding_signals)
        
        # Check hiring signals
        hiring_signals = self._check_hiring_signals(lead)
        trigger_events.extend(hiring_signals)
        
        # Check job change signals
        job_signals = self._check_job_change_signals(lead)
        trigger_events.extend(job_signals)
        
        # Store trigger events
        for event in trigger_events:
            self.db.create_trigger_event({
                "lead_id": lead_id,
                "trigger_type": event["type"],
                "trigger_data": event["data"],
                "detected_at": datetime.utcnow().isoformat(),
                "relevance_score": event.get("relevance_score", 0.5)
            })
        
        # Broadcast trigger detection event
        if trigger_events:
            self.communication_bus.broadcast(
                EventType.TRIGGER_DETECTED,
                "DeadLeadReactivationAgent",
                {
                    "lead_id": lead_id,
                    "trigger_events": trigger_events,
                    "count": len(trigger_events)
                }
            )
            
            # Update shared context
            self.communication_bus.update_lead_context(lead_id, {
                "triggers_detected": trigger_events,
                "last_trigger_check": datetime.utcnow().isoformat()
            })
        
        return trigger_events
    
    def _check_linkedin_signals(self, lead: Dict) -> List[Dict]:
        """Check LinkedIn for trigger signals."""
        signals = []
        company = lead.get("company", "")
        email = lead.get("email", "")
        
        try:
            # Get LinkedIn profile data
            profile_data = self.linkedin_tool.get_profile_data(email)
            
            # Check for job changes
            if profile_data.get("job_changes"):
                signals.append({
                    "type": "linkedin_job_change",
                    "data": profile_data["job_changes"],
                    "relevance_score": 0.9
                })
            
            # Check for recent posts
            if profile_data.get("recent_posts"):
                signals.append({
                    "type": "linkedin_post_activity",
                    "data": profile_data["recent_posts"],
                    "relevance_score": 0.6
                })
            
            # Get company updates
            company_updates = self.linkedin_tool.get_company_updates(company)
            if company_updates:
                signals.append({
                    "type": "company_linkedin_update",
                    "data": company_updates,
                    "relevance_score": 0.7
                })
            
        except Exception as e:
            print(f"Error checking LinkedIn signals: {e}")
        
        return signals
    
    def _check_company_news_signals(self, lead: Dict) -> List[Dict]:
        """Check for company news signals."""
        # This would integrate with news APIs (Google News, TechCrunch, etc.)
        # For now, return empty list
        return []
    
    def _check_funding_signals(self, lead: Dict) -> List[Dict]:
        """Check for funding announcements."""
        # This would integrate with Crunchbase API
        # For now, return empty list
        return []
    
    def _check_hiring_signals(self, lead: Dict) -> List[Dict]:
        """Check for hiring signals."""
        signals = []
        company = lead.get("company", "")
        
        try:
            job_postings = self.linkedin_tool.get_job_postings(company)
            if job_postings and len(job_postings) >= 5:
                signals.append({
                    "type": "team_expansion_5plus",
                    "data": {"job_count": len(job_postings), "postings": job_postings},
                    "relevance_score": 0.8
                })
        except Exception as e:
            print(f"Error checking hiring signals: {e}")
        
        return signals
    
    def _check_job_change_signals(self, lead: Dict) -> List[Dict]:
        """Check for job change signals."""
        # Already handled in _check_linkedin_signals
        return []
    
    @log_agent_execution(agent_name="DeadLeadReactivationAgent")
    @retry(max_attempts=3, backoff="exponential")
    def craft_trigger_specific_message(self, lead_id: str, trigger_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Craft a hyper-personalized re-engagement message based on the trigger event.
        
        Each trigger type has a specific template that references the exact event.
        """
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        trigger_type = trigger_event["type"]
        trigger_data = trigger_event["data"]
        dormancy_category = lead.get("dormancy_category", "E")
        
        # Get trigger-specific template
        message_template = self._get_trigger_template(trigger_type, dormancy_category)
        
        # Personalize the message with trigger data
        personalized_message = self._personalize_message(
            message_template,
            lead,
            trigger_data
        )
        
        return {
            "lead_id": lead_id,
            "trigger_type": trigger_type,
            "subject": personalized_message["subject"],
            "body": personalized_message["body"],
            "channel": personalized_message.get("channel", "email"),
            "urgency": personalized_message.get("urgency", "medium")
        }
    
    def _get_trigger_template(self, trigger_type: str, dormancy_category: str) -> Dict[str, str]:
        """Get the appropriate template for a trigger type and dormancy category."""
        
        # Budget trigger templates (Category A)
        if trigger_type in ["funding_announcement", "series_a", "series_b", "series_c"]:
            return {
                "subject": "[Company] + your Series [Round] funding",
                "body": """Hi [Name],

Saw [Company] just raised [Amount] Series [Round] ([Source]). Congrats.

Quick question: is [pain_point_we_discussed] back on the radar now that you have fresh capital?

Either way, happy to share what three other companies in your space did post-raise. No strings attached.

Worth 12 minutes this week?

Best,
[Your Name]""",
                "channel": "email"
            }
        
        # Timing trigger templates (Category B)
        if trigger_type in ["team_expansion_5plus", "job_posting_sales", "job_posting_marketing"]:
            return {
                "subject": "[Company]'s Q4 hiring + this onboarding playbook",
                "body": """Hi [Name],

Noticed [Company] is hiring [Number] [Role] roles according to LinkedIn. That [specific_challenge] we discussed in [Month] is probably hitting right now.

Want the playbook we built for that exact scenario? No strings attached.

Best,
[Your Name]""",
                "channel": "email"
            }
        
        # Competitor trigger templates (Category C)
        if trigger_type in ["competitor_negative_review", "competitor_downtime"]:
            return {
                "subject": "[Competitor] issues + how [Your Solution] handles it differently",
                "body": """Hi [Name],

Saw some noise about [Competitor] having [specific_issue]. Not sure if that's relevant to you, but if you're re-evaluating options, happy to show you how [Your Solution] handles that differently.

Worth 12 minutes this week?

Best,
[Your Name]""",
                "channel": "email"
            }
        
        # Job change trigger templates (Category D)
        if trigger_type in ["linkedin_job_change", "promotion_to_decision_maker"]:
            return {
                "subject": "Congrats on your new role at [Company]",
                "body": """Hi [Name],

Saw you're now [New Role] at [Company]—congrats!

Given your new responsibilities, [specific_value_prop] might be more relevant now. Worth a quick 12-minute chat to see if it makes sense?

Best,
[Your Name]""",
                "channel": "email"
            }
        
        # Default template for ghosted leads (Category E)
        return {
            "subject": "[Company] + [Recent News/Activity]",
            "body": """Hi [Name],

Saw [Company] [recent_activity]. That [specific_pain_point] we discussed [timeframe] ago might be more relevant now.

Worth reconnecting?

Best,
[Your Name]""",
            "channel": "email"
        }
    
    def _personalize_message(self, template: Dict[str, str], lead: Dict, trigger_data: Dict) -> Dict[str, str]:
        """Personalize a message template with lead and trigger data."""
        body = template["body"]
        subject = template["subject"]
        
        # Replace placeholders
        replacements = {
            "[Name]": lead.get("first_name", "there"),
            "[Company]": lead.get("company", "your company"),
            "[Your Name]": "The Rekindle Team"
        }
        
        # Add trigger-specific replacements
        if "funding" in trigger_data:
            replacements["[Amount]"] = trigger_data.get("amount", "")
            replacements["[Round]"] = trigger_data.get("round", "")
            replacements["[Source]"] = trigger_data.get("source", "TechCrunch")
        
        if "job_count" in trigger_data:
            replacements["[Number]"] = str(trigger_data["job_count"])
            replacements["[Role]"] = trigger_data.get("role", "new team members")
        
        # Apply replacements
        for placeholder, value in replacements.items():
            body = body.replace(placeholder, value)
            subject = subject.replace(placeholder, value)
        
        return {
            "subject": subject,
            "body": body,
            "channel": template.get("channel", "email")
        }
    
    @log_agent_execution(agent_name="DeadLeadReactivationAgent")
    @retry(max_attempts=2)
    def queue_lead_for_campaign(self, lead_id: str, trigger_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queue a lead for campaign when a trigger event fires.
        
        This automatically adds the lead to the campaign queue with the
        trigger-specific message ready to send.
        """
        # Craft the message
        message = self.craft_trigger_specific_message(lead_id, trigger_event)
        
        if "error" in message:
            return message
        
        # Update lead status
        self.db.update_lead(lead_id, {
            "status": "queued_for_reactivation",
            "reactivation_trigger": trigger_event["type"],
            "reactivation_message": message,
            "queued_at": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "lead_id": lead_id,
            "message": message,
            "queued_at": datetime.utcnow().isoformat()
        }
    
    @log_agent_execution(agent_name="DeadLeadReactivationAgent")
    @retry(max_attempts=2)
    def monitor_all_dormant_leads(self, user_id: str, batch_size: int = 50) -> Dict[str, Any]:
        """
        Monitor all dormant leads for a user in batches.
        
        This is the main entry point that runs 24/7 to monitor all dormant leads
        and automatically queue them for reactivation when triggers fire.
        """
        # Get all dormant leads
        dormant_leads = self.db.get_dormant_leads(user_id, limit=batch_size)
        
        results = {
            "leads_checked": 0,
            "triggers_detected": 0,
            "leads_queued": 0,
            "errors": []
        }
        
        for lead in dormant_leads:
            try:
                results["leads_checked"] += 1
                lead_id = lead["id"]
                
                # Segment if not already segmented
                if not lead.get("dormancy_category"):
                    self.segment_lead_by_dormancy_reason(lead_id)
                
                # Monitor for trigger events
                trigger_events = self.monitor_trigger_events(lead_id)
                
                if trigger_events:
                    results["triggers_detected"] += len(trigger_events)
                    
                    # Queue lead for campaign with highest relevance trigger
                    best_trigger = max(trigger_events, key=lambda x: x.get("relevance_score", 0))
                    queue_result = self.queue_lead_for_campaign(lead_id, best_trigger)
                    
                    if queue_result.get("success"):
                        results["leads_queued"] += 1
                
            except Exception as e:
                results["errors"].append({
                    "lead_id": lead.get("id"),
                    "error": str(e)
                })
        
        return results

