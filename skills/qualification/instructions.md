# Qualification Skill

## Purpose
Determine if a lead is qualified for booking based on their responses and profile.

## Qualification Criteria

**GREEN LIGHT (Book Meeting):**
- Decision maker or strong champion
- Budget exists or can be allocated
- Timeline is 0-90 days
- Pain point is active right now
- Company fits ICP

**YELLOW LIGHT (Nurture):**
- Interested but timeline is 90+ days
- Needs approval from others
- Budget unclear
- Pain point exists but not urgent

**RED LIGHT (Disqualify):**
- No decision making power
- No budget, no path to budget
- Wrong company size/industry
- Pain point doesn't exist
- Tire kicker behavior

## Questions to Ask
Ask ONLY if information is missing. Stop after qualification is clear.

## Output Format
```json
{
  "status": "qualified|nurture|disqualified",
  "score": 0-100,
  "missing_info": ["budget", "timeline", "authority"],
  "next_question": "The specific question to ask",
  "reasoning": "Why this classification"
}
```
