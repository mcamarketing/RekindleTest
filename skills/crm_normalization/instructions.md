# CRM Normalization Skill

## Purpose
Transform lead/contact data from various CRMs into a canonical Rekindle format. Handles field mapping, data cleaning, and validation to ensure consistent data quality across all sources.

## Supported CRM Systems

### Tier 1 (Full Support)
- Salesforce
- HubSpot
- Pipedrive
- Close.com
- Copper

### Tier 2 (Basic Support)
- Zoho CRM
- Freshsales
- Monday.com
- Generic CSV imports

## Canonical Schema

### Required Fields
- `email` (string, validated format)
- `name` (string, split into first_name + last_name if needed)
- `company` (string)

### Optional Fields
- `phone` (string, normalized to E.164 format)
- `title` (string, cleaned)
- `industry` (string, mapped to standard taxonomy)
- `company_size` (enum: 1-10, 11-50, 51-200, 201-1000, 1000+)
- `deal_value` (number, converted to USD)
- `last_interaction_date` (ISO 8601 datetime)
- `interaction_count` (number)
- `lead_source` (enum, mapped to standard sources)
- `tags` (array of strings, normalized)

## Normalization Rules

### Email
- Convert to lowercase
- Trim whitespace
- Validate RFC 5322 format
- Remove role-based emails (info@, noreply@, etc.)

### Name
- Split "First Last" into first_name and last_name
- Handle "Last, First" format
- Capitalize properly (McDonald, O'Brien, etc.)
- Remove titles (Mr., Dr., etc.)

### Phone
- Remove all non-numeric characters
- Convert to E.164 format (+1XXXXXXXXXX)
- Detect country code or assume US if missing

### Company
- Remove "Inc", "LLC", "Ltd", etc. from name
- Normalize capitalization
- Deduplicate ("Acme Corp" = "ACME CORP" = "acme corp")

### Industry
- Map CRM-specific industry values to Rekindle taxonomy
- Consolidate synonyms ("Tech" = "Technology" = "IT")
- Standard taxonomy: saas, agency, real-estate, restaurant, local-services, ecommerce, finance, healthcare, manufacturing, other

### Company Size
- Map various formats to standard ranges:
  - "Small", "1-10", "<10" → "1-10"
  - "Medium", "50-100" → "51-200"
  - Parse free-text like "about 50 employees"

### Deal Value
- Extract numbers from text ("$10k", "10000 USD")
- Convert currencies to USD using exchange rates
- Validate range (flag suspicious values)

### Lead Source
- Map CRM-specific sources to canonical taxonomy
- Taxonomy: referral, inbound-inquiry, cold-outreach, webinar, event-lead, content-download, partnership, purchased-list, unknown

### Tags
- Convert to lowercase
- Remove special characters
- Consolidate synonyms
- Limit to 10 tags per record

## Data Quality Checks

### Validation Rules
1. Email must be valid format and not role-based
2. Name must have at least 2 characters
3. Company must be provided
4. Phone must be valid if provided
5. Deal value must be positive number if provided
6. Dates must be valid and not in future

### Enrichment Flags
- `needs_enrichment`: missing optional fields
- `low_quality`: missing required fields or validation failures
- `duplicate_risk`: similar to existing record (fuzzy match on email/company/name)

## Field Mapping by CRM

### Salesforce
```
Lead.Email → email
Lead.FirstName + Lead.LastName → name
Lead.Company → company
Lead.Phone → phone
Lead.Title → title
Lead.Industry → industry (mapped)
Lead.NumberOfEmployees → company_size (mapped)
Opportunity.Amount → deal_value
Lead.LastActivityDate → last_interaction_date
Lead.LeadSource → lead_source (mapped)
```

### HubSpot
```
properties.email → email
properties.firstname + properties.lastname → name
properties.company → company
properties.phone → phone
properties.jobtitle → title
properties.industry → industry (mapped)
properties.numberofemployees → company_size (mapped)
associations.deals[0].amount → deal_value
properties.notes_last_updated → last_interaction_date
properties.hs_analytics_source → lead_source (mapped)
```

### Pipedrive
```
email[0].value → email
name → name (split)
org_id.name → company
phone[0].value → phone
org_id.people_count → company_size (mapped)
value → deal_value
update_time → last_interaction_date
```

## Output Format

```json
{
  "canonical_record": {
    "email": "sarah.chen@datapulse.io",
    "first_name": "Sarah",
    "last_name": "Chen",
    "company": "DataPulse Analytics",
    "phone": "+14155551234",
    "title": "VP of Sales",
    "industry": "saas",
    "company_size": "11-50",
    "deal_value": 25000,
    "last_interaction_date": "2024-12-01T10:00:00Z",
    "interaction_count": 8,
    "lead_source": "referral",
    "tags": ["pilot", "high-priority", "q1-2025"]
  },
  "metadata": {
    "source_crm": "salesforce",
    "normalized_at": "2025-01-15T14:30:00Z",
    "quality_score": 95,
    "needs_enrichment": false,
    "duplicate_risk": false,
    "validation_warnings": []
  }
}
```

## Error Handling

### Critical Errors (reject record)
- Missing required field (email, name, company)
- Invalid email format
- Duplicate email in batch

### Warnings (accept with flag)
- Missing optional fields
- Invalid phone format
- Unknown industry/source (map to "other"/"unknown")
- Out-of-range company size (use "unknown")

## Success Criteria
- 95%+ normalization success rate (non-critical errors)
- <200ms per record processing time
- 99%+ email validation accuracy
- Zero data loss on critical fields
