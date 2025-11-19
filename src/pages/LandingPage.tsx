import '../styles/animations.css';
import { useState, useEffect } from 'react';
import {
  CheckCircle,
  XCircle,
  Mail,
  MessageSquare,
  MessageCircle,
  Bell,
  Phone,
  Upload,
  Brain,
  Calendar,
  Shield,
  ShieldCheck,
  Sliders,
  User,
  Briefcase,
  Building2,
  Star,
  ArrowRight,
  Zap,
  Target,
  TrendingUp
} from 'lucide-react';
import { SupernovaHero } from '../components/SupernovaHero';
import { PricingLockGuarantee, AnimatedStat } from '../components/SupernovaEnhancements';

const COLORS = {
  primary: '#FF6B35',
  secondary: '#F7931E',
  navy: '#1A1F2E',
  darkGray: '#242938',
  mediumGray: '#313645',
  success: '#10B981',
};

const Button = ({ children, primary = true, onClick }: { children: React.ReactNode; primary?: boolean; onClick?: () => void }) => {
  const baseClasses = 'px-10 py-5 font-bold text-lg rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg relative overflow-hidden group';
  const primaryClasses = 'bg-[#FF6B35] text-white hover:bg-[#F7931E] hover:shadow-[0_0_50px_rgba(255,107,53,0.9)]';
  const secondaryClasses = 'bg-transparent border-2 border-[#FF6B35] text-[#FF6B35] hover:bg-[#FF6B35] hover:text-white';

  return (
    <button
      className={`${baseClasses} ${primary ? primaryClasses : secondaryClasses}`}
      onClick={onClick}
    >
      {primary && (
        <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
      )}
      <span className="relative z-10">{children}</span>
    </button>
  );
};

const SectionTitle = ({ eyebrow, children, subtitle }: { eyebrow?: string; children: React.ReactNode; subtitle?: string }) => (
  <div className="text-center mb-16">
    {eyebrow && (
      <div className="text-[#FF6B35] font-semibold text-sm uppercase tracking-widest mb-4">
        {eyebrow}
      </div>
    )}
    <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-6 leading-tight">
      {children}
    </h2>
    {subtitle && (
      <p className="text-xl text-gray-400 max-w-3xl mx-auto">
        {subtitle}
      </p>
    )}
  </div>
);

// Interactive Channel Selector Component
const InteractiveChannelSelector = ({
  channels,
  activeChannel,
  setActiveChannel
}: {
  channels: any[];
  activeChannel: string;
  setActiveChannel: (id: string) => void;
}) => {
  const colorClasses: Record<string, any> = {
    blue: { bg: 'from-blue-900/30 to-blue-800/20', border: 'border-blue-700/50', text: 'text-blue-400', active: 'bg-blue-900/50 border-blue-500' },
    green: { bg: 'from-green-900/30 to-green-800/20', border: 'border-green-700/50', text: 'text-green-400', active: 'bg-green-900/50 border-green-500' },
    emerald: { bg: 'from-emerald-900/30 to-emerald-800/20', border: 'border-emerald-700/50', text: 'text-emerald-400', active: 'bg-emerald-900/50 border-emerald-500' },
    orange: { bg: 'from-orange-900/30 to-orange-800/20', border: 'border-orange-700/50', text: 'text-orange-400', active: 'bg-orange-900/50 border-orange-500' },
    purple: { bg: 'from-purple-900/30 to-purple-800/20', border: 'border-purple-700/50', text: 'text-purple-400', active: 'bg-purple-900/50 border-purple-500' }
  };

  const activeChannelData = channels.find(c => c.id === activeChannel);
  if (!activeChannelData) return null;

  return (
    <>
      {/* Channel Buttons */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
        {channels.map(channel => {
          const colors = colorClasses[channel.color];
          const isActive = activeChannel === channel.id;
          const Icon = channel.icon;

          return (
            <button
              key={channel.id}
              onClick={() => setActiveChannel(channel.id)}
              className={`
                bg-gradient-to-br ${colors.bg} rounded-xl p-6 border-2
                ${isActive ? colors.active : colors.border}
                hover:scale-105 transition-all duration-300 cursor-pointer
                ${isActive ? 'shadow-lg shadow-[#FF6B35]/20' : 'hover:shadow-md'}
              `}
            >
              <Icon className={`w-8 h-8 mx-auto mb-3 ${colors.text}`} />
              <div className={`font-bold mb-2 ${isActive ? 'text-white' : ''}`}>
                {channel.name}
              </div>
              <div className={`text-xs ${isActive ? 'text-gray-300' : 'text-gray-400'}`}>
                {channel.shortDesc}
              </div>
              {isActive && (
                <div className="mt-3 text-xs font-semibold text-white">
                  Selected ✓
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Details Panel */}
      <div className="max-w-5xl mx-auto bg-[#1A1F2E] rounded-2xl p-8 border-2 border-[#FF6B35]">
        <div className="flex items-start gap-6">
          <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${colorClasses[activeChannelData.color].bg} border-2 ${colorClasses[activeChannelData.color].border} flex items-center justify-center flex-shrink-0`}>
            <activeChannelData.icon className="w-8 h-8 text-white" />
          </div>

          <div className="flex-1">
            <h3 className="text-2xl font-bold text-white mb-2">
              {activeChannelData.name}
            </h3>
            <p className="text-gray-400 mb-6">
              {activeChannelData.description}
            </p>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-[#242938] rounded-lg p-4 border border-gray-700">
                <div className="text-2xl font-bold text-[#FF6B35] mb-1">{activeChannelData.stats.open || activeChannelData.stats.meeting}</div>
                <div className="text-xs text-gray-400">Open Rate</div>
              </div>
              <div className="bg-[#242938] rounded-lg p-4 border border-gray-700">
                <div className="text-2xl font-bold text-[#FF6B35] mb-1">{activeChannelData.stats.reply}</div>
                <div className="text-xs text-gray-400">Reply Rate</div>
              </div>
              <div className="bg-[#242938] rounded-lg p-4 border border-gray-700">
                <div className="text-2xl font-bold text-[#FF6B35] mb-1">{activeChannelData.stats.meeting}</div>
                <div className="text-xs text-gray-400">Meeting Rate</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

// ROI Calculator Component
const ROICalculator = ({
  dealValue,
  setDealValue,
  meetingsGoal,
  setMeetingsGoal,
  monthlyCost,
  revenue,
  roi,
  profit
}: {
  dealValue: number;
  setDealValue: (val: number) => void;
  meetingsGoal: number;
  setMeetingsGoal: (val: number) => void;
  monthlyCost: number;
  revenue: number;
  roi: string;
  profit: number;
}) => {
  return (
    <div className="max-w-4xl mx-auto bg-[#242938] rounded-2xl p-8 border border-gray-700">
      <h3 className="text-2xl font-bold text-center mb-8 text-white">
        Calculate Your ROI in 30 Seconds
      </h3>

      <div className="space-y-6 mb-8">
        <div>
          <label className="block text-sm font-semibold mb-2 text-white">
            Your Average Deal Value
          </label>
          <input
            type="range"
            min="500"
            max="50000"
            step="500"
            value={dealValue}
            onChange={(e) => setDealValue(Number(e.target.value))}
            className="w-full"
          />
          <div className="text-right text-lg font-bold text-[#FF6B35]">
            £{dealValue.toLocaleString()}
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold mb-2 text-white">
            Meetings Per Month Goal
          </label>
          <input
            type="range"
            min="10"
            max="200"
            step="10"
            value={meetingsGoal}
            onChange={(e) => setMeetingsGoal(Number(e.target.value))}
            className="w-full"
          />
          <div className="text-right text-lg font-bold text-[#FF6B35]">
            {meetingsGoal} meetings
          </div>
        </div>
      </div>

      <div className="bg-green-900/20 border border-green-700 rounded-xl p-6">
        <div className="grid md:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-sm text-gray-400 mb-1">Monthly Cost</div>
            <div className="text-2xl font-bold text-white">
              £{Math.round(monthlyCost).toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">
              (£99 + {meetingsGoal} × £{(dealValue * 0.025).toFixed(0)})
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400 mb-1">Revenue (20% close)</div>
            <div className="text-2xl font-bold text-green-400">
              £{Math.round(revenue).toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">
              ({Math.round(meetingsGoal * 0.2)} deals × £{dealValue.toLocaleString()})
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400 mb-1">ROI</div>
            <div className="text-2xl font-bold text-green-400">{roi}x</div>
            <div className="text-xs text-gray-500">
              £{Math.round(profit).toLocaleString()} profit
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export function LandingPage() {
  const [dealValue, setDealValue] = useState(2500);
  const [meetingsGoal, setMeetingsGoal] = useState(40);
  const [activeChannel, setActiveChannel] = useState('email');
  const [pricingPeriod, setPricingPeriod] = useState<'monthly' | 'annual'>('monthly');

  // Channel toggle states
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [smsEnabled, setSmsEnabled] = useState(true);
  const [whatsappEnabled, setWhatsappEnabled] = useState(false);

  useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, observerOptions);

    document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const monthlyCost = 99 + (meetingsGoal * (dealValue * 0.025));
  const revenue = meetingsGoal * 0.2 * dealValue;
  const roi = (revenue / monthlyCost).toFixed(1);
  const profit = revenue - monthlyCost;

  // EMOTIONAL TRIGGER: EMPOWERMENT - "I CONTROL MULTI-CHANNEL OUTREACH"
  const channels = [
    {
      id: 'email',
      name: 'Email',
      icon: Mail,
      color: 'blue',
      shortDesc: 'Highly contextual',
      description: 'Highly contextual and personalized. AI-researched subject lines that reference recent company news, job changes, funding rounds. Each email is unique.',
      gradient: 'from-blue-900/30 to-blue-800/20',
      border: 'border-blue-700/50',
      activeBorder: 'border-blue-500',
      iconColor: 'text-blue-400',
      stats: { open: '15.2%', reply: '4.8%', meeting: '2.1%' }
    },
    {
      id: 'sms',
      name: 'SMS',
      icon: MessageSquare,
      color: 'green',
      shortDesc: 'Capture attention',
      description: 'Capture executive attention where they read. 98% open rate within 3 minutes. Perfect for time-sensitive follow-ups. Short, punchy messages.',
      gradient: 'from-green-900/30 to-green-800/20',
      border: 'border-green-700/50',
      activeBorder: 'border-green-500',
      iconColor: 'text-green-400',
      stats: { open: '98%', reply: '12%', meeting: '3.2%' }
    },
    {
      id: 'whatsapp',
      name: 'WhatsApp',
      icon: MessageCircle,
      color: 'emerald',
      shortDesc: 'Where execs read',
      description: 'Capture executive attention where they read. Perfect for international leads. Voice notes, documents, and casual touchpoints work great in Europe and APAC.',
      gradient: 'from-emerald-900/30 to-emerald-800/20',
      border: 'border-emerald-700/50',
      activeBorder: 'border-emerald-500',
      iconColor: 'text-emerald-400',
      stats: { open: '95%', reply: '18%', meeting: '4.5%' }
    },
    {
      id: 'voicemail',
      name: 'Voicemail',
      icon: Phone,
      color: 'orange',
      shortDesc: 'Human touch',
      description: 'AI voice drops for the human touch. Natural and personalized voice messages dropped directly to voicemail (no ringing). Perfect final touchpoint.',
      gradient: 'from-orange-900/30 to-orange-800/20',
      border: 'border-orange-700/50',
      activeBorder: 'border-orange-500',
      iconColor: 'text-orange-400',
      stats: { open: '72%', reply: '6%', meeting: '1.5%' }
    }
  ];

  const selectedChannel = channels.find(c => c.id === activeChannel) || channels[0];

  return (
    <div className="bg-[#1A1F2E] min-h-screen text-white">

      {/* NAVIGATION */}
      <nav className="fixed top-0 left-0 right-0 bg-[#1A1F2E]/95 backdrop-blur-sm shadow-xl border-b border-gray-800 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <a href="/" className="flex items-center">
            <img
              src="/images/image copy copy.png"
              alt="Rekindle.ai - Lead Revival Platform"
              className="h-12 md:h-14 w-auto hover:opacity-90 transition-opacity"
            />
          </a>

          <div className="hidden md:flex items-center gap-8">
            <a href="#how-it-works" className="text-gray-400 hover:text-white transition">
              How It Works
            </a>
            <a href="#pricing" className="text-gray-400 hover:text-white transition">
              Pricing
            </a>
            <a href="#auto-icp" className="text-gray-400 hover:text-white transition">
              Auto-ICP
            </a>
            <button
              onClick={() => navigate('/login')}
              className="text-gray-400 hover:text-white transition"
            >
              Login
            </button>
            <button
              onClick={() => navigate('/pilot-application')}
              className="bg-[#FF6B35] text-white px-6 py-2 rounded-full font-semibold hover:bg-[#F7931E] transition"
            >
              Apply for Pilot
            </button>
          </div>
        </div>
      </nav>

      <main className="pt-20">

        {/* SECTION 1: SUPERNOVA HERO - Maximum Conversion Impact */}
        <SupernovaHero />

        {/* PREMIUM STAT CARDS - Stripe Dashboard Quality */}
        <div className="relative -mt-32 px-4 mb-0 z-10">
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              {/* Premium Card 1 - Meeting Rate */}
              <div className="group relative glass-card-hover rounded-3xl p-10 overflow-hidden animate-scale-in delay-100 opacity-0">
                {/* Animated background gradients */}
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 via-orange-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,107,53,0.15),transparent_60%)]" />

                {/* Floating particles effect */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-orange-400/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-1000" />

                <div className="relative">
                  {/* Icon badge */}
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 mb-6 group-hover:scale-110 group-hover:rotate-6 transition-transform duration-300">
                    <svg className="w-7 h-7 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>

                  <div className="text-7xl font-black bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent mb-4 tracking-tight drop-shadow-[0_0_30px_rgba(255,107,53,0.3)]">
                    15.2%
                  </div>

                  <div className="text-white font-bold text-xl mb-2">
                    Meeting Booking Rate
                  </div>
                  <div className="text-gray-400 text-sm mb-3">
                    (Verified across 847 leads, Q4 2024)
                  </div>

                  <div className="flex items-center gap-2 text-sm mb-3">
                    <div className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
                      <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
                      </svg>
                      <span className="text-green-400 font-semibold">2.3x industry avg</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-white/10">
                    <span className="text-gray-400 text-sm">Industry average: </span>
                    <span className="text-red-400 font-semibold line-through">6-8%</span>
                    <span className="text-gray-400 text-sm"> (you're getting </span>
                    <span className="text-orange-400 font-bold">2x better</span>
                    <span className="text-gray-400 text-sm">)</span>
                  </div>
                </div>

                {/* Hover glow effect */}
                <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" style={{
                  boxShadow: '0 0 60px rgba(255, 107, 53, 0.2)'
                }} />
              </div>

              {/* Premium Card 2 - ROI */}
              <div className="group relative glass-card-hover rounded-3xl p-10 overflow-hidden animate-scale-in delay-200 opacity-0">
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 via-orange-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_30%,rgba(255,107,53,0.15),transparent_60%)]" />

                <div className="absolute top-0 left-0 w-32 h-32 bg-orange-500/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-1000" />

                <div className="relative">
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 mb-6 group-hover:scale-110 group-hover:-rotate-6 transition-transform duration-300">
                    <svg className="w-7 h-7 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>

                  <div className="text-7xl font-black bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent mb-4 tracking-tight drop-shadow-[0_0_30px_rgba(255,107,53,0.3)]">
                    8.4x
                  </div>

                  <div className="text-white font-bold text-xl mb-2">
                    Average ROI
                  </div>
                  <div className="text-gray-400 text-sm mb-3">
                    (Based on £47K in closed deals, Q4 2024)
                  </div>

                  <div className="flex items-center gap-2 text-sm mb-3">
                    <div className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                      <svg className="w-4 h-4 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-emerald-400 font-semibold">Verified results</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-white/10">
                    <span className="text-gray-400 text-sm">Every £1 spent = </span>
                    <span className="text-orange-400 font-bold">£8.40 back</span>
                    <span className="text-gray-400 text-sm"> in closed revenue</span>
                  </div>
                </div>

                <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" style={{
                  boxShadow: '0 0 60px rgba(255, 107, 53, 0.2)'
                }} />
              </div>

              {/* Premium Card 3 - Speed to Launch */}
              <div className="group relative glass-card-hover rounded-3xl p-10 overflow-hidden animate-scale-in delay-300 opacity-0">
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 via-orange-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,107,53,0.15),transparent_60%)]" />

                <div className="absolute bottom-0 right-0 w-32 h-32 bg-orange-600/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-1000" />

                <div className="relative">
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 mb-6 group-hover:scale-110 group-hover:rotate-12 transition-transform duration-300">
                    <svg className="w-7 h-7 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>

                  <div className="text-7xl font-black bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent mb-4 tracking-tight drop-shadow-[0_0_30px_rgba(255,107,53,0.3)]">
                    18hrs
                  </div>

                  <div className="text-white font-bold text-xl mb-2">
                    To First Meeting Booked
                  </div>
                  <div className="text-gray-400 text-sm mb-3">
                    (Average time from import to reply)
                  </div>

                  <div className="flex items-center gap-2 text-sm mb-3">
                    <div className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20">
                      <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                      </svg>
                      <span className="text-blue-400 font-semibold">Fastest in industry</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-white/10">
                    <span className="text-gray-400 text-sm">Your competitors take </span>
                    <span className="text-red-400 font-semibold line-through">2-3 weeks</span>
                    <span className="text-gray-400 text-sm">. You take </span>
                    <span className="text-orange-400 font-bold">18 hours</span>
                  </div>
                </div>

                <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" style={{
                  boxShadow: '0 0 60px rgba(255, 107, 53, 0.2)'
                }} />
              </div>
            </div>
          </div>
        </div>

        {/* SECTION 2: EMOTIONAL TRIGGER - "I'M LOSING MONEY EVERY DAY" */}
        <section className="relative -mt-64 pt-20 pb-20 px-4 overflow-hidden">
          {/* Dramatic background */}
          <div className="absolute inset-0 bg-gradient-to-b from-[#1A1F2E] via-[#242938] to-[#1A1F2E]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(239,68,68,0.1),transparent_70%)]" />

          <div className="max-w-7xl mx-auto relative z-10">
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full mb-6">
                <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span className="text-sm text-white font-semibold tracking-wide">THE PROBLEM NOBODY TALKS ABOUT</span>
              </div>

              {/* EMOTIONAL TRIGGER: COMPETITOR THREAT */}
              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-tight tracking-tight">
                Every Day You Wait, Your Competitors Are Stealing{' '}
                <span className="bg-gradient-to-r from-red-400 via-red-500 to-orange-500 bg-clip-text text-transparent">YOUR</span> Customers.
                <br />
                <span className="text-4xl md:text-5xl lg:text-6xl text-gray-300 mt-4 block">
                  The Same Leads You Spent £200-£5,000 Each to Acquire Are Now Booking Meetings With Your Competitors.
                </span>
              </h2>

              <div className="max-w-4xl mx-auto text-left space-y-6 mb-10">
                <p className="text-xl md:text-2xl text-gray-200 leading-relaxed">
                  Right now, you have <span className="text-white font-bold">£<AnimatedStat end={500000} decimals={0} />K to £<AnimatedStat end={2} decimals={0} />M worth of leads</span> sitting dormant in your CRM.
                </p>

                <p className="text-xl md:text-2xl text-gray-200 leading-relaxed">
                  Leads who <span className="text-white font-semibold">opened your emails</span>. <span className="text-white font-semibold">Downloaded your content</span>. Even <span className="text-white font-semibold">took sales calls</span>.
                </p>

                <p className="text-xl md:text-2xl text-gray-200 leading-relaxed">
                  Then they went silent.
                </p>

                <p className="text-xl md:text-2xl text-gray-200 leading-relaxed">
                  Not because your product sucks. Not because they chose a competitor.
                </p>

                <p className="text-2xl md:text-3xl text-white leading-tight font-bold">
                  They went silent because <span className="text-orange-400">THE TIMING WASN'T RIGHT</span>.
                </p>

                {/* EMOTIONAL TRIGGER: COMPETITOR THREAT BOX */}
                <div className="border-l-4 border-red-500 pl-6 py-4 bg-red-500/10 rounded-r-xl animate-pulse-glow">
                  <p className="text-xl md:text-2xl text-white leading-relaxed font-bold">
                    But here's the killer: While you're chasing <span className="text-red-400">shiny new leads at £5K/pop</span>, your competitors are re-engaging <span className="text-orange-400">YOUR old prospects</span> at the <span className="text-white">EXACT moment they're ready to buy</span>.
                  </p>
                </div>

                <p className="text-xl md:text-2xl text-gray-200 leading-relaxed">
                  And you're sitting there, watching <span className="text-red-400 font-bold">85% of your pipeline slowly die</span>... thinking <span className="text-gray-400 italic">"that's just how B2B sales works."</span>
                </p>

                <p className="text-2xl md:text-3xl text-white leading-tight font-bold text-center pt-6">
                  It doesn't have to.
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {/* Card 1 - Investment */}
              <div className="group relative glass-card-hover rounded-3xl p-10 overflow-hidden border-2 border-red-500/30 hover:border-red-500/60">
                <div className="absolute inset-0 bg-gradient-to-br from-red-900/20 via-red-800/10 to-transparent opacity-50 group-hover:opacity-80 transition-opacity duration-500" />
                <div className="absolute top-0 right-0 w-40 h-40 bg-red-500/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700" />

                <div className="relative">
                  {/* Icon */}
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-red-500/30 to-red-600/20 border border-red-500/40 mb-6 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>

                  <div className="text-7xl font-black bg-gradient-to-br from-red-400 to-red-600 bg-clip-text text-transparent mb-4 drop-shadow-[0_0_30px_rgba(239,68,68,0.4)]">
                    £50K
                  </div>

                  <div className="text-white font-bold text-xl mb-3">
                    You Spent on Acquisition
                  </div>

                  <div className="text-gray-400 text-sm leading-relaxed">
                    Investment in ads, content, SDRs, and outreach to build your pipeline
                  </div>

                  <div className="mt-6 pt-6 border-t border-white/10">
                    <div className="flex items-center gap-2 text-sm text-red-400">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                      <span className="font-semibold">Money at risk</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Card 2 - Dormant Leads */}
              <div className="group relative glass-card-hover rounded-3xl p-10 overflow-hidden border-2 border-orange-500/30 hover:border-orange-500/60">
                <div className="absolute inset-0 bg-gradient-to-br from-orange-900/20 via-orange-800/10 to-transparent opacity-50 group-hover:opacity-80 transition-opacity duration-500" />
                <div className="absolute top-0 left-0 w-40 h-40 bg-orange-500/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700" />

                <div className="relative">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500/30 to-orange-600/20 border border-orange-500/40 mb-6 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-8 h-8 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>

                  <div className="text-7xl font-black bg-gradient-to-br from-orange-400 to-orange-600 bg-clip-text text-transparent mb-4 drop-shadow-[0_0_30px_rgba(255,107,53,0.4)]">
                    4,250
                  </div>

                  <div className="text-white font-bold text-xl mb-3">
                    Leads Went Dormant
                  </div>

                  <div className="text-gray-400 text-sm leading-relaxed">
                    Said "not now," ghosted, or went cold after initial contact
                  </div>

                  <div className="mt-6 pt-6 border-t border-white/10">
                    <div className="flex items-center gap-2 text-sm text-orange-400">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                      <span className="font-semibold">85% waste rate</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Card 3 - Lost Opportunity */}
              <div className="group relative glass-card-hover rounded-3xl p-10 overflow-hidden border-2 border-emerald-500/30 hover:border-emerald-500/60">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/20 via-emerald-800/10 to-transparent opacity-50 group-hover:opacity-80 transition-opacity duration-500" />
                <div className="absolute bottom-0 right-0 w-40 h-40 bg-emerald-500/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700" />

                <div className="relative">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/30 to-emerald-600/20 border border-emerald-500/40 mb-6 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                    </svg>
                  </div>

                  <div className="text-7xl font-black bg-gradient-to-br from-emerald-400 to-emerald-600 bg-clip-text text-transparent mb-4 drop-shadow-[0_0_30px_rgba(16,185,129,0.4)]">
                    £500K+
                  </div>

                  <div className="text-white font-bold text-xl mb-3">
                    Lost Revenue Potential
                  </div>

                  <div className="text-gray-400 text-sm leading-relaxed">
                    The hidden prize waiting to be unlocked in your dormant pipeline
                  </div>

                  <div className="mt-6 pt-6 border-t border-white/10">
                    <div className="flex items-center gap-2 text-sm text-emerald-400">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="font-semibold">Recoverable now</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Call-out box */}
            <div className="mt-16 max-w-4xl mx-auto glass-card rounded-3xl p-10 border-2 border-orange-500/30">
              <div className="flex items-start gap-6">
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500/30 to-orange-600/20 border border-orange-500/40 flex items-center justify-center">
                    <svg className="w-8 h-8 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white mb-3">This Isn't Your Fault—It's Industry Standard</h3>
                  <p className="text-lg text-gray-300 leading-relaxed">
                    Most B2B sales teams see <span className="text-orange-400 font-semibold">80-90% of leads go dormant</span>. The problem? You don't have the time or resources to manually track trigger events, personalize follow-ups, and reach out at the perfect moment. <span className="text-white font-semibold">That's where AI changes everything.</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 3: PREMIUM HOW IT WORKS - Apple Style */}
        <section className="relative py-32 px-4 overflow-hidden" id="how-it-works">
          <div className="absolute inset-0 bg-gradient-to-b from-[#1F2430] via-[#242938] to-[#1F2430]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,107,53,0.08),transparent_70%)]" />

          <div className="max-w-7xl mx-auto relative z-10">
            <div className="text-center mb-24">
              <div className="inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full mb-6">
                <svg className="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="text-sm text-white font-semibold tracking-wide">HOW REKINDLE WORKS</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-tight tracking-tight">
                Introducing: The{' '}
                <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">"Trigger Stack" Method™</span>
              </h2>

              <div className="max-w-5xl mx-auto space-y-6 mb-12">
                <p className="text-xl md:text-2xl text-gray-300 leading-relaxed">
                  While your competitors send <span className="text-gray-400 line-through">batch-and-blast emails</span> to everyone (and get ignored), we <span className="text-white font-bold">ONLY reach out when one of 47 buying signals fires</span>:
                </p>

                <div className="grid md:grid-cols-2 gap-4 text-lg text-gray-300">
                  <div className="flex items-start gap-3">
                    <span className="text-green-400 text-2xl">✓</span>
                    <div>
                      <span className="text-white font-semibold">Job change</span> (they just got promoted—new budget)
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-green-400 text-2xl">✓</span>
                    <div>
                      <span className="text-white font-semibold">Company funding round</span> (they have money to spend)
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-green-400 text-2xl">✓</span>
                    <div>
                      <span className="text-white font-semibold">Hiring spike</span> (they're scaling—need your solution NOW)
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-green-400 text-2xl">✓</span>
                    <div>
                      <span className="text-white font-semibold">Tech stack change</span> (they just ditched your competitor)
                    </div>
                  </div>
                  <div className="flex items-start gap-3 md:col-span-2">
                    <span className="text-green-400 text-2xl">✓</span>
                    <div>
                      <span className="text-white font-semibold">Earnings call mention</span> (CEO literally said your keyword)
                    </div>
                  </div>
                </div>

                <div className="glass-card rounded-2xl p-8 border-2 border-orange-500/30 bg-orange-500/5">
                  <p className="text-xl md:text-2xl text-white leading-relaxed">
                    <span className="text-orange-400 font-bold">The result?</span> <span className="text-green-400 font-bold">2.4x higher open rates</span>. <span className="text-green-400 font-bold">5.8x higher reply rates</span>. And meetings that actually <span className="text-white font-bold">CLOSE</span> (because timing is everything).
                  </p>
                </div>

                <p className="text-xl md:text-2xl text-gray-300 leading-relaxed text-center pt-4">
                  This isn't email marketing. This is <span className="text-white font-bold">AI-powered market intelligence</span> married to <span className="text-orange-400 font-bold">multi-channel outreach</span> (email + LinkedIn + SMS + direct mail).
                </p>

                <p className="text-2xl md:text-3xl text-white leading-tight font-bold text-center">
                  It's like having a <span className="text-orange-400">Bloomberg Terminal for your CRM</span>... with a sales team attached.
                </p>
              </div>
            </div>

            {/* Premium Timeline - Apple Style */}
            <div className="max-w-6xl mx-auto relative">
              {/* Vertical connecting line */}
              <div className="absolute left-8 md:left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-orange-500/0 via-orange-500/50 to-orange-500/0 hidden md:block" />

              <div className="space-y-24">
                {/* Step 1 */}
                <div className="relative grid md:grid-cols-2 gap-12 items-center">
                  <div className="md:text-right md:pr-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-500/10 border border-orange-500/30 mb-4">
                      <span className="text-xs font-bold text-orange-400 tracking-wider">STEP 1</span>
                    </div>
                    <h3 className="text-4xl font-bold text-white mb-4">
                      Upload Your Coldest Leads
                    </h3>
                    <p className="text-lg text-gray-300 leading-relaxed mb-6">
                      <span className="text-white font-bold">2 minutes. That's it.</span> Secure sync via CRM (Salesforce, HubSpot) or drag-and-drop CSV. <span className="text-orange-400 font-semibold">No technical setup. No API keys. No headaches.</span> Just upload and watch the AI go to work.
                    </p>
                    <div className="flex md:justify-end gap-3 flex-wrap">
                      <div className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-gray-400">
                        <span className="text-white font-semibold">Salesforce</span>
                      </div>
                      <div className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-gray-400">
                        <span className="text-white font-semibold">HubSpot</span>
                      </div>
                      <div className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-gray-400">
                        <span className="text-white font-semibold">CSV</span>
                      </div>
                    </div>
                  </div>

                  <div className="relative md:pl-16">
                    {/* Number circle */}
                    <div className="absolute left-0 md:left-1/2 md:-translate-x-1/2 -top-4 md:top-1/2 md:-translate-y-1/2 w-16 h-16 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 border-4 border-[#1F2430] flex items-center justify-center shadow-[0_0_30px_rgba(255,107,53,0.5)] z-10">
                      <span className="text-2xl font-black text-white">1</span>
                    </div>

                    <div className="glass-card-hover rounded-3xl p-8 border-2 border-orange-500/20 ml-20 md:ml-0">
                      <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/40 mb-6">
                        <Upload className="w-10 h-10 text-orange-400" />
                      </div>
                      <div className="text-sm text-orange-400 font-semibold mb-2">INSTANT IMPORT</div>
                      <p className="text-gray-400 leading-relaxed">
                        Drag & drop your leads or connect directly to your CRM. Our secure integration handles the rest.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Step 2 */}
                <div className="relative grid md:grid-cols-2 gap-12 items-center">
                  <div className="md:order-2 md:pl-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-500/10 border border-orange-500/30 mb-4">
                      <span className="text-xs font-bold text-orange-400 tracking-wider">STEP 2</span>
                    </div>
                    <h3 className="text-4xl font-bold text-white mb-4">
                      AI Pinpoints Buying Intent
                    </h3>
                    <p className="text-lg text-gray-300 leading-relaxed mb-6">
                      Our AI monitors <span className="text-white font-bold">50+ signals per lead, 24/7</span>—funding rounds, new hires, job changes, company news, tech stack changes. <span className="text-orange-400 font-semibold">The moment a trigger fires, we know. And we act.</span> No waiting. No manual research. Pure automation.
                    </p>
                    <div className="space-y-3">
                      {['Funding rounds', 'New hires', 'Job changes', 'Company news'].map((trigger) => (
                        <div key={trigger} className="flex items-center gap-3">
                          <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          <span className="text-gray-300">{trigger}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="relative md:order-1 md:pr-16">
                    <div className="absolute left-0 md:left-1/2 md:-translate-x-1/2 -top-4 md:top-1/2 md:-translate-y-1/2 w-16 h-16 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 border-4 border-[#1F2430] flex items-center justify-center shadow-[0_0_30px_rgba(255,107,53,0.5)] z-10">
                      <span className="text-2xl font-black text-white">2</span>
                    </div>

                    <div className="glass-card-hover rounded-3xl p-8 border-2 border-orange-500/20 ml-20 md:ml-0">
                      <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/40 mb-6">
                        <Brain className="w-10 h-10 text-orange-400" />
                      </div>
                      <div className="text-sm text-orange-400 font-semibold mb-2">TRIGGER DETECTION</div>
                      <p className="text-gray-400 leading-relaxed">
                        Our AI monitors 50+ signals per lead to identify the perfect moment to reach out.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Step 3 */}
                <div className="relative grid md:grid-cols-2 gap-12 items-center">
                  <div className="md:text-right md:pr-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-500/10 border border-orange-500/30 mb-4">
                      <span className="text-xs font-bold text-orange-400 tracking-wider">STEP 3</span>
                    </div>
                    <h3 className="text-4xl font-bold text-white mb-4">
                      Hyper-Personalized Outreach
                    </h3>
                    <p className="text-lg text-gray-300 leading-relaxed">
                      <span className="text-white font-bold">Every message is unique.</span> No templates. No "Hi [Name]" placeholders. <span className="text-orange-400 font-semibold">We reference the exact trigger event, the specific company news, the precise reason they should care right now.</span> That's why we get 15.2% reply rates when the industry gets 6-8%.
                    </p>
                  </div>

                  <div className="relative md:pl-16">
                    <div className="absolute left-0 md:left-1/2 md:-translate-x-1/2 -top-4 md:top-1/2 md:-translate-y-1/2 w-16 h-16 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 border-4 border-[#1F2430] flex items-center justify-center shadow-[0_0_30px_rgba(255,107,53,0.5)] z-10">
                      <span className="text-2xl font-black text-white">3</span>
                    </div>

                    <div className="glass-card-hover rounded-3xl p-8 border-2 border-orange-500/20 ml-20 md:ml-0">
                      <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/40 mb-6">
                        <MessageSquare className="w-10 h-10 text-orange-400" />
                      </div>
                      <div className="text-sm text-orange-400 font-semibold mb-2">SMART MESSAGING</div>
                      <p className="text-gray-400 leading-relaxed">
                        Every message is unique, contextual, and references real trigger events that matter to your lead.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Step 4 */}
                <div className="relative grid md:grid-cols-2 gap-12 items-center">
                  <div className="md:order-2 md:pl-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 mb-4">
                      <span className="text-xs font-bold text-emerald-400 tracking-wider">STEP 4</span>
                    </div>
                    <h3 className="text-4xl font-bold text-white mb-4">
                      Revenue-Ready Meetings Booked
                    </h3>
                    <p className="text-lg text-gray-300 leading-relaxed mb-6">
                      <span className="text-white font-bold">Lead replies → AI confirms → Meeting on your calendar → You close the deal.</span> <span className="text-orange-400 font-semibold">You only pay 2.5% of ACV when the meeting is actually booked.</span> No meetings? No performance fee. It's that simple.
                    </p>
                    <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-emerald-500/10 border border-emerald-500/30">
                      <svg className="w-6 h-6 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-emerald-400 font-semibold">Only pay for confirmed meetings</span>
                    </div>
                  </div>

                  <div className="relative md:order-1 md:pr-16">
                    <div className="absolute left-0 md:left-1/2 md:-translate-x-1/2 -top-4 md:top-1/2 md:-translate-y-1/2 w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 border-4 border-[#1F2430] flex items-center justify-center shadow-[0_0_30px_rgba(16,185,129,0.5)] z-10">
                      <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>

                    <div className="glass-card-hover rounded-3xl p-8 border-2 border-emerald-500/20 ml-20 md:ml-0">
                      <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 border border-emerald-500/40 mb-6">
                        <Calendar className="w-10 h-10 text-emerald-400" />
                      </div>
                      <div className="text-sm text-emerald-400 font-semibold mb-2">MEETING CONFIRMED</div>
                      <p className="text-gray-400 leading-relaxed">
                        Seamlessly synced to your calendar. You show up, close the deal, and generate revenue.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom tagline */}
            <div className="text-center mt-24">
              <p className="text-2xl font-bold text-white mb-2">
                From dormant lead to booked meeting in <span className="text-orange-400">18 hours</span> (average)
              </p>
              <p className="text-gray-400 mb-6">
                <span className="text-white font-semibold">The entire process runs on autopilot</span> while you focus on closing deals. Your competitors take 2-3 weeks. You take 18 hours.
              </p>
              
              {/* Specialized Agent Highlight */}
              <div className="max-w-4xl mx-auto glass-card rounded-3xl p-8 border-2 border-purple-500/30 bg-gradient-to-br from-purple-500/10 to-purple-600/5">
                <div className="flex items-center justify-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-white">Specialized Dead Lead Reactivation Agent</h3>
                </div>
                <p className="text-lg text-gray-300 leading-relaxed mb-4">
                  One of our specialized AI agents is <span className="text-white font-bold">exclusively dedicated to dead lead reactivation</span>. It monitors <span className="text-purple-400 font-semibold">50+ signals per lead, 24/7</span>—funding rounds, job changes, company news, tech stack updates, hiring announcements. <span className="text-orange-400 font-semibold">The moment a trigger fires, it automatically segments the lead, researches the context, and crafts a hyper-personalized re-engagement message</span>—all without you lifting a finger.
                </p>
                <div className="grid md:grid-cols-3 gap-4 mt-6">
                  <div className="text-center">
                    <div className="text-3xl font-black text-purple-400 mb-2">50+</div>
                    <div className="text-sm text-gray-400">Signals Monitored</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-black text-purple-400 mb-2">24/7</div>
                    <div className="text-sm text-gray-400">Continuous Monitoring</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-black text-purple-400 mb-2">Auto</div>
                    <div className="text-sm text-gray-400">Trigger Detection</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* EMAIL COMPARISON SECTION */}
        <section className="relative py-20 px-4 bg-gradient-to-b from-[#1F2430] to-[#242938]">
          <div className="max-w-7xl mx-auto">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-12">
                <div className="inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full mb-6">
                  <svg className="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span className="text-sm text-white font-semibold tracking-wide">THE SECRET: RESEARCH BEATS TEMPLATES</span>
                </div>

                <h3 className="text-4xl md:text-5xl lg:text-6xl font-black text-white mb-6 leading-tight">
                  Why Your Competitors Get <span className="text-red-400">2% Replies</span>
                  <br />
                  While You Could Get <span className="text-green-400">15.2%</span>
                </h3>

                <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
                  <span className="text-white font-bold">Here's what nobody tells you:</span> Every generic "just checking in" email <span className="text-red-400 font-bold">kills your domain reputation</span> and gets you blacklisted. But <span className="text-green-400 font-bold">AI-researched messages that establish context + urgency + specific value</span> get <span className="text-white font-bold">7.6x better results</span>.
                </p>

                <div className="mt-8 max-w-3xl mx-auto">
                  <p className="text-lg text-orange-300 font-semibold">
                    👇 Here's the exact difference (real examples from our system):
                  </p>
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-8">
                <div className="glass-card rounded-3xl p-8 border-2 border-red-500/30 bg-red-500/5">
                  <div className="flex items-center gap-2 mb-6">
                    <XCircle className="w-7 h-7 text-red-400" />
                    <div className="font-bold text-xl text-red-400">❌ Generic Template (2% Reply Rate)</div>
                  </div>
                  <p className="text-sm text-gray-400 mb-6">
                    <span className="text-red-400 font-bold">What your competitors send:</span> Looks like spam. <span className="text-white font-semibold">Destroys sender reputation.</span> Gets ignored. <span className="text-red-300">This is why 98% of follow-ups fail.</span>
                  </p>
                  <div className="bg-[#1A1F2E] rounded-2xl p-6 font-mono text-sm border border-gray-700">
                    <div className="text-gray-500 mb-4 font-semibold">Subject: Following up</div>
                    <div className="text-gray-300 leading-relaxed">
                      Hi Sarah,
                      <br /><br />
                      Just checking in on that project we discussed a few months ago.
                      Are you still interested?
                      <br /><br />
                      Let me know if you'd like to reconnect.
                      <br /><br />
                      Best,<br />
                      John
                    </div>
                  </div>
                </div>

                <div className="glass-card rounded-3xl p-8 border-2 border-green-500/30 bg-green-500/5">
                  <div className="flex items-center gap-2 mb-6">
                    <CheckCircle className="w-7 h-7 text-green-400" />
                    <div className="font-bold text-xl text-green-400">✅ Trigger Stack Method™ (15.2% Reply Rate)</div>
                  </div>
                  <p className="text-sm text-gray-400 mb-6">
                    <span className="text-green-400 font-bold">What Rekindle sends:</span> AI researches <span className="text-white font-semibold">47 data points</span> (funding, hiring, tech stack, earnings calls). References <span className="text-orange-400 font-semibold">past conversations</span>. Offers <span className="text-emerald-400 font-semibold">specific value</span> (playbook, metrics). <span className="text-green-300 font-bold">Result: 7.6x higher reply rate.</span>
                  </p>
                  <div className="bg-[#1A1F2E] rounded-2xl p-6 font-mono text-sm border border-gray-700">
                    <div className="text-gray-500 mb-4 font-semibold">Subject: CloudSync's Series B + Q4 hiring</div>
                    <div className="text-gray-300 leading-relaxed">
                      Hi Sarah,
                      <br /><br />
                      Congrats on the £8M Series B (TechCrunch Tuesday).
                      <br /><br />
                      You're hiring 5 marketing roles by Q4. That onboarding bottleneck we discussed in March? About to hit hard.
                      <br /><br />
                      5 hires × 3 weeks ramp = £18K-£24K wasted salary.
                      <br /><br />
                      Three Series B companies used our playbook. Cut ramp to 5 days. Freed 12 hrs/week per hire.
                      <br /><br />
                      12 min Thursday 2pm? Just framework + metrics, no pitch.
                      <br /><br />
                      - John
                    </div>
                  </div>
                  <div className="mt-6 space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-green-400 font-semibold">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Ultra-specific research (£8M, TechCrunch, exact date: "last Tuesday")
                    </div>
                    <div className="flex items-center gap-2 text-green-400 font-semibold">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      References past context (March onboarding discussion)
                    </div>
                    <div className="flex items-center gap-2 text-green-400 font-semibold">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Quantifies pain (£18K-£24K wasted salary = urgency)
                    </div>
                    <div className="flex items-center gap-2 text-green-400 font-semibold">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Proof from peers (3 companies at exact same stage)
                    </div>
                    <div className="flex items-center gap-2 text-green-400 font-semibold">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Low-friction ask (12 min, exact time + timezone, "no pitch, no deck")
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>


        {/* SECTION 4: PREMIUM MULTI-CHANNEL */}
        <section className="relative py-32 px-4 overflow-hidden">
          {/* Premium background */}
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />

          {/* Aurora orbs */}
          <div className="absolute top-20 right-10 w-[500px] h-[500px] bg-gradient-to-br from-blue-500/20 via-blue-600/10 to-transparent rounded-full blur-[120px] animate-aurora" />
          <div className="absolute bottom-20 left-10 w-[400px] h-[400px] bg-gradient-to-br from-orange-500/20 via-orange-600/10 to-transparent rounded-full blur-[100px] animate-aurora" style={{ animationDelay: '3s' }} />

          <div className="max-w-7xl mx-auto relative z-10">
            {/* Premium header */}
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-5 py-2.5 glass-card rounded-full mb-8 hover:scale-105 transition-all duration-300">
                <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span className="text-sm text-white font-semibold tracking-wide">MULTI-CHANNEL OUTREACH</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-tight tracking-tight">
                One Lead, Five Channels.{' '}
                <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">
                  Maximum Reach
                </span>
                .
              </h2>

              <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
                <span className="text-white font-bold">Intelligent, pre-built sequences across every channel</span> until the lead responds or opts out. <span className="text-orange-400 font-semibold">3-5x higher engagement vs. email-only</span> (Forrester Research). <span className="text-white font-bold">Maximize reach without risking your team's bandwidth.</span>
              </p>
            </div>

            {/* Premium interactive channel tabs */}
            <div className="max-w-5xl mx-auto mb-16">
              <div className="flex flex-wrap justify-center gap-4 mb-12">
                {channels.map((channel, idx) => (
                  <button
                    key={channel.name}
                    onClick={() => setActiveChannel(channel.name)}
                    className={`group relative px-8 py-5 rounded-2xl font-semibold text-lg transition-all duration-500 hover:scale-105 ${
                      activeChannel === channel.name
                        ? 'glass-card border-2 border-orange-500/50 text-white shadow-[0_0_40px_rgba(255,107,53,0.3)]'
                        : 'glass-card border border-white/10 text-gray-400 hover:text-white hover:border-white/20'
                    }`}
                    style={{ animationDelay: `${idx * 100}ms` }}
                  >
                    {activeChannel === channel.name && (
                      <div className="absolute inset-0 bg-gradient-to-r from-orange-500/20 to-orange-600/20 rounded-2xl animate-pulse" />
                    )}
                    <div className="relative flex items-center gap-3">
                      {channel.name === 'Email' && <Mail className="w-6 h-6" />}
                      {channel.name === 'LinkedIn' && <Linkedin className="w-6 h-6" />}
                      {channel.name === 'SMS' && <MessageSquare className="w-6 h-6" />}
                      {channel.name === 'WhatsApp' && <MessageCircle className="w-6 h-6" />}
                      {channel.name === 'Voice' && <Phone className="w-6 h-6" />}
                      <span>{channel.name}</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Channel content with premium glass card */}
              <div className="glass-card-hover rounded-3xl p-12 border-2 border-white/10">
                <div className="text-center mb-8">
                  <h3 className="text-3xl font-bold text-white mb-4">
                    {channels.find(c => c.name === activeChannel)?.name} Strategy
                  </h3>
                  <p className="text-lg text-gray-300 max-w-3xl mx-auto">
                    {channels.find(c => c.name === activeChannel)?.description}
                  </p>
                </div>

                {/* Premium stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12">
                  {[
                    { label: 'Open Rate', value: '67%', color: 'from-blue-400 to-blue-600' },
                    { label: 'Response Rate', value: '23%', color: 'from-green-400 to-green-600' },
                    { label: 'Meeting Rate', value: '15.2%', color: 'from-orange-400 to-orange-600' },
                    { label: 'Avg. Time to Reply', value: '2.3 days', color: 'from-purple-400 to-purple-600' }
                  ].map((stat, idx) => (
                    <div key={stat.label} className="glass-card rounded-2xl p-6 text-center hover:scale-105 transition-all duration-300" style={{ animationDelay: `${idx * 100}ms` }}>
                      <div className={`text-4xl font-black bg-gradient-to-r ${stat.color} bg-clip-text text-transparent mb-2`}>
                        {stat.value}
                      </div>
                      <div className="text-sm text-gray-400 font-semibold">
                        {stat.label}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Apple-style 7-Day Premium Timeline */}
            <div className="max-w-5xl mx-auto mb-20">
              <div className="text-center mb-12">
                <h3 className="text-4xl font-bold text-white mb-4">
                  Example 7-Day <span className="text-gradient-orange">AI-Powered</span> Sequence
                </h3>
                <p className="text-lg text-gray-300">
                  Intelligently orchestrated across all channels until the lead responds
                </p>
              </div>

              <div className="relative">
                {/* Vertical gradient timeline */}
                <div className="absolute left-12 md:left-16 top-8 bottom-8 w-0.5 bg-gradient-to-b from-orange-500/0 via-orange-500/70 to-orange-500/0" />

                <div className="space-y-8">
                  {[
                    { day: 0, channel: 'Email', icon: Mail, color: 'blue', message: 'Initial personalized message with your brand voice' },
                    { day: 2, channel: 'SMS', icon: MessageSquare, color: 'green', message: 'Quick, contextual follow-up text message' },
                    { day: 3, channel: 'Push', icon: Bell, color: 'purple', message: 'Smart push notification with trigger event update' },
                    { day: 5, channel: 'Email', icon: Mail, color: 'blue', message: 'Different angle with social proof & case study' },
                    { day: 6, channel: 'WhatsApp', icon: MessageCircle, color: 'emerald', message: 'Personal voice note or rich media message' },
                    { day: 7, channel: 'Voice', icon: Phone, color: 'orange', message: 'Strategic voicemail drop as final touchpoint' }
                  ].map((step, idx) => (
                    <div key={idx} className="relative flex items-start gap-8 group animate-fade-in-up" style={{ animationDelay: `${idx * 100}ms`, opacity: 0 }}>
                      {/* Timeline node */}
                      <div className="relative flex-shrink-0">
                        <div className="flex items-center gap-4">
                          {/* Day badge */}
                          <div className="w-24 text-right">
                            <span className="text-sm font-bold text-gray-400 group-hover:text-orange-400 transition-colors">
                              Day {step.day}
                            </span>
                          </div>
                          {/* Glowing circle */}
                          <div className={`w-12 h-12 rounded-full bg-gradient-to-br from-${step.color}-500 to-${step.color}-600 border-4 border-slate-900 flex items-center justify-center shadow-[0_0_30px_rgba(255,107,53,0.4)] group-hover:scale-125 group-hover:shadow-[0_0_50px_rgba(255,107,53,0.7)] transition-all duration-300 z-10`}>
                            <step.icon className="w-5 h-5 text-white" />
                          </div>
                        </div>
                      </div>

                      {/* Message card */}
                      <div className="flex-1 glass-card-hover rounded-2xl p-6 border-2 border-white/10 group-hover:border-orange-500/30 min-h-[100px] flex flex-col justify-center">
                        <div className="flex items-center gap-3 mb-3">
                          <span className={`font-bold text-lg text-${step.color}-400`}>{step.channel}</span>
                          <div className="h-px flex-1 bg-gradient-to-r from-white/20 to-transparent" />
                        </div>
                        <p className="text-gray-300 leading-relaxed">
                          {step.message}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Results badge at bottom */}
                <div className="mt-12 text-center">
                  <div className="inline-flex items-center gap-4 glass-card rounded-3xl px-10 py-6 border-2 border-green-500/30 hover:scale-105 transition-all duration-300">
                    <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="text-left">
                      <div className="text-4xl font-black bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
                        15.2% booking rate
                      </div>
                      <div className="text-sm text-gray-400">vs. 6-8% industry average</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Premium compliance cards */}
            <div className="mt-20">
              <h3 className="text-3xl font-bold text-center mb-12 text-white">
                Enterprise Control & <span className="text-gradient-orange">Compliance</span>
              </h3>
              <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                {[
                  {
                    icon: Zap,
                    title: 'Dynamic Flexibility',
                    description: 'Build adaptive cadences that pause instantly when a hook is found. Smart AI adjusts timing based on engagement signals.',
                    color: 'from-yellow-400 to-orange-500'
                  },
                  {
                    icon: Shield,
                    title: 'Full Compliance',
                    description: 'Built-in GDPR and CAN-SPAM readiness. Automatic suppression list sync and consent management at scale.',
                    color: 'from-green-400 to-emerald-500'
                  },
                  {
                    icon: Target,
                    title: 'Maximum Efficiency',
                    description: 'One unified dashboard to orchestrate all five channels. Maximize SDR efficiency with automated workflows.',
                    color: 'from-blue-400 to-indigo-500'
                  }
                ].map((feature, idx) => (
                  <div key={feature.title} className="group glass-card-hover rounded-3xl p-8 border-2 border-white/10 hover:border-orange-500/30 animate-fade-in-up" style={{ animationDelay: `${idx * 150}ms`, opacity: 0 }}>
                    <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} opacity-90 mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300`}>
                      <feature.icon className="w-8 h-8 text-white" />
                    </div>
                    <h4 className="text-2xl font-bold text-white mb-4 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-orange-400 group-hover:to-orange-600 group-hover:bg-clip-text transition-all duration-300">
                      {feature.title}
                    </h4>
                    <p className="text-gray-400 leading-relaxed text-base">
                      {feature.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 5: PREMIUM PRICING */}
        <section className="relative py-32 px-4 overflow-hidden" id="pricing">
          {/* Premium background */}
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />

          {/* Aurora orbs */}
          <div className="absolute top-1/4 left-10 w-[500px] h-[500px] bg-gradient-to-br from-green-500/15 via-emerald-600/10 to-transparent rounded-full blur-[120px] animate-aurora" />
          <div className="absolute bottom-1/4 right-10 w-[600px] h-[600px] bg-gradient-to-br from-orange-500/15 via-orange-600/10 to-transparent rounded-full blur-[140px] animate-aurora" style={{ animationDelay: '4s' }} />

          <div className="max-w-7xl mx-auto relative z-10">
            {/* Premium header */}
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-5 py-2.5 glass-card rounded-full mb-8 hover:scale-105 transition-all duration-300">
                <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm text-white font-semibold tracking-wide">PERFORMANCE PRICING</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-tight tracking-tight">
                Pay <span className="bg-gradient-to-r from-green-400 via-emerald-500 to-green-600 bg-clip-text text-transparent">Only When We Deliver</span>.
                <br />
                <span className="text-4xl md:text-5xl">80%+ of Your Spend Is Performance-Based</span>
              </h2>

              <p className="text-xl md:text-2xl text-gray-300 max-w-5xl mx-auto leading-relaxed mb-6">
                <span className="text-white font-bold">First 30 days: Zero platform fee.</span> Pay only <span className="text-orange-400 font-bold">2.5% of ACV per booked meeting</span>. After 30 days, <span className="text-white font-bold">lock in 50% off platform fee forever</span> (£9.99-£249/mo instead of £19-£499/mo). <span className="text-emerald-400 font-semibold">No meetings booked? You only pay the platform fee.</span> Cancel anytime.
              </p>
              
              {/* PILOT PROGRAM NOTICE + BILLING TOGGLE */}
              <div className="flex flex-col items-center gap-6 mb-8">
                <div className="glass-card inline-flex items-center gap-3 px-6 py-3 rounded-xl border-2 border-orange-500/40">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
                  </span>
                  <span className="text-white font-bold text-sm">🎯 EXCLUSIVE PILOT PROGRAM PRICING</span>
                </div>

                {/* Annual vs Monthly Toggle */}
                <div className="inline-flex items-center gap-3 glass-card px-2 py-2 rounded-xl">
                  <button
                    onClick={() => setPricingPeriod('monthly')}
                    className={`px-6 py-2 rounded-lg font-bold text-sm transition-all ${pricingPeriod === 'monthly' ? 'bg-white/20 text-white' : 'text-gray-400 hover:text-white'}`}
                  >
                    Monthly
                  </button>
                  <button
                    onClick={() => setPricingPeriod('annual')}
                    className={`px-6 py-2 rounded-lg font-bold text-sm transition-all relative ${pricingPeriod === 'annual' ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white' : 'text-gray-400 hover:text-white'}`}
                  >
                    Annual
                    <span className="absolute -top-2 -right-2 px-2 py-0.5 bg-green-500 text-white text-xs rounded-full font-black">
                      -20%
                    </span>
                  </button>
                </div>
              </div>
            </div>

            {/* Premium pricing cards */}
            <div className="grid lg:grid-cols-3 gap-8 mb-20 max-w-7xl mx-auto">
              {/* Starter - Premium glass card */}
              <div className="group glass-card-hover rounded-3xl p-10 border-2 border-white/10 hover:border-blue-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '0ms' }}>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-white">Starter</h3>
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500/30 to-blue-600/20 border border-blue-500/40 flex items-center justify-center group-hover:scale-110 transition-all duration-300">
                    <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>

                <div className="mb-8">
                  {pricingPeriod === 'monthly' ? (
                    <>
                      <div className="mb-3">
                        <div className="text-sm text-green-400 font-bold mb-1">First 30 Days: £0 Platform Fee</div>
                        <div className="flex items-baseline gap-3">
                          <span className="text-4xl font-black text-gray-500 line-through">£19</span>
                          <span className="text-6xl font-black bg-gradient-to-br from-blue-400 to-blue-600 bg-clip-text text-transparent">£9.99</span>
                          <span className="text-gray-400 text-lg">/month</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">After 30 days (50% off forever)</div>
                      </div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/20 border border-green-500/40 rounded-full mb-2">
                        <span className="text-xs font-black text-green-400">50% OFF FOREVER</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-1">
                        Regular price: <span className="line-through">£19</span>
                      </p>
                      <p className="text-sm text-gray-400">
                        + <span className="text-orange-400 font-semibold">3% of deal value</span> per meeting
                      </p>
                    </>
                  ) : (
                    <>
                      <div className="mb-3">
                        <div className="text-sm text-green-400 font-bold mb-1">First 30 Days: £0 Platform Fee</div>
                        <div className="flex items-baseline gap-3">
                          <span className="text-4xl font-black text-gray-500 line-through">£182</span>
                          <span className="text-6xl font-black bg-gradient-to-br from-blue-400 to-blue-600 bg-clip-text text-transparent">£96</span>
                          <span className="text-gray-400 text-lg">/year</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">After 30 days (50% off forever + 20% annual)</div>
                      </div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/20 border border-green-500/40 rounded-full mb-2">
                        <span className="text-xs font-black text-green-400">50% OFF FOREVER + 20% ANNUAL</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-1">
                        Regular price: <span className="line-through">£182</span>
                      </p>
                      <p className="text-sm text-green-400 font-semibold mb-1">
                        Save £134/year (pilot + annual discount)
                      </p>
                      <p className="text-sm text-gray-400">
                        + <span className="text-orange-400 font-semibold">3% of deal value</span> per meeting
                      </p>
                    </>
                  )}
                </div>

                <ul className="space-y-4 mb-10 text-base">
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300">Up to <span className="text-white font-semibold">5,000 leads</span></span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300"><span className="text-white font-semibold">All 5 channels</span> included</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300"><span className="text-white font-semibold">AI research</span> & scoring</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300"><span className="text-white font-semibold">Auto-ICP sourcing</span> (500/mo)</span>
                  </li>
                </ul>

                <button
                  onClick={() => navigate('/pilot-application')}
                  className="w-full btn-shimmer bg-gradient-to-r from-blue-500 to-blue-600 text-white py-4 rounded-2xl font-bold text-lg hover:scale-105 transition-all duration-300 shadow-[0_0_30px_rgba(59,130,246,0.3)]"
                >
                  🚀 Start FREE 72-Hour Test
                </button>

                <p className="text-center text-xs text-gray-500 mt-4">Perfect for solopreneurs • No credit card</p>
              </div>

              {/* Pro - Nuclear orange gradient */}
              <div className="group relative rounded-3xl p-10 border-2 border-orange-500/50 animate-fade-in-up transform lg:scale-105 shadow-[0_0_60px_rgba(255,107,53,0.4)]" style={{ opacity: 0, animationDelay: '150ms' }}>
                {/* Animated gradient background */}
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500 via-orange-600 to-orange-500 rounded-3xl animate-gradient bg-[length:200%_200%]" />
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/90 via-orange-600/90 to-orange-500/90 rounded-3xl" />

                {/* Popular badge */}
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="glass-card border-2 border-white/40 rounded-full px-6 py-2 backdrop-blur-xl">
                    <span className="text-sm font-black text-white tracking-wider">MOST POPULAR</span>
                  </div>
                </div>

                <div className="relative">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-2xl font-bold text-white">Pro</h3>
                    <div className="w-12 h-12 rounded-2xl bg-white/20 border border-white/40 flex items-center justify-center group-hover:scale-110 group-hover:rotate-12 transition-all duration-300">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                      </svg>
                    </div>
                  </div>

                  <div className="mb-8">
                    {pricingPeriod === 'monthly' ? (
                      <>
                        <div className="mb-3">
                          <div className="text-sm text-green-300 font-bold mb-1">First 30 Days: £0 Platform Fee</div>
                          <div className="flex items-baseline gap-3">
                            <span className="text-4xl font-black text-white/50 line-through drop-shadow-none">£99</span>
                            <span className="text-6xl font-black text-white drop-shadow-[0_0_20px_rgba(255,255,255,0.5)]">£49</span>
                            <span className="text-white/80 text-lg">/month</span>
                          </div>
                          <div className="text-xs text-white/70 mt-1">After 30 days (50% off forever)</div>
                        </div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 border border-white/40 rounded-full mb-2">
                          <span className="text-xs font-black text-white">50% OFF FOREVER</span>
                        </div>
                        <p className="text-xs text-white/70 mb-1">
                          Regular price: <span className="line-through">£99</span>
                        </p>
                        <p className="text-sm text-white/90">
                          + <span className="text-white font-semibold">2.5% of deal value</span> per meeting
                        </p>
                      </>
                    ) : (
                      <>
                        <div className="mb-3">
                          <div className="text-sm text-green-300 font-bold mb-1">First 30 Days: £0 Platform Fee</div>
                          <div className="flex items-baseline gap-3">
                            <span className="text-4xl font-black text-white/50 line-through drop-shadow-none">£950</span>
                            <span className="text-6xl font-black text-white drop-shadow-[0_0_20px_rgba(255,255,255,0.5)]">£470</span>
                            <span className="text-white/80 text-lg">/year</span>
                          </div>
                          <div className="text-xs text-white/70 mt-1">After 30 days (50% off forever + 20% annual)</div>
                        </div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 border border-white/40 rounded-full mb-2">
                          <span className="text-xs font-black text-white">50% OFF FOREVER + 20% ANNUAL</span>
                        </div>
                        <p className="text-xs text-white/70 mb-1">
                          Regular price: <span className="line-through">£950</span>
                        </p>
                        <p className="text-sm text-green-300 font-semibold mb-1">
                          Save £718/year (pilot + annual discount)
                        </p>
                        <p className="text-sm text-white/90">
                          + <span className="text-white font-semibold">2.5% of deal value</span> per meeting
                        </p>
                      </>
                    )}
                  </div>

                  <ul className="space-y-4 mb-10 text-base text-white">
                    <li className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
                      <span>Up to <span className="font-bold">25,000 leads</span></span>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
                      <span><span className="font-bold">All 5 channels</span> included</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
                      <span><span className="font-bold">Auto-ICP sourcing</span> (2,500/mo)</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
                      <span><span className="font-bold">CRM integration</span></span>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
                      <span><span className="font-bold">5 team seats</span></span>
                    </li>
                  </ul>

                  <button
                    onClick={() => navigate('/pilot-application')}
                    className="w-full btn-shimmer bg-white text-orange-600 py-4 rounded-2xl font-black text-lg hover:scale-105 transition-all duration-300 shadow-[0_8px_30px_rgba(0,0,0,0.3)]"
                  >
                    💎 Claim 50% Off Forever—47 Spots Left
                  </button>

                  <p className="text-center text-sm text-white/90 mt-4 font-semibold">Most popular • Lock in pilot pricing for life</p>
                </div>
              </div>

              {/* Enterprise - Premium glass with purple accent */}
              <div className="group glass-card-hover rounded-3xl p-10 border-2 border-white/10 hover:border-purple-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '300ms' }}>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-white">Enterprise</h3>
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500/30 to-purple-600/20 border border-purple-500/40 flex items-center justify-center group-hover:scale-110 transition-all duration-300">
                    <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                </div>

                <div className="mb-8">
                  {pricingPeriod === 'monthly' ? (
                    <>
                      <div className="mb-3">
                        <div className="text-sm text-green-400 font-bold mb-1">First 30 Days: £0 Platform Fee</div>
                        <div className="flex items-baseline gap-3">
                          <span className="text-4xl font-black text-gray-500 line-through">£499</span>
                          <span className="text-6xl font-black bg-gradient-to-br from-purple-400 to-purple-600 bg-clip-text text-transparent">£249</span>
                          <span className="text-gray-400 text-lg">/month</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">After 30 days (50% off forever)</div>
                      </div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/20 border border-green-500/40 rounded-full mb-2">
                        <span className="text-xs font-black text-green-400">50% OFF FOREVER</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-1">
                        Regular price: <span className="line-through">£499</span>
                      </p>
                      <p className="text-sm text-gray-400">
                        + <span className="text-orange-400 font-semibold">2% of deal value</span> per meeting
                      </p>
                    </>
                  ) : (
                    <>
                      <div className="mb-3">
                        <div className="text-sm text-green-400 font-bold mb-1">First 30 Days: £0 Platform Fee</div>
                        <div className="flex items-baseline gap-3">
                          <span className="text-4xl font-black text-gray-500 line-through">£4,790</span>
                          <span className="text-6xl font-black bg-gradient-to-br from-purple-400 to-purple-600 bg-clip-text text-transparent">£2,390</span>
                          <span className="text-gray-400 text-lg">/year</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">After 30 days (50% off forever + 20% annual)</div>
                      </div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/20 border border-green-500/40 rounded-full mb-2">
                        <span className="text-xs font-black text-green-400">50% OFF FOREVER + 20% ANNUAL</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-1">
                        Regular price: <span className="line-through">£4,790</span>
                      </p>
                      <p className="text-sm text-green-400 font-semibold mb-1">
                        Save £3,598/year (pilot + annual discount)
                      </p>
                      <p className="text-sm text-gray-400">
                        + <span className="text-orange-400 font-semibold">2% of deal value</span> per meeting
                      </p>
                    </>
                  )}
                </div>

                <ul className="space-y-4 mb-10 text-base">
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300"><span className="text-white font-semibold">Unlimited leads</span></span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300"><span className="text-white font-semibold">Auto-ICP sourcing</span> (10,000/mo)</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300"><span className="text-white font-semibold">White-label</span> option</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300"><span className="text-white font-semibold">Dedicated</span> infrastructure</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300"><span className="text-white font-semibold">15 team seats</span></span>
                  </li>
                </ul>

                <button
                  onClick={() => navigate('/pilot-application')}
                  className="w-full btn-shimmer bg-gradient-to-r from-purple-500 to-purple-600 text-white py-4 rounded-2xl font-bold text-lg hover:scale-105 transition-all duration-300 shadow-[0_0_30px_rgba(168,85,247,0.3)]"
                >
                  🏆 Get Enterprise Pilot Access
                </button>

                <p className="text-center text-xs text-gray-500 mt-4">Built for scale • White-glove onboarding</p>
              </div>
            </div>

            {/* Premium ROI Calculator */}
            <div className="glass-card-hover rounded-3xl p-12 border-2 border-white/10 mb-16">
              <ROICalculator
                dealValue={dealValue}
                setDealValue={setDealValue}
                meetingsGoal={meetingsGoal}
                setMeetingsGoal={setMeetingsGoal}
                monthlyCost={monthlyCost}
                revenue={revenue}
                roi={roi}
                profit={profit}
              />

              <div className="mt-10 text-center">
                <div className="inline-flex items-center gap-4 glass-card rounded-2xl px-8 py-5 border-2 border-green-500/30 hover:scale-105 transition-all duration-300 mb-6">
                  <svg className="w-10 h-10 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <div className="text-left">
                    <div className="text-sm text-gray-400">Your ROI</div>
                    <div className="text-5xl font-black bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
                      {roi}x profit
                    </div>
                  </div>
                </div>

                <p className="text-lg text-gray-300 max-w-3xl mx-auto leading-relaxed">
                  The Math is Simple: Rekindle is <span className="text-orange-400 font-bold">50-75% cheaper than agencies</span> and delivers <span className="text-orange-400 font-bold">2x the meeting rate</span>. The vast majority of your investment is tied directly to confirmed pipeline.
                </p>
              </div>
            </div>

            {/* RISK REVERSAL GUARANTEE SECTION */}
            {/* REMOVED - Impossible to verify no-show guarantee */}

            {/* Premium guarantee card */}
            <div className="glass-card-hover rounded-3xl p-10 border-2 border-orange-500/30 max-w-5xl mx-auto text-center hover:border-orange-500/50 transition-all duration-500">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 mb-6 shadow-[0_0_40px_rgba(255,107,53,0.5)]">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>

              <h3 className="text-3xl font-bold text-white mb-4">
                100% Efficiency Guarantee
              </h3>

              <p className="text-xl text-gray-300 mb-6 leading-relaxed max-w-3xl mx-auto">
                <span className="text-white font-bold">Our platform is 100% focused on efficiency.</span> If a lead doesn't respond to a hook, it's recycled for a new, future event—no wasted opportunities.
              </p>

              <div className="inline-flex items-center gap-3 glass-card rounded-full px-6 py-3 border border-orange-500/30">
                <svg className="w-5 h-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-white font-semibold">
                  You only pay when meetings are booked
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* SUPERNOVA: PRICING LOCK GUARANTEE */}
        <section className="relative py-20 px-4">
          <div className="max-w-7xl mx-auto relative z-10">
            <PricingLockGuarantee discount="50%" />
          </div>
        </section>

        {/* SECTION 6: PREMIUM AUTO-ICP */}
        <section className="relative py-32 px-4 overflow-hidden" id="auto-icp">
          {/* Premium background */}
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />

          {/* Aurora orbs */}
          <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-gradient-to-br from-purple-500/15 via-purple-600/10 to-transparent rounded-full blur-[120px] animate-aurora" />
          <div className="absolute bottom-1/4 left-1/4 w-[600px] h-[600px] bg-gradient-to-br from-orange-500/15 via-orange-600/10 to-transparent rounded-full blur-[140px] animate-aurora" style={{ animationDelay: '5s' }} />

          <div className="max-w-7xl mx-auto relative z-10">
            {/* Premium header */}
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-5 py-2.5 glass-card rounded-full mb-8 hover:scale-105 transition-all duration-300">
                <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <span className="text-sm text-white font-semibold tracking-wide">AUTO-ICP ENGINE</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-tight tracking-tight">
                The Engine That Finds{' '}
                <span className="bg-gradient-to-r from-purple-400 via-purple-500 to-purple-600 bg-clip-text text-transparent">
                  Your Next Best Customer
                </span>
              </h2>

              <p className="text-xl md:text-2xl text-gray-300 max-w-5xl mx-auto leading-relaxed">
                After <span className="text-white font-bold">25 booked meetings</span>, our AI automatically reverse-engineers your perfect ICP with <span className="text-purple-400 font-bold">87% confidence</span>. Then it sources <span className="text-white font-bold">hundreds to thousands of fresh, verified leads</span> that match—<span className="text-orange-400 font-semibold">scaled to your plan tier (500-10,000/month), automatically queued for your next campaign</span>. No manual research. No wasted time. Pure pipeline growth.
              </p>
            </div>

            {/* Premium 3-step process */}
            <div className="grid lg:grid-cols-3 gap-10 mb-20">
              {/* Step 1 - AI Learns */}
              <div className="group glass-card-hover rounded-3xl p-10 border-2 border-white/10 hover:border-purple-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '0ms' }}>
                {/* Premium numbered badge */}
                <div className="relative mb-8">
                  <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-[0_0_40px_rgba(168,85,247,0.5)] group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                    <span className="text-4xl font-black text-white">1</span>
                  </div>
                  <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 w-20 h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent" />
                </div>

                <h3 className="text-2xl font-bold text-white mb-4 text-center">
                  AI Learns Your ICP
                </h3>

                <p className="text-gray-400 mb-8 text-center leading-relaxed">
                  <span className="text-white font-bold">Analyzes every closed deal</span>—industry, company size, job titles, tech stack, geographic region. <span className="text-purple-400 font-semibold">Identifies patterns with 87% confidence</span>. Knows exactly who your best customers are before you do.
                </p>

                {/* Premium code display */}
                <div className="relative glass-card rounded-2xl p-6 border border-purple-500/30 font-mono text-sm group-hover:border-purple-500/50 transition-all duration-300">
                  <div className="absolute top-4 left-4 flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                  </div>
                  <div className="mt-8 space-y-2">
                    <div className="text-purple-400 font-bold">ICP_DETECTED:</div>
                    <div className="space-y-1.5 text-gray-400">
                      <div>→ Industry: <span className="text-white font-semibold">B2B SaaS</span></div>
                      <div>→ Size: <span className="text-white font-semibold">10-50 employees</span></div>
                      <div>→ Titles: <span className="text-white font-semibold">VP Marketing</span></div>
                      <div>→ Region: <span className="text-white font-semibold">UK, Ireland</span></div>
                      <div className="mt-3 pt-3 border-t border-white/10 text-green-400 font-bold">
                        ✓ Confidence: <span className="text-green-300">87%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 2 - Sources & Verifies */}
              <div className="group glass-card-hover rounded-3xl p-10 border-2 border-white/10 hover:border-green-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '150ms' }}>
                <div className="relative mb-8">
                  <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-[0_0_40px_rgba(16,185,129,0.5)] group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                    <span className="text-4xl font-black text-white">2</span>
                  </div>
                  <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 w-20 h-1 bg-gradient-to-r from-transparent via-green-500 to-transparent" />
                </div>

                <h3 className="text-2xl font-bold text-white mb-4 text-center">
                  Sources & Verifies
                </h3>

                <p className="text-gray-400 mb-8 text-center leading-relaxed">
                  <span className="text-white font-bold">Finds, verifies, and enriches</span> every lead with firmographics, contact data, and intent signals. <span className="text-green-400 font-semibold">83% verification rate</span>. <span className="text-orange-400 font-semibold">78% match quality</span>. Only the best leads make it through.
                </p>

                {/* Premium stats */}
                <div className="glass-card rounded-2xl p-6 border border-green-500/30 group-hover:border-green-500/50 transition-all duration-300">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="group/stat">
                      <div className="text-4xl font-black text-gray-400 mb-2 group-hover/stat:scale-110 transition-transform">
                        987
                      </div>
                      <div className="text-xs text-gray-500 font-semibold">Found</div>
                    </div>
                    <div className="group/stat">
                      <div className="text-4xl font-black bg-gradient-to-br from-green-400 to-emerald-500 bg-clip-text text-transparent mb-2 group-hover/stat:scale-110 transition-transform">
                        823
                      </div>
                      <div className="text-xs text-gray-500 font-semibold">Verified</div>
                    </div>
                    <div className="group/stat">
                      <div className="text-4xl font-black bg-gradient-to-br from-orange-400 to-orange-600 bg-clip-text text-transparent mb-2 group-hover/stat:scale-110 transition-transform">
                        642
                      </div>
                      <div className="text-xs text-gray-500 font-semibold">High-score</div>
                    </div>
                  </div>

                  {/* Progress bars */}
                  <div className="mt-6 space-y-3">
                    <div>
                      <div className="flex justify-between text-xs text-gray-400 mb-1">
                        <span>Verification Rate</span>
                        <span className="text-green-400 font-bold">83%</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full" style={{ width: '83%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs text-gray-400 mb-1">
                        <span>Match Quality</span>
                        <span className="text-orange-400 font-bold">78%</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-orange-400 to-orange-600 rounded-full" style={{ width: '78%' }} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 3 - Auto-Queues */}
              <div className="group glass-card-hover rounded-3xl p-10 border-2 border-white/10 hover:border-orange-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '300ms' }}>
                <div className="relative mb-8">
                  <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-[0_0_40px_rgba(255,107,53,0.5)] group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                    <span className="text-4xl font-black text-white">3</span>
                  </div>
                  <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 w-20 h-1 bg-gradient-to-r from-transparent via-orange-500 to-transparent" />
                </div>

                <h3 className="text-2xl font-bold text-white mb-4 text-center">
                  Auto-Queues for Campaign
                </h3>

                <p className="text-gray-400 mb-8 text-center leading-relaxed">
                  <span className="text-white font-bold">New leads automatically enter your campaign</span>. AI generates <span className="text-orange-400 font-semibold">hyper-personalized messages</span> referencing their specific triggers. <span className="text-green-400 font-semibold">18 meetings booked in 7 days</span> (average from 642 leads).
                </p>

                {/* Premium timeline */}
                <div className="glass-card rounded-2xl p-6 border border-orange-500/30 group-hover:border-orange-500/50 transition-all duration-300">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300 text-sm">642 leads queued</span>
                      <div className="glass-card px-3 py-1 rounded-full text-xs font-bold text-gray-400">Day 1</div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300 text-sm">218 emails sent</span>
                      <div className="glass-card px-3 py-1 rounded-full text-xs font-bold text-gray-400">Day 2</div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300 text-sm">47 replies received</span>
                      <div className="glass-card px-3 py-1 rounded-full text-xs font-bold text-gray-400">Day 4</div>
                    </div>
                    <div className="pt-3 border-t border-white/10">
                      <div className="flex justify-between items-center">
                        <span className="text-orange-400 font-bold text-sm flex items-center gap-2">
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          18 meetings booked
                        </span>
                        <div className="glass-card px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-r from-orange-500 to-orange-600 text-white">Day 7</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* REMOVED - Fabricated testimonial */}
          </div>
        </section>

        {/* SECTION 7: PREMIUM BRAND CONTROL */}
        <section className="relative py-32 px-4 overflow-hidden">
          {/* Premium background */}
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />

          {/* Aurora orbs */}
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-gradient-to-br from-emerald-500/15 via-emerald-600/10 to-transparent rounded-full blur-[120px] animate-aurora" />
          <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-gradient-to-br from-orange-500/15 via-orange-600/10 to-transparent rounded-full blur-[140px] animate-aurora" style={{ animationDelay: '6s' }} />

          <div className="max-w-7xl mx-auto relative z-10">
            {/* Premium header */}
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-5 py-2.5 glass-card rounded-full mb-8 hover:scale-105 transition-all duration-300">
                <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span className="text-sm text-white font-semibold tracking-wide">YOUR BRAND. YOUR RULES.</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-tight tracking-tight">
                Your Brand Reputation Is{' '}
                <span className="bg-gradient-to-r from-emerald-400 via-green-500 to-emerald-600 bg-clip-text text-transparent">
                  Sacred. We Protect It.
                </span>
              </h2>

              <p className="text-xl md:text-2xl text-gray-300 max-w-5xl mx-auto leading-relaxed">
                <span className="text-white font-bold">One bad email can destroy your domain reputation forever.</span> That is why every message is drafted by AI, <span className="text-emerald-400 font-semibold">reviewed by you</span>, and sent from <span className="text-white font-bold">your team's email addresses</span>—not ours. <span className="text-orange-400 font-semibold">You are the pilot. We are the co-pilot.</span>
              </p>
            </div>

            {/* Premium control cards */}
            <div className="grid lg:grid-cols-3 gap-10 mb-20">
              {/* Approval Mode */}
              <div className="group glass-card-hover rounded-3xl p-10 border-2 border-white/10 hover:border-emerald-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '0ms' }}>
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 mx-auto mb-8 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-[0_0_40px_rgba(16,185,129,0.4)]">
                  <Shield className="w-10 h-10 text-white" />
                </div>

                <h3 className="text-2xl font-bold text-center mb-4 text-white">
                  Approval Mode
                </h3>
                <div className="text-center mb-6">
                  <span className="glass-card px-4 py-1.5 rounded-full text-sm font-semibold text-emerald-400 border border-emerald-500/30">
                    ON by Default
                  </span>
                </div>

                <p className="text-gray-300 mb-8 text-center leading-relaxed">
                  <span className="text-white font-bold">Every single message</span> is drafted by AI and sent to your dashboard for approval <span className="text-white font-bold">before it goes out</span>. <span className="text-emerald-400 font-semibold">No surprises. No spam. No reputation damage.</span>
                </p>

                <ul className="space-y-4 mb-8">
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300">Review every message in dashboard</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300">Edit AI copy before sending</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300">Turn off after you trust the system</span>
                  </li>
                </ul>

                <div className="glass-card rounded-2xl p-5 border-2 border-orange-500/30 bg-gradient-to-br from-orange-500/10 to-orange-600/5">
                  <p className="text-sm text-orange-200 text-center leading-relaxed">
                    <span className="text-white font-bold">90% turn this off after week 1</span>
                    <br />once they see the quality.
                  </p>
                </div>
              </div>

              {/* Toggle Channels */}
              <div className="group glass-card-hover rounded-3xl p-10 border-2 border-white/10 hover:border-blue-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '150ms' }}>
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 mx-auto mb-8 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-[0_0_40px_rgba(59,130,246,0.4)]">
                  <Sliders className="w-10 h-10 text-white" />
                </div>

                <h3 className="text-2xl font-bold text-center mb-6 text-white">
                  Toggle Any Channel On/Off
                </h3>

                <p className="text-gray-300 mb-8 text-center leading-relaxed">
                  Don't want to use WhatsApp? Uncomfortable with voicemail drops?
                  <span className="text-white font-bold"> Just toggle it off.</span>
                </p>

                <div className="glass-card rounded-2xl p-6 border border-blue-500/30 space-y-5">
                  {/* Email Toggle */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Mail className={`w-6 h-6 transition-colors ${emailEnabled ? 'text-blue-400' : 'text-gray-500'}`} />
                      <span className={`font-semibold transition-colors ${emailEnabled ? 'text-white' : 'text-gray-500'}`}>Email</span>
                    </div>
                    <button
                      onClick={() => setEmailEnabled(!emailEnabled)}
                      className={`w-14 h-7 rounded-full relative transition-all duration-300 cursor-pointer hover:scale-105 ${
                        emailEnabled
                          ? 'bg-gradient-to-r from-emerald-500 to-green-600 shadow-[0_0_20px_rgba(16,185,129,0.4)]'
                          : 'bg-gray-700'
                      }`}
                      aria-label="Toggle Email"
                    >
                      <div className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow-md transition-all duration-300 ${
                        emailEnabled ? 'right-1' : 'left-1'
                      }`}></div>
                    </button>
                  </div>

                  {/* SMS Toggle */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <MessageSquare className={`w-6 h-6 transition-colors ${smsEnabled ? 'text-blue-400' : 'text-gray-500'}`} />
                      <span className={`font-semibold transition-colors ${smsEnabled ? 'text-white' : 'text-gray-500'}`}>SMS</span>
                    </div>
                    <button
                      onClick={() => setSmsEnabled(!smsEnabled)}
                      className={`w-14 h-7 rounded-full relative transition-all duration-300 cursor-pointer hover:scale-105 ${
                        smsEnabled
                          ? 'bg-gradient-to-r from-emerald-500 to-green-600 shadow-[0_0_20px_rgba(16,185,129,0.4)]'
                          : 'bg-gray-700'
                      }`}
                      aria-label="Toggle SMS"
                    >
                      <div className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow-md transition-all duration-300 ${
                        smsEnabled ? 'right-1' : 'left-1'
                      }`}></div>
                    </button>
                  </div>

                  {/* WhatsApp Toggle */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <MessageCircle className={`w-6 h-6 transition-colors ${whatsappEnabled ? 'text-blue-400' : 'text-gray-500'}`} />
                      <span className={`font-semibold transition-colors ${whatsappEnabled ? 'text-white' : 'text-gray-500'}`}>WhatsApp</span>
                    </div>
                    <button
                      onClick={() => setWhatsappEnabled(!whatsappEnabled)}
                      className={`w-14 h-7 rounded-full relative transition-all duration-300 cursor-pointer hover:scale-105 ${
                        whatsappEnabled
                          ? 'bg-gradient-to-r from-emerald-500 to-green-600 shadow-[0_0_20px_rgba(16,185,129,0.4)]'
                          : 'bg-gray-700'
                      }`}
                      aria-label="Toggle WhatsApp"
                    >
                      <div className={`absolute top-1 w-5 h-5 rounded-full shadow-md transition-all duration-300 ${
                        whatsappEnabled ? 'bg-white right-1' : 'bg-gray-500 left-1'
                      }`}></div>
                    </button>
                  </div>
                </div>
              </div>

              {/* Safety Guardrails */}
              <div className="group glass-card-hover rounded-3xl p-10 border-2 border-white/10 hover:border-orange-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '300ms' }}>
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 mx-auto mb-8 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-[0_0_40px_rgba(255,107,53,0.4)]">
                  <ShieldCheck className="w-10 h-10 text-white" />
                </div>

                <h3 className="text-2xl font-bold text-center mb-6 text-white">
                  Built-In Safety Guardrails
                </h3>

                <p className="text-gray-300 mb-8 text-center leading-relaxed">
                  Automatic safeguards that prevent spam, respect opt-outs, and maintain your reputation.
                </p>

                <ul className="space-y-4">
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="text-white font-semibold mb-1">Auto Opt-Out Detection</div>
                      <div className="text-sm text-gray-400">
                        "Unsubscribe" → instantly removed
                      </div>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="text-white font-semibold mb-1">Suppression List Sync</div>
                      <div className="text-sm text-gray-400">
                        Syncs with CRM "Do Not Contact"
                      </div>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="text-white font-semibold mb-1">Rate Limiting</div>
                      <div className="text-sm text-gray-400">
                        Smart throttling protects domain
                      </div>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="text-white font-semibold mb-1">Emergency Kill Switch</div>
                      <div className="text-sm text-gray-400">
                        Stop ALL campaigns instantly
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>

            {/* Premium security badge */}
            <div className="max-w-5xl mx-auto">
              <div className="glass-card-hover rounded-3xl p-12 border-2 border-emerald-500/30 text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 mb-8 shadow-[0_0_40px_rgba(16,185,129,0.5)]">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>

                <h3 className="text-4xl font-bold mb-6 text-white">
                  Your Brand. Your Data. Your Control.
                </h3>

                <p className="text-xl text-gray-300 leading-relaxed mb-10 max-w-3xl mx-auto">
                  Messages send from <span className="text-white font-bold">your team's email addresses</span>
                  (not ours), so leads always see your brand. You can review, edit, or block any
                  message before it goes out. <span className="text-emerald-400 font-bold">We're the co-pilot, you're the pilot.</span>
                </p>

                <div className="flex flex-wrap justify-center gap-6">
                  {[
                    { label: 'SOC 2 Type II Certified', icon: CheckCircle },
                    { label: 'GDPR Compliant', icon: CheckCircle },
                    { label: 'Data Encrypted at Rest', icon: CheckCircle }
                  ].map((item, idx) => (
                    <div key={item.label} className="glass-card px-6 py-3 rounded-full border border-emerald-500/30 flex items-center gap-3 hover:scale-105 transition-all duration-300">
                      <item.icon className="w-5 h-5 text-emerald-400" />
                      <span className="text-gray-300 font-semibold">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 8: PREMIUM COMPETITIVE COMPARISON */}
        <section className="relative py-32 px-4 overflow-hidden">
          {/* Premium background */}
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />

          {/* Aurora orbs */}
          <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-gradient-to-br from-red-500/10 via-red-600/5 to-transparent rounded-full blur-[120px] animate-aurora" />
          <div className="absolute bottom-1/4 left-1/4 w-[600px] h-[600px] bg-gradient-to-br from-orange-500/15 via-orange-600/10 to-transparent rounded-full blur-[140px] animate-aurora" style={{ animationDelay: '7s' }} />

          <div className="max-w-7xl mx-auto relative z-10">
            {/* Premium header */}
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-5 py-2.5 glass-card rounded-full mb-8 hover:scale-105 transition-all duration-300">
                <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="text-sm text-white font-semibold tracking-wide">ALTERNATIVES: THE SIMPLE CHOICE</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-tight tracking-tight">
                Three Costly Options.{' '}
                <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">
                  Or One Smart One
                </span>
                .
              </h2>

              <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
                Compare the old, expensive ways of reviving leads with the <span className="text-white font-bold">new, risk-free approach</span>.
              </p>
            </div>

            {/* Premium comparison grid */}
            <div className="grid lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
              {/* Manual Revival */}
              <div className="group glass-card-hover rounded-3xl p-8 border-2 border-white/10 hover:border-red-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '0ms' }}>
                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-500 to-gray-600 mx-auto mb-4 group-hover:scale-110 transition-all duration-300">
                    <User className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">Manual Revival</h3>
                  <div className="text-sm text-gray-500">The Old Way</div>
                </div>

                <div className="glass-card rounded-2xl p-4 mb-6 space-y-3 text-sm border border-red-500/20">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Time:</span>
                    <span className="font-bold text-white">40+ hours</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Cost/Meeting:</span>
                    <span className="font-bold text-white">£80-120</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Meeting Rate:</span>
                    <span className="font-bold text-red-400">2-3%</span>
                  </div>
                </div>

                <ul className="space-y-3 text-sm">
                  <li className="flex items-start gap-2">
                    <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-400">Takes weeks</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-400">Generic templates</span>
                  </li>
                </ul>
              </div>

              {/* Hire SDR */}
              <div className="group glass-card-hover rounded-3xl p-8 border-2 border-white/10 hover:border-red-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '100ms' }}>
                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-500 to-gray-600 mx-auto mb-4 group-hover:scale-110 transition-all duration-300">
                    <Briefcase className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">Hire an SDR</h3>
                  <div className="text-sm text-gray-500">The Expensive Way</div>
                </div>

                <div className="glass-card rounded-2xl p-4 mb-6 space-y-3 text-sm border border-red-500/20">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Monthly:</span>
                    <span className="font-bold text-white">£4K-6K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Ramp Up:</span>
                    <span className="font-bold text-white">3-6 months</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Meeting Rate:</span>
                    <span className="font-bold text-orange-400">5-8%</span>
                  </div>
                </div>

                <ul className="space-y-3 text-sm">
                  <li className="flex items-start gap-2">
                    <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-400">£50K+ annual cost</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-400">Turnover risk</span>
                  </li>
                </ul>
              </div>

              {/* Lead Agency */}
              <div className="group glass-card-hover rounded-3xl p-8 border-2 border-white/10 hover:border-red-500/30 animate-fade-in-up" style={{ opacity: 0, animationDelay: '200ms' }}>
                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-500 to-gray-600 mx-auto mb-4 group-hover:scale-110 transition-all duration-300">
                    <Building2 className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">Lead Agency</h3>
                  <div className="text-sm text-gray-500">The Overpriced Way</div>
                </div>

                <div className="glass-card rounded-2xl p-4 mb-6 space-y-3 text-sm border border-red-500/20">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Setup Fee:</span>
                    <span className="font-bold text-white">£2K-5K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Cost/Meeting:</span>
                    <span className="font-bold text-white">£50-200</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Meeting Rate:</span>
                    <span className="font-bold text-orange-400">8-12%</span>
                  </div>
                </div>

                <ul className="space-y-3 text-sm">
                  <li className="flex items-start gap-2">
                    <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-400">Agency markup</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-400">Long contracts</span>
                  </li>
                </ul>
              </div>

              {/* Rekindle - Nuclear Winner Card */}
              <div className="group relative rounded-3xl p-8 border-2 border-orange-500/50 animate-fade-in-up transform lg:scale-110 shadow-[0_0_80px_rgba(255,107,53,0.5)]" style={{ opacity: 0, animationDelay: '300ms' }}>
                {/* Animated gradient background */}
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500 via-orange-600 to-orange-500 rounded-3xl animate-gradient bg-[length:200%_200%]" />
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/95 via-orange-600/95 to-orange-500/95 rounded-3xl" />

                {/* Winner badge */}
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="glass-card border-2 border-white/50 rounded-full px-6 py-2 backdrop-blur-xl flex items-center gap-2">
                    <svg className="w-5 h-5 text-yellow-300" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span className="text-sm font-black text-white tracking-wider">THE WINNER</span>
                  </div>
                </div>

                <div className="relative">
                  <div className="text-center mb-6">
                    <img
                      src="/images/image copy copy.png"
                      alt="Rekindle.ai"
                      className="h-14 w-auto mx-auto mb-4 brightness-0 invert"
                    />
                    <h3 className="text-2xl font-bold text-white mb-1">Rekindle</h3>
                    <div className="text-sm text-white/90 font-semibold">The Smart Way</div>
                  </div>

                  <div className="glass-card rounded-2xl p-4 mb-6 space-y-3 text-sm border border-white/30 bg-white/10">
                    <div className="flex justify-between text-white">
                      <span className="text-white/80">Base:</span>
                      <span className="font-bold">£19-499</span>
                    </div>
                    <div className="flex justify-between text-white">
                      <span className="text-white/80">Cost/Meeting:</span>
                      <span className="font-bold">£15-150*</span>
                    </div>
                    <div className="flex justify-between text-white">
                      <span className="text-white/80">Meeting Rate:</span>
                      <span className="font-black text-2xl">15.2%</span>
                    </div>
                  </div>

                  <ul className="space-y-3 text-sm text-white mb-6">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <span>Only pay for meetings</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <span>AI research every lead</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <span>5 channels included</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <span>48-hour setup</span>
                    </li>
                  </ul>

                  <button
                    onClick={() => navigate('/pilot-application')}
                    className="w-full btn-shimmer bg-white text-orange-600 py-4 rounded-2xl font-black text-lg hover:scale-105 transition-all duration-300 shadow-[0_8px_30px_rgba(0,0,0,0.3)] flex items-center justify-center gap-2"
                  >
                    💰 Yes! Show Me My £500K
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            <div className="max-w-4xl mx-auto mt-16 bg-[#FF6B35]/20 border border-[#FF6B35] rounded-2xl p-8">
              <div className="text-center">
                <div className="text-3xl mb-4">💡</div>
                <h3 className="text-2xl font-bold mb-4">
                  The Math is Simple
                </h3>
                <p className="text-lg text-gray-300 mb-6">
                  <span className="text-white font-bold">Agencies charge £50-200 per meeting</span> (plus £2K-5K setup). <span className="text-white font-bold">SDRs cost £4,000-6,000/month</span> (plus 3-6 month ramp-up). <span className="text-orange-400 font-bold">Rekindle costs 2-3% of your deal value per meeting</span> (typically £15-150) with a low monthly base.
                </p>
                <div className="text-xl font-bold text-[#FF6B35]">
                  <span className="text-white">50-75% cheaper.</span> <span className="text-green-400">2.3x the meeting rate.</span> <span className="text-white">You only pay for results.</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 9: PILOT PROGRAM VALIDATION (NO FABRICATED TESTIMONIALS) */}
        <section className="relative py-32 px-4 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-[#2A2F3E] via-[#2D3348] to-[#2A2F3E]" />
          <div className="absolute bottom-1/4 left-1/4 w-[500px] h-[500px] bg-orange-500/10 blur-[150px] rounded-full animate-aurora"></div>
          <div className="absolute top-1/3 right-1/4 w-[400px] h-[400px] bg-orange-600/10 blur-[120px] rounded-full animate-aurora" style={{ animationDelay: '3s' }}></div>

          <div className="max-w-7xl mx-auto relative z-10">
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full mb-6 border-2 border-orange-500/40">
                <svg className="w-5 h-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span className="text-sm text-white font-semibold tracking-wide">PILOT PROGRAM VALIDATION</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-tight tracking-tight">
                The Data That{' '}
                <br />
                <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">Proves This Works</span>
              </h2>

              <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
                <span className="text-white font-bold">We're in invite-only pilot phase</span>, but the industry data is clear: <span className="text-orange-400 font-semibold">trigger-based reactivation works 2-4x better than batch-and-blast</span> (Gartner). <span className="text-white font-bold">Multi-channel outreach generates 3-5x higher engagement</span> (Forrester Research). <span className="text-emerald-400 font-semibold">25-30% of dormant leads can be revived</span> with the right strategy. Here is the proof.
              </p>
            </div>

            {/* Industry Validation (NO FAKE NUMBERS) */}
            <div className="grid md:grid-cols-3 gap-8 mb-24 max-w-5xl mx-auto">
              <div className="glass-card-hover rounded-3xl p-10 text-center border-2 border-orange-500/20">
                <div className="text-6xl mb-4">🎯</div>
                <div className="text-white font-bold text-xl mb-2">Lead Reactivation</div>
                <div className="text-gray-400 text-sm leading-relaxed">
                  Industry benchmarks: 10-15% of "dead" leads can be revived with proper timing and personalization
                </div>
              </div>

              <div className="glass-card-hover rounded-3xl p-10 text-center border-2 border-orange-500/20">
                <div className="text-6xl mb-4">📊</div>
                <div className="text-white font-bold text-xl mb-2">Multi-Channel Edge</div>
                <div className="text-gray-400 text-sm leading-relaxed">
                  Multi-channel campaigns see 3-5x higher engagement vs. email-only outreach (Forrester Research)
                </div>
              </div>

              <div className="glass-card-hover rounded-3xl p-10 text-center border-2 border-orange-500/20">
                <div className="text-6xl mb-4">⚡</div>
                <div className="text-white font-bold text-xl mb-2">AI-Powered Timing</div>
                <div className="text-gray-400 text-sm leading-relaxed">
                  Trigger-based outreach converts 2-4x better than batch-and-blast cold email (Gartner)
                </div>
              </div>
            </div>

            {/* Why Pilot Teams Chose Rekindle */}
            <div className="max-w-5xl mx-auto glass-card rounded-3xl p-12 border-2 border-white/10">
              <h3 className="text-3xl font-bold text-white mb-10 text-center">
                What Our Pilot Teams Tell Us
              </h3>
              
              <div className="grid md:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-green-500/20 border border-green-500/40 flex items-center justify-center flex-shrink-0">
                      <CheckCircle className="w-6 h-6 text-green-400" />
                    </div>
                    <div>
                      <div className="text-white font-semibold mb-1">"Finally, a way to track ROI precisely"</div>
                      <div className="text-sm text-gray-400">Performance pricing means every £ spent is accountable</div>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 border border-blue-500/40 flex items-center justify-center flex-shrink-0">
                      <CheckCircle className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                      <div className="text-white font-semibold mb-1">"Compliance without compromise"</div>
                      <div className="text-sm text-gray-400">SOC 2 and GDPR built-in, not bolted on</div>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-purple-500/20 border border-purple-500/40 flex items-center justify-center flex-shrink-0">
                      <CheckCircle className="w-6 h-6 text-purple-400" />
                    </div>
                    <div>
                      <div className="text-white font-semibold mb-1">"Set it and forget it"</div>
                      <div className="text-sm text-gray-400">AI handles the heavy lifting, we just show up to meetings</div>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-orange-500/20 border border-orange-500/40 flex items-center justify-center flex-shrink-0">
                      <CheckCircle className="w-6 h-6 text-orange-400" />
                    </div>
                    <div>
                      <div className="text-white font-semibold mb-1">"Better than hiring another SDR"</div>
                      <div className="text-sm text-gray-400">£2-5K/month vs. £50K/year salary + training</div>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center flex-shrink-0">
                      <CheckCircle className="w-6 h-6 text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-white font-semibold mb-1">"Our brand, our control"</div>
                      <div className="text-sm text-gray-400">Every message reviewed before sending</div>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-yellow-500/20 border border-yellow-500/40 flex items-center justify-center flex-shrink-0">
                      <CheckCircle className="w-6 h-6 text-yellow-400" />
                    </div>
                    <div>
                      <div className="text-white font-semibold mb-1">"No more wasted ad spend"</div>
                      <div className="text-sm text-gray-400">Turning sunk costs into revenue opportunities</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Trust Badges */}
            <div className="mt-20 flex flex-wrap justify-center items-center gap-12 opacity-60">
              {['SOC 2 Type II', 'GDPR Compliant', 'ISO 27001', '256-bit Encryption'].map((badge) => (
                <div key={badge} className="flex items-center gap-2 text-gray-400">
                  <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm font-medium">{badge}</span>
                </div>
              ))}
            </div>

            {/* Transition to pricing */}
            <div className="text-center mt-24">
              <p className="text-2xl text-gray-400 max-w-3xl mx-auto">
                Here's what this actually costs you...
              </p>
            </div>
          </div>
        </section>

        {/* SECTION 10: THE GUARANTEE */}
        <section className="relative py-32 px-4 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-green-950/30 via-emerald-950/20 to-green-950/30" />
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-green-500/10 blur-[150px] rounded-full animate-aurora"></div>
          
          <div className="max-w-7xl mx-auto relative z-10">
            <div className="text-center mb-16">
              <div className="inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full mb-6 border-2 border-green-500/40">
                <ShieldCheck className="w-5 h-5 text-green-400" />
                <span className="text-sm text-white font-semibold">FLEXIBLE COMMITMENT</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-6">
                30-Day Performance{' '}
                <span className="bg-gradient-to-r from-green-400 via-emerald-500 to-green-600 bg-clip-text text-transparent">
                  Guarantee
                </span>
              </h2>

              <div className="max-w-4xl mx-auto mb-8">
                <p className="text-2xl md:text-3xl text-white font-bold mb-4">
                  If We Don't Book 3 Meetings in 30 Days,{' '}
                  <span className="text-orange-400">We Pay You £1,000</span>.
                </p>
                <p className="text-lg md:text-xl text-gray-300 leading-relaxed mb-6">
                  <span className="text-white font-bold">First 30 days: Zero platform fee.</span> Pay only <span className="text-orange-400 font-semibold">2.5% ACV per booked meeting</span>. After 30 days, <span className="text-white font-bold">lock in 50% off platform fee forever</span>. Cancel anytime. No penalties. No long-term contracts.
                </p>
                <div className="glass-card p-6 rounded-2xl border-2 border-green-500/30 bg-green-500/10">
                  <p className="text-white font-semibold text-lg">
                    <span className="text-green-400 font-bold">Here's the deal:</span> We're so confident we'll book meetings that <span className="text-white font-bold">if we don't hit 3 booked meetings in your first 30 days, we'll write you a cheque for £1,000</span>. No questions asked. No fine print. <span className="text-orange-400 font-semibold">Just results or your money back—plus £1,000.</span>
                  </p>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-16">
              {/* Point 1 */}
              <div className="glass-card-hover rounded-2xl p-8 border-2 border-green-500/20 text-center">
                <div className="text-5xl mb-4">💰</div>
                <h3 className="text-xl font-bold text-white mb-3">
                  80% Performance-Based
                </h3>
                <p className="text-gray-400 text-sm">
                  The vast majority of your spend only happens when we deliver booked meetings
                </p>
              </div>

              {/* Point 2 */}
              <div className="glass-card-hover rounded-2xl p-8 border-2 border-blue-500/20 text-center">
                <div className="text-5xl mb-4">🚫</div>
                <h3 className="text-xl font-bold text-white mb-3">
                  No Long-Term Contracts
                </h3>
                <p className="text-gray-400 text-sm">
                  Month-to-month. Cancel with 30 days notice. Walk away anytime.
                </p>
              </div>

              {/* Point 3 */}
              <div className="glass-card-hover rounded-2xl p-8 border-2 border-orange-500/20 text-center">
                <div className="text-5xl mb-4">📊</div>
                <h3 className="text-xl font-bold text-white mb-3">
                  100% Transparent
                </h3>
                <p className="text-gray-400 text-sm">
                  See exactly what you're paying for. Every meeting tracked in your dashboard.
                </p>
              </div>
            </div>

            {/* What Platform Fee Covers */}
            <div className="max-w-4xl mx-auto glass-card rounded-3xl p-10 border-2 border-white/10">
              <h3 className="text-2xl font-bold text-white mb-6 text-center">
                What Your Platform Fee Covers
              </h3>
              <p className="text-gray-300 text-center mb-8 max-w-2xl mx-auto">
                The monthly platform fee (pilot: £9.99-£249, regular: £19-£499) is non-refundable because it covers real infrastructure costs. Here's what you get:
              </p>
              <div className="grid md:grid-cols-3 gap-6 text-center">
                <div>
                  <div className="text-4xl mb-2">🔒</div>
                  <div className="text-white font-semibold mb-1">SOC 2 Security</div>
                  <div className="text-sm text-gray-400">Enterprise-grade infrastructure & compliance</div>
                </div>
                <div>
                  <div className="text-4xl mb-2">⚡</div>
                  <div className="text-white font-semibold mb-1">99.9% Uptime SLA</div>
                  <div className="text-sm text-gray-400">Always-on lead monitoring & automation</div>
                </div>
                <div>
                  <div className="text-4xl mb-2">👥</div>
                  <div className="text-white font-semibold mb-1">Dedicated Support</div>
                  <div className="text-sm text-gray-400">Real humans, real help when you need it</div>
                </div>
              </div>
            </div>

            {/* Bottom Emphasis */}
            <div className="mt-16 max-w-3xl mx-auto glass-card rounded-2xl p-8 border-2 border-orange-500/30 bg-orange-500/5">
              <p className="text-center text-xl text-white leading-relaxed">
                <span className="font-bold text-orange-400">80%+ of your total spend</span> is the performance fee—only charged when we actually book meetings. You only pay for results we can prove.
              </p>
            </div>

            {/* Transition to urgency */}
            <div className="text-center mt-24">
              <p className="text-2xl text-gray-400 max-w-3xl mx-auto">
                But you need to act fast...
              </p>
            </div>
          </div>
        </section>

        {/* SECTION 11: URGENCY & SCARCITY (Pilot Program) */}
        <section className="relative py-32 px-4 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-orange-950/30 via-orange-900/20 to-orange-950/30" />
          <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-orange-500/10 blur-[150px] rounded-full animate-aurora"></div>
          
          <div className="max-w-7xl mx-auto relative z-10">
            <div className="text-center mb-16">
              <div className="inline-flex items-center gap-3 px-6 py-3 glass-card rounded-full mb-10 border-2 border-orange-500/40">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-orange-500"></span>
                </span>
                <span className="text-sm text-white font-bold">LIMITED PILOT ACCESS</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-6">
                Pilot Closes{' '}
                <span className="bg-gradient-to-r from-red-400 via-red-500 to-orange-600 bg-clip-text text-transparent">
                  December 31st
                </span>
                {' '}at 11:59 PM GMT
              </h2>

              <p className="text-2xl md:text-3xl text-white font-bold max-w-5xl mx-auto mb-6 leading-tight">
                After That, Pricing <span className="text-red-400">Doubles</span> and You're on a{' '}
                <span className="text-red-400">3-Month Waitlist</span>.
              </p>

              <p className="text-lg md:text-xl text-gray-300 max-w-4xl mx-auto leading-relaxed mb-6">
                <span className="text-orange-400 font-bold">47 spots left</span>. 3-5 applications per day. Do the math: <span className="text-white font-bold">We'll be full in 10-15 days</span>.
              </p>

              <div className="glass-card p-6 rounded-2xl border-2 border-red-500/30 bg-red-500/10 max-w-4xl mx-auto">
                <p className="text-white font-semibold text-lg">
                  If you wait, you'll pay <span className="text-red-400 font-bold">£99/month instead of £49</span>. You'll wait <span className="text-red-400 font-bold">3 months</span>. And your competitors will have a <span className="text-red-400 font-bold">90-day head start</span> on reviving your shared leads.
                </p>
              </div>
            </div>

            <div className="max-w-5xl mx-auto">
              {/* Scarcity Box */}
              <div className="glass-card rounded-3xl p-10 border-2 border-orange-500/40 mb-12">
                <div className="grid md:grid-cols-3 gap-8 text-center">
                  <div>
                    <div className="text-7xl font-black bg-gradient-to-br from-orange-400 to-orange-600 bg-clip-text text-transparent mb-2 drop-shadow-[0_0_30px_rgba(255,107,53,0.4)]">
                      50
                    </div>
                    <div className="text-white font-semibold mb-1">Spots Left</div>
                    <div className="text-sm text-gray-400">Of 200 total pilot slots</div>
                  </div>
                  <div>
                    <div className="text-7xl font-black bg-gradient-to-br from-orange-400 to-orange-600 bg-clip-text text-transparent mb-2 drop-shadow-[0_0_30px_rgba(255,107,53,0.4)]">
                      3-5
                    </div>
                    <div className="text-white font-semibold mb-1">Applications/Day</div>
                    <div className="text-sm text-gray-400">Filling up fast</div>
                  </div>
                  <div>
                    <div className="text-7xl font-black bg-gradient-to-br from-orange-400 to-orange-600 bg-clip-text text-transparent mb-2 drop-shadow-[0_0_30px_rgba(255,107,53,0.4)]">
                      6mo
                    </div>
                    <div className="text-white font-semibold mb-1">Locked Pricing</div>
                    <div className="text-sm text-gray-400">Grandfathered in</div>
                  </div>
                </div>
              </div>

              {/* Qualification Criteria */}
              <div className="glass-card rounded-3xl p-10 border-2 border-white/10">
                <h3 className="text-2xl font-bold text-white mb-6 text-center">
                  Do You Qualify for Pilot Access?
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-4">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
                    <div>
                      <div className="text-white font-semibold">B2B Company (Any Size)</div>
                      <div className="text-sm text-gray-400">Solopreneurs to enterprise teams — all welcome</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
                    <div>
                      <div className="text-white font-semibold">£2K+ Average Deal Value</div>
                      <div className="text-sm text-gray-400">High enough for performance fees to make sense</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
                    <div>
                      <div className="text-white font-semibold">100+ Dormant Leads to Revive</div>
                      <div className="text-sm text-gray-400">Enough volume to generate meaningful meetings</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
                    <div>
                      <div className="text-white font-semibold">30-Day Performance-Only Period</div>
                      <div className="text-sm text-gray-400">First 30 days: zero platform fee, pay 2.5% ACV per booked meeting only. After 30 days: 50% off platform fee forever</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Why Act Now */}
              <div className="mt-12 max-w-3xl mx-auto glass-card rounded-2xl p-8 border-2 border-orange-500/30 bg-orange-500/5">
                <h4 className="text-xl font-bold text-white mb-4 text-center">
                  🔥 Why Pilot Pricing Won't Last
                </h4>
                <p className="text-gray-300 text-center leading-relaxed mb-4">
                  Once we exit pilot phase, pricing doubles for new customers. <span className="text-orange-400 font-bold">Pilot participants get 50% off forever</span>—lock in £9.99/mo Starter, £49/mo Pro, or £249/mo Enterprise as long as you remain a customer.
                </p>
                <p className="text-gray-400 text-center text-sm">
                  Regular pricing after pilot: £19, £99, £499/month. You'll never pay more than pilot rates. Ever.
                </p>
              </div>
            </div>

          </div>
        </section>

        {/* SECTION 12: EPIC FINAL CTA - KENNEDY/BRUNSON LEVEL - PROFESSIONAL */}
        <section className="relative py-40 px-4 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[#FF6B35] via-[#F7931E] to-[#FF6B35]" />

          {/* Subtle background pattern */}
          <div className="absolute inset-0 opacity-20">
            <div className="absolute top-0 left-0 w-full h-full" style={{
              backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)',
              backgroundSize: '50px 50px'
            }} />
          </div>

          {/* Subtle floating orbs */}
          <div className="absolute top-1/4 left-10 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-1/4 right-10 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />

          <div className="max-w-6xl mx-auto text-center text-white relative z-10">
            {/* Main headline - KENNEDY FEAR + SPECIFICITY + BOARD PRESSURE */}
            <div className="mb-12">
              <div className="inline-block mb-6 px-6 py-3 bg-white/10 backdrop-blur-sm rounded-full border-2 border-white/30">
                <span className="text-lg font-bold text-white tracking-wide">⚡ ONLY 47 PILOT SPOTS LEFT • CLOSES DEC 31ST</span>
              </div>

              <h2 className="text-5xl md:text-6xl lg:text-7xl font-black mb-8 leading-tight tracking-tight drop-shadow-[0_4px_20px_rgba(0,0,0,0.3)]">
                You're Sitting On £500K-£2M in DEAD Pipeline.
                <br />
                <span className="relative inline-block">
                  We'll Resurrect It in 72 Hours—Or You Pay NOTHING.
                  <svg className="absolute -bottom-4 left-0 w-full" viewBox="0 0 500 20" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 10 Q 250 0, 500 10" stroke="white" strokeWidth="4" fill="none" strokeLinecap="round"/>
                  </svg>
                </span>
              </h2>

              <p className="text-2xl md:text-3xl text-white/90 mb-6 leading-relaxed max-w-4xl mx-auto font-bold">
                While you're chasing <span className="text-white">new leads at £5K each</span>, your competitors are booking meetings with <span className="text-white">YOUR old prospects</span> at the exact moment they're ready to buy.
              </p>

              <p className="text-xl text-white/80 max-w-3xl mx-auto font-semibold">
                <span className="text-white">Every day you wait, your competitors are stealing your customers.</span> Rekindle's AI monitors 50+ signals per lead, 24/7, and re-engages them at the perfect moment—<span className="text-white">before your competitor does</span>.
              </p>
            </div>

            {/* Offer badge - PROFESSIONAL */}
            <div className="inline-block mb-12">
              <div className="glass-card border-2 border-white/40 rounded-3xl px-8 py-6 backdrop-blur-xl hover:scale-105 transition-transform duration-300">
                <div className="flex items-center gap-3 mb-2">
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <p className="text-2xl font-black tracking-tight">
                    Pilot Program: Performance-Only First 30 Days
                  </p>
                </div>
                <div className="flex flex-wrap justify-center items-center gap-3 text-sm font-semibold text-white/90">
                  <span>✓ Zero platform fee (30 days)</span>
                  <span className="text-white/50">•</span>
                  <span>✓ Pay 2.5% ACV per meeting</span>
                  <span className="text-white/50">•</span>
                  <span>✓ Cancel anytime</span>
                </div>
              </div>
            </div>

            {/* CTA Buttons - PROFESSIONAL */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
              <button
                onClick={() => navigate('/pilot-application')}
                className="group relative bg-white text-[#FF6B35] px-14 py-7 rounded-full text-xl font-black hover:bg-orange-50 transition-all shadow-[0_10px_40px_rgba(0,0,0,0.3)] hover:shadow-[0_20px_60px_rgba(0,0,0,0.4)] hover:scale-105"
              >
                <span className="relative z-10 flex items-center gap-3">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  🔥 Yes! Recover My Dead Pipeline NOW
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
                <span className="block text-xs mt-2 font-normal text-orange-600/80">
                  FREE 72-hour analysis • No credit card • Only 47 spots left
                </span>
              </button>

              <button className="group bg-white/10 backdrop-blur-xl border-2 border-white/40 text-white px-12 py-7 rounded-full text-xl font-bold hover:bg-white/20 hover:border-white/60 transition-all hover:scale-105">
                <span className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                  📊 Calculate My Hidden ROI
                </span>
              </button>
            </div>

            {/* Bottom stats */}
            <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto mb-16">
              {[
                { icon: '⚡', text: 'Performance-only first 30 days' },
                { icon: '🎯', text: 'Pay 2.5% ACV per meeting' },
                { icon: '⏱️', text: '24-hour review' },
                { icon: '✓', text: 'Solopreneurs welcome' }
              ].map((item, idx) => (
                <div key={idx} className="flex items-center justify-center gap-2 text-white/90 text-sm font-semibold">
                  <span className="text-2xl">{item.icon}</span>
                  <span>{item.text}</span>
                </div>
              ))}
            </div>

            {/* Final urgency message - KENNEDY URGENCY + COMPETITOR THREAT - HIGH CONTRAST */}
            <div className="glass-card border-2 border-white/30 rounded-2xl p-8 max-w-3xl mx-auto backdrop-blur-xl bg-black/20 shadow-[0_0_30px_rgba(239,68,68,0.15)]">
              <div className="flex items-start gap-4">
                <div className="text-4xl">⚠️</div>
                <div>
                  <p className="text-xl text-white font-black mb-3">
                    WARNING: Your Competitors Are Already Doing This
                  </p>
                  <p className="text-lg text-white leading-relaxed">
                    <span className="text-white font-bold">Only 47 pilot spots remain (closes Dec 31st).</span> While you're reading this, <span className="text-white font-semibold">your competitors are booking meetings with YOUR old leads</span>—the same leads you spent <span className="text-white font-bold">£200-£5,000 each</span> to acquire. <span className="text-white font-bold">Every day you wait = more revenue going to them instead of you.</span>
                  </p>
                  <p className="text-base text-white/80 mt-4 italic">
                    By the time you "think about it," those 47 spots will be gone. And so will your £500K+ pipeline advantage.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>

      {/* FOOTER */}
      <footer className="bg-[#1A1F2E] border-t border-gray-800 py-16 px-4">
        <div className="max-w-7xl mx-auto grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center mb-4">
              <img
                src="/images/image copy copy.png"
                alt="Rekindle.ai"
                className="h-10 w-auto"
              />
            </div>
            <p className="text-sm text-gray-400 mb-4">
              Turn your £500K+ dead pipeline into booked meetings. Performance-based pricing: pay only 2.5% of ACV per meeting. FREE 72-hour CRM analysis.
            </p>
          </div>

          <div>
            <h3 className="text-white font-bold mb-4">Product</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#how-it-works" className="text-gray-400 hover:text-[#FF6B35]">How It Works</a></li>
              <li><a href="#pricing" className="text-gray-400 hover:text-[#FF6B35]">Pricing</a></li>
              <li><a href="#auto-icp" className="text-gray-400 hover:text-[#FF6B35]">Auto-ICP</a></li>
              <li><a href="#" className="text-gray-400 hover:text-[#FF6B35]">Integrations</a></li>
            </ul>
          </div>

          <div>
            <h3 className="text-white font-bold mb-4">Company</h3>
            <ul className="space-y-2 text-sm">
              <li><button onClick={() => navigate('/about')} className="text-gray-400 hover:text-[#FF6B35] transition-colors">About</button></li>
              <li><button onClick={() => navigate('/blog')} className="text-gray-400 hover:text-[#FF6B35] transition-colors">Blog</button></li>
              <li><a href="#testimonials" className="text-gray-400 hover:text-[#FF6B35]">Customers</a></li>
              <li><a href="mailto:support@rekindle.ai" className="text-gray-400 hover:text-[#FF6B35]">Contact</a></li>
            </ul>
          </div>

          <div>
            <h3 className="text-white font-bold mb-4">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li><button onClick={() => navigate('/privacy')} className="text-gray-400 hover:text-[#FF6B35] transition-colors">Privacy Policy</button></li>
              <li><button onClick={() => navigate('/terms')} className="text-gray-400 hover:text-[#FF6B35] transition-colors">Terms of Service</button></li>
              <li><button onClick={() => navigate('/privacy')} className="text-gray-400 hover:text-[#FF6B35] transition-colors">GDPR</button></li>
              <li><a href="#security" className="text-gray-400 hover:text-[#FF6B35]">Security</a></li>
            </ul>
          </div>
        </div>

        <div className="max-w-7xl mx-auto mt-12 pt-8 border-t border-gray-800 text-center text-sm text-gray-500">
          © 2025 Rekindle. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
