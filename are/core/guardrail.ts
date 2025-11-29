/**
 * ARE Guardrail Agent
 *
 * Safety and compliance enforcement layer for all ARE operations.
 * Validates plans, actions, and content against policies and constraints.
 */

import {
  Plan,
  AgentAction,
  ValidationResult,
  RiskLevel,
  AgentContext,
  AREError,
  PolicyViolationError,
  AutonomyLimitError
} from './types';

export class GuardrailAgent {
  /**
   * Validate a plan before execution
   */
  async validatePlan(plan: Plan, context: AgentContext): Promise<ValidationResult> {
    const violations: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    // Check autonomy level constraints
    if (this.isAutonomyLevelViolated(plan.autonomyLevel, context)) {
      violations.push(`Autonomy level ${plan.autonomyLevel} exceeds context limit ${context.autonomyLevel}`);
    }

    // Check risk assessment
    if (plan.riskAssessment.requiresApproval && plan.autonomyLevel !== 'L0') {
      violations.push('High-risk plan requires human approval');
    }

    // Check resource constraints
    const resourceCheck = await this.checkResourceConstraints(plan, context);
    violations.push(...resourceCheck.violations);
    warnings.push(...resourceCheck.warnings);

    // Determine risk level
    let riskLevel = RiskLevel.LOW;
    if (violations.length > 0) {
      riskLevel = RiskLevel.CRITICAL;
    } else if (warnings.length > 0) {
      riskLevel = RiskLevel.MEDIUM;
    }

    return {
      valid: violations.length === 0,
      riskLevel,
      violations,
      warnings,
      suggestions
    };
  }

  /**
   * Validate an individual action
   */
  async validateAction(action: AgentAction, context: AgentContext): Promise<ValidationResult> {
    const violations: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    // Check content safety if applicable
    if (action.type.includes('CONTENT') || action.type.includes('MESSAGE')) {
      const contentValidation = await this.validateContent(action.payload, context);
      violations.push(...contentValidation.violations);
      warnings.push(...contentValidation.warnings);
    }

    // Check rate limits
    const rateCheck = await this.checkRateLimits(action, context);
    if (!rateCheck.allowed) {
      violations.push(`Rate limit exceeded: ${rateCheck.reason}`);
    }

    // Check policy compliance
    const policyCheck = await this.checkPolicyCompliance(action, context);
    violations.push(...policyCheck.violations);
    warnings.push(...policyCheck.warnings);

    let riskLevel = RiskLevel.LOW;
    if (violations.length > 0) {
      riskLevel = RiskLevel.HIGH;
    } else if (warnings.length > 0) {
      riskLevel = RiskLevel.MEDIUM;
    }

    return {
      valid: violations.length === 0,
      riskLevel,
      violations,
      warnings,
      suggestions
    };
  }

  /**
   * Validate message content
   */
  async validateContent(payload: Record<string, any>, context: AgentContext): Promise<ValidationResult> {
    const violations: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    // Basic content validation - placeholder for more sophisticated checks
    const content = payload.body || payload.content || '';
    if (!content || content.length < 10) {
      violations.push('Content too short or empty');
    }

    // Check for potentially harmful content patterns
    const harmfulPatterns = [
      /urgent.*action.*required/i,
      /limited.*time.*offer/i,
      /guaranteed.*results/i
    ];

    for (const pattern of harmfulPatterns) {
      if (pattern.test(content)) {
        warnings.push(`Potentially spammy content pattern detected: ${pattern}`);
      }
    }

    return {
      valid: violations.length === 0,
      riskLevel: violations.length > 0 ? RiskLevel.HIGH : RiskLevel.LOW,
      violations,
      warnings,
      suggestions
    };
  }

  /**
   * Check if autonomy level is violated
   */
  private isAutonomyLevelViolated(planLevel: string, context: AgentContext): boolean {
    const levels = ['L0', 'L1', 'L2', 'L3'];
    const planIndex = levels.indexOf(planLevel);
    const contextIndex = levels.indexOf(context.autonomyLevel);

    return planIndex > contextIndex;
  }

  /**
   * Check resource constraints
   */
  private async checkResourceConstraints(plan: Plan, context: AgentContext): Promise<ValidationResult> {
    // Placeholder - integrate with actual resource monitoring
    return {
      valid: true,
      riskLevel: RiskLevel.LOW,
      violations: [],
      warnings: [],
      suggestions: []
    };
  }

  /**
   * Check rate limits
   */
  private async checkRateLimits(action: AgentAction, context: AgentContext): Promise<{
    allowed: boolean;
    reason?: string;
  }> {
    // Placeholder - integrate with rate limiting service
    return { allowed: true };
  }

  /**
   * Check policy compliance
   */
  private async checkPolicyCompliance(action: AgentAction, context: AgentContext): Promise<ValidationResult> {
    // Placeholder - integrate with policy engine
    return {
      valid: true,
      riskLevel: RiskLevel.LOW,
      violations: [],
      warnings: [],
      suggestions: []
    };
  }
}