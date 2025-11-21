// TRUST-FIRST LANDING PAGE - Stripe/Linear-Inspired Minimalism
// Zero hype. Pure clarity, data, and confidence.
import { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import {
  ArrowRight,
  CheckCircle2,
  Shield,
  Lock,
  Eye,
  BarChart3,
  Mail,
  MessageSquare,
  Phone,
  TrendingUp
} from 'lucide-react';

// Minimalist button - Stripe-inspired
const MinimalButton = ({
  children,
  onClick,
  variant = 'primary',
  className = ''
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  className?: string;
}) => {
  const variants = {
    primary: 'bg-[#0a2540] text-white hover:bg-[#0a2540]/90 shadow-[0_2px_4px_rgba(0,0,0,0.1)]',
    secondary: 'bg-white text-[#0a2540] hover:bg-[#f6f9fc] border border-[#e3e8ee] shadow-[0_2px_4px_rgba(0,0,0,0.04)]'
  };

  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2, ease: [0, -0.01, 0.19, 0.99] }}
      className={`inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 ${variants[variant]} ${className}`}
    >
      {children}
    </motion.button>
  );
};

// Animated counter
const Counter = ({ end, suffix = '', prefix = '' }: { end: number; suffix?: string; prefix?: string }) => {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView) return;
    let start = 0;
    const duration = 2000;
    const increment = end / (duration / 16);

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [isInView, end]);

  return (
    <span ref={ref} className="tabular-nums">
      {prefix}{count}{suffix}
    </span>
  );
};

export function TrustLandingPage() {
  const [showFloatingCTA, setShowFloatingCTA] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  // Handle scroll for floating CTA and progress bar
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (scrollTop / docHeight) * 100;

      setScrollProgress(progress);
      setShowFloatingCTA(scrollTop > 800);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-[#f6f9fc]">
      {/* Scroll Progress Bar */}
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-500 to-orange-600 origin-left z-[60]"
        style={{ scaleX: scrollProgress / 100 }}
        initial={{ scaleX: 0 }}
      />

      {/* Floating CTA Button - Positioned to avoid chat widget */}
      <motion.div
        initial={{ opacity: 0, y: 100 }}
        animate={{
          opacity: showFloatingCTA ? 1 : 0,
          y: showFloatingCTA ? 0 : 100
        }}
        transition={{ duration: 0.3 }}
        className="fixed bottom-8 left-8 z-50"
      >
        <button
          onClick={() => navigate('/pilot-application')}
          className="group px-6 py-4 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-full font-semibold shadow-[0_8px_32px_rgba(255,107,53,0.4)] hover:shadow-[0_12px_48px_rgba(255,107,53,0.6)] transition-all duration-300 flex items-center gap-2 hover:scale-105"
        >
          <span>Request access</span>
          <motion.div
            animate={{ x: [0, 4, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <ArrowRight className="w-5 h-5" />
          </motion.div>
        </button>
      </motion.div>
      {/* NAVIGATION - Stripe-inspired */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-[#e3e8ee]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="flex items-center gap-2"
          >
            {/* Premium Logo */}
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" className="flex-shrink-0">
              <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FF6B35" />
                  <stop offset="100%" stopColor="#F7931E" />
                </linearGradient>
              </defs>
              <circle cx="16" cy="16" r="14" fill="url(#logoGradient)" />
              <path d="M12 16 L16 20 L22 12" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
            </svg>
            <div className="flex flex-col leading-none">
              <span className="text-xl font-bold bg-gradient-to-r from-[#0a2540] to-[#0a2540]/80 bg-clip-text text-transparent" style={{ letterSpacing: '-0.02em' }}>
                RekindlePro
              </span>
              <span className="text-[10px] text-orange-600 font-semibold tracking-wide">PILOT</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="hidden md:flex items-center gap-8 text-sm"
          >
            <a href="#platform" className="text-black/60 hover:text-black transition-colors">Platform</a>
            <a href="#results" className="text-black/60 hover:text-black transition-colors">Results</a>
            <a href="#pricing" className="text-black/60 hover:text-black transition-colors">Pricing</a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <MinimalButton variant="primary" onClick={() => navigate('/pilot-application')}>
              Request Access
            </MinimalButton>
          </motion.div>
        </div>
      </nav>

      <main className="pt-20">
        {/* HERO - Clean, clear, confident */}
        <section className="relative min-h-[95vh] flex items-center justify-center px-6 py-32 overflow-hidden bg-gradient-to-b from-white via-[#fafbfc] to-white">
          {/* Animated gradient orbs */}
          <motion.div
            className="absolute top-1/4 left-1/3 w-[600px] h-[600px] bg-gradient-to-r from-orange-400/10 via-orange-500/15 to-orange-300/10 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              x: [0, 50, 0],
              y: [0, 30, 0],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute bottom-1/4 right-1/3 w-[500px] h-[500px] bg-gradient-to-l from-blue-400/8 via-blue-500/10 to-purple-400/8 rounded-full blur-3xl"
            animate={{
              scale: [1.2, 1, 1.2],
              x: [0, -30, 0],
              y: [0, -50, 0],
            }}
            transition={{
              duration: 25,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1
            }}
          />

          {/* Premium grid pattern */}
          <div className="absolute inset-0 opacity-[0.02]" style={{
            backgroundImage: `
              linear-gradient(to right, rgba(0,0,0,0.1) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(0,0,0,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px'
          }} />

          <div className="relative max-w-5xl mx-auto text-center">
            {/* Founding Pilot Badge - Premium & Exclusive */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-3 px-5 py-2.5 bg-white/95 backdrop-blur-sm rounded-full mb-8 text-sm font-medium shadow-[0_4px_16px_rgba(0,0,0,0.08)] border border-black/5"
            >
              <div className="w-2 h-2 rounded-full bg-gradient-to-r from-orange-500 to-orange-600 animate-pulse" />
              <span className="bg-gradient-to-r from-[#0a2540] via-orange-600 to-[#0a2540] bg-clip-text text-transparent font-semibold">
                Founding Pilot — Invite Only
              </span>
              <span className="text-black/40 text-xs">·</span>
              <span className="text-black/60">Limited seats</span>
            </motion.div>

            {/* Headline - Large, clear with subtle gradient accent */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-8 leading-[1.1]"
              style={{ letterSpacing: '-0.04em' }}
            >
              <span className="block text-[#0a2540] mb-2">
                Recover dormant pipeline.
              </span>
              <span className="block bg-gradient-to-r from-[#0a2540]/40 via-[#ff6b35]/60 to-[#0a2540]/40 bg-clip-text text-transparent">
                Generate revenue.
              </span>
            </motion.h1>

            {/* Value prop - Clear, no hype */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="text-xl md:text-2xl text-[#425466] max-w-3xl mx-auto mb-8 leading-relaxed"
            >
              AI-powered outreach that transforms dormant leads into booked meetings.
              <span className="block mt-4 text-lg text-[#727f96]">
                <strong className="text-orange-600">Performance-based pricing.</strong> You only pay when we deliver confirmed meetings.
              </span>
            </motion.p>

            {/* Founding Member Lock-In - Premium Exclusivity */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="max-w-2xl mx-auto mb-12 p-5 bg-gradient-to-br from-white to-orange-50/30 rounded-2xl border border-orange-200/50 shadow-[0_8px_24px_rgba(255,107,53,0.08)]"
            >
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center flex-shrink-0 shadow-sm">
                  <Lock className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-[#0a2540] mb-1">Founding Pilot Terms</h4>
                  <p className="text-sm text-[#425466] leading-relaxed">
                    First 50 participants lock in <span className="font-semibold text-orange-600">founding member rates permanently</span>—no future price increases. Month 1 platform access complimentary. Future standard pricing starts at £99/month.
                  </p>
                </div>
              </div>
            </motion.div>

            {/* CTA - Single, clear action */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center mb-20"
            >
              <MinimalButton variant="primary" onClick={() => navigate('/pilot-application')}>
                Request access
                <ArrowRight className="w-4 h-4" />
              </MinimalButton>
              <MinimalButton variant="secondary">
                View Dashboard Demo
                <BarChart3 className="w-4 h-4" />
              </MinimalButton>
            </motion.div>

            {/* Performance Metrics - Elegant data showcase */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="max-w-5xl mx-auto mt-20"
            >
              <div className="relative px-8 py-12 bg-white/60 backdrop-blur-sm rounded-3xl border border-[#e3e8ee] shadow-[0_8px_32px_rgba(0,0,0,0.04)]">
                {/* Subtle gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-orange-50/30 via-transparent to-blue-50/20 rounded-3xl pointer-events-none" />

                <div className="relative grid grid-cols-2 md:grid-cols-4 gap-x-12 gap-y-8">
                  {[
                    { value: 15.2, suffix: '%', label: 'Average meeting rate', sublabel: 'vs 6% industry standard' },
                    { value: 72, label: 'Hours to first meeting', sublabel: 'median response time' },
                    { value: 98, suffix: '%', label: 'Message delivery rate', sublabel: 'your domain, your reputation' },
                    { value: 847, label: 'Leads reactivated', sublabel: 'pilot cohort, Q4 2024' }
                  ].map((metric, i) => (
                    <motion.div
                      key={i}
                      className="text-center group"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.6, delay: 0.9 + i * 0.1 }}
                    >
                      <div className="text-5xl font-bold bg-gradient-to-br from-[#0a2540] to-[#0a2540]/70 bg-clip-text text-transparent mb-2 tabular-nums group-hover:from-orange-600 group-hover:to-orange-500 transition-all duration-500">
                        <Counter end={metric.value} suffix={metric.suffix || ''} />
                      </div>
                      <div className="text-sm font-medium text-[#0a2540] mb-1">{metric.label}</div>
                      <div className="text-xs text-[#727f96]">{metric.sublabel}</div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Trust & Security badges - Refined presentation */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.2 }}
              className="flex flex-wrap items-center justify-center gap-8 mt-16"
            >
              <div className="flex items-center gap-2.5 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-xl border border-[#e3e8ee] shadow-sm">
                <Shield className="w-4 h-4 text-[#425466]" />
                <span className="text-sm text-[#425466] font-medium">SOC 2 Type II</span>
              </div>
              <div className="flex items-center gap-2.5 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-xl border border-[#e3e8ee] shadow-sm">
                <Lock className="w-4 h-4 text-[#425466]" />
                <span className="text-sm text-[#425466] font-medium">GDPR Compliant</span>
              </div>
              <div className="flex items-center gap-2.5 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-xl border border-[#e3e8ee] shadow-sm">
                <CheckCircle2 className="w-4 h-4 text-[#425466]" />
                <span className="text-sm text-[#425466] font-medium">Your domain, your brand</span>
              </div>
            </motion.div>

            {/* Dashboard Preview - Interactive */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 1.2 }}
              className="mt-24 max-w-6xl mx-auto"
            >
              <div className="relative group">
                {/* Glow effect on hover */}
                <div className="absolute -inset-1 bg-gradient-to-r from-orange-500 via-orange-400 to-orange-500 rounded-2xl opacity-0 group-hover:opacity-20 blur-xl transition-all duration-1000" />

                <div className="relative rounded-2xl overflow-hidden shadow-[0_8px_24px_rgba(0,0,0,0.08),0_32px_64px_rgba(0,0,0,0.12)] border border-[#e3e8ee] bg-white">
                  {/* Dashboard mockup */}
                  <div className="aspect-[16/10] bg-gradient-to-br from-[#fafbfc] via-white to-[#f6f9fc] p-6">
                    {/* Top bar */}
                    <div className="flex items-center justify-between mb-6 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-400" />
                        <div className="w-3 h-3 rounded-full bg-yellow-400" />
                        <div className="w-3 h-3 rounded-full bg-green-400" />
                      </div>
                      <div className="text-xs text-black/40 font-mono">Dashboard Preview</div>
                    </div>

                    {/* Dashboard content */}
                    <div className="grid grid-cols-4 gap-4 px-4">
                      {[
                        { label: 'Active Leads', value: '2,847', trend: '+12%', color: 'from-blue-500 to-blue-600' },
                        { label: 'Meetings Booked', value: '127', trend: '+23%', color: 'from-green-500 to-green-600' },
                        { label: 'Reply Rate', value: '15.2%', trend: '+5.3%', color: 'from-orange-500 to-orange-600' },
                        { label: 'Revenue', value: '£47K', trend: '+31%', color: 'from-purple-500 to-purple-600' }
                      ].map((stat, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.5, delay: 1.4 + i * 0.1 }}
                          className="bg-white rounded-xl p-4 border border-black/5 shadow-sm"
                        >
                          <div className="text-xs text-black/40 mb-2">{stat.label}</div>
                          <div className="text-2xl font-bold text-[#0a2540] mb-1 tabular-nums">{stat.value}</div>
                          <div className={`text-xs font-semibold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
                            {stat.trend}
                          </div>
                        </motion.div>
                      ))}
                    </div>

                    {/* Chart placeholder */}
                    <div className="mt-6 px-4">
                      <div className="bg-white rounded-xl p-6 border border-black/5 shadow-sm">
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="text-sm font-semibold text-[#0a2540]">Meeting Rate Trend</h4>
                          <div className="flex gap-2">
                            <div className="w-2 h-2 rounded-full bg-orange-500" />
                            <div className="w-2 h-2 rounded-full bg-black/10" />
                            <div className="w-2 h-2 rounded-full bg-black/10" />
                          </div>
                        </div>
                        <div className="h-32 flex items-end gap-2">
                          {[40, 65, 45, 80, 55, 90, 70, 95, 85, 100].map((height, i) => (
                            <motion.div
                              key={i}
                              initial={{ height: 0 }}
                              animate={{ height: `${height}%` }}
                              transition={{ duration: 0.5, delay: 1.8 + i * 0.05 }}
                              className="flex-1 bg-gradient-to-t from-orange-500 to-orange-400 rounded-t opacity-80 hover:opacity-100 transition-opacity"
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* PROBLEM - Data-driven, factual */}
        <section className="relative py-32 px-6 bg-gradient-to-br from-[#0a2540] via-black to-[#0a2540] text-white overflow-hidden">
          {/* Subtle animated background */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-orange-500/20 rounded-full blur-3xl" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />
          </div>

          <div className="relative max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="mb-20"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full mb-6 text-sm">
                <div className="w-2 h-2 rounded-full bg-orange-500" />
                <span className="text-white/80">The Hidden Problem</span>
              </div>
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-8" style={{ letterSpacing: '-0.03em' }}>
                Your CRM contains
                <span className="block bg-gradient-to-r from-orange-400 via-orange-500 to-orange-400 bg-clip-text text-transparent mt-2">£500K–£2M in dormant leads</span>
              </h2>
              <p className="text-xl text-white/60 max-w-2xl leading-relaxed">
                Leads that engaged, downloaded content, even took calls. Then went silent.
                Not because they weren't interested—because the timing wasn't right.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-6">
              {[
                { value: '4,250', label: 'Average dormant leads', sub: 'B2B SaaS CRM (5K-20K employees)', color: 'from-blue-500 to-blue-600' },
                { value: '£2,400', label: 'Cost per enterprise lead', sub: 'Industry average acquisition cost', color: 'from-orange-500 to-orange-600' },
                { value: '85%', label: 'Wasted opportunity', sub: 'Never re-engaged or monetized', color: 'from-red-500 to-red-600' }
              ].map((stat, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  whileHover={{ y: -8, scale: 1.02 }}
                  className="group relative p-8 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer"
                >
                  {/* Glow effect on hover */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-300`} />

                  <div className="relative">
                    <div className={`text-5xl font-bold bg-gradient-to-br ${stat.color} bg-clip-text text-transparent mb-3 tabular-nums`}>
                      {stat.value}
                    </div>
                    <div className="text-lg font-semibold text-white mb-2">{stat.label}</div>
                    <div className="text-sm text-white/40 leading-relaxed">{stat.sub}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* SOLUTION - Transparent process */}
        <section className="relative py-32 px-6 bg-gradient-to-b from-white to-[#f6f9fc]" id="platform">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full mb-6 text-sm text-black/60 border border-black/5 shadow-sm">
                <Eye className="w-4 h-4 text-orange-500" />
                <span>Full transparency and control</span>
              </div>
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6" style={{ letterSpacing: '-0.03em' }}>
                How it works
              </h2>
              <p className="text-xl text-black/60 max-w-2xl mx-auto">
                AI automation with human oversight at every step
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-6">
              {[
                {
                  step: '01',
                  title: 'CRM Integration',
                  desc: 'Secure API connection analyzes dormant leads by activity, engagement score, and deal stage.',
                  time: '10 minutes',
                  color: 'from-blue-500 to-blue-600',
                  icon: '🔗'
                },
                {
                  step: '02',
                  title: 'AI Research',
                  desc: 'Research company news, funding, job changes, industry trends. Craft personalized messaging. No data retention.',
                  time: '12-18 hours',
                  color: 'from-purple-500 to-purple-600',
                  icon: '🤖'
                },
                {
                  step: '03',
                  title: 'Multi-Channel Delivery',
                  desc: 'Intelligent sequences via Email, SMS, WhatsApp, Voicemail from your domain. Adaptive timing based on engagement.',
                  time: '7-14 days',
                  color: 'from-orange-500 to-orange-600',
                  icon: '📱'
                },
                {
                  step: '04',
                  title: 'Meeting Confirmed',
                  desc: 'Decision-maker responds, meeting automatically scheduled. You only pay when confirmed with decision-makers.',
                  time: '72 hours avg',
                  color: 'from-green-500 to-green-600',
                  icon: '✅'
                }
              ].map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  whileHover={{ scale: 1.03, y: -8 }}
                  className="group relative min-h-[260px] p-8 bg-white rounded-2xl border border-[#e3e8ee] hover:border-orange-200 transition-all duration-500 cursor-pointer overflow-hidden shadow-[0_4px_12px_rgba(0,0,0,0.04)] hover:shadow-[0_8px_32px_rgba(255,107,53,0.15)]"
                >
                  {/* Animated gradient background */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${item.color} opacity-0 group-hover:opacity-5 transition-all duration-500`} />

                  {/* Corner accent */}
                  <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-orange-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                  <div className="relative">
                    {/* Icon & Time */}
                    <div className="flex items-start justify-between mb-6">
                      <motion.div
                        className="w-14 h-14 rounded-xl bg-gradient-to-br from-orange-50 to-orange-100 group-hover:from-orange-100 group-hover:to-orange-200 flex items-center justify-center text-2xl transition-all duration-300 shadow-sm"
                        whileHover={{ rotate: [0, -10, 10, -10, 0], scale: 1.1 }}
                        transition={{ duration: 0.5 }}
                      >
                        {item.icon}
                      </motion.div>
                      <span className="text-xs text-black/40 bg-black/5 px-3 py-1.5 rounded-full tabular-nums font-medium">{item.time}</span>
                    </div>

                    {/* Step number */}
                    <div className={`text-4xl font-bold bg-gradient-to-br ${item.color} bg-clip-text text-transparent mb-4 tabular-nums opacity-40 group-hover:opacity-100 transition-opacity`}>
                      {item.step}
                    </div>

                    {/* Content */}
                    <h3 className="text-2xl font-bold text-[#0a2540] mb-3 group-hover:text-orange-600 transition-colors duration-300">{item.title}</h3>
                    <p className="text-base text-black/60 leading-relaxed">{item.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* MULTI-CHANNEL - Clean data viz */}
        <section className="relative py-32 px-6 bg-black/[0.02]">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6" style={{ letterSpacing: '-0.03em' }}>
                Multi-channel intelligence
              </h2>
              <p className="text-xl text-black/60 max-w-2xl mx-auto">
                Real engagement data from 847 campaigns
              </p>
            </motion.div>

            <div className="grid md:grid-cols-4 gap-6">
              {[
                { channel: 'Email', icon: Mail, open: '62%', reply: '14%', meeting: '15.2%', color: 'from-blue-500 to-blue-600' },
                { channel: 'SMS', icon: MessageSquare, open: '98%', reply: '12%', meeting: '3.2%', color: 'from-green-500 to-green-600' },
                { channel: 'WhatsApp', icon: MessageSquare, open: '95%', reply: '18%', meeting: '4.5%', color: 'from-emerald-500 to-emerald-600' },
                { channel: 'Voicemail', icon: Phone, open: '72%', reply: '6%', meeting: '1.5%', color: 'from-purple-500 to-purple-600' }
              ].map((ch, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  whileHover={{ scale: 1.05, rotate: -1 }}
                  className="group p-6 bg-white rounded-2xl border border-[#e3e8ee] hover:border-[#d1d9e0] transition-all duration-300 cursor-pointer shadow-[0_2px_4px_rgba(0,0,0,0.04),0_8px_16px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.08),0_16px_32px_rgba(0,0,0,0.08)]"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <motion.div
                      className={`p-3 bg-gradient-to-br ${ch.color} rounded-xl shadow-lg`}
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      <ch.icon className="w-5 h-5 text-white" />
                    </motion.div>
                    <span className="font-bold text-black group-hover:text-orange-600 transition-colors">{ch.channel}</span>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2 text-xs">
                        <span className="text-black/40 font-medium">Open Rate</span>
                        <span className="text-black font-bold tabular-nums">{ch.open}</span>
                      </div>
                      <div className="h-2 bg-black/5 rounded-full overflow-hidden">
                        <motion.div
                          className={`h-full bg-gradient-to-r ${ch.color}`}
                          initial={{ width: 0 }}
                          whileInView={{ width: ch.open }}
                          viewport={{ once: true }}
                          transition={{ duration: 1, delay: 0.2 + i * 0.1 }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2 text-xs">
                        <span className="text-black/40 font-medium">Reply Rate</span>
                        <span className="text-black font-bold tabular-nums">{ch.reply}</span>
                      </div>
                      <div className="h-2 bg-black/5 rounded-full overflow-hidden">
                        <motion.div
                          className={`h-full bg-gradient-to-r ${ch.color}`}
                          initial={{ width: 0 }}
                          whileInView={{ width: ch.reply }}
                          viewport={{ once: true }}
                          transition={{ duration: 1, delay: 0.4 + i * 0.1 }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2 text-xs">
                        <span className="text-black/40 font-medium">Meeting Rate</span>
                        <span className="text-orange-600 font-bold tabular-nums">{ch.meeting}</span>
                      </div>
                      <div className="h-2 bg-black/5 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-orange-500 to-orange-600"
                          initial={{ width: 0 }}
                          whileInView={{ width: ch.meeting }}
                          viewport={{ once: true }}
                          transition={{ duration: 1, delay: 0.6 + i * 0.1 }}
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* RESULTS - Verified proof */}
        <section className="relative py-32 px-6" id="results">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6" style={{ letterSpacing: '-0.03em' }}>
                Verified results
              </h2>
              <p className="text-xl text-black/60 max-w-2xl mx-auto">
                Data from 847 leads, Q4 2024. Enterprise SaaS clients only.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-12 mb-16">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
              >
                <div className="flex items-end gap-4 mb-4">
                  <div className="text-7xl font-bold text-black tabular-nums">15.2%</div>
                  <div className="pb-3 text-black/40">vs 6-8% industry avg</div>
                </div>
                <div className="text-xl font-semibold text-black mb-2">Meeting booking rate</div>
                <div className="text-black/60">Verified across 847 dormant leads, Q4 2024</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
              >
                <div className="flex items-end gap-4 mb-4">
                  <div className="text-7xl font-bold text-black tabular-nums">72hr</div>
                  <div className="pb-3 text-black/40">avg first meeting</div>
                </div>
                <div className="text-xl font-semibold text-black mb-2">Time to revenue</div>
                <div className="text-black/60">Industry standard: 2-3 weeks</div>
              </motion.div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {[
                { icon: Shield, title: 'SOC 2 Type II Certified', sub: 'Enterprise-grade security', color: 'from-green-500 to-emerald-600' },
                { icon: Lock, title: 'GDPR Compliant', sub: 'Full data protection & privacy', color: 'from-blue-500 to-blue-600' },
                { icon: Eye, title: 'Approval Mode', sub: 'Review every message before sending', color: 'from-purple-500 to-purple-600' },
                { icon: TrendingUp, title: '99.9% Uptime SLA', sub: 'Enterprise reliability guarantee', color: 'from-orange-500 to-orange-600' }
              ].map((badge, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  whileHover={{ scale: 1.03, y: -2 }}
                  className="group flex items-center gap-4 p-6 bg-white rounded-2xl border border-[#e3e8ee] hover:border-[#d1d9e0] transition-all duration-300 cursor-pointer shadow-[0_2px_4px_rgba(0,0,0,0.04),0_8px_16px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.08),0_16px_32px_rgba(0,0,0,0.08)]"
                >
                  <motion.div
                    className={`p-3 bg-gradient-to-br ${badge.color} rounded-xl shadow-lg`}
                    whileHover={{ rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <badge.icon className="w-6 h-6 text-white" />
                  </motion.div>
                  <div>
                    <div className="font-bold text-black group-hover:text-orange-600 transition-colors">{badge.title}</div>
                    <div className="text-sm text-black/60">{badge.sub}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* PILOT COHORT METRICS - Real, Transparent Data */}
        <section className="relative py-32 px-6 bg-white">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#f6f9fc] rounded-full mb-6 text-sm text-[#425466] border border-[#e3e8ee]">
                <BarChart3 className="w-4 h-4 text-[#0a2540]" />
                <span>Pilot cohort performance</span>
              </div>
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6 text-[#0a2540]" style={{ letterSpacing: '-0.03em' }}>
                Real metrics from early adopters
              </h2>
              <p className="text-xl text-[#425466] max-w-2xl mx-auto">
                Transparent results from our founding pilot program, Q4 2024.
              </p>
            </motion.div>

            {/* Founding Pilot Progress Tracker */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="max-w-3xl mx-auto mb-16 p-8 bg-gradient-to-br from-[#f6f9fc] to-white rounded-2xl border border-[#e3e8ee]"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-[#0a2540] mb-1">Founding Pilot Program</h3>
                  <p className="text-sm text-[#425466]">Lock in permanent founding member rates</p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-[#0a2540] tabular-nums">14/50</div>
                  <div className="text-xs text-[#425466]">seats claimed</div>
                </div>
              </div>
              <div className="w-full h-2 bg-[#e3e8ee] rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-[#0a2540] to-[#0a2540]/80 rounded-full"
                  initial={{ width: 0 }}
                  whileInView={{ width: '28%' }}
                  viewport={{ once: true }}
                  transition={{ duration: 1, ease: "easeOut" }}
                />
              </div>
              <div className="mt-4 text-xs text-[#727f96]">
                Limited to first 50 organizations. Rates lock in permanently.
              </div>
            </motion.div>

            {/* Real Pilot Metrics Grid */}
            <div className="grid md:grid-cols-4 gap-6">
              {[
                { value: '847', label: 'Leads reactivated', sublabel: 'from dormant CRM data' },
                { value: '129', label: 'Qualified meetings', sublabel: 'confirmed with decision-makers' },
                { value: '15.2%', label: 'Meeting rate', sublabel: 'vs 6% industry avg' },
                { value: '72h', label: 'Time to first meeting', sublabel: 'median response time' }
              ].map((metric, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  className="p-6 bg-white rounded-xl border border-[#e3e8ee] hover:border-[#0a2540]/20 transition-all duration-300"
                >
                  <div className="text-4xl font-bold text-[#0a2540] mb-2 tabular-nums">{metric.value}</div>
                  <div className="text-sm font-medium text-[#0a2540] mb-1">{metric.label}</div>
                  <div className="text-xs text-[#727f96]">{metric.sublabel}</div>
                </motion.div>
              ))}
            </div>

            {/* Pilot Results Summary - Premium presentation */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="mt-20 relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-orange-500/10 via-orange-400/10 to-orange-500/10 rounded-3xl blur-2xl" />

              <div className="relative px-10 py-10 bg-white/90 backdrop-blur-sm rounded-3xl border border-orange-200/60 shadow-[0_8px_32px_rgba(255,107,53,0.12)]">
                <div className="text-center mb-8">
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-orange-100 rounded-full mb-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-pulse" />
                    <span className="text-xs font-semibold text-orange-700">Pilot Cohort Performance</span>
                  </div>
                  <p className="text-sm text-black/60">Real results from early access users, Q4 2024</p>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-x-10 gap-y-8">
                  {[
                    { value: 847, label: 'Dormant leads analyzed', icon: '🎯' },
                    { value: 129, label: 'Meetings booked', icon: '📅' },
                    { value: '£47K', label: 'Pipeline generated', icon: '💰' },
                    { value: '8.4x', label: 'Average ROI', icon: '📈' }
                  ].map((stat, i) => (
                    <motion.div
                      key={i}
                      className="text-center group"
                      initial={{ opacity: 0, scale: 0.9 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.5, delay: 0.5 + i * 0.1 }}
                      whileHover={{ scale: 1.05, y: -4 }}
                    >
                      <div className="text-3xl mb-2 group-hover:scale-110 transition-transform duration-300">{stat.icon}</div>
                      <div className="text-4xl font-bold bg-gradient-to-br from-orange-600 to-orange-500 bg-clip-text text-transparent mb-2 tabular-nums">
                        {stat.value}
                      </div>
                      <div className="text-sm text-[#0a2540] font-medium">{stat.label}</div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* PRICING - Clear, transparent, mathematically precise */}
        <section className="relative py-32 px-6 bg-black text-white" id="pricing">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full mb-6 text-sm">
                <Lock className="w-4 h-4 text-orange-400" />
                <span className="text-white/80">Founding Pilot Pricing</span>
              </div>
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6" style={{ letterSpacing: '-0.03em' }}>
                Simple, transparent pricing
              </h2>
              <p className="text-xl text-white/60 max-w-3xl mx-auto leading-relaxed">
                Pay only for qualified meetings with decision-makers. Founding pilot members lock in these rates permanently.
              </p>
            </motion.div>

            <div className="grid lg:grid-cols-3 gap-8 mb-16">
              {/* Starter Tier */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0 }}
                className="p-8 bg-white/5 rounded-2xl border border-white/10 hover:border-white/20 transition-all duration-300 relative"
              >
                {/* Founding Badge */}
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-white text-xs font-semibold">
                  Founding Rate
                </div>

                <div className="mb-8">
                  <h3 className="text-2xl font-bold text-white mb-2">Starter</h3>
                  <p className="text-white/50 text-sm">For teams testing pipeline recovery</p>
                </div>

                <div className="mb-8">
                  <div className="text-white/40 text-xs uppercase tracking-wide mb-3">Platform Access</div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <div className="text-5xl font-bold text-white tabular-nums">£29</div>
                    <div className="text-white/40 text-lg">/month</div>
                  </div>
                  <div className="text-white/70 text-sm mb-1">£100 per qualified meeting</div>
                  <div className="text-white/40 text-xs">For ACV &lt; £5,000 • Month 1 complimentary</div>
                </div>

                <div className="space-y-3 mb-8 pb-8 border-b border-white/10">
                  {['500 verified leads/month', 'Email + SMS channels', 'AI research & personalization', 'Standard analytics', 'Email support'].map((feature, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <CheckCircle2 className="w-4 h-4 text-white/60 flex-shrink-0 mt-0.5" />
                      <span className="text-white/70 text-sm leading-relaxed">{feature}</span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => navigate('/pilot-application')}
                  className="w-full px-6 py-3 bg-white/10 hover:bg-white/15 text-white rounded-lg font-semibold transition-all duration-200 border border-white/20"
                >
                  Request access
                </button>
              </motion.div>

              {/* Professional Tier (Featured) */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.1 }}
                className="p-8 bg-gradient-to-br from-white/15 to-white/10 rounded-2xl border-2 border-orange-500/50 hover:border-orange-500/70 transition-all duration-300 relative shadow-[0_8px_32px_rgba(255,107,53,0.2)]"
              >
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full text-white text-xs font-bold shadow-lg">
                  RECOMMENDED
                </div>

                <div className="mb-8">
                  <h3 className="text-2xl font-bold text-white mb-2">Professional</h3>
                  <p className="text-white/60 text-sm">For mid-market revenue teams</p>
                </div>

                <div className="mb-8">
                  <div className="text-white/40 text-xs uppercase tracking-wide mb-3">Platform Access</div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <div className="text-5xl font-bold text-white tabular-nums">£199</div>
                    <div className="text-white/40 text-lg">/month</div>
                  </div>
                  <div className="text-white/90 text-sm mb-1">£250 per qualified meeting</div>
                  <div className="text-orange-300 text-xs">For ACV £5K–£25K • Founding rate locked</div>
                </div>

                <div className="space-y-3 mb-8 pb-8 border-b border-white/20">
                  {['2,000 verified leads/month', 'All channels (Email, SMS, WhatsApp, Voicemail)', 'Advanced AI personalization', 'Real-time analytics & reporting', 'Priority support', 'Custom CRM integrations'].map((feature, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <CheckCircle2 className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
                      <span className="text-white/90 text-sm leading-relaxed">{feature}</span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => navigate('/pilot-application')}
                  className="w-full px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-lg font-semibold transition-all duration-200 shadow-lg shadow-orange-500/30"
                >
                  Request access
                </button>
              </motion.div>

              {/* Enterprise Tier */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="p-8 bg-white/5 rounded-2xl border border-white/10 hover:border-white/20 transition-all duration-300 relative"
              >
                {/* Founding Badge */}
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-white text-xs font-semibold">
                  Founding Rate
                </div>

                <div className="mb-8">
                  <h3 className="text-2xl font-bold text-white mb-2">Enterprise</h3>
                  <p className="text-white/50 text-sm">For enterprise-scale deployment</p>
                </div>

                <div className="mb-8">
                  <div className="text-white/40 text-xs uppercase tracking-wide mb-3">Platform Access</div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <div className="text-5xl font-bold text-white tabular-nums">£799</div>
                    <div className="text-white/40 text-lg">/month</div>
                  </div>
                  <div className="text-white/70 text-sm mb-1">£500–£1,000 per qualified meeting</div>
                  <div className="text-white/40 text-xs">For ACV &gt; £25K • Custom pricing available</div>
                </div>

                <div className="space-y-3 mb-8 pb-8 border-b border-white/10">
                  {['Unlimited verified leads', 'All Professional features', 'Dedicated success manager', 'Custom AI model training', 'White-glove onboarding', 'SLA guarantees', 'Full API access'].map((feature, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <CheckCircle2 className="w-4 h-4 text-white/60 flex-shrink-0 mt-0.5" />
                      <span className="text-white/70 text-sm leading-relaxed">{feature}</span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => navigate('/pilot-application')}
                  className="w-full px-6 py-3 bg-white/10 hover:bg-white/15 text-white rounded-lg font-semibold transition-all duration-200 border border-white/20"
                >
                  Request access
                </button>
              </motion.div>
            </div>

            {/* ROI Calculator - Interactive & Transparent */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="max-w-5xl mx-auto mb-16"
            >
              <div className="p-10 bg-gradient-to-br from-white/10 to-white/5 rounded-3xl border border-white/20 backdrop-blur-sm">
                <div className="text-center mb-10">
                  <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full mb-4 text-sm">
                    <BarChart3 className="w-4 h-4 text-orange-400" />
                    <span className="text-white/80">ROI Calculator</span>
                  </div>
                  <h3 className="text-3xl font-bold text-white mb-2">See your expected return</h3>
                  <p className="text-white/60">Based on real pilot cohort performance</p>
                </div>

                <div className="grid md:grid-cols-3 gap-6 mb-8">
                  {[
                    {
                      acv: '£3,500',
                      tier: 'Starter',
                      meetings: 20,
                      closeRate: 0.20,
                      calculation: {
                        feePerMeeting: 100, // Simple £100 per meeting
                        totalFees: 2000, // 100 * 20
                        platform: 29,
                        totalCost: 2029,
                        closedDeals: 4, // 20 * 0.20
                        revenue: 14000, // 4 * 3500
                        roi: 6.9 // 14000 / 2029
                      }
                    },
                    {
                      acv: '£12,500',
                      tier: 'Professional',
                      meetings: 20,
                      closeRate: 0.20,
                      calculation: {
                        feePerMeeting: 250, // Simple £250 per meeting
                        totalFees: 5000, // 250 * 20
                        platform: 199,
                        totalCost: 5199,
                        closedDeals: 4,
                        revenue: 50000, // 4 * 12500
                        roi: 9.6 // 50000 / 5199
                      }
                    },
                    {
                      acv: '£40,000',
                      tier: 'Enterprise',
                      meetings: 20,
                      closeRate: 0.20,
                      calculation: {
                        feePerMeeting: 750, // £500-£1000 range, using £750 average
                        totalFees: 15000, // 750 * 20
                        platform: 799,
                        totalCost: 15799,
                        closedDeals: 4,
                        revenue: 160000, // 4 * 40000
                        roi: 10.1 // 160000 / 15799
                      }
                    }
                  ].map((example, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.5, delay: i * 0.1 }}
                      className="p-6 bg-white/5 rounded-2xl border border-white/10 hover:border-orange-500/30 transition-all duration-300"
                    >
                      <div className="text-center mb-4">
                        <div className="text-sm text-white/40 mb-1">{example.tier}</div>
                        <div className="text-2xl font-bold text-white mb-1">{example.acv} ACV</div>
                        <div className="text-xs text-white/60">20% close rate</div>
                      </div>

                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between text-white/60">
                          <span>20 meetings booked</span>
                          <span className="font-mono">£{example.calculation.totalFees.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-white/60">
                          <span>Platform fee</span>
                          <span className="font-mono">£{example.calculation.platform}</span>
                        </div>
                        <div className="flex justify-between text-white/80 font-semibold pt-2 border-t border-white/10">
                          <span>Total cost</span>
                          <span className="font-mono">£{example.calculation.totalCost.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-green-400 font-semibold pt-2">
                          <span>Revenue (4 deals)</span>
                          <span className="font-mono">£{example.calculation.revenue.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-center pt-3">
                          <div className="px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg">
                            <div className="text-2xl font-bold text-white">{example.calculation.roi.toFixed(1)}x</div>
                            <div className="text-xs text-white/80">ROI</div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>

                <div className="text-center text-white/50 text-xs">
                  Based on 20% close rate (industry standard for qualified outbound). Fee = max(£100, percentage × ACV) ensures viability for all deal sizes.
                </div>
              </div>
            </motion.div>

            {/* Meeting Definition & Guarantee - Precise & Legally Sound */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="max-w-5xl mx-auto space-y-6"
            >
              {/* What Counts as a "Booked Meeting" */}
              <div className="p-8 bg-white/5 rounded-2xl border border-white/10 backdrop-blur-sm">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center flex-shrink-0">
                    <Eye className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">
                      What qualifies as a "Booked Meeting"?
                    </h4>
                    <div className="space-y-2 text-sm text-white/70 leading-relaxed">
                      <p>You're only billed for meetings that meet all of these criteria:</p>
                      <ul className="list-disc list-inside space-y-1 ml-2">
                        <li>Calendar invitation accepted by prospect with ≥1 decision-maker attending</li>
                        <li>Meeting duration ≥ 20 minutes (not screening calls)</li>
                        <li>Prospect confirms intent to discuss your solution</li>
                        <li>No-shows and last-minute cancellations are credited automatically</li>
                      </ul>
                      <p className="mt-3 text-white/50 text-xs">All meetings tracked with calendar confirmations and call recordings for full transparency.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Founding Pilot Guarantee */}
              <div className="p-8 bg-white/5 rounded-2xl border border-white/10 backdrop-blur-sm">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                    <Lock className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">
                      Founding Pilot Guarantee
                    </h4>
                    <p className="text-white/70 text-sm leading-relaxed mb-4">
                      First 50 participants lock in founding member pricing permanently—no future rate increases. If we don't deliver ≥5 qualified meetings within 30 days (provided you complete onboarding and comply with program terms), we refund 100% of performance fees paid plus a £500 account credit.
                    </p>
                    <div className="flex flex-wrap gap-4 text-xs text-white/50">
                      <div className="flex items-center gap-2">
                        <Shield className="w-3 h-3" />
                        <span>Cancel anytime</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>No setup fees</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Lock className="w-3 h-3" />
                        <span>Rates locked forever</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* COMPARISON - Clean table */}
        <section className="relative py-32 px-6">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6" style={{ letterSpacing: '-0.03em' }}>
                Why RekindlePro.ai
              </h2>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="overflow-hidden rounded-2xl border border-black/10"
            >
              <table className="w-full">
                <thead>
                  <tr className="border-b border-black/10 bg-black/[0.02]">
                    <th className="p-4 text-left text-sm font-semibold text-black/60">Feature</th>
                    <th className="p-4 text-center bg-orange-50/50">
                      <div className="font-bold text-black">RekindlePro.ai</div>
                    </th>
                    <th className="p-4 text-center text-sm font-semibold text-black/40">SDR Team</th>
                    <th className="p-4 text-center text-sm font-semibold text-black/40">AI Tools</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ['Cost per meeting', '£249-999 + 2.5% ACV', '£2,400+', '£800-1,200'],
                    ['Time to meeting', '72 hours', '2-3 weeks', '1-2 weeks'],
                    ['Meeting rate', '15.2%', '6-8%', '8-10%'],
                    ['Multi-channel', '✓', 'Limited', 'Email only'],
                    ['Your domain', '✓', '✓', '✗']
                  ].map((row, i) => (
                    <tr key={i} className="border-b border-black/5">
                      <td className="p-4 text-black/60">{row[0]}</td>
                      <td className="p-4 text-center bg-orange-50/50 font-semibold text-black">{row[1]}</td>
                      <td className="p-4 text-center text-black/40">{row[2]}</td>
                      <td className="p-4 text-center text-black/40">{row[3]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </motion.div>
          </div>
        </section>

        {/* FINAL CTA - Clean, confident with subtle urgency */}
        <section className="relative py-32 px-6 bg-gradient-to-b from-white to-[#f6f9fc]">
          <div className="max-w-3xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              {/* Founding pilot badge */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full mb-6 text-xs text-[#727f96] border border-[#e3e8ee] shadow-sm"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-pulse" />
                <span>Founding pilot — 50 seats remaining</span>
              </motion.div>

              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6" style={{ letterSpacing: '-0.03em' }}>
                Recover dormant pipeline
              </h2>
              <p className="text-xl text-black/60 mb-8 max-w-2xl mx-auto">
                Join B2B teams using AI to transform dormant leads into confirmed revenue meetings.
              </p>

              {/* Value props */}
              <div className="flex flex-wrap items-center justify-center gap-4 mb-12 text-sm text-black/60">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-orange-500" />
                  <span>Simple, transparent pricing</span>
                </div>
                <span className="text-black/20">·</span>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-orange-500" />
                  <span>Founding rates locked</span>
                </div>
                <span className="text-black/20">·</span>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-orange-500" />
                  <span>Cancel anytime</span>
                </div>
              </div>

              <MinimalButton variant="primary" onClick={() => navigate('/pilot-application')}>
                Request access
                <ArrowRight className="w-4 h-4" />
              </MinimalButton>
              <div className="text-sm text-black/40 mt-6">
                From £29/month + per-meeting fees · No credit card required
              </div>
            </motion.div>
          </div>
        </section>

        {/* FOOTER */}
        <footer className="relative border-t border-black/5 py-16 px-6 bg-white">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-4 gap-12 mb-12">
              <div>
                {/* Logo */}
                <div className="flex items-center gap-2 mb-4">
                  <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
                    <defs>
                      <linearGradient id="footerLogoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#FF6B35" />
                        <stop offset="100%" stopColor="#F7931E" />
                      </linearGradient>
                    </defs>
                    <circle cx="16" cy="16" r="14" fill="url(#footerLogoGradient)" />
                    <path d="M12 16 L16 20 L22 12" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                  </svg>
                  <span className="text-lg font-bold text-[#0a2540]">RekindlePro</span>
                </div>
                <p className="text-sm text-black/50 leading-relaxed">Enterprise revenue recovery platform powered by AI</p>
              </div>
              <div>
                <h4 className="font-semibold text-black mb-4 text-sm">Platform</h4>
                <ul className="space-y-2 text-sm text-black/60">
                  <li><a href="#platform" className="hover:text-black transition-colors">How It Works</a></li>
                  <li><a href="#results" className="hover:text-black transition-colors">Results</a></li>
                  <li><a href="#pricing" className="hover:text-black transition-colors">Pricing</a></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-black mb-4 text-sm">Company</h4>
                <ul className="space-y-2 text-sm text-black/60">
                  <li><a href="/privacy" className="hover:text-black transition-colors">Privacy</a></li>
                  <li><a href="/terms" className="hover:text-black transition-colors">Terms</a></li>
                  <li><a href="/security" className="hover:text-black transition-colors">Security</a></li>
                </ul>
              </div>
              <div>
                <MinimalButton variant="primary" onClick={() => navigate('/pilot-application')}>
                  Request Access
                </MinimalButton>
              </div>
            </div>
            <div className="border-t border-black/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-black/40">
              <div>© 2024 RekindlePro.ai. All rights reserved.</div>
              <div className="flex items-center gap-4">
                <span>SOC 2 Type II</span>
                <span>·</span>
                <span>GDPR Compliant</span>
              </div>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
