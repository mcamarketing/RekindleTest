# Dormant Lead Analysis

## Purpose
This skill provides a framework for segmenting and scoring dormant leads to prioritize revival efforts. It evaluates leads based on recency, frequency, value, and source to determine their revival potential.

## Thinking About Recency, Frequency, Value, and Source

### Recency
- **High**: Interacted within last 30 days
- **Medium**: 31-90 days ago
- **Low**: Over 90 days ago

### Frequency
- **High**: 5+ interactions (emails, calls, meetings)
- **Medium**: 2-4 interactions
- **Low**: 1 interaction or less

### Value
- **High**: Deal value >$10,000 or high-value industry
- **Medium**: $1,000-$10,000
- **Low**: <$1,000 or unknown

### Source
- **High**: Referred, inbound inquiry, webinar attendee
- **Medium**: Cold outreach, event lead
- **Low**: Purchased list, unknown

## Ranking Leads: High, Medium, Low Chance of Revival

### High Chance
- Recency: High + Frequency: High + Value: High/Medium + Source: High/Medium
- Or Recency: High + Value: High + Source: High
- Score threshold: 8-10

### Medium Chance
- Balanced mix: e.g., Recency: Medium + Frequency: Medium + Value: Medium
- Or strong in one area compensating for others
- Score threshold: 5-7

### Low Chance
- Recency: Low + Frequency: Low + Value: Low
- Or very old leads with minimal engagement
- Score threshold: 1-4

## Scoring Algorithm
Assign points:
- Recency: High=3, Medium=2, Low=1
- Frequency: High=3, Medium=2, Low=1
- Value: High=3, Medium=2, Low=1
- Source: High=3, Medium=2, Low=1

Total score = sum of all factors.

Map to segments:
- 10-12: High
- 6-9: Medium
- 1-5: Low