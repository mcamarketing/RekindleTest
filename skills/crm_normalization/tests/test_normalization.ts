/**
 * Tests for CRM Normalization
 */

import {
  normalizeRecord,
  normalizeEmail,
  normalizePhone,
  normalizeCompany,
  mapIndustry,
  calculateQualityScore
} from '../scripts/normalize_records';

describe('CRM Normalization - Field-Level Functions', () => {
  describe('normalizeEmail', () => {
    it('should lowercase and trim email', () => {
      expect(normalizeEmail('  SARAH@EXAMPLE.COM  ')).toBe('sarah@example.com');
    });

    it('should reject role-based emails', () => {
      expect(() => normalizeEmail('info@company.com')).toThrow();
      expect(() => normalizeEmail('noreply@company.com')).toThrow();
      expect(() => normalizeEmail('support@company.com')).toThrow();
    });

    it('should validate email format', () => {
      expect(() => normalizeEmail('invalid-email')).toThrow();
      expect(() => normalizeEmail('missing@')).toThrow();
      expect(() => normalizeEmail('@domain.com')).toThrow();
    });

    it('should accept valid emails', () => {
      expect(normalizeEmail('sarah.chen+test@example.com')).toBe('sarah.chen+test@example.com');
      expect(normalizeEmail('user123@sub.domain.co.uk')).toBe('user123@sub.domain.co.uk');
    });
  });

  describe('normalizePhone', () => {
    it('should convert US phone to E.164 format', () => {
      expect(normalizePhone('(415) 555-1234')).toBe('+14155551234');
      expect(normalizePhone('415-555-1234')).toBe('+14155551234');
      expect(normalizePhone('4155551234')).toBe('+14155551234');
    });

    it('should handle international formats', () => {
      expect(normalizePhone('+44 20 7123 4567')).toBe('+442071234567');
      expect(normalizePhone('+61 2 1234 5678')).toBe('+61212345678');
    });

    it('should assume US country code if not provided', () => {
      expect(normalizePhone('5551234')).toBe('+15551234');
    });

    it('should remove all non-numeric characters except +', () => {
      expect(normalizePhone('(555) 123-4567 ext. 890')).toBe('+15551234567890');
    });
  });

  describe('normalizeCompany', () => {
    it('should remove common suffixes', () => {
      expect(normalizeCompany('Acme Corp, Inc.')).toBe('Acme Corp');
      expect(normalizeCompany('DataPulse LLC')).toBe('DataPulse');
      expect(normalizeCompany('Tech Solutions Ltd')).toBe('Tech Solutions');
    });

    it('should normalize capitalization for deduplication', () => {
      const normalized1 = normalizeCompany('ACME CORP');
      const normalized2 = normalizeCompany('acme corp');
      const normalized3 = normalizeCompany('Acme Corp');

      expect(normalized1.toLowerCase()).toBe(normalized2.toLowerCase());
      expect(normalized2.toLowerCase()).toBe(normalized3.toLowerCase());
    });

    it('should trim whitespace', () => {
      expect(normalizeCompany('  DataPulse  ')).toBe('DataPulse');
    });
  });

  describe('mapIndustry', () => {
    it('should map common variations to saas', () => {
      expect(mapIndustry('Software')).toBe('saas');
      expect(mapIndustry('Technology')).toBe('saas');
      expect(mapIndustry('IT')).toBe('saas');
      expect(mapIndustry('SaaS')).toBe('saas');
    });

    it('should map marketing/advertising to agency', () => {
      expect(mapIndustry('Marketing')).toBe('agency');
      expect(mapIndustry('Advertising')).toBe('agency');
      expect(mapIndustry('Marketing and Advertising')).toBe('agency');
    });

    it('should map real estate variations', () => {
      expect(mapIndustry('Real Estate')).toBe('real-estate');
      expect(mapIndustry('Property Management')).toBe('real-estate');
    });

    it('should map to other for unknown industries', () => {
      expect(mapIndustry('Unknown Industry')).toBe('other');
      expect(mapIndustry('')).toBe('other');
    });

    it('should be case-insensitive', () => {
      expect(mapIndustry('SOFTWARE')).toBe('saas');
      expect(mapIndustry('software')).toBe('saas');
    });
  });

  describe('calculateQualityScore', () => {
    it('should give perfect score for complete record', () => {
      const record = {
        email: 'valid@example.com',
        first_name: 'John',
        last_name: 'Doe',
        company: 'Acme Corp',
        phone: '+14155551234',
        industry: 'saas',
        deal_value: 5000,
        last_interaction_date: '2024-01-01'
      };

      expect(calculateQualityScore(record)).toBe(100);
    });

    it('should deduct points for missing optional fields', () => {
      const record = {
        email: 'valid@example.com',
        first_name: 'John',
        last_name: 'Doe',
        company: 'Acme Corp'
      };

      const score = calculateQualityScore(record);
      expect(score).toBeLessThan(100);
      expect(score).toBeGreaterThanOrEqual(50); // Has required fields
    });

    it('should give low score for missing required fields', () => {
      const record = {
        email: 'valid@example.com'
      };

      const score = calculateQualityScore(record);
      expect(score).toBeLessThan(50);
    });
  });
});

describe('CRM Normalization - Full Record Processing', () => {
  describe('Salesforce normalization', () => {
    it('should correctly normalize Salesforce lead', () => {
      const salesforceLead = {
        Email: 'sarah.chen@DATAPULSE.IO',
        FirstName: 'Sarah',
        LastName: 'Chen',
        Company: 'DataPulse Analytics, Inc.',
        Phone: '(415) 555-1234',
        Industry: 'Software',
        LeadSource: 'Partner Referral'
      };

      const result = normalizeRecord('salesforce', salesforceLead);

      expect(result.canonical_record.email).toBe('sarah.chen@datapulse.io');
      expect(result.canonical_record.first_name).toBe('Sarah');
      expect(result.canonical_record.last_name).toBe('Chen');
      expect(result.canonical_record.company).toBe('DataPulse Analytics');
      expect(result.canonical_record.phone).toBe('+14155551234');
      expect(result.canonical_record.industry).toBe('saas');
      expect(result.canonical_record.lead_source).toBe('referral');
      expect(result.metadata.source_crm).toBe('salesforce');
    });
  });

  describe('HubSpot normalization', () => {
    it('should correctly normalize HubSpot contact', () => {
      const hubspotContact = {
        properties: {
          email: 'marcus@velocity.com',
          firstname: 'Marcus',
          lastname: 'Rivera',
          company: 'Velocity Creative',
          phone: '555-0100',
          industry: 'Marketing and Advertising',
          hs_analytics_source: 'ORGANIC_SEARCH'
        }
      };

      const result = normalizeRecord('hubspot', hubspotContact);

      expect(result.canonical_record.email).toBe('marcus@velocity.com');
      expect(result.canonical_record.first_name).toBe('Marcus');
      expect(result.canonical_record.industry).toBe('agency');
      expect(result.canonical_record.lead_source).toBe('inbound-inquiry');
      expect(result.metadata.source_crm).toBe('hubspot');
    });
  });

  describe('Pipedrive normalization', () => {
    it('should correctly normalize Pipedrive person', () => {
      const pipedrivePerson = {
        name: 'Jennifer Lopez',
        email: [{ value: 'jennifer@coastal.com', primary: true }],
        phone: [{ value: '(858) 555-7890', primary: true }],
        org_id: {
          name: 'Coastal Properties'
        }
      };

      const result = normalizeRecord('pipedrive', pipedrivePerson);

      expect(result.canonical_record.email).toBe('jennifer@coastal.com');
      expect(result.canonical_record.first_name).toBe('Jennifer');
      expect(result.canonical_record.last_name).toBe('Lopez');
      expect(result.canonical_record.company).toBe('Coastal Properties');
      expect(result.canonical_record.phone).toBe('+18585557890');
      expect(result.metadata.source_crm).toBe('pipedrive');
    });
  });

  describe('Error handling', () => {
    it('should throw error for missing required email', () => {
      const invalidRecord = {
        FirstName: 'John',
        LastName: 'Doe',
        Company: 'Acme'
      };

      expect(() => normalizeRecord('salesforce', invalidRecord)).toThrow(/email/i);
    });

    it('should throw error for missing required company', () => {
      const invalidRecord = {
        Email: 'john@example.com',
        FirstName: 'John',
        LastName: 'Doe'
      };

      expect(() => normalizeRecord('salesforce', invalidRecord)).toThrow(/company/i);
    });

    it('should handle invalid phone gracefully with warning', () => {
      const record = {
        Email: 'john@example.com',
        FirstName: 'John',
        LastName: 'Doe',
        Company: 'Acme',
        Phone: 'invalid-phone'
      };

      const result = normalizeRecord('salesforce', record);

      expect(result.canonical_record.phone).toBeNull();
      expect(result.metadata.validation_warnings).toContain('invalid_phone_format');
    });
  });

  describe('Metadata generation', () => {
    it('should include proper metadata', () => {
      const record = {
        Email: 'test@example.com',
        FirstName: 'Test',
        LastName: 'User',
        Company: 'Test Corp'
      };

      const result = normalizeRecord('salesforce', record);

      expect(result.metadata.source_crm).toBe('salesforce');
      expect(result.metadata.normalized_at).toBeDefined();
      expect(result.metadata.quality_score).toBeGreaterThan(0);
      expect(result.metadata.quality_score).toBeLessThanOrEqual(100);
      expect(typeof result.metadata.needs_enrichment).toBe('boolean');
      expect(typeof result.metadata.duplicate_risk).toBe('boolean');
      expect(Array.isArray(result.metadata.validation_warnings)).toBe(true);
    });

    it('should flag records needing enrichment', () => {
      const minimalRecord = {
        Email: 'test@example.com',
        Company: 'Test Corp'
      };

      const result = normalizeRecord('salesforce', minimalRecord);

      expect(result.metadata.needs_enrichment).toBe(true);
      expect(result.metadata.quality_score).toBeLessThan(90);
    });
  });
});
