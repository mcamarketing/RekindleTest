/**
 * ARE Planner Agent
 *
 * The central planning agent that decomposes high-level goals into executable plans.
 * Creates DAGs of steps with dependencies, agent assignments, and autonomy levels.
 */

import { v4 as uuidv4 } from 'uuid';
import {
  Goal,
  Plan,
  PlanStep,
  PlanDependency,
  AgentType,
  AutonomyLevel,
  RiskAssessment,
  RiskLevel,
  GoalType,
  StepStatus,
  AREError,
  AgentContext
} from './types';
import { getMessageBus } from './message-bus';
import { GuardrailAgent } from './guardrail';

export class PlannerAgent {
  private guardrail: GuardrailAgent;
  private messageBus = getMessageBus();

  constructor(guardrail: GuardrailAgent) {
    this.guardrail = guardrail;
  }

  /**
   * Create a plan from a high-level goal
   */
  async createPlan(goal: Goal, context: AgentContext): Promise<Plan> {
    console.log(`🎯 Planning for goal: ${goal.description}`);

    try {
      // Step 1: Analyze goal and determine strategy
      const strategy = await this.analyzeGoal(goal, context);

      // Step 2: Decompose into steps
      const steps = await this.decomposeGoal(goal, strategy, context);

      // Step 3: Establish dependencies
      const dependencies = this.establishDependencies(steps);

      // Step 4: Assess risk and set autonomy
      const riskAssessment = await this.assessRisk(steps, goal, context);

      // Step 5: Validate plan with guardrail
      const validation = await this.guardrail.validatePlan({
        id: uuidv4(),
        goalId: goal.id,
        steps,
        dependencies,
        status: 'DRAFT',
        autonomyLevel: this.determineAutonomyLevel(riskAssessment, goal),
        riskAssessment,
        createdAt: new Date()
      } as Plan, context);

      if (!validation.valid) {
        throw new AREError(
          `Plan validation failed: ${validation.violations.join(', ')}`,
          'PLAN_VALIDATION_FAILED',
          { violations: validation.violations }
        );
      }

      // Step 6: Create final plan
      const plan: Plan = {
        id: uuidv4(),
        goalId: goal.id,
        steps,
        dependencies,
        status: 'VALIDATED',
        autonomyLevel: this.determineAutonomyLevel(riskAssessment, goal),
        riskAssessment,
        createdAt: new Date(),
        estimatedCompletion: this.estimateCompletion(steps)
      };

      // Step 7: Publish plan creation event
      await this.messageBus.publish({
        type: 'ARE.plan.created' as any,
        from: AgentType.PLANNER,
        payload: { plan, goal },
        correlationId: context.sessionId
      });

      console.log(`✅ Created plan ${plan.id} with ${steps.length} steps`);
      return plan;

    } catch (error) {
      console.error('❌ Plan creation failed:', error);

      // Publish failure event
      await this.messageBus.publish({
        type: 'ARE.plan.failed' as any,
        from: AgentType.PLANNER,
        payload: { goal, error: error.message },
        correlationId: context.sessionId
      });

      throw error;
    }
  }

  /**
   * Analyze goal and determine planning strategy
   */
  private async analyzeGoal(goal: Goal, context: AgentContext): Promise<PlanningStrategy> {
    const strategy: PlanningStrategy = {
      approach: 'SEQUENTIAL',
      agents: [],
      parallelization: 1,
      riskFactors: []
    };

    switch (goal.type) {
      case GoalType.REVIVE_PIPELINE:
        strategy.approach = 'PARALLEL';
        strategy.agents = [
          AgentType.RESEARCH,
          AgentType.REVIVAL,
          AgentType.COPY,
          AgentType.SEND_TIME_BANDIT
        ];
        strategy.parallelization = 3;
        break;

      case GoalType.INCREASE_MEETINGS:
        strategy.approach = 'SEQUENTIAL';
        strategy.agents = [
          AgentType.LEAKAGE_DETECTOR,
          AgentType.SEQUENCING,
          AgentType.COPY_BANDIT,
          AgentType.AUTONOMY_CALIBRATOR
        ];
        break;

      case GoalType.OPTIMIZE_SEQUENCE:
        strategy.approach = 'ITERATIVE';
        strategy.agents = [
          AgentType.SEQUENCING,
          AgentType.COPY,
          AgentType.COHORT_BANDIT,
          AgentType.ANOMALY_DETECTOR
        ];
        break;

      case GoalType.BUILD_ICP:
        strategy.approach = 'ANALYTICAL';
        strategy.agents = [
          AgentType.ICP_BUILDER,
          AgentType.RESEARCH,
          AgentType.PERSONALIZATION
        ];
        break;

      case GoalType.DETECT_LEAKAGE:
        strategy.approach = 'DIAGNOSTIC';
        strategy.agents = [
          AgentType.LEAKAGE_DETECTOR,
          AgentType.ANOMALY_DETECTOR,
          AgentType.FORECASTER
        ];
        break;

      case GoalType.PREDICT_CHURN:
        strategy.approach = 'PREDICTIVE';
        strategy.agents = [
          AgentType.CHURN_PREDICTOR,
          AgentType.ANOMALY_DETECTOR,
          AgentType.RISK_SENTINEL
        ];
        break;

      case GoalType.FORECAST_REVENUE:
        strategy.approach = 'ANALYTICAL';
        strategy.agents = [
          AgentType.FORECASTER,
          AgentType.LEAKAGE_DETECTOR,
          AgentType.ICP_BUILDER
        ];
        break;
    }

    // Assess risk factors
    strategy.riskFactors = await this.identifyRiskFactors(goal, context);

    return strategy;
  }

  /**
   * Decompose goal into executable steps
   */
  private async decomposeGoal(
    goal: Goal,
    strategy: PlanningStrategy,
    context: AgentContext
  ): Promise<PlanStep[]> {
    const steps: PlanStep[] = [];

    for (let i = 0; i < strategy.agents.length; i++) {
      const agentType = strategy.agents[i];
      const step = await this.createStepForAgent(agentType, goal, i, strategy, context);
      steps.push(step);
    }

    return steps;
  }

  /**
   * Create a step for a specific agent
   */
  private async createStepForAgent(
    agentType: AgentType,
    goal: Goal,
    stepIndex: number,
    strategy: PlanningStrategy,
    context: AgentContext
  ): Promise<PlanStep> {
    const stepConfig = this.getStepConfig(agentType, goal);

    return {
      id: uuidv4(),
      agentType,
      description: stepConfig.description,
      input: {
        goal: goal,
        context: context,
        strategy: strategy,
        stepIndex: stepIndex
      },
      requiredTools: stepConfig.requiredTools,
      status: StepStatus.PENDING,
      autonomyLevel: this.calculateStepAutonomy(agentType, strategy, context),
      priority: stepConfig.priority,
      retryCount: 0,
      maxRetries: stepConfig.maxRetries,
      timeoutMinutes: stepConfig.timeoutMinutes,
      createdAt: new Date()
    };
  }

  /**
   * Establish dependencies between steps
   */
  private establishDependencies(steps: PlanStep[]): PlanDependency[] {
    const dependencies: PlanDependency[] = [];

    // Create sequential dependencies by default
    for (let i = 1; i < steps.length; i++) {
      dependencies.push({
        fromStepId: steps[i - 1].id,
        toStepId: steps[i].id
      });
    }

    // Add specific dependencies based on agent relationships
    const agentDependencies = this.getAgentDependencies(steps);
    dependencies.push(...agentDependencies);

    return dependencies;
  }

  /**
   * Assess overall risk of the plan
   */
  private async assessRisk(
    steps: PlanStep[],
    goal: Goal,
    context: AgentContext
  ): Promise<RiskAssessment> {
    let riskScore = 0;
    const factors: string[] = [];
    const mitigations: string[] = [];

    // Assess based on goal type
    if (goal.type === GoalType.REVIVE_PIPELINE) {
      riskScore += 0.3; // Moderate risk for outreach
      factors.push('Outbound communication risk');
      mitigations.push('Rate limiting and compliance checks');
    }

    // Assess based on autonomy level
    const highAutonomySteps = steps.filter(s => s.autonomyLevel === AutonomyLevel.L3);
    if (highAutonomySteps.length > 0) {
      riskScore += 0.4;
      factors.push('High autonomy execution');
      mitigations.push('Continuous monitoring and anomaly detection');
    }

    // Assess based on target metrics
    if (goal.targetMetrics.budget && goal.targetMetrics.budget > 10000) {
      riskScore += 0.2;
      factors.push('High budget allocation');
      mitigations.push('Budget caps and spending alerts');
    }

    // Determine risk level
    let level: RiskLevel;
    if (riskScore >= 0.7) level = RiskLevel.CRITICAL;
    else if (riskScore >= 0.5) level = RiskLevel.HIGH;
    else if (riskScore >= 0.3) level = RiskLevel.MEDIUM;
    else level = RiskLevel.LOW;

    return {
      level,
      score: riskScore,
      factors,
      mitigations,
      requiresApproval: level === RiskLevel.CRITICAL || level === RiskLevel.HIGH
    };
  }

  /**
   * Determine autonomy level for the plan
   */
  private determineAutonomyLevel(risk: RiskAssessment, goal: Goal): AutonomyLevel {
    if (risk.level === RiskLevel.CRITICAL) return AutonomyLevel.L0;
    if (risk.level === RiskLevel.HIGH) return AutonomyLevel.L1;
    if (goal.constraints.autonomyLevel) return goal.constraints.autonomyLevel;
    return AutonomyLevel.L2;
  }

  /**
   * Estimate completion time
   */
  private estimateCompletion(steps: PlanStep[]): Date {
    const totalMinutes = steps.reduce((sum, step) => sum + (step.timeoutMinutes || 30), 0);
    return new Date(Date.now() + totalMinutes * 60 * 1000);
  }

  /**
   * Identify risk factors for a goal
   */
  private async identifyRiskFactors(goal: Goal, context: AgentContext): Promise<string[]> {
    const factors: string[] = [];

    if (goal.type === GoalType.REVIVE_PIPELINE) {
      factors.push('lead quality uncertainty');
      factors.push('compliance requirements');
    }

    if (context.autonomyLevel === AutonomyLevel.L3) {
      factors.push('full autonomy execution');
    }

    // Check for high-value targets
    if (goal.targetMetrics.revenue && goal.targetMetrics.revenue > 100000) {
      factors.push('high revenue target');
    }

    return factors;
  }

  /**
   * Get configuration for a step based on agent type
   */
  private getStepConfig(agentType: AgentType, goal: Goal): StepConfig {
    const configs: Record<AgentType, StepConfig> = {
      [AgentType.RESEARCH]: {
        description: 'Research and enrich lead data',
        requiredTools: ['linkedin_api', 'company_enrichment'],
        priority: 8,
        maxRetries: 2,
        timeoutMinutes: 15
      },
      [AgentType.REVIVAL]: {
        description: 'Generate revival campaign for dormant leads',
        requiredTools: ['campaign_builder', 'template_engine'],
        priority: 9,
        maxRetries: 1,
        timeoutMinutes: 20
      },
      [AgentType.COPY]: {
        description: 'Generate personalized messaging content',
        requiredTools: ['llm_api', 'personalization_engine'],
        priority: 7,
        maxRetries: 2,
        timeoutMinutes: 10
      },
      [AgentType.SEQUENCING]: {
        description: 'Design multi-touch campaign sequence',
        requiredTools: ['sequence_optimizer', 'channel_selector'],
        priority: 6,
        maxRetries: 1,
        timeoutMinutes: 25
      },
      [AgentType.PERSONALIZATION]: {
        description: 'Apply ICP-based personalization',
        requiredTools: ['icp_matcher', 'segmentation_engine'],
        priority: 5,
        maxRetries: 1,
        timeoutMinutes: 5
      },
      [AgentType.MULTI_TOUCH]: {
        description: 'Optimize channel selection and timing',
        requiredTools: ['channel_analyzer', 'engagement_predictor'],
        priority: 4,
        maxRetries: 1,
        timeoutMinutes: 10
      },
      [AgentType.SEND_TIME_BANDIT]: {
        description: 'Optimize send timing using bandit algorithm',
        requiredTools: ['time_optimizer', 'engagement_analyzer'],
        priority: 3,
        maxRetries: 1,
        timeoutMinutes: 5
      },
      [AgentType.COPY_BANDIT]: {
        description: 'A/B test and optimize content variants',
        requiredTools: ['variant_tester', 'performance_analyzer'],
        priority: 2,
        maxRetries: 1,
        timeoutMinutes: 5
      },
      [AgentType.COHORT_BANDIT]: {
        description: 'Optimize targeting for different segments',
        requiredTools: ['cohort_analyzer', 'segment_optimizer'],
        priority: 1,
        maxRetries: 1,
        timeoutMinutes: 5
      },
      [AgentType.AUTONOMY_CALIBRATOR]: {
        description: 'Adjust autonomy levels based on performance',
        requiredTools: ['performance_monitor', 'risk_assessor'],
        priority: 1,
        maxRetries: 1,
        timeoutMinutes: 5
      },
      [AgentType.ANOMALY_DETECTOR]: {
        description: 'Monitor for performance anomalies',
        requiredTools: ['anomaly_detector', 'alert_system'],
        priority: 10,
        maxRetries: 1,
        timeoutMinutes: 2
      },
      [AgentType.ICP_BUILDER]: {
        description: 'Build and update Ideal Customer Profile',
        requiredTools: ['data_analyzer', 'pattern_recognizer'],
        priority: 6,
        maxRetries: 1,
        timeoutMinutes: 30
      },
      [AgentType.FORECASTER]: {
        description: 'Generate revenue and pipeline forecasts',
        requiredTools: ['forecasting_engine', 'trend_analyzer'],
        priority: 4,
        maxRetries: 1,
        timeoutMinutes: 20
      },
      [AgentType.LEAKAGE_DETECTOR]: {
        description: 'Identify revenue leakage points',
        requiredTools: ['funnel_analyzer', 'leakage_detector'],
        priority: 7,
        maxRetries: 1,
        timeoutMinutes: 15
      },
      [AgentType.RISK_SENTINEL]: {
        description: 'Monitor compliance and risk factors',
        requiredTools: ['compliance_checker', 'risk_analyzer'],
        priority: 9,
        maxRetries: 1,
        timeoutMinutes: 5
      },
      [AgentType.CHURN_PREDICTOR]: {
        description: 'Predict customer churn risk',
        requiredTools: ['churn_model', 'engagement_analyzer'],
        priority: 5,
        maxRetries: 1,
        timeoutMinutes: 10
      },
      // Core agents don't have steps
      [AgentType.PLANNER]: { description: '', requiredTools: [], priority: 0, maxRetries: 0, timeoutMinutes: 0 },
      [AgentType.EXECUTOR]: { description: '', requiredTools: [], priority: 0, maxRetries: 0, timeoutMinutes: 0 },
      [AgentType.CRITIC]: { description: '', requiredTools: [], priority: 0, maxRetries: 0, timeoutMinutes: 0 },
      [AgentType.GUARDRAIL]: { description: '', requiredTools: [], priority: 0, maxRetries: 0, timeoutMinutes: 0 },
      [AgentType.RAG_SERVICE]: { description: '', requiredTools: [], priority: 0, maxRetries: 0, timeoutMinutes: 0 }
    };

    return configs[agentType] || {
      description: 'Execute agent task',
      requiredTools: [],
      priority: 5,
      maxRetries: 1,
      timeoutMinutes: 10
    };
  }

  /**
   * Calculate autonomy level for a specific step
   */
  private calculateStepAutonomy(
    agentType: AgentType,
    strategy: PlanningStrategy,
    context: AgentContext
  ): AutonomyLevel {
    // High-risk agents get lower autonomy
    const highRiskAgents = [AgentType.REVIVAL, AgentType.COPY, AgentType.SEQUENCING];
    if (highRiskAgents.includes(agentType) && strategy.riskFactors.length > 0) {
      return this.minAutonomyLevel(context.autonomyLevel, AutonomyLevel.L1);
    }

    // Low-risk agents can have higher autonomy
    const lowRiskAgents = [AgentType.ANOMALY_DETECTOR, AgentType.AUTONOMY_CALIBRATOR];
    if (lowRiskAgents.includes(agentType)) {
      return context.autonomyLevel;
    }

    return context.autonomyLevel;
  }

  /**
   * Get the minimum of two autonomy levels
   */
  private minAutonomyLevel(level1: AutonomyLevel, level2: AutonomyLevel): AutonomyLevel {
    const levels = [AutonomyLevel.L0, AutonomyLevel.L1, AutonomyLevel.L2, AutonomyLevel.L3];
    const index1 = levels.indexOf(level1);
    const index2 = levels.indexOf(level2);
    return levels[Math.min(index1, index2)];
  }

  /**
   * Get agent-specific dependencies
   */
  private getAgentDependencies(steps: PlanStep[]): PlanDependency[] {
    const dependencies: PlanDependency[] = [];
    const stepMap = new Map(steps.map(s => [s.agentType, s.id]));

    // Research must complete before revival
    if (stepMap.has(AgentType.RESEARCH) && stepMap.has(AgentType.REVIVAL)) {
      dependencies.push({
        fromStepId: stepMap.get(AgentType.RESEARCH)!,
        toStepId: stepMap.get(AgentType.REVIVAL)!,
        condition: 'SUCCESS'
      });
    }

    // Personalization should complete before copy generation
    if (stepMap.has(AgentType.PERSONALIZATION) && stepMap.has(AgentType.COPY)) {
      dependencies.push({
        fromStepId: stepMap.get(AgentType.PERSONALIZATION)!,
        toStepId: stepMap.get(AgentType.COPY)!,
        condition: 'SUCCESS'
      });
    }

    return dependencies;
  }
}

interface PlanningStrategy {
  approach: 'SEQUENTIAL' | 'PARALLEL' | 'ITERATIVE' | 'ANALYTICAL' | 'PREDICTIVE' | 'DIAGNOSTIC';
  agents: AgentType[];
  parallelization: number;
  riskFactors: string[];
}

interface StepConfig {
  description: string;
  requiredTools: string[];
  priority: number;
  maxRetries: number;
  timeoutMinutes: number;
}