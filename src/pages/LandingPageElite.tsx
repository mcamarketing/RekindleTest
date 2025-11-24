// RekindlePro - Stripe/Linear/Apple Quality Landing Page
// Ultra-clean, visual-driven, enterprise-grade
// @ts-nocheck
import '../styles/animations.css';
import { useState } from 'react';
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
// NAVIGATION - Stripe-minimal
// ============================================================================
const Navigation = () => {
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <nav className="fixed top-0 left-0 right-0 bg-slate-950/80 backdrop-blur-xl border-b border-white/5 z-50">
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
            className="px-5 py-2.5 bg-white text-slate-950 rounded-lg text-sm font-medium hover:bg-gray-100 transition-all"
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
    <section className="relative min-h-screen flex items-center justify-center px-6 pt-32 pb-24">
      {/* Subtle background */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />
      <div className="absolute inset-0 linear-grid opacity-10" />

      {/* Subtle glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-orange-500/5 blur-[100px]" />

      <div className="max-w-5xl mx-auto text-center relative z-10">
        {/* Pilot badge - subtle */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
          <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
          <span className="text-sm text-gray-400">Pilot Program Open</span>
        </div>

        {/* Massive headline - Stripe/Linear sizing */}
        <h1 className="text-6xl md:text-7xl lg:text-8xl font-black text-white mb-8 leading-[1.05] tracking-tight">
          Revenue recovery,<br />automated.
        </h1>

        {/* Clean subhead */}
        <p className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed font-light">
          AI-powered multi-channel follow-up that transforms dormant leads into qualified meetings.
          Enterprise-grade deliverability. Exceptional results.
        </p>

        {/* Single CTA */}
        <div className="flex items-center justify-center gap-4 mb-16">
          <button
            onClick={() => navigate('/pilot-application')}
            className="group px-8 py-4 bg-white text-slate-950 rounded-xl font-semibold hover:bg-gray-100 transition-all flex items-center gap-2"
          >
            Start free trial
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
          <button className="px-8 py-4 bg-white/5 text-white rounded-xl font-semibold hover:bg-white/10 transition-all border border-white/10">
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
// STATS BAR - Linear-style clean metrics
// ============================================================================
const StatsBar = () => (
  <section className="relative py-24 px-6">
    <div className="max-w-6xl mx-auto">
      <div className="grid md:grid-cols-3 gap-12">
        <div className="text-center">
          <div className="text-5xl font-black text-white mb-3">15.2%</div>
          <div className="text-gray-400 text-sm">Meeting rate</div>
          <div className="text-gray-600 text-xs mt-1">Industry avg: 6-8%</div>
        </div>
        <div className="text-center">
          <div className="text-5xl font-black text-white mb-3">8.4x</div>
          <div className="text-gray-400 text-sm">Average ROI</div>
          <div className="text-gray-600 text-xs mt-1">First 90 days</div>
        </div>
        <div className="text-center">
          <div className="text-5xl font-black text-white mb-3">98%</div>
          <div className="text-gray-400 text-sm">Deliverability</div>
          <div className="text-gray-600 text-xs mt-1">Enterprise infrastructure</div>
        </div>
      </div>
    </div>
  </section>
);

// ============================================================================
// VISUAL DEMO - Show product (placeholder for now)
// ============================================================================
const ProductDemo = () => (
  <section className="relative py-32 px-6">
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
                { label: 'Active Sequences', value: '12', color: 'from-blue-400 to-blue-600' },
                { label: 'Meetings Booked', value: '47', color: 'from-green-400 to-green-600' },
                { label: 'Response Rate', value: '18.4%', color: 'from-orange-400 to-orange-600' }
              ].map((stat, idx) => (
                <div key={idx} className="glass-premium rounded-2xl p-6">
                  <div className="text-gray-400 text-sm mb-2">{stat.label}</div>
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
    <section className="relative py-32 px-6" id="features">
      <div className="max-w-7xl mx-auto">
        {/* Section title */}
        <div className="mb-16">
          <h2 className="text-5xl md:text-6xl font-black text-white mb-4">
            Built for enterprise performance.
          </h2>
          <p className="text-xl text-gray-400">
            Advanced automation that respects your brand and delivers results.
          </p>
        </div>

        {/* Bento grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className={`glass-premium rounded-3xl p-10 hover:bg-white/5 transition-all duration-500 ${feature.span}`}
            >
              <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6">
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed">{feature.description}</p>
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
    <section className="relative py-32 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Title */}
        <div className="text-center mb-24">
          <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
            Effortless implementation.
          </h2>
          <p className="text-xl text-gray-400">
            From connection to first meeting in under 72 hours.
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-16">
          {steps.map((step, idx) => (
            <div key={idx} className="flex items-start gap-8">
              <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
                <span className="text-2xl font-black text-white">{step.number}</span>
              </div>
              <div className="flex-1 pt-3">
                <h3 className="text-3xl font-bold text-white mb-3">{step.title}</h3>
                <p className="text-xl text-gray-400 leading-relaxed">{step.description}</p>
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
    <section className="relative py-32 px-6" id="pricing">
      <div className="max-w-7xl mx-auto">
        {/* Title */}
        <div className="text-center mb-20">
          <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
            Performance-based pricing.
          </h2>
          <p className="text-xl text-gray-400 mb-4">
            30 days free. Then pay only 2.5% of deal value per booked meeting.
          </p>
          <p className="text-sm text-gray-500">
            No meetings booked = no performance fee. Cancel anytime.
          </p>
        </div>

        {/* Cards */}
        <div className="grid lg:grid-cols-3 gap-8">
          {plans.map((plan, idx) => (
            <div
              key={idx}
              className={`relative rounded-3xl p-10 ${
                plan.popular
                  ? 'glass-premium border-2 border-white/20 transform lg:scale-105'
                  : 'glass-premium border border-white/10'
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
// GUARANTEE - Calm confidence
// ============================================================================
const Guarantee = () => (
  <section className="relative py-32 px-6">
    <div className="max-w-4xl mx-auto">
      <div className="glass-premium rounded-3xl p-12 border border-white/10 text-center">
        <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center mx-auto mb-6">
          <Shield className="w-8 h-8 text-green-400" />
        </div>
        <h3 className="text-3xl font-bold text-white mb-4">30-day performance guarantee</h3>
        <p className="text-lg text-gray-400 leading-relaxed">
          If we don't book at least 5 qualified meetings in your first 30 days,
          we'll refund your subscription and work for free until you hit your goal.
        </p>
      </div>
    </div>
  </section>
);

// ============================================================================
// SECURITY - Badge row (Apple-style)
// ============================================================================
const Security = () => (
  <section className="relative py-32 px-6" id="security">
    <div className="max-w-5xl mx-auto text-center">
      <h2 className="text-4xl font-bold text-white mb-6">
        Enterprise-grade security and compliance.
      </h2>
      <p className="text-gray-400 mb-16">
        Built for teams that take data protection seriously.
      </p>

      <div className="grid md:grid-cols-4 gap-8">
        {[
          { icon: Shield, label: 'SOC 2 Type II' },
          { icon: Lock, label: 'GDPR Compliant' },
          { icon: Shield, label: 'ISO 27001' },
          { icon: Lock, label: 'CCPA Ready' }
        ].map((item, idx) => (
          <div key={idx} className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center">
              <item.icon className="w-6 h-6 text-gray-400" />
            </div>
            <span className="text-sm text-gray-400">{item.label}</span>
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
