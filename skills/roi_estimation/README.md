# ROI Estimation Skill

Calculate revenue upside from revival campaigns using industry-specific conversion rates across three scenarios: low (pessimistic), base (realistic), and strong (optimistic).

## What This Skill Does

Estimates the financial impact of lead revival campaigns by:
- Applying industry-specific conversion rate ranges
- Calculating expected meetings and revenue across scenarios
- Factoring in meeting-to-deal conversion (50% default)
- Computing ROI multiples when campaign costs are provided

## Quick Start

```typescript
import { estimateROI } from './scripts/calc_roi';

const campaign = {
  leadCount: 1000,
  industryVertical: 'saas',
  averageDealValue: 8000,
  campaignCost: 5000 // optional
};

const estimation = estimateROI(campaign);

console.log(estimation.base);
// {
//   conversionRate: 0.11,
//   estimatedMeetings: 110,
//   estimatedRevenue: 440000,
//   roiMultiple: 88
// }
```

## Industry Conversion Rates

### SaaS
- **Low**: 3-7% → Base: 5%
- **Base**: 7-15% → Base: 11%
- **Strong**: 15-25% → Base: 20%

### Agency
- **Low**: 5-10% → Base: 7.5%
- **Base**: 10-20% → Base: 15%
- **Strong**: 20-30% → Base: 25%

### Real Estate
- **Low**: 8-15% → Base: 11.5%
- **Base**: 15-25% → Base: 20%
- **Strong**: 25-35% → Base: 30%

### Restaurant/Hospitality
- **Low**: 10-18% → Base: 14%
- **Base**: 18-30% → Base: 24%
- **Strong**: 30-45% → Base: 37.5%

### Local Services (HVAC, Plumbing, etc.)
- **Low**: 12-20% → Base: 16%
- **Base**: 20-35% → Base: 27.5%
- **Strong**: 35-50% → Base: 42.5%

### Generic/Unknown
- **Low**: 5-10% → Base: 7.5%
- **Base**: 10-20% → Base: 15%
- **Strong**: 20-30% → Base: 25%

## Calculation Formula

```
Meetings = Lead Count × Conversion Rate
Deals = Meetings × Meeting-to-Deal Rate (default: 50%)
Revenue = Deals × Average Deal Value
ROI Multiple = Revenue / Campaign Cost (if cost provided)
```

## Scenarios Explained

### Low Scenario (Pessimistic)
- Uses lower bound of conversion range
- Accounts for poor list quality, weak messaging, or bad timing
- Conservative forecast for risk management
- Useful for worst-case planning

### Base Scenario (Realistic)
- Uses midpoint of conversion range
- Expected outcome under normal conditions
- Primary planning number
- Most accurate for established processes

### Strong Scenario (Optimistic)
- Uses upper bound of conversion range
- Accounts for excellent targeting, messaging, and timing
- Best-case forecast
- Goal-setting benchmark

## Integration

This skill integrates with:
- `dormant_lead_analysis`: Filter leads by segment before ROI calculation
- `pipeline_revival_messaging`: Use scenarios to justify outreach investment
- Revival Priority Engine (`backend/src/services/revival-priority-engine.ts`): Replace hardcoded ROI logic at line 498-506

## Files Structure

```
roi_estimation/
├── README.md
├── instructions.md           # Full methodology
├── config.json              # Skill metadata
├── scripts/
│   └── calc_roi.ts          # ROI calculation implementation
├── examples/
│   ├── saas-campaign.json
│   ├── agency-campaign.json
│   └── local-services-campaign.json
└── tests/
    └── test_roi_calc.ts
```

## Usage Examples

### Example 1: SaaS Campaign (1,000 leads, $8K ACV)
```typescript
const result = estimateROI({
  leadCount: 1000,
  industryVertical: 'saas',
  averageDealValue: 8000,
  campaignCost: 5000
});

// Low: 50 meetings → 25 deals → $200K revenue (40x ROI)
// Base: 110 meetings → 55 deals → $440K revenue (88x ROI)
// Strong: 200 meetings → 100 deals → $800K revenue (160x ROI)
```

### Example 2: Agency Campaign (500 leads, $5K project)
```typescript
const result = estimateROI({
  leadCount: 500,
  industryVertical: 'agency',
  averageDealValue: 5000,
  campaignCost: 3000
});

// Low: 37 meetings → 19 projects → $95K revenue (32x ROI)
// Base: 75 meetings → 38 projects → $190K revenue (63x ROI)
// Strong: 125 meetings → 63 projects → $315K revenue (105x ROI)
```

### Example 3: Local Services Campaign (2,000 leads, $1.2K job)
```typescript
const result = estimateROI({
  leadCount: 2000,
  industryVertical: 'local-services',
  averageDealValue: 1200,
  campaignCost: 8000
});

// Low: 320 meetings → 160 jobs → $192K revenue (24x ROI)
// Base: 550 meetings → 275 jobs → $330K revenue (41x ROI)
// Strong: 850 meetings → 425 jobs → $510K revenue (64x ROI)
```

## Success Metrics

- **Forecast Accuracy**: >75% of actual results fall within 25% of base scenario
- **Processing Speed**: <50ms per calculation
- **Scenario Coverage**: 95% confidence interval (low to strong range)

## Configuration

See `config.json` for:
- Required data fields (lead_count, industry_vertical, average_deal_value)
- Optional parameters (campaign_cost for ROI multiple)
- Output schema
- Performance targets

## Assumptions

1. **Meeting-to-Deal Conversion**: Default 50% (configurable)
2. **Industry Rates**: Based on Rekindle Pro historical data + industry benchmarks
3. **Lead Quality**: Assumes pre-filtered dormant leads (not cold lists)
4. **Time Horizon**: 60-90 day revival window

## Maintenance

**Version**: 1.0.0
**Owners**: revenue_intelligence, finance_team
**Last Updated**: 2025-01-15

For rate calibration based on new data, contact Revenue Intelligence team.
