# Booking Rules Skill

## Purpose
Determine booking eligibility and generate booking payload for manual or automated booking.

## Booking Criteria

**ALLOW BOOKING:**
- Lead is qualified (score >= 70)
- Lead explicitly requested call/demo/meeting
- All required info collected
- No recent booking exists (7 day window)

**DEFER BOOKING:**
- Lead interested but wants info first
- Timeline is 30+ days out
- Waiting on internal approval
- Needs to check calendar first

**BLOCK BOOKING:**
- Lead not qualified
- Spam/abuse signals
- On suppression list
- Previously no-showed 2+ times

## Output Format
```json
{
  "allow_booking": true/false,
  "reason": "Why booking is allowed or blocked",
  "booking_type": "discovery|demo|consultation",
  "duration_minutes": 15|30|60,
  "notes_for_human": "Any special instructions",
  "calendar_link": "URL if automated"
}
```
