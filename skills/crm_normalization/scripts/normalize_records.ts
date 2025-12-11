interface RawRecord {
  [key: string]: any;
}

interface NormalizedRecord {
  id: string;
  name: string;
  email: string;
  company?: string;
  industry?: string;
  last_interaction_date?: string;
  interaction_count: number;
  deal_value?: number;
  source?: string;
  phone?: string;
  location?: string;
  notes?: string;
  tags?: string[];
}

const FIELD_MAPPINGS = {
  salesforce: {
    Id: 'id',
    Name: 'name',
    Email: 'email',
    'Account.Name': 'company',
    Industry: 'industry',
    LastActivityDate: 'last_interaction_date',
    NumberOfInteractions__c: 'interaction_count',
    Amount: 'deal_value',
    LeadSource: 'source'
  },
  hubspot: {
    vid: 'id',
    firstname: 'first_name',
    lastname: 'last_name',
    email: 'email',
    company: 'company',
    industry: 'industry',
    lastmodifieddate: 'last_interaction_date',
    num_contacted_notes: 'interaction_count',
    deal_amount: 'deal_value',
    lead_source: 'source'
  },
  pipedrive: {
    id: 'id',
    name: 'name',
    email: 'email',
    org_name: 'company',
    industry: 'industry',
    last_activity_date: 'last_interaction_date',
    activities_count: 'interaction_count',
    value: 'deal_value',
    source: 'source'
  }
};

function mapRecord(record: RawRecord, crmType?: string): NormalizedRecord {
  let mapped: any = {};

  if (crmType && FIELD_MAPPINGS[crmType as keyof typeof FIELD_MAPPINGS]) {
    const mapping = FIELD_MAPPINGS[crmType as keyof typeof FIELD_MAPPINGS];
    for (const [crmField, standardField] of Object.entries(mapping)) {
      if (record[crmField] !== undefined) {
        mapped[standardField] = record[crmField];
      }
    }
  } else {
    // Generic mapping - assume headers match field names
    mapped = { ...record };
  }

  // Handle special cases
  if (mapped.first_name && mapped.last_name) {
    mapped.name = `${mapped.first_name} ${mapped.last_name}`;
    delete mapped.first_name;
    delete mapped.last_name;
  }

  // Ensure required fields
  if (!mapped.id) mapped.id = Math.random().toString(36).substr(2, 9);
  if (!mapped.name) mapped.name = 'Unknown';
  if (!mapped.email) mapped.email = '';
  if (!mapped.interaction_count) mapped.interaction_count = 0;

  // Convert types
  if (mapped.interaction_count) mapped.interaction_count = parseInt(mapped.interaction_count) || 0;
  if (mapped.deal_value) mapped.deal_value = parseFloat(mapped.deal_value) || undefined;

  return mapped as NormalizedRecord;
}

export function normalizeRecords(records: RawRecord[], crmType?: string): NormalizedRecord[] {
  return records.map(record => mapRecord(record, crmType));
}