/**
 * ARE Agents Registry
 *
 * Factory and registry for ARE agents.
 * Currently supports core brainstem agents, with placeholders for others.
 */

import { AgentType } from './types';

// Import implemented agent classes
import { PlannerAgent } from './planner';
import { ExecutorAgent } from './executor';
import { CriticAgent } from './critic';
import { GuardrailAgent } from './guardrail';
import { getRAGService } from './rag-service';

/**
 * Agent factory function
 * Currently supports core brainstem agents only.
 * Other agents will be implemented in future phases.
 */
export function getAgentInstance(type: AgentType): any {
  switch (type) {
    // Core agents (implemented)
    case AgentType.PLANNER:
      return new PlannerAgent(getAgentInstance(AgentType.GUARDRAIL));
    case AgentType.EXECUTOR:
      return new ExecutorAgent(getAgentInstance(AgentType.GUARDRAIL));
    case AgentType.CRITIC:
      return new CriticAgent();
    case AgentType.GUARDRAIL:
      return new GuardrailAgent();
    case AgentType.RAG_SERVICE:
      return getRAGService();

    // Placeholder for unimplemented agents
    default:
      throw new Error(`Agent type ${type} not yet implemented. Currently supporting: PLANNER, EXECUTOR, CRITIC, GUARDRAIL, RAG_SERVICE`);
  }
}

/**
 * Check if an agent type is enabled in configuration
 */
export function isAgentEnabled(type: AgentType, config?: any): boolean {
  if (!config) return true; // Default to enabled

  const category = getAgentCategory(type);
  const enabledAgents = config.agents?.[category]?.enabled || [];

  return enabledAgents.includes(type);
}

/**
 * Get agent category
 */
export function getAgentCategory(type: AgentType): string {
  if ([AgentType.PLANNER, AgentType.EXECUTOR, AgentType.CRITIC, AgentType.GUARDRAIL, AgentType.RAG_SERVICE].includes(type)) {
    return 'core';
  }
  if ([AgentType.REVIVAL, AgentType.SEQUENCING, AgentType.COPY, AgentType.RESEARCH, AgentType.PERSONALIZATION, AgentType.MULTI_TOUCH].includes(type)) {
    return 'revenue';
  }
  if ([AgentType.SEND_TIME_BANDIT, AgentType.COPY_BANDIT, AgentType.COHORT_BANDIT, AgentType.AUTONOMY_CALIBRATOR, AgentType.ANOMALY_DETECTOR].includes(type)) {
    return 'optimization';
  }
  if ([AgentType.ICP_BUILDER, AgentType.FORECASTER, AgentType.LEAKAGE_DETECTOR, AgentType.RISK_SENTINEL, AgentType.CHURN_PREDICTOR].includes(type)) {
    return 'strategic';
  }
  return 'unknown';
}

/**
 * Get agent priority for execution ordering
 */
export function getAgentPriority(type: AgentType): number {
  const priorities: Record<AgentType, number> = {
    // Core agents (highest priority)
    [AgentType.PLANNER]: 10,
    [AgentType.EXECUTOR]: 9,
    [AgentType.GUARDRAIL]: 8,
    [AgentType.CRITIC]: 7,
    [AgentType.RAG_SERVICE]: 6,

    // Revenue agents
    [AgentType.RESEARCH]: 5,
    [AgentType.PERSONALIZATION]: 5,
    [AgentType.REVIVAL]: 4,
    [AgentType.COPY]: 4,
    [AgentType.SEQUENCING]: 3,
    [AgentType.MULTI_TOUCH]: 3,

    // Optimization agents
    [AgentType.ANOMALY_DETECTOR]: 6,
    [AgentType.AUTONOMY_CALIBRATOR]: 5,
    [AgentType.SEND_TIME_BANDIT]: 4,
    [AgentType.COPY_BANDIT]: 4,
    [AgentType.COHORT_BANDIT]: 4,

    // Strategic agents
    [AgentType.RISK_SENTINEL]: 7,
    [AgentType.LEAKAGE_DETECTOR]: 6,
    [AgentType.ICP_BUILDER]: 5,
    [AgentType.FORECASTER]: 5,
    [AgentType.CHURN_PREDICTOR]: 4
  };

  return priorities[type] || 1;
}

/**
 * Get all available agent types
 */
export function getAllAgentTypes(): AgentType[] {
  return Object.values(AgentType);
}

/**
 * Get agent types by category
 */
export function getAgentTypesByCategory(category: string): AgentType[] {
  return getAllAgentTypes().filter(type => getAgentCategory(type) === category);
}

/**
 * Validate agent dependencies
 * Currently only supports implemented core agents
 */
export function validateAgentDependencies(type: AgentType): AgentType[] {
  const dependencies: Partial<Record<AgentType, AgentType[]>> = {
    [AgentType.PLANNER]: [AgentType.GUARDRAIL, AgentType.RAG_SERVICE],
    [AgentType.EXECUTOR]: [AgentType.GUARDRAIL],
    // Other dependencies will be added as agents are implemented
  };

  return dependencies[type] || [];
}