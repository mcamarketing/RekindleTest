// @ts-nocheck
import { useEffect, useState, useRef, useCallback } from 'react';

export interface AgentActivity {
  agent_id: string;
  agent_name: string;
  agent_type: string;
  status: 'idle' | 'working' | 'completed' | 'error';
  task: string;
  progress?: number;
  timestamp: string;
  metadata?: Record<string, any>;
}

interface AgentWorkflowState {
  activities: AgentActivity[];
  connections: Array<{
    from: string;
    to: string;
    status: 'active' | 'pending' | 'completed';
  }>;
  campaignId?: string;
}

export function useAgentWebSocket(enabled: boolean = true) {
  const [connected, setConnected] = useState(false);
  const [workflowState, setWorkflowState] = useState<AgentWorkflowState>({
    activities: [],
    connections: [],
  });
  const [latestActivity, setLatestActivity] = useState<AgentActivity | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!enabled || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:3001/ws/agents';
      console.log('🔌 Connecting to Agent WebSocket:', wsUrl);

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ Agent WebSocket connected');
        setConnected(true);
        reconnectAttempts.current = 0;

        // Subscribe to agent activities
        ws.send(JSON.stringify({
          type: 'subscribe',
          channel: 'agent_activities'
        }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          switch (data.type) {
            case 'agent_activity':
              const activity: AgentActivity = data.payload;
              setLatestActivity(activity);
              setWorkflowState((prev) => ({
                ...prev,
                activities: [activity, ...prev.activities].slice(0, 50), // Keep last 50
              }));
              break;

            case 'workflow_update':
              setWorkflowState((prev) => ({
                ...prev,
                connections: data.payload.connections || prev.connections,
                campaignId: data.payload.campaignId || prev.campaignId,
              }));
              break;

            case 'agent_status':
              // Update specific agent status in activities
              setWorkflowState((prev) => ({
                ...prev,
                activities: prev.activities.map((act) =>
                  act.agent_id === data.payload.agent_id
                    ? { ...act, status: data.payload.status }
                    : act
                ),
              }));
              break;

            default:
              console.log('📨 Unknown WebSocket message type:', data.type);
          }
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setConnected(false);
        wsRef.current = null;

        // Attempt to reconnect with exponential backoff
        if (enabled && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        }
      };
    } catch (error) {
      console.error('❌ Failed to create WebSocket:', error);
    }
  }, [enabled]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setConnected(false);
  }, []);

  const clearActivities = useCallback(() => {
    setWorkflowState({
      activities: [],
      connections: [],
    });
    setLatestActivity(null);
  }, []);

  useEffect(() => {
    if (enabled) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    connected,
    workflowState,
    latestActivity,
    clearActivities,
    reconnect: connect,
  };
}
