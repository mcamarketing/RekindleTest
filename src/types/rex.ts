// @ts-nocheck
// REX: Autonomous Orchestration System - TypeScript Types
// Shared types between frontend and backend

// ============================================================================
// ENUMS
// ============================================================================

export enum MissionType {
  LEAD_REACTIVATION = 'lead_reactivation',
  CAMPAIGN_EXECUTION = 'campaign_execution',
  ICP_EXTRACTION = 'icp_extraction',
  DOMAIN_ROTATION = 'domain_rotation',
  PERFORMANCE_OPTIMIZATION = 'performance_optimization',
  ERROR_RECOVERY = 'error_recovery',
}

export enum MissionState {
  QUEUED = 'queued',
  ASSIGNED = 'assigned',
  EXECUTING = 'executing',
  COLLECTING = 'collecting',
  ANALYZING = 'analyzing',
  OPTIMIZING = 'optimizing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  ESCALATED = 'escalated',
}

export enum TaskState {
  PENDING = 'pending',
  EXECUTING = 'executing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum DomainType {
  CUSTOM = 'custom',
  PREWARMED = 'prewarmed',
}

export enum DomainStatus {
  ACTIVE = 'active',
  WARMING = 'warming',
  ROTATED = 'rotated',
  FAILED = 'failed',
  PENDING_VERIFICATION = 'pending_verification',
}

export enum MessageType {
  // Rex → Agent
  MISSION_ASSIGNED = 'mission.assigned',
  MISSION_CANCELLED = 'mission.cancelled',
  RESOURCE_ALLOCATED = 'resource.allocated',

  // Agent → Rex
  MISSION_STARTED = 'mission.started',
  MISSION_PROGRESS = 'mission.progress',
  MISSION_COMPLETED = 'mission.completed',
  MISSION_FAILED = 'mission.failed',

  // System
  RESOURCE_EXHAUSTED = 'resource.exhausted',
  ERROR_ESCALATION = 'error.escalation',
  DOMAIN_ROTATION_NEEDED = 'domain.rotation_needed',
}

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

// ============================================================================
// CORE INTERFACES
// ============================================================================

export interface Mission {
  id: string;
  user_id: string;
  type: MissionType;
  state: MissionState;
  priority: number; // 0-100

  // Context
  campaign_id?: string;
  lead_ids?: string[];
  custom_params?: Record<string, any>;

  // Execution
  assigned_crew?: string;
  assigned_agents?: string[];
  allocated_resources?: ResourceAllocation;

  // Results
  outcome?: MissionOutcome;
  metrics?: MissionMetrics;
  error?: MissionError;

  // Timestamps
  created_at: string;
  assigned_at?: string;
  started_at?: string;
  completed_at?: string;
  updated_at: string;
}

export interface Task {
  id: string;
  mission_id: string;
  agent_name: string;
  state: TaskState;

  // Execution
  input?: Record<string, any>;
  output?: Record<string, any>;
  error?: MissionError;

  // Metrics
  duration_ms?: number;
  tokens_used?: number;
  cost_usd?: number;

  // Timestamps
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface MissionOutcome {
  success: boolean;
  summary: string;

  results: {
    leads_analyzed?: number;
    leads_qualified?: number;
    messages_sent?: number;
    replies_received?: number;
    meetings_booked?: number;
    [key: string]: number | undefined;
  };

  recommendations?: string[];
  next_actions?: string[];
}

export interface MissionMetrics {
  duration_ms: number;
  tokens_used: number;
  api_calls: {
    openai: number;
    sendgrid: number;
    twilio: number;
  };
  cost_usd: number;
}

export interface MissionError {
  code: string;
  message: string;
  details?: any;
  stack?: string;
  recoverable: boolean;
  retry_count: number;
}

export interface ResourceAllocation {
  agents: {
    [crew_name: string]: string[]; // crew_name -> agent_names
  };
  domains: string[];
  api_quota: {
    openai: number;
    sendgrid: number;
    twilio: number;
  };
}

export interface ResourcePool {
  agents: {
    [crew_name: string]: {
      total: number;
      available: number;
      executing: number;
      failed: number;
    };
  };

  domains: {
    total: number;
    active: number;
    warming: number;
    rotated: number;
    custom: number;
    prewarmed: number;
  };

  api_limits: {
    openai: { used: number; limit: number; reset_at: string };
    sendgrid: { used: number; limit: number; reset_at: string };
    twilio: { used: number; limit: number; reset_at: string };
  };
}

// ============================================================================
// DOMAIN MANAGEMENT
// ============================================================================

export interface Domain {
  id: string;
  user_id: string;
  domain: string;
  type: DomainType;

  // Status
  status: DomainStatus;
  reputation_score: number; // 0.00 - 1.00

  // Usage
  emails_sent_today: number;
  emails_sent_total: number;
  last_used_at?: string;
  assigned_to_campaign?: string;

  // Health metrics
  bounce_rate: number;
  spam_complaint_rate: number;
  open_rate: number;

  // Warmup
  warmup_progress: number; // 0.00 - 1.00
  warmup_started_at?: string;
  warmup_completed_at?: string;

  // Rotation
  rotated_at?: string;
  rotation_reason?: string;
  replacement_domain_id?: string;

  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface DomainHealth {
  domain: string;
  reputation_score: number; // 0.0 - 1.0
  status: 'healthy' | 'degraded' | 'critical' | 'rotated';
  metrics: {
    emails_sent_24h: number;
    bounce_rate: number;
    spam_complaint_rate: number;
    open_rate: number;
  };
  rotation_threshold: number;
  rotation_recommended: boolean;
}

// ============================================================================
// ANALYTICS
// ============================================================================

export interface AnalyticsSnapshot {
  timestamp: string;

  missions: {
    total: number;
    active: number;
    completed: number;
    failed: number;
    avg_duration_ms: number;
  };

  agents: {
    [crew_name: string]: {
      executions: number;
      success_rate: number;
      avg_duration_ms: number;
      error_count: number;
    };
  };

  campaigns: {
    total_leads: number;
    contacted: number;
    replied: number;
    meetings_booked: number;
    reply_rate: number;
    meeting_rate: number;
  };

  domains: {
    reputation_avg: number;
    rotation_events: number;
    warmup_in_progress: number;
  };
}

export interface RexLog {
  id: string;
  mission_id?: string;
  user_id: string;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
  source: string; // 'rex' | crew_name | agent_name
  created_at: string;
}

// ============================================================================
// MESSAGE BUS
// ============================================================================

export interface RexMessage {
  id: string;
  type: MessageType;
  timestamp: string;
  sender: string; // 'rex' | crew_name | agent_name
  recipient: string; // 'rex' | crew_name | agent_name | 'broadcast'

  // Payload
  mission_id?: string;
  data: any;

  // Tracking
  correlation_id?: string;
  reply_to?: string;
}

// ============================================================================
// API REQUEST/RESPONSE TYPES
// ============================================================================

// GET /api/rex/status
export interface RexStatusResponse {
  status: 'operational' | 'degraded' | 'error';
  uptime_ms: number;

  missions: {
    active: number;
    queued: number;
    completed_24h: number;
    failed_24h: number;
  };

  resources: ResourcePool;
  analytics: AnalyticsSnapshot;
}

// POST /api/rex/missions
export interface CreateMissionRequest {
  type: MissionType;
  priority?: number;
  context: {
    campaign_id?: string;
    lead_ids?: string[];
    custom_params?: Record<string, any>;
  };
}

export interface CreateMissionResponse {
  mission_id: string;
  estimated_duration_ms: number;
  assigned_crew: string;
}

// GET /api/rex/missions/:id
export interface MissionDetailsResponse extends Mission {
  tasks: Task[];
  progress: number; // 0-1
  logs: RexLog[];
}

// POST /api/rex/missions/:id/cancel
export interface CancelMissionResponse {
  cancelled: boolean;
  state: MissionState;
}

// GET /api/rex/analytics
export interface AnalyticsResponse {
  current: AnalyticsSnapshot;
  history: AnalyticsSnapshot[]; // Last 24 hours, 1-hour intervals
  trends: {
    missions_per_hour: number[];
    success_rate: number[];
    avg_duration_ms: number[];
  };
}

// GET /api/rex/agents/status
export interface AgentStatusResponse {
  agents: {
    [crew_name: string]: {
      [agent_name: string]: {
        status: 'idle' | 'executing' | 'failed';
        current_task?: string;
        last_execution_at?: string;
        success_rate: number;
        avg_duration_ms: number;
      };
    };
  };
}

// POST /api/rex/agents/:crew/:agent/restart
export interface RestartAgentResponse {
  restarted: boolean;
  new_status: string;
}

// GET /api/rex/domains
export interface DomainPoolResponse {
  domains: {
    domain: string;
    type: DomainType;
    status: DomainStatus;
    health: DomainHealth;
    assigned_to?: string;
  }[];
  summary: {
    total: number;
    active: number;
    warming: number;
    rotated: number;
  };
}

// POST /api/rex/domains/rotate
export interface RotateDomainRequest {
  domain: string;
  reason: string;
  immediate: boolean;
}

export interface RotateDomainResponse {
  rotated: boolean;
  replacement_domain?: string;
  warmup_eta_hours?: number;
}

// POST /api/rex/domains/add
export interface AddDomainRequest {
  domain: string;
  type: DomainType;
  verify: boolean; // Run DNS verification
}

export interface AddDomainResponse {
  added: boolean;
  verification_status?: 'pending' | 'verified' | 'failed';
  dns_records?: any[];
}

// ============================================================================
// DECISION ENGINE TYPES
// ============================================================================

export interface Decision {
  action: string;
  params?: Record<string, any>;
  target_state?: MissionState;
  reason: string;
  confidence: number; // 0.0 - 1.0
  alternatives_considered?: string[];
  llm_used?: boolean;
}

// ============================================================================
// UI COMPONENT PROPS
// ============================================================================

export interface MissionCardProps {
  mission: Mission;
  onCancel?: (missionId: string) => void;
  onView?: (missionId: string) => void;
}

export interface AgentStatusCardProps {
  crewName: string;
  agents: AgentStatusResponse['agents'][string];
  onRestart?: (crewName: string, agentName: string) => void;
}

export interface DomainCardProps {
  domain: Domain;
  health: DomainHealth;
  onRotate?: (domain: string) => void;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type MissionWithProgress = Mission & {
  progress: number;
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
};

export type AgentStatus = 'idle' | 'executing' | 'failed';

export type RexSystemStatus = 'operational' | 'degraded' | 'error';
