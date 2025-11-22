"""
SendGrid Integration Adapter

Handles email delivery via SendGrid API with deliverability tracking,
webhook processing, and error handling.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class SendGridAdapter:
    """SendGrid email delivery adapter"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            logger.warning("SendGrid API key not configured")

    async def send_email(
        self,
        to_email: str,
        from_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        tracking_enabled: bool = True,
        custom_args: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send email via SendGrid

        Args:
            to_email: Recipient email address
            from_email: Sender email address
            subject: Email subject line
            html_content: HTML email body
            text_content: Plain text email body (optional)
            tracking_enabled: Enable click and open tracking
            custom_args: Custom arguments for tracking

        Returns:
            Dict with message_id and status
        """
        if not self.api_key:
            raise ValueError("SendGrid API key not configured")

        try:
            # Import SendGrid SDK
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, TrackingSettings, ClickTracking, OpenTracking

            # Build email
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content or self._html_to_text(html_content)
            )

            # Configure tracking
            if tracking_enabled:
                message.tracking_settings = TrackingSettings()
                message.tracking_settings.click_tracking = ClickTracking(True, True)
                message.tracking_settings.open_tracking = OpenTracking(True)

            # Add custom arguments for webhook tracking
            if custom_args:
                for key, value in custom_args.items():
                    message.custom_arg = {key: value}

            # Send via SendGrid
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            logger.info(f"Email sent successfully: {response.status_code}")

            return {
                'success': True,
                'message_id': response.headers.get('X-Message-Id'),
                'status_code': response.status_code,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def send_batch(
        self,
        messages: List[Dict[str, Any]],
        max_batch_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Send batch of emails via SendGrid

        Args:
            messages: List of message dicts with to_email, from_email, subject, html_content
            max_batch_size: Maximum batch size (SendGrid limit is 1000)

        Returns:
            Dict with success count and failures
        """
        if not self.api_key:
            raise ValueError("SendGrid API key not configured")

        # Chunk messages into batches
        batches = [
            messages[i:i + max_batch_size]
            for i in range(0, len(messages), max_batch_size)
        ]

        sent_count = 0
        failed_count = 0
        failures = []

        for batch in batches:
            for message in batch:
                result = await self.send_email(**message)
                if result['success']:
                    sent_count += 1
                else:
                    failed_count += 1
                    failures.append({
                        'to_email': message.get('to_email'),
                        'error': result.get('error')
                    })

        return {
            'sent_count': sent_count,
            'failed_count': failed_count,
            'failures': failures
        }

    def process_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process SendGrid webhook event

        SendGrid sends events for: delivered, opened, clicked, bounced, etc.

        Args:
            event_data: Webhook event data from SendGrid

        Returns:
            Normalized event data
        """
        event_type = event_data.get('event')

        # Map SendGrid events to our internal events
        event_mapping = {
            'delivered': 'delivered',
            'open': 'opened',
            'click': 'clicked',
            'bounce': 'bounced',
            'dropped': 'bounced',
            'deferred': 'deferred',
            'spam_report': 'spam_reported',
            'unsubscribe': 'unsubscribed'
        }

        normalized_event = {
            'event_type': event_mapping.get(event_type, event_type),
            'email': event_data.get('email'),
            'timestamp': event_data.get('timestamp'),
            'message_id': event_data.get('sg_message_id'),
            'custom_args': event_data.get('custom_args', {}),
            'raw_event': event_type,
            'url': event_data.get('url'),  # For click events
            'reason': event_data.get('reason'),  # For bounce/drop events
        }

        return normalized_event

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text (simple implementation)"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        return text.strip()

    async def get_stats(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get SendGrid statistics for date range

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dict with delivery statistics
        """
        if not self.api_key:
            raise ValueError("SendGrid API key not configured")

        try:
            from sendgrid import SendGridAPIClient

            sg = SendGridAPIClient(self.api_key)

            # Get stats from SendGrid API
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'aggregated_by': 'day'
            }

            response = sg.client.stats.get(query_params=params)

            return {
                'success': True,
                'stats': response.body,
                'status_code': response.status_code
            }

        except Exception as e:
            logger.error(f"Failed to fetch SendGrid stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }
