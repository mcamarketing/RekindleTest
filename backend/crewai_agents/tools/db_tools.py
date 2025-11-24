"""
Database Tools for Agents

Provides Supabase database access for all agents.
"""

from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()


class SupabaseDB:
    """Database access layer for agents."""

    def __init__(self):
        # Database connection with service role key for bypassing RLS
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        )
    
    def get_lead(self, lead_id: str) -> Optional[Dict]:
        """Get a single lead by ID."""
        result = self.supabase.table("leads").select("*").eq("id", lead_id).execute()
        return result.data[0] if result.data else None
    
    def get_dormant_leads(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get all dormant leads for a user."""
        result = self.supabase.table("leads").select("*").eq(
            "user_id", user_id
        ).eq("status", "dormant").limit(limit).execute()
        return result.data or []
    
    def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> Dict:
        """Update a lead."""
        result = self.supabase.table("leads").update(updates).eq("id", lead_id).execute()
        return result.data[0] if result.data else {}
    
    def create_trigger_event(self, event_data: Dict[str, Any]) -> Dict:
        """Create a trigger event record."""
        # Assuming a trigger_events table exists
        result = self.supabase.table("trigger_events").insert(event_data).execute()
        return result.data[0] if result.data else {}
    
    def get_closed_deals(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get closed deals for ICP analysis."""
        result = self.supabase.table("leads").select("*").eq(
            "user_id", user_id
        ).eq("status", "converted").limit(limit).execute()
        return result.data or []









