/**
 * Tests for ROI Estimation Calculations
 */

import { estimateROI, getConversionRates, calculateScenario } from '../scripts/calc_roi';

describe('ROI Estimation - Calculation Functions', () => {
  describe('getConversionRates', () => {
    it('should return correct rates for SaaS industry', () => {
      const rates = getConversionRates('saas');
      expect(rates.low).toBe(0.05);
      expect(rates.base).toBe(0.11);
      expect(rates.strong).toBe(0.20);
    });

    it('should return correct rates for Agency industry', () => {
      const rates = getConversionRates('agency');
      expect(rates.low).toBe(0.075);
      expect(rates.base).toBe(0.15);
      expect(rates.strong).toBe(0.25);
    });

    it('should return correct rates for Real Estate industry', () => {
      const rates = getConversionRates('real-estate');
      expect(rates.low).toBe(0.115);
      expect(rates.base).toBe(0.20);
      expect(rates.strong).toBe(0.30);
    });

    it('should return correct rates for Restaurant industry', () => {
      const rates = getConversionRates('restaurant');
      expect(rates.low).toBe(0.14);
      expect(rates.base).toBe(0.24);
      expect(rates.strong).toBe(0.375);
    });

    it('should return correct rates for Local Services industry', () => {
      const rates = getConversionRates('local-services');
      expect(rates.low).toBe(0.16);
      expect(rates.base).toBe(0.275);
      expect(rates.strong).toBe(0.425);
    });

    it('should return generic rates for unknown industry', () => {
      const rates = getConversionRates('unknown-industry');
      expect(rates.low).toBe(0.075);
      expect(rates.base).toBe(0.15);
      expect(rates.strong).toBe(0.25);
    });

    it('should handle case-insensitive industry names', () => {
      const ratesUpper = getConversionRates('SAAS');
      const ratesLower = getConversionRates('saas');
      expect(ratesUpper).toEqual(ratesLower);
    });
  });

  describe('calculateScenario', () => {
    it('should correctly calculate meetings and revenue', () => {
      const result = calculateScenario(1000, 0.10, 5000);

      expect(result.estimatedMeetings).toBe(100);
      expect(result.estimatedDeals).toBe(50); // 50% of meetings
      expect(result.estimatedRevenue).toBe(250000); // 50 deals * $5000
    });

    it('should calculate ROI multiple when campaign cost provided', () => {
      const result = calculateScenario(1000, 0.10, 5000, 5000);

      expect(result.roiMultiple).toBe(50); // $250K revenue / $5K cost
    });

    it('should not calculate ROI multiple when cost not provided', () => {
      const result = calculateScenario(1000, 0.10, 5000);

      expect(result.roiMultiple).toBeUndefined();
    });

    it('should handle zero conversion rate', () => {
      const result = calculateScenario(1000, 0, 5000);

      expect(result.estimatedMeetings).toBe(0);
      expect(result.estimatedDeals).toBe(0);
      expect(result.estimatedRevenue).toBe(0);
    });

    it('should handle fractional meetings correctly', () => {
      const result = calculateScenario(100, 0.055, 5000);

      expect(result.estimatedMeetings).toBe(6); // 5.5 rounded up
      expect(result.estimatedDeals).toBe(3); // 50% of 6 rounded down
    });
  });

  describe('estimateROI - Full Integration', () => {
    it('should calculate all three scenarios for SaaS campaign', () => {
      const result = estimateROI({
        leadCount: 1000,
        industryVertical: 'saas',
        averageDealValue: 8000,
        campaignCost: 5000
      });

      // Low scenario (5% conversion)
      expect(result.low.conversionRate).toBe(0.05);
      expect(result.low.estimatedMeetings).toBe(50);
      expect(result.low.estimatedDeals).toBe(25);
      expect(result.low.estimatedRevenue).toBe(200000);
      expect(result.low.roiMultiple).toBe(40);

      // Base scenario (11% conversion)
      expect(result.base.conversionRate).toBe(0.11);
      expect(result.base.estimatedMeetings).toBe(110);
      expect(result.base.estimatedDeals).toBe(55);
      expect(result.base.estimatedRevenue).toBe(440000);
      expect(result.base.roiMultiple).toBe(88);

      // Strong scenario (20% conversion)
      expect(result.strong.conversionRate).toBe(0.20);
      expect(result.strong.estimatedMeetings).toBe(200);
      expect(result.strong.estimatedDeals).toBe(100);
      expect(result.strong.estimatedRevenue).toBe(800000);
      expect(result.strong.roiMultiple).toBe(160);
    });

    it('should provide recommendation based on base scenario', () => {
      const result = estimateROI({
        leadCount: 500,
        industryVertical: 'agency',
        averageDealValue: 5000,
        campaignCost: 3000
      });

      expect(result.recommendation).toBeDefined();
      expect(result.recommendation).toContain('ROI');
      expect(result.recommendation.length).toBeGreaterThan(20);
    });

    it('should work without campaign cost', () => {
      const result = estimateROI({
        leadCount: 1000,
        industryVertical: 'real-estate',
        averageDealValue: 10000
      });

      expect(result.base.estimatedRevenue).toBeGreaterThan(0);
      expect(result.base.roiMultiple).toBeUndefined();
      expect(result.low.roiMultiple).toBeUndefined();
      expect(result.strong.roiMultiple).toBeUndefined();
    });

    it('should handle local services with high conversion rates', () => {
      const result = estimateROI({
        leadCount: 2000,
        industryVertical: 'local-services',
        averageDealValue: 1200,
        campaignCost: 8000
      });

      // Local services should have higher conversion rates
      expect(result.base.conversionRate).toBeGreaterThan(0.25);
      expect(result.strong.conversionRate).toBeGreaterThan(0.40);

      // Should generate significant revenue even with lower deal value
      expect(result.base.estimatedRevenue).toBeGreaterThan(300000);
    });

    it('should show proper scenario progression (low < base < strong)', () => {
      const result = estimateROI({
        leadCount: 1000,
        industryVertical: 'saas',
        averageDealValue: 5000
      });

      expect(result.low.estimatedRevenue).toBeLessThan(result.base.estimatedRevenue);
      expect(result.base.estimatedRevenue).toBeLessThan(result.strong.estimatedRevenue);

      expect(result.low.estimatedMeetings).toBeLessThan(result.base.estimatedMeetings);
      expect(result.base.estimatedMeetings).toBeLessThan(result.strong.estimatedMeetings);
    });

    it('should handle small campaigns realistically', () => {
      const result = estimateROI({
        leadCount: 50,
        industryVertical: 'saas',
        averageDealValue: 10000,
        campaignCost: 500
      });

      // Even with small lead count, should produce reasonable estimates
      expect(result.base.estimatedMeetings).toBeGreaterThan(0);
      expect(result.base.estimatedMeetings).toBeLessThan(50);
      expect(result.base.estimatedRevenue).toBeGreaterThan(0);
    });

    it('should handle large campaigns', () => {
      const result = estimateROI({
        leadCount: 10000,
        industryVertical: 'restaurant',
        averageDealValue: 800,
        campaignCost: 15000
      });

      expect(result.base.estimatedMeetings).toBeGreaterThan(1000);
      expect(result.base.estimatedRevenue).toBeGreaterThan(500000);
    });
  });

  describe('Edge cases and validation', () => {
    it('should handle zero leads gracefully', () => {
      const result = estimateROI({
        leadCount: 0,
        industryVertical: 'saas',
        averageDealValue: 5000
      });

      expect(result.base.estimatedMeetings).toBe(0);
      expect(result.base.estimatedRevenue).toBe(0);
    });

    it('should handle zero average deal value', () => {
      const result = estimateROI({
        leadCount: 1000,
        industryVertical: 'saas',
        averageDealValue: 0
      });

      expect(result.base.estimatedRevenue).toBe(0);
    });

    it('should handle negative campaign cost as zero', () => {
      const result = estimateROI({
        leadCount: 1000,
        industryVertical: 'saas',
        averageDealValue: 5000,
        campaignCost: -1000
      });

      expect(result.base.roiMultiple).toBeUndefined();
    });
  });
});
