"""
Data Validation & Sanitization

Validates and sanitizes all inputs to prevent security vulnerabilities.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re
import html
import logging

logger = logging.getLogger(__name__)


class LeadData(BaseModel):
    """Validated lead data structure."""
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=5000)
    user_id: str = Field(..., min_length=1)
    
    @field_validator('first_name', 'last_name', 'company', 'job_title')
    @classmethod
    def sanitize_text(cls, v):
        """Sanitize text fields."""
        if v is None:
            return v
        # Remove HTML tags
        v = re.sub(r'<[^>]+>', '', v)
        # Escape special characters
        v = html.escape(v)
        # Trim whitespace
        v = v.strip()
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        # Remove non-digit characters
        v = re.sub(r'\D', '', v)
        # Basic validation (10-15 digits)
        if len(v) < 10 or len(v) > 15:
            raise ValueError("Invalid phone number format")
        return v
    
    @field_validator('notes')
    @classmethod
    def sanitize_notes(cls, v):
        """Sanitize notes field."""
        if v is None:
            return v
        # Remove script tags and dangerous content
        v = re.sub(r'<script[^>]*>.*?</script>', '', v, flags=re.IGNORECASE | re.DOTALL)
        v = html.escape(v)
        return v


class MessageData(BaseModel):
    """Validated message data structure."""
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=10000)
    lead_id: str = Field(..., min_length=1)
    channel: str = Field(..., pattern="^(email|sms|whatsapp|push|voicemail)$")
    
    @field_validator('subject', 'body')
    @classmethod
    def sanitize_content(cls, v):
        """Sanitize message content."""
        # Remove dangerous HTML/JavaScript
        v = re.sub(r'<script[^>]*>.*?</script>', '', v, flags=re.IGNORECASE | re.DOTALL)
        v = re.sub(r'javascript:', '', v, flags=re.IGNORECASE)
        v = re.sub(r'on\w+\s*=', '', v, flags=re.IGNORECASE)
        # Escape HTML but preserve line breaks
        v = html.escape(v)
        return v
    
    @field_validator('body')
    @classmethod
    def validate_body_length(cls, v):
        """Validate body length by channel."""
        # This would be set based on channel in full validation
        if len(v) > 10000:
            raise ValueError("Message body too long")
        return v


class CampaignData(BaseModel):
    """Validated campaign data structure."""
    user_id: str = Field(..., min_length=1)
    lead_ids: List[str] = Field(..., min_length=1)  # min_length works for lists in Pydantic v2
    campaign_type: str = Field(..., pattern=r"^(reactivation|new_lead|nurturing)$")
    
    @field_validator('lead_ids')
    @classmethod
    def validate_lead_ids(cls, v):
        """Validate lead IDs."""
        if len(v) > 1000:
            raise ValueError("Too many leads in campaign (max 1000)")
        return v


def validate_lead_data(data: Dict[str, Any]) -> LeadData:
    """Validate and sanitize lead data."""
    try:
        return LeadData(**data)
    except Exception as e:
        logger.error(f"Lead validation failed: {e}")
        raise ValueError(f"Invalid lead data: {e}")


def validate_message_data(data: Dict[str, Any]) -> MessageData:
    """Validate and sanitize message data."""
    try:
        return MessageData(**data)
    except Exception as e:
        logger.error(f"Message validation failed: {e}")
        raise ValueError(f"Invalid message data: {e}")


def validate_campaign_data(data: Dict[str, Any]) -> CampaignData:
    """Validate and sanitize campaign data."""
    try:
        return CampaignData(**data)
    except Exception as e:
        logger.error(f"Campaign validation failed: {e}")
        raise ValueError(f"Invalid campaign data: {e}")


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize a string value."""
    if not isinstance(value, str):
        value = str(value)
    
    # Remove HTML tags
    value = re.sub(r'<[^>]+>', '', value)
    
    # Escape HTML entities
    value = html.escape(value)
    
    # Trim whitespace
    value = value.strip()
    
    # Enforce max length
    if max_length and len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value


def sanitize_input(value: Any, max_length: Optional[int] = None) -> str:
    """
    Sanitize input value (alias for sanitize_string for backward compatibility).
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Optional maximum length for the string
        
    Returns:
        Sanitized string
    """
    if value is None:
        return ""
    return sanitize_string(str(value), max_length)


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_uuid(uuid: str) -> bool:
    """Validate UUID format."""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid, re.IGNORECASE))


