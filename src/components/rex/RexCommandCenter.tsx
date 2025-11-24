// @ts-nocheck
/**
 * RexCommandCenter - Central mission control for Rex orchestration
 *
 * Real-time monitoring, mission management, agent status tracking,
 * and performance analytics for the Rex autonomous system.
 */

import React, { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';

interface Mission {
  id: string;
  type: string;
  state: string;
  priority: number;
  user_id: string;
  campaign_id?: string;
  assigned_agent?: string;
  progress: number;
  result_data?: any;
  error_message?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

interface AgentStatus {
  agent_name: string;
  status: 'idle' | 'active' | 'error';
  current_mission?: string;
  missions_completed: number;
  success_rate: number;
  last_active: string;
}

export const RexCommandCenter: React.FC = () => {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchMissions();
    fetchAgentStatus();

    // Set up real-time subscriptions
    const missionsSubscription = supabase
      .channel('missions_changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'rex_missions',
        },
        () => {
          fetchMissions();
        }
      )
      .subscribe();

    return () => {
      missionsSubscription.unsubscribe();
    };
  }, [filter]);

  const fetchMissions = async () => {
    try {
      let query = supabase
        .from('rex_missions')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50);

      if (filter !== 'all') {
        query = query.eq('state', filter);
      }

      const { data, error } = await query;

      if (error) throw error;
      setMissions(data || []);
    } catch (error) {
      console.error('Error fetching missions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAgentStatus = async () => {
    try {
      // Fetch recent agent activity from logs
      const { data: logs, error } = await supabase
        .from('agent_logs')
        .select('agent_name, event_type, created_at')
        .gte('created_at', new Date(Date.now() - 3600000).toISOString()) // Last hour
        .order('created_at', { ascending: false });

      if (error) throw error;

      // Aggregate agent status
      const agentMap = new Map<string, AgentStatus>();
      const agentNames = [
        'ReviverAgent',
        'DeliverabilityAgent',
        'PersonalizerAgent',
        'ICPIntelligenceAgent',
        'ScraperAgent',
        'OutreachAgent',
        'AnalyticsAgent',
        'SpecialForcesCoordinator',
      ];

      agentNames.forEach((name) => {
        agentMap.set(name, {
          agent_name: name,
          status: 'idle',
          missions_completed: 0,
          success_rate: 0,
          last_active: 'Never',
        });
      });

      logs?.forEach((log) => {
        const agent = agentMap.get(log.agent_name);
        if (agent) {
          agent.last_active = new Date(log.created_at).toLocaleString();
          if (log.event_type === 'mission_started') {
            agent.status = 'active';
          } else if (log.event_type === 'mission_completed') {
            agent.missions_completed += 1;
          }
        }
      });

      setAgents(Array.from(agentMap.values()));
    } catch (error) {
      console.error('Error fetching agent status:', error);
    }
  };

  const createMission = async (type: string) => {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      const { data, error } = await supabase
        .from('rex_missions')
        .insert({
          type,
          state: 'queued',
          priority: 50,
          user_id: user?.id,
          progress: 0,
        })
        .select()
        .single();

      if (error) throw error;
      fetchMissions();
    } catch (error) {
      console.error('Error creating mission:', error);
    }
  };

  const cancelMission = async (missionId: string) => {
    try {
      const { error } = await supabase
        .from('rex_missions')
        .update({ state: 'cancelled' })
        .eq('id', missionId);

      if (error) throw error;
      fetchMissions();
    } catch (error) {
      console.error('Error cancelling mission:', error);
    }
  };

  const getStateColor = (state: string): string => {
    switch (state) {
      case 'queued':
        return 'bg-gray-100 text-gray-800';
      case 'assigned':
        return 'bg-blue-100 text-blue-800';
      case 'executing':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-600';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: number): string => {
    if (priority >= 80) return 'text-red-600';
    if (priority >= 50) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getAgentStatusColor = (status: string): string => {
    switch (status) {
      case 'active':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading command center...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Rex Command Center</h2>
        <p className="text-gray-600 mt-1">
          Autonomous orchestration mission control
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">Active Missions</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {
              missions.filter((m) =>
                ['queued', 'assigned', 'executing'].includes(m.state)
              ).length
            }
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">Completed</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {missions.filter((m) => m.state === 'completed').length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">Failed</div>
          <div className="text-2xl font-bold text-red-600 mt-1">
            {missions.filter((m) => m.state === 'failed').length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">Success Rate</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {missions.length > 0
              ? (
                  (missions.filter((m) => m.state === 'completed').length /
                    missions.length) *
                  100
                ).toFixed(0)
              : 0}
            %
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">Active Agents</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {agents.filter((a) => a.status === 'active').length}/{agents.length}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Mission List */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">Missions</h3>
                <div className="flex space-x-2">
                  <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="px-3 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option value="all">All States</option>
                    <option value="queued">Queued</option>
                    <option value="executing">Executing</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                  </select>
                  <button
                    onClick={() => createMission('lead_reactivation')}
                    className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                  >
                    New Mission
                  </button>
                </div>
              </div>
            </div>

            <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
              {missions.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No missions found
                </div>
              ) : (
                missions.map((mission) => (
                  <div
                    key={mission.id}
                    className="p-4 hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedMission(mission)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span
                            className={`px-2 py-1 text-xs font-semibold rounded ${getStateColor(
                              mission.state
                            )}`}
                          >
                            {mission.state}
                          </span>
                          <span className="text-sm font-medium text-gray-900">
                            {mission.type.replace(/_/g, ' ')}
                          </span>
                          <span
                            className={`text-xs font-medium ${getPriorityColor(
                              mission.priority
                            )}`}
                          >
                            P{mission.priority}
                          </span>
                        </div>
                        <div className="mt-2 text-xs text-gray-500">
                          ID: {mission.id.substring(0, 8)}
                          {mission.assigned_agent && (
                            <span className="ml-2">
                              • Agent: {mission.assigned_agent}
                            </span>
                          )}
                        </div>
                        {mission.progress > 0 && mission.state === 'executing' && (
                          <div className="mt-2">
                            <div className="w-full bg-gray-200 rounded-full h-1.5">
                              <div
                                className="bg-blue-600 h-1.5 rounded-full transition-all"
                                style={{ width: `${mission.progress * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="text-right text-xs text-gray-500">
                        {new Date(mission.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Agent Status Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                Agent Status
              </h3>
            </div>
            <div className="divide-y divide-gray-200">
              {agents.map((agent) => (
                <div key={agent.agent_name} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div
                        className={`w-2 h-2 rounded-full ${getAgentStatusColor(
                          agent.status
                        )}`}
                      ></div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {agent.agent_name.replace('Agent', '')}
                        </div>
                        <div className="text-xs text-gray-500">
                          {agent.missions_completed} missions
                        </div>
                      </div>
                    </div>
                    <span
                      className={`text-xs font-medium ${
                        agent.status === 'active'
                          ? 'text-green-600'
                          : 'text-gray-500'
                      }`}
                    >
                      {agent.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Mission Detail Modal */}
      {selectedMission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  <span
                    className={`px-2 py-1 text-xs font-semibold rounded ${getStateColor(
                      selectedMission.state
                    )}`}
                  >
                    {selectedMission.state}
                  </span>
                  <h3 className="text-xl font-bold text-gray-900">
                    {selectedMission.type.replace(/_/g, ' ')}
                  </h3>
                </div>
                <p className="text-sm text-gray-600">
                  Mission ID: {selectedMission.id}
                </p>
              </div>
              <button
                onClick={() => setSelectedMission(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              {/* Mission Details */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Details</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-600">Priority</div>
                    <div className="font-medium">{selectedMission.priority}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Progress</div>
                    <div className="font-medium">
                      {(selectedMission.progress * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-600">Assigned Agent</div>
                    <div className="font-medium">
                      {selectedMission.assigned_agent || 'Not assigned'}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-600">Created</div>
                    <div className="font-medium">
                      {new Date(selectedMission.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>

              {/* Result Data */}
              {selectedMission.result_data && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-3">Results</h4>
                  <pre className="text-xs bg-white p-3 rounded border border-gray-200 overflow-x-auto">
                    {JSON.stringify(selectedMission.result_data, null, 2)}
                  </pre>
                </div>
              )}

              {/* Error Message */}
              {selectedMission.error_message && (
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                  <h4 className="font-semibold text-red-900 mb-2">Error</h4>
                  <p className="text-sm text-red-700">
                    {selectedMission.error_message}
                  </p>
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              {['queued', 'assigned', 'executing'].includes(
                selectedMission.state
              ) && (
                <button
                  onClick={() => {
                    cancelMission(selectedMission.id);
                    setSelectedMission(null);
                  }}
                  className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                >
                  Cancel Mission
                </button>
              )}
              <button
                onClick={() => setSelectedMission(null)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
