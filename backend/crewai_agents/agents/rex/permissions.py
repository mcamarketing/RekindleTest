"""
Permissions Module for REX

Determines user login status, package type, and feature permissions.
Enforces package-based access control for all REX actions.
"""

from typing import Dict, List, Optional, Any, Tuple
from ..tools.db_tools import SupabaseDB
import logging

logger = logging.getLogger(__name__)


class PermissionsManager:
    """Manages user permissions and package-based feature access."""
    
    # Package feature mappings
    PACKAGE_FEATURES = {
        "free": {
            "campaign_launch": False,
            "lead_reactivation": False,
            "icp_analysis": False,
            "lead_sourcing": False,
            "lead_research": False,
            "kpis": True,
            "campaign_status": True,
            "lead_details": True
        },
        "starter": {
            "campaign_launch": True,
            "lead_reactivation": False,
            "icp_analysis": False,
            "lead_sourcing": False,
            "lead_research": True,
            "kpis": True,
            "campaign_status": True,
            "lead_details": True
        },
        "professional": {
            "campaign_launch": True,
            "lead_reactivation": True,
            "icp_analysis": True,
            "lead_sourcing": True,
            "lead_research": True,
            "kpis": True,
            "campaign_status": True,
            "lead_details": True
        },
        "pro": {  # Alias for professional
            "campaign_launch": True,
            "lead_reactivation": True,
            "icp_analysis": True,
            "lead_sourcing": True,
            "lead_research": True,
            "kpis": True,
            "campaign_status": True,
            "lead_details": True
        },
        "enterprise": {
            "campaign_launch": True,
            "lead_reactivation": True,
            "icp_analysis": True,
            "lead_sourcing": True,
            "lead_research": True,
            "kpis": True,
            "campaign_status": True,
            "lead_details": True
        }
    }
    
    # Action to feature mapping
    ACTION_FEATURE_MAP = {
        "launch_campaign": "campaign_launch",
        "reactivate_leads": "lead_reactivation",
        "analyze_icp": "icp_analysis",
        "source_leads": "lead_sourcing",
        "research_leads": "lead_research",
        "get_kpis": "kpis",
        "get_campaign_status": "campaign_status",
        "get_lead_details": "lead_details"
    }
    
    def __init__(self, db: SupabaseDB):
        self.db = db
    
    def check_user_state(self, user_id: Optional[str]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if user is logged in and get package info.
        
        Returns:
            (is_logged_in, user_id, package_type)
        """
        if not user_id:
            return (False, None, None)
        
        try:
            # Get user profile with package info
            # Try both package_type and subscription_tier fields
            profile_result = self.db.supabase.table("profiles").select("id, package_type, subscription_tier, subscription_status").eq("id", user_id).maybe_single().execute()
            
            if not profile_result.data:
                return (False, None, None)
            
            profile = profile_result.data
            # Check both field names for package type
            package_type = profile.get("package_type") or profile.get("subscription_tier", "free")
            subscription_status = profile.get("subscription_status", "inactive")
            
            # Normalize package type (pro is already in PACKAGE_FEATURES, but keep for compatibility)
            if package_type not in self.PACKAGE_FEATURES:
                package_type = "free"  # Default to free for unknown packages
            
            # Check if subscription is active
            is_active = subscription_status in ["active", "trial"]
            
            if not is_active:
                return (True, user_id, "free")  # Default to free if inactive
            
            return (True, user_id, package_type)
            
        except Exception as e:
            logger.error(f"Error checking user state: {e}")
            return (False, None, None)
    
    def check_permission(self, user_id: Optional[str], action: str) -> Tuple[bool, Optional[str]]:
        """
        Check if user has permission for an action.
        
        Returns:
            (has_permission, error_message)
        """
        # Check login state
        is_logged_in, actual_user_id, package_type = self.check_user_state(user_id)
        
        if not is_logged_in:
            return (False, "Please log in to access this feature.")
        
        # Map action to feature
        feature = self.ACTION_FEATURE_MAP.get(action)
        if not feature:
            # Unknown action - allow for logged-in users (will be handled by executor)
            return (True, None)
        
        # Check package permissions
        package_features = self.PACKAGE_FEATURES.get(package_type, self.PACKAGE_FEATURES["free"])
        has_permission = package_features.get(feature, False)
        
        if not has_permission:
            return (False, "This feature is not included in your package. Upgrade to access.")
        
        return (True, None)
    
    def get_user_package(self, user_id: Optional[str]) -> Optional[str]:
        """Get user's package type."""
        _, _, package_type = self.check_user_state(user_id)
        return package_type
    
    def get_available_features(self, user_id: Optional[str]) -> List[str]:
        """Get list of features available to user."""
        is_logged_in, _, package_type = self.check_user_state(user_id)
        
        if not is_logged_in:
            return []
        
        package_features = self.PACKAGE_FEATURES.get(package_type, self.PACKAGE_FEATURES["free"])
        return [feature for feature, enabled in package_features.items() if enabled]
    
    def can_execute_action(self, user_id: Optional[str], action: str) -> Tuple[bool, Optional[str]]:
        """
        Main permission check method.
        
        Returns:
            (can_execute, error_message)
        """
        return self.check_permission(user_id, action)

