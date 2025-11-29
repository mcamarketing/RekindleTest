/**
 * ARE RAG (Retrieval-Augmented Generation) Service
 *
 * Provides context retrieval and memory access for ARE agents.
 * Integrates with vector stores and knowledge bases.
 */

import {
  AgentContext,
  AgentType
} from './types';

export interface ContextQuery {
  query: string;
  agentType: AgentType;
  context: AgentContext;
  limit?: number;
  filters?: Record<string, any>;
}

export interface RetrievedContext {
  documents: ContextDocument[];
  relevanceScores: number[];
  totalFound: number;
  queryTimeMs: number;
}

export interface ContextDocument {
  id: string;
  content: string;
  metadata: Record<string, any>;
  score: number;
  source: string;
  timestamp: Date;
}

export interface MemoryEntry {
  id: string;
  key: string;
  value: any;
  agentType: AgentType;
  context: AgentContext;
  ttl?: number; // Time to live in seconds
  createdAt: Date;
}

export class RAGService {
  private vectorStoreUrl?: string;
  private knowledgeBaseUrl?: string;

  constructor(vectorStoreUrl?: string, knowledgeBaseUrl?: string) {
    this.vectorStoreUrl = vectorStoreUrl;
    this.knowledgeBaseUrl = knowledgeBaseUrl;
  }

  /**
   * Get context for a specific lead
   */
  async getContextForLead(leadId: string, context: AgentContext): Promise<RetrievedContext> {
    console.log(`🔍 Getting context for lead ${leadId}`);

    const query: ContextQuery = {
      query: `lead context for ${leadId}`,
      agentType: context.memory.context.agentType || AgentType.RESEARCH,
      context,
      limit: 10,
      filters: { leadId, orgId: context.orgId }
    };

    return this.performRetrieval(query);
  }

  /**
   * Get context for a campaign
   */
  async getContextForCampaign(campaignId: string, context: AgentContext): Promise<RetrievedContext> {
    console.log(`📊 Getting context for campaign ${campaignId}`);

    const query: ContextQuery = {
      query: `campaign context for ${campaignId}`,
      agentType: context.memory.context.agentType || AgentType.SEQUENCING,
      context,
      limit: 15,
      filters: { campaignId, orgId: context.orgId }
    };

    return this.performRetrieval(query);
  }

  /**
   * Get best performing examples for a given context
   */
  async getBestPerformingExamples(params: {
    agentType: AgentType;
    objective: string;
    context: AgentContext;
    limit?: number;
  }): Promise<RetrievedContext> {
    const { agentType, objective, context, limit = 5 } = params;

    console.log(`🏆 Getting best examples for ${agentType}: ${objective}`);

    const query: ContextQuery = {
      query: `best performing examples for ${objective}`,
      agentType,
      context,
      limit,
      filters: {
        agentType,
        performance: 'high',
        orgId: context.orgId
      }
    };

    return this.performRetrieval(query);
  }

  /**
   * Store agent memory
   */
  async storeMemory(entry: Omit<MemoryEntry, 'id' | 'createdAt'>): Promise<string> {
    const memoryEntry: MemoryEntry = {
      ...entry,
      id: this.generateMemoryId(),
      createdAt: new Date()
    };

    console.log(`💾 Storing memory: ${memoryEntry.key} for ${entry.agentType}`);

    // In a real implementation, this would persist to Redis/PostgreSQL
    // For now, just log and return the ID
    await this.persistMemory(memoryEntry);

    return memoryEntry.id;
  }

  /**
   * Retrieve agent memory
   */
  async retrieveMemory(
    key: string,
    agentType: AgentType,
    context: AgentContext
  ): Promise<MemoryEntry | null> {
    console.log(`📖 Retrieving memory: ${key} for ${agentType}`);

    // In a real implementation, this would query the memory store
    return this.queryMemory(key, agentType, context);
  }

  /**
   * Update agent short-term memory
   */
  async updateShortTermMemory(
    agentType: AgentType,
    updates: Record<string, any>,
    context: AgentContext
  ): Promise<void> {
    console.log(`🔄 Updating short-term memory for ${agentType}`);

    const memoryKey = `short_term_${agentType}_${context.sessionId}`;

    // Merge with existing memory
    const existing = await this.retrieveMemory(memoryKey, agentType, context);
    const updatedValue = {
      ...existing?.value,
      ...updates,
      lastUpdated: new Date()
    };

    await this.storeMemory({
      key: memoryKey,
      value: updatedValue,
      agentType,
      context
    });
  }

  /**
   * Get context for copy generation
   */
  async getCopyContext(params: {
    persona: string;
    industry: string;
    context: AgentContext;
  }): Promise<RetrievedContext> {
    const { persona, industry, context } = params;

    const query: ContextQuery = {
      query: `effective copy examples for ${persona} in ${industry}`,
      agentType: AgentType.COPY,
      context,
      limit: 8,
      filters: {
        contentType: 'copy',
        persona,
        industry,
        performance: 'high'
      }
    };

    return this.performRetrieval(query);
  }

  /**
   * Get sequencing patterns
   */
  async getSequencingPatterns(params: {
    stage: string;
    channel: string;
    context: AgentContext;
  }): Promise<RetrievedContext> {
    const { stage, channel, context } = params;

    const query: ContextQuery = {
      query: `effective sequences for ${stage} stage using ${channel}`,
      agentType: AgentType.SEQUENCING,
      context,
      limit: 5,
      filters: {
        contentType: 'sequence',
        stage,
        channel,
        performance: 'high'
      }
    };

    return this.performRetrieval(query);
  }

  /**
   * Get objection handling examples
   */
  async getObjectionExamples(params: {
    objectionType: string;
    context: AgentContext;
  }): Promise<RetrievedContext> {
    const { objectionType, context } = params;

    const query: ContextQuery = {
      query: `successful responses to ${objectionType} objections`,
      agentType: AgentType.SEQUENCING,
      context,
      limit: 6,
      filters: {
        contentType: 'objection',
        objectionType,
        performance: 'high'
      }
    };

    return this.performRetrieval(query);
  }

  /**
   * Perform vector retrieval
   */
  private async performRetrieval(query: ContextQuery): Promise<RetrievedContext> {
    const startTime = Date.now();

    try {
      // In a real implementation, this would call the vector store API
      // For now, return mock results
      const mockDocuments: ContextDocument[] = [
        {
          id: 'doc-1',
          content: `Sample context for ${query.query}`,
          metadata: { source: 'knowledge_base', relevance: 0.95 },
          score: 0.95,
          source: 'knowledge_base',
          timestamp: new Date()
        },
        {
          id: 'doc-2',
          content: `Additional context related to ${query.agentType}`,
          metadata: { source: 'outcome_store', relevance: 0.87 },
          score: 0.87,
          source: 'outcome_store',
          timestamp: new Date()
        }
      ];

      return {
        documents: mockDocuments,
        relevanceScores: mockDocuments.map(d => d.score),
        totalFound: mockDocuments.length,
        queryTimeMs: Date.now() - startTime
      };

    } catch (error) {
      console.error('❌ Retrieval failed:', error);
      throw new Error(`Context retrieval failed: ${error}`);
    }
  }

  /**
   * Persist memory entry
   */
  private async persistMemory(entry: MemoryEntry): Promise<void> {
    // In a real implementation, this would save to Redis/PostgreSQL
    console.log(`💾 Persisted memory entry ${entry.id}`);
  }

  /**
   * Query memory store
   */
  private async queryMemory(
    key: string,
    agentType: AgentType,
    context: AgentContext
  ): Promise<MemoryEntry | null> {
    // In a real implementation, this would query Redis/PostgreSQL
    // For now, return null (no existing memory)
    return null;
  }

  /**
   * Generate unique memory ID
   */
  private generateMemoryId(): string {
    return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get RAG service health
   */
  getHealth(): {
    vectorStoreConnected: boolean;
    knowledgeBaseConnected: boolean;
    memoryStoreConnected: boolean;
  } {
    return {
      vectorStoreConnected: !!this.vectorStoreUrl,
      knowledgeBaseConnected: !!this.knowledgeBaseUrl,
      memoryStoreConnected: true // Assume local memory works
    };
  }
}

// Singleton instance
let ragServiceInstance: RAGService | null = null;

export function getRAGService(): RAGService {
  if (!ragServiceInstance) {
    // Check for URLs in environment
    const vectorStoreUrl = process.env.VECTOR_STORE_URL;
    const knowledgeBaseUrl = process.env.KNOWLEDGE_BASE_URL;

    ragServiceInstance = new RAGService(vectorStoreUrl, knowledgeBaseUrl);
  }
  return ragServiceInstance;
}

export function createRAGService(vectorStoreUrl?: string, knowledgeBaseUrl?: string): RAGService {
  return new RAGService(vectorStoreUrl, knowledgeBaseUrl);
}