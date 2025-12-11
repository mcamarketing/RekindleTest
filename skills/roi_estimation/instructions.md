# ROI Estimation

## Purpose
This skill calculates revenue upside from revival campaigns by estimating meetings and revenue across low, base, and strong scenarios.

## Calculating Low, Base, and Strong Scenarios

### Conversion Ranges per Industry
- **Agency**: 5-10% (low), 10-20% (base), 20-30% (strong)
- **SaaS**: 3-7% (low), 7-15% (base), 15-25% (strong)
- **Real Estate**: 8-15% (low), 15-25% (base), 25-35% (strong)
- **Restaurant**: 10-18% (low), 18-30% (base), 30-45% (strong)
- **Local Services**: 12-20% (low), 20-35% (base), 35-50% (strong)
- **Generic**: 5-10% (low), 10-20% (base), 20-30% (strong)

### Meeting to Revenue Conversion
- Assume 50% of meetings convert to deals
- Average deal value provided as input

### Scenarios
- **Low**: Pessimistic, uses lower end of conversion ranges
- **Base**: Realistic, uses midpoint of ranges
- **Strong**: Optimistic, uses higher end of ranges

## Estimation Formula
Meetings = Leads × Conversion Rate
Revenue = Meetings × 0.5 × Average Deal Value