/**
 * Comprehensive Type Definitions for Rekindle
 * Full type safety - NO 'any' types allowed
 */

// Base Entity
export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

// User & Auth
export interface User extends BaseEntity {
  email: string;
  role?: string;
  last_sign_in_at?: string;
}

export interface Profile extends BaseEntity {
  id: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  email?: string;
  avatar_url?: string;
  company?: string;
  role?: string;
}

export interface AuthContext {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, fullName?: string) => Promise<void>;
  signOut: () => Promise<void>;
}

// AI Agent System
export interface Agent extends BaseEntity {
  name: string;
  agent_type: AgentType;
  description: string;
  status: AgentStatus;
  capabilities: string[];
  last_heartbeat?: string;
  version?: string;
}

export type AgentType =
  | 'research'
  | 'content'
  | 'safety'
  | 'revenue'
  | 'analytics'
  | 'optimization'
  | 'orchestration'
  | 'intelligence'
  | 'infrastructure'
  | 'specialized'
  | 'sync';

export type AgentStatus = 'active' | 'idle' | 'error' | 'maintenance';

export interface AgentMetric extends BaseEntity {
  agent_id: string;
  cpu_usage: number;
  memory_usage: number;
  response_time: number;
  error_count: number;
  tasks_completed: number;
  recorded_at: string;
  active_tasks?: number;
  completed_tasks?: number;
}

export interface AgentTask extends BaseEntity {
  agent_id: string;
  campaign_id?: string;
  lead_id?: string;
  task_type: string;
  status: TaskStatus;
  priority: TaskPriority;
  input_data?: Record<string, unknown>;
  output_data?: Record<string, unknown>;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
}

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

// Leads
export interface Lead extends BaseEntity {
  user_id: string;
  email: string;
  name?: string;
  company?: string;
  phone?: string;
  status: LeadStatus;
  lead_score: number;
  source?: string;
  custom_fields?: Record<string, unknown>;
  last_contacted_at?: string;
  notes?: string;
}

export type LeadStatus =
  | 'new'
  | 'contacted'
  | 'responded'
  | 'qualified'
  | 'converted'
  | 'unqualified'
  | 'bounced';

// Campaigns
export interface Campaign extends BaseEntity {
  user_id: string;
  name: string;
  description?: string;
  status: CampaignStatus;
  channels: CampaignChannel[];
  message_template?: string;
  subject_line?: string;
  start_date?: string;
  end_date?: string;
  target_lead_ids?: string[];
}

export type CampaignStatus =
  | 'draft'
  | 'active'
  | 'paused'
  | 'completed'
  | 'archived';

export type CampaignChannel = 'email' | 'sms' | 'whatsapp' | 'push';

export interface CampaignLead extends BaseEntity {
  campaign_id: string;
  lead_id: string;
  status: CampaignLeadStatus;
  messages_sent: number;
  messages_opened: number;
  messages_replied: number;
  next_message_scheduled_at?: string;
  last_message_sent_at?: string;
}

export type CampaignLeadStatus =
  | 'pending'
  | 'active'
  | 'paused'
  | 'completed'
  | 'replied'
  | 'bounced'
  | 'unsubscribed';

export interface CampaignStats {
  totalLeads: number;
  activeLeads: number;
  completedLeads: number;
  repliedLeads: number;
  messagesSent: number;
  messagesOpened: number;
  messagesClicked: number;
  messagesReplied: number;
  openRate: number;
  replyRate: number;
}

// Messages
export interface Message extends BaseEntity {
  campaign_id: string;
  lead_id: string;
  subject?: string;
  body: string;
  channel: CampaignChannel;
  status: MessageStatus;
  sent_at?: string;
  delivered_at?: string;
  opened_at?: string;
  clicked_at?: string;
  replied_at?: string;
  open_count: number;
  click_count: number;
  error_message?: string;
}

export type MessageStatus =
  | 'draft'
  | 'scheduled'
  | 'sending'
  | 'sent'
  | 'delivered'
  | 'opened'
  | 'clicked'
  | 'replied'
  | 'bounced'
  | 'failed';

// AI Chat
export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: Date;
  type?: MessageType;
  metadata?: ChatMetadata;
}

export type ChatRole = 'user' | 'assistant' | 'system';
export type MessageType = 'text' | 'insight' | 'suggestion' | 'alert';

export interface ChatMetadata {
  icon?: React.ReactNode;
  actionable?: boolean;
  priority?: 'low' | 'medium' | 'high';
}

export interface ChatContext {
  userId: string;
  purpose: string;
  userName?: string | null;
  leadCount?: number;
  campaignCount?: number;
  recentActivity?: string[];
}

export interface ChatRequest {
  message: string;
  context?: ChatContext;
  conversationHistory?: Array<{
    role: ChatRole;
    content: string;
  }>;
}

export interface ChatResponse {
  success: boolean;
  data?: {
    response: string;
  };
  error?: string;
  timeout?: boolean;
}

// API Responses
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    hasMore: boolean;
  };
}

// Dashboard & Analytics
export interface DashboardStats {
  totalLeads: number;
  activeCampaigns: number;
  responseRate: number;
  meetingsBooked: number;
  totalACV: number;
  potentialRevenue: number;
  hotLeads: number;
  coldLeads: number;
}

export interface AnalyticsMetric {
  timestamp: string;
  value: number;
  label?: string;
}

export interface AnalyticsData {
  responseRate: AnalyticsMetric[];
  conversionRate: AnalyticsMetric[];
  revenue: AnalyticsMetric[];
  activeLeads: AnalyticsMetric[];
}

// System
export interface SystemAlert extends BaseEntity {
  severity: AlertSeverity;
  type: string;
  message: string;
  source: string;
  is_resolved: boolean;
  resolved_at?: string;
  metadata?: Record<string, unknown>;
}

export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical';

// Error Types
export interface AppError extends Error {
  code?: string;
  statusCode?: number;
  details?: unknown;
}

// Form Types
export interface LeadFormData {
  email: string;
  name?: string;
  company?: string;
  phone?: string;
  notes?: string;
  source?: string;
}

export interface CampaignFormData {
  name: string;
  description?: string;
  channels: CampaignChannel[];
  target_lead_ids: string[];
  message_template?: string;
  subject_line?: string;
}

// UI State
export interface LoadingState {
  isLoading: boolean;
  loadingMessage?: string;
}

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

export type ToastType = 'success' | 'error' | 'warning' | 'info';

// Navigation
export interface NavigationProps {
  currentPage?: string;
}

// Utility Types
export type Optional<T> = T | null | undefined;
export type Nullable<T> = T | null;
export type AsyncResult<T> = Promise<ApiResponse<T>>;

// Rex AI Insights
export interface AgentInsight {
  type: InsightType;
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: () => void;
  actionLabel?: string;
  priority?: 'low' | 'medium' | 'high';
}

export type InsightType = 'opportunity' | 'warning' | 'tip' | 'achievement';

// File Upload
export interface FileUploadResult {
  success: boolean;
  filename?: string;
  rowCount?: number;
  errors?: string[];
}

// Webhook
export interface WebhookEvent {
  type: string;
  payload: Record<string, unknown>;
  timestamp: string;
  source: string;
}

// Billing
export interface BillingInfo {
  plan: BillingPlan;
  status: BillingStatus;
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
}

export type BillingPlan = 'free' | 'starter' | 'professional' | 'enterprise';
export type BillingStatus = 'active' | 'past_due' | 'canceled' | 'incomplete';

// Activity Feed
export interface Activity extends BaseEntity {
  user_id: string;
  type: ActivityType;
  description: string;
  metadata?: Record<string, unknown>;
  icon?: string;
}

export type ActivityType =
  | 'lead_imported'
  | 'campaign_launched'
  | 'message_sent'
  | 'lead_responded'
  | 'meeting_booked'
  | 'agent_activated'
  | 'system_alert';

// JWT Token
export interface JWTPayload {
  sub: string; // user_id
  email: string;
  role?: string;
  iat: number;
  exp: number;
}

export interface AuthenticatedRequest {
  userId: string;
  userEmail: string;
  userRole?: string;
}
