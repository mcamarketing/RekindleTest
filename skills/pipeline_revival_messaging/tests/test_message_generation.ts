/**
 * Tests for Pipeline Revival Message Generation
 */

import {
  generateRevivalMessage,
  generateMessageVariants,
  validateMessage
} from '../scripts/generate_message';

describe('Pipeline Revival Message Generation', () => {
  const mockLeadSaas = {
    name: 'Sarah Chen',
    company: 'DataPulse Analytics',
    businessType: 'saas' as const,
    lastEngagementDate: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000), // 45 days ago
    triggerEvents: [
      {
        type: 'funding' as const,
        description: 'closed Series B ($12M)',
        confidence: 0.95,
        detectedAt: new Date()
      }
    ]
  };

  const mockLeadAgency = {
    name: 'Marcus Rivera',
    company: 'Velocity Creative',
    businessType: 'agency' as const,
    lastEngagementDate: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000), // 120 days ago
    triggerEvents: [
      {
        type: 'hiring' as const,
        description: 'hired Head of Client Success',
        confidence: 0.85,
        detectedAt: new Date()
      }
    ]
  };

  const mockLeadCold = {
    name: 'Jennifer Lopez',
    company: 'Coastal Properties',
    businessType: 'real-estate' as const,
    lastEngagementDate: new Date(Date.now() - 240 * 24 * 60 * 60 * 1000), // 240 days ago
    triggerEvents: [
      {
        type: 'market-change' as const,
        description: 'inventory dropped 35%',
        confidence: 0.78,
        detectedAt: new Date()
      }
    ]
  };

  describe('generateRevivalMessage', () => {
    it('should generate message for hot SaaS lead', () => {
      const message = generateRevivalMessage(mockLeadSaas);

      expect(message.subjectLine).toBeTruthy();
      expect(message.subjectLine.length).toBeGreaterThanOrEqual(20);
      expect(message.subjectLine.length).toBeLessThanOrEqual(60);

      expect(message.fullMessage).toContain('Sarah');
      expect(message.fullMessage).toContain('DataPulse');
      expect(message.metadata.toneCategory).toBe('hot');
      expect(message.metadata.wordCount).toBeGreaterThanOrEqual(50);
      expect(message.metadata.wordCount).toBeLessThanOrEqual(120);
    });

    it('should generate message for warm agency lead', () => {
      const message = generateRevivalMessage(mockLeadAgency);

      expect(message.fullMessage).toContain('Marcus');
      expect(message.fullMessage).toContain('Velocity');
      expect(message.metadata.toneCategory).toBe('warm');
      expect(message.fullMessage.toLowerCase()).toMatch(/minute|while/); // Should acknowledge gap
    });

    it('should generate message for cold real estate lead', () => {
      const message = generateRevivalMessage(mockLeadCold);

      expect(message.fullMessage).toContain('Jennifer');
      expect(message.fullMessage).toContain('Coastal');
      expect(message.metadata.toneCategory).toBe('cold');
      expect(message.metadata.wordCount).toBeGreaterThan(70); // Cold messages slightly longer
    });

    it('should include all required components', () => {
      const message = generateRevivalMessage(mockLeadSaas);

      expect(message.subjectLine).toBeTruthy();
      expect(message.opening).toBeTruthy();
      expect(message.body).toBeTruthy();
      expect(message.cta).toBeTruthy();
      expect(message.fullMessage).toBeTruthy();
      expect(message.metadata).toBeTruthy();
    });

    it('should throw error if no trigger events provided', () => {
      const invalidLead = {
        ...mockLeadSaas,
        triggerEvents: []
      };

      expect(() => generateRevivalMessage(invalidLead)).toThrow(
        'At least one trigger event is required'
      );
    });

    it('should prioritize highest confidence trigger', () => {
      const multiTriggerLead = {
        ...mockLeadSaas,
        triggerEvents: [
          {
            type: 'funding' as const,
            description: 'Series B',
            confidence: 0.6,
            detectedAt: new Date()
          },
          {
            type: 'hiring' as const,
            description: 'hired VP Sales',
            confidence: 0.95,
            detectedAt: new Date()
          }
        ]
      };

      const message = generateRevivalMessage(multiTriggerLead);
      expect(message.metadata.triggerType).toBe('hiring');
    });
  });

  describe('generateMessageVariants', () => {
    it('should generate multiple variants', () => {
      const variants = generateMessageVariants(mockLeadSaas, 3);

      expect(variants).toHaveLength(3);
      variants.forEach(variant => {
        expect(variant.fullMessage).toBeTruthy();
        expect(variant.metadata.toneCategory).toBe('hot');
      });
    });

    it('should generate variants with different content', () => {
      const variants = generateMessageVariants(mockLeadSaas, 3);

      // At least some variants should have different subject lines (due to randomization)
      const uniqueSubjects = new Set(variants.map(v => v.subjectLine));
      expect(uniqueSubjects.size).toBeGreaterThan(0);
    });
  });

  describe('validateMessage', () => {
    it('should validate message within success criteria', () => {
      const message = generateRevivalMessage(mockLeadSaas);
      const validation = validateMessage(message);

      // Should have minimal warnings for well-generated message
      expect(validation.warnings.length).toBeLessThan(2);
    });

    it('should warn if subject line too short', () => {
      const message = generateRevivalMessage(mockLeadSaas);
      message.subjectLine = 'Too short'; // 9 chars

      const validation = validateMessage(message);
      expect(validation.isValid).toBe(false);
      expect(validation.warnings.some(w => w.includes('Subject line length'))).toBe(true);
    });

    it('should warn if word count outside range', () => {
      const message = generateRevivalMessage(mockLeadSaas);
      message.fullMessage = 'This is way too short.';
      message.metadata.wordCount = 5;

      const validation = validateMessage(message);
      expect(validation.isValid).toBe(false);
      expect(validation.warnings.some(w => w.includes('Word count'))).toBe(true);
    });

    it('should warn if readability score too low', () => {
      const message = generateRevivalMessage(mockLeadSaas);
      message.metadata.readabilityScore = 45;

      const validation = validateMessage(message);
      expect(validation.isValid).toBe(false);
      expect(validation.warnings.some(w => w.includes('Readability score'))).toBe(true);
    });

    it('should warn if estimated open rate too low', () => {
      const message = generateRevivalMessage(mockLeadSaas);
      message.metadata.estimatedOpenRate = 25;

      const validation = validateMessage(message);
      expect(validation.isValid).toBe(false);
      expect(validation.warnings.some(w => w.includes('open rate'))).toBe(true);
    });
  });

  describe('Industry-specific adaptations', () => {
    it('should use SaaS-specific language', () => {
      const message = generateRevivalMessage(mockLeadSaas);
      expect(message.fullMessage.toLowerCase()).toMatch(/arr|pipeline|saas/);
    });

    it('should use agency-specific language', () => {
      const message = generateRevivalMessage(mockLeadAgency);
      expect(message.fullMessage.toLowerCase()).toMatch(/project|client|shop/);
    });

    it('should use real estate-specific language', () => {
      const message = generateRevivalMessage(mockLeadCold);
      expect(message.fullMessage.toLowerCase()).toMatch(/market|lead|pipeline/);
    });
  });

  describe('Performance estimates', () => {
    it('should estimate higher performance for hot leads', () => {
      const hotMessage = generateRevivalMessage(mockLeadSaas);
      const coldMessage = generateRevivalMessage(mockLeadCold);

      expect(hotMessage.metadata.estimatedOpenRate).toBeGreaterThan(
        coldMessage.metadata.estimatedOpenRate
      );
      expect(hotMessage.metadata.estimatedResponseRate).toBeGreaterThan(
        coldMessage.metadata.estimatedResponseRate
      );
    });

    it('should estimate higher performance for high-confidence triggers', () => {
      const highConfidenceLead = {
        ...mockLeadSaas,
        triggerEvents: [
          {
            type: 'funding' as const,
            description: 'Series B',
            confidence: 0.95,
            detectedAt: new Date()
          }
        ]
      };

      const lowConfidenceLead = {
        ...mockLeadSaas,
        triggerEvents: [
          {
            type: 'funding' as const,
            description: 'Series B',
            confidence: 0.5,
            detectedAt: new Date()
          }
        ]
      };

      const highConfMessage = generateRevivalMessage(highConfidenceLead);
      const lowConfMessage = generateRevivalMessage(lowConfidenceLead);

      expect(highConfMessage.metadata.estimatedOpenRate).toBeGreaterThan(
        lowConfMessage.metadata.estimatedOpenRate
      );
    });
  });
});
