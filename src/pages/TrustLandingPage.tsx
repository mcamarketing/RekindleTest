// TRUST-FIRST LANDING PAGE - Stripe/Linear-Inspired Minimalism
// Zero hype. Pure clarity, data, and confidence.
import { useState, useEffect, useRef } from 'react';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';
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
    primary: 'bg-white text-black hover:bg-gray-100 shadow-sm',
    secondary: 'bg-black/5 text-black hover:bg-black/10 border border-black/10'
  };

  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] ${variants[variant]} ${className}`}
    >
      {children}
    </button>
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
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <div className="min-h-screen bg-white">
      {/* NAVIGATION - Ultra-minimal */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-black/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <img
              src="/images/image copy copy.png"
              alt="Rekindle"
              className="h-8 w-auto"
            />
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
        <section className="relative min-h-[90vh] flex items-center justify-center px-6 py-32 overflow-hidden">
          {/* Subtle animated gradient background */}
          <div className="absolute inset-0 bg-gradient-to-b from-orange-50/30 via-white to-white" />

          {/* Animated glow effect */}
          <motion.div
            className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-r from-orange-200/20 via-orange-300/20 to-orange-200/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.1, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />

          {/* Subtle grid pattern */}
          <div className="absolute inset-0 opacity-[0.015]" style={{
            backgroundImage: 'radial-gradient(circle, rgba(0,0,0,0.3) 1px, transparent 1px)',
            backgroundSize: '40px 40px'
          }} />

          <div className="relative max-w-5xl mx-auto text-center">
            {/* Trust badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-black/5 rounded-full mb-8 text-sm text-black/60"
            >
              <Shield className="w-4 h-4" />
              <span>SOC 2 Type II Certified</span>
            </motion.div>

            {/* Headline - Large, clear with subtle gradient accent */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-8 leading-[1.1]"
              style={{ letterSpacing: '-0.04em' }}
            >
              <span className="block text-black mb-2">
                Recover dormant pipeline.
              </span>
              <span className="block bg-gradient-to-r from-black/40 via-orange-600/60 to-black/40 bg-clip-text text-transparent">
                Generate revenue.
              </span>
            </motion.h1>

            {/* Value prop - Clear, no hype */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="text-xl md:text-2xl text-black/60 max-w-3xl mx-auto mb-12 leading-relaxed"
            >
              AI-powered outreach that transforms dormant leads into booked meetings.
              <span className="block mt-2 text-lg text-black/40">You only pay when we deliver results.</span>
            </motion.p>

            {/* CTA - Single, clear action */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center mb-20"
            >
              <MinimalButton variant="primary" onClick={() => navigate('/pilot-application')}>
                Request Platform Access
                <ArrowRight className="w-4 h-4" />
              </MinimalButton>
              <MinimalButton variant="secondary">
                View Dashboard Demo
                <BarChart3 className="w-4 h-4" />
              </MinimalButton>
            </motion.div>

            {/* Metrics - Clean, data-first */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto pt-12 border-t border-black/5"
            >
              {[
                { value: 15.2, suffix: '%', label: 'Meeting rate' },
                { value: 72, label: 'Hours to first meeting' },
                { value: 98, suffix: '%', label: 'Delivery rate' },
                { value: 847, label: 'Leads analyzed Q4 2024' }
              ].map((metric, i) => (
                <div key={i} className="text-center">
                  <div className="text-4xl font-bold text-black mb-2 tabular-nums">
                    <Counter end={metric.value} suffix={metric.suffix || ''} />
                  </div>
                  <div className="text-sm text-black/40">{metric.label}</div>
                </div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* PROBLEM - Data-driven, factual */}
        <section className="relative py-32 px-6 bg-black text-white">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="mb-20"
            >
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-8" style={{ letterSpacing: '-0.03em' }}>
                Your CRM contains
                <span className="block text-white/40 mt-2">£500K–£2M in dormant leads</span>
              </h2>
              <p className="text-xl text-white/60 max-w-2xl leading-relaxed">
                Leads that engaged, downloaded content, even took calls. Then went silent.
                Not because they weren't interested—because the timing wasn't right.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                { value: '4,250', label: 'Average dormant leads', sub: 'B2B SaaS CRM (5K-20K employees)' },
                { value: '£2,400', label: 'Cost per enterprise lead', sub: 'Industry average acquisition cost' },
                { value: '85%', label: 'Wasted opportunity', sub: 'Never re-engaged or monetized' }
              ].map((stat, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  className="p-8 bg-white/5 rounded-2xl border border-white/10"
                >
                  <div className="text-5xl font-bold text-white mb-3 tabular-nums">{stat.value}</div>
                  <div className="text-lg font-semibold text-white mb-2">{stat.label}</div>
                  <div className="text-sm text-white/40">{stat.sub}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* SOLUTION - Transparent process */}
        <section className="relative py-32 px-6" id="platform">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-black/5 rounded-full mb-6 text-sm text-black/60">
                <Eye className="w-4 h-4" />
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
                  time: '10 minutes'
                },
                {
                  step: '02',
                  title: 'AI Research',
                  desc: 'Research company news, funding, job changes, industry trends. Craft personalized messaging.',
                  time: '12-18 hours'
                },
                {
                  step: '03',
                  title: 'Multi-Channel Outreach',
                  desc: 'Intelligent sequences via Email, SMS, WhatsApp, Voicemail. Adaptive timing based on engagement.',
                  time: '7-14 days'
                },
                {
                  step: '04',
                  title: 'Meeting Booked',
                  desc: 'Lead responds, meeting automatically scheduled. You only pay when confirmed.',
                  time: '72 hours avg'
                }
              ].map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  whileHover={{ scale: 1.02, y: -4 }}
                  className="group relative min-h-[240px] p-8 bg-gradient-to-br from-white to-black/[0.02] rounded-2xl border border-black/5 hover:border-black/10 hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden"
                >
                  {/* Hover glow effect */}
                  <div className="absolute inset-0 bg-gradient-to-br from-orange-50/0 to-orange-50/50 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                  <div className="relative">
                    <div className="flex items-start justify-between mb-4">
                      <div className="text-5xl font-bold bg-gradient-to-br from-black to-black/40 bg-clip-text text-transparent tabular-nums">{item.step}</div>
                      <span className="text-xs text-black/40 bg-black/5 px-3 py-1 rounded-full tabular-nums">{item.time}</span>
                    </div>
                    <h3 className="text-2xl font-bold text-black mb-3 group-hover:text-orange-600 transition-colors">{item.title}</h3>
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
                  className="group p-6 bg-white rounded-2xl border border-black/5 hover:border-black/10 hover:shadow-2xl transition-all duration-300 cursor-pointer"
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
                  className="group flex items-center gap-4 p-6 bg-gradient-to-br from-white to-black/[0.02] rounded-2xl border border-black/5 hover:border-black/10 hover:shadow-xl transition-all duration-300 cursor-pointer"
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

        {/* PRICING - Clear, transparent */}
        <section className="relative py-32 px-6 bg-black text-white" id="pricing">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6" style={{ letterSpacing: '-0.03em' }}>
                Performance-based pricing
              </h2>
              <p className="text-xl text-white/60 max-w-2xl mx-auto">
                Pay only when we deliver results. No upfront risk.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="p-12 bg-white/5 rounded-3xl border border-white/10"
            >
              <div className="grid md:grid-cols-2 gap-12 mb-12">
                <div>
                  <div className="text-white/40 text-sm mb-2">Platform Access</div>
                  <div className="text-7xl font-bold text-white mb-2 tabular-nums">£99</div>
                  <div className="text-white/40 mb-8">per month</div>
                  <div className="space-y-3">
                    {['Unlimited lead analysis', 'AI research & personalization', 'Multi-channel automation', 'Real-time analytics'].map((feature, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
                        <span className="text-white/80">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-white/40 text-sm mb-2">Performance Fee</div>
                  <div className="text-7xl font-bold text-white mb-2 tabular-nums">2.5%</div>
                  <div className="text-white/40 mb-8">of ACV per meeting</div>
                  <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
                    <div className="text-sm text-white/60 mb-4">Example: £10K ACV Deal</div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between text-white/60">
                        <span>Platform (monthly)</span>
                        <span className="tabular-nums">£99</span>
                      </div>
                      <div className="flex justify-between text-white/60">
                        <span>Performance (one-time)</span>
                        <span className="tabular-nums">£250</span>
                      </div>
                      <div className="border-t border-white/10 my-3" />
                      <div className="flex justify-between text-white font-semibold">
                        <span>Total per meeting</span>
                        <span className="tabular-nums">£349</span>
                      </div>
                      <div className="text-xs text-white/40 mt-2">vs £2,400 avg acquisition cost</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="text-center">
                <button
                  onClick={() => navigate('/pilot-application')}
                  className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-black rounded-lg font-semibold hover:bg-gray-100 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
                >
                  Request Platform Access
                  <ArrowRight className="w-4 h-4" />
                </button>
                <div className="text-sm text-white/40 mt-4">
                  Pilot program · Qualified B2B SaaS teams only
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
                Why Rekindle
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
                      <div className="font-bold text-black">Rekindle</div>
                    </th>
                    <th className="p-4 text-center text-sm font-semibold text-black/40">SDR Team</th>
                    <th className="p-4 text-center text-sm font-semibold text-black/40">AI Tools</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ['Cost per meeting', '£349', '£2,400+', '£800-1,200'],
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

        {/* FINAL CTA - Clean, confident */}
        <section className="relative py-32 px-6 bg-black/[0.02]">
          <div className="max-w-3xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6" style={{ letterSpacing: '-0.03em' }}>
                Start recovering pipeline today
              </h2>
              <p className="text-xl text-black/60 mb-12 max-w-2xl mx-auto">
                Join qualified B2B SaaS teams using AI to transform dormant leads into revenue.
              </p>
              <MinimalButton variant="primary" onClick={() => navigate('/pilot-application')}>
                Request Platform Access
                <ArrowRight className="w-4 h-4" />
              </MinimalButton>
              <div className="text-sm text-black/40 mt-6">
                £99/month platform fee · 2.5% ACV per meeting
              </div>
            </motion.div>
          </div>
        </section>

        {/* FOOTER */}
        <footer className="relative border-t border-black/5 py-12 px-6">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-4 gap-8 mb-8">
              <div>
                <img src="/images/image copy copy.png" alt="Rekindle" className="h-6 w-auto mb-4" />
                <p className="text-sm text-black/40">Enterprise revenue recovery platform</p>
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
              <div>© 2024 Rekindle. All rights reserved.</div>
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
