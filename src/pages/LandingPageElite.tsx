// RekindlePro - Stripe/Linear/Apple Quality Landing Page
// Ultra-clean, visual-driven, enterprise-grade
// @ts-nocheck
import '../styles/animations.css';
import { useState, useEffect } from 'react';
import {
  ArrowRight,
  CheckCircle,
  Shield,
  Lock,
  Zap,
  TrendingUp,
  Users,
  Target,
  BarChart3,
  Mail,
  MessageSquare,
  Phone
} from 'lucide-react';

// ============================================================================
// NAVIGATION - Stripe-minimal with scroll effect
// ============================================================================
const Navigation = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled
        ? 'bg-slate-950/90 backdrop-blur-xl border-b border-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]'
        : 'bg-slate-950/80 backdrop-blur-xl border-b border-white/5'
    }`}>
      <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
        <div className="flex items-center gap-12">
          <img
            src="/images/image copy copy.png"
            alt="Rekindle"
            className="h-8 w-auto"
          />
          <div className="hidden md:flex items-center gap-8 text-sm">
            <a href="#features" className="text-gray-400 hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</a>
            <a href="#security" className="text-gray-400 hover:text-white transition-colors">Security</a>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/login')}
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Sign in
          </button>
          <button
            onClick={() => navigate('/pilot-application')}
            className="px-5 py-2.5 bg-white text-slate-950 rounded-lg text-sm font-medium hover:bg-gray-100 hover:scale-[1.02] transition-all duration-200 shadow-sm hover:shadow-md"
          >
            Get started
          </button>
        </div>
      </div>
    </nav>
  );
};

// ============================================================================
// HERO - Massive whitespace, single value prop
// ============================================================================
const Hero = () => {
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center px-6 pt-40 pb-32">
      {/* Subtle background */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />
      <div className="absolute inset-0 linear-grid opacity-10" />

      {/* Brand accent - subtle orange glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-r from-orange-500/8 via-orange-600/5 to-orange-500/8 blur-[120px]" />
      <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[300px] bg-gradient-to-l from-blue-500/5 to-transparent blur-[100px]" />

      <div className="max-w-5xl mx-auto text-center relative z-10">
        {/* Pilot badge - subtle with brand accent */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-12 hover:bg-white/8 hover:border-white/15 transition-all duration-300 group">
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 group-hover:animate-pulse" />
          <span className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">Pilot Program Open</span>
        </div>

        {/* Massive headline - Stripe/Linear sizing with enhanced spacing */}
        <h1 className="text-6xl md:text-7xl lg:text-8xl font-black text-white mb-10 leading-[1.05] tracking-tight">
          Revenue recovery,<br />automated.
        </h1>

        {/* Clean subhead with enhanced line-height */}
        <p className="text-xl md:text-2xl text-gray-400 mb-16 max-w-3xl mx-auto leading-[1.6] font-light">
          AI-powered multi-channel follow-up that transforms dormant leads into qualified meetings.
          Enterprise-grade deliverability. Exceptional results.
        </p>

        {/* Single CTA - Premium microinteractions */}
        <div className="flex items-center justify-center gap-4 mb-20">
          <button
            onClick={() => navigate('/pilot-application')}
            className="group px-8 py-4 bg-white text-slate-950 rounded-xl font-semibold hover:bg-gray-100 hover:scale-[1.01] transition-all duration-200 flex items-center gap-2 shadow-lg hover:shadow-xl"
          >
            Start free trial
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
          </button>
          <button className="px-8 py-4 bg-white/5 text-white rounded-xl font-semibold hover:bg-white/10 hover:scale-[1.01] transition-all duration-200 border border-white/10">
            View demo
          </button>
        </div>

        {/* Trust - ultra-minimal */}
        <div className="flex items-center justify-center gap-8 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            <span>SOC 2 Type II</span>
          </div>
          <div className="w-px h-4 bg-white/10" />
          <div className="flex items-center gap-2">
            <Lock className="w-4 h-4" />
            <span>GDPR Compliant</span>
          </div>
          <div className="w-px h-4 bg-white/10" />
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            <span>Enterprise Security</span>
          </div>
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// STATS BAR - Linear-style clean metrics with enhanced spacing
// ============================================================================
const StatsBar = () => (
  <section className="relative py-32 px-6">
    <div className="max-w-6xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-16 md:gap-12">
        <div className="text-center group">
          <div className="text-6xl md:text-5xl font-black text-white mb-4 group-hover:text-orange-400 transition-colors duration-300">15.2%</div>
          <div className="text-gray-400 text-sm mb-2 leading-relaxed">Meeting rate</div>
          <div className="text-gray-600 text-xs leading-relaxed">Industry avg: 6-8%</div>
        </div>
        <div className="text-center group">
          <div className="text-6xl md:text-5xl font-black text-white mb-4 group-hover:text-orange-400 transition-colors duration-300">8.4x</div>
          <div className="text-gray-400 text-sm mb-2 leading-relaxed">Average ROI</div>
          <div className="text-gray-600 text-xs leading-relaxed">First 90 days</div>
        </div>
        <div className="text-center group">
          <div className="text-6xl md:text-5xl font-black text-white mb-4 group-hover:text-orange-400 transition-colors duration-300">98%</div>
          <div className="text-gray-400 text-sm mb-2 leading-relaxed">Deliverability</div>
          <div className="text-gray-600 text-xs leading-relaxed">Enterprise infrastructure</div>
        </div>
      </div>
    </div>
  </section>
);

// ============================================================================
// VISUAL DEMO - Show product (placeholder for now)
// ============================================================================
const ProductDemo = () => {
  const [hoveredStat, setHoveredStat] = useState<number | null>(null);

  return (
    <section className="relative py-40 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Clean title */}
        <div className="text-center mb-20">
          <h2 className="text-5xl md:text-6xl font-black text-white mb-6 leading-tight">
            Intelligence that works<br />while you focus on closing.
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Automated trigger detection, hyper-personalized outreach, and seamless calendar booking.
          </p>
        </div>

        {/* Product visual placeholder */}
        <div className="relative glass-premium rounded-3xl p-4 border border-white/10 shadow-[0_40px_100px_rgba(0,0,0,0.4)]">
          {/* Browser chrome */}
          <div className="flex items-center gap-2 mb-4 px-4 py-3 bg-white/5 rounded-t-2xl border-b border-white/10">
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
            </div>
            <div className="flex-1 text-center">
              <div className="inline-block px-6 py-1 bg-white/5 rounded-lg text-gray-400 text-sm">
                app.rekindlepro.com/dashboard
              </div>
            </div>
          </div>

          {/* Dashboard preview */}
          <div className="relative aspect-[16/10] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl overflow-hidden">
            <div className="absolute inset-0 linear-grid opacity-20" />

            {/* Simplified dashboard elements */}
            <div className="absolute inset-0 p-12">
              <div className="grid grid-cols-3 gap-6 mb-8">
                {[
                  { label: 'Active Sequences', value: '12', color: 'from-blue-400 to-blue-600', tooltip: 'AI detected signal' },
                  { label: 'Meetings Booked', value: '47', color: 'from-green-400 to-green-600', tooltip: 'Meeting scheduled' },
                  { label: 'Response Rate', value: '18.4%', color: 'from-orange-400 to-orange-600', tooltip: 'Industry avg: 6-8%' }
                ].map((stat, idx) => (
                  <div
                    key={idx}
                    className="relative glass-premium rounded-2xl p-6 hover:scale-[1.02] hover:-translate-y-1 transition-all duration-300 cursor-pointer group"
                    onMouseEnter={() => setHoveredStat(idx)}
                    onMouseLeave={() => setHoveredStat(null)}
                  >
                    {hoveredStat === idx && (
                      <div className="absolute -top-10 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-slate-800 border border-white/10 rounded-lg text-xs text-gray-300 whitespace-nowrap animate-spring-in">
                        {stat.tooltip}
                      </div>
                    )}
                    <div className="text-gray-400 text-sm mb-2 group-hover:text-gray-300 transition-colors">{stat.label}</div>
                    <div className={`text-4xl font-black bg-gradient-to-br ${stat.color} bg-clip-text text-transparent`}>
                      {stat.value}
                    </div>
                  </div>
                ))}
              </div>

              {/* Chart visualization */}
              <div className="glass-premium rounded-2xl p-6 h-48 flex items-end gap-2">
                {Array.from({ length: 12 }).map((_, idx) => (
                  <div
                    key={idx}
                    className="flex-1 bg-gradient-to-t from-orange-500 to-orange-600 rounded-t-lg"
                    style={{ height: `${Math.random() * 80 + 20}%` }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// FEATURES - Bento grid layout (Apple/Linear style)
// ============================================================================
const Features = () => {
  const features = [
    {
      icon: Zap,
      title: 'AI-powered trigger detection',
      description: 'Monitors job changes, funding rounds, and buying signals across your pipeline.',
      span: 'md:col-span-2'
    },
    {
      icon: Mail,
      title: 'Multi-channel orchestration',
      description: 'Email, SMS, LinkedIn, WhatsApp, and voice—sequenced intelligently.',
      span: 'md:col-span-1'
    },
    {
      icon: Target,
      title: 'Hyper-personalization',
      description: 'Every message references recent company news, role changes, and context.',
      span: 'md:col-span-1'
    },
    {
      icon: BarChart3,
      title: 'Real-time analytics',
      description: 'Track engagement, optimize sequences, and measure ROI across every channel.',
      span: 'md:col-span-2'
    }
  ];

  return (
    <section className="relative py-40 px-6" id="features">
      <div className="max-w-7xl mx-auto">
        {/* Section title with enhanced spacing */}
        <div className="mb-20">
          <h2 className="text-5xl md:text-6xl font-black text-white mb-6 leading-tight tracking-tight">
            Built for enterprise performance.
          </h2>
          <p className="text-xl text-gray-400 leading-relaxed">
            Advanced automation that respects your brand and delivers results.
          </p>
        </div>

        {/* Bento grid with microinteractions */}
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className={`group glass-premium rounded-3xl p-10 hover:bg-white/5 hover:-translate-y-1 hover:shadow-[0_20px_50px_rgba(0,0,0,0.3)] transition-all duration-300 ${feature.span}`}
            >
              <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 group-hover:bg-white/10 transition-all duration-300">
                <feature.icon className="w-6 h-6 text-white group-hover:text-orange-400 transition-colors duration-300" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-4 leading-tight">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// HOW IT WORKS - Visual timeline (Linear-style)
// ============================================================================
const HowItWorks = () => {
  const steps = [
    {
      number: '01',
      title: 'Connect your CRM',
      description: 'Sync your pipeline in minutes. We support Salesforce, HubSpot, and custom integrations.'
    },
    {
      number: '02',
      title: 'AI analyzes triggers',
      description: 'Our intelligence layer monitors job changes, funding, and engagement signals.'
    },
    {
      number: '03',
      title: 'Personalized outreach',
      description: 'Multi-channel sequences launch automatically with context-aware messaging.'
    },
    {
      number: '04',
      title: 'Meetings booked',
      description: 'Qualified leads schedule directly to your calendar. You show up and close.'
    }
  ];

  return (
    <section className="relative py-40 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Title with enhanced spacing */}
        <div className="text-center mb-28">
          <h2 className="text-5xl md:text-6xl font-black text-white mb-8 leading-tight tracking-tight">
            Effortless implementation.
          </h2>
          <p className="text-xl text-gray-400 leading-relaxed">
            From connection to first meeting in under 72 hours.
          </p>
        </div>

        {/* Steps with enhanced interaction */}
        <div className="space-y-20">
          {steps.map((step, idx) => (
            <div key={idx} className="group flex items-start gap-8 hover:-translate-y-1 transition-all duration-300">
              <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0 group-hover:bg-white/10 group-hover:border-orange-400/30 transition-all duration-300">
                <span className="text-2xl font-black text-white group-hover:text-orange-400 transition-colors">{step.number}</span>
              </div>
              <div className="flex-1 pt-3">
                <h3 className="text-3xl font-bold text-white mb-4 leading-tight">{step.title}</h3>
                <p className="text-xl text-gray-400 leading-[1.7] group-hover:text-gray-300 transition-colors">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// PRICING - Stripe-clean cards
// ============================================================================
const Pricing = () => {
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const plans = [
    {
      name: 'Starter',
      description: 'For small teams testing the waters',
      originalPrice: '£29.99',
      price: '£14.99',
      features: [
        'Up to 500 leads/month',
        'Email & SMS outreach',
        'AI personalization',
        'Basic analytics'
      ]
    },
    {
      name: 'Pro',
      description: 'Most popular for scaling teams',
      originalPrice: '£199.99',
      price: '£99.99',
      features: [
        'Up to 5,000 leads/month',
        'All 5 channels',
        'Advanced AI personalization',
        'Real-time analytics',
        'CRM integrations',
        'Priority support'
      ],
      popular: true
    },
    {
      name: 'Enterprise',
      description: 'Custom for high-volume teams',
      originalPrice: 'Custom',
      price: 'Custom',
      features: [
        'Unlimited leads',
        'White-label option',
        'Custom integrations',
        'SLA guarantees',
        '24/7 support'
      ]
    }
  ];

  return (
    <section className="relative py-40 px-6" id="pricing">
      <div className="max-w-7xl mx-auto">
        {/* Title - Enhanced spacing */}
        <div className="text-center mb-24">
          <h2 className="text-5xl md:text-6xl font-black text-white mb-8 leading-tight tracking-tight">
            Performance-based pricing.
          </h2>
          <p className="text-xl text-gray-400 mb-6 leading-relaxed">
            30 days free. Then pay only 2.5% of deal value per booked meeting.
          </p>
          <p className="text-sm text-gray-500 leading-relaxed">
            No meetings booked = no performance fee. Cancel anytime.
          </p>
        </div>

        {/* Cards with enhanced hover */}
        <div className="grid lg:grid-cols-3 gap-8">
          {plans.map((plan, idx) => (
            <div
              key={idx}
              className={`group relative rounded-3xl p-10 transition-all duration-300 ${
                plan.popular
                  ? 'glass-premium border-2 border-white/20 transform lg:scale-105 hover:scale-[1.08] hover:shadow-[0_30px_80px_rgba(0,0,0,0.3)]'
                  : 'glass-premium border border-white/10 hover:-translate-y-1 hover:shadow-[0_20px_50px_rgba(0,0,0,0.2)]'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="px-4 py-1.5 bg-white/10 border border-white/20 rounded-full backdrop-blur-xl">
                    <span className="text-xs font-bold text-white">MOST POPULAR</span>
                  </div>
                </div>
              )}

              <div className="mb-8">
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <p className="text-sm text-gray-400 mb-6">{plan.description}</p>

                {plan.originalPrice !== 'Custom' ? (
                  <>
                    <div className="flex items-baseline gap-3 mb-2">
                      <span className="text-gray-500 text-lg line-through">{plan.originalPrice}</span>
                      <span className="px-2 py-1 bg-green-500/10 border border-green-500/20 rounded text-xs font-bold text-green-400">
                        SAVE 50%
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-5xl font-black text-white">{plan.price}</span>
                      <span className="text-gray-400">/month</span>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">+ 2.5% per meeting booked</p>
                  </>
                ) : (
                  <div className="text-4xl font-black text-white">Let's talk</div>
                )}
              </div>

              <ul className="space-y-3 mb-10">
                {plan.features.map((feature, fIdx) => (
                  <li key={fIdx} className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    <span className="text-gray-300 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => navigate('/pilot-application')}
                className={`w-full py-3 rounded-xl font-semibold transition-all ${
                  plan.popular
                    ? 'bg-white text-slate-950 hover:bg-gray-100'
                    : 'bg-white/5 text-white hover:bg-white/10 border border-white/10'
                }`}
              >
                {plan.originalPrice === 'Custom' ? 'Contact sales' : 'Start free trial'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// GUARANTEE - Calm confidence with hover effect
// ============================================================================
const Guarantee = () => (
  <section className="relative py-40 px-6">
    <div className="max-w-4xl mx-auto">
      <div className="group glass-premium rounded-3xl p-14 border border-white/10 text-center hover:border-green-500/20 hover:-translate-y-1 hover:shadow-[0_30px_80px_rgba(34,197,94,0.15)] transition-all duration-500">
        <div className="w-20 h-20 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center mx-auto mb-8 group-hover:scale-110 group-hover:bg-green-500/15 transition-all duration-300">
          <Shield className="w-10 h-10 text-green-400" />
        </div>
        <h3 className="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight">30-day performance guarantee</h3>
        <p className="text-lg md:text-xl text-gray-400 leading-[1.7]">
          If we don't book at least 5 qualified meetings in your first 30 days,
          we'll refund your subscription and work for free until you hit your goal.
        </p>
      </div>
    </div>
  </section>
);

// ============================================================================
// SECURITY - Badge row (Apple-style) with enhanced spacing
// ============================================================================
const Security = () => (
  <section className="relative py-40 px-6" id="security">
    <div className="max-w-5xl mx-auto text-center">
      <h2 className="text-4xl md:text-5xl font-bold text-white mb-8 leading-tight tracking-tight">
        Enterprise-grade security and compliance.
      </h2>
      <p className="text-gray-400 mb-20 text-lg leading-relaxed">
        Built for teams that take data protection seriously.
      </p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-12">
        {[
          { icon: Shield, label: 'SOC 2 Type II' },
          { icon: Lock, label: 'GDPR Compliant' },
          { icon: Shield, label: 'ISO 27001' },
          { icon: Lock, label: 'CCPA Ready' }
        ].map((item, idx) => (
          <div key={idx} className="group flex flex-col items-center gap-4 hover:-translate-y-1 transition-all duration-300">
            <div className="w-14 h-14 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:bg-white/10 group-hover:border-white/20 transition-all duration-300">
              <item.icon className="w-7 h-7 text-gray-400 group-hover:text-gray-300 transition-colors" />
            </div>
            <span className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors leading-relaxed">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  </section>
);

// ============================================================================
// FOOTER - Minimal Stripe-style
// ============================================================================
const Footer = () => (
  <footer className="relative py-20 px-6 border-t border-white/5">
    <div className="max-w-7xl mx-auto">
      <div className="grid md:grid-cols-5 gap-12 mb-16">
        <div className="md:col-span-2">
          <div className="text-xl font-bold text-white mb-3">RekindlePro</div>
          <p className="text-gray-500 text-sm mb-6">
            Intelligent revenue recovery for modern sales teams.
          </p>
        </div>

        <div>
          <div className="text-sm font-semibold text-white mb-4">Product</div>
          <ul className="space-y-3 text-sm text-gray-500">
            <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
            <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
            <li><a href="#security" className="hover:text-white transition-colors">Security</a></li>
          </ul>
        </div>

        <div>
          <div className="text-sm font-semibold text-white mb-4">Company</div>
          <ul className="space-y-3 text-sm text-gray-500">
            <li><a href="/blog" className="hover:text-white transition-colors">Blog</a></li>
            <li><a href="#" className="hover:text-white transition-colors">About</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
          </ul>
        </div>

        <div>
          <div className="text-sm font-semibold text-white mb-4">Legal</div>
          <ul className="space-y-3 text-sm text-gray-500">
            <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
          </ul>
        </div>
      </div>

      <div className="pt-8 border-t border-white/5 flex items-center justify-between text-sm text-gray-500">
        <span>© 2025 RekindlePro. All rights reserved.</span>
        <span>Made in London</span>
      </div>
    </div>
  </footer>
);

// ============================================================================
// MAIN COMPONENT
// ============================================================================
export default function LandingPageElite() {
  return (
    <div className="bg-slate-950 min-h-screen">
      <Navigation />
      <Hero />
      <StatsBar />
      <ProductDemo />
      <Features />
      <HowItWorks />
      <Pricing />
      <Guarantee />
      <Security />
      <Footer />
    </div>
  );
}
