"""
Twilio Integration Adapter

Handles SMS delivery via Twilio API with delivery tracking,
status callbacks, and error handling.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class TwilioAdapter:
    """Twilio SMS delivery adapter"""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = from_number or os.getenv('TWILIO_PHONE_NUMBER')

        if not all([self.account_sid, self.auth_token]):
            logger.warning("Twilio credentials not fully configured")

    async def send_sms(
        self,
        to_number: str,
        message: str,
        status_callback: Optional[str] = None,
        max_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Send SMS via Twilio

        Args:
            to_number: Recipient phone number (E.164 format)
            message: SMS message body (max 160 chars for single segment)
            status_callback: URL for delivery status callbacks
            max_price: Maximum price willing to pay for message

        Returns:
            Dict with message_sid and status
        """
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Twilio credentials not configured")

        try:
            from twilio.rest import Client

            client = Client(self.account_sid, self.auth_token)

            # Send SMS
            message_params = {
                'from_': self.from_number,
                'to': to_number,
                'body': message
            }

            if status_callback:
                message_params['status_callback'] = status_callback

            if max_price:
                message_params['max_price'] = max_price

            twilio_message = client.messages.create(**message_params)

            logger.info(f"SMS sent successfully: {twilio_message.sid}")

            return {
                'success': True,
                'message_sid': twilio_message.sid,
                'status': twilio_message.status,
                'segments': twilio_message.num_segments,
                'price': twilio_message.price,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Twilio send failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def send_batch(
        self,
        messages: List[Dict[str, Any]],
        rate_limit_delay: float = 0.1
    ) -> Dict[str, Any]:
        """
        Send batch of SMS messages via Twilio

        Args:
            messages: List of message dicts with to_number and message
            rate_limit_delay: Delay between messages in seconds

        Returns:
            Dict with success count and failures
        """
        import asyncio

        sent_count = 0
        failed_count = 0
        failures = []

        for message in messages:
            result = await self.send_sms(**message)

            if result['success']:
                sent_count += 1
            else:
                failed_count += 1
                failures.append({
                    'to_number': message.get('to_number'),
                    'error': result.get('error')
                })

            # Rate limiting delay
            if rate_limit_delay > 0:
                await asyncio.sleep(rate_limit_delay)

        return {
            'sent_count': sent_count,
            'failed_count': failed_count,
            'failures': failures
        }

    def process_status_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Twilio status callback

        Twilio sends callbacks for: queued, sent, delivered, failed, undelivered

        Args:
            callback_data: Callback data from Twilio

        Returns:
            Normalized event data
        """
        message_status = callback_data.get('MessageStatus')

        # Map Twilio status to our internal events
        status_mapping = {
            'queued': 'queued',
            'sent': 'sent',
            'delivered': 'delivered',
            'failed': 'failed',
            'undelivered': 'failed'
        }

        normalized_event = {
            'event_type': status_mapping.get(message_status, message_status),
            'message_sid': callback_data.get('MessageSid'),
            'to_number': callback_data.get('To'),
            'from_number': callback_data.get('From'),
            'status': message_status,
            'error_code': callback_data.get('ErrorCode'),
            'error_message': callback_data.get('ErrorMessage'),
            'timestamp': datetime.utcnow().isoformat()
        }

        return normalized_event

    async def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get status of a specific message

        Args:
            message_sid: Twilio message SID

        Returns:
            Dict with message status and details
        """
        if not all([self.account_sid, self.auth_token]):
            raise ValueError("Twilio credentials not configured")

        try:
            from twilio.rest import Client

            client = Client(self.account_sid, self.auth_token)
            message = client.messages(message_sid).fetch()

            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'body': message.body,
                'num_segments': message.num_segments,
                'price': message.price,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_created': message.date_created.isoformat() if message.date_created else None,
                'date_sent': message.date_sent.isoformat() if message.date_sent else None,
            }

        except Exception as e:
            logger.error(f"Failed to fetch message status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format (E.164)

        Args:
            phone_number: Phone number to validate

        Returns:
            True if valid E.164 format
        """
        import re
        # E.164 format: +[country code][subscriber number]
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone_number))

    def format_phone_number(self, phone_number: str, country_code: str = '+1') -> str:
        """
        Format phone number to E.164 format

        Args:
            phone_number: Raw phone number
            country_code: Country code (default: +1 for US)

        Returns:
            Formatted phone number in E.164 format
        """
        # Remove non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))

        # Add country code if not present
        if not phone_number.startswith('+'):
            if len(digits) == 10:  # US number without country code
                return f"{country_code}{digits}"
            elif len(digits) == 11 and digits[0] == '1':  # US number with 1 prefix
                return f"+{digits}"

        return phone_number
