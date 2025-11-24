// @ts-nocheck
// Production-ready: Require API_URL in production, allow localhost only in development
const API_BASE_URL = (() => {
  const apiUrl = import.meta.env.VITE_API_URL;

  // In production, API_URL is required
  if (import.meta.env.PROD && !apiUrl) {
    const error = 'VITE_API_URL environment variable is required for production builds. ' +
      'Set this in your deployment configuration.';
    console.error('❌ API CONFIG ERROR:', error);
    throw new Error(error);
  }

  // In development, allow fallback to localhost
  if (!apiUrl) {
    console.warn('⚠️  VITE_API_URL not set, using localhost fallback (development only)');
    return 'http://localhost:3001/api';
  }

  // Validate URL format
  if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
    throw new Error(`Invalid API_URL format: ${apiUrl}. Must start with http:// or https://`);
  }

  return apiUrl;
})();

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Helper to get auth token
async function getAuthToken(): Promise<string | null> {
  try {
    const { supabase } = await import('./supabase');
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  } catch (error) {
    console.error('Error getting auth token:', error);
    return null;
  }
}

interface RequestOptions extends RequestInit {
  retries?: number;
  retryDelay?: number;
}

class ApiClient {
  private baseUrl: string;
  private requestCache: Map<string, { data: any; timestamp: number }>;
  private cacheDuration: number = 30000;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.requestCache = new Map();
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  private getCacheKey(endpoint: string, options?: RequestInit): string {
    return `${endpoint}-${JSON.stringify(options)}`;
  }

  private getFromCache<T>(key: string): ApiResponse<T> | null {
    const cached = this.requestCache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheDuration) {
      return cached.data;
    }
    return null;
  }

  private setCache(key: string, data: any): void {
    this.requestCache.set(key, { data, timestamp: Date.now() });
  }

  private async request<T>(
    endpoint: string,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    const { retries = 1, retryDelay = 500, ...fetchOptions } = options || {}; // Reduced retries and delay for speed

    const cacheKey = this.getCacheKey(endpoint, fetchOptions);
    if (fetchOptions.method === 'GET' || !fetchOptions.method) {
      const cached = this.getFromCache<T>(cacheKey);
      if (cached) {
        return cached;
      }
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        // Get auth token for authenticated requests
        const authToken = await getAuthToken();
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
          ...fetchOptions?.headers,
        };
        
        if (authToken) {
          headers['Authorization'] = `Bearer ${authToken}`;
        }

        // Add timeout for faster failure
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout
        
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
          ...fetchOptions,
          headers,
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);

        const data = await response.json();

        if (!response.ok) {
          if (response.status >= 500 && attempt < retries) {
            await this.sleep(retryDelay * Math.pow(2, attempt));
            continue;
          }
          throw new Error(data.error || `Request failed with status ${response.status}`);
        }

        if (fetchOptions.method === 'GET' || !fetchOptions.method) {
          this.setCache(cacheKey, data);
        }

        return data;
      } catch (error: any) {
        lastError = error;

        if (attempt < retries && (error.name === 'TypeError' || error.message.includes('fetch'))) {
          await this.sleep(retryDelay * Math.pow(2, attempt));
          continue;
        }

        if (attempt === retries) {
          break;
        }
      }
    }

    console.error('API Error after retries:', lastError);
    return {
      success: false,
      error: lastError?.message || 'Network error',
    };
  }

  // Agents
  async getAgents() {
    return this.request('/agents');
  }

  async getAgent(id: string) {
    return this.request(`/agents/${id}`);
  }

  async getAgentMetrics(id: string, limit?: number) {
    const params = limit ? `?limit=${limit}` : '';
    return this.request(`/agents/${id}/metrics${params}`);
  }

  // Metrics
  async getMetrics(hours?: number) {
    const params = hours ? `?hours=${hours}` : '';
    return this.request(`/metrics${params}`);
  }

  // Tasks
  async getTasks(filters?: { agent_id?: string; status?: string }) {
    const params = new URLSearchParams();
    if (filters?.agent_id) params.append('agent_id', filters.agent_id);
    if (filters?.status) params.append('status', filters.status);
    const query = params.toString();
    return this.request(`/tasks${query ? `?${query}` : ''}`);
  }

  // Dashboard
  async getDashboardStats() {
    return this.request('/dashboard/stats');
  }

  // Alerts
  async getAlerts(isResolved?: boolean) {
    const params = isResolved !== undefined ? `?is_resolved=${isResolved}` : '';
    return this.request(`/alerts${params}`);
  }

  async createCampaign(campaignData: any) {
    return this.request('/campaigns/create', {
      method: 'POST',
      body: JSON.stringify(campaignData),
    });
  }

  async startCampaign(campaignId: string) {
    return this.request(`/campaigns/${campaignId}/start`, {
      method: 'POST',
    });
  }

  async pauseCampaign(campaignId: string) {
    return this.request(`/campaigns/${campaignId}/pause`, {
      method: 'POST',
    });
  }

  async generateMessage(data: { leadName: string; company?: string; tone: string; context?: string }) {
    return this.request('/messages/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async importLeads(leads: any[]) {
    return this.request('/leads/import', {
      method: 'POST',
      body: JSON.stringify({ leads }),
    });
  }

  async scoreLeads(leadIds: string[]) {
    return this.request('/leads/score', {
      method: 'POST',
      body: JSON.stringify({ leadIds }),
    });
  }

  // AI Chat (Legacy - kept for backward compatibility)
  async chatWithAI(data: { message: string; context?: { userId?: string; purpose?: string; userName?: string }; conversationHistory?: Array<{ role: string; content: string }> }) {
    return this.request('/ai/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Quantum Leap: Stateful Agent Chat (Rex Orchestrator)
  async chatWithRex(data: { message: string; conversation_id?: string | null }) {
    return this.request('/v1/agent/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // AI Agents Campaign Integration
  async launchCampaignWithAgents(data: {
    user_id: string;
    lead_ids: string[];
    campaign_type?: string
  }) {
    return this.request('/v1/campaigns/start', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCampaignAgentStatus(campaignId: string) {
    return this.request(`/v1/campaigns/${campaignId}/agent-status`);
  }

  async getAgentWorkflow() {
    return this.request('/v1/agents/workflow');
  }

  async getAgentActivity(limit?: number) {
    const params = limit ? `?limit=${limit}` : '';
    return this.request(`/v1/agents/activity${params}`);
  }
}

export const apiClient = new ApiClient(API_BASE_URL);

// Health check function
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch('http://localhost:3001/health', {
      method: 'GET',
      signal: AbortSignal.timeout(2000), // 2 second timeout
    });
    return response.ok;
  } catch (error) {
    console.log('Backend not available, using direct Supabase connection');
    return false;
  }
}
