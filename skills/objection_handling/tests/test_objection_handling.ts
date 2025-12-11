/**
 * Tests for Objection Handling
 */

import {
  handleObjection,
  selectResponseForObjection,
  validateResponse
} from '../scripts/choose_response';

describe('Objection Handling - Response Selection', () => {
  describe('handleObjection', () => {
    it('should generate response for budget objection', () => {
      const result = handleObjection({
        type: 'budget',
        leadTemperature: 'warm',
        industryVertical: 'saas'
      });

      expect(result.message_text).toBeDefined();
      expect(result.message_text.length).toBeGreaterThan(20);
      expect(result.message_text.toLowerCase()).toContain('budget');
      expect(result.tone).toBe('empathetic');
      expect(result.next_step).toBeDefined();
    });

    it('should generate response for timing objection', () => {
      const result = handleObjection({
        type: 'timing',
        leadTemperature: 'hot',
        industryVertical: 'agency'
      });

      expect(result.message_text).toBeDefined();
      expect(result.message_text.toLowerCase()).toMatch(/time|timing|busy|q4/);
      expect(result.objection_addressed).toBe(true);
    });

    it('should generate response for skepticism objection', () => {
      const result = handleObjection({
        type: 'skepticism',
        leadTemperature: 'cold',
        industryVertical: 'local-services'
      });

      expect(result.message_text).toBeDefined();
      expect(result.message_text.toLowerCase()).toMatch(/understand|skeptic|different/);
    });

    it('should generate response for authority objection', () => {
      const result = handleObjection({
        type: 'authority',
        leadTemperature: 'warm'
      });

      expect(result.message_text).toBeDefined();
      expect(result.message_text.toLowerCase()).toMatch(/team|boss|share/);
    });

    it('should generate response for status_quo objection', () => {
      const result = handleObjection({
        type: 'status_quo',
        leadTemperature: 'warm',
        industryVertical: 'saas'
      });

      expect(result.message_text).toBeDefined();
      expect(result.message_text.toLowerCase()).toMatch(/current|process|dormant/);
    });

    it('should generate response for competition objection', () => {
      const result = handleObjection({
        type: 'competition',
        leadTemperature: 'hot'
      });

      expect(result.message_text).toBeDefined();
      expect(result.message_text.toLowerCase()).toMatch(/different|trigger|pilot/);
    });

    it('should generate response for data_privacy objection', () => {
      const result = handleObjection({
        type: 'data_privacy',
        leadTemperature: 'warm'
      });

      expect(result.message_text).toBeDefined();
      expect(result.message_text.toLowerCase()).toMatch(/gdpr|complian|privacy/);
    });
  });

  describe('Tone calibration by lead temperature', () => {
    it('should use more direct tone for hot leads', () => {
      const hotResponse = handleObjection({
        type: 'budget',
        leadTemperature: 'hot',
        industryVertical: 'saas'
      });

      expect(hotResponse.tone).toMatch(/direct|confident/);
      expect(hotResponse.message_text.split(' ').length).toBeLessThan(60); // More concise
    });

    it('should use empathetic tone for cold leads', () => {
      const coldResponse = handleObjection({
        type: 'budget',
        leadTemperature: 'cold',
        industryVertical: 'saas'
      });

      expect(coldResponse.tone).toBe('empathetic');
    });

    it('should use consultative tone for warm leads', () => {
      const warmResponse = handleObjection({
        type: 'budget',
        leadTemperature: 'warm',
        industryVertical: 'agency'
      });

      expect(warmResponse.tone).toMatch(/consultative|empathetic/);
    });
  });

  describe('Industry-specific language', () => {
    it('should use SaaS terminology for SaaS leads', () => {
      const result = handleObjection({
        type: 'budget',
        leadTemperature: 'warm',
        industryVertical: 'saas'
      });

      expect(result.message_text.toLowerCase()).toMatch(/arr|pipeline|saas/);
    });

    it('should use agency terminology for agency leads', () => {
      const result = handleObjection({
        type: 'budget',
        leadTemperature: 'warm',
        industryVertical: 'agency'
      });

      expect(result.message_text.toLowerCase()).toMatch(/project|client|agenc/);
    });

    it('should use local services terminology for HVAC/services leads', () => {
      const result = handleObjection({
        type: 'skepticism',
        leadTemperature: 'cold',
        industryVertical: 'local-services'
      });

      expect(result.message_text.toLowerCase()).toMatch(/job|hvac|home|service/);
    });
  });

  describe('Response validation', () => {
    it('should validate message is under 75 words', () => {
      const response = handleObjection({
        type: 'budget',
        leadTemperature: 'warm',
        industryVertical: 'saas'
      });

      const wordCount = response.message_text.split(/\s+/).length;
      expect(wordCount).toBeLessThanOrEqual(75);
    });

    it('should ensure response follows acknowledge-reframe-reduce framework', () => {
      const response = handleObjection({
        type: 'timing',
        leadTemperature: 'warm'
      });

      const { validation } = validateResponse(response);

      expect(validation.hasAcknowledgment).toBe(true);
      expect(validation.hasReframe).toBe(true);
      expect(validation.hasNextStep).toBe(true);
    });

    it('should not use forbidden phrases', () => {
      const response = handleObjection({
        type: 'skepticism',
        leadTemperature: 'warm'
      });

      const forbiddenPhrases = ['actually', 'but', 'leaving money on the table', 'you should'];
      const lowerMessage = response.message_text.toLowerCase();

      forbiddenPhrases.forEach(phrase => {
        expect(lowerMessage).not.toContain(phrase);
      });
    });
  });

  describe('Alternative responses', () => {
    it('should provide alternative responses', () => {
      const result = handleObjection({
        type: 'budget',
        leadTemperature: 'warm',
        industryVertical: 'saas',
        includeAlternatives: true
      });

      expect(result.alternatives).toBeDefined();
      expect(result.alternatives.length).toBeGreaterThan(0);
      expect(result.alternatives[0].message_text).toBeDefined();
      expect(result.alternatives[0].use_case).toBeDefined();
    });

    it('should not repeat same response in alternatives', () => {
      const result = handleObjection({
        type: 'timing',
        leadTemperature: 'warm',
        includeAlternatives: true
      });

      const mainMessage = result.message_text;
      result.alternatives.forEach(alt => {
        expect(alt.message_text).not.toBe(mainMessage);
      });
    });
  });

  describe('Context-aware selection', () => {
    it('should avoid repeating previous objection approaches', () => {
      const firstResponse = handleObjection({
        type: 'timing',
        leadTemperature: 'warm',
        industryVertical: 'saas'
      });

      const secondResponse = handleObjection({
        type: 'timing',
        leadTemperature: 'warm',
        industryVertical: 'saas',
        previousObjections: [
          {
            type: 'timing',
            response_used: firstResponse.message_text
          }
        ]
      });

      // Should provide different response variant
      expect(secondResponse.message_text).not.toBe(firstResponse.message_text);
    });

    it('should include deal value in response when provided', () => {
      const result = handleObjection({
        type: 'budget',
        leadTemperature: 'warm',
        industryVertical: 'saas',
        dealValue: 50000
      });

      // High deal value should influence response
      expect(result.message_text).toBeDefined();
    });
  });

  describe('Edge cases', () => {
    it('should handle unknown objection type gracefully', () => {
      const result = handleObjection({
        type: 'unknown_objection' as any,
        leadTemperature: 'warm'
      });

      expect(result.message_text).toBeDefined();
      expect(result.objection_addressed).toBe(false);
      expect(result.message_text).toContain('understand');
    });

    it('should handle missing optional fields', () => {
      const result = handleObjection({
        type: 'budget',
        leadTemperature: 'warm'
        // No industry, dealValue, previousObjections
      });

      expect(result.message_text).toBeDefined();
      expect(result.tone).toBeDefined();
      expect(result.next_step).toBeDefined();
    });
  });
});
