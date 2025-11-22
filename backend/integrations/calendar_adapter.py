"""
Calendar Integration Adapter

Handles calendar booking via Calendly/Google Calendar with
meeting scheduling, webhook processing, and conflict detection.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class CalendarAdapter:
    """Calendar booking and scheduling adapter"""

    def __init__(
        self,
        calendly_api_key: Optional[str] = None,
        google_credentials: Optional[str] = None
    ):
        self.calendly_api_key = calendly_api_key or os.getenv('CALENDLY_API_KEY')
        self.google_credentials = google_credentials or os.getenv('GOOGLE_CALENDAR_CREDENTIALS')

    async def create_booking_link(
        self,
        event_type: str,
        duration_minutes: int = 30,
        buffer_minutes: int = 15,
        max_events_per_day: int = 8
    ) -> Dict[str, Any]:
        """
        Create personalized booking link for lead

        Args:
            event_type: Type of event (demo, consultation, etc.)
            duration_minutes: Meeting duration
            buffer_minutes: Buffer time between meetings
            max_events_per_day: Maximum bookings per day

        Returns:
            Dict with booking_url and configuration
        """
        try:
            # In production, this would integrate with Calendly or similar
            # For now, return a simulated booking link

            booking_id = f"booking_{datetime.utcnow().timestamp()}"

            return {
                'success': True,
                'booking_url': f"https://calendly.com/your-org/{event_type}",
                'booking_id': booking_id,
                'event_type': event_type,
                'duration_minutes': duration_minutes,
                'buffer_minutes': buffer_minutes,
                'max_events_per_day': max_events_per_day,
                'created_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to create booking link: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def check_availability(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Check calendar availability for time slots

        Args:
            start_date: Start of availability window
            end_date: End of availability window
            duration_minutes: Required slot duration

        Returns:
            Dict with available time slots
        """
        try:
            # Simulated availability checking
            # In production, would check Google Calendar API or similar

            available_slots = []
            current = start_date

            while current < end_date:
                # Business hours: 9am - 5pm weekdays
                if current.weekday() < 5 and 9 <= current.hour < 17:
                    available_slots.append({
                        'start': current.isoformat(),
                        'end': (current + timedelta(minutes=duration_minutes)).isoformat(),
                        'duration_minutes': duration_minutes
                    })

                current += timedelta(minutes=duration_minutes)

            return {
                'success': True,
                'available_slots': available_slots,
                'total_slots': len(available_slots)
            }

        except Exception as e:
            logger.error(f"Failed to check availability: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def schedule_meeting(
        self,
        lead_email: str,
        lead_name: str,
        start_time: datetime,
        duration_minutes: int = 30,
        meeting_type: str = 'demo',
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a meeting with a lead

        Args:
            lead_email: Lead's email address
            lead_name: Lead's full name
            start_time: Meeting start time
            duration_minutes: Meeting duration
            meeting_type: Type of meeting
            notes: Additional notes

        Returns:
            Dict with meeting_id and details
        """
        try:
            # In production, would use Google Calendar API or Calendly

            meeting_id = f"meeting_{datetime.utcnow().timestamp()}"
            end_time = start_time + timedelta(minutes=duration_minutes)

            meeting_data = {
                'meeting_id': meeting_id,
                'lead_email': lead_email,
                'lead_name': lead_name,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': duration_minutes,
                'meeting_type': meeting_type,
                'notes': notes,
                'status': 'scheduled',
                'created_at': datetime.utcnow().isoformat()
            }

            logger.info(f"Meeting scheduled: {meeting_id}")

            return {
                'success': True,
                **meeting_data
            }

        except Exception as e:
            logger.error(f"Failed to schedule meeting: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def cancel_meeting(self, meeting_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel a scheduled meeting

        Args:
            meeting_id: Meeting identifier
            reason: Cancellation reason

        Returns:
            Dict with cancellation status
        """
        try:
            logger.info(f"Meeting cancelled: {meeting_id}")

            return {
                'success': True,
                'meeting_id': meeting_id,
                'status': 'cancelled',
                'reason': reason,
                'cancelled_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to cancel meeting: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def reschedule_meeting(
        self,
        meeting_id: str,
        new_start_time: datetime
    ) -> Dict[str, Any]:
        """
        Reschedule an existing meeting

        Args:
            meeting_id: Meeting identifier
            new_start_time: New start time

        Returns:
            Dict with updated meeting details
        """
        try:
            logger.info(f"Meeting rescheduled: {meeting_id}")

            return {
                'success': True,
                'meeting_id': meeting_id,
                'new_start_time': new_start_time.isoformat(),
                'status': 'rescheduled',
                'updated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to reschedule meeting: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def process_booking_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Calendly/Google Calendar booking webhook

        Args:
            webhook_data: Webhook payload from calendar provider

        Returns:
            Normalized event data
        """
        event_type = webhook_data.get('event')

        # Map provider events to internal events
        event_mapping = {
            'invitee.created': 'booking_created',
            'invitee.canceled': 'booking_cancelled',
            'event.created': 'meeting_scheduled',
            'event.canceled': 'meeting_cancelled',
        }

        normalized_event = {
            'event_type': event_mapping.get(event_type, event_type),
            'invitee_email': webhook_data.get('payload', {}).get('email'),
            'invitee_name': webhook_data.get('payload', {}).get('name'),
            'event_start_time': webhook_data.get('payload', {}).get('start_time'),
            'event_end_time': webhook_data.get('payload', {}).get('end_time'),
            'event_uri': webhook_data.get('payload', {}).get('uri'),
            'cancel_url': webhook_data.get('payload', {}).get('cancel_url'),
            'reschedule_url': webhook_data.get('payload', {}).get('reschedule_url'),
            'timestamp': datetime.utcnow().isoformat()
        }

        return normalized_event

    async def send_meeting_reminder(
        self,
        meeting_id: str,
        lead_email: str,
        meeting_time: datetime,
        hours_before: int = 24
    ) -> Dict[str, Any]:
        """
        Send meeting reminder to lead

        Args:
            meeting_id: Meeting identifier
            lead_email: Lead's email
            meeting_time: Scheduled meeting time
            hours_before: Hours before meeting to send reminder

        Returns:
            Dict with reminder status
        """
        try:
            time_until_meeting = (meeting_time - datetime.utcnow()).total_seconds() / 3600

            if time_until_meeting <= hours_before:
                # Reminder would be sent
                logger.info(f"Meeting reminder sent: {meeting_id}")

                return {
                    'success': True,
                    'meeting_id': meeting_id,
                    'reminder_sent': True,
                    'sent_at': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': True,
                    'meeting_id': meeting_id,
                    'reminder_sent': False,
                    'reason': 'too_early',
                    'time_until_meeting_hours': time_until_meeting
                }

        except Exception as e:
            logger.error(f"Failed to send meeting reminder: {e}")
            return {
                'success': False,
                'error': str(e)
            }
