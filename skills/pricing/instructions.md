# Pricing Skill

## Purpose
Calculate fees based on performance-only pricing model.

## Pricing Model
- £0 upfront
- £25 per booked meeting (qualified, shows up)
- £0.10 per revived lead (replies with interest)
- No charge for non-responses or disqualified leads

## Calculation Rules

**Revived Lead:**
- Lead replied to opener
- Reply shows any level of interest
- Does NOT include out-of-office or bounces
- Does NOT include "unsubscribe" replies

**Booked Meeting:**
- Meeting scheduled via calendar
- Lead confirmed attendance
- Meeting is >= 15 minutes
- Lead did not cancel before meeting

**Qualified Meeting (for bonus):**
- Meeting happened
- Lead showed up
- Lead fits ICP
- Next steps defined

## Output Format
```json
{
  "revived_leads": 0,
  "booked_meetings": 0,
  "qualified_meetings": 0,
  "revival_fee": 0.00,
  "booking_fee": 0.00,
  "total_fee": 0.00,
  "currency": "GBP"
}
```
