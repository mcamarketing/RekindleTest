/**
 * Tests for Dormant Lead Analysis Scoring
 */

import { scoreAndSegmentLead, calculateRecencyScore, calculateFrequencyScore, calculateValueScore, calculateSourceScore } from '../scripts/score_leads';

describe('Dormant Lead Analysis - Scoring Functions', () => {
  describe('calculateRecencyScore', () => {
    it('should return 3 for interactions within 30 days', () => {
      const date = new Date(Date.now() - 15 * 24 * 60 * 60 * 1000); // 15 days ago
      expect(calculateRecencyScore(date)).toBe(3);
    });

    it('should return 2 for interactions 31-90 days ago', () => {
      const date = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000); // 60 days ago
      expect(calculateRecencyScore(date)).toBe(2);
    });

    it('should return 1 for interactions over 90 days ago', () => {
      const date = new Date(Date.now() - 180 * 24 * 60 * 60 * 1000); // 180 days ago
      expect(calculateRecencyScore(date)).toBe(1);
    });

    it('should handle edge case at 30 days exactly', () => {
      const date = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
      expect(calculateRecencyScore(date)).toBe(3);
    });

    it('should handle edge case at 90 days exactly', () => {
      const date = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
      expect(calculateRecencyScore(date)).toBe(2);
    });
  });

  describe('calculateFrequencyScore', () => {
    it('should return 3 for 5+ interactions', () => {
      expect(calculateFrequencyScore(5)).toBe(3);
      expect(calculateFrequencyScore(10)).toBe(3);
    });

    it('should return 2 for 2-4 interactions', () => {
      expect(calculateFrequencyScore(2)).toBe(2);
      expect(calculateFrequencyScore(3)).toBe(2);
      expect(calculateFrequencyScore(4)).toBe(2);
    });

    it('should return 1 for 0-1 interactions', () => {
      expect(calculateFrequencyScore(0)).toBe(1);
      expect(calculateFrequencyScore(1)).toBe(1);
    });
  });

  describe('calculateValueScore', () => {
    it('should return 3 for values over $10,000', () => {
      expect(calculateValueScore(10001)).toBe(3);
      expect(calculateValueScore(50000)).toBe(3);
    });

    it('should return 2 for values $1,000-$10,000', () => {
      expect(calculateValueScore(1000)).toBe(2);
      expect(calculateValueScore(5000)).toBe(2);
      expect(calculateValueScore(10000)).toBe(2);
    });

    it('should return 1 for values under $1,000', () => {
      expect(calculateValueScore(500)).toBe(1);
      expect(calculateValueScore(999)).toBe(1);
    });

    it('should return 1 for unknown/null values', () => {
      expect(calculateValueScore(0)).toBe(1);
      expect(calculateValueScore(null as any)).toBe(1);
      expect(calculateValueScore(undefined as any)).toBe(1);
    });
  });

  describe('calculateSourceScore', () => {
    it('should return 3 for high-quality sources', () => {
      expect(calculateSourceScore('referral')).toBe(3);
      expect(calculateSourceScore('inbound-inquiry')).toBe(3);
      expect(calculateSourceScore('webinar')).toBe(3);
      expect(calculateSourceScore('partnership')).toBe(3);
    });

    it('should return 2 for medium-quality sources', () => {
      expect(calculateSourceScore('cold-outreach')).toBe(2);
      expect(calculateSourceScore('event-lead')).toBe(2);
      expect(calculateSourceScore('content-download')).toBe(2);
    });

    it('should return 1 for low-quality sources', () => {
      expect(calculateSourceScore('purchased-list')).toBe(1);
      expect(calculateSourceScore('scraping')).toBe(1);
      expect(calculateSourceScore('unknown')).toBe(1);
    });

    it('should be case-insensitive', () => {
      expect(calculateSourceScore('REFERRAL')).toBe(3);
      expect(calculateSourceScore('Webinar')).toBe(3);
    });
  });

  describe('scoreAndSegmentLead', () => {
    it('should correctly score and segment high-priority lead', () => {
      const lead = {
        lastInteractionDate: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000), // 15 days ago
        interactionCount: 8,
        estimatedDealValue: 25000,
        leadSource: 'referral'
      };

      const result = scoreAndSegmentLead(lead);

      expect(result.recencyScore).toBe(3);
      expect(result.frequencyScore).toBe(3);
      expect(result.valueScore).toBe(3);
      expect(result.sourceScore).toBe(3);
      expect(result.totalScore).toBe(12);
      expect(result.segment).toBe('high');
      expect(result.revivalPriority).toBeGreaterThan(90);
    });

    it('should correctly score and segment medium-priority lead', () => {
      const lead = {
        lastInteractionDate: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000), // 60 days ago
        interactionCount: 3,
        estimatedDealValue: 5000,
        leadSource: 'content-download'
      };

      const result = scoreAndSegmentLead(lead);

      expect(result.totalScore).toBe(8);
      expect(result.segment).toBe('medium');
      expect(result.revivalPriority).toBeGreaterThanOrEqual(50);
      expect(result.revivalPriority).toBeLessThan(90);
    });

    it('should correctly score and segment low-priority lead', () => {
      const lead = {
        lastInteractionDate: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000), // 180 days ago
        interactionCount: 1,
        estimatedDealValue: 800,
        leadSource: 'purchased-list'
      };

      const result = scoreAndSegmentLead(lead);

      expect(result.totalScore).toBe(4);
      expect(result.segment).toBe('low');
      expect(result.revivalPriority).toBeLessThan(50);
    });

    it('should provide appropriate recommended approach for each segment', () => {
      const highLead = {
        lastInteractionDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
        interactionCount: 7,
        estimatedDealValue: 15000,
        leadSource: 'inbound-inquiry'
      };

      const mediumLead = {
        lastInteractionDate: new Date(Date.now() - 75 * 24 * 60 * 60 * 1000),
        interactionCount: 3,
        estimatedDealValue: 5000,
        leadSource: 'event-lead'
      };

      const lowLead = {
        lastInteractionDate: new Date(Date.now() - 200 * 24 * 60 * 60 * 1000),
        interactionCount: 1,
        estimatedDealValue: 500,
        leadSource: 'unknown'
      };

      expect(scoreAndSegmentLead(highLead).recommendedApproach).toContain('Immediate');
      expect(scoreAndSegmentLead(mediumLead).recommendedApproach).toContain('Trigger');
      expect(scoreAndSegmentLead(lowLead).recommendedApproach).toContain('bulk');
    });

    it('should calculate revival priority as percentage of max score', () => {
      const perfectLead = {
        lastInteractionDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
        interactionCount: 10,
        estimatedDealValue: 50000,
        leadSource: 'referral'
      };

      const result = scoreAndSegmentLead(perfectLead);
      expect(result.totalScore).toBe(12);
      expect(result.revivalPriority).toBe(100); // 12/12 * 100
    });

    it('should handle edge cases gracefully', () => {
      const edgeCase = {
        lastInteractionDate: new Date(Date.now()),
        interactionCount: 0,
        estimatedDealValue: 0,
        leadSource: ''
      };

      const result = scoreAndSegmentLead(edgeCase);
      expect(result.totalScore).toBeGreaterThanOrEqual(4); // At least minimum score
      expect(result.segment).toBeDefined();
      expect(result.recommendedApproach).toBeDefined();
    });
  });

  describe('Segmentation boundaries', () => {
    it('should segment score 10 as high', () => {
      const lead = {
        lastInteractionDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
        interactionCount: 6,
        estimatedDealValue: 12000,
        leadSource: 'webinar'
      };
      expect(scoreAndSegmentLead(lead).segment).toBe('high');
    });

    it('should segment score 9 as medium', () => {
      const lead = {
        lastInteractionDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
        interactionCount: 4,
        estimatedDealValue: 12000,
        leadSource: 'webinar'
      };
      expect(scoreAndSegmentLead(lead).segment).toBe('medium');
    });

    it('should segment score 5 as low', () => {
      const lead = {
        lastInteractionDate: new Date(Date.now() - 100 * 24 * 60 * 60 * 1000),
        interactionCount: 2,
        estimatedDealValue: 8000,
        leadSource: 'unknown'
      };
      expect(scoreAndSegmentLead(lead).segment).toBe('low');
    });
  });
});
