# CRM Normalization Skill

Transform lead/contact data from various CRMs (Salesforce, HubSpot, Pipedrive, etc.) into a canonical Rekindle format with validation, cleaning, and enrichment flags.

## What This Skill Does

- **Field Mapping**: Maps CRM-specific fields to canonical schema
- **Data Cleaning**: Normalizes emails, phones, names, companies
- **Validation**: Checks data quality and flags issues
- **Enrichment Detection**: Identifies records needing additional data
- **Deduplication**: Flags potential duplicates

## Quick Start

```typescript
import { normalizeRecord } from './scripts/normalize_records';

const salesforceRecord = {
  Email: 'sarah.chen@DATAPULSE.IO',
  FirstName: 'Sarah',
  LastName: 'Chen',
  Company: 'DataPulse Analytics, Inc.',
  Phone: '(415) 555-1234',
  Industry: 'Software',
  LeadSource: 'Partner Referral'
};

const result = normalizeRecord('salesforce', salesforceRecord);

console.log(result.canonical_record);
// {
//   email: 'sarah.chen@datapulse.io',
//   first_name: 'Sarah',
//   last_name: 'Chen',
//   company: 'DataPulse Analytics',
//   phone: '+14155551234',
//   industry: 'saas',
//   lead_source: 'referral'
// }

console.log(result.metadata.quality_score); // 95
```

## Supported CRMs

### Tier 1 (Full Field Mapping)
- Salesforce
- HubSpot
- Pipedrive
- Close.com
- Copper CRM

### Tier 2 (Basic Mapping)
- Zoho CRM
- Freshsales
- Monday.com
- Generic CSV imports

## Canonical Schema

### Required Fields
- `email`: Validated email address (lowercase, trimmed)
- `name` or `first_name + last_name`: Contact name
- `company`: Company name (cleaned)

### Optional Fields
- `phone`: E.164 format (+1XXXXXXXXXX)
- `title`: Job title
- `industry`: Mapped to taxonomy (saas, agency, real-estate, etc.)
- `company_size`: Standardized ranges (1-10, 11-50, 51-200, 201-1000, 1000+)
- `deal_value`: Number in USD
- `last_interaction_date`: ISO 8601 datetime
- `interaction_count`: Number of interactions
- `lead_source`: Mapped to taxonomy (referral, inbound-inquiry, cold-outreach, etc.)
- `tags`: Array of normalized strings

## Normalization Rules

### Email Normalization
```typescript
// Input: "Sarah.CHEN@DataPulse.IO  "
// Output: "sarah.chen@datapulse.io"

// Rejects:
// - info@company.com (role-based)
// - invalid@format (malformed)
```

### Phone Normalization
```typescript
// Input: "(415) 555-1234"
// Output: "+14155551234"

// Input: "555-1234" (assumes US)
// Output: "+15551234"
```

### Company Normalization
```typescript
// Input: "DataPulse Analytics, Inc."
// Output: "DataPulse Analytics"

// Deduplicates:
// "ACME CORP" = "acme corp" = "Acme Corp"
```

### Industry Mapping
```typescript
// Salesforce "Software" → "saas"
// HubSpot "Technology" → "saas"
// HubSpot "Marketing Agency" → "agency"
// Custom "IT Services" → "saas"
```

## Data Quality Scoring

Quality score (0-100) based on:
- **Required fields present**: +50 points
- **Email valid**: +20 points
- **Phone valid**: +10 points
- **Industry mapped**: +10 points
- **Deal value present**: +5 points
- **Last interaction date present**: +5 points

**Thresholds**:
- 90-100: Excellent
- 70-89: Good
- 50-69: Fair (needs enrichment)
- <50: Poor (manual review recommended)

## Integration

This skill integrates with:
- Lead import pipelines
- CRM sync jobs
- Data enrichment services
- Deduplication engines

## Files Structure

```
crm_normalization/
├── README.md
├── instructions.md           # Full normalization rules
├── config.json              # Skill metadata
├── scripts/
│   └── normalize_records.ts # Normalization implementation
├── examples/
│   ├── salesforce-mapping.json
│   ├── hubspot-mapping.json
│   └── pipedrive-mapping.json
└── tests/
    └── test_normalization.ts
```

## Usage Examples

### Example 1: Salesforce Lead
```typescript
const salesforceLead = {
  Email: 'marcus@velocity.com',
  FirstName: 'Marcus',
  LastName: 'Rivera',
  Company: 'Velocity Creative Group, LLC',
  Phone: '555-0100',
  Title: 'Creative Director',
  Industry: 'Marketing and Advertising',
  NumberOfEmployees: '25',
  LeadSource: 'Web',
  LastActivityDate: '2024-09-15'
};

const normalized = normalizeRecord('salesforce', salesforceLead);
// Output: canonical record with industry='agency', company_size='11-50'
```

### Example 2: HubSpot Contact
```typescript
const hubspotContact = {
  properties: {
    email: 'john@ACME.COM',
    firstname: 'John',
    lastname: 'Smith',
    company: 'ACME CORP',
    phone: '(212) 555-9999',
    jobtitle: 'CEO',
    industry: 'Real Estate',
    hs_analytics_source: 'ORGANIC_SEARCH'
  }
};

const normalized = normalizeRecord('hubspot', hubspotContact);
// Output: email='john@acme.com', company='ACME', industry='real-estate',
//         lead_source='inbound-inquiry'
```

### Example 3: CSV Import
```typescript
const csvRow = {
  'Email Address': 'sarah@test.com',
  'Full Name': 'Sarah Chen',
  'Company Name': 'DataPulse',
  'Phone Number': '4155551234'
};

const normalized = normalizeRecord('csv', csvRow, {
  field_mapping: {
    'Email Address': 'email',
    'Full Name': 'name',
    'Company Name': 'company',
    'Phone Number': 'phone'
  }
});
```

## Error Handling

### Critical Errors (Record Rejected)
- Missing email
- Invalid email format
- Missing company name
- Duplicate email in current batch

### Warnings (Record Accepted with Flags)
- Missing phone or invalid format
- Unknown industry (mapped to "other")
- Missing deal value
- Out-of-range dates

## Success Metrics

- **Normalization Success Rate**: >95%
- **Processing Speed**: <200ms per record
- **Email Validation Accuracy**: >99%
- **Zero Data Loss**: On critical fields (email, name, company)

## Configuration

See `config.json` for:
- Supported CRM systems
- Required and optional fields
- Output schema
- Performance targets

## Maintenance

**Version**: 1.0.0
**Owners**: data_team, platform_team
**Last Updated**: 2025-01-15

For new CRM integrations or field mappings, contact the Data team.
