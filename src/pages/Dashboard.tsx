import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { supabase } from "../lib/supabase";
import { Navigation } from "../components/Navigation";
import {
  Users,
  TrendingUp,
  Mail,
  Plus,
  ArrowUp,
  Activity,
} from "lucide-react";
import { motion } from "framer-motion";
import { Chart } from "../components/Chart";

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
    coldLeads: 0,
  });
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    loadDashboardStats();
    const interval = setInterval(loadDashboardStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const chartData = [
    { name: "Jan", value: 400 },
    { name: "Feb", value: 300 },
    { name: "Mar", value: 600 },
    { name: "Apr", value: 800 },
    { name: "May", value: 500 },
    { name: "Jun", value: 700 },
    { name: "Jul", value: 900 },
  ];

  const loadDashboardStats = async () => {
    try {
      // Get total leads count
      const { count: leadsCount } = await supabase
        .from("leads")
        .select("*", { count: "exact", head: true });

      // Get active campaigns count
      const { count: campaignsCount } = await supabase
        .from("campaigns")
        .select("*", { count: "exact", head: true })
        .eq("status", "active");

      // Get leads with full data for ACV calculation
      const { data: leadsData } = await supabase
        .from("leads")
        .select("lead_score, status, custom_fields");

      // Calculate ACV and lead breakdown
      const defaultACV = 2500; // Default deal value
      const hotLeadsCount =
        leadsData?.filter((l) => l.lead_score >= 70).length || 0;
      const coldLeadsCount =
        leadsData?.filter((l) => l.lead_score < 40 && l.status !== "converted")
          .length || 0;
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
        coldLeads: coldLeadsCount,
      });
      setLastUpdated(new Date());
    } catch (error) {
      console.error("Error loading dashboard stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, "", path);
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const getTimeSinceUpdate = () => {
    const seconds = Math.floor((Date.now() - lastUpdated.getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  return (
    <div className="min-h-screen bg-[#f6f9fc]">
      <Navigation currentPage="dashboard" />

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Header Section - Stripe-inspired minimal */}
        <motion.div
          className="mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-3xl font-bold text-[#0a2540] tracking-tight">
              Dashboard
            </h1>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#e3e8ee] rounded-md">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-xs text-[#425466] font-medium">
                Live · Updated {getTimeSinceUpdate()}
              </span>
            </div>
          </div>
          <p className="text-[#425466] text-base">
            Welcome back
            {user?.email ? `, ${user.email.split("@")[0]}` : ""}. Here's your
            pipeline overview.
          </p>
        </motion.div>

        {loading ? (
          <div className="flex justify-center py-16">
            <div className="relative">
              <div className="w-12 h-12 border-2 border-[#e3e8ee] rounded-full"></div>
              <div className="absolute inset-0 w-12 h-12 border-2 border-[#0a2540] border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        ) : (
          <>
            {/* Key Metrics - Stripe-style minimal cards */}
            <motion.div
              className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {/* Leads Contacted */}
              <div className="bg-white border border-[#e3e8ee] rounded-lg p-6 hover:shadow-md transition-shadow duration-200">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs uppercase tracking-wider text-[#727f96] font-medium">
                    Leads Contacted
                  </span>
                  <Users className="w-4 h-4 text-[#727f96]" />
                </div>
                <div className="text-3xl font-bold text-[#0a2540] mb-1 tabular-nums">
                  {stats.totalLeads}
                </div>
                <div className="text-sm text-[#425466]">
                  Total pipeline leads
                </div>
              </div>

              {/* Meetings Booked */}
              <div className="bg-white border border-[#e3e8ee] rounded-lg p-6 hover:shadow-md transition-shadow duration-200">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs uppercase tracking-wider text-[#727f96] font-medium">
                    Meetings Booked
                  </span>
                  <Activity className="w-4 h-4 text-[#727f96]" />
                </div>
                <div className="text-3xl font-bold text-[#0a2540] mb-1 tabular-nums">
                  {stats.meetingsBooked}
                </div>
                <div className="text-sm text-[#425466]">This month</div>
              </div>

              {/* Reply Rate */}
              <div className="bg-white border border-[#e3e8ee] rounded-lg p-6 hover:shadow-md transition-shadow duration-200">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs uppercase tracking-wider text-[#727f96] font-medium">
                    Reply Rate
                  </span>
                  <TrendingUp className="w-4 h-4 text-[#727f96]" />
                </div>
                <div className="text-3xl font-bold text-[#0a2540] mb-1 tabular-nums">
                  {stats.responseRate}%
                </div>
                <div className="text-sm text-[#10b981] flex items-center gap-1">
                  <ArrowUp className="w-3 h-3" />
                  <span>vs industry avg</span>
                </div>
              </div>
            </motion.div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
              <Chart data={chartData} title="Leads Generated" />
              <Chart data={chartData} title="Conversion Rate" />
            </div>

            {/* Active Campaigns Section */}
            <motion.div
              className="mb-12"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-[#0a2540]">
                  Active Campaigns
                </h2>
                <button
                  onClick={() => navigate("/campaigns")}
                  className="text-sm text-[#425466] hover:text-[#0a2540] font-medium transition-colors"
                >
                  View all →
                </button>
              </div>

              {stats.activeCampaigns === 0 ? (
                <div className="bg-white border border-[#e3e8ee] rounded-lg p-8 text-center">
                  <Mail className="w-12 h-12 text-[#e3e8ee] mx-auto mb-4" />
                  <p className="text-[#425466] mb-4">
                    No active campaigns yet
                  </p>
                  <button
                    onClick={() => navigate("/campaigns/create")}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-[#0a2540] text-white rounded-md hover:bg-[#0d2d52] transition-colors text-sm font-medium"
                  >
                    <Plus className="w-4 h-4" />
                    Create campaign
                  </button>
                </div>
              ) : (
                <div className="bg-white border border-[#e3e8ee] rounded-lg p-6">
                  <div className="flex items-center justify-between pb-4 border-b border-[#e3e8ee]">
                    <div className="flex items-center gap-3">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      <div>
                        <div className="font-medium text-[#0a2540]">
                          Q4 Re-engagement
                        </div>
                        <div className="text-sm text-[#727f96]">
                          Multi-channel sequence
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => navigate("/campaigns")}
                      className="text-sm text-[#425466] hover:text-[#0a2540] font-medium transition-colors"
                    >
                      View details →
                    </button>
                  </div>
                  <div className="grid grid-cols-3 gap-6 pt-4">
                    <div>
                      <div className="text-xs uppercase tracking-wider text-[#727f96] mb-1">
                        Leads
                      </div>
                      <div className="text-lg font-bold text-[#0a2540] tabular-nums">
                        {stats.totalLeads}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs uppercase tracking-wider text-[#727f96] mb-1">
                        Meetings
                      </div>
                      <div className="text-lg font-bold text-[#0a2540] tabular-nums">
                        {stats.meetingsBooked}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs uppercase tracking-wider text-[#727f96] mb-1">
                        Rate
                      </div>
                      <div className="text-lg font-bold text-[#0a2540] tabular-nums">
                        {stats.responseRate}%
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              className="grid md:grid-cols-3 gap-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <button
                onClick={() => navigate("/leads/import")}
                className="bg-white border border-[#e3e8ee] rounded-lg p-6 text-left hover:shadow-md transition-shadow duration-200 group"
              >
                <Plus className="w-5 h-5 text-[#727f96] mb-3 group-hover:text-[#0a2540] transition-colors" />
                <div className="font-medium text-[#0a2540] mb-1">
                  Import leads
                </div>
                <div className="text-sm text-[#727f96]">
                  Upload CSV or connect CRM
                </div>
              </button>

              <button
                onClick={() => navigate("/campaigns/create")}
                className="bg-white border border-[#e3e8ee] rounded-lg p-6 text-left hover:shadow-md transition-shadow duration-200 group"
              >
                <Mail className="w-5 h-5 text-[#727f96] mb-3 group-hover:text-[#0a2540] transition-colors" />
                <div className="font-medium text-[#0a2540] mb-1">
                  Create campaign
                </div>
                <div className="text-sm text-[#727f96]">
                  AI-powered sequences
                </div>
              </button>

              <button
                onClick={() => navigate("/analytics")}
                className="bg-white border border-[#e3e8ee] rounded-lg p-6 text-left hover:shadow-md transition-shadow duration-200 group"
              >
                <TrendingUp className="w-5 h-5 text-[#727f96] mb-3 group-hover:text-[#0a2540] transition-colors" />
                <div className="font-medium text-[#0a2540] mb-1">
                  View analytics
                </div>
                <div className="text-sm text-[#727f96]">
                  Performance insights
                </div>
              </button>
            </motion.div>

            {/* Getting Started - Only show when no leads */}
            {stats.totalLeads === 0 && (
              <motion.div
                className="mt-12 bg-white border border-[#e3e8ee] rounded-lg p-12"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <h2 className="text-2xl font-bold text-[#0a2540] mb-3">
                  Get started with RekindlePro
                </h2>
                <p className="text-[#425466] mb-8 text-base">
                  Recover dormant pipeline in three simple steps
                </p>
                <div className="space-y-4 mb-8">
                  {[
                    {
                      num: 1,
                      text: "Import your dormant leads from CSV or CRM",
                    },
                    {
                      num: 2,
                      text: "Create AI-powered re-engagement campaign",
                    },
                    {
                      num: 3,
                      text: "Review and approve messages before sending",
                    },
                  ].map((step) => (
                    <div key={step.num} className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-[#e3e8ee] flex items-center justify-center text-sm font-bold text-[#727f96]">
                        {step.num}
                      </div>
                      <p className="text-[#425466] pt-0.5">{step.text}</p>
                    </div>
                  ))}
                </div>
                <button
                  onClick={() => navigate("/leads/import")}
                  className="px-4 py-2 bg-[#0a2540] text-white rounded-md hover:bg-[#0d2d52] transition-colors text-sm font-medium"
                >
                  Import leads
                </button>
              </motion.div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
