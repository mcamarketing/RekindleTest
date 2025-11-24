// @ts-nocheck
// PREMIUM LANDING PAGE - Trust-First, Apple-Level Design Quality
// Emotional Journey: Confidence → Control → Exclusivity → Trust → Action
import { useState, useEffect, useRef } from 'react';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';
import {
  Shield,
  Lock,
  TrendingUp,
  CheckCircle2,
  ArrowRight,
  BarChart3,
  Users,
  Mail,
  MessageSquare,
  Phone,
  Clock,
  Zap,
  Eye
} from 'lucide-react';

// Premium color palette
const colors = {
  navy: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
    950: '#020617'
  },
  gold: {
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706'
  },
  orange: {
    400: '#fb923c',
    500: '#f97316',
    600: '#ea580c'
  }
};

// Premium typography system
const typography = {
  display: 'font-display tracking-tight font-bold',
  heading: 'font-sans tracking-tight font-semibold',
  body: 'font-sans leading-relaxed',
  mono: 'font-mono tabular-nums'
};

// Trust badge component
const TrustBadge = ({ icon: Icon, title, subtitle }: { icon: any; title: string; subtitle: string }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.6 }}
    className="flex items-center gap-4 px-6 py-4 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/20 transition-all duration-300"
  >
    <div className="p-3 bg-gradient-to-br from-orange-500/20 to-orange-600/10 rounded-xl">
      <Icon className="w-6 h-6 text-orange-400" />
    </div>
    <div>
      <div className="text-white font-semibold text-sm">{title}</div>
      <div className="text-gray-400 text-xs">{subtitle}</div>
    </div>
  </motion.div>
);

// Metric card component
const MetricCard = ({ value, label, prefix = '', suffix = '', delay = 0 }: {
  value: number;
  label: string;
  prefix?: string;
  suffix?: string;
  delay?: number;
}) => {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView) return;

    let startTime: number;
    const duration = 2000;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 4);
      setCount(value * easeOut);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    setTimeout(() => requestAnimationFrame(animate), delay);
  }, [isInView, value, delay]);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: delay / 1000 }}
      whileHover={{ scale: 1.05, y: -5 }}
      className="text-center group cursor-pointer"
    >
      <div className="relative">
        <motion.div
          className="text-5xl lg:text-6xl font-bold bg-gradient-to-r from-orange-400 via-orange-500 to-pink-500 bg-clip-text text-transparent mb-3 tabular-nums drop-shadow-lg"
          animate={{
            backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "linear"
          }}
        >
          {prefix}{Math.round(count)}{suffix}
        </motion.div>
        <div className="absolute inset-0 bg-gradient-to-r from-orange-400 to-orange-600 blur-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-300" />
      </div>
      <div className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors uppercase tracking-wider">{label}</div>
    </motion.div>
  );
};

// Premium button component
const PremiumButton = ({
  children,
  onClick,
  variant = 'primary',
  size = 'lg',
  className = ''
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  size?: 'md' | 'lg';
  className?: string;
}) => {
  const baseClasses = "relative group overflow-hidden font-semibold transition-all duration-300 rounded-full flex items-center justify-center gap-2";
  const sizeClasses = {
    md: "px-8 py-3 text-sm",
    lg: "px-10 py-4 text-base"
  };
  const variantClasses = {
    primary: "bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-lg shadow-orange-500/25 hover:shadow-xl hover:shadow-orange-500/40 hover:scale-[1.02]",
    secondary: "bg-white/5 backdrop-blur-sm border border-white/20 text-white hover:bg-white/10 hover:border-white/30"
  };

  return (
    <motion.button
      onClick={onClick}
      whileTap={{ scale: 0.98 }}
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
      data-analytics="cta-click"
    >
      {variant === 'primary' && (
        <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
      )}
      <span className="relative z-10">{children}</span>
    </motion.button>
  );
};

export function PremiumLandingPage() {
  const { scrollY } = useScroll();
  const heroOpacity = useTransform(scrollY, [0, 300], [1, 0]);
  const heroScale = useTransform(scrollY, [0, 300], [1, 0.98]);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <div className="bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 min-h-screen text-white">
      {/* PREMIUM NAVIGATION */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <img
              src="/images/image copy copy.png"
              alt="Rekindle"
              className="h-10 w-auto"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="hidden md:flex items-center gap-8"
          >
            <a href="#solution" className="text-sm text-gray-400 hover:text-white transition-colors">Platform</a>
            <a href="#proof" className="text-sm text-gray-400 hover:text-white transition-colors">Results</a>
            <a href="#pricing" className="text-sm text-gray-400 hover:text-white transition-colors">Pricing</a>
            <PremiumButton
              variant="primary"
              size="md"
              onClick={() => navigate('/pilot-application')}
            >
              Apply for Access
            </PremiumButton>
          </motion.div>
        </div>
      </nav>

      <main className="pt-20">
        {/* HERO: AUTHORITY + CLARITY */}
        {/* Emotional Goal: Confidence - Product works, proven results */}
        <motion.section
          style={{ opacity: heroOpacity, scale: heroScale }}
          className="relative min-h-[90vh] flex items-center justify-center px-6 py-32 overflow-hidden"
        >
          {/* Enhanced animated gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 via-purple-500/5 to-transparent animate-gradient" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(251,146,60,0.12),transparent_50%)]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_60%,rgba(168,85,247,0.08),transparent_50%)]" />

          {/* Floating orbs for depth */}
          <motion.div
            className="absolute top-1/4 left-1/4 w-96 h-96 bg-orange-500/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
            animate={{
              scale: [1.2, 1, 1.2],
              opacity: [0.5, 0.3, 0.5],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />

          <div className="relative max-w-6xl mx-auto text-center">
            {/* Enhanced trust indicator with glassmorphism */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              whileHover={{ scale: 1.05 }}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 backdrop-blur-xl rounded-full border border-white/20 mb-8 shadow-lg shadow-orange-500/10 hover:shadow-orange-500/20 transition-all duration-300"
            >
              <motion.div
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                <Shield className="w-4 h-4 text-orange-400" />
              </motion.div>
              <span className="text-xs text-gray-200 font-semibold tracking-wide">Enterprise-Grade Revenue Recovery Platform</span>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            </motion.div>

            {/* Enhanced premium headline with better typography */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-5xl md:text-6xl lg:text-8xl font-bold tracking-tight mb-6 leading-[1.05]"
            >
              <motion.span
                className="block text-white mb-3 drop-shadow-2xl"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.5 }}
              >
                Recover Dormant Pipeline.
              </motion.span>
              <motion.span
                className="block bg-gradient-to-r from-orange-400 via-orange-500 to-pink-500 bg-clip-text text-transparent animate-gradient-x"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
              >
                Generate Revenue on Autopilot.
              </motion.span>
            </motion.h1>

            {/* Value proposition */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto mb-12 leading-relaxed"
            >
              AI-powered multi-channel outreach that transforms dormant leads into booked meetings.
              <span className="block mt-2 text-gray-400 text-lg">Performance-based pricing. You only pay when we deliver results.</span>
            </motion.p>

            {/* Primary CTA */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
              className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
            >
              <PremiumButton
                variant="primary"
                onClick={() => navigate('/pilot-application')}
              >
                Request Platform Access
                <ArrowRight className="w-5 h-5" />
              </PremiumButton>
              <PremiumButton variant="secondary">
                View Live Dashboard
                <BarChart3 className="w-5 h-5" />
              </PremiumButton>
            </motion.div>

            {/* Trust metrics */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto"
            >
              <MetricCard value={15.2} label="Meeting Rate" suffix="%" delay={100} />
              <MetricCard value={72} label="Hours to First Meeting" delay={200} />
              <MetricCard value={98} label="Message Delivery" suffix="%" delay={300} />
              <MetricCard value={2.3} label="Industry Average" suffix="x" delay={400} />
            </motion.div>
          </div>
        </motion.section>

        {/* PROBLEM: DATA-DRIVEN PAIN */}
        {/* Emotional Goal: Awareness - Understand the cost of inaction */}
        <section className="relative py-32 px-6 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-900/50 to-transparent" />

          <div className="relative max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 tracking-tight">
                Your CRM Contains £500K-£2M
                <span className="block text-gray-400 mt-2">In Unmonetized Opportunity</span>
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
                Leads that engaged, downloaded content, even took calls—then went silent.
                Not because they weren't interested. Because the timing wasn't right.
              </p>
            </motion.div>

            {/* Data visualization */}
            <div className="grid md:grid-cols-3 gap-6">
              {[
                { title: "Dormant Leads", value: "4,250", description: "Average B2B SaaS CRM (5K-20K employees)", color: "from-red-500/20 to-red-600/10", border: "border-red-500/20" },
                { title: "Acquisition Cost", value: "£2,400", description: "Per enterprise lead (avg)", color: "from-orange-500/20 to-orange-600/10", border: "border-orange-500/20" },
                { title: "Recovery Rate", value: "15.2%", description: "With AI multi-channel approach", color: "from-green-500/20 to-green-600/10", border: "border-green-500/20" }
              ].map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className={`p-8 bg-gradient-to-br ${stat.color} backdrop-blur-sm rounded-2xl border ${stat.border}`}
                >
                  <div className="text-5xl font-bold text-white mb-3 tabular-nums">{stat.value}</div>
                  <div className="text-lg font-semibold text-white mb-2">{stat.title}</div>
                  <div className="text-sm text-gray-400">{stat.description}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* SOLUTION: TRANSPARENT PROCESS */}
        {/* Emotional Goal: Control - AI is overseen by them */}
        <section className="relative py-32 px-6" id="solution">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 backdrop-blur-sm rounded-full border border-white/10 mb-6">
                <Eye className="w-4 h-4 text-orange-400" />
                <span className="text-xs text-gray-300 font-medium">Full Transparency & Control</span>
              </div>
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 tracking-tight">
                How It Works
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                AI-powered automation with human oversight at every step.
              </p>
            </motion.div>

            {/* Process timeline */}
            <div className="space-y-12">
              {[
                {
                  step: "01",
                  title: "CRM Integration",
                  description: "Secure API connection to your CRM. We analyze dormant leads based on last activity, engagement score, and deal stage.",
                  time: "10 minutes",
                  icon: Users
                },
                {
                  step: "02",
                  title: "AI Research & Personalization",
                  description: "Our AI researches each lead: recent company news, funding rounds, job changes, industry trends. Crafts personalized hooks.",
                  time: "12-18 hours",
                  icon: BarChart3
                },
                {
                  step: "03",
                  title: "Multi-Channel Sequence",
                  description: "Intelligent outreach via Email, SMS, WhatsApp, and Voicemail. Adaptive timing based on engagement signals.",
                  time: "7-14 days",
                  icon: Mail
                },
                {
                  step: "04",
                  title: "Meeting Booked",
                  description: "Lead responds and meeting is automatically scheduled. You only pay when the meeting is confirmed.",
                  time: "72 hours avg",
                  icon: CheckCircle2
                }
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="flex gap-8 items-start group"
                >
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-gradient-to-br from-orange-500/20 to-orange-600/10 rounded-2xl border border-orange-500/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <item.icon className="w-8 h-8 text-orange-400" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <span className="text-sm font-mono text-orange-400">{item.step}</span>
                      <span className="text-sm text-gray-500">•</span>
                      <span className="text-sm font-mono text-gray-500">{item.time}</span>
                    </div>
                    <h3 className="text-2xl font-semibold text-white mb-2">{item.title}</h3>
                    <p className="text-gray-400 leading-relaxed">{item.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* MULTI-CHANNEL: CLEAN DATA VISUALIZATION */}
        {/* Emotional Goal: Confidence in multi-channel approach */}
        <section className="relative py-32 px-6 bg-gradient-to-b from-transparent via-slate-900/30 to-transparent">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 tracking-tight">
                Multi-Channel Intelligence
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Reach leads where they're most responsive. Data from 847 campaigns.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-4 gap-6">
              {[
                { channel: "Email", icon: Mail, open: "62%", reply: "14%", meeting: "15.2%", color: "blue" },
                { channel: "SMS", icon: MessageSquare, open: "98%", reply: "12%", meeting: "3.2%", color: "green" },
                { channel: "WhatsApp", icon: MessageSquare, open: "95%", reply: "18%", meeting: "4.5%", color: "emerald" },
                { channel: "Voicemail", icon: Phone, open: "72%", reply: "6%", meeting: "1.5%", color: "orange" }
              ].map((channel, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/20 transition-all duration-300"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <div className={`p-2 bg-${channel.color}-500/20 rounded-lg`}>
                      <channel.icon className={`w-5 h-5 text-${channel.color}-400`} />
                    </div>
                    <span className="font-semibold text-white">{channel.channel}</span>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-xs text-gray-400">Open Rate</span>
                        <span className="text-xs font-mono text-white">{channel.open}</span>
                      </div>
                      <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                        <div className={`h-full bg-${channel.color}-500`} style={{ width: channel.open }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-xs text-gray-400">Reply Rate</span>
                        <span className="text-xs font-mono text-white">{channel.reply}</span>
                      </div>
                      <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                        <div className={`h-full bg-${channel.color}-500`} style={{ width: channel.reply }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-xs text-gray-400">Meeting Rate</span>
                        <span className="text-xs font-mono text-orange-400 font-semibold">{channel.meeting}</span>
                      </div>
                      <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                        <div className={`h-full bg-gradient-to-r from-orange-500 to-orange-600`} style={{ width: channel.meeting }} />
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* PROOF & METRICS */}
        {/* Emotional Goal: Trust through verified results */}
        <section className="relative py-32 px-6" id="proof">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 tracking-tight">
                Verified Results
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Data from 847 leads across Q4 2024. Enterprise SaaS clients only.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-12">
              {/* Metric comparison */}
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                className="space-y-8"
              >
                <div>
                  <div className="flex items-end gap-4 mb-3">
                    <div className="text-6xl font-bold text-orange-400 tabular-nums">15.2%</div>
                    <div className="pb-2 text-gray-400">vs industry avg 6-8%</div>
                  </div>
                  <div className="text-lg text-white font-semibold mb-2">Meeting Booking Rate</div>
                  <div className="text-gray-400">Verified across 847 dormant leads, Q4 2024</div>
                </div>

                <div>
                  <div className="flex items-end gap-4 mb-3">
                    <div className="text-6xl font-bold text-orange-400 tabular-nums">72hr</div>
                    <div className="pb-2 text-gray-400">avg first meeting</div>
                  </div>
                  <div className="text-lg text-white font-semibold mb-2">Time to Revenue</div>
                  <div className="text-gray-400">Industry standard: 2-3 weeks</div>
                </div>
              </motion.div>

              {/* Trust indicators */}
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                className="space-y-4"
              >
                <TrustBadge
                  icon={Shield}
                  title="SOC 2 Type II Certified"
                  subtitle="Enterprise-grade security"
                />
                <TrustBadge
                  icon={Lock}
                  title="GDPR Compliant"
                  subtitle="Full data protection & privacy"
                />
                <TrustBadge
                  icon={Eye}
                  title="Approval Mode Available"
                  subtitle="Review every message before sending"
                />
                <TrustBadge
                  icon={Zap}
                  title="99.9% Uptime SLA"
                  subtitle="Enterprise reliability guarantee"
                />
              </motion.div>
            </div>
          </div>
        </section>

        {/* PILOT OFFER: PREMIUM FRAMING */}
        {/* Emotional Goal: Exclusivity - Access is limited */}
        <section className="relative py-32 px-6" id="pricing">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-500/10 backdrop-blur-sm rounded-full border border-orange-500/20 mb-6">
                <Clock className="w-4 h-4 text-orange-400" />
                <span className="text-sm text-orange-300 font-medium">Limited Access Program</span>
              </div>
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 tracking-tight">
                Performance-Based Pricing
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Pay only when we deliver results. No upfront risk.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="p-12 bg-gradient-to-br from-white/5 to-white/[0.02] backdrop-blur-sm rounded-3xl border border-white/10"
            >
              <div className="grid md:grid-cols-2 gap-12">
                <div>
                  <div className="mb-8">
                    <div className="text-gray-400 text-sm mb-2">Platform Access</div>
                    <div className="text-6xl font-bold text-white mb-2 tabular-nums">£99</div>
                    <div className="text-gray-400">per month</div>
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
                      <div className="text-gray-300">Unlimited dormant lead analysis</div>
                    </div>
                    <div className="flex items-start gap-3">
                      <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
                      <div className="text-gray-300">AI research & personalization</div>
                    </div>
                    <div className="flex items-start gap-3">
                      <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
                      <div className="text-gray-300">Multi-channel automation</div>
                    </div>
                    <div className="flex items-start gap-3">
                      <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
                      <div className="text-gray-300">Real-time analytics dashboard</div>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="mb-8">
                    <div className="text-gray-400 text-sm mb-2">Performance Fee</div>
                    <div className="text-6xl font-bold bg-gradient-to-r from-orange-400 to-orange-600 bg-clip-text text-transparent mb-2 tabular-nums">2.5%</div>
                    <div className="text-gray-400">of ACV per booked meeting</div>
                  </div>
                  <div className="p-6 bg-orange-500/10 rounded-2xl border border-orange-500/20">
                    <div className="text-sm text-orange-300 mb-3 font-medium">Example: £10K ACV Deal</div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between text-gray-400">
                        <span>Platform fee (monthly)</span>
                        <span className="font-mono">£99</span>
                      </div>
                      <div className="flex justify-between text-gray-400">
                        <span>Performance fee (one-time)</span>
                        <span className="font-mono">£250</span>
                      </div>
                      <div className="border-t border-orange-500/20 my-2" />
                      <div className="flex justify-between text-orange-400 font-semibold">
                        <span>Cost per qualified meeting</span>
                        <span className="font-mono">£349</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-2">
                        vs £2,400 avg acquisition cost
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-12 text-center">
                <PremiumButton
                  variant="primary"
                  size="lg"
                  onClick={() => navigate('/pilot-application')}
                >
                  Request Platform Access
                  <ArrowRight className="w-5 h-5" />
                </PremiumButton>
                <div className="text-sm text-gray-400 mt-4">
                  Pilot program • Qualified B2B SaaS teams only
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* TRUST & COMPLIANCE */}
        {/* Emotional Goal: Security and control */}
        <section className="relative py-32 px-6 bg-gradient-to-b from-transparent via-slate-900/30 to-transparent">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
                Enterprise-Grade Security
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Your data, your control. Full transparency at every step.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  title: "Data Encryption",
                  description: "AES-256 encryption at rest and in transit. Your data never leaves your region.",
                  icon: Lock
                },
                {
                  title: "Approval Mode",
                  description: "Review and approve every message before it's sent. Full oversight.",
                  icon: Eye
                },
                {
                  title: "Your Domain",
                  description: "All messages sent from your verified domain. Complete brand control.",
                  icon: Shield
                }
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="p-8 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 text-center"
                >
                  <div className="inline-flex p-4 bg-gradient-to-br from-orange-500/20 to-orange-600/10 rounded-2xl mb-6">
                    <item.icon className="w-8 h-8 text-orange-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">{item.title}</h3>
                  <p className="text-gray-400 leading-relaxed">{item.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* COMPARISON TABLE */}
        {/* Emotional Goal: Confidence in superiority */}
        <section className="relative py-32 px-6">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
                Why Rekindle
              </h2>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="overflow-hidden rounded-2xl border border-white/10"
            >
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="p-6 text-left text-gray-400 font-medium">Feature</th>
                    <th className="p-6 text-center bg-orange-500/5">
                      <div className="text-white font-semibold">Rekindle</div>
                    </th>
                    <th className="p-6 text-center text-gray-400 font-medium">Traditional SDR</th>
                    <th className="p-6 text-center text-gray-400 font-medium">Generic AI Tools</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["Cost per meeting", "£349", "£2,400+", "£800-1,200"],
                    ["Time to first meeting", "72 hours", "2-3 weeks", "1-2 weeks"],
                    ["Meeting rate", "15.2%", "6-8%", "8-10%"],
                    ["Multi-channel", "✓", "Limited", "Email only"],
                    ["AI personalization", "✓", "✗", "Basic"],
                    ["Approval mode", "✓", "✓", "✗"],
                    ["Your domain", "✓", "✓", "✗"]
                  ].map((row, index) => (
                    <tr key={index} className="border-b border-white/5">
                      <td className="p-6 text-gray-300">{row[0]}</td>
                      <td className="p-6 text-center bg-orange-500/5 text-orange-400 font-semibold">{row[1]}</td>
                      <td className="p-6 text-center text-gray-400">{row[2]}</td>
                      <td className="p-6 text-center text-gray-400">{row[3]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </motion.div>
          </div>
        </section>

        {/* FINAL CTA */}
        {/* Emotional Goal: Confident action */}
        <section className="relative py-32 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 tracking-tight">
                Ready to Recover Your Pipeline?
              </h2>
              <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
                Join qualified B2B SaaS teams using AI to transform dormant leads into revenue.
              </p>
              <PremiumButton
                variant="primary"
                size="lg"
                onClick={() => navigate('/pilot-application')}
              >
                Request Platform Access
                <ArrowRight className="w-5 h-5" />
              </PremiumButton>
              <div className="text-sm text-gray-400 mt-6">
                Platform fee: £99/month • Performance fee: 2.5% ACV per meeting
              </div>
            </motion.div>
          </div>
        </section>

        {/* FOOTER */}
        <footer className="relative border-t border-white/5 py-12 px-6">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-4 gap-8 mb-8">
              <div>
                <img src="/images/image copy copy.png" alt="Rekindle" className="h-8 w-auto mb-4" />
                <p className="text-sm text-gray-400">
                  Enterprise revenue recovery platform
                </p>
              </div>
              <div>
                <h4 className="text-white font-semibold mb-4">Platform</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="#solution" className="hover:text-white transition-colors">How It Works</a></li>
                  <li><a href="#proof" className="hover:text-white transition-colors">Results</a></li>
                  <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-white font-semibold mb-4">Company</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="/privacy" className="hover:text-white transition-colors">Privacy Policy</a></li>
                  <li><a href="/terms" className="hover:text-white transition-colors">Terms of Service</a></li>
                  <li><a href="/security" className="hover:text-white transition-colors">Security</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-white font-semibold mb-4">Get Started</h4>
                <PremiumButton
                  variant="primary"
                  size="md"
                  onClick={() => navigate('/pilot-application')}
                >
                  Apply for Access
                </PremiumButton>
              </div>
            </div>
            <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="text-sm text-gray-500">
                © 2024 Rekindle. All rights reserved.
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>SOC 2 Type II</span>
                <span>•</span>
                <span>GDPR Compliant</span>
              </div>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
