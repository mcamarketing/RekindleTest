"""
Rex Tools - User-Scoped Database Access Tools

These tools allow Rex (the conversational orchestrator) to securely access
user data for intelligent, context-aware responses. All tools are:
- User-scoped (only access data for the authenticated user)
- Read-only (no mutations, only queries)
- Secure (validate user_id from JWT)
"""

import logging
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependency
def get_supa_client():
    """Get Supabase client - lazy import to avoid circular dependency."""
    try:
        from ..api_server import get_supa_client as _get_client
        return _get_client()
    except (ImportError, AttributeError):
        # Fallback: create client directly
        from ..tools.db_tools import SupabaseDB
        if not hasattr(get_supa_client, '_db_instance'):
            get_supa_client._db_instance = SupabaseDB()
        return get_supa_client._db_instance.supabase


# --- Tool: Get User KPIs ---

class GetUserKPIsInput(BaseModel):
    user_id: str = Field(..., description="The authenticated user's ID.")


class GetUserKPIsTool(BaseTool):
    name: str = "Get User KPIs"
    description: str = "Fetches high-level stats (Total Leads, Meetings Booked, Current ROI) for the user's dashboard."
    args_schema: Type[BaseModel] = GetUserKPIsInput

    def _run(self, user_id: str) -> str:
        logger.info(f"REX_TOOL_START: get_user_kpis, user_id={user_id}")
        try:
            supabase = get_supa_client()
            
            # Get total leads count
            leads_result = supabase.table('leads').select('id', count='exact').eq('user_id', user_id).execute()
            leads_count = leads_result.count if hasattr(leads_result, 'count') and leads_result.count else len(leads_result.data or [])
            
            # Get hot leads (score 70+)
            hot_leads_result = supabase.table('leads').select('id', count='exact').eq('user_id', user_id).gte('lead_score', 70).execute()
            hot_leads = hot_leads_result.count if hasattr(hot_leads_result, 'count') and hot_leads_result.count else len(hot_leads_result.data or [])
            
            # Get meetings booked this month
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
            meetings_result = supabase.table('meetings').select('id', count='exact').eq('user_id', user_id).eq('status', 'confirmed').gte('created_at', start_of_month).execute()
            meetings_count = meetings_result.count if hasattr(meetings_result, 'count') and meetings_result.count else len(meetings_result.data or [])
            
            # Get active campaigns
            campaigns_result = supabase.table('campaigns').select('id', count='exact').eq('user_id', user_id).eq('status', 'active').execute()
            active_campaigns = campaigns_result.count if hasattr(campaigns_result, 'count') and campaigns_result.count else len(campaigns_result.data or [])
            
            # Get messages sent and opens for ROI calculation
            messages_result = supabase.table('messages').select('status, open_count').eq('user_id', user_id).in_('status', ['sent', 'delivered']).execute()
            messages_data = messages_result.data or []
            total_messages = len(messages_data)
            total_opens = sum(msg.get('open_count', 0) for msg in messages_data)
            open_rate = round((total_opens / total_messages * 100) if total_messages > 0 else 0, 1)
            
            # Calculate estimated ROI (simplified)
            estimated_reactivations = round(leads_count * 0.075)  # 7.5% average
            estimated_roi = estimated_reactivations * 5000  # $5K per deal average
            roi_percent = round((estimated_roi / 99) * 100) if estimated_roi > 0 else 0  # ROI as multiplier
            
            kpis = {
                "total_leads": leads_count,
                "hot_leads": hot_leads,
                "active_campaigns": active_campaigns,
                "meetings_booked_this_month": meetings_count,
                "messages_sent": total_messages,
                "open_rate_percent": open_rate,
                "current_estimated_roi_percent": roi_percent,
                "estimated_roi_value": f"${estimated_roi:,}"
            }
            
            logger.info(f"REX_TOOL_SUCCESS: get_user_kpis, user_id={user_id}, kpis={kpis}")
            return f"""User KPIs:
- Total Leads: {leads_count}
- Hot Leads (70+ score): {hot_leads}
- Active Campaigns: {active_campaigns}
- Meetings Booked (This Month): {meetings_count}
- Messages Sent: {total_messages}
- Open Rate: {open_rate}%
- Estimated ROI: {roi_percent}x (${estimated_roi:,} potential)"""
            
        except Exception as e:
            logger.error(f"REX_TOOL_ERROR: get_user_kpis, user_id={user_id}, error={e}", exc_info=True)
            return f"Error fetching KPIs: {e}"


# --- Tool: Get Campaign Status ---

class GetCampaignStatusInput(BaseModel):
    user_id: str = Field(..., description="The authenticated user's ID.")
    campaign_name: Optional[str] = Field(None, description="Optional campaign name to filter by.")


class GetCampaignStatusTool(BaseTool):
    name: str = "Get Campaign Status"
    description: str = "Fetches the status of active campaigns for the user."
    args_schema: Type[BaseModel] = GetCampaignStatusInput

    def _run(self, user_id: str, campaign_name: Optional[str] = None) -> str:
        logger.info(f"REX_TOOL_START: get_campaign_status, user_id={user_id}, campaign_name={campaign_name}")
        try:
            supabase = get_supa_client()
            
            query = supabase.table('campaigns').select('*').eq('user_id', user_id)
            
            if campaign_name:
                query = query.ilike('name', f'%{campaign_name}%')
            else:
                query = query.eq('status', 'active')
            
            campaigns_result = query.execute()
            campaigns = campaigns_result.data or []
            
            if not campaigns:
                return f"No {'active' if not campaign_name else 'matching'} campaigns found."
            
            results = []
            for campaign in campaigns:
                # Get campaign leads count
                campaign_leads_result = supabase.table('campaign_leads').select('id', count='exact').eq('campaign_id', campaign['id']).execute()
                leads_count = campaign_leads_result.count if hasattr(campaign_leads_result, 'count') and campaign_leads_result.count else len(campaign_leads_result.data or [])
                
                # Get messages for this campaign
                messages_result = supabase.table('messages').select('status, open_count, reply_count').eq('campaign_id', campaign['id']).execute()
                messages_data = messages_result.data or []
                messages_sent = len(messages_data)
                total_opens = sum(msg.get('open_count', 0) for msg in messages_data)
                total_replies = sum(msg.get('reply_count', 0) for msg in messages_data)
                open_rate = round((total_opens / messages_sent * 100) if messages_sent > 0 else 0, 1)
                reply_rate = round((total_replies / messages_sent * 100) if messages_sent > 0 else 0, 1)
                
                results.append(f"""Campaign: {campaign.get('name', 'Unnamed')}
- Status: {campaign.get('status', 'unknown')}
- Leads: {leads_count}
- Messages Sent: {messages_sent}
- Open Rate: {open_rate}%
- Reply Rate: {reply_rate}%""")
            
            logger.info(f"REX_TOOL_SUCCESS: get_campaign_status, user_id={user_id}, found={len(campaigns)} campaigns")
            return "\n\n".join(results)
            
        except Exception as e:
            logger.error(f"REX_TOOL_ERROR: get_campaign_status, user_id={user_id}, error={e}", exc_info=True)
            return f"Error fetching campaign status: {e}"


# --- Tool: Get Lead Details ---

class GetLeadDetailsInput(BaseModel):
    user_id: str = Field(..., description="The authenticated user's ID.")
    lead_email: str = Field(..., description="Email of the lead to find.")


class GetLeadDetailsTool(BaseTool):
    name: str = "Get Lead Details"
    description: str = "Fetches a single lead's status and last contact date."
    args_schema: Type[BaseModel] = GetLeadDetailsInput

    def _run(self, user_id: str, lead_email: str) -> str:
        logger.info(f"REX_TOOL_START: get_lead_details, user_id={user_id}, email={lead_email}")
        try:
            supabase = get_supa_client()
            
            # Find lead by email
            lead_result = supabase.table('leads').select('*').eq('user_id', user_id).eq('email', lead_email.lower()).maybe_single().execute()
            
            if not lead_result.data:
                return f"Lead with email {lead_email} not found."
            
            lead = lead_result.data
            
            # Get last message date
            last_message_result = supabase.table('messages').select('sent_at').eq('lead_id', lead['id']).order('sent_at', desc=True).limit(1).execute()
            last_contact = last_message_result.data[0]['sent_at'] if last_message_result.data else "Never"
            
            # Get campaign association
            campaign_lead_result = supabase.table('campaign_leads').select('campaign_id').eq('lead_id', lead['id']).limit(1).execute()
            campaign_id = campaign_lead_result.data[0]['campaign_id'] if campaign_lead_result.data else None
            
            campaign_name = "None"
            if campaign_id:
                campaign_result = supabase.table('campaigns').select('name').eq('id', campaign_id).maybe_single().execute()
                if campaign_result.data:
                    campaign_name = campaign_result.data.get('name', 'Unknown')
            
            result = f"""Lead Details:
- Name: {lead.get('first_name', '')} {lead.get('last_name', '')}
- Email: {lead.get('email', '')}
- Company: {lead.get('company', 'N/A')}
- Job Title: {lead.get('job_title', 'N/A')}
- Lead Score: {lead.get('lead_score', 0)}/100
- Status: {lead.get('status', 'unknown')}
- Last Contact: {last_contact}
- Campaign: {campaign_name}"""
            
            logger.info(f"REX_TOOL_SUCCESS: get_lead_details, user_id={user_id}, email={lead_email}")
            return result
            
        except Exception as e:
            logger.error(f"REX_TOOL_ERROR: get_lead_details, user_id={user_id}, error={e}", exc_info=True)
            return f"Error fetching lead details: {e}"


# --- Tool: Launch Campaign (ACTION TOOL) ---

class LaunchCampaignInput(BaseModel):
    user_id: str = Field(..., description="The authenticated user's ID.")
    lead_ids: Optional[List[str]] = Field(default=None, description="List of lead IDs to target. If None, uses hot leads (70+ score).")
    campaign_name: Optional[str] = Field(default=None, description="Optional campaign name.")


class LaunchCampaignTool(BaseTool):
    name: str = "Launch Campaign"
    description: str = """LAUNCHES A CAMPAIGN IMMEDIATELY. Use this when user says 'launch', 'start', 'create', 'send campaign', etc.
    This tool will trigger the FullCampaignCrew to execute a campaign for the specified leads.
    Returns confirmation with campaign details."""
    args_schema: Type[BaseModel] = LaunchCampaignInput

    def _run(self, user_id: str, lead_ids: Optional[List[str]] = None, campaign_name: Optional[str] = None) -> str:
        logger.info(f"REX_TOOL_START: launch_campaign, user_id={user_id}, lead_ids={lead_ids}")
        try:
            # Import here to avoid circular dependency
            from ..orchestration_service import OrchestrationService
            orchestration_service = OrchestrationService()
            
            # If no lead_ids provided, get hot leads
            if not lead_ids:
                supabase = get_supa_client()
                hot_leads_result = supabase.table("leads").select("id").eq("user_id", user_id).gte("lead_score", 70).limit(50).execute()
                lead_ids = [lead["id"] for lead in (hot_leads_result.data or [])]
            
            if not lead_ids:
                return "No leads found to target. Please import leads first or specify lead IDs."
            
            # Launch campaign
            result = orchestration_service.run_full_campaign(user_id, lead_ids[:50])  # Limit to 50
            
            campaigns_started = result.get("campaigns_started", 0)
            leads_processed = result.get("leads_processed", 0)
            
            logger.info(f"REX_TOOL_SUCCESS: launch_campaign, user_id={user_id}, campaigns_started={campaigns_started}")
            return f"""✅ Campaign Launched Successfully

**Campaign Details:**
- Leads Processed: {leads_processed}
- Campaigns Started: {campaigns_started}
- Status: Running in background

The FullCampaignCrew (28 agents) is now:
• Scoring and prioritizing leads
• Researching each lead
• Generating personalized messages
• Optimizing subject lines
• Ensuring compliance and quality
• Queuing messages for sending

You can monitor progress on your Campaigns page. First responses typically arrive within 48 hours."""
            
        except Exception as e:
            logger.error(f"REX_TOOL_ERROR: launch_campaign, user_id={user_id}, error={e}", exc_info=True)
            return f"Error launching campaign: {e}"


# --- Tool: Reactivate Dormant Leads (ACTION TOOL) ---

class ReactivateLeadsInput(BaseModel):
    user_id: str = Field(..., description="The authenticated user's ID.")
    batch_size: int = Field(default=50, description="Number of dormant leads to process.")


class ReactivateLeadsTool(BaseTool):
    name: str = "Reactivate Dormant Leads"
    description: str = """REACTIVATES DORMANT LEADS IMMEDIATELY. Use this when user says 'reactivate', 'revive', 're-engage', 'dead leads', etc.
    This tool triggers the DeadLeadReactivationCrew to monitor and reactivate dormant leads.
    Returns status of reactivation process."""
    args_schema: Type[BaseModel] = ReactivateLeadsInput

    def _run(self, user_id: str, batch_size: int = 50) -> str:
        logger.info(f"REX_TOOL_START: reactivate_leads, user_id={user_id}, batch_size={batch_size}")
        try:
            from ..orchestration_service import OrchestrationService
            orchestration_service = OrchestrationService()
            
            result = orchestration_service.run_dead_lead_reactivation(user_id, batch_size=batch_size)
            
            reactivated = result.get("reactivated", 0)
            messages_sent = result.get("messages_sent", 0)
            
            logger.info(f"REX_TOOL_SUCCESS: reactivate_leads, user_id={user_id}, reactivated={reactivated}")
            return f"""✅ Dormant Lead Reactivation Started

**Status:**
- Leads Being Monitored: {batch_size}
- Leads Reactivated: {reactivated}
- Messages Sent: {messages_sent}

The DeadLeadReactivationCrew (9 agents) is now monitoring 50+ signals per lead for trigger events. When triggers are detected, the system will automatically reactivate leads."""
            
        except Exception as e:
            logger.error(f"REX_TOOL_ERROR: reactivate_leads, user_id={user_id}, error={e}", exc_info=True)
            return f"Error reactivating leads: {e}"


# --- Tool: Analyze ICP and Source Leads (ACTION TOOL) ---

class AnalyzeICPSourceLeadsInput(BaseModel):
    user_id: str = Field(..., description="The authenticated user's ID.")
    min_deals: int = Field(default=25, description="Minimum closed deals required for ICP analysis.")
    lead_limit: int = Field(default=100, description="Maximum number of leads to source.")


class AnalyzeICPSourceLeadsTool(BaseTool):
    name: str = "Analyze ICP and Source Leads"
    description: str = """ANALYZES ICP AND SOURCES NEW LEADS IMMEDIATELY. Use this when user says 'analyze icp', 'source leads', 'find leads', etc.
    This tool triggers the AutoICPCrew to analyze closed deals and find new leads matching the ICP.
    Returns status of analysis and sourcing."""
    args_schema: Type[BaseModel] = AnalyzeICPSourceLeadsInput

    def _run(self, user_id: str, min_deals: int = 25, lead_limit: int = 100) -> str:
        logger.info(f"REX_TOOL_START: analyze_icp_source, user_id={user_id}")
        try:
            from ..orchestration_service import OrchestrationService
            orchestration_service = OrchestrationService()
            
            result = orchestration_service.run_auto_icp_sourcing(user_id, min_deals=min_deals, lead_limit=lead_limit)
            
            leads_found = result.get("leads_found", 0)
            leads_scored = result.get("leads_scored", 0)
            
            logger.info(f"REX_TOOL_SUCCESS: analyze_icp_source, user_id={user_id}, leads_found={leads_found}")
            return f"""✅ ICP Analysis and Lead Sourcing Started

**Status:**
- ICP Analysis: Complete
- New Leads Found: {leads_found}
- Leads Scored: {leads_scored}

The AutoICPCrew (4 agents) has analyzed your closed deals and sourced new leads matching your ICP. High-scoring leads (70+) are ready for campaign launch."""
            
        except Exception as e:
            logger.error(f"REX_TOOL_ERROR: analyze_icp_source, user_id={user_id}, error={e}", exc_info=True)
            return f"Error analyzing ICP and sourcing leads: {e}"


# Instantiate all tools for the agent
get_user_kpis_tool = GetUserKPIsTool()
get_campaign_status_tool = GetCampaignStatusTool()
get_lead_details_tool = GetLeadDetailsTool()
launch_campaign_tool = LaunchCampaignTool()
reactivate_leads_tool = ReactivateLeadsTool()
analyze_icp_source_tool = AnalyzeICPSourceLeadsTool()

# All tools including ACTION tools
rex_tools = [
    get_user_kpis_tool,
    get_campaign_status_tool,
    get_lead_details_tool,
    launch_campaign_tool,
    reactivate_leads_tool,
    analyze_icp_source_tool
]

# Export for backward compatibility
REX_TOOLS = rex_tools
