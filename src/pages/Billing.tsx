// @ts-nocheck
import { useEffect, useState } from 'react';
import { Navigation } from '../components/Navigation';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { DollarSign, TrendingUp, Calendar, CheckCircle, Clock } from 'lucide-react';

interface BillingData {
  totalMeetings: number;
  totalRevenue: number;
  averageACV: number;
  thisMonthMeetings: number;
  thisMonthRevenue: number;
  pendingCharges: number;
  platformFee: number;
  performanceFees: number;
  totalMonthlyBill: number;
}

export function Billing() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [billingData, setBillingData] = useState<BillingData>({
    totalMeetings: 0,
    totalRevenue: 0,
    averageACV: 2500,
    thisMonthMeetings: 0,
    thisMonthRevenue: 0,
    pendingCharges: 0,
    platformFee: 99, // Pro plan platform fee
    performanceFees: 0,
    totalMonthlyBill: 99
  });

  useEffect(() => {
    loadBillingData();
    const interval = setInterval(loadBillingData, 30000); // Real-time updates every 30s
    return () => clearInterval(interval);
  }, []);

  const loadBillingData = async () => {
    try {
      setLoading(true);

      // Get all converted leads (meetings booked)
      const { data: convertedLeads } = await supabase
        .from('leads')
        .select('id, created_at, custom_fields')
        .eq('status', 'meeting_booked');

      const totalMeetings = convertedLeads?.length || 0;
      const averageACV = 2500; // Default ACV
      const performanceFeeRate = 0.025; // 2.5%
      const totalRevenue = totalMeetings * averageACV * performanceFeeRate;

      // Calculate this month's data
      const now = new Date();
      const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
      const thisMonthMeetings = convertedLeads?.filter(l => 
        new Date(l.created_at) >= monthStart
      ).length || 0;
      const thisMonthRevenue = thisMonthMeetings * averageACV * performanceFeeRate;

      // Two-Part Pricing Model
      const platformFee = 99; // Pro plan base fee
      const performanceFees = thisMonthRevenue;
      const totalMonthlyBill = platformFee + performanceFees;

      setBillingData({
        totalMeetings,
        totalRevenue,
        averageACV,
        thisMonthMeetings,
        thisMonthRevenue,
        pendingCharges: 0,
        platformFee,
        performanceFees,
        totalMonthlyBill
      });
    } catch (error) {
      console.error('Error loading billing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 2
    }).format(value);
  };

  const statCards = [
    {
      title: 'Platform Access Fee',
      value: formatCurrency(billingData.platformFee),
      icon: CheckCircle,
      gradient: 'from-blue-500 to-blue-600',
      description: 'Fixed monthly infrastructure cost',
      badge: 'Non-refundable'
    },
    {
      title: 'This Month Performance Fees',
      value: formatCurrency(billingData.performanceFees),
      icon: TrendingUp,
      gradient: 'from-orange-500 to-orange-600',
      description: `${billingData.thisMonthMeetings} meetings × 2.5% ACV`,
      badge: 'Results-based'
    },
    {
      title: 'Total Monthly Bill',
      value: formatCurrency(billingData.totalMonthlyBill),
      icon: DollarSign,
      gradient: 'from-green-500 to-green-600',
      description: 'Platform + Performance',
      badge: 'Due this month'
    },
    {
      title: 'Performance Fee %',
      value: `${Math.round((billingData.performanceFees / billingData.totalMonthlyBill) * 100)}%`,
      icon: Calendar,
      gradient: 'from-purple-500 to-purple-600',
      description: 'Of your total spend',
      badge: 'Results-tied'
    },
  ];

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-green-500 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-blue-500 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '3s' }} />
      </div>

      <Navigation currentPage="billing" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">
            Billing & Performance
          </h1>
          <p className="text-gray-400 text-lg">
            Real-time billing transparency. You only pay for booked meetings.
          </p>
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
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
              {statCards.map((stat, index) => (
                <div
                  key={stat.title}
                  className="glass-card glass-card-hover p-8 h-full animate-fade-in group relative overflow-hidden"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
                  
                  <div className="relative z-10">
                    {'badge' in stat && (
                      <div className="absolute -top-2 -right-2">
                        <span className="px-3 py-1 text-xs font-bold bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-full shadow-lg">
                          {stat.badge}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex-1">
                        <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">
                          {stat.title}
                        </p>
                        <p className="text-4xl font-black text-white mb-2">
                          {stat.value}
                        </p>
                        <p className="text-sm text-gray-400 font-medium">
                          {stat.description}
                        </p>
                      </div>
                      <div className={`p-5 bg-gradient-to-br ${stat.gradient} rounded-2xl transition-all duration-500 group-hover:scale-110 shadow-lg`}>
                        <stat.icon className="w-10 h-10 text-white" />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* TWO-PART PRICING BREAKDOWN */}
            <div className="glass-card p-10 mb-8">
              <h2 className="text-3xl font-bold text-white mb-8">Two-Part Pricing Model</h2>
              <div className="grid md:grid-cols-3 gap-8">
                <div className="bg-blue-500/10 p-6 rounded-xl border-2 border-blue-500/30">
                  <div className="text-blue-400 font-bold text-sm uppercase tracking-wider mb-3">
                    Platform Access Fee
                  </div>
                  <div className="text-4xl font-black text-white mb-2">{formatCurrency(billingData.platformFee)}</div>
                  <div className="text-gray-400 text-sm">Fixed monthly • Non-refundable</div>
                  <div className="mt-4 text-xs text-gray-500">
                    Covers: Infrastructure, security, support
                  </div>
                </div>

                <div className="bg-orange-500/10 p-6 rounded-xl border-2 border-orange-500/30">
                  <div className="text-orange-400 font-bold text-sm uppercase tracking-wider mb-3">
                    Performance Fee
                  </div>
                  <div className="text-4xl font-black text-white mb-2">2.5%</div>
                  <div className="text-gray-400 text-sm">of ACV × per meeting • Refundable</div>
                  <div className="mt-4 text-xs text-gray-500">
                    100% refund if booked meeting no-shows
                  </div>
                </div>

                <div className="bg-green-500/10 p-6 rounded-xl border-2 border-green-500/30">
                  <div className="text-green-400 font-bold text-sm uppercase tracking-wider mb-3">
                    Average Cost/Meeting
                  </div>
                  <div className="text-4xl font-black text-white mb-2">{formatCurrency(billingData.averageACV * 0.025)}</div>
                  <div className="text-gray-400 text-sm">Based on {formatCurrency(billingData.averageACV)} ACV</div>
                  <div className="mt-4 text-xs text-gray-500">
                    80%+ of total spend is results-based
                  </div>
                </div>
              </div>
            </div>

            {/* Transparency Notice - TWO-PART MODEL */}
            <div className="glass-card p-8 border-2 border-green-500/30 bg-green-500/5">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-green-500/20 rounded-xl">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">
                    100% Transparent Two-Part Pricing
                  </h3>
                  <p className="text-gray-300 leading-relaxed mb-4">
                    <span className="text-white font-bold">Platform Access Fee ({formatCurrency(billingData.platformFee)}/month):</span> Covers enterprise infrastructure (99.9% uptime), SOC 2 security, dedicated support, and real-time CRM sync. This fee is non-refundable as it pays for real costs.
                  </p>
                  <p className="text-gray-300 leading-relaxed">
                    <span className="text-orange-400 font-bold">Performance Fee (2.5% ACV):</span> Only charged when meetings book. <span className="text-green-400 font-bold">100% refundable if they no-show.</span> This is where 80%+ of your spend goes—directly tied to results. No hidden fees, no surprises.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
