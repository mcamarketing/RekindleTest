import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MissionType,
  MissionState,
  RexStatusResponse,
  Mission,
  CreateMissionRequest,
  ResourcePool,
} from '@/types/rex';

interface CommandCenterProps {
  userId: string;
}

const CommandCenter: React.FC<CommandCenterProps> = ({ userId }) => {
  const [status, setStatus] = useState<RexStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedView, setSelectedView] = useState<'overview' | 'missions' | 'resources'>('overview');
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Fetch Rex status
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  // WebSocket connection
  useEffect(() => {
    const websocket = new WebSocket(`ws://localhost:8000/api/rex/ws?user_id=${userId}`);

    websocket.onopen = () => {
      console.log('Rex WebSocket connected');
      // Subscribe to all updates
      websocket.send(JSON.stringify({
        type: 'subscribe',
        subscriptions: ['missions', 'agents', 'domains', 'analytics', 'system']
      }));
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('Rex WebSocket disconnected');
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [userId]);

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/rex/status');
      if (!response.ok) throw new Error('Failed to fetch Rex status');

      const data = await response.json();
      setStatus(data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setLoading(false);
    }
  };

  const handleWebSocketMessage = (message: any) => {
    console.log('WebSocket message:', message);

    // Update UI based on message type
    if (message.type === 'mission.progress' || message.type === 'mission.completed') {
      // Refresh status to get latest data
      fetchStatus();
    }
  };

  const createMission = async (request: CreateMissionRequest) => {
    try {
      const response = await fetch('/api/rex/missions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.ok) throw new Error('Failed to create mission');

      const data = await response.json();
      console.log('Mission created:', data);

      // Refresh status
      fetchStatus();
    } catch (err) {
      console.error('Error creating mission:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-2">Error loading Rex Command Center</div>
          <div className="text-slate-400">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-2xl font-bold tracking-tight">
                REX <span className="text-blue-400">Command Center</span>
              </div>
              <StatusIndicator status={status?.status || 'error'} />
            </div>

            <div className="flex items-center gap-4">
              <div className="text-sm text-slate-400">
                Uptime: {formatUptime(status?.uptime_ms || 0)}
              </div>
              <div className="flex gap-2">
                <ViewButton
                  active={selectedView === 'overview'}
                  onClick={() => setSelectedView('overview')}
                >
                  Overview
                </ViewButton>
                <ViewButton
                  active={selectedView === 'missions'}
                  onClick={() => setSelectedView('missions')}
                >
                  Missions
                </ViewButton>
                <ViewButton
                  active={selectedView === 'resources'}
                  onClick={() => setSelectedView('resources')}
                >
                  Resources
                </ViewButton>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {selectedView === 'overview' && (
            <OverviewView status={status} onCreateMission={createMission} />
          )}
          {selectedView === 'missions' && (
            <MissionsView status={status} />
          )}
          {selectedView === 'resources' && (
            <ResourcesView resources={status?.resources} />
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

// Status Indicator
const StatusIndicator: React.FC<{ status: string }> = ({ status }) => {
  const colors = {
    operational: 'bg-green-500',
    degraded: 'bg-yellow-500',
    error: 'bg-red-500',
  };

  return (
    <div className="flex items-center gap-2">
      <motion.div
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
        className={`w-2 h-2 rounded-full ${colors[status as keyof typeof colors]}`}
      />
      <span className="text-sm text-slate-300 capitalize">{status}</span>
    </div>
  );
};

// View Button
const ViewButton: React.FC<{
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}> = ({ active, onClick, children }) => {
  return (
    <button
      onClick={onClick}
      className={`
        px-4 py-2 rounded-lg text-sm font-medium transition-all
        ${active
          ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/25'
          : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
        }
      `}
    >
      {children}
    </button>
  );
};

// Overview View
const OverviewView: React.FC<{
  status: RexStatusResponse | null;
  onCreateMission: (request: CreateMissionRequest) => void;
}> = ({ status, onCreateMission }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Mission Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          label="Active Missions"
          value={status?.missions.active || 0}
          trend="neutral"
          icon="🎯"
        />
        <StatCard
          label="Queued"
          value={status?.missions.queued || 0}
          trend="neutral"
          icon="⏳"
        />
        <StatCard
          label="Completed (24h)"
          value={status?.missions.completed_24h || 0}
          trend="up"
          icon="✅"
        />
        <StatCard
          label="Failed (24h)"
          value={status?.missions.failed_24h || 0}
          trend={status?.missions.failed_24h && status.missions.failed_24h > 5 ? 'down' : 'neutral'}
          icon="❌"
        />
      </div>

      {/* Resource Pool Summary */}
      <div className="grid grid-cols-3 gap-4">
        <ResourceCard
          title="Agent Pool"
          data={status?.resources.agents || {}}
        />
        <ResourceCard
          title="Domain Pool"
          data={status?.resources.domains || {}}
        />
        <ResourceCard
          title="API Limits"
          data={status?.resources.api_limits || {}}
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-3 gap-4">
          <ActionButton
            label="Reactivate Dead Leads"
            icon="🔄"
            onClick={() => onCreateMission({
              type: MissionType.LEAD_REACTIVATION,
              priority: 70,
            })}
          />
          <ActionButton
            label="Execute Campaign"
            icon="📧"
            onClick={() => onCreateMission({
              type: MissionType.CAMPAIGN_EXECUTION,
              priority: 80,
            })}
          />
          <ActionButton
            label="Extract ICP"
            icon="🎯"
            onClick={() => onCreateMission({
              type: MissionType.ICP_EXTRACTION,
              priority: 60,
            })}
          />
        </div>
      </div>
    </motion.div>
  );
};

// Missions View
const MissionsView: React.FC<{ status: RexStatusResponse | null }> = ({ status }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6"
    >
      <h3 className="text-lg font-semibold mb-4">Mission Feed</h3>
      <div className="text-slate-400 text-center py-12">
        Mission feed component coming soon...
      </div>
    </motion.div>
  );
};

// Resources View
const ResourcesView: React.FC<{ resources?: ResourcePool }> = ({ resources }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Agent Status Grid */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">Agent Status</h3>
        <div className="grid grid-cols-2 gap-4">
          {resources?.agents && Object.entries(resources.agents).map(([crew, stats]) => (
            <div key={crew} className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-4">
              <div className="font-medium text-sm mb-2">{formatCrewName(crew)}</div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <div className="text-slate-400">Available</div>
                  <div className="text-green-400 font-semibold">{stats.available}</div>
                </div>
                <div>
                  <div className="text-slate-400">Executing</div>
                  <div className="text-blue-400 font-semibold">{stats.executing}</div>
                </div>
                <div>
                  <div className="text-slate-400">Failed</div>
                  <div className="text-red-400 font-semibold">{stats.failed}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Domain Health */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">Domain Health</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">Total Domains</div>
            <div className="text-2xl font-semibold">{resources?.domains.total || 0}</div>
          </div>
          <div className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">Active</div>
            <div className="text-2xl font-semibold text-green-400">{resources?.domains.active || 0}</div>
          </div>
          <div className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">Warming</div>
            <div className="text-2xl font-semibold text-yellow-400">{resources?.domains.warming || 0}</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// Stat Card
const StatCard: React.FC<{
  label: string;
  value: number;
  trend: 'up' | 'down' | 'neutral';
  icon: string;
}> = ({ label, value, trend, icon }) => {
  const trendColors = {
    up: 'text-green-400',
    down: 'text-red-400',
    neutral: 'text-slate-400',
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6"
    >
      <div className="flex items-start justify-between mb-2">
        <div className="text-2xl">{icon}</div>
      </div>
      <div className="text-3xl font-bold mb-1">{value}</div>
      <div className="text-sm text-slate-400">{label}</div>
    </motion.div>
  );
};

// Resource Card
const ResourceCard: React.FC<{
  title: string;
  data: any;
}> = ({ title, data }) => {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
      <h4 className="font-semibold mb-4">{title}</h4>
      <div className="space-y-2">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex justify-between text-sm">
            <span className="text-slate-400">{formatKey(key)}</span>
            <span className="font-medium">{formatValue(value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Action Button
const ActionButton: React.FC<{
  label: string;
  icon: string;
  onClick: () => void;
}> = ({ label, icon, onClick }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="bg-slate-700/50 border border-slate-600/50 rounded-lg p-4 text-left hover:bg-slate-700 transition-colors"
    >
      <div className="text-2xl mb-2">{icon}</div>
      <div className="text-sm font-medium">{label}</div>
    </motion.button>
  );
};

// Utility Functions
const formatUptime = (ms: number): string => {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ${hours % 24}h`;
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
};

const formatCrewName = (crew: string): string => {
  return crew
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const formatKey = (key: string): string => {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const formatValue = (value: any): string => {
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value);
  }
  return String(value);
};

export default CommandCenter;
