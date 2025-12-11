# Pipeline Revival Messaging Skill

Generate warm, human, trigger-aware revival messages for dormant leads that spark re-engagement without being pushy or salesy.

## What This Skill Does

This skill generates personalized outreach messages for dormant leads based on:
- **Trigger events** (funding, hiring, market changes, seasonal timing, tech adoption, pain points)
- **Lead temperature** (hot/warm/cold based on last engagement)
- **Business type** (SaaS, agency, real estate, restaurant, local services)
- **Industry-specific language** and metrics

## Quick Start

```typescript
import { generateRevivalMessage } from './scripts/generate_message';

const lead = {
  name: 'Sarah Chen',
  company: 'DataPulse Analytics',
  businessType: 'saas',
  lastEngagementDate: new Date('2024-11-01'),
  triggerEvents: [
    {
      type: 'funding',
      description: 'closed Series B ($12M)',
      confidence: 0.95,
      detectedAt: new Date()
    }
  ]
};

const message = generateRevivalMessage(lead);

console.log(message.subjectLine);
// "Your Series B + our pipeline work"

console.log(message.fullMessage);
// Hey Sarah – saw DataPulse just closed the Series B...
```

## Files Structure

```
pipeline_revival_messaging/
├── README.md                     # This file
├── instructions.md               # Full skill instructions and guidelines
├── config.json                   # Skill metadata and configuration
├── scripts/
│   └── generate_message.ts       # Message generation logic
├── examples/
│   ├── saas-hot-funding.md       # SaaS example with funding trigger
│   ├── agency-warm-hiring.md     # Agency example with hiring trigger
│   ├── real-estate-cold-market-change.md
│   ├── restaurant-warm-seasonal.md
│   └── local-services-hot-tech-adoption.md
└── tests/
    └── test_message_generation.ts
```

## Core Principles

1. **Human-First Tone**: Write like a consultant, not a sales robot
2. **Trigger-Aware Context**: Every message references a specific trigger event
3. **Value-First Approach**: Lead with insight, not pitch

## Message Structure

Every generated message includes:
- **Subject Line** (30-50 chars): References trigger or shared context
- **Opening** (1-2 sentences): Acknowledges trigger, shows understanding
- **Body** (2-3 sentences): Shares insight, mentions specific outcomes
- **CTA** (1 sentence): Low-friction ask with escape hatch

Total message length: 60-100 words

## Success Criteria

Messages generated with this skill achieve:
- **40%+ open rate**
- **15%+ response rate**
- **8%+ meeting booking rate**
- **<2% unsubscribe rate**

## Industry Adaptations

### SaaS/Tech
- Metrics: ARR, CAC, churn, product-market fit
- Language: "reduced churn by 23%" not "improved retention"

### Agency/Services
- Metrics: CAC, utilization rates, project margins
- Language: "booked pipeline" not "generated leads"

### Real Estate
- Metrics: transaction volume, market conditions
- Language: "closed 14 deals" not "helped buyers"

### Restaurant/Hospitality
- Metrics: covers, table turns, labor costs
- Language: "seats filled" not "customers acquired"

### Local Services
- Metrics: job volume, crew utilization
- Language: "booked 40% more jobs" not "grew business"

## Usage Examples

### Hot Lead (< 90 days)
```typescript
const hotLead = {
  name: 'Tom Bradley',
  company: 'ProTech HVAC',
  businessType: 'local-services',
  lastEngagementDate: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000),
  triggerEvents: [{
    type: 'tech-adoption',
    description: 'adopted ServiceTitan CRM',
    confidence: 0.9,
    detectedAt: new Date()
  }]
};

const message = generateRevivalMessage(hotLead);
// Short, direct, confident tone
```

### Warm Lead (90-180 days)
```typescript
const warmLead = {
  name: 'Marcus Rivera',
  company: 'Velocity Creative',
  businessType: 'agency',
  lastEngagementDate: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000),
  triggerEvents: [{
    type: 'hiring',
    description: 'hired Head of Client Success',
    confidence: 0.85,
    detectedAt: new Date()
  }]
};

const message = generateRevivalMessage(warmLead);
// Acknowledges gap, reestablishes context
```

### Cold Lead (180+ days)
```typescript
const coldLead = {
  name: 'Jennifer Lopez',
  company: 'Coastal Properties',
  businessType: 'real-estate',
  lastEngagementDate: new Date(Date.now() - 240 * 24 * 60 * 60 * 1000),
  triggerEvents: [{
    type: 'market-change',
    description: 'inventory dropped 35%',
    confidence: 0.78,
    detectedAt: new Date()
  }]
};

const message = generateRevivalMessage(coldLead);
// Humble re-introduction, strong trigger justification
```

## Testing

Run tests with:
```bash
npm test skills/pipeline_revival_messaging/tests
```

Tests cover:
- Message generation for all business types
- Temperature-based tone calibration
- Industry-specific language
- Success criteria validation
- Performance estimation
- Multiple trigger prioritization

## Integration

This skill integrates with:
- **Lead Segmentation Service** (`backend/src/services/lead-segmentation.ts`)
- **Revival Priority Engine** (`backend/src/services/revival-priority-engine.ts`)
- **CrewAI Agents** (`backend/crewai_agents/`)
- **REX System** (`backend/rex/`)

## Configuration

See `config.json` for:
- Required and optional lead data fields
- Output message components and metadata
- Success criteria thresholds
- Execution mode and performance specs

## Examples Gallery

Browse `/examples` for real message samples across:
- 5 business types
- 3 temperature levels
- 6 trigger event types

Each example includes metrics and analysis of why it works.

## Maintenance

**Version**: 1.0.0
**Owners**: rex_team, revenue_intelligence
**Last Updated**: 2025-01-15

For questions or improvements, contact the REX team.
