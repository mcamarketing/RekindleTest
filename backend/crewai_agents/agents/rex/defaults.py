"""
Intelligent Defaults for REX

Provides intelligent default values and parameter inference for REX commands.
Allows REX to execute actions without asking for clarification.
"""

from typing import Dict, List, Optional, Any
from ..tools.db_tools import SupabaseDB
import logging

logger = logging.getLogger(__name__)


class IntelligentDefaults:
    """Intelligent default values and parameter inference."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
    
    def infer_lead_ids(self, user_id: str, criteria: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Infer lead IDs from context or criteria.
        
        Default behavior:
        - If no criteria: return hot leads (score 70+)
        - If criteria specified: filter accordingly
        """
        try:
            query = self.db.supabase.table("leads").select("id").eq("user_id", user_id)
            
            if criteria:
                if criteria.get("hot_only"):
                    query = query.gte("lead_score", 70)
                if criteria.get("state"):
                    query = query.ilike("state", f"%{criteria['state']}%")
                if criteria.get("industry"):
                    query = query.ilike("industry", f"%{criteria['industry']}%")
                if criteria.get("status"):
                    query = query.eq("status", criteria["status"])
            else:
                # Default: hot leads
                query = query.gte("lead_score", 70)
            
            result = query.limit(50).execute()
            return [lead["id"] for lead in (result.data or [])]
        except Exception as e:
            logger.error(f"Error inferring lead IDs: {e}")
            return []
    
    def infer_campaign_name(self, user_id: str, context: Optional[str] = None) -> str:
        """Infer campaign name from context or generate default."""
        if context:
            # Extract potential campaign name from context
            if "campaign" in context.lower():
                # Try to extract name after "campaign" keyword
                parts = context.lower().split("campaign")
                if len(parts) > 1:
                    name = parts[1].strip()
                    if name and len(name) > 3:
                        return name.title()
        
        # Default: generate based on date
        from datetime import datetime
        return f"Campaign {datetime.utcnow().strftime('%Y-%m-%d')}"
    
    def infer_batch_size(self, user_id: str, action_type: str) -> int:
        """Infer batch size based on action type and user data."""
        defaults = {
            "reactivation": 50,
            "campaign": 50,
            "research": 100,
            "sourcing": 100
        }
        return defaults.get(action_type, 50)
    
    def infer_lead_email(self, user_id: str, context: str) -> Optional[str]:
        """Extract lead email from context if mentioned."""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, context)
        if emails:
            # Verify email belongs to user
            try:
                result = self.db.supabase.table("leads").select("email").eq("user_id", user_id).eq("email", emails[0].lower()).maybe_single().execute()
                if result.data:
                    return emails[0].lower()
            except:
                pass
        return None
    
    def get_user_defaults(self, user_id: str) -> Dict[str, Any]:
        """Get intelligent defaults for a user based on their data."""
        try:
            # Get user's typical patterns
            leads_result = self.db.supabase.table("leads").select("lead_score, status").eq("user_id", user_id).limit(100).execute()
            leads = leads_result.data or []
            
            hot_leads_count = sum(1 for lead in leads if lead.get("lead_score", 0) >= 70)
            total_leads = len(leads)
            
            defaults = {
                "preferred_batch_size": 50,
                "prefer_hot_leads": hot_leads_count > total_leads * 0.3,  # If >30% are hot
                "default_campaign_type": "reactivation" if total_leads > 100 else "new"
            }
            
            return defaults
        except Exception as e:
            logger.error(f"Error getting user defaults: {e}")
            return {
                "preferred_batch_size": 50,
                "prefer_hot_leads": True,
                "default_campaign_type": "reactivation"
            }

