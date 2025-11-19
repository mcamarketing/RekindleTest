import { useEffect, useState } from 'react';
import { Navigation } from '../components/Navigation';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { Campaign } from '../types/api';
import { Plus, Play, Pause, Trash2, Calendar, Users, MessageSquare } from 'lucide-react';

export function Campaigns() {
  const { user } = useAuth();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadCampaigns();
    }
  }, [user]);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      setError(null);

      const { data, error: fetchError } = await supabase
        .from('campaigns')
        .select('*')
        .eq('user_id', user?.id)
        .order('created_at', { ascending: false });

      if (fetchError) {
        throw fetchError;
      }

      setCampaigns(data || []);
    } catch (err: any) {
      console.error('Error loading campaigns:', err);
      setError(err.message || 'Failed to load campaigns');
    } finally {
      setLoading(false);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const getStatusColor = (status: Campaign['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'paused':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'completed':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'draft':
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getStatusIcon = (status: Campaign['status']) => {
    switch (status) {
      case 'active':
        return <Play className="w-4 h-4" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden animate-fade-in">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
        <div className="absolute bottom-1/4 left-1/3 w-[700px] h-[700px] bg-green-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '7s' }} />
      </div>

      <Navigation currentPage="campaigns" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-5xl font-bold text-white mb-3">Campaigns</h1>
            <p className="text-xl text-gray-400">
              Manage your outreach campaigns
            </p>
          </div>
          <button
            onClick={() => navigate('/campaigns/create')}
            className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold rounded-xl shadow-lg hover:shadow-2xl hover:shadow-[#FF6B35]/40 hover:scale-105 active:scale-95 transition-all duration-300"
          >
            <Plus className="w-6 h-6" />
            Create Campaign
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="glass-card p-6 mb-8 border-2 border-red-500/30 bg-red-500/10">
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-white/30 rounded-full"></div>
              <div className="absolute inset-0 w-20 h-20 border-4 border-[#FF6B35] border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        ) : campaigns.length === 0 ? (
          /* Empty State */
          <div className="glass-card p-20 text-center">
            <div className="inline-flex p-8 bg-gradient-to-br from-[#FF6B35]/20 to-[#F7931E]/20 rounded-3xl mb-6">
              <MessageSquare className="w-20 h-20 text-[#FF6B35]" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">No Campaigns Yet</h2>
            <p className="text-xl text-gray-400 mb-8 max-w-lg mx-auto">
              Create your first campaign to start reaching out to your leads
            </p>
            <button
              onClick={() => navigate('/campaigns/create')}
              className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold rounded-xl shadow-lg hover:shadow-2xl hover:shadow-[#FF6B35]/40 hover:scale-105 active:scale-95 transition-all duration-300"
            >
              <Plus className="w-6 h-6" />
              Create Your First Campaign
            </button>
          </div>
        ) : (
          /* Campaigns Grid */
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {campaigns.map((campaign) => (
              <div
                key={campaign.id}
                className="glass-card p-6 hover:border-[#FF6B35]/50 transition-all cursor-pointer group"
                onClick={() => navigate(`/campaigns/${campaign.id}`)}
              >
                {/* Status Badge */}
                <div className="flex items-center justify-between mb-4">
                  <span
                    className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold border ${getStatusColor(
                      campaign.status
                    )}`}
                  >
                    {getStatusIcon(campaign.status)}
                    {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                  </span>
                </div>

                {/* Campaign Name */}
                <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-[#FF6B35] transition-colors">
                  {campaign.name}
                </h3>

                {/* Stats */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-center gap-3 text-gray-400">
                    <Users className="w-5 h-5" />
                    <span className="text-sm">
                      {campaign.lead_ids?.length || 0} leads
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-gray-400">
                    <Calendar className="w-5 h-5" />
                    <span className="text-sm">
                      Created {new Date(campaign.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Message Template Preview */}
                {campaign.message_template && (
                  <div className="mt-4 p-4 bg-white/5 rounded-lg border border-white/10">
                    <p className="text-sm text-gray-400 line-clamp-2">
                      {campaign.message_template}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
