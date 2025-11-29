/**
 * ARE Executor Agent
 *
 * Executes validated plans by coordinating with specialized agents and tools.
 * Manages step dependencies, error handling, and result aggregation.
 */

import { v4 as uuidv4 } from 'uuid';
import {
  Plan,
  PlanStep,
  StepResult,
  AgentType,
  AgentContext,
  AREError,
  StepStatus,
  AgentAction
} from './types';
import { getMessageBus } from './message-bus';
import { GuardrailAgent } from './guardrail';

export class ExecutorAgent {
  private guardrail: GuardrailAgent;
  private messageBus = getMessageBus();

  constructor(guardrail: GuardrailAgent) {
    this.guardrail = guardrail;
  }

  /**
   * Execute a validated plan
   */
  async executePlan(plan: Plan, context: AgentContext): Promise<Plan> {
    console.log(`🚀 Executing plan ${plan.id} with ${plan.steps.length} steps`);

    const updatedPlan = { ...plan, status: 'EXECUTING' as 'EXECUTING' | 'COMPLETED' | 'FAILED' };
    const executedSteps = new Map<string, PlanStep>();

    try {
      // Execute steps respecting dependencies
      const executionOrder = this.determineExecutionOrder(plan.steps, plan.dependencies);

      for (const stepId of executionOrder) {
        const step = plan.steps.find(s => s.id === stepId);
        if (!step) continue;

        // Check if dependencies are satisfied
        if (!this.areDependenciesSatisfied(step, executedSteps, plan.dependencies)) {
          console.log(`⏳ Skipping step ${stepId} - dependencies not satisfied`);
          continue;
        }

        // Execute the step
        const result = await this.executeStep(step, context);

        // Update step with result
        const updatedStep = {
          ...step,
          status: result.success ? StepStatus.COMPLETED : StepStatus.FAILED,
          completedAt: new Date(),
          result
        };

        executedSteps.set(stepId, updatedStep);

        // Publish step completion event
        await this.messageBus.publish({
          type: 'ARE.step.completed' as any,
          from: AgentType.EXECUTOR,
          payload: { step: updatedStep, planId: plan.id },
          correlationId: context.sessionId
        });

        // Check if we should continue execution
        if (!result.success && step.maxRetries > step.retryCount) {
          // Schedule retry
          await this.scheduleStepRetry(updatedStep, context);
        } else if (!result.success) {
          // Step failed permanently
          throw new AREError(`Step ${stepId} failed: ${result.data?.error || 'Unknown error'}`, 'STEP_EXECUTION_FAILED');
        }
      }

      // Update plan with completed steps
      updatedPlan.steps = plan.steps.map(step =>
        executedSteps.get(step.id) || step
      );
      updatedPlan.status = 'COMPLETED';

      // Publish plan completion event
      await this.messageBus.publish({
        type: 'ARE.plan.completed' as any,
        from: AgentType.EXECUTOR,
        payload: { plan: updatedPlan },
        correlationId: context.sessionId
      });

      console.log(`✅ Plan ${plan.id} executed successfully`);
      return updatedPlan;

    } catch (error) {
      console.error('❌ Plan execution failed:', error);

      // Mark plan as failed
      updatedPlan.status = 'FAILED';

      // Publish failure event
      await this.messageBus.publish({
        type: 'ARE.plan.failed' as any,
        from: AgentType.EXECUTOR,
        payload: { plan: updatedPlan, error: error.message },
        correlationId: context.sessionId
      });

      throw error;
    }
  }

  /**
   * Execute a single step
   */
  private async executeStep(step: PlanStep, context: AgentContext): Promise<StepResult> {
    const startTime = Date.now();

    try {
      console.log(`⚙️ Executing step ${step.id}: ${step.description}`);

      // Update step status to processing
      step.status = StepStatus.PROCESSING;
      step.startedAt = new Date();

      // Get the agent instance for this step
      const agent = await this.getAgentInstance(step.agentType);

      // Prepare step context
      const stepContext = {
        ...context,
        stepId: step.id,
        planId: context.planId
      };

      // Execute based on autonomy level
      let result: StepResult;

      if (step.autonomyLevel === 'L0') {
        // Human approval required - create draft
        result = await this.executeWithApproval(step, agent, stepContext);
      } else {
        // Autonomous execution
        result = await this.executeAutonomously(step, agent, stepContext);
      }

      const executionTime = Date.now() - startTime;
      return {
        ...result,
        executionTimeMs: executionTime
      };

    } catch (error: any) {
      console.error(`❌ Step ${step.id} execution error:`, error);

      return {
        success: false,
        data: { error: error.message },
        metrics: {},
        confidence: 0,
        executionTimeMs: Date.now() - startTime
      };
    }
  }

  /**
   * Execute step with human approval (L0)
   */
  private async executeWithApproval(
    step: PlanStep,
    agent: any,
    context: AgentContext
  ): Promise<StepResult> {
    const stepStartTime = Date.now();

    // Generate draft result
    const draftResult = await agent.generateDraft(step.input, context);

    // Create approval request
    const approvalRequest = {
      stepId: step.id,
      agentType: step.agentType,
      draft: draftResult,
      requiredBy: new Date(Date.now() + (step.timeoutMinutes || 60) * 60 * 1000)
    };

    // In a real implementation, this would be sent to a human approval queue
    console.log(`📋 Step ${step.id} requires approval:`, approvalRequest);

    // For now, auto-approve for development
    return {
      success: true,
      data: draftResult,
      metrics: { approvalRequired: 1 },
      confidence: 0.8,
      executionTimeMs: Date.now() - stepStartTime
    };
  }

  /**
   * Execute step autonomously
   */
  private async executeAutonomously(
    step: PlanStep,
    agent: any,
    context: AgentContext
  ): Promise<StepResult> {
    const stepStartTime = Date.now();

    // Validate action with guardrail
    const action: AgentAction = {
      id: uuidv4(),
      agentType: step.agentType,
      type: `EXECUTE_${step.agentType}`,
      payload: step.input,
      riskLevel: 'LOW' as any, // Would be determined by agent
      requiresApproval: false,
      planId: context.planId,
      stepId: step.id,
      createdAt: new Date()
    };

    const validation = await this.guardrail.validateAction(action, context);
    if (!validation.valid) {
      throw new AREError(
        `Action validation failed: ${validation.violations.join(', ')}`,
        'ACTION_VALIDATION_FAILED'
      );
    }

    // Execute the agent
    const result = await agent.execute(step.input, context);

    return {
      success: true,
      data: result,
      metrics: result.metrics || {},
      confidence: result.confidence || 0.8,
      executionTimeMs: Date.now() - stepStartTime
    };
  }

  /**
   * Get agent instance for execution
   */
  private async getAgentInstance(agentType: AgentType): Promise<any> {
    // This would integrate with the agent registry/factory
    // For now, return a mock agent
    return {
      execute: async (input: any, context: AgentContext) => {
        console.log(`🤖 Mock executing ${agentType} with input:`, input);
        return {
          success: true,
          data: { mockResult: `Executed ${agentType}` },
          metrics: { executionTime: 100 },
          confidence: 0.9
        };
      },
      generateDraft: async (input: any, context: AgentContext) => {
        return { draft: `Draft for ${agentType}`, needsApproval: true };
      }
    };
  }

  /**
   * Determine execution order based on dependencies
   */
  private determineExecutionOrder(steps: PlanStep[], dependencies: any[]): string[] {
    const stepMap = new Map(steps.map(s => [s.id, s]));
    const dependencyMap = new Map<string, string[]>();

    // Build dependency graph
    dependencies.forEach(dep => {
      if (!dependencyMap.has(dep.toStepId)) {
        dependencyMap.set(dep.toStepId, []);
      }
      dependencyMap.get(dep.toStepId)!.push(dep.fromStepId);
    });

    // Topological sort
    const visited = new Set<string>();
    const visiting = new Set<string>();
    const order: string[] = [];

    const visit = (stepId: string) => {
      if (visited.has(stepId)) return;
      if (visiting.has(stepId)) {
        throw new AREError('Circular dependency detected', 'CIRCULAR_DEPENDENCY');
      }

      visiting.add(stepId);

      const deps = dependencyMap.get(stepId) || [];
      deps.forEach(depId => visit(depId));

      visiting.delete(stepId);
      visited.add(stepId);
      order.unshift(stepId); // Add to front for correct order
    };

    steps.forEach(step => visit(step.id));

    return order;
  }

  /**
   * Check if step dependencies are satisfied
   */
  private areDependenciesSatisfied(
    step: PlanStep,
    executedSteps: Map<string, PlanStep>,
    dependencies: any[]
  ): boolean {
    const stepDeps = dependencies.filter(d => d.toStepId === step.id);

    for (const dep of stepDeps) {
      const depStep = executedSteps.get(dep.fromStepId);
      if (!depStep) return false;

      // Check dependency condition
      if (dep.condition === 'SUCCESS') {
        if (depStep.status !== StepStatus.COMPLETED) return false;
      }
      // Add other condition checks as needed
    }

    return true;
  }

  /**
   * Schedule a failed step for retry
   */
  private async scheduleStepRetry(step: PlanStep, context: AgentContext): Promise<void> {
    const retryStep = {
      ...step,
      retryCount: step.retryCount + 1,
      status: StepStatus.PENDING
    };

    // In a real implementation, this would schedule the retry
    console.log(`🔄 Scheduled retry for step ${step.id} (attempt ${retryStep.retryCount})`);
  }
}