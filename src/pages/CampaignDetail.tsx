// @ts-nocheck
import { useEffect, useState } from 'react';
import { Navigation } from '../components/Navigation';
import { supabase } from '../lib/supabase';
import { apiClient } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../components/Toast';
import {
  Play, Pause, ArrowLeft, Users, Mail, MousePointerClick,
  TrendingUp, Calendar, MessageSquare, CheckCircle2, Clock,
  AlertCircle, Loader2
} from 'lucide-react';

interface Campaign {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  total_messages: number;
  days_between_messages: number;
  total_leads: number;
  start_date: string | null;
  created_at: string;
}

interface CampaignStats {
  totalLeads: number;
  activeLeads: number;
  completedLeads: number;
  repliedLeads: number;
  messagesSent: number;
  messagesOpened: number;
  messagesClicked: number;
  messagesReplied: number;
  openRate: number;
  replyRate: number;
}

export function CampaignDetail() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [stats, setStats] = useState<CampaignStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const campaignId = window.location.pathname.split('/').pop();

  useEffect(() => {
    if (user && campaignId) {
      loadCampaignData();
    }
  }, [user, campaignId]);

  const loadCampaignData = async () => {
    try {
      setLoading(true);

      // Load campaign details
      const { data: campaignData, error: campaignError } = await supabase
        .from('campaigns')
        .select('*')
        .eq('id', campaignId)
        .eq('user_id', user?.id)
        .single();

      if (campaignError) throw campaignError;
      setCampaign(campaignData);

      // Load campaign statistics
      const statsResponse = await apiClient.request(`/campaigns/${campaignId}/stats`);
      if (statsResponse.success && statsResponse.data) {
        setStats(statsResponse.data);
      }
    } catch (error: any) {
      console.error('Error loading campaign:', error);
      showToast({
        type: 'error',
        title: 'Failed to load campaign',
        message: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLaunchCampaign = async () => {
    if (!campaign) return;

    setActionLoading(true);
    try {
      const response = await apiClient.request(`/campaigns/${campaign.id}/launch`, {
        method: 'POST',
      });

      if (!response.success) throw new Error(response.error || 'Failed to launch campaign');

      if (response.data) {
        setCampaign(response.data);
        await loadCampaignData();
      }

      showToast({
        type: 'success',
        title: 'Campaign Launched!',
        message: 'Your campaign is now active and messages will be sent',
      });
    } catch (error: any) {
      showToast({
        type: 'error',
        title: 'Failed to launch campaign',
        message: error.message,
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handlePauseCampaign = async () => {
    if (!campaign) return;

    setActionLoading(true);
    try {
      const response = await apiClient.request(`/campaigns/${campaign.id}/pause`, {
        method: 'POST',
      });

      if (!response.success) throw new Error(response.error || 'Failed to pause campaign');

      if (response.data) {
        setCampaign(response.data);
      }
      showToast({
        type: 'success',
        title: 'Campaign Paused',
        message: 'Your campaign has been paused',
      });
    } catch (error: any) {
      showToast({
        type: 'error',
        title: 'Failed to pause campaign',
        message: error.message,
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleResumeCampaign = async () => {
    if (!campaign) return;

    setActionLoading(true);
    try {
      const response = await apiClient.request(`/campaigns/${campaign.id}/resume`, {
        method: 'POST',
      });

      if (!response.success) throw new Error(response.error || 'Failed to resume campaign');

      if (response.data) {
        setCampaign(response.data);
        await loadCampaignData();
      }

      showToast({
        type: 'success',
        title: 'Campaign Resumed',
        message: 'Your campaign is now active again',
      });
    } catch (error: any) {
      showToast({
        type: 'error',
        title: 'Failed to resume campaign',
        message: error.message,
      });
    } finally {
      setActionLoading(false);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const getStatusBadge = () => {
    if (!campaign) return null;

    const statusConfig = {
      draft: { bg: 'bg-gray-500/20', text: 'text-gray-400', border: 'border-gray-500/30', icon: Clock },
      active: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/30', icon: Play },
      paused: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/30', icon: Pause },
      completed: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/30', icon: CheckCircle2 },
    };

    const config = statusConfig[campaign.status];
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl border ${config.bg} ${config.text} ${config.border} font-bold`}>
        <Icon className="w-5 h-5" />
        {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#1A1F2E] flex items-center justify-center">
        <div className="relative">
          <div className="w-20 h-20 border-4 border-white/30 rounded-full"></div>
          <div className="absolute inset-0 w-20 h-20 border-4 border-[#FF6B35] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="min-h-screen bg-[#1A1F2E]">
        <Navigation currentPage="campaigns" />
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="glass-card p-12 text-center">
            <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-4">Campaign Not Found</h2>
            <button
              onClick={() => navigate('/campaigns')}
              className="text-[#FF6B35] hover:text-[#F7931E] font-bold"
            >
              ← Back to Campaigns
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
      </div>

      <Navigation currentPage="campaigns" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/campaigns')}
            className="text-[#FF6B35] hover:text-[#F7931E] mb-4 inline-flex items-center gap-2 font-bold transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Campaigns
          </button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-3">{campaign.name}</h1>
              {campaign.description && (
                <p className="text-xl text-gray-400">{campaign.description}</p>
              )}
            </div>
            <div className="flex items-center gap-4">
              {getStatusBadge()}
              {campaign.status === 'draft' && (
                <button
                  onClick={handleLaunchCampaign}
                  disabled={actionLoading}
                  className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-green-600 to-green-500 text-white font-bold rounded-xl shadow-lg hover:shadow-2xl hover:shadow-green-600/40 hover:scale-105 active:scale-95 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {actionLoading ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" />
                      Launching...
                    </>
                  ) : (
                    <>
                      <Play className="w-6 h-6" />
                      Launch Campaign
                    </>
                  )}
                </button>
              )}
              {campaign.status === 'active' && (
                <button
                  onClick={handlePauseCampaign}
                  disabled={actionLoading}
                  className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-yellow-600 to-yellow-500 text-white font-bold rounded-xl shadow-lg hover:shadow-2xl hover:shadow-yellow-600/40 hover:scale-105 active:scale-95 transition-all duration-300"
                >
                  {actionLoading ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" />
                      Pausing...
                    </>
                  ) : (
                    <>
                      <Pause className="w-6 h-6" />
                      Pause Campaign
                    </>
                  )}
                </button>
              )}
              {campaign.status === 'paused' && (
                <button
                  onClick={handleResumeCampaign}
                  disabled={actionLoading}
                  className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-green-600 to-green-500 text-white font-bold rounded-xl shadow-lg hover:shadow-2xl hover:shadow-green-600/40 hover:scale-105 active:scale-95 transition-all duration-300"
                >
                  {actionLoading ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" />
                      Resuming...
                    </>
                  ) : (
                    <>
                      <Play className="w-6 h-6" />
                      Resume Campaign
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Campaign Configuration */}
        <div className="glass-card p-8 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-white/5 rounded-2xl hover:bg-white/10 transition-colors">
              <MessageSquare className="w-10 h-10 text-[#FF6B35] mx-auto mb-3" />
              <p className="text-3xl font-black text-white mb-2">{campaign.total_messages}</p>
              <p className="text-sm text-gray-400 font-bold">Messages per Lead</p>
            </div>
            <div className="text-center p-6 bg-white/5 rounded-2xl hover:bg-white/10 transition-colors">
              <Calendar className="w-10 h-10 text-[#FF6B35] mx-auto mb-3" />
              <p className="text-3xl font-black text-white mb-2">{campaign.days_between_messages}d</p>
              <p className="text-sm text-gray-400 font-bold">Days Between Messages</p>
            </div>
            <div className="text-center p-6 bg-white/5 rounded-2xl hover:bg-white/10 transition-colors">
              <Users className="w-10 h-10 text-[#FF6B35] mx-auto mb-3" />
              <p className="text-3xl font-black text-white mb-2">{campaign.total_leads}</p>
              <p className="text-sm text-gray-400 font-bold">Total Leads</p>
            </div>
          </div>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="glass-card p-8">
            <h2 className="text-2xl font-bold text-white mb-6">Performance</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
              <div className="text-center p-6 bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-2xl border border-blue-500/30">
                <Mail className="w-8 h-8 text-blue-400 mx-auto mb-3" />
                <p className="text-4xl font-black text-white mb-2">{stats.messagesSent}</p>
                <p className="text-sm text-blue-300 font-bold">Messages Sent</p>
              </div>
              <div className="text-center p-6 bg-gradient-to-br from-green-500/20 to-green-600/20 rounded-2xl border border-green-500/30">
                <TrendingUp className="w-8 h-8 text-green-400 mx-auto mb-3" />
                <p className="text-4xl font-black text-white mb-2">{stats.openRate}%</p>
                <p className="text-sm text-green-300 font-bold">Open Rate</p>
              </div>
              <div className="text-center p-6 bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-2xl border border-purple-500/30">
                <MousePointerClick className="w-8 h-8 text-purple-400 mx-auto mb-3" />
                <p className="text-4xl font-black text-white mb-2">{stats.messagesClicked}</p>
                <p className="text-sm text-purple-300 font-bold">Clicks</p>
              </div>
              <div className="text-center p-6 bg-gradient-to-br from-[#FF6B35]/20 to-[#F7931E]/20 rounded-2xl border border-[#FF6B35]/30">
                <MessageSquare className="w-8 h-8 text-[#FF6B35] mx-auto mb-3" />
                <p className="text-4xl font-black text-white mb-2">{stats.repliedLeads}</p>
                <p className="text-sm text-[#FF6B35] font-bold">Replies</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-6 bg-white/5 rounded-2xl">
                <p className="text-sm text-gray-400 font-bold mb-2">Active Leads</p>
                <p className="text-2xl font-black text-white">{stats.activeLeads} / {stats.totalLeads}</p>
              </div>
              <div className="p-6 bg-white/5 rounded-2xl">
                <p className="text-sm text-gray-400 font-bold mb-2">Completed</p>
                <p className="text-2xl font-black text-white">{stats.completedLeads}</p>
              </div>
              <div className="p-6 bg-white/5 rounded-2xl">
                <p className="text-sm text-gray-400 font-bold mb-2">Reply Rate</p>
                <p className="text-2xl font-black text-white">{stats.replyRate}%</p>
              </div>
            </div>
          </div>
        )}

        {campaign.status === 'draft' && (
          <div className="mt-8 glass-card p-6 bg-yellow-500/10 border-2 border-yellow-500/30">
            <div className="flex items-start gap-4">
              <AlertCircle className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-lg font-bold text-white mb-2">Campaign Not Launched</h3>
                <p className="text-gray-300 mb-4">
                  This campaign is in draft mode. Click "Launch Campaign" to activate it and start sending messages to your leads.
                </p>
                <p className="text-sm text-gray-400">
                  Note: Messages will be sent gradually over time based on your configured schedule ({campaign.days_between_messages} days between messages).
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
