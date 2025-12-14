# Reply Handling Skill

## Purpose
Classify incoming replies as interested, not_interested, or unclear. Extract intent and next action.

## Classification Rules

**INTERESTED signals:**
- "yes", "sure", "sounds good", "let's chat"
- Asks for pricing, demo, call
- Asks clarifying questions about product
- "send me info", "tell me more"

**NOT_INTERESTED signals:**
- "no thanks", "not interested", "unsubscribe"
- "we went another direction"
- "already solved this"
- "stop emailing"

**UNCLEAR signals:**
- Out of office replies
- "maybe later", "check back in X months"
- Questions about who you are
- Non-committal responses

## Output Format
```json
{
  "classification": "interested|not_interested|unclear",
  "confidence": 0.0-1.0,
  "extracted_intent": "Brief summary of what they said",
  "next_action": "send_qualifier|send_booking|nurture|remove",
  "notes": "Any relevant context"
}
```
