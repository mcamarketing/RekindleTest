# Opener Templates Skill

## Purpose
Generate personalized revival messages for dormant leads based on business type and lead context.

## Rules
1. Keep messages under 160 characters for SMS compatibility
2. Use lead's first name if available
3. Match tone to business type
4. Include one clear question or hook
5. No marketing jargon
6. Sound like a human checking in

## Template Selection
- Use business_type to pick industry variant
- Fall back to generic if type unknown
- Personalize with lead name, company if available

## Output Format
```json
{
  "subject": "Brief subject line (email only)",
  "body": "The actual message text",
  "channel": "email|sms"
}
```
