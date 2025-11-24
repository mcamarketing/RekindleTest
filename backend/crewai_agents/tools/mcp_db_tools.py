"""
MCP Database Tools for Agents

Provides safe, intention-revealing database access via MCP for agents.
All operations are read-only with scoped access to prevent data leakage.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

try:
    from backend.mcp_servers.supabase_postgres_mcp_server import get_supabase_postgres_mcp_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class MCPDBTools:
    """MCP-based database tools for agents with intention-revealing functions."""

    def __init__(self):
        if MCP_AVAILABLE:
            self.mcp_server = get_supabase_postgres_mcp_server()
        else:
            self.mcp_server = None
            print("Warning: Supabase Postgres MCP server not available")

    def get_pipeline_summary(self, account_id: str) -> Dict[str, Any]:
        """
        Get comprehensive pipeline summary for an account.

        Returns aggregated metrics including:
        - Total leads in pipeline
        - Conversion rates by stage
        - Revenue projections
        - Activity metrics
        """
        if not self.mcp_server:
            raise RuntimeError("MCP server not available")

        return self.mcp_server.get_pipeline_summary(account_id=account_id)

    def get_campaign_performance(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get detailed performance metrics for a specific campaign.

        Returns:
        - Open rates, click rates, conversion rates
        - Revenue attribution
        - Lead quality scores
        - Timeline performance
        """
        if not self.mcp_server:
            raise RuntimeError("MCP server not available")

        return self.mcp_server.get_campaign_performance(campaign_id=campaign_id)

    def get_dormant_leads(self, account_id: str, since: datetime) -> List[Dict[str, Any]]:
        """
        Get leads that have been dormant since the specified date.

        Filters for leads with no activity (opens, clicks, replies) since 'since'.
        Returns lead profiles with last activity timestamps.
        """
        if not self.mcp_server:
            raise RuntimeError("MCP server not available")

        return self.mcp_server.get_dormant_leads(
            account_id=account_id,
            since=since.isoformat()
        )

    def get_meeting_stats(self, account_id: str, period: str = "30d") -> Dict[str, Any]:
        """
        Get meeting statistics for an account over the specified period.

        Period formats: '7d', '30d', '90d', '1y'
        Returns:
        - Total meetings booked
        - Meeting types distribution
        - Conversion rates from meetings
        - Revenue from meetings
        """
        if not self.mcp_server:
            raise RuntimeError("MCP server not available")

        return self.mcp_server.get_meeting_stats(
            account_id=account_id,
            period=period
        )


# Singleton instance for easy access
_mcp_db_tools: Optional[MCPDBTools] = None

def get_mcp_db_tools() -> MCPDBTools:
    """Get singleton MCP database tools instance."""
    global _mcp_db_tools
    if _mcp_db_tools is None:
        _mcp_db_tools = MCPDBTools()
    return _mcp_db_tools