// @ts-nocheck
import { useEffect, useState } from 'react';
import { Navigation } from '../components/Navigation';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { Campaign } from '../types/api';
import { Plus, Play, Pause, Trash2, Calendar, Users, MessageSquare, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

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
        return 'bg-green-50 text-green-700 border-green-200';
      case 'paused':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      case 'completed':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'draft':
        return 'bg-gray-50 text-gray-600 border-gray-200';
      default:
        return 'bg-gray-50 text-gray-600 border-gray-200';
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
    <div className="min-h-screen bg-[#f6f9fc]">
      <Navigation currentPage="campaigns" />

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Header - Stripe-style minimal */}
        <motion.div
          className="flex items-center justify-between mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div>
            <h1 className="text-3xl font-bold text-[#0a2540] tracking-tight mb-2">Campaigns</h1>
            <p className="text-base text-[#425466]">
              Manage your outreach campaigns
            </p>
          </div>
          <button
            onClick={() => navigate('/campaigns/create')}
            className="inline-flex items-center gap-2 px-4 py-2 bg-[#0a2540] text-white font-medium text-sm rounded-md hover:bg-[#0d2d52] transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create campaign
          </button>
        </motion.div>

        {/* Error Message */}
        {error && (
          <motion.div
            className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <p className="text-sm text-red-700">{error}</p>
          </motion.div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="relative">
              <div className="w-12 h-12 border-2 border-[#e3e8ee] rounded-full"></div>
              <div className="absolute inset-0 w-12 h-12 border-2 border-[#0a2540] border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        ) : campaigns.length === 0 ? (
          /* Empty State - Stripe-style minimal */
          <motion.div
            className="bg-white border border-[#e3e8ee] rounded-lg p-16 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <MessageSquare className="w-12 h-12 text-[#e3e8ee] mx-auto mb-4" />
            <h2 className="text-xl font-bold text-[#0a2540] mb-2">No campaigns yet</h2>
            <p className="text-base text-[#425466] mb-6 max-w-md mx-auto">
              Create your first campaign to start reaching out to your leads
            </p>
            <button
              onClick={() => navigate('/campaigns/create')}
              className="inline-flex items-center gap-2 px-4 py-2 bg-[#0a2540] text-white font-medium text-sm rounded-md hover:bg-[#0d2d52] transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create campaign
            </button>
          </motion.div>
        ) : (
          /* Campaigns Grid - Stripe-style cards */
          <motion.div
            className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {campaigns.map((campaign, index) => (
              <motion.div
                key={campaign.id}
                className="bg-white border border-[#e3e8ee] rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer group"
                onClick={() => navigate(`/campaigns/${campaign.id}`)}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                {/* Header: Status and Arrow */}
                <div className="flex items-center justify-between mb-4">
                  <span
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border ${getStatusColor(
                      campaign.status
                    )}`}
                  >
                    {getStatusIcon(campaign.status)}
                    {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                  </span>
                  <ArrowRight className="w-4 h-4 text-[#727f96] group-hover:text-[#0a2540] group-hover:translate-x-1 transition-all" />
                </div>

                {/* Campaign Name */}
                <h3 className="text-lg font-bold text-[#0a2540] mb-3 group-hover:text-[#0a2540]">
                  {campaign.name}
                </h3>

                {/* Stats - Compact */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-[#727f96]">
                    <Users className="w-4 h-4" />
                    <span className="text-sm">
                      {campaign.lead_ids?.length || 0} leads
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-[#727f96]">
                    <Calendar className="w-4 h-4" />
                    <span className="text-sm">
                      {new Date(campaign.created_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </span>
                  </div>
                </div>

                {/* Message Template Preview */}
                {campaign.message_template && (
                  <div className="mt-4 p-3 bg-[#f6f9fc] rounded-md border border-[#e3e8ee]">
                    <p className="text-xs text-[#727f96] line-clamp-2">
                      {campaign.message_template}
                    </p>
                  </div>
                )}
              </motion.div>
            ))}
          </motion.div>
        )}
      </main>
    </div>
  );
}
