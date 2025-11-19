import { useEffect, useRef, useState } from 'react';
import { Activity, Zap, CheckCircle, AlertCircle, Clock, ArrowRight, Play, Pause, Loader2 } from 'lucide-react';
import { AgentActivity } from '../hooks/useAgentWebSocket';

interface AgentWorkflowViewProps {
  activities: AgentActivity[];
  connections: Array<{
    from: string;
    to: string;
    status: 'active' | 'pending' | 'completed';
  }>;
}

// Agent workflow configuration with modern styling
const AGENT_WORKFLOW = [
  { id: 'master_intelligence', name: 'Master Intelligence', type: 'intelligence', layer: 0, icon: '🧠' },
  { id: 'icp_analyzer', name: 'ICP Analyzer', type: 'intelligence', layer: 1, icon: '🎯' },
  { id: 'lead_scorer', name: 'Lead Scorer', type: 'intelligence', layer: 1, icon: '⭐' },
  { id: 'researcher', name: 'Researcher', type: 'research', layer: 2, icon: '🔍' },
  { id: 'dead_lead_reactivation', name: 'Dead Lead Reactivation', type: 'reactivation', layer: 2, icon: '🔄' },
  { id: 'subject_optimizer', name: 'Subject Optimizer', type: 'content', layer: 3, icon: '✨' },
  { id: 'writer', name: 'Writer', type: 'content', layer: 3, icon: '✍️' },
  { id: 'compliance', name: 'Compliance', type: 'safety', layer: 4, icon: '🛡️' },
  { id: 'quality_control', name: 'Quality Control', type: 'safety', layer: 4, icon: '✓' },
  { id: 'tracker', name: 'Tracker', type: 'sync', layer: 5, icon: '📊' },
  { id: 'email_sender', name: 'Email Sender', type: 'infrastructure', layer: 5, icon: '📧' },
  { id: 'engagement_analyzer', name: 'Engagement Analyzer', type: 'content', layer: 6, icon: '📈' },
  { id: 'followup', name: 'Follow-Up', type: 'content', layer: 6, icon: '🔔' },
  { id: 'objection_handler', name: 'Objection Handler', type: 'content', layer: 6, icon: '💬' },
  { id: 'meeting_booker', name: 'Meeting Booker', type: 'revenue', layer: 7, icon: '📅' },
  { id: 'billing', name: 'Billing', type: 'revenue', layer: 7, icon: '💰' },
];

const AGENT_COLORS = {
  intelligence: {
    bg: 'bg-black/60',
    border: 'border-purple-500/40',
    text: 'text-purple-400',
    glow: 'from-purple-500/50 via-pink-500/50 to-purple-500/50',
    activeGlow: 'shadow-[0_0_30px_rgba(168,85,247,0.4)]'
  },
  research: {
    bg: 'bg-black/60',
    border: 'border-blue-500/40',
    text: 'text-blue-400',
    glow: 'from-blue-500/50 via-cyan-500/50 to-blue-500/50',
    activeGlow: 'shadow-[0_0_30px_rgba(59,130,246,0.4)]'
  },
  reactivation: {
    bg: 'bg-black/60',
    border: 'border-cyan-500/40',
    text: 'text-cyan-400',
    glow: 'from-cyan-500/50 via-blue-500/50 to-cyan-500/50',
    activeGlow: 'shadow-[0_0_30px_rgba(34,211,238,0.4)]'
  },
  content: {
    bg: 'bg-black/60',
    border: 'border-green-500/40',
    text: 'text-green-400',
    glow: 'from-green-500/50 via-emerald-500/50 to-green-500/50',
    activeGlow: 'shadow-[0_0_30px_rgba(34,197,94,0.4)]'
  },
  safety: {
    bg: 'bg-black/60',
    border: 'border-yellow-500/40',
    text: 'text-yellow-400',
    glow: 'from-yellow-500/50 via-orange-500/50 to-yellow-500/50',
    activeGlow: 'shadow-[0_0_30px_rgba(234,179,8,0.4)]'
  },
  sync: {
    bg: 'bg-black/60',
    border: 'border-orange-500/40',
    text: 'text-orange-400',
    glow: 'from-orange-500/50 via-red-500/50 to-orange-500/50',
    activeGlow: 'shadow-[0_0_30px_rgba(249,115,22,0.4)]'
  },
  infrastructure: {
    bg: 'bg-black/60',
    border: 'border-red-500/40',
    text: 'text-red-400',
    glow: 'from-red-500/50 via-pink-500/50 to-red-500/50',
    activeGlow: 'shadow-[0_0_30px_rgba(239,68,68,0.4)]'
  },
  revenue: {
    bg: 'bg-black/60',
    border: 'border-emerald-500/40',
    text: 'text-emerald-400',
    glow: 'from-emerald-500/50 via-green-500/50 to-emerald-500/50',
    activeGlow: 'shadow-[0_0_30px_rgba(16,185,129,0.4)]'
  },
};

export function AgentWorkflowView({ activities, connections }: AgentWorkflowViewProps) {
  const [agentStates, setAgentStates] = useState<Record<string, AgentActivity>>({});
  const canvasRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const newStates: Record<string, AgentActivity> = {};
    activities.forEach((activity) => {
      newStates[activity.agent_id] = activity;
    });
    setAgentStates(newStates);
  }, [activities]);

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'working':
        return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  // Group agents by layer
  const agentsByLayer = AGENT_WORKFLOW.reduce((acc, agent) => {
    if (!acc[agent.layer]) acc[agent.layer] = [];
    acc[agent.layer].push(agent);
    return acc;
  }, {} as Record<number, typeof AGENT_WORKFLOW>);

  const layers = Object.keys(agentsByLayer).map(Number).sort((a, b) => a - b);

  return (
    <div className="space-y-6">
      {/* Cyberpunk Activity Feed */}
      <div className="group relative">
        {/* Holographic glow */}
        <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/50 via-blue-500/50 to-cyan-500/50 rounded-2xl blur-xl opacity-60 group-hover:opacity-100 transition-opacity animate-pulse" />

        <div className="relative bg-black/60 backdrop-blur-xl border border-cyan-500/30 rounded-2xl p-6 overflow-hidden">
          {/* Corner accents */}
          <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-cyan-400" />
          <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-cyan-400" />
          <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-cyan-400" />
          <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-cyan-400" />

          {/* Scan lines */}
          <div className="absolute inset-0 pointer-events-none opacity-10">
            {[...Array(20)].map((_, i) => (
              <div key={i} className="h-px w-full bg-cyan-400" style={{ top: `${i * 5}%` }} />
            ))}
          </div>

          <div className="relative flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="relative w-12 h-12 rounded-lg bg-black/40 border border-cyan-500/40 flex items-center justify-center overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 animate-pulse" />
                <Zap className="w-6 h-6 text-cyan-400 relative z-10" />
              </div>
              <div>
                <h3 className="text-xl font-black bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent tracking-tight">
                  LIVE ACTIVITY STREAM
                </h3>
                <p className="text-xs text-cyan-500/70 font-mono uppercase tracking-wider">Real-time agent execution</p>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-1 bg-green-500/40 rounded-lg blur-md animate-pulse" />
              <div className="relative flex items-center gap-2 px-4 py-2 rounded-lg bg-black/60 border border-green-500/40">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.8)]" />
                <span className="text-xs font-bold text-green-400 font-mono uppercase tracking-wider">ONLINE</span>
              </div>
            </div>
          </div>

        <div className="relative space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
          {activities.slice(0, 5).map((activity, idx) => (
            <div
              key={`${activity.agent_id}-${idx}`}
              className="group relative"
            >
              {/* Activity card glow */}
              <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-blue-500/30 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity" />

              <div className="relative bg-black/40 backdrop-blur-sm hover:bg-black/60 rounded-xl p-4 border border-blue-500/20 hover:border-blue-500/40 transition-all duration-300 cursor-pointer overflow-hidden">
                {/* Animated background grid */}
                <div className="absolute inset-0 opacity-5">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="absolute h-px w-full bg-blue-400" style={{ top: `${33 * i}%` }} />
                  ))}
                </div>

                <div className="relative flex items-start gap-4">
                  <div className="flex-shrink-0 relative w-10 h-10 rounded-lg bg-black/60 border border-blue-500/30 flex items-center justify-center overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10" />
                    <div className="relative z-10">{getStatusIcon(activity.status)}</div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-cyan-300 text-sm font-mono">{activity.agent_name}</span>
                      <span className="text-xs text-cyan-600/60 font-mono">
                        {new Date(activity.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-blue-300/80 line-clamp-1 font-mono">{activity.task}</p>
                    {activity.progress !== undefined && (
                      <div className="mt-3">
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-xs text-blue-400/60 font-mono uppercase tracking-wider">Progress</span>
                          <span className="text-xs font-bold text-cyan-400 font-mono">{activity.progress}%</span>
                        </div>
                        <div className="relative w-full h-1.5 bg-black/60 rounded-full overflow-hidden border border-blue-500/20">
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/10 to-transparent animate-pulse" />
                          <div
                            className="relative h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 rounded-full transition-all duration-500 shadow-[0_0_10px_rgba(59,130,246,0.6)]"
                            style={{ width: `${activity.progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          {activities.length === 0 && (
            <div className="relative text-center py-12">
              <div className="relative w-20 h-20 rounded-xl bg-black/60 border-2 border-cyan-500/30 flex items-center justify-center mx-auto mb-4 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 animate-pulse" />
                <Clock className="w-10 h-10 text-cyan-400/50 relative z-10" />
              </div>
              <p className="text-sm text-cyan-400/60 font-mono uppercase tracking-wider">Waiting for agent activity...</p>
            </div>
          )}
        </div>
        </div>
      </div>

      {/* Cyberpunk Workflow Canvas */}
      <div className="group relative">
        {/* Holographic glow */}
        <div className="absolute -inset-1 bg-gradient-to-r from-purple-500/50 via-pink-500/50 to-purple-500/50 rounded-2xl blur-xl opacity-60 group-hover:opacity-100 transition-opacity animate-pulse" />

        <div className="relative bg-black/60 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-8 overflow-hidden">
          {/* Corner accents */}
          <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-purple-400" />
          <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-purple-400" />
          <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-purple-400" />
          <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-purple-400" />

          {/* Scan lines */}
          <div className="absolute inset-0 pointer-events-none opacity-5">
            {[...Array(30)].map((_, i) => (
              <div key={i} className="h-px w-full bg-purple-400" style={{ top: `${i * 3.33}%` }} />
            ))}
          </div>

          <div className="relative mb-8">
            <h3 className="text-2xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent tracking-tight mb-2">
              AGENT WORKFLOW PIPELINE
            </h3>
            <p className="text-xs text-purple-500/70 font-mono uppercase tracking-wider">Node-based execution flow</p>
          </div>

        <div ref={canvasRef} className="relative space-y-12 overflow-x-auto pb-4">
          {layers.map((layer, layerIdx) => (
            <div key={layer} className="relative">
              {/* Cyberpunk Layer Header */}
              <div className="flex items-center gap-3 mb-6">
                <div className="relative w-10 h-10 rounded-lg bg-black/60 border-2 border-purple-500/40 flex items-center justify-center overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-pink-500/20 animate-pulse" />
                  <span className="relative text-sm font-black text-purple-400 font-mono">L{layer + 1}</span>
                </div>
                <div className="flex-1 h-px bg-gradient-to-r from-purple-500/50 via-pink-500/30 to-transparent" />
                <span className="text-xs text-purple-500/50 font-mono uppercase tracking-wider">Layer {layer + 1}</span>
              </div>

              {/* Agent Nodes */}
              <div className="flex flex-wrap gap-4">
                {agentsByLayer[layer].map((agent) => {
                  const state = agentStates[agent.id];
                  const isActive = state?.status === 'working';
                  const isCompleted = state?.status === 'completed';
                  const colors = AGENT_COLORS[agent.type as keyof typeof AGENT_COLORS];

                  return (
                    <div
                      key={agent.id}
                      className="group relative"
                    >
                      {/* Holographic glow for active agents */}
                      {isActive && (
                        <div className={`absolute -inset-1 bg-gradient-to-r ${colors.glow} rounded-xl blur-lg opacity-70 animate-pulse`} />
                      )}

                      {/* Node Card */}
                      <div
                        className={`
                          relative min-w-[220px] rounded-xl border-2 transition-all duration-300 cursor-pointer overflow-hidden
                          ${colors.bg} ${colors.border}
                          ${isActive ? `${colors.activeGlow} scale-105` : 'hover:scale-105'}
                          backdrop-blur-xl
                        `}
                      >
                        {/* Corner accents */}
                        <div className={`absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 ${colors.border}`} />
                        <div className={`absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 ${colors.border}`} />
                        <div className={`absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 ${colors.border}`} />
                        <div className={`absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 ${colors.border}`} />

                        {/* Grid background */}
                        <div className="absolute inset-0 opacity-5">
                          {[...Array(5)].map((_, i) => (
                            <div key={i} className={`absolute h-px w-full bg-current ${colors.text}`} style={{ top: `${20 * i}%` }} />
                          ))}
                        </div>

                        <div className="relative p-5">
                          {/* Header */}
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl filter drop-shadow-lg">{agent.icon}</span>
                              <span className={`text-xs font-black uppercase tracking-wider ${colors.text} font-mono`}>
                                {agent.type}
                              </span>
                            </div>
                            <div className={`relative w-7 h-7 rounded-lg bg-black/40 border ${colors.border} flex items-center justify-center`}>
                              <div className={`absolute inset-0 bg-gradient-to-br ${colors.glow} opacity-20`} />
                              <div className="relative z-10">{getStatusIcon(state?.status)}</div>
                            </div>
                          </div>

                          {/* Name */}
                          <h4 className={`font-black text-sm mb-2 ${colors.text} font-mono uppercase tracking-tight`}>{agent.name}</h4>

                          {/* Task */}
                          {state?.task && (
                            <p className="text-xs text-white/60 line-clamp-2 mb-3 font-mono">
                              {state.task}
                            </p>
                          )}

                          {/* Progress Bar */}
                          {state?.progress !== undefined && isActive && (
                            <div className="space-y-1.5 mb-3">
                              <div className="flex justify-between text-xs">
                                <span className="text-white/40 font-mono uppercase tracking-wider">Progress</span>
                                <span className={`font-black ${colors.text} font-mono`}>{state.progress}%</span>
                              </div>
                              <div className={`relative w-full h-1.5 bg-black/60 rounded-full overflow-hidden border ${colors.border}`}>
                                <div className={`absolute inset-0 bg-gradient-to-r ${colors.glow} opacity-20 animate-pulse`} />
                                <div
                                  className={`relative h-full bg-gradient-to-r ${colors.glow} rounded-full transition-all duration-500 ${colors.activeGlow}`}
                                  style={{ width: `${state.progress}%` }}
                                />
                              </div>
                            </div>
                          )}

                          {/* Status Badge */}
                          <div className={`pt-3 border-t ${colors.border}`}>
                            <span className={`
                              inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-black font-mono uppercase tracking-wider
                              ${isActive ? `bg-black/40 ${colors.text} border ${colors.border}` :
                                isCompleted ? 'bg-black/40 text-green-400 border border-green-500/40' :
                                'bg-black/40 text-gray-500 border border-gray-600/40'}
                            `}>
                              {isActive && <Play className="w-3 h-3" />}
                              {isCompleted && <CheckCircle className="w-3 h-3" />}
                              {!isActive && !isCompleted && <Pause className="w-3 h-3" />}
                              {isActive ? 'Running' : isCompleted ? 'Complete' : 'Idle'}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Cyberpunk Connection Arrow */}
                      {layerIdx < layers.length - 1 && (
                        <div className="absolute left-1/2 -translate-x-1/2 -bottom-10 z-10">
                          <div className="flex flex-col items-center">
                            <div className="w-0.5 h-6 bg-gradient-to-b from-purple-500/60 via-pink-500/40 to-transparent" />
                            <div className="relative">
                              <div className="absolute inset-0 blur-sm bg-purple-500/40 rounded-full" />
                              <ArrowRight className="w-4 h-4 text-purple-400 rotate-90 relative z-10" />
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Cyberpunk Legend */}
        <div className="relative mt-8 pt-6 border-t border-purple-500/20">
          <h4 className="text-xs font-black text-purple-400/60 uppercase tracking-wider mb-4 font-mono">Agent Types</h4>
          <div className="flex flex-wrap gap-4">
            {Object.entries(AGENT_COLORS).map(([type, colors]) => (
              <div key={type} className="group flex items-center gap-2">
                <div className={`relative w-4 h-4 rounded border-2 ${colors.border} ${colors.bg} overflow-hidden`}>
                  <div className={`absolute inset-0 bg-gradient-to-br ${colors.glow} opacity-30 group-hover:opacity-60 transition-opacity`} />
                </div>
                <span className={`text-xs ${colors.text} capitalize font-mono tracking-wide`}>{type}</span>
              </div>
            ))}
          </div>
        </div>
        </div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.4);
          border: 1px solid rgba(34, 211, 238, 0.2);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, rgba(34, 211, 238, 0.6), rgba(59, 130, 246, 0.6));
          border-radius: 4px;
          border: 1px solid rgba(34, 211, 238, 0.3);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(180deg, rgba(34, 211, 238, 0.8), rgba(59, 130, 246, 0.8));
          box-shadow: 0 0 10px rgba(34, 211, 238, 0.5);
        }
      `}</style>
    </div>
  );
}
