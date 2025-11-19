import { useEffect, useState } from 'react';
import { Navigation } from '../components/Navigation';
import { supabase } from '../lib/supabase';
import { apiClient, checkBackendHealth } from '../lib/api';
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react';

interface MetricsData {
  timestamp: string;
  cpu: number;
  memory: number;
  responseTime: number;
  errors: number;
}

interface TasksData {
  date: string;
  completed: number;
  failed: number;
  pending: number;
}

export function Analytics() {
  const [metricsHistory, setMetricsHistory] = useState<MetricsData[]>([]);
  const [tasksHistory, setTasksHistory] = useState<TasksData[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');
  const [useBackend, setUseBackend] = useState(false);

  useEffect(() => {
    checkBackend();
  }, []);

  useEffect(() => {
    loadAnalytics();
  }, [timeRange, useBackend]);

  const checkBackend = async () => {
    const isHealthy = await checkBackendHealth();
    setUseBackend(isHealthy);
  };

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      await Promise.all([loadMetricsHistory(), loadTasksHistory()]);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMetricsHistory = async () => {
    const hoursBack = timeRange === '24h' ? 24 : timeRange === '7d' ? 168 : 720;
    const timeAgo = new Date(Date.now() - hoursBack * 60 * 60 * 1000).toISOString();

    const { data, error } = await supabase
      .from('agent_metrics')
      .select('*')
      .gte('recorded_at', timeAgo)
      .order('recorded_at', { ascending: true });

    if (error) throw error;

    const aggregated = aggregateMetrics(data || [], timeRange);
    setMetricsHistory(aggregated);
  };

  const loadTasksHistory = async () => {
    const daysBack = timeRange === '24h' ? 1 : timeRange === '7d' ? 7 : 30;
    const timeAgo = new Date(Date.now() - daysBack * 24 * 60 * 60 * 1000).toISOString();

    const { data, error } = await supabase
      .from('agent_tasks')
      .select('status, created_at')
      .gte('created_at', timeAgo);

    if (error) throw error;

    const aggregated = aggregateTasks(data || [], timeRange);
    setTasksHistory(aggregated);
  };

  const aggregateMetrics = (data: any[], range: string): MetricsData[] => {
    if (data.length === 0) return [];

    const bucketSize = range === '24h' ? 3600000 : range === '7d' ? 3600000 * 4 : 86400000;
    const buckets: Record<number, any[]> = {};

    data.forEach(item => {
      const time = new Date(item.recorded_at).getTime();
      const bucketKey = Math.floor(time / bucketSize) * bucketSize;
      if (!buckets[bucketKey]) buckets[bucketKey] = [];
      buckets[bucketKey].push(item);
    });

    return Object.entries(buckets).map(([key, items]) => ({
      timestamp: new Date(parseInt(key)).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      cpu: items.reduce((sum, i) => sum + Number(i.cpu_usage || 0), 0) / items.length,
      memory: items.reduce((sum, i) => sum + Number(i.memory_usage || 0), 0) / items.length,
      responseTime: items.reduce((sum, i) => sum + Number(i.response_time || 0), 0) / items.length,
      errors: items.reduce((sum, i) => sum + (i.error_count || 0), 0)
    }));
  };

  const aggregateTasks = (data: any[], range: string): TasksData[] => {
    const days = range === '24h' ? 1 : range === '7d' ? 7 : 30;
    const result: TasksData[] = [];

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(Date.now() - i * 24 * 60 * 60 * 1000);
      const dateStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      const dayStart = new Date(date.setHours(0, 0, 0, 0));
      const dayEnd = new Date(date.setHours(23, 59, 59, 999));

      const dayTasks = data.filter(t => {
        const taskDate = new Date(t.created_at);
        return taskDate >= dayStart && taskDate <= dayEnd;
      });

      result.push({
        date: dateStr,
        completed: dayTasks.filter(t => t.status === 'completed').length,
        failed: dayTasks.filter(t => t.status === 'failed').length,
        pending: dayTasks.filter(t => t.status === 'pending' || t.status === 'in_progress').length
      });
    }

    return result;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/3 w-[800px] h-[800px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" />
        </div>
        <Navigation currentPage="analytics" />
        <div className="flex items-center justify-center h-96 relative z-10">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-[#FF6B35]/30 rounded-full"></div>
            <div className="absolute inset-0 w-16 h-16 border-4 border-[#FF6B35] border-t-transparent rounded-full animate-spin"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 left-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
        <div className="absolute bottom-1/4 right-1/3 w-[700px] h-[700px] bg-purple-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '7s' }} />
      </div>

      <Navigation currentPage="analytics" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <div className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Analytics</h1>
            <p className="text-gray-400 text-lg">Agent performance metrics and insights</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setTimeRange('24h')}
              className={`px-6 py-3 rounded-xl font-bold transition-all duration-300 ${
                timeRange === '24h'
                  ? 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white shadow-2xl shadow-[#FF6B35]/40 scale-110'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10'
              }`}
            >
              24 Hours
            </button>
            <button
              onClick={() => setTimeRange('7d')}
              className={`px-6 py-3 rounded-xl font-bold transition-all duration-300 ${
                timeRange === '7d'
                  ? 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white shadow-2xl shadow-[#FF6B35]/40 scale-110'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10'
              }`}
            >
              7 Days
            </button>
            <button
              onClick={() => setTimeRange('30d')}
              className={`px-6 py-3 rounded-xl font-bold transition-all duration-300 ${
                timeRange === '30d'
                  ? 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white shadow-2xl shadow-[#FF6B35]/40 scale-110'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10'
              }`}
            >
              30 Days
            </button>
          </div>
        </div>

        <div className="space-y-8">
          {metricsHistory.length > 0 && (
            <>
              <div className="glass-card p-8 animate-fade-in">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-2xl shadow-lg">
                    <Activity className="w-6 h-6 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-white">CPU & Memory Usage</h2>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={metricsHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="timestamp" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip contentStyle={{ backgroundColor: '#1A1F2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="cpu"
                      stackId="1"
                      stroke="#FF6B35"
                      fill="#FF6B35"
                      fillOpacity={0.6}
                      name="CPU %"
                    />
                    <Area
                      type="monotone"
                      dataKey="memory"
                      stackId="2"
                      stroke="#F7931E"
                      fill="#F7931E"
                      fillOpacity={0.6}
                      name="Memory MB"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="glass-card p-8 animate-fade-in" style={{ animationDelay: '0.1s' }}>
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl shadow-lg">
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-white">Response Time</h2>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={metricsHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="timestamp" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip contentStyle={{ backgroundColor: '#1A1F2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="responseTime"
                      stroke="#3B82F6"
                      strokeWidth={3}
                      dot={false}
                      name="Response Time (ms)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </>
          )}

          {tasksHistory.length > 0 && (
            <div className="glass-card p-8 animate-fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl shadow-lg">
                  <CheckCircle2 className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white">Task Completion</h2>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={tasksHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="date" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip contentStyle={{ backgroundColor: '#1A1F2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                  <Legend />
                  <Bar dataKey="completed" fill="#10b981" name="Completed" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="pending" fill="#f59e0b" name="Pending" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="failed" fill="#ef4444" name="Failed" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {metricsHistory.length > 0 && (
            <div className="glass-card p-8 animate-fade-in" style={{ animationDelay: '0.3s' }}>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-red-500 to-pink-500 rounded-2xl shadow-lg">
                  <AlertCircle className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white">Error Count</h2>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={metricsHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="timestamp" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip contentStyle={{ backgroundColor: '#1A1F2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                  <Legend />
                  <Bar dataKey="errors" fill="#ef4444" name="Errors" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {metricsHistory.length === 0 && tasksHistory.length === 0 && (
            <div className="glass-card p-12 text-center">
              <div className="p-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-3xl w-fit mx-auto mb-6 shadow-2xl">
                <Activity className="w-20 h-20 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">No Data Available</h3>
              <p className="text-gray-400 text-lg">
                Analytics data will appear here once agents start reporting metrics
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
