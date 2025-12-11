interface ROIInput {
  numberOfLeads: number;
  averageDealValue: number;
  businessType: 'agency' | 'saas' | 'real_estate' | 'restaurant' | 'local_services' | 'generic';
}

interface ROIOutput {
  low: { meetings: number; revenue: number };
  base: { meetings: number; revenue: number };
  strong: { meetings: number; revenue: number };
}

const conversionRanges: Record<string, { low: number; base: number; strong: number }> = {
  agency: { low: 0.05, base: 0.15, strong: 0.25 },
  saas: { low: 0.03, base: 0.11, strong: 0.20 },
  real_estate: { low: 0.08, base: 0.20, strong: 0.30 },
  restaurant: { low: 0.10, base: 0.24, strong: 0.375 },
  local_services: { low: 0.12, base: 0.275, strong: 0.425 },
  generic: { low: 0.05, base: 0.15, strong: 0.25 }
};

const MEETING_TO_REVENUE_CONVERSION = 0.5;

export function calcROI(input: ROIInput): ROIOutput {
  const { numberOfLeads, averageDealValue, businessType } = input;
  const ranges = conversionRanges[businessType] || conversionRanges.generic;

  const lowMeetings = Math.round(numberOfLeads * ranges.low);
  const baseMeetings = Math.round(numberOfLeads * ranges.base);
  const strongMeetings = Math.round(numberOfLeads * ranges.strong);

  const lowRevenue = Math.round(lowMeetings * MEETING_TO_REVENUE_CONVERSION * averageDealValue);
  const baseRevenue = Math.round(baseMeetings * MEETING_TO_REVENUE_CONVERSION * averageDealValue);
  const strongRevenue = Math.round(strongMeetings * MEETING_TO_REVENUE_CONVERSION * averageDealValue);

  return {
    low: { meetings: lowMeetings, revenue: lowRevenue },
    base: { meetings: baseMeetings, revenue: baseRevenue },
    strong: { meetings: strongMeetings, revenue: strongRevenue }
  };
}