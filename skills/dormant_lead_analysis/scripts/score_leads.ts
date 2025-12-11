interface Lead {
  id: string;
  name: string;
  lastInteractionDays: number;
  interactionCount: number;
  dealValue?: number;
  source: string;
}

interface ScoredLead extends Lead {
  score: number;
  segment: 'high' | 'medium' | 'low';
}

function scoreRecency(days: number): number {
  if (days <= 30) return 3;
  if (days <= 90) return 2;
  return 1;
}

function scoreFrequency(count: number): number {
  if (count >= 5) return 3;
  if (count >= 2) return 2;
  return 1;
}

function scoreValue(value?: number): number {
  if (!value) return 1;
  if (value > 10000) return 3;
  if (value >= 1000) return 2;
  return 1;
}

function scoreSource(source: string): number {
  const highSources = ['referred', 'inbound', 'webinar'];
  const mediumSources = ['cold_outreach', 'event'];
  if (highSources.includes(source.toLowerCase())) return 3;
  if (mediumSources.includes(source.toLowerCase())) return 2;
  return 1;
}

function getSegment(score: number): 'high' | 'medium' | 'low' {
  if (score >= 10) return 'high';
  if (score >= 6) return 'medium';
  return 'low';
}

export function scoreLeads(leads: Lead[]): ScoredLead[] {
  return leads.map(lead => {
    const recencyScore = scoreRecency(lead.lastInteractionDays);
    const frequencyScore = scoreFrequency(lead.interactionCount);
    const valueScore = scoreValue(lead.dealValue);
    const sourceScore = scoreSource(lead.source);

    const totalScore = recencyScore + frequencyScore + valueScore + sourceScore;

    return {
      ...lead,
      score: totalScore,
      segment: getSegment(totalScore)
    };
  });
}