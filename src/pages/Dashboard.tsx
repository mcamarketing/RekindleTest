import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import { Navigation } from '../components/Navigation';
import { RippleButton } from '../components/RippleButton';
import { StatCard } from '../components/StatCard';
import { ActivityFeed } from '../components/ActivityFeed';
import { Users, TrendingUp, Mail, Plus, LayoutDashboard, ArrowUp, ArrowDown, DollarSign, Target } from 'lucide-react';

interface DashboardStats {
  totalLeads: number;
  activeCampaigns: number;
  responseRate: number;
  meetingsBooked: number;
  totalACV: number;
  potentialRevenue: number;
  hotLeads: number;
  coldLeads: number;
}

export function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalLeads: 0,
    activeCampaigns: 0,
    responseRate: 0,
    meetingsBooked: 0,
    totalACV: 0,
    potentialRevenue: 0,
    hotLeads: 0,
    coldLeads: 0
  });
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    loadDashboardStats();
    const interval = setInterval(loadDashboardStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardStats = async () => {
    try {
      // Get total leads count
      const { count: leadsCount } = await supabase
        .from('leads')
        .select('*', { count: 'exact', head: true });

      // Get active campaigns count
      const { count: campaignsCount } = await supabase
        .from('campaigns')
        .select('*', { count: 'exact', head: true })
        .eq('status', 'active');

      // Get leads with full data for ACV calculation
      const { data: leadsData } = await supabase
        .from('leads')
        .select('lead_score, status, custom_fields');

      // Calculate ACV and lead breakdown
      const defaultACV = 2500; // Default deal value
      const hotLeadsCount = leadsData?.filter(l => l.lead_score >= 70).length || 0;
      const coldLeadsCount = leadsData?.filter(l => l.lead_score < 40 && l.status !== 'converted').length || 0;
      const totalACV = (leadsData?.length || 0) * defaultACV;
      const potentialRevenue = hotLeadsCount * defaultACV * 0.2; // 20% conversion estimate

      setStats({
        totalLeads: leadsCount || 0,
        activeCampaigns: campaignsCount || 0,
        responseRate: 0,
        meetingsBooked: 0,
        totalACV,
        potentialRevenue,
        hotLeads: hotLeadsCount,
        coldLeads: coldLeadsCount
      });
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  // Format currency for display
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const statCardsData = [
    {
      title: 'Total Pipeline ACV',
      value: formatCurrency(stats.totalACV),
      numericValue: stats.totalACV,
      icon: DollarSign,
      gradient: 'from-emerald-500 to-emerald-600',
      description: `${stats.totalLeads} leads in pipeline`,
      onClick: () => navigate('/leads')
    },
    {
      title: 'Potential Revenue (30d)',
      value: formatCurrency(stats.potentialRevenue),
      numericValue: stats.potentialRevenue,
      icon: TrendingUp,
      gradient: 'from-green-500 to-green-600',
      description: `${stats.hotLeads} hot leads × 20% close rate`,
      trend: 'up' as const,
      trendValue: '12%',
      onClick: () => navigate('/leads?filter=hot')
    },
    {
      title: 'Hot Leads (70+ Score)',
      value: stats.hotLeads.toString(),
      numericValue: stats.hotLeads,
      icon: Target,
      gradient: 'from-orange-500 to-orange-600',
      description: 'Ready for outreach now',
      onClick: () => navigate('/leads?filter=hot')
    },
    {
      title: 'Cold Leads to Revive',
      value: stats.coldLeads.toString(),
      numericValue: stats.coldLeads,
      icon: Mail,
      gradient: 'from-blue-500 to-blue-600',
      description: 'Reactivation opportunities',
      onClick: () => navigate('/leads?filter=cold')
    },
    {
      title: 'Active Campaigns',
      value: stats.activeCampaigns.toString(),
      numericValue: stats.activeCampaigns,
      icon: TrendingUp,
      gradient: 'from-purple-500 to-purple-600',
      description: 'Running campaigns',
      onClick: () => navigate('/campaigns')
    },
    {
      title: 'Meetings Booked',
      value: stats.meetingsBooked.toString(),
      numericValue: stats.meetingsBooked,
      icon: LayoutDashboard,
      gradient: 'from-pink-500 to-pink-600',
      description: 'This month',
      onClick: () => navigate('/billing')
    },
  ];

  // Mock activity data (in a real app, this would come from the database)
  const recentActivities = [];

  const getTimeSinceUpdate = () => {
    const seconds = Math.floor((Date.now() - lastUpdated.getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#F7931E] rounded-full blur-[150px] opacity-15 animate-aurora" style={{ animationDelay: '3s' }} />
        <div className="absolute bottom-0 left-1/3 w-[700px] h-[700px] bg-purple-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '6s' }} />
      </div>

      <Navigation currentPage="dashboard" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <div className="mb-12 animate-fade-in">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}!
              </h1>
              <p className="text-gray-400 text-lg">Here's what's happening with your lead revival campaigns</p>
            </div>
            <div className="flex items-center gap-3 glass-card px-4 py-2 rounded-xl">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-sm text-gray-400">
                Updated {getTimeSinceUpdate()}
              </span>
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
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
              {statCardsData.map((stat, index) => (
                <StatCard
                  key={stat.title}
                  {...stat}
                  delay={index * 100}
                />
              ))}
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-12">
              {/* Activity Feed */}
              <ActivityFeed activities={recentActivities} />

              {/* Quick Actions - Now in a card */}
              <div className="glass-card p-10 animate-fade-in">
                <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
                <div className="space-y-4">
                  <button
                    onClick={() => navigate('/leads/import')}
                    className="w-full flex items-center gap-4 p-6 border-2 border-dashed border-gray-700 rounded-2xl hover:border-[#FF6B35] hover:bg-[#FF6B35]/10 transition-all duration-300 hover:scale-105 group relative overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-gradient-to-br from-[#FF6B35]/0 to-[#FF6B35]/0 group-hover:from-[#FF6B35]/10 group-hover:to-[#F7931E]/10 transition-all duration-500" />
                    <div className="p-4 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                      <Plus className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-bold text-white text-lg group-hover:text-orange-400 transition-colors">Import Leads</div>
                      <div className="text-sm text-gray-400">Upload CSV or connect CRM</div>
                    </div>
                  </button>

                  <button
                    onClick={() => navigate('/campaigns/create')}
                    className="w-full flex items-center gap-4 p-6 border-2 border-dashed border-gray-700 rounded-2xl hover:border-[#FF6B35] hover:bg-[#FF6B35]/10 transition-all duration-300 hover:scale-105 group relative overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-gradient-to-br from-[#FF6B35]/0 to-[#FF6B35]/0 group-hover:from-[#FF6B35]/10 group-hover:to-[#F7931E]/10 transition-all duration-500" />
                    <div className="p-4 bg-gradient-to-br from-green-500 to-green-600 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                      <Mail className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-bold text-white text-lg group-hover:text-orange-400 transition-colors">Create Campaign</div>
                      <div className="text-sm text-gray-400">AI-powered outreach sequence</div>
                    </div>
                  </button>

                  <button
                    onClick={() => navigate('/leads')}
                    className="w-full flex items-center gap-4 p-6 border-2 border-dashed border-gray-700 rounded-2xl hover:border-[#FF6B35] hover:bg-[#FF6B35]/10 transition-all duration-300 hover:scale-105 group relative overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-gradient-to-br from-[#FF6B35]/0 to-[#FF6B35]/0 group-hover:from-[#FF6B35]/10 group-hover:to-[#F7931E]/10 transition-all duration-500" />
                    <div className="p-4 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                      <Users className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-bold text-white text-lg group-hover:text-orange-400 transition-colors">View All Leads</div>
                      <div className="text-sm text-gray-400">Manage your pipeline</div>
                    </div>
                  </button>
                </div>
              </div>
            </div>

            {/* Removed old Quick Actions panel - now integrated above */}


            {stats.totalLeads === 0 && (
              <div className="mt-12 glass-card p-12 animate-fade-in relative overflow-hidden">
                {/* Premium gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#FF6B35]/20 via-[#F7931E]/10 to-purple-600/20 opacity-50" />

                <div className="relative z-10">
                  <h2 className="text-4xl font-bold mb-4 text-white">Get Started with Rekindle</h2>
                  <p className="mb-10 text-gray-300 text-lg">
                    Start reviving your dormant leads in 3 simple steps:
                  </p>
                  <ol className="space-y-6 mb-10">
                    {[
                      'Import your dormant leads (CSV, CRM sync, or manual entry)',
                      'Create your first revival campaign with AI-powered messaging',
                      'Watch your leads come back to life with automated follow-ups'
                    ].map((step, index) => (
                      <li
                        key={index}
                        className="flex items-start gap-4 animate-slide-in-left glass-morphism p-6 rounded-2xl"
                        style={{ animationDelay: `${index * 100}ms` }}
                      >
                        <span className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] text-white rounded-full flex items-center justify-center font-black text-lg shadow-lg">
                          {index + 1}
                        </span>
                        <span className="text-white font-medium text-lg pt-1.5">{step}</span>
                      </li>
                    ))}
                  </ol>
                  <RippleButton
                    onClick={() => navigate('/leads/import')}
                    variant="primary"
                    className="bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white hover:shadow-2xl hover:shadow-[#FF6B35]/50 px-10 py-4 text-lg font-bold"
                  >
                    Import Your First Leads
                  </RippleButton>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
