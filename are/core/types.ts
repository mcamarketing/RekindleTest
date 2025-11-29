/**
 * ARE (Autonomous Revenue Engine) Core Types
 *
 * Defines the type system for the Autonomous Revenue Engine,
 * including goals, plans, agents, outcomes, and autonomy levels.
 */

export enum AutonomyLevel {
  L0 = 'L0', // Human-only: Generate drafts, require approval
  L1 = 'L1', // Assisted: Execute with human oversight
  L2 = 'L2', // Semi-autonomous: Execute with monitoring
  L3 = 'L3'  // Full autonomy: Execute independently
}

export enum AgentType {
  // Core Brainstem
  PLANNER = 'PLANNER',
  EXECUTOR = 'EXECUTOR',
  CRITIC = 'CRITIC',
  GUARDRAIL = 'GUARDRAIL',
  RAG_SERVICE = 'RAG_SERVICE',

  // Revenue Agents
  REVIVAL = 'REVIVAL',
  SEQUENCING = 'SEQUENCING',
  COPY = 'COPY',
  RESEARCH = 'RESEARCH',
  PERSONALIZATION = 'PERSONALIZATION',
  MULTI_TOUCH = 'MULTI_TOUCH',

  // Optimization Agents
  SEND_TIME_BANDIT = 'SEND_TIME_BANDIT',
  COPY_BANDIT = 'COPY_BANDIT',
  COHORT_BANDIT = 'COHORT_BANDIT',
  AUTONOMY_CALIBRATOR = 'AUTONOMY_CALIBRATOR',
  ANOMALY_DETECTOR = 'ANOMALY_DETECTOR',

  // Strategic Agents
  ICP_BUILDER = 'ICP_BUILDER',
  FORECASTER = 'FORECASTER',
  LEAKAGE_DETECTOR = 'LEAKAGE_DETECTOR',
  RISK_SENTINEL = 'RISK_SENTINEL',
  CHURN_PREDICTOR = 'CHURN_PREDICTOR'
}

export enum GoalType {
  REVIVE_PIPELINE = 'REVIVE_PIPELINE',
  INCREASE_MEETINGS = 'INCREASE_MEETINGS',
  OPTIMIZE_SEQUENCE = 'OPTIMIZE_SEQUENCE',
  BUILD_ICP = 'BUILD_ICP',
  DETECT_LEAKAGE = 'DETECT_LEAKAGE',
  PREDICT_CHURN = 'PREDICT_CHURN',
  FORECAST_REVENUE = 'FORECAST_REVENUE'
}

export enum StepStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  SKIPPED = 'SKIPPED'
}

export enum OutcomeType {
  EMAIL_OPEN = 'EMAIL_OPEN',
  EMAIL_CLICK = 'EMAIL_CLICK',
  EMAIL_REPLY = 'EMAIL_REPLY',
  MEETING_BOOKED = 'MEETING_BOOKED',
  PIPELINE_MOVE = 'PIPELINE_MOVE',
  REVENUE_WON = 'REVENUE_WON',
  SPAM_REPORT = 'SPAM_REPORT',
  UNSUBSCRIBE = 'UNSUBSCRIBE'
}

export enum ChannelType {
  EMAIL = 'EMAIL',
  LINKEDIN = 'LINKEDIN',
  WHATSAPP = 'WHATSAPP',
  SMS = 'SMS',
  CALL = 'CALL'
}

export enum RiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export interface Goal {
  id: string;
  type: GoalType;
  description: string;
  targetMetrics: Record<string, number>;
  constraints: GoalConstraints;
  priority: number;
  createdAt: Date;
  deadline?: Date;
  orgId: string;
  userId?: string;
}

export interface GoalConstraints {
  maxBudget?: number;
  maxActionsPerDay?: number;
  allowedChannels?: ChannelType[];
  restrictedSegments?: string[];
  autonomyLevel: AutonomyLevel;
}

export interface Plan {
  id: string;
  goalId: string;
  steps: PlanStep[];
  dependencies: PlanDependency[];
  status: 'DRAFT' | 'VALIDATED' | 'EXECUTING' | 'COMPLETED' | 'FAILED';
  autonomyLevel: AutonomyLevel;
  riskAssessment: RiskAssessment;
  createdAt: Date;
  estimatedCompletion?: Date;
}

export interface PlanStep {
  id: string;
  agentType: AgentType;
  description: string;
  input: Record<string, any>;
  requiredTools: string[];
  status: StepStatus;
  autonomyLevel: AutonomyLevel;
  priority: number;
  retryCount: number;
  maxRetries: number;
  timeoutMinutes?: number;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  result?: StepResult;
  error?: string;
}

export interface PlanDependency {
  fromStepId: string;
  toStepId: string;
  condition?: string; // e.g., "SUCCESS", "result.metric > 0.8"
}

export interface StepResult {
  success: boolean;
  data: Record<string, any>;
  metrics: Record<string, number>;
  confidence: number;
  executionTimeMs: number;
}

export interface RiskAssessment {
  level: RiskLevel;
  score: number; // 0-1
  factors: string[];
  mitigations: string[];
  requiresApproval: boolean;
}

export interface AgentContext {
  orgId: string;
  userId?: string;
  planId?: string;
  stepId?: string;
  sessionId: string;
  autonomyLevel: AutonomyLevel;
  constraints: Record<string, any>;
  memory: AgentMemory;
}

export interface AgentMemory {
  shortTerm: Record<string, any>;
  longTerm: Record<string, any>;
  context: Record<string, any>;
}

export interface Outcome {
  id: string;
  type: OutcomeType;
  planId?: string;
  stepId?: string;
  agentType?: AgentType;
  leadId?: string;
  campaignId?: string;
  channel?: ChannelType;
  timestamp: Date;
  value: number;
  metadata: Record<string, any>;
  confidence?: number;
}

export interface AgentAction {
  id: string;
  agentType: AgentType;
  type: string; // e.g., "SEND_EMAIL", "UPDATE_CRM", "CREATE_TASK"
  payload: Record<string, any>;
  riskLevel: RiskLevel;
  requiresApproval: boolean;
  planId?: string;
  stepId?: string;
  createdAt: Date;
}

export interface ValidationResult {
  valid: boolean;
  riskLevel: RiskLevel;
  violations: string[];
  warnings: string[];
  suggestions: string[];
}

export interface PolicyRule {
  id: string;
  name: string;
  type: 'ALLOW' | 'DENY' | 'WARN';
  conditions: Record<string, any>;
  actions: string[];
  priority: number;
  orgId?: string;
  verticalId?: string;
}

export interface ICPProfile {
  id: string;
  orgId: string;
  name: string;
  criteria: ICPCriteria;
  segments: ICPSegment[];
  embeddings: number[];
  confidence: number;
  lastUpdated: Date;
  sampleSize: number;
}

export interface ICPCriteria {
  industries: string[];
  companySizes: string[];
  titles: string[];
  geographies: string[];
  technologies: string[];
  signals: string[];
}

export interface ICPSegment {
  id: string;
  name: string;
  criteria: Partial<ICPCriteria>;
  size: number;
  conversionRate: number;
  avgDealSize: number;
}

export interface Forecast {
  id: string;
  orgId: string;
  type: 'PIPELINE' | 'REVENUE' | 'MEETINGS';
  period: {
    start: Date;
    end: Date;
  };
  predictions: ForecastPoint[];
  confidence: number;
  assumptions: string[];
  createdAt: Date;
}

export interface ForecastPoint {
  date: Date;
  value: number;
  lowerBound: number;
  upperBound: number;
  drivers: Record<string, number>;
}

export interface LeakageEvent {
  id: string;
  type: string; // e.g., "REPLY_ABANDONED", "SEQUENCE_EXHAUSTED"
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  leadId?: string;
  campaignId?: string;
  value: number; // potential revenue lost
  detectedAt: Date;
  autoFixed: boolean;
  resolution?: string;
}

export interface AnomalyEvent {
  id: string;
  type: string; // e.g., "SPAM_SPIKE", "REPLY_DROP"
  metric: string;
  threshold: number;
  actualValue: number;
  severity: RiskLevel;
  affectedSegments: string[];
  detectedAt: Date;
  resolved: boolean;
}

export interface BanditVariant {
  id: string;
  type: string; // e.g., "SUBJECT_LINE", "SEND_TIME", "CONTENT"
  value: any;
  trials: number;
  successes: number;
  reward: number;
  confidence: number;
  lastUpdated: Date;
}

export interface MessageContent {
  subject?: string;
  body: string;
  callToAction?: string;
  variantId?: string;
  personalization: Record<string, any>;
  riskScore: number;
  confidence: number;
}

export interface SequenceStep {
  id: string;
  channel: ChannelType;
  delayDays: number;
  content: MessageContent;
  conditions?: string[]; // e.g., ["no_reply", "opened"]
  priority: number;
}

export interface CampaignSequence {
  id: string;
  name: string;
  steps: SequenceStep[];
  targetSegments: string[];
  optimizationGoals: string[];
  performance: {
    replyRate: number;
    meetingRate: number;
    unsubscribeRate: number;
  };
}

// API DTOs
export interface CreateGoalRequest {
  type: GoalType;
  description: string;
  targetMetrics: Record<string, number>;
  constraints: GoalConstraints;
  priority?: number;
  deadline?: Date;
}

export interface ExecutePlanRequest {
  planId: string;
  approvalToken?: string;
  overrides?: Record<string, any>;
}

export interface PlanStatusResponse {
  plan: Plan;
  currentStep?: PlanStep;
  progress: number;
  estimatedCompletion?: Date;
  nextActions: string[];
}

export interface AutonomyConfig {
  orgId: string;
  defaultLevel: AutonomyLevel;
  maxLevel: AutonomyLevel;
  overrides: Record<string, AutonomyLevel>;
  calibrations: AutonomyCalibration[];
}

export interface AutonomyCalibration {
  scenario: string;
  currentLevel: AutonomyLevel;
  performance: number;
  lastAdjusted: Date;
  reason: string;
}

// Error types
export class AREError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'AREError';
  }
}

export class ValidationError extends AREError {
  constructor(message: string, violations: string[]) {
    super(message, 'VALIDATION_ERROR', { violations });
    this.name = 'ValidationError';
  }
}

export class PolicyViolationError extends AREError {
  constructor(message: string, ruleId: string) {
    super(message, 'POLICY_VIOLATION', { ruleId });
    this.name = 'PolicyViolationError';
  }
}

export class AutonomyLimitError extends AREError {
  constructor(message: string, requiredLevel: AutonomyLevel, currentLevel: AutonomyLevel) {
    super(message, 'AUTONOMY_LIMIT', { requiredLevel, currentLevel });
    this.name = 'AutonomyLimitError';
  }
}