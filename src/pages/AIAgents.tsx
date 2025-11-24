// @ts-nocheck
import { useEffect, useState, useMemo } from 'react';
import { Navigation } from '../components/Navigation';
import { supabase } from '../lib/supabase';
import { apiClient, checkBackendHealth } from '../lib/api';
import { Cpu, Activity, AlertCircle, CheckCircle, Clock, Zap, TrendingUp, Network, Grid, GitBranch, Workflow } from 'lucide-react';
import { AgentWorkflowView } from '../components/AgentWorkflowView';
import { useAgentWebSocket } from '../hooks/useAgentWebSocket';

interface Agent {
  id: string;
  name: string;
  description: string;
  status: string;
  agent_type: string;
  last_heartbeat: string;
  metadata: any;
}

interface AgentMetrics {
  agent_id: string;
  cpu_usage: number;
  memory_usage: number;
  response_time: number;
  active_tasks: number;
  completed_tasks: number;
  error_count: number;
  recorded_at: string;
}

export function AIAgents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [metrics, setMetrics] = useState<Record<string, AgentMetrics>>({});
  const [loading, setLoading] = useState(true);
  const [useBackend, setUseBackend] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'network' | 'workflow'>('workflow');

  // WebSocket connection for real-time agent activity
  const { connected, workflowState, latestActivity } = useAgentWebSocket(true);

  useEffect(() => {
    const initialize = async () => {
      const isHealthy = await checkBackendHealth();
      setUseBackend(isHealthy);
      if (isHealthy) {
        console.log('✅ Using backend API');
      } else {
        console.log('📊 Using direct Supabase connection');
      }
      // Load agents after checking backend
      await loadAgents();
    };
    initialize();
    const interval = setInterval(loadAgents, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkBackend = async () => {
    const isHealthy = await checkBackendHealth();
    setUseBackend(isHealthy);
    return isHealthy;
  };

  const loadAgents = async () => {
    try {
      // Try backend first, then fallback to Supabase
      const isBackendHealthy = await checkBackend();
      setUseBackend(isBackendHealthy);

      if (isBackendHealthy) {
        try {
          // Use backend API
          const agentsResponse = await apiClient.getAgents();
          console.log('🔍 Backend response:', agentsResponse);

          if (agentsResponse.success && agentsResponse.data) {
            const agentsData = agentsResponse.data as Agent[];
            console.log('✅ Loaded agents from backend:', agentsData.length);
            if (agentsData.length > 0) {
              setAgents(agentsData);

              // Load metrics for each agent
              const latestMetrics: Record<string, AgentMetrics> = {};
              for (const agent of agentsData) {
                try {
                  const metricsResponse = await apiClient.getAgentMetrics(agent.id, 1);
                  if (metricsResponse.success && metricsResponse.data) {
                    const metricsArray = metricsResponse.data as AgentMetrics[];
                    if (metricsArray.length > 0) {
                      latestMetrics[agent.id] = metricsArray[0];
                    }
                  }
                } catch (err) {
                  console.warn(`Could not load metrics for agent ${agent.id}:`, err);
                }
              }
              setMetrics(latestMetrics);
              setLoading(false);
              return;
            }
          }
        } catch (backendError) {
          console.warn('Backend failed, trying Supabase:', backendError);
        }
      }

      // Fallback to direct Supabase
      console.log('📊 Loading agents directly from Supabase...');
      const { data: agentsData, error: agentsError } = await supabase
        .from('agents')
        .select('*')
        .order('name');

      if (agentsError) {
        console.error('❌ Error loading agents from Supabase:', agentsError);
        // Don't throw - show empty state instead
        setAgents([]);
        setLoading(false);
        return;
      }
      
      console.log('✅ Loaded agents from Supabase:', agentsData?.length || 0);
      if (agentsData && agentsData.length > 0) {
        console.log('📋 Agent names:', agentsData.map(a => a.name).join(', '));
      }

      // Try to load metrics (optional, don't fail if this errors)
      let metricsData = null;
      try {
        const { data, error: metricsError } = await supabase
          .from('agent_metrics')
          .select('*')
          .order('recorded_at', { ascending: false });

        if (!metricsError) {
          metricsData = data;
        }
      } catch (err) {
        console.warn('Could not load metrics:', err);
      }

      const latestMetrics: Record<string, AgentMetrics> = {};
      if (metricsData) {
        metricsData.forEach(metric => {
          if (!latestMetrics[metric.agent_id]) {
            latestMetrics[metric.agent_id] = metric;
          }
        });
      }

      // Remove duplicates by ID (in case of any data issues)
      const uniqueAgents = (agentsData || []).filter((agent, index, self) => 
        index === self.findIndex(a => a.id === agent.id)
      );
      
      console.log(`📊 Unique agents: ${uniqueAgents.length} (removed ${(agentsData || []).length - uniqueAgents.length} duplicates)`);
      
      setAgents(uniqueAgents);
      setMetrics(latestMetrics);
    } catch (error) {
      console.error('❌ Error loading agents:', error);
      setAgents([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return (
          <div className="relative">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <div className="absolute inset-0 rounded-full bg-green-500/20 animate-ping" />
          </div>
        );
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'offline':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <Activity className="w-5 h-5 text-blue-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-500/20 text-green-400 border-green-500/30',
      idle: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      error: 'bg-red-500/20 text-red-400 border-red-500/30',
      offline: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    };
    return colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const getAgentTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      researcher: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      writer: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      scorer: 'bg-green-500/20 text-green-400 border-green-500/30',
      sourcer: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      analyzer: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
      optimizer: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
      tracker: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
      sender: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    };
    return colors[type.toLowerCase()] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const formatUptime = (lastHeartbeat: string) => {
    const diff = Date.now() - new Date(lastHeartbeat).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  const agentsByType = agents.reduce((acc, agent) => {
    const type = agent.agent_type;
    if (!acc[type]) acc[type] = [];
    acc[type].push(agent);
    return acc;
  }, {} as Record<string, Agent[]>);

  // Build agent connections based on crew assignments
  const agentConnections = useMemo(() => {
    const connections: Array<{ from: string; to: string; crew: string }> = [];
    const crewMap = new Map<string, string[]>();

    // Group agents by crew
    agents.forEach(agent => {
      const metadata = agent.metadata || {};
      const crews = metadata.crew ? (typeof metadata.crew === 'string' ? metadata.crew.split(',') : [metadata.crew]) : [];
      crews.forEach(crew => {
        const crewName = crew.trim();
        if (!crewMap.has(crewName)) {
          crewMap.set(crewName, []);
        }
        crewMap.get(crewName)!.push(agent.id);
      });
    });

    // Create connections between agents in the same crew
    crewMap.forEach((agentIds, crew) => {
      for (let i = 0; i < agentIds.length; i++) {
        for (let j = i + 1; j < agentIds.length; j++) {
          connections.push({
            from: agentIds[i],
            to: agentIds[j],
            crew: crew
          });
        }
      }
    });

    return connections;
  }, [agents]);

  // Get crew name for an agent
  const getAgentCrews = (agent: Agent): string[] => {
    const metadata = agent.metadata || {};
    const crews = metadata.crew ? (typeof metadata.crew === 'string' ? metadata.crew.split(',') : [metadata.crew]) : [];
    return crews.map(c => c.trim());
  };

  // Determine if agent is actually working (not just status='active')
  const isAgentActuallyWorking = (agent: Agent): boolean => {
    const metric = metrics[agent.id];
    const lastHeartbeat = agent.last_heartbeat ? new Date(agent.last_heartbeat).getTime() : 0;
    const now = Date.now();
    const timeSinceHeartbeat = now - lastHeartbeat;
    
    // Agent is working if:
    // 1. Has active tasks OR
    // 2. Has completed tasks recently (within last hour) OR
    // 3. Has recent heartbeat (within last 5 minutes) AND status is active
    const hasActiveTasks = metric && metric.active_tasks > 0;
    const hasRecentActivity = metric && metric.completed_tasks > 0;
    const hasRecentHeartbeat = timeSinceHeartbeat < 5 * 60 * 1000; // 5 minutes
    const isStatusActive = agent.status === 'active';
    
    return hasActiveTasks || (hasRecentHeartbeat && isStatusActive && hasRecentActivity);
  };

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 left-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
        <div className="absolute bottom-1/4 right-1/3 w-[700px] h-[700px] bg-purple-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '7s' }} />
      </div>

      <Navigation currentPage="agents" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Futuristic Header with Holographic Effect */}
        <div className="mb-10 animate-fade-in relative">
          {/* Holographic scan lines */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 via-transparent to-purple-500/5 animate-pulse" />
            <div className="absolute inset-0 opacity-10">
              {[...Array(20)].map((_, i) => (
                <div
                  key={i}
                  className="h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent"
                  style={{
                    top: `${i * 5}%`,
                    animationDelay: `${i * 0.1}s`
                  }}
                />
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between mb-3 relative">
            <div className="space-y-3">
              {/* Cyberpunk Title */}
              <div className="relative inline-block">
                <h1 className="text-6xl font-black bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent mb-2 tracking-tight relative z-10">
                  AI AGENTS
                </h1>
                <div className="absolute -inset-2 bg-gradient-to-r from-cyan-500/20 via-blue-500/20 to-purple-600/20 blur-2xl -z-10 animate-pulse" />
                {/* Glitch lines */}
                <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-cyan-400 to-transparent opacity-50 animate-pulse" />
                <div className="absolute bottom-0 right-0 w-3/4 h-px bg-gradient-to-l from-purple-400 to-transparent opacity-50 animate-pulse" style={{ animationDelay: '0.5s' }} />
              </div>

              <p className="text-cyan-300/80 text-lg font-medium tracking-wide flex items-center gap-2">
                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-lg shadow-cyan-400/50" />
                <span className="font-mono text-sm">NEURAL_NETWORK_ACTIVE</span>
                <span className="mx-2 text-cyan-500/50">│</span>
                <span className="text-gray-400">Autonomous Intelligence Orchestration System</span>
              </p>
            </div>

            {/* Futuristic View Mode Toggle */}
            <div className="flex gap-3 relative">
              {/* Holographic container */}
              <div className="absolute -inset-2 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-pink-500/10 rounded-2xl blur-xl" />
              <div className="relative flex gap-1 bg-black/40 backdrop-blur-xl rounded-2xl p-1.5 border border-cyan-500/30 shadow-2xl shadow-cyan-500/20">
                {/* Corner accents */}
                <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-cyan-400 rounded-tl-xl" />
                <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-purple-400 rounded-tr-xl" />
                <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-purple-400 rounded-bl-xl" />
                <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-cyan-400 rounded-br-xl" />

                <button
                  onClick={() => setViewMode('workflow')}
                  className={`relative px-5 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 flex items-center gap-2 overflow-hidden group ${
                    viewMode === 'workflow'
                      ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/50'
                      : 'text-cyan-300/60 hover:text-cyan-300 hover:bg-white/5'
                  }`}
                >
                  {viewMode === 'workflow' && (
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/20 to-blue-500/20 animate-pulse" />
                  )}
                  <Workflow className="w-4 h-4 relative z-10" />
                  <span className="relative z-10 font-mono">WORKFLOW</span>
                  {connected && (
                    <span className="relative z-10 flex items-center">
                      <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50" />
                      <span className="absolute w-2 h-2 bg-green-400 rounded-full animate-ping" />
                    </span>
                  )}
                </button>

                <button
                  onClick={() => setViewMode('network')}
                  className={`relative px-5 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 flex items-center gap-2 overflow-hidden group ${
                    viewMode === 'network'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg shadow-purple-500/50'
                      : 'text-cyan-300/60 hover:text-cyan-300 hover:bg-white/5'
                  }`}
                >
                  {viewMode === 'network' && (
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-pink-500/20 animate-pulse" />
                  )}
                  <Network className="w-4 h-4 relative z-10" />
                  <span className="relative z-10 font-mono">NETWORK</span>
                </button>

                <button
                  onClick={() => setViewMode('grid')}
                  className={`relative px-5 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 flex items-center gap-2 overflow-hidden group ${
                    viewMode === 'grid'
                      ? 'bg-gradient-to-r from-pink-500 to-orange-600 text-white shadow-lg shadow-pink-500/50'
                      : 'text-cyan-300/60 hover:text-cyan-300 hover:bg-white/5'
                  }`}
                >
                  {viewMode === 'grid' && (
                    <div className="absolute inset-0 bg-gradient-to-r from-pink-400/20 to-orange-500/20 animate-pulse" />
                  )}
                  <Grid className="w-4 h-4 relative z-10" />
                  <span className="relative z-10 font-mono">GRID</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-[#FF6B35]/30 rounded-full"></div>
              <div className="absolute inset-0 w-16 h-16 border-4 border-[#FF6B35] border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        ) : agents.length === 0 ? (
          <div className="glass-card p-12 text-center animate-fade-in">
            <div className="p-6 bg-gradient-to-br from-blue-500 to-purple-500 rounded-3xl w-fit mx-auto mb-6 shadow-2xl">
              <Cpu className="w-20 h-20 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">
              No agents found
            </h3>
            <p className="text-gray-400 text-lg">
              AI agents will appear here once they are initialized
            </p>
          </div>
        ) : (
          <>
            {/* Holographic Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              {/* Total Agents Card */}
              <div className="group relative animate-fade-in" style={{ animationDelay: '0.1s' }}>
                {/* Holographic glow */}
                <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/50 via-blue-500/50 to-cyan-500/50 rounded-2xl blur-xl opacity-60 group-hover:opacity-100 transition-opacity animate-pulse" />

                <div className="relative bg-black/60 backdrop-blur-xl border border-cyan-500/30 rounded-2xl p-6 overflow-hidden hover:border-cyan-400/50 transition-all duration-300">
                  {/* Animated grid background */}
                  <div className="absolute inset-0 opacity-10">
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-transparent" />
                    {[...Array(4)].map((_, i) => (
                      <div key={i} className="absolute h-px w-full bg-cyan-500/30" style={{ top: `${25 * i}%` }} />
                    ))}
                  </div>

                  <div className="relative flex items-center justify-between">
                    <div className="space-y-2">
                      <p className="text-xs font-bold text-cyan-400/80 uppercase tracking-widest font-mono">TOTAL_AGENTS</p>
                      <p className="text-5xl font-black bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                        {agents.length}
                      </p>
                      <div className="h-px w-16 bg-gradient-to-r from-cyan-500 to-transparent" />
                    </div>

                    <div className="relative">
                      <div className="absolute inset-0 bg-cyan-500/30 blur-xl animate-pulse" />
                      <div className="relative p-4 bg-gradient-to-br from-cyan-500/20 to-blue-600/20 backdrop-blur-sm rounded-xl border border-cyan-400/30">
                        <Cpu className="w-8 h-8 text-cyan-400" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Working Card */}
              <div className="group relative animate-fade-in" style={{ animationDelay: '0.15s' }}>
                <div className="absolute -inset-1 bg-gradient-to-r from-green-500/50 via-emerald-500/50 to-green-500/50 rounded-2xl blur-xl opacity-60 group-hover:opacity-100 transition-opacity animate-pulse" />

                <div className="relative bg-black/60 backdrop-blur-xl border border-green-500/30 rounded-2xl p-6 overflow-hidden hover:border-green-400/50 transition-all duration-300">
                  <div className="absolute inset-0 opacity-10">
                    <div className="absolute inset-0 bg-gradient-to-br from-green-500/20 to-transparent" />
                    {[...Array(4)].map((_, i) => (
                      <div key={i} className="absolute h-px w-full bg-green-500/30" style={{ top: `${25 * i}%` }} />
                    ))}
                  </div>

                  <div className="relative flex items-center justify-between">
                    <div className="space-y-2">
                      <p className="text-xs font-bold text-green-400/80 uppercase tracking-widest font-mono">ACTIVE_NOW</p>
                      <p className="text-5xl font-black bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
                        {agents.filter(a => isAgentActuallyWorking(a)).length}
                      </p>
                      <div className="h-px w-16 bg-gradient-to-r from-green-500 to-transparent" />
                    </div>

                    <div className="relative">
                      <div className="absolute inset-0 bg-green-500/30 blur-xl animate-pulse" />
                      <div className="relative p-4 bg-gradient-to-br from-green-500/20 to-emerald-600/20 backdrop-blur-sm rounded-xl border border-green-400/30">
                        <CheckCircle className="w-8 h-8 text-green-400" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Idle Card */}
              <div className="group relative animate-fade-in" style={{ animationDelay: '0.2s' }}>
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-500/50 via-pink-500/50 to-purple-500/50 rounded-2xl blur-xl opacity-60 group-hover:opacity-100 transition-opacity animate-pulse" />

                <div className="relative bg-black/60 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6 overflow-hidden hover:border-purple-400/50 transition-all duration-300">
                  <div className="absolute inset-0 opacity-10">
                    <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-transparent" />
                    {[...Array(4)].map((_, i) => (
                      <div key={i} className="absolute h-px w-full bg-purple-500/30" style={{ top: `${25 * i}%` }} />
                    ))}
                  </div>

                  <div className="relative flex items-center justify-between">
                    <div className="space-y-2">
                      <p className="text-xs font-bold text-purple-400/80 uppercase tracking-widest font-mono">STANDBY_MODE</p>
                      <p className="text-5xl font-black bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
                        {agents.filter(a => a.status === 'idle').length}
                      </p>
                      <div className="h-px w-16 bg-gradient-to-r from-purple-500 to-transparent" />
                    </div>

                    <div className="relative">
                      <div className="absolute inset-0 bg-purple-500/30 blur-xl animate-pulse" />
                      <div className="relative p-4 bg-gradient-to-br from-purple-500/20 to-pink-600/20 backdrop-blur-sm rounded-xl border border-purple-400/30">
                        <Activity className="w-8 h-8 text-purple-400" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Issues Card */}
              <div className="group relative animate-fade-in" style={{ animationDelay: '0.25s' }}>
                <div className="absolute -inset-1 bg-gradient-to-r from-red-500/50 via-orange-500/50 to-red-500/50 rounded-2xl blur-xl opacity-60 group-hover:opacity-100 transition-opacity animate-pulse" />

                <div className="relative bg-black/60 backdrop-blur-xl border border-red-500/30 rounded-2xl p-6 overflow-hidden hover:border-red-400/50 transition-all duration-300">
                  <div className="absolute inset-0 opacity-10">
                    <div className="absolute inset-0 bg-gradient-to-br from-red-500/20 to-transparent" />
                    {[...Array(4)].map((_, i) => (
                      <div key={i} className="absolute h-px w-full bg-red-500/30" style={{ top: `${25 * i}%` }} />
                    ))}
                  </div>

                  <div className="relative flex items-center justify-between">
                    <div className="space-y-2">
                      <p className="text-xs font-bold text-red-400/80 uppercase tracking-widest font-mono">ALERT_STATUS</p>
                      <p className="text-5xl font-black bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent">
                        {agents.filter(a => a.status === 'error' || a.status === 'warning').length}
                      </p>
                      <div className="h-px w-16 bg-gradient-to-r from-red-500 to-transparent" />
                    </div>

                    <div className="relative">
                      <div className="absolute inset-0 bg-red-500/30 blur-xl animate-pulse" />
                      <div className="relative p-4 bg-gradient-to-br from-red-500/20 to-orange-600/20 backdrop-blur-sm rounded-xl border border-red-400/30">
                        <AlertCircle className="w-8 h-8 text-red-400" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Workflow View - Live Agent Activity */}
            {viewMode === 'workflow' ? (
              <div className="animate-fade-in">
                {/* Connection Status Banner */}
                {!connected && (
                  <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-yellow-400" />
                    <div>
                      <p className="text-sm font-semibold text-yellow-400">WebSocket Disconnected</p>
                      <p className="text-xs text-gray-400">Real-time updates are currently unavailable. Attempting to reconnect...</p>
                    </div>
                  </div>
                )}

                <AgentWorkflowView
                  activities={workflowState.activities}
                  connections={workflowState.connections}
                />
              </div>
            ) : viewMode === 'network' ? (
              <div className="group relative animate-fade-in">
                {/* Holographic glow */}
                <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/50 via-purple-500/50 to-pink-500/50 rounded-2xl blur-xl opacity-60 group-hover:opacity-100 transition-opacity animate-pulse" />

                <div className="relative bg-black/60 backdrop-blur-xl border border-cyan-500/30 rounded-2xl p-8 overflow-x-auto overflow-y-visible" style={{ minHeight: '800px', maxHeight: '90vh' }}>
                  {/* Corner accents */}
                  <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-cyan-400" />
                  <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-cyan-400" />
                  <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-cyan-400" />
                  <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-cyan-400" />

                  {/* Scan lines */}
                  <div className="absolute inset-0 pointer-events-none opacity-5">
                    {[...Array(40)].map((_, i) => (
                      <div key={i} className="h-px w-full bg-cyan-400" style={{ top: `${i * 2.5}%` }} />
                    ))}
                  </div>

              <div className="relative">
                {(() => {
                  // Workflow stages - left to right pipeline
                  const workflowStages = [
                    { name: 'Intelligence', types: ['research', 'intelligence'], color: 'purple', icon: '🔍' },
                    { name: 'Content', types: ['content'], color: 'blue', icon: '✍️' },
                    { name: 'Safety', types: ['safety'], color: 'yellow', icon: '🛡️' },
                    { name: 'Execution', types: ['sync', 'specialized'], color: 'green', icon: '⚡' },
                    { name: 'Revenue', types: ['revenue'], color: 'orange', icon: '💰' },
                    { name: 'Optimization', types: ['optimization', 'infrastructure', 'analytics'], color: 'indigo', icon: '📊' },
                    { name: 'Orchestration', types: ['orchestration'], color: 'pink', icon: '🎯' },
                  ];

                  const agentsByStage = workflowStages.map(stage => ({
                    ...stage,
                    agents: agents.filter(a => stage.types.includes(a.agent_type))
                  }));

                  const stageWidth = 200;
                  const stageGap = 60;
                  const containerWidth = agentsByStage.length * stageWidth + (agentsByStage.length - 1) * stageGap;
                  
                  return (
                    <div className="relative" style={{ minHeight: '750px', width: `${Math.max(containerWidth, 1000)}px` }}>
                      {/* Workflow Pipeline Background */}
                      <svg className="absolute inset-0 w-full h-full pointer-events-none z-0" style={{ minHeight: '750px' }}>
                        {/* Main pipeline flow arrows */}
                        {agentsByStage.slice(0, -1).map((_, idx) => {
                          const x1 = (idx + 1) * stageWidth + idx * stageGap;
                          const x2 = (idx + 1) * stageWidth + idx * stageGap + stageGap;
                          const y = 60;
                          return (
                            <g key={`pipeline-${idx}`}>
                              <line x1={x1} y1={y} x2={x2} y2={y} stroke="#6b7280" strokeWidth="3" strokeDasharray="8,4" opacity="0.3" />
                              <polygon 
                                points={`${x2},${y} ${x2-12},${y-6} ${x2-12},${y+6}`} 
                                fill="#6b7280" 
                                opacity="0.4"
                              />
                            </g>
                          );
                        })}
                        
                        {/* Agent connections */}
                        {agentConnections
                          .filter(conn => {
                            const fromAgent = agents.find(a => a.id === conn.from);
                            const toAgent = agents.find(a => a.id === conn.to);
                            if (!fromAgent || !toAgent) return false;
                            
                            const fromStageIdx = agentsByStage.findIndex(s => s.types.includes(fromAgent.agent_type));
                            const toStageIdx = agentsByStage.findIndex(s => s.types.includes(toAgent.agent_type));
                            
                            return fromStageIdx >= 0 && toStageIdx >= 0 && Math.abs(fromStageIdx - toStageIdx) <= 2;
                          })
                          .map((conn, idx) => {
                            const fromAgent = agents.find(a => a.id === conn.from);
                            const toAgent = agents.find(a => a.id === conn.to);
                            if (!fromAgent || !toAgent) return null;
                            
                            const fromStageIdx = agentsByStage.findIndex(s => s.types.includes(fromAgent.agent_type));
                            const toStageIdx = agentsByStage.findIndex(s => s.types.includes(toAgent.agent_type));
                            
                            const fromStage = agentsByStage[fromStageIdx];
                            const toStage = agentsByStage[toStageIdx];
                            
                            const fromIdx = fromStage.agents.findIndex(a => a.id === fromAgent.id);
                            const toIdx = toStage.agents.findIndex(a => a.id === toAgent.id);
                            
                            const stageX1 = fromStageIdx * stageWidth + fromStageIdx * stageGap + stageWidth / 2;
                            const stageX2 = toStageIdx * stageWidth + toStageIdx * stageGap + stageWidth / 2;
                            
                            const y1 = 120 + fromIdx * 70 + 25;
                            const y2 = 120 + toIdx * 70 + 25;
                            
                            const isActive = isAgentActuallyWorking(fromAgent) && isAgentActuallyWorking(toAgent);
                            
                            return (
                              <line
                                key={`workflow-conn-${idx}`}
                                x1={stageX1}
                                y1={y1}
                                x2={stageX2}
                                y2={y2}
                                stroke={isActive ? '#10b981' : '#4b5563'}
                                strokeWidth={isActive ? '2.5' : '1'}
                                strokeOpacity={isActive ? '0.7' : '0.2'}
                                markerEnd={isActive ? "url(#arrow-active)" : "url(#arrow-inactive)"}
                                className={isActive ? 'animate-pulse' : ''}
                              />
                            );
                          })}
                        
                        <defs>
                          <marker id="arrow-active" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                            <polygon points="0 0, 10 3, 0 6" fill="#10b981" />
                          </marker>
                          <marker id="arrow-inactive" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                            <polygon points="0 0, 10 3, 0 6" fill="#4b5563" opacity="0.2" />
                          </marker>
                        </defs>
                      </svg>

                      {/* Workflow Stages */}
                      <div className="relative z-10 flex gap-15">
                        {agentsByStage.map((stage, stageIdx) => {
                          if (stage.agents.length === 0) return null;
                          
                          const workingCount = stage.agents.filter(a => isAgentActuallyWorking(a)).length;
                          
                          return (
                            <div key={stage.name} className="flex-shrink-0 flex flex-col items-center" style={{ width: `${stageWidth}px` }}>
                              {/* Cyberpunk Stage Header */}
                              <div className="group/stage relative w-full mb-6">
                                <div className={`absolute -inset-0.5 rounded-xl blur-md opacity-50 group-hover/stage:opacity-80 transition-opacity ${
                                  stage.color === 'purple' ? 'bg-gradient-to-r from-purple-500/50 to-pink-500/50 animate-pulse' :
                                  stage.color === 'blue' ? 'bg-gradient-to-r from-blue-500/50 to-cyan-500/50 animate-pulse' :
                                  stage.color === 'yellow' ? 'bg-gradient-to-r from-yellow-500/50 to-orange-500/50 animate-pulse' :
                                  stage.color === 'green' ? 'bg-gradient-to-r from-green-500/50 to-emerald-500/50 animate-pulse' :
                                  stage.color === 'orange' ? 'bg-gradient-to-r from-orange-500/50 to-red-500/50 animate-pulse' :
                                  stage.color === 'indigo' ? 'bg-gradient-to-r from-indigo-500/50 to-purple-500/50 animate-pulse' :
                                  'bg-gradient-to-r from-pink-500/50 to-purple-500/50 animate-pulse'
                                }`} />

                                <div className={`relative p-4 rounded-xl border-2 bg-black/60 backdrop-blur-xl text-center overflow-hidden ${
                                  stage.color === 'purple' ? 'border-purple-500/40' :
                                  stage.color === 'blue' ? 'border-blue-500/40' :
                                  stage.color === 'yellow' ? 'border-yellow-500/40' :
                                  stage.color === 'green' ? 'border-green-500/40' :
                                  stage.color === 'orange' ? 'border-orange-500/40' :
                                  stage.color === 'indigo' ? 'border-indigo-500/40' :
                                  'border-pink-500/40'
                                }`}>
                                  {/* Grid background */}
                                  <div className="absolute inset-0 opacity-5">
                                    {[...Array(3)].map((_, i) => (
                                      <div key={i} className={`absolute h-px w-full ${
                                        stage.color === 'purple' ? 'bg-purple-400' :
                                        stage.color === 'blue' ? 'bg-blue-400' :
                                        stage.color === 'yellow' ? 'bg-yellow-400' :
                                        stage.color === 'green' ? 'bg-green-400' :
                                        stage.color === 'orange' ? 'bg-orange-400' :
                                        stage.color === 'indigo' ? 'bg-indigo-400' :
                                        'bg-pink-400'
                                      }`} style={{ top: `${33 * i}%` }} />
                                    ))}
                                  </div>

                                  <div className="relative">
                                    <div className="text-3xl mb-2 filter drop-shadow-lg">{stage.icon}</div>
                                    <h3 className={`text-base font-black mb-2 font-mono uppercase tracking-tight ${
                                      stage.color === 'purple' ? 'text-purple-400' :
                                      stage.color === 'blue' ? 'text-blue-400' :
                                      stage.color === 'yellow' ? 'text-yellow-400' :
                                      stage.color === 'green' ? 'text-green-400' :
                                      stage.color === 'orange' ? 'text-orange-400' :
                                      stage.color === 'indigo' ? 'text-indigo-400' :
                                      'text-pink-400'
                                    }`}>{stage.name}</h3>
                                    <div className="flex items-center justify-center gap-2 text-xs font-mono">
                                      <span className="text-gray-400 uppercase tracking-wider">{stage.agents.length} units</span>
                                      {workingCount > 0 && (
                                        <>
                                          <span className="text-gray-600">•</span>
                                          <span className="text-green-400 font-bold uppercase tracking-wider">{workingCount} active</span>
                                        </>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Agents Stack */}
                              <div className="w-full space-y-2">
                                {stage.agents.map((agent, agentIdx) => {
                                  const isActive = isAgentActuallyWorking(agent);
                                  const metric = metrics[agent.id];
                                  const crews = getAgentCrews(agent);
                                  
                                  return (
                                    <div
                                      key={agent.id}
                                      className="group/agent relative"
                                    >
                                      {/* Cyberpunk glow for active agents */}
                                      {isActive && (
                                        <div className="absolute -inset-0.5 rounded-xl bg-gradient-to-r from-green-500/50 via-emerald-500/50 to-green-500/50 blur-md animate-pulse" />
                                      )}

                                      <div className={`relative p-3 cursor-pointer transition-all hover:scale-105 hover:z-30 rounded-xl border-2 bg-black/60 backdrop-blur-xl overflow-hidden ${
                                        isActive
                                          ? 'border-green-500/60 shadow-[0_0_20px_rgba(34,197,94,0.3)]'
                                          : 'border-white/10 hover:border-cyan-500/40'
                                      }`}>
                                        {/* Corner accents */}
                                        <div className={`absolute top-0 left-0 w-2 h-2 border-t border-l ${isActive ? 'border-green-400' : 'border-cyan-400/40'}`} />
                                        <div className={`absolute top-0 right-0 w-2 h-2 border-t border-r ${isActive ? 'border-green-400' : 'border-cyan-400/40'}`} />
                                        <div className={`absolute bottom-0 left-0 w-2 h-2 border-b border-l ${isActive ? 'border-green-400' : 'border-cyan-400/40'}`} />
                                        <div className={`absolute bottom-0 right-0 w-2 h-2 border-b border-r ${isActive ? 'border-green-400' : 'border-cyan-400/40'}`} />

                                        {/* Grid background */}
                                        <div className="absolute inset-0 opacity-5">
                                          {[...Array(2)].map((_, i) => (
                                            <div key={i} className={`absolute h-px w-full ${isActive ? 'bg-green-400' : 'bg-cyan-400'}`} style={{ top: `${50 * i}%` }} />
                                          ))}
                                        </div>

                                      <div className="relative">
                                        <div className="flex items-center gap-2 mb-2">
                                          {isActive ? (
                                            <div className="relative flex-shrink-0">
                                              <CheckCircle className="w-4 h-4 text-green-400" />
                                              <div className="absolute inset-0 rounded-full bg-green-500/40 animate-ping" />
                                            </div>
                                          ) : (
                                            <div className="flex-shrink-0 scale-75">{getStatusIcon(agent.status)}</div>
                                          )}
                                          <h4 className="font-black text-cyan-300 text-xs truncate flex-1 font-mono uppercase">{agent.name}</h4>
                                        </div>

                                        <div className="flex items-center gap-1.5 mb-1">
                                          <span className={`px-2 py-0.5 text-xs font-black rounded-lg border font-mono uppercase tracking-wider ${
                                            isActive
                                              ? 'bg-black/40 text-green-400 border-green-500/60'
                                              : getStatusColor(agent.status)
                                          }`}>
                                            {isActive ? 'ACTIVE' : agent.status.toUpperCase()}
                                          </span>
                                        </div>

                                        {metric && metric.active_tasks > 0 && (
                                          <div className="flex items-center gap-1.5 text-xs text-blue-400 mt-1.5">
                                            <Activity className="w-3 h-3 animate-pulse" />
                                            <span className="font-bold font-mono">{metric.active_tasks} tasks</span>
                                          </div>
                                        )}
                                        
                                        {/* Cyberpunk Tooltip */}
                                        <div className="absolute left-full ml-3 top-0 hidden group-hover/agent:block z-50 pointer-events-none w-64">
                                          <div className="relative">
                                            <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500/50 to-purple-500/50 rounded-xl blur-md" />
                                            <div className="relative bg-black/90 backdrop-blur-xl border-2 border-cyan-500/40 rounded-xl p-4 text-xs shadow-2xl overflow-hidden">
                                              {/* Corner accents */}
                                              <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-cyan-400" />
                                              <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-cyan-400" />
                                              <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-cyan-400" />
                                              <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-cyan-400" />

                                              {/* Grid background */}
                                              <div className="absolute inset-0 opacity-5">
                                                {[...Array(4)].map((_, i) => (
                                                  <div key={i} className="absolute h-px w-full bg-cyan-400" style={{ top: `${25 * i}%` }} />
                                                ))}
                                              </div>

                                            <div className="relative">
                                            <p className="text-cyan-200 mb-3 font-medium leading-relaxed font-mono">{agent.description}</p>
                                            <div className="space-y-2 text-cyan-400/80 border-t border-cyan-500/20 pt-3">
                                              <div className="flex justify-between">
                                                <span className="font-mono text-xs uppercase tracking-wider">Type:</span>
                                                <span className="text-cyan-300 font-black capitalize font-mono">{agent.agent_type}</span>
                                              </div>
                                              {crews.length > 0 && (
                                                <div className="flex justify-between">
                                                  <span className="font-mono text-xs uppercase tracking-wider">Crews:</span>
                                                  <span className="text-cyan-300 font-black text-right font-mono">{crews.join(', ')}</span>
                                                </div>
                                              )}
                                              {metric && (
                                                <>
                                                  {metric.active_tasks > 0 && (
                                                    <div className="flex justify-between">
                                                      <span className="font-mono text-xs uppercase tracking-wider">Active:</span>
                                                      <span className="text-blue-400 font-black font-mono">{metric.active_tasks}</span>
                                                    </div>
                                                  )}
                                                  {metric.completed_tasks > 0 && (
                                                    <div className="flex justify-between">
                                                      <span className="font-mono text-xs uppercase tracking-wider">Complete:</span>
                                                      <span className="text-green-400 font-black font-mono">{metric.completed_tasks}</span>
                                                    </div>
                                                  )}
                                                </>
                                              )}
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
                    </div>
                  );
                })()}
              </div>
            </div>
          </div>
        ) : (
          <>
              {/* Cyberpunk Agents Grid by Type */}
              {Object.entries(agentsByType).map(([type, typeAgents], typeIdx) => (
              <div key={type} className="group relative mb-10 animate-fade-in" style={{ animationDelay: `${0.3 + typeIdx * 0.1}s` }}>
                {/* Section glow */}
                <div className="absolute -inset-2 bg-gradient-to-r from-purple-500/20 via-cyan-500/20 to-purple-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />

                <div className="relative mb-6 pb-4 border-b-2 border-gradient-to-r from-transparent via-cyan-500/30 to-transparent">
                  <h2 className="text-3xl font-black bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent capitalize font-mono tracking-tight">
                    {type} AGENTS <span className="text-cyan-500/60">({typeAgents.length})</span>
                  </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {typeAgents.map((agent, agentIdx) => {
                    const metric = metrics[agent.id];
                    return (
                      <div
                        key={agent.id}
                        className="group/gridcard relative animate-fade-in"
                        style={{ animationDelay: `${0.4 + typeIdx * 0.1 + agentIdx * 0.05}s` }}
                      >
                        {/* Holographic glow */}
                        <div className={`absolute -inset-0.5 rounded-2xl blur-md transition-opacity ${
                          isAgentActuallyWorking(agent)
                            ? 'bg-gradient-to-r from-green-500/50 via-emerald-500/50 to-green-500/50 opacity-70 animate-pulse'
                            : 'bg-gradient-to-r from-cyan-500/40 via-purple-500/40 to-cyan-500/40 opacity-0 group-hover/gridcard:opacity-100'
                        }`} />

                        <div className={`relative bg-black/60 backdrop-blur-xl rounded-2xl border-2 overflow-hidden transition-all duration-300 hover:scale-[1.02] ${
                          isAgentActuallyWorking(agent)
                            ? 'border-green-500/60 shadow-[0_0_30px_rgba(34,197,94,0.3)]'
                            : 'border-cyan-500/30 hover:border-cyan-500/50'
                        }`}>
                          {/* Corner accents */}
                          <div className={`absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 ${isAgentActuallyWorking(agent) ? 'border-green-400' : 'border-cyan-400'}`} />
                          <div className={`absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 ${isAgentActuallyWorking(agent) ? 'border-green-400' : 'border-cyan-400'}`} />
                          <div className={`absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 ${isAgentActuallyWorking(agent) ? 'border-green-400' : 'border-cyan-400'}`} />
                          <div className={`absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 ${isAgentActuallyWorking(agent) ? 'border-green-400' : 'border-cyan-400'}`} />

                          {/* Grid background */}
                          <div className="absolute inset-0 opacity-5">
                            {[...Array(6)].map((_, i) => (
                              <div key={i} className={`absolute h-px w-full ${isAgentActuallyWorking(agent) ? 'bg-green-400' : 'bg-cyan-400'}`} style={{ top: `${(100 / 6) * i}%` }} />
                            ))}
                          </div>

                        <div className="relative p-6">
                          {/* Cyberpunk Header */}
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-3">
                                {isAgentActuallyWorking(agent) ? (
                                  <div className="relative">
                                    <CheckCircle className="w-6 h-6 text-green-400" />
                                    <div className="absolute inset-0 rounded-full bg-green-500/40 animate-ping" />
                                  </div>
                                ) : (
                                  <div className="scale-110">{getStatusIcon(agent.status)}</div>
                                )}
                                <h3 className="font-black text-cyan-300 text-lg font-mono uppercase tracking-tight">{agent.name}</h3>
                              </div>
                              <p className="text-sm text-blue-300/70 line-clamp-2 font-mono leading-relaxed">
                                {agent.description || 'No description'}
                              </p>
                            </div>
                          </div>

                          {/* Cyberpunk Status Badges */}
                          <div className="flex gap-2 mb-4 flex-wrap">
                            <span className={`px-3 py-1.5 text-xs font-black rounded-lg border font-mono uppercase tracking-wider ${
                              isAgentActuallyWorking(agent)
                                ? 'bg-black/40 text-green-400 border-green-500/60'
                                : getStatusColor(agent.status)
                            }`}>
                              {isAgentActuallyWorking(agent) ? 'ACTIVE' : agent.status.toUpperCase()}
                            </span>
                            <span className={`px-3 py-1.5 text-xs font-black rounded-lg border font-mono uppercase tracking-wider ${getAgentTypeColor(agent.agent_type)}`}>
                              {agent.agent_type}
                            </span>
                          </div>

                          {/* Cyberpunk Metrics */}
                          {metric ? (
                            <div className="space-y-3 mb-4 pb-4 border-b border-cyan-500/20">
                              {metric.active_tasks > 0 && (
                                <div className="flex items-center justify-between text-sm">
                                  <span className="text-blue-300/80 flex items-center gap-2 font-mono uppercase tracking-wider text-xs">
                                    <Activity className="w-4 h-4 text-blue-400 animate-pulse" />
                                    Active
                                  </span>
                                  <span className="font-black text-blue-400 font-mono text-lg">
                                    {metric.active_tasks}
                                  </span>
                                </div>
                              )}
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-green-300/80 flex items-center gap-2 font-mono uppercase tracking-wider text-xs">
                                  <TrendingUp className="w-4 h-4 text-green-400" />
                                  Complete
                                </span>
                                <span className="font-black text-green-400 font-mono text-lg">
                                  {metric.completed_tasks}
                                </span>
                              </div>
                              {metric.cpu_usage > 0 && (
                                <div className="flex items-center justify-between text-sm">
                                  <span className="text-purple-300/80 flex items-center gap-2 font-mono uppercase tracking-wider text-xs">
                                    <Zap className="w-4 h-4 text-purple-400" />
                                    CPU
                                  </span>
                                  <span className="font-black text-purple-400 font-mono text-lg">
                                    {metric.cpu_usage.toFixed(1)}%
                                  </span>
                                </div>
                              )}
                              {metric.error_count > 0 && (
                                <div className="flex items-center justify-between text-sm">
                                  <span className="text-red-300/80 flex items-center gap-2 font-mono uppercase tracking-wider text-xs">
                                    <AlertCircle className="w-4 h-4 text-red-400" />
                                    Errors
                                  </span>
                                  <span className="font-black text-red-400 font-mono text-lg">
                                    {metric.error_count}
                                  </span>
                                </div>
                              )}
                            </div>
                          ) : (
                            <div className="mb-4 pb-4 border-b border-cyan-500/20">
                              <p className="text-xs text-cyan-500/40 italic font-mono uppercase tracking-wider">No activity data</p>
                            </div>
                          )}

                          {/* Cyberpunk Last Heartbeat */}
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-black text-cyan-400/60 font-mono uppercase tracking-wider">Last Seen</span>
                            <span className="font-black text-cyan-400 font-mono">{formatUptime(agent.last_heartbeat)}</span>
                          </div>
                        </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
              </>
            )}
          </>
        )}
      </main>
    </div>
  );
}
