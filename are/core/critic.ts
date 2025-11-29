/**
 * ARE Critic Agent
 *
 * Evaluates execution outcomes, provides quality assessment, and generates
 * learning signals for continuous improvement of the ARE system.
 */

import {
  Outcome,
  AgentType,
  AgentContext,
  OutcomeType,
  RiskLevel
} from './types';
import { getMessageBus } from './message-bus';

export class CriticAgent {
  private messageBus = getMessageBus();

  /**
   * Evaluate a completed plan execution
   */
  async evaluatePlan(planId: string, context: AgentContext): Promise<PlanEvaluation> {
    console.log(`🔍 Evaluating plan ${planId}`);

    try {
      // Gather all outcomes for this plan
      const outcomes = await this.gatherPlanOutcomes(planId);

      // Analyze performance metrics
      const metrics = this.analyzePerformanceMetrics(outcomes);

      // Assess quality and effectiveness
      const quality = this.assessExecutionQuality(outcomes, metrics);

      // Generate improvement recommendations
      const recommendations = this.generateRecommendations(outcomes, metrics, quality);

      // Detect anomalies
      const anomalies = this.detectAnomalies(outcomes, metrics);

      const evaluation: PlanEvaluation = {
        planId,
        overallScore: quality.overallScore,
        metrics,
        quality,
        recommendations,
        anomalies,
        evaluatedAt: new Date()
      };

      // Publish evaluation results
      await this.messageBus.publish({
        type: 'ARE.plan.evaluated' as any,
        from: AgentType.CRITIC,
        payload: evaluation,
        correlationId: context.sessionId
      });

      // Trigger learning updates if needed
      if (recommendations.length > 0) {
        await this.triggerLearningUpdates(evaluation, context);
      }

      console.log(`✅ Plan ${planId} evaluation complete: ${quality.overallScore.toFixed(2)}/1.0`);
      return evaluation;

    } catch (error) {
      console.error('❌ Plan evaluation failed:', error);
      throw new AREError('Plan evaluation failed', 'EVALUATION_ERROR', { planId });
    }
  }

  /**
   * Evaluate individual agent performance
   */
  async evaluateAgentPerformance(
    agentType: AgentType,
    outcomes: Outcome[],
    context: AgentContext
  ): Promise<AgentPerformance> {
    console.log(`📊 Evaluating ${agentType} performance`);

    const agentOutcomes = outcomes.filter(o => o.agentType === agentType);

    if (agentOutcomes.length === 0) {
      return {
        agentType,
        sampleSize: 0,
        metrics: {},
        quality: { overallScore: 0, strengths: [], weaknesses: [] },
        recommendations: []
      };
    }

    // Calculate agent-specific metrics
    const metrics = this.calculateAgentMetrics(agentType, agentOutcomes);

    // Assess agent quality
    const quality = this.assessAgentQuality(agentType, metrics);

    // Generate agent-specific recommendations
    const recommendations = this.generateAgentRecommendations(agentType, metrics, quality);

    const performance: AgentPerformance = {
      agentType,
      sampleSize: agentOutcomes.length,
      metrics,
      quality,
      recommendations
    };

    // Publish agent performance
    await this.messageBus.publish({
      type: 'ARE.agent.performance' as any,
      from: AgentType.CRITIC,
      payload: performance,
      correlationId: context.sessionId
    });

    return performance;
  }

  /**
   * Process real-time outcome feedback
   */
  async processOutcome(outcome: Outcome, context: AgentContext): Promise<void> {
    console.log(`📈 Processing outcome: ${outcome.type} for ${outcome.agentType}`);

    try {
      // Immediate quality assessment
      const quality = this.assessOutcomeQuality(outcome);

      // Update running metrics
      await this.updateRunningMetrics(outcome, quality);

      // Check for immediate intervention needs
      const intervention = this.checkInterventionNeeded(outcome, quality);
      if (intervention.needed) {
        await this.triggerIntervention(intervention, context);
      }

      // Publish outcome analysis
      await this.messageBus.publish({
        type: 'ARE.outcome.analyzed' as any,
        from: AgentType.CRITIC,
        payload: {
          outcome,
          quality,
          intervention: intervention.needed ? intervention : undefined
        },
        correlationId: context.sessionId
      });

    } catch (error) {
      console.error('❌ Outcome processing failed:', error);
    }
  }

  /**
   * Gather all outcomes for a plan
   */
  private async gatherPlanOutcomes(planId: string): Promise<Outcome[]> {
    // In a real implementation, this would query the outcome store
    // For now, return mock data
    return [
      {
        id: 'outcome-1',
        type: OutcomeType.EMAIL_REPLY,
        planId,
        agentType: AgentType.COPY,
        timestamp: new Date(),
        value: 1,
        metadata: { replyQuality: 0.8 },
        confidence: 0.9
      },
      {
        id: 'outcome-2',
        type: OutcomeType.MEETING_BOOKED,
        planId,
        agentType: AgentType.SEQUENCING,
        timestamp: new Date(),
        value: 1,
        metadata: { meetingValue: 5000 },
        confidence: 0.95
      }
    ];
  }

  /**
   * Analyze performance metrics from outcomes
   */
  private analyzePerformanceMetrics(outcomes: Outcome[]): PerformanceMetrics {
    const metrics: PerformanceMetrics = {
      totalOutcomes: outcomes.length,
      successRate: 0,
      avgConfidence: 0,
      avgValue: 0,
      responseTime: 0,
      conversionRate: 0,
      revenueImpact: 0
    };

    if (outcomes.length === 0) return metrics;

    // Calculate basic metrics
    const successfulOutcomes = outcomes.filter(o => o.value > 0);
    metrics.successRate = successfulOutcomes.length / outcomes.length;

    metrics.avgConfidence = outcomes.reduce((sum, o) => sum + (o.confidence || 0), 0) / outcomes.length;
    metrics.avgValue = outcomes.reduce((sum, o) => sum + o.value, 0) / outcomes.length;

    // Calculate conversion metrics
    const replies = outcomes.filter(o => o.type === OutcomeType.EMAIL_REPLY).length;
    const meetings = outcomes.filter(o => o.type === OutcomeType.MEETING_BOOKED).length;
    metrics.conversionRate = replies > 0 ? meetings / replies : 0;

    // Calculate revenue impact
    metrics.revenueImpact = outcomes
      .filter(o => o.type === OutcomeType.REVENUE_WON)
      .reduce((sum, o) => sum + o.value, 0);

    return metrics;
  }

  /**
   * Assess overall execution quality
   */
  private assessExecutionQuality(outcomes: Outcome[], metrics: PerformanceMetrics): QualityAssessment {
    let overallScore = 0;

    // Weight different factors
    overallScore += metrics.successRate * 0.4;        // 40% - success rate
    overallScore += metrics.avgConfidence * 0.2;      // 20% - confidence
    overallScore += Math.min(metrics.conversionRate, 1) * 0.2; // 20% - conversion (capped)
    overallScore += (metrics.revenueImpact > 0 ? 1 : 0) * 0.2; // 20% - revenue generation

    // Identify strengths and weaknesses
    const strengths: string[] = [];
    const weaknesses: string[] = [];

    if (metrics.successRate > 0.8) strengths.push('High success rate');
    else if (metrics.successRate < 0.5) weaknesses.push('Low success rate');

    if (metrics.avgConfidence > 0.8) strengths.push('High confidence in actions');
    else if (metrics.avgConfidence < 0.6) weaknesses.push('Low confidence in actions');

    if (metrics.conversionRate > 0.1) strengths.push('Strong reply-to-meeting conversion');
    else weaknesses.push('Weak conversion performance');

    if (metrics.revenueImpact > 0) strengths.push('Revenue generation achieved');
    else weaknesses.push('No revenue impact');

    return {
      overallScore: Math.min(overallScore, 1.0),
      strengths,
      weaknesses
    };
  }

  /**
   * Generate improvement recommendations
   */
  private generateRecommendations(
    outcomes: Outcome[],
    metrics: PerformanceMetrics,
    quality: QualityAssessment
  ): Recommendation[] {
    const recommendations: Recommendation[] = [];

    // Success rate recommendations
    if (metrics.successRate < 0.7) {
      recommendations.push({
        type: 'IMPROVE_SUCCESS_RATE',
        priority: 'HIGH',
        description: 'Improve overall success rate through better targeting and messaging',
        actions: ['Review ICP matching', 'Optimize copy variants', 'Adjust send timing']
      });
    }

    // Confidence recommendations
    if (metrics.avgConfidence < 0.75) {
      recommendations.push({
        type: 'INCREASE_CONFIDENCE',
        priority: 'MEDIUM',
        description: 'Increase decision confidence through better data and models',
        actions: ['Enhance training data', 'Improve feature engineering', 'Add validation checks']
      });
    }

    // Conversion recommendations
    if (metrics.conversionRate < 0.05) {
      recommendations.push({
        type: 'BOOST_CONVERSION',
        priority: 'HIGH',
        description: 'Improve reply-to-meeting conversion rates',
        actions: ['Optimize follow-up sequences', 'Improve objection handling', 'Enhance personalization']
      });
    }

    // Revenue recommendations
    if (metrics.revenueImpact === 0) {
      recommendations.push({
        type: 'ENABLE_REVENUE_GENERATION',
        priority: 'CRITICAL',
        description: 'Focus on revenue-generating outcomes',
        actions: ['Prioritize high-value prospects', 'Optimize meeting booking flow', 'Improve qualification']
      });
    }

    return recommendations;
  }

  /**
   * Detect performance anomalies
   */
  private detectAnomalies(outcomes: Outcome[], metrics: PerformanceMetrics): Anomaly[] {
    const anomalies: Anomaly[] = [];

    // Check for sudden drops
    const recentOutcomes = outcomes.slice(-10); // Last 10 outcomes
    const recentSuccessRate = recentOutcomes.filter(o => o.value > 0).length / recentOutcomes.length;

    if (recentSuccessRate < metrics.successRate * 0.5) {
      anomalies.push({
        type: 'SUCCESS_RATE_DROP',
        severity: 'HIGH',
        description: 'Recent success rate significantly below average',
        metric: 'successRate',
        expected: metrics.successRate,
        actual: recentSuccessRate,
        detectedAt: new Date()
      });
    }

    // Check for spam/unsubscribe spikes
    const spamOutcomes = outcomes.filter(o => o.type === OutcomeType.SPAM_REPORT);
    if (spamOutcomes.length > outcomes.length * 0.05) { // >5% spam rate
      anomalies.push({
        type: 'SPAM_RATE_SPIKE',
        severity: 'CRITICAL',
        description: 'Abnormally high spam report rate',
        metric: 'spamRate',
        expected: 0.02,
        actual: spamOutcomes.length / outcomes.length,
        detectedAt: new Date()
      });
    }

    return anomalies;
  }

  /**
   * Calculate agent-specific metrics
   */
  private calculateAgentMetrics(agentType: AgentType, outcomes: Outcome[]): Record<string, number> {
    const metrics: Record<string, number> = {};

    switch (agentType) {
      case AgentType.COPY:
        metrics.replyRate = outcomes.filter(o => o.type === OutcomeType.EMAIL_REPLY).length / outcomes.length;
        metrics.avgReplyQuality = outcomes
          .filter(o => o.metadata?.replyQuality)
          .reduce((sum, o) => sum + (o.metadata?.replyQuality || 0), 0) / outcomes.length;
        break;

      case AgentType.SEQUENCING:
        metrics.meetingRate = outcomes.filter(o => o.type === OutcomeType.MEETING_BOOKED).length / outcomes.length;
        metrics.avgSequenceLength = outcomes
          .filter(o => o.metadata?.sequenceLength)
          .reduce((sum, o) => sum + (o.metadata?.sequenceLength || 0), 0) / outcomes.length;
        break;

      case AgentType.REVIVAL:
        metrics.revivalSuccess = outcomes.filter(o => o.value > 0).length / outcomes.length;
        metrics.avgTimeToResponse = outcomes
          .filter(o => o.metadata?.timeToResponse)
          .reduce((sum, o) => sum + (o.metadata?.timeToResponse || 0), 0) / outcomes.length;
        break;
    }

    return metrics;
  }

  /**
   * Assess agent quality
   */
  private assessAgentQuality(agentType: AgentType, metrics: Record<string, number>): QualityAssessment {
    let score = 0;
    const strengths: string[] = [];
    const weaknesses: string[] = [];

    switch (agentType) {
      case AgentType.COPY:
        if (metrics.replyRate > 0.1) {
          score += 0.5;
          strengths.push('Good reply generation');
        } else {
          weaknesses.push('Low reply rates');
        }
        if (metrics.avgReplyQuality > 0.7) {
          score += 0.5;
          strengths.push('High-quality replies');
        }
        break;

      case AgentType.SEQUENCING:
        if (metrics.meetingRate > 0.05) {
          score += 0.6;
          strengths.push('Effective meeting booking');
        } else {
          weaknesses.push('Poor meeting conversion');
        }
        if (metrics.avgSequenceLength < 10) {
          score += 0.4;
          strengths.push('Efficient sequences');
        }
        break;
    }

    return {
      overallScore: Math.min(score, 1.0),
      strengths,
      weaknesses
    };
  }

  /**
   * Generate agent-specific recommendations
   */
  private generateAgentRecommendations(
    agentType: AgentType,
    metrics: Record<string, number>,
    quality: QualityAssessment
  ): string[] {
    const recommendations: string[] = [];

    switch (agentType) {
      case AgentType.COPY:
        if (metrics.replyRate < 0.05) {
          recommendations.push('Experiment with different subject lines and hooks');
        }
        if (metrics.avgReplyQuality < 0.6) {
          recommendations.push('Improve personalization and value propositions');
        }
        break;

      case AgentType.SEQUENCING:
        if (metrics.meetingRate < 0.03) {
          recommendations.push('Optimize follow-up timing and messaging');
        }
        if (metrics.avgSequenceLength > 15) {
          recommendations.push('Shorten sequences to reduce fatigue');
        }
        break;
    }

    return recommendations;
  }

  /**
   * Assess individual outcome quality
   */
  private assessOutcomeQuality(outcome: Outcome): OutcomeQuality {
    let quality = 0.5; // Default neutral

    // Adjust based on outcome type and value
    switch (outcome.type) {
      case OutcomeType.MEETING_BOOKED:
        quality = outcome.value > 0 ? 0.9 : 0.1;
        break;
      case OutcomeType.EMAIL_REPLY:
        quality = Math.min((outcome.metadata?.replyQuality || 0.5) * 1.2, 1.0);
        break;
      case OutcomeType.SPAM_REPORT:
      case OutcomeType.UNSUBSCRIBE:
        quality = 0.1;
        break;
      case OutcomeType.REVENUE_WON:
        quality = 1.0;
        break;
    }

    // Factor in confidence
    quality *= outcome.confidence || 1.0;

    return {
      score: quality,
      factors: [`Outcome type: ${outcome.type}`, `Value: ${outcome.value}`],
      riskLevel: quality < 0.3 ? RiskLevel.HIGH : quality > 0.8 ? RiskLevel.LOW : RiskLevel.MEDIUM
    };
  }

  /**
   * Update running performance metrics
   */
  private async updateRunningMetrics(outcome: Outcome, quality: OutcomeQuality): Promise<void> {
    // In a real implementation, this would update persistent metrics
    console.log(`📊 Updated metrics for ${outcome.agentType}: quality ${quality.score.toFixed(2)}`);
  }

  /**
   * Check if intervention is needed
   */
  private checkInterventionNeeded(outcome: Outcome, quality: OutcomeQuality): InterventionCheck {
    if (outcome.type === OutcomeType.SPAM_REPORT && quality.score < 0.2) {
      return {
        needed: true,
        type: 'AUTONOMY_REDUCTION',
        reason: 'High spam risk detected',
        severity: 'CRITICAL'
      };
    }

    if (outcome.type === OutcomeType.UNSUBSCRIBE && quality.score < 0.3) {
      return {
        needed: true,
        type: 'SEQUENCE_PAUSE',
        reason: 'Unsubscribe spike detected',
        severity: 'HIGH'
      };
    }

    return { needed: false };
  }

  /**
   * Trigger intervention for anomalies
   */
  private async triggerIntervention(intervention: InterventionCheck, context: AgentContext): Promise<void> {
    console.log(`🚨 Triggering intervention: ${intervention.type} - ${intervention.reason}`);

    await this.messageBus.publish({
      type: 'ARE.intervention.triggered' as any,
      from: AgentType.CRITIC,
      payload: intervention,
      correlationId: context.sessionId
    });
  }

  /**
   * Trigger learning updates based on evaluation
   */
  private async triggerLearningUpdates(evaluation: PlanEvaluation, context: AgentContext): Promise<void> {
    // Trigger bandit updates
    if (evaluation.recommendations.some(r => r.type.includes('COPY'))) {
      await this.messageBus.publish({
        type: 'ARE.bandit.update' as any,
        from: AgentType.CRITIC,
        payload: { type: 'COPY', evaluation },
        correlationId: context.sessionId
      });
    }

    // Trigger autonomy calibration
    if (evaluation.anomalies.length > 0) {
      await this.messageBus.publish({
        type: 'ARE.autonomy.adjust' as any,
        from: AgentType.CRITIC,
        payload: { evaluation, anomalies: evaluation.anomalies },
        correlationId: context.sessionId
      });
    }
  }
}

interface PlanEvaluation {
  planId: string;
  overallScore: number;
  metrics: PerformanceMetrics;
  quality: QualityAssessment;
  recommendations: Recommendation[];
  anomalies: Anomaly[];
  evaluatedAt: Date;
}

interface PerformanceMetrics {
  totalOutcomes: number;
  successRate: number;
  avgConfidence: number;
  avgValue: number;
  responseTime: number;
  conversionRate: number;
  revenueImpact: number;
}

interface QualityAssessment {
  overallScore: number;
  strengths: string[];
  weaknesses: string[];
}

interface Recommendation {
  type: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  actions: string[];
}

interface Anomaly {
  type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  metric: string;
  expected: number;
  actual: number;
  detectedAt: Date;
}

interface AgentPerformance {
  agentType: AgentType;
  sampleSize: number;
  metrics: Record<string, number>;
  quality: QualityAssessment;
  recommendations: string[];
}

interface OutcomeQuality {
  score: number;
  factors: string[];
  riskLevel: RiskLevel;
}

interface InterventionCheck {
  needed: boolean;
  type?: string;
  reason?: string;
  severity?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}