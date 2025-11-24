"""
LinkedIn MCP Server

Model Context Protocol server for LinkedIn integration.
Handles profile data, company updates, job postings, and engagement tracking.
"""

from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv
import logging
import requests
from datetime import datetime

load_dotenv()

logger = logging.getLogger(__name__)

# LinkedIn API configuration
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"


class LinkedInMCPServer:
    """
    LinkedIn MCP Server for lead intelligence.
    
    Provides methods for:
    - Fetching profile data
    - Getting company updates
    - Finding job postings
    - Tracking engagement
    """
    
    def __init__(self):
        if not LINKEDIN_ACCESS_TOKEN:
            logger.warning("LINKEDIN_ACCESS_TOKEN not set - LinkedIn operations will fail")
        self.access_token = LINKEDIN_ACCESS_TOKEN
        self.api_base = LINKEDIN_API_BASE
    
    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to LinkedIn API.
        
        Args:
            endpoint: API endpoint (e.g., "/people/~")
            method: HTTP method
            params: Query parameters
            data: Request body
        
        Returns:
            API response
        """
        if not self.access_token:
            return {
                "success": False,
                "error": "LinkedIn access token not configured"
            }
        
        url = f"{self.api_base}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported method: {method}"
                }
            
            response.raise_for_status()
            
            return {
                "success": True,
                "data": response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_profile_data(
        self,
        email: Optional[str] = None,
        profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get LinkedIn profile data.
        
        Args:
            email: Email address (for lookup)
            profile_id: LinkedIn profile ID (if known)
        
        Returns:
            Profile data
        """
        # Note: LinkedIn API v2 requires specific permissions and endpoints
        # This is a simplified implementation
        
        if profile_id:
            # Get profile by ID
            endpoint = f"/people/(id:{profile_id})"
            params = {
                "projection": "(id,firstName,lastName,headline,summary,positions,educations)"
            }
        else:
            # Get own profile (requires authentication)
            endpoint = "/people/~"
            params = {
                "projection": "(id,firstName,lastName,headline,summary,positions,educations)"
            }
        
        result = self._make_request(endpoint, params=params)
        
        if result.get("success"):
            profile = result.get("data", {})
            return {
                "success": True,
                "profile": {
                    "id": profile.get("id"),
                    "first_name": profile.get("firstName", {}).get("localized", {}).get("en_US"),
                    "last_name": profile.get("lastName", {}).get("localized", {}).get("en_US"),
                    "headline": profile.get("headline", {}).get("localized", {}).get("en_US"),
                    "summary": profile.get("summary", {}).get("localized", {}).get("en_US"),
                    "current_role": self._extract_current_role(profile),
                    "positions": profile.get("positions", {}).get("elements", [])
                }
            }
        else:
            return result
    
    def _extract_current_role(self, profile: Dict) -> Optional[str]:
        """Extract current role from profile positions."""
        positions = profile.get("positions", {}).get("elements", [])
        if positions:
            # Get most recent position
            current = positions[0]
            title = current.get("title", {}).get("localized", {}).get("en_US")
            company = current.get("companyName", {}).get("localized", {}).get("en_US")
            return f"{title} at {company}" if title and company else title
        return None
    
    def get_company_updates(
        self,
        company_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get company updates/posts.
        
        Args:
            company_id: LinkedIn company ID
            limit: Maximum number of updates to return
        
        Returns:
            List of company updates
        """
        # Note: This requires Company Page Admin access
        # For public data, would use different endpoint
        
        endpoint = f"/companies/{company_id}/updates"
        params = {
            "count": limit,
            "format": "json"
        }
        
        result = self._make_request(endpoint, params=params)
        
        if result.get("success"):
            updates = result.get("data", {}).get("values", [])
            return {
                "success": True,
                "updates": [
                    {
                        "id": update.get("updateKey"),
                        "text": update.get("updateContent", {}).get("companyStatusUpdate", {}).get("share", {}).get("comment"),
                        "timestamp": update.get("timestamp"),
                        "engagement": update.get("numLikes", 0) + update.get("numComments", 0)
                    }
                    for update in updates
                ]
            }
        else:
            return result
    
    def get_job_postings(
        self,
        company_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get job postings for a company.
        
        Args:
            company_id: LinkedIn company ID
            limit: Maximum number of postings to return
        
        Returns:
            List of job postings
        """
        # Note: LinkedIn Job Search API requires specific permissions
        # This is a placeholder implementation
        
        # Would use: /jobSearch or company-specific endpoint
        endpoint = f"/companies/{company_id}/jobs"
        params = {
            "count": limit
        }
        
        result = self._make_request(endpoint, params=params)
        
        if result.get("success"):
            jobs = result.get("data", {}).get("elements", [])
            return {
                "success": True,
                "job_postings": [
                    {
                        "id": job.get("id"),
                        "title": job.get("title"),
                        "location": job.get("location"),
                        "posted_date": job.get("postedDate"),
                        "description": job.get("description", {}).get("text")
                    }
                    for job in jobs
                ]
            }
        else:
            # Fallback: Return placeholder data structure
            return {
                "success": True,
                "job_postings": [],
                "note": "LinkedIn Job API requires additional permissions"
            }
    
    def search_profiles(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search LinkedIn profiles.
        
        Args:
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of matching profiles
        """
        # Note: LinkedIn People Search API requires specific permissions
        # This is a placeholder implementation
        
        endpoint = "/people-search"
        params = {
            "keywords": query,
            "count": limit
        }
        
        result = self._make_request(endpoint, params=params)
        
        if result.get("success"):
            profiles = result.get("data", {}).get("elements", [])
            return {
                "success": True,
                "profiles": [
                    {
                        "id": profile.get("id"),
                        "first_name": profile.get("firstName"),
                        "last_name": profile.get("lastName"),
                        "headline": profile.get("headline")
                    }
                    for profile in profiles
                ]
            }
        else:
            return result
    
    def get_company_info(
        self,
        company_id: str
    ) -> Dict[str, Any]:
        """
        Get company information.
        
        Args:
            company_id: LinkedIn company ID
        
        Returns:
            Company data
        """
        endpoint = f"/companies/{company_id}"
        params = {
            "projection": "(id,name,description,websiteUrl,employeeCount,industries,locations)"
        }
        
        result = self._make_request(endpoint, params=params)
        
        if result.get("success"):
            company = result.get("data", {})
            return {
                "success": True,
                "company": {
                    "id": company.get("id"),
                    "name": company.get("name", {}).get("localized", {}).get("en_US"),
                    "description": company.get("description", {}).get("localized", {}).get("en_US"),
                    "website": company.get("websiteUrl"),
                    "employee_count": company.get("employeeCount"),
                    "industries": company.get("industries", []),
                    "locations": company.get("locations", {}).get("elements", [])
                }
            }
        else:
            return result


# Singleton instance
_linkedin_mcp_server: Optional[LinkedInMCPServer] = None

def get_linkedin_mcp_server() -> LinkedInMCPServer:
    """Get singleton LinkedIn MCP server instance."""
    global _linkedin_mcp_server
    if _linkedin_mcp_server is None:
        _linkedin_mcp_server = LinkedInMCPServer()
    return _linkedin_mcp_server









