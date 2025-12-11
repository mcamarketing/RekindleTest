# Dormant Lead Analysis Skill

Score and segment dormant leads using RFV+S framework (Recency, Frequency, Value, Source) to prioritize revival efforts.

## What This Skill Does

Analyzes dormant leads across four dimensions:
- **Recency**: How long since last interaction
- **Frequency**: Number of previous interactions
- **Value**: Estimated deal size or customer lifetime value
- **Source**: Quality of lead origin (referral, inbound, cold, etc.)

Produces a composite score (1-12) and segments leads into High/Medium/Low revival priority.

## Quick Start

```typescript
import { scoreAndSegmentLead } from './scripts/score_leads';

const lead = {
  lastInteractionDate: new Date('2024-10-15'),
  interactionCount: 7,
  estimatedDealValue: 15000,
  leadSource: 'inbound-inquiry'
};

const analysis = scoreAndSegmentLead(lead);

console.log(analysis.totalScore); // 11
console.log(analysis.segment); // "high"
console.log(analysis.revivalPriority); // 92
console.log(analysis.recommendedApproach);
// "Immediate outreach with personalized message referencing previous interactions"
```

## Scoring Framework

### Recency Scoring
- **3 points (High)**: Last interaction within 30 days
- **2 points (Medium)**: 31-90 days ago
- **1 point (Low)**: Over 90 days ago

### Frequency Scoring
- **3 points (High)**: 5+ interactions
- **2 points (Medium)**: 2-4 interactions
- **1 point (Low)**: 1 or fewer interactions

### Value Scoring
- **3 points (High)**: Deal value >$10,000
- **2 points (Medium)**: $1,000-$10,000
- **1 point (Low)**: <$1,000 or unknown

### Source Scoring
- **3 points (High)**: Referral, inbound inquiry, webinar, partnership
- **2 points (Medium)**: Cold outreach, event lead, content download
- **1 point (Low)**: Purchased list, scraping, unknown

## Segmentation

### High Priority (Score 10-12)
- Characteristics: Recently engaged, high value, quality source
- Revival rate: 40-60%
- Recommended approach: Immediate personalized outreach
- Examples: Hot leads that went dark, high-value prospects who ghosted

### Medium Priority (Score 6-9)
- Characteristics: Balanced profile or strong in 1-2 areas
- Revival rate: 20-35%
- Recommended approach: Trigger-based outreach, nurture sequence
- Examples: Warm leads from 3 months ago, moderate-value prospects

### Low Priority (Score 1-5)
- Characteristics: Old, low engagement, low value, poor source
- Revival rate: 5-15%
- Recommended approach: Bulk reactivation campaign, archive consideration
- Examples: Year-old cold leads, low-value prospects with no engagement

## Integration

This skill integrates with:
- `pipeline_revival_messaging`: Use segment to calibrate message tone and urgency
- `roi_estimation`: Filter leads by segment before revenue calculation
- Revival Priority Engine (`backend/src/services/revival-priority-engine.ts`)

## Files Structure

```
dormant_lead_analysis/
├── README.md
├── instructions.md           # Full scoring methodology
├── config.json              # Skill metadata
├── scripts/
│   └── score_leads.ts       # Scoring implementation
├── examples/
│   ├── high-priority-lead.json
│   ├── medium-priority-lead.json
│   └── low-priority-lead.json
└── tests/
    └── test_scoring.ts
```

## Usage Examples

### Example 1: High-Value Recent Lead
```typescript
const lead = {
  lastInteractionDate: new Date('2024-12-01'),
  interactionCount: 8,
  estimatedDealValue: 25000,
  leadSource: 'referral'
};
// Score: 12 (3+3+3+3)
// Segment: high
// Priority: 100
```

### Example 2: Medium Engagement Lead
```typescript
const lead = {
  lastInteractionDate: new Date('2024-09-15'),
  interactionCount: 3,
  estimatedDealValue: 5000,
  leadSource: 'content-download'
};
// Score: 7 (2+2+2+1)
// Segment: medium
// Priority: 58
```

### Example 3: Old Cold Lead
```typescript
const lead = {
  lastInteractionDate: new Date('2023-06-01'),
  interactionCount: 1,
  estimatedDealValue: 800,
  leadSource: 'purchased-list'
};
// Score: 4 (1+1+1+1)
// Segment: low
// Priority: 17
```

## Success Metrics

- **High Segment Accuracy**: >85% of leads scored as "high" actually convert
- **Revival Rate Correlation**: Spearman's ρ > 0.7 between score and actual revival success
- **Processing Speed**: <100ms per lead

## Configuration

See `config.json` for:
- Required data fields (last_interaction_date, interaction_count, etc.)
- Optional enrichment data
- Output schema
- Performance targets

## Maintenance

**Version**: 1.0.0
**Owners**: revenue_intelligence, data_team
**Last Updated**: 2025-01-15

For calibration or threshold adjustments, contact the Revenue Intelligence team.
