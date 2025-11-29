/**
 * ARE Message Bus
 *
 * Lightweight internal bus interface for agents to communicate.
 * Provides publish/subscribe pattern for inter-agent coordination.
 */

import { EventEmitter } from 'events';
import Redis from 'ioredis';
import { AgentType, AREError } from './types';

export enum MessageType {
  // Planning messages
  PLAN_CREATED = 'ARE.plan.created',
  PLAN_VALIDATED = 'ARE.plan.validated',
  PLAN_EXECUTING = 'ARE.plan.executing',
  PLAN_COMPLETED = 'ARE.plan.completed',
  PLAN_FAILED = 'ARE.plan.failed',

  // Execution messages
  STEP_STARTED = 'ARE.step.started',
  STEP_COMPLETED = 'ARE.step.completed',
  STEP_FAILED = 'ARE.step.failed',

  // Outcome messages
  OUTCOME_RECORDED = 'ARE.outcome.recorded',
  OUTCOME_ANALYZED = 'ARE.outcome.analyzed',

  // Agent coordination
  AGENT_REQUEST = 'ARE.agent.request',
  AGENT_RESPONSE = 'ARE.agent.response',

  // Control messages
  AUTONOMY_ADJUSTED = 'ARE.autonomy.adjusted',
  POLICY_VIOLATION = 'ARE.policy.violation',
  ANOMALY_DETECTED = 'ARE.anomaly.detected',

  // Learning messages
  MODEL_UPDATED = 'ARE.model.updated',
  BANDIT_UPDATED = 'ARE.bandit.updated'
}

export interface Message {
  id: string;
  type: MessageType;
  from: AgentType | string;
  to?: AgentType | string;
  payload: Record<string, any>;
  correlationId?: string;
  timestamp: Date;
  ttl?: number; // Time to live in seconds
}

export interface Subscription {
  id: string;
  pattern: string; // e.g., "ARE.*", "ARE.plan.*"
  handler: (message: Message) => Promise<void> | void;
  agentType?: AgentType;
}

export class MessageBus {
  private emitter: EventEmitter;
  private redis?: Redis;
  private subscriptions: Map<string, Subscription> = new Map();
  private isDistributed: boolean = false;

  constructor(redisUrl?: string) {
    this.emitter = new EventEmitter();
    this.emitter.setMaxListeners(100); // Allow more listeners for agent communication

    if (redisUrl) {
      this.redis = new Redis(redisUrl);
      this.isDistributed = true;
      this.setupRedisSubscription();
    }
  }

  /**
   * Publish a message to the bus
   */
  async publish(message: Omit<Message, 'id' | 'timestamp'>): Promise<void> {
    const fullMessage: Message = {
      ...message,
      id: this.generateMessageId(),
      timestamp: new Date()
    };

    try {
      if (this.isDistributed && this.redis) {
        // Publish to Redis for distributed agents
        await this.redis.publish('are-messages', JSON.stringify(fullMessage));
      } else {
        // Local emission
        this.emitter.emit(message.type, fullMessage);
        this.emitter.emit('ARE.*', fullMessage); // Wildcard for all ARE messages
      }

      console.log(`📡 Published ${message.type} from ${message.from}`);
    } catch (error) {
      console.error('❌ Failed to publish message:', error);
      throw new AREError('Message publish failed', 'MESSAGE_BUS_ERROR', { message: fullMessage });
    }
  }

  /**
   * Subscribe to messages matching a pattern
   */
  subscribe(subscription: Omit<Subscription, 'id'>): string {
    const id = this.generateSubscriptionId();
    const fullSubscription: Subscription = {
      ...subscription,
      id
    };

    this.subscriptions.set(id, fullSubscription);

    if (this.isDistributed && this.redis) {
      // Redis pattern subscription would be handled in setupRedisSubscription
    } else {
      // Local subscription
      this.emitter.on(subscription.pattern, fullSubscription.handler);
    }

    console.log(`👂 Subscribed to ${subscription.pattern} by ${subscription.agentType || 'system'}`);
    return id;
  }

  /**
   * Unsubscribe from messages
   */
  unsubscribe(subscriptionId: string): void {
    const subscription = this.subscriptions.get(subscriptionId);
    if (!subscription) return;

    if (this.isDistributed && this.redis) {
      // Redis unsubscription
    } else {
      this.emitter.off(subscription.pattern, subscription.handler);
    }

    this.subscriptions.delete(subscriptionId);
    console.log(`🔕 Unsubscribed from ${subscription.pattern}`);
  }

  /**
   * Send a request to a specific agent and wait for response
   */
  async request(
    to: AgentType,
    type: string,
    payload: Record<string, any>,
    timeoutMs: number = 30000
  ): Promise<Record<string, any>> {
    return new Promise((resolve, reject) => {
      const correlationId = this.generateMessageId();
      const timeout = setTimeout(() => {
        reject(new AREError(`Request timeout: ${type}`, 'REQUEST_TIMEOUT', { to, type }));
      }, timeoutMs);

      // Subscribe to response
      const responsePattern = `ARE.agent.response.${correlationId}`;
      const subscriptionId = this.subscribe({
        pattern: responsePattern,
        handler: (message: Message) => {
          clearTimeout(timeout);
          this.unsubscribe(subscriptionId);
          resolve(message.payload);
        }
      });

      // Send request
      this.publish({
        type: MessageType.AGENT_REQUEST,
        from: 'MESSAGE_BUS',
        to,
        payload: {
          requestType: type,
          data: payload,
          correlationId
        },
        correlationId
      }).catch(error => {
        clearTimeout(timeout);
        this.unsubscribe(subscriptionId);
        reject(error);
      });
    });
  }

  /**
   * Reply to a request
   */
  async reply(correlationId: string, payload: Record<string, any>): Promise<void> {
    await this.publish({
      type: `ARE.agent.response.${correlationId}` as MessageType,
      from: 'MESSAGE_BUS',
      payload,
      correlationId
    });
  }

  /**
   * Broadcast a message to all agents
   */
  async broadcast(from: AgentType, type: string, payload: Record<string, any>): Promise<void> {
    await this.publish({
      type: type as MessageType,
      from,
      payload,
      ttl: 300 // 5 minutes TTL
    });
  }

  /**
   * Get bus health and statistics
   */
  getHealth(): {
    isDistributed: boolean;
    subscriptionCount: number;
    emitterListenerCount: number;
    redisConnected?: boolean;
  } {
    return {
      isDistributed: this.isDistributed,
      subscriptionCount: this.subscriptions.size,
      emitterListenerCount: this.emitter.listenerCount('ARE.*'),
      redisConnected: this.redis?.status === 'ready'
    };
  }

  /**
   * Gracefully shutdown the message bus
   */
  async shutdown(): Promise<void> {
    console.log('🛑 Shutting down ARE Message Bus...');

    // Clear all subscriptions
    for (const [id] of this.subscriptions) {
      this.unsubscribe(id);
    }

    // Close Redis connection
    if (this.redis) {
      await this.redis.quit();
    }

    // Remove all listeners
    this.emitter.removeAllListeners();

    console.log('✅ ARE Message Bus shut down');
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateSubscriptionId(): string {
    return `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private setupRedisSubscription(): void {
    if (!this.redis) return;

    this.redis.on('message', (channel, message) => {
      if (channel === 'are-messages') {
        try {
          const parsedMessage: Message = JSON.parse(message);
          // Emit locally for handlers
          this.emitter.emit(parsedMessage.type, parsedMessage);
          this.emitter.emit('ARE.*', parsedMessage);
        } catch (error) {
          console.error('❌ Failed to parse Redis message:', error);
        }
      }
    });

    this.redis.subscribe('are-messages');
  }
}

// Singleton instance
let messageBusInstance: MessageBus | null = null;

export function getMessageBus(): MessageBus {
  if (!messageBusInstance) {
    // Check for Redis URL in environment
    const redisUrl = process.env.REDIS_URL;
    messageBusInstance = new MessageBus(redisUrl);
  }
  return messageBusInstance;
}

export function createMessageBus(redisUrl?: string): MessageBus {
  return new MessageBus(redisUrl);
}