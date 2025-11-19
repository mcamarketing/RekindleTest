// API Type Definitions for REKINDLE
// Created: 2025-11-10
// Purpose: Type safety across all API calls

export interface Lead {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  job_title?: string;
  status: 'cold' | 'warm' | 'hot' | 'meeting_booked' | 'campaign_active' | 'unsubscribed';
  lead_score?: number;
  last_contact_date?: string;
  total_messages_sent?: number;
  notes?: string;
  custom_fields?: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
}

export interface Agent {
  id: string;
  user_id?: string;
  name: string;
  type: string;
  status: 'active' | 'paused' | 'error';
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
}

export interface Campaign {
  id: string;
  user_id: string;
  name: string;
  lead_ids: string[];
  message_template: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  created_at: string;
  updated_at?: string;
  settings?: {
    send_schedule?: string;
    max_messages_per_day?: number;
  };
}

export interface AgentMetric {
  id: string;
  agent_id: string;
  metric_type: string;
  value: number;
  recorded_at: string;
}

export interface Task {
  id: string;
  agent_id: string;
  user_id?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  task_type: string;
  payload?: Record<string, unknown>;
  result?: Record<string, unknown>;
  error?: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
}

export interface DashboardStats {
  totalLeads: number;
  hotLeads: number;
  coldLeads: number;
  activeCampaigns: number;
  totalPipelineValue: number;
  potentialRevenue: number;
  meetingRate?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasMore: boolean;
  };
}

export interface AIChatRequest {
  message: string;
  context?: string;
  conversationHistory?: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
}

export interface AIChatResponse {
  response: string;
  context?: string;
}

// Request/Response types for specific endpoints
export interface CreateCampaignRequest {
  name: string;
  lead_ids: string[];
  message_template: string;
  settings?: Campaign['settings'];
}

export interface ImportLeadsRequest {
  leads: Omit<Lead, 'id' | 'user_id' | 'created_at'>[];
  consent_given: boolean;
}

export interface GenerateMessageRequest {
  lead_id: string;
  context?: string;
  template?: string;
}

export interface GenerateMessageResponse {
  message: string;
  lead_id: string;
  personalization_data?: Record<string, unknown>;
}

export interface LeadScoreRequest {
  lead_id: string;
  signals?: {
    linkedin?: boolean;
    company_news?: boolean;
    trigger_events?: boolean;
  };
}

export interface LeadScoreResponse {
  lead_id: string;
  score: number;
  factors: Array<{
    type: string;
    impact: number;
    description: string;
  }>;
}

// User and Auth types
export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  first_name?: string;
  last_name?: string;
  company?: string;
  role?: string;
  subscription_tier?: 'free' | 'starter' | 'pro' | 'enterprise';
  created_at: string;
  updated_at?: string;
}

// Billing types
export interface BillingStatus {
  user_id: string;
  subscription_tier: string;
  monthly_fee: number;
  performance_fees: number;
  total_due: number;
  meetings_booked: number;
  next_billing_date?: string;
}

// Calendar integration types
export interface CalendarIntegration {
  provider: 'google' | 'microsoft';
  connected: boolean;
  connected_at?: string;
  email?: string;
}

export interface CalendarOAuthRequest {
  provider: 'google' | 'microsoft';
  redirect_uri: string;
}

export interface CalendarOAuthCallback {
  code: string;
  state: string;
  provider: 'google' | 'microsoft';
}
