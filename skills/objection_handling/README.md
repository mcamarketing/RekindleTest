# Objection Handling Skill

Provide tactical, empathetic responses to common objections during lead revival outreach. Focuses on validation, reframing, and removing friction rather than high-pressure "overcoming."

## What This Skill Does

Generates contextual responses to 7 common objection types:
1. **Timing** - "Not the right time"
2. **Budget** - "Too expensive / No budget"
3. **Skepticism** - "Doesn't work / Tried before"
4. **Authority** - "Need to check with team"
5. **Status Quo** - "Happy with current process"
6. **Competition** - "Already using competitor"
7. **Data Privacy** - "GDPR / Privacy concerns"

## Quick Start

```typescript
import { handleObjection } from './scripts/choose_response';

const objection = {
  type: 'budget',
  leadTemperature: 'warm',
  industryVertical: 'saas'
};

const response = handleObjection(objection);

console.log(response.message_text);
// "Budget constraints are real – I hear you. The thing is, our average
//  SaaS client recovers $200K-$500K from dormant pipeline in the first 60 days,
//  and we only charge for confirmed meetings. Want to see a quick ROI
//  estimate based on your list size?"
```

## Response Framework

Every response follows this 3-part structure:

### 1. Acknowledge
Validate their concern genuinely without being defensive

```
"Budget constraints are real – I hear you."
"I totally understand the skepticism..."
"Smart to involve the team."
```

### 2. Reframe
Provide context or insight that shifts perspective

```
"The thing is, our average client recovers $200K-$500K..."
"We're different: we monitor 50+ trigger events..."
"What if I sent you a one-pager you can forward?"
```

### 3. Reduce Friction
Offer low-stakes next step with easy out

```
"Want to see a quick ROI estimate?"
"Can I share a case study?"
"If not, no worries."
```

## Objection Types and Responses

### Timing Objection
**Trigger phrases**: "not the right time", "check back later", "too busy"

**Response approach**:
- Acknowledge bandwidth constraints
- Reframe: Why timing might be better than they think
- Offer async resource or calendar hold

### Budget Objection
**Trigger phrases**: "no budget", "too expensive", "can't afford"

**Response approach**:
- Validate budget constraints
- Reframe as revenue generator vs. cost
- Offer ROI calculator or performance-based pricing

### Skepticism Objection
**Trigger phrases**: "tried before", "doesn't work", "too good to be true"

**Response approach**:
- Validate past bad experiences
- Differentiate from generic approaches
- Share industry-specific case study

### Authority Objection
**Trigger phrases**: "check with team", "need boss approval"

**Response approach**:
- Validate collaborative decision-making
- Offer to join conversation or provide materials
- Provide shareable one-pager

### Status Quo Objection
**Trigger phrases**: "happy with current process", "not looking to change"

**Response approach**:
- Don't attack their current system
- Position as complementary, not replacement
- Share insight about hidden opportunity

### Competition Objection
**Trigger phrases**: "already using [competitor]", "have similar tool"

**Response approach**:
- Don't bash competition
- Focus on unique differentiation
- Offer pilot comparison

### Data Privacy Objection
**Trigger phrases**: "GDPR", "privacy concerns", "can't share list"

**Response approach**:
- Validate importance of compliance
- Reassure with certifications (SOC 2, GDPR)
- Offer compliance documentation

## Tone Calibration

### Hot Leads (engaged recently)
- More direct and confident
- Assume context, less explanation
- Stronger call-to-action

### Warm Leads (engaged 90-180 days ago)
- Balanced, consultative tone
- Moderate explanation
- Softer ask with escape hatch

### Cold Leads (180+ days dormant)
- Most empathetic and patient
- More context and explanation
- Lowest-friction next step

## Integration

This skill integrates with:
- `pipeline_revival_messaging`: Include objection handling in follow-up sequences
- Sales enablement tools
- REX conversational flows

## Files Structure

```
objection_handling/
├── README.md
├── instructions.md           # Full objection types and frameworks
├── config.json              # Skill metadata
├── scripts/
│   └── choose_response.ts   # Response selection logic
├── examples/
│   ├── budget-objection.json
│   ├── timing-objection.json
│   └── skepticism-objection.json
└── tests/
    └── test_objection_handling.ts
```

## Usage Examples

### Example 1: Budget Objection (SaaS, Warm Lead)
```typescript
const response = handleObjection({
  type: 'budget',
  leadTemperature: 'warm',
  industryVertical: 'saas',
  dealValue: 8000
});

// Output:
// "Budget constraints are real – I hear you. The thing is, our average
//  SaaS client recovers $200K-$500K from dormant pipeline in the first
//  60 days, and we only charge for confirmed meetings. Want to see a quick
//  ROI estimate based on your list size?"
```

### Example 2: Timing Objection (Agency, Hot Lead)
```typescript
const response = handleObjection({
  type: 'timing',
  leadTemperature: 'hot',
  industryVertical: 'agency'
});

// Output:
// "Totally get it – Q4 is always crazy. The reason I'm reaching out now
//  is we've seen agencies leave 30% of pipeline on the table during busy
//  periods. Worth a 15-min async overview so it's on your radar when
//  bandwidth opens up?"
```

### Example 3: Skepticism Objection (Local Services, Cold Lead)
```typescript
const response = handleObjection({
  type: 'skepticism',
  leadTemperature: 'cold',
  industryVertical: 'local-services',
  previousObjections: ['timing']
});

// Output:
// "I totally understand the skepticism – most revival attempts are just
//  generic blasts. We're different: trigger-based outreach for HVAC/home
//  services. Companies like yours typically recover 8-12 jobs per month
//  from old leads. Want to see a quick case study?"
```

## DO NOT Rules

❌ Never use high-pressure tactics
❌ Never dismiss or minimize the objection
❌ Never use "Actually..." or "But..."
❌ Never make exaggerated claims
❌ Never guilt-trip ("You're leaving money on the table!")
❌ Never bash competitors
❌ Never argue or debate

## Success Metrics

- **Engagement Rate**: >40% (lead responds after handling)
- **Unsubscribe Rate**: <5%
- **Conversion to Next Step**: >20% (call, demo, pilot)

## Configuration

See `config.json` for:
- Supported objection types
- Required context data
- Output schema
- Performance targets

## Maintenance

**Version**: 1.0.0
**Owners**: sales_enablement, rex_team
**Last Updated**: 2025-01-15

For new objection patterns or response refinements, contact Sales Enablement team.
