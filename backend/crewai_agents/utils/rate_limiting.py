"""
Global Rate Limiting Coordination

Coordinates rate limiting across all agents to prevent domain reputation damage.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import time

logger = logging.getLogger(__name__)


class GlobalRateLimiter:
    """
    Global rate limiter that coordinates across all agents.
    
    Prevents:
    - Multiple agents sending simultaneously
    - Exceeding domain/account limits
    - Reputation damage
    """
    
    def __init__(self):
        # Per-domain rate limits
        self.domain_limits: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "daily_limit": 1000,
            "hourly_limit": 100,
            "sent_today": 0,
            "sent_this_hour": 0,
            "last_reset_daily": datetime.utcnow().date(),
            "last_reset_hourly": datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        })
        
        # Per-account rate limits
        self.account_limits: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "daily_limit": 10000,
            "hourly_limit": 1000,
            "sent_today": 0,
            "sent_this_hour": 0,
            "last_reset_daily": datetime.utcnow().date(),
            "last_reset_hourly": datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        })
        
        # Pending requests queue
        self.pending_requests: Dict[str, list] = defaultdict(list)
    
    def check_rate_limit(
        self,
        user_id: str,
        domain: str,
        count: int = 1
    ) -> Dict[str, Any]:
        """
        Check if sending is allowed within rate limits.
        
        Args:
            user_id: User account ID
            domain: Email domain
            count: Number of messages to send
        
        Returns:
            Dict with can_send, reason, wait_time
        """
        # Reset counters if needed
        self._reset_counters_if_needed(domain, user_id)
        
        # Get current limits
        domain_data = self.domain_limits[domain]
        account_data = self.account_limits[user_id]
        
        # Check domain limits
        if domain_data["sent_today"] + count > domain_data["daily_limit"]:
            return {
                "can_send": False,
                "reason": "domain_daily_limit_exceeded",
                "limit_type": "domain",
                "limit": domain_data["daily_limit"],
                "current": domain_data["sent_today"],
                "wait_time": self._time_until_daily_reset()
            }
        
        if domain_data["sent_this_hour"] + count > domain_data["hourly_limit"]:
            return {
                "can_send": False,
                "reason": "domain_hourly_limit_exceeded",
                "limit_type": "domain",
                "limit": domain_data["hourly_limit"],
                "current": domain_data["sent_this_hour"],
                "wait_time": self._time_until_hourly_reset()
            }
        
        # Check account limits
        if account_data["sent_today"] + count > account_data["daily_limit"]:
            return {
                "can_send": False,
                "reason": "account_daily_limit_exceeded",
                "limit_type": "account",
                "limit": account_data["daily_limit"],
                "current": account_data["sent_today"],
                "wait_time": self._time_until_daily_reset()
            }
        
        if account_data["sent_this_hour"] + count > account_data["hourly_limit"]:
            return {
                "can_send": False,
                "reason": "account_hourly_limit_exceeded",
                "limit_type": "account",
                "limit": account_data["hourly_limit"],
                "current": account_data["sent_this_hour"],
                "wait_time": self._time_until_hourly_reset()
            }
        
        return {
            "can_send": True,
            "reason": "within_limits",
            "domain_remaining_daily": domain_data["daily_limit"] - domain_data["sent_today"],
            "domain_remaining_hourly": domain_data["hourly_limit"] - domain_data["sent_this_hour"],
            "account_remaining_daily": account_data["daily_limit"] - account_data["sent_today"],
            "account_remaining_hourly": account_data["hourly_limit"] - account_data["sent_this_hour"]
        }
    
    def acquire_slot(
        self,
        user_id: str,
        domain: str,
        count: int = 1
    ) -> bool:
        """
        Acquire a rate limit slot (atomic operation).
        
        Returns True if slot acquired, False if limit exceeded.
        """
        result = self.check_rate_limit(user_id, domain, count)
        
        if not result["can_send"]:
            return False
        
        # Atomically increment counters
        self.domain_limits[domain]["sent_today"] += count
        self.domain_limits[domain]["sent_this_hour"] += count
        self.account_limits[user_id]["sent_today"] += count
        self.account_limits[user_id]["sent_this_hour"] += count
        
        logger.debug(
            f"Rate limit slot acquired: {count} messages for domain {domain}, "
            f"user {user_id}"
        )
        
        return True
    
    def release_slot(self, user_id: str, domain: str, count: int = 1):
        """Release a rate limit slot (if message sending failed)."""
        self.domain_limits[domain]["sent_today"] = max(0, self.domain_limits[domain]["sent_today"] - count)
        self.domain_limits[domain]["sent_this_hour"] = max(0, self.domain_limits[domain]["sent_this_hour"] - count)
        self.account_limits[user_id]["sent_today"] = max(0, self.account_limits[user_id]["sent_today"] - count)
        self.account_limits[user_id]["sent_this_hour"] = max(0, self.account_limits[user_id]["sent_this_hour"] - count)
    
    def _reset_counters_if_needed(self, domain: str, user_id: str):
        """Reset counters if new day/hour."""
        now = datetime.utcnow()
        
        # Reset daily counters
        domain_data = self.domain_limits[domain]
        if domain_data["last_reset_daily"] < now.date():
            domain_data["sent_today"] = 0
            domain_data["last_reset_daily"] = now.date()
        
        account_data = self.account_limits[user_id]
        if account_data["last_reset_daily"] < now.date():
            account_data["sent_today"] = 0
            account_data["last_reset_daily"] = now.date()
        
        # Reset hourly counters
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        if domain_data["last_reset_hourly"] < current_hour:
            domain_data["sent_this_hour"] = 0
            domain_data["last_reset_hourly"] = current_hour
        
        if account_data["last_reset_hourly"] < current_hour:
            account_data["sent_this_hour"] = 0
            account_data["last_reset_hourly"] = current_hour
    
    def _time_until_daily_reset(self) -> int:
        """Seconds until daily reset (midnight UTC)."""
        now = datetime.utcnow()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int((tomorrow - now).total_seconds())
    
    def _time_until_hourly_reset(self) -> int:
        """Seconds until hourly reset."""
        now = datetime.utcnow()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        return int((next_hour - now).total_seconds())
    
    def set_limits(
        self,
        domain: Optional[str] = None,
        user_id: Optional[str] = None,
        daily_limit: Optional[int] = None,
        hourly_limit: Optional[int] = None
    ):
        """Set custom rate limits."""
        if domain:
            if daily_limit is not None:
                self.domain_limits[domain]["daily_limit"] = daily_limit
            if hourly_limit is not None:
                self.domain_limits[domain]["hourly_limit"] = hourly_limit
        
        if user_id:
            if daily_limit is not None:
                self.account_limits[user_id]["daily_limit"] = daily_limit
            if hourly_limit is not None:
                self.account_limits[user_id]["hourly_limit"] = hourly_limit
    
    def get_status(self, user_id: str, domain: str) -> Dict[str, Any]:
        """Get current rate limit status."""
        self._reset_counters_if_needed(domain, user_id)
        
        domain_data = self.domain_limits[domain]
        account_data = self.account_limits[user_id]
        
        return {
            "domain": {
                "daily": {
                    "limit": domain_data["daily_limit"],
                    "used": domain_data["sent_today"],
                    "remaining": domain_data["daily_limit"] - domain_data["sent_today"]
                },
                "hourly": {
                    "limit": domain_data["hourly_limit"],
                    "used": domain_data["sent_this_hour"],
                    "remaining": domain_data["hourly_limit"] - domain_data["sent_this_hour"]
                }
            },
            "account": {
                "daily": {
                    "limit": account_data["daily_limit"],
                    "used": account_data["sent_today"],
                    "remaining": account_data["daily_limit"] - account_data["sent_today"]
                },
                "hourly": {
                    "limit": account_data["hourly_limit"],
                    "used": account_data["sent_this_hour"],
                    "remaining": account_data["hourly_limit"] - account_data["sent_this_hour"]
                }
            }
        }


# Global instance
_rate_limiter: Optional[GlobalRateLimiter] = None


def get_rate_limiter() -> GlobalRateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = GlobalRateLimiter()
    return _rate_limiter






