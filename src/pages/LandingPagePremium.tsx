// RekindlePro Landing Page - Stripe/Linear/Apple Quality
// @ts-nocheck
import '../styles/animations.css';
import { useState, useEffect } from 'react';
import {
  CheckCircle,
  Shield,
  Lock,
  ArrowRight,
  Play,
  Eye,
  MessageSquare,
  TrendingUp,
  Users,
  Award,
  Zap,
  Mail,
  Phone,
  MessageCircle,
  Calendar,
  Target,
  BarChart3,
  Building2
} from 'lucide-react';

// ============================================================================
// PREMIUM BUTTON COMPONENT - Stripe-inspired magnetic hover
// ============================================================================
const PremiumButton = ({
  children,
  variant = 'primary',
  size = 'lg',
  onClick
}: {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  const sizeClasses = {
    sm: 'px-6 py-2.5 text-sm',
    md: 'px-8 py-3.5 text-base',
    lg: 'px-10 py-4 text-lg'
  };

  const variantClasses = {
    primary: 'bg-gradient-to-r from-orange-500 via-orange-600 to-orange-500 text-white hover:shadow-[0_20px_60px_rgba(255,107,53,0.4)] animate-premium-gradient',
    secondary: 'bg-white/5 border-2 border-white/20 text-white hover:bg-white/10 hover:border-white/30',
    ghost: 'text-gray-300 hover:text-white hover:bg-white/5'
  };

  return (
    <button
      className={`${sizeClasses[size]} ${variantClasses[variant]} font-semibold rounded-2xl transition-all duration-500 relative overflow-hidden group backdrop-blur-xl`}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        transform: isHovered && variant === 'primary'
          ? `perspective(1000px) rotateX(${(mousePosition.y - 25) * 0.05}deg) rotateY(${(mousePosition.x - 100) * 0.05}deg) scale(1.02)`
          : 'none',
      }}
    >
      {/* Magnetic glow */}
      {variant === 'primary' && isHovered && (
        <span
          className="absolute w-32 h-32 bg-gradient-radial from-white/40 via-white/20 to-transparent rounded-full blur-3xl transition-all duration-300 pointer-events-none"
          style={{ left: mousePosition.x - 64, top: mousePosition.y - 64 }}
        />
      )}

      {/* Shimmer */}
      {variant === 'primary' && (
        <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
      )}

      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </button>
  );
};

// ============================================================================
// HERO SECTION - Emotional, trust-driven copy
// ============================================================================
const HeroSection = () => {
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center px-4 py-20 overflow-hidden">
      {/* Premium background */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />

      {/* Ambient orbs */}
      <div className="absolute top-1/4 -left-1/4 w-[800px] h-[800px] bg-gradient-to-br from-orange-500/10 via-orange-600/5 to-transparent rounded-full blur-[140px] animate-aurora" />
      <div className="absolute bottom-1/4 -right-1/4 w-[600px] h-[600px] bg-gradient-to-br from-purple-500/10 via-blue-500/5 to-transparent rounded-full blur-[120px] animate-aurora" style={{ animationDelay: '5s' }} />

      {/* Linear grid */}
      <div className="absolute inset-0 linear-grid opacity-10" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center max-w-5xl mx-auto mb-16 animate-apple-fade-in">
          {/* Trust badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-premium border border-white/10 mb-8 hover:scale-105 transition-transform duration-300">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-white/80 font-medium text-sm">Trusted by 32 founding partners</span>
          </div>

          {/* Hero headline - Emotional, fear-based */}
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-black text-white mb-8 leading-[1.05] tracking-tight">
            Stop Watching Your<br />
            <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent animate-premium-gradient">
              Pipeline Die
            </span>
          </h1>

          {/* Sub-headline - Relief & clarity */}
          <p className="text-2xl md:text-3xl text-gray-300 mb-6 leading-relaxed font-light max-w-4xl mx-auto">
            <span className="text-white font-semibold">Rekindle automates intelligent, multi-channel follow-up</span> so every lead gets touched until they respond—or opt out.
          </p>

          <p className="text-xl text-gray-400 mb-12 max-w-3xl mx-auto">
            No more dead pipelines. No more manual follow-up. Just qualified meetings on your calendar.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <PremiumButton variant="primary" size="lg" onClick={() => navigate('/pilot-application')}>
              Join Pilot Program
              <ArrowRight className="w-5 h-5" />
            </PremiumButton>
            <PremiumButton variant="secondary" size="lg">
              <Play className="w-4 h-4" />
              Watch 60s Demo
            </PremiumButton>
          </div>

          {/* Trust signals */}
          <div className="flex items-center justify-center gap-8 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>30 days free</span>
            </div>
            <div className="w-px h-4 bg-white/10" />
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Pay per meeting</span>
            </div>
            <div className="w-px h-4 bg-white/10" />
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Cancel anytime</span>
            </div>
          </div>
        </div>

        {/* Trust badges row */}
        <div className="flex items-center justify-center gap-8 opacity-40 hover:opacity-70 transition-opacity">
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <Shield className="w-4 h-4" />
            <span>SOC 2 Type II</span>
          </div>
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <Lock className="w-4 h-4" />
            <span>GDPR Compliant</span>
          </div>
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <Shield className="w-4 h-4" />
            <span>Your Domain Protection</span>
          </div>
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// PILOT PROGRESS - Scarcity indicator
// ============================================================================
const PilotProgressSection = () => {
  const [progress, setProgress] = useState(0);
  const seatsTaken = 32;
  const totalSeats = 50;
  const percentage = (seatsTaken / totalSeats) * 100;

  useEffect(() => {
    const timer = setTimeout(() => setProgress(percentage), 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <section className="relative py-20 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="glass-premium rounded-3xl p-10 border border-orange-500/20 relative overflow-hidden">
          {/* Glow effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-transparent" />

          <div className="relative">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-orange-500 animate-pulse" />
                <span className="text-white font-bold text-xl">Founding Pilot Program</span>
              </div>
              <div className="text-orange-400 font-black text-2xl">{seatsTaken}/{totalSeats}</div>
            </div>

            {/* Progress bar */}
            <div className="relative w-full h-4 bg-white/5 rounded-full overflow-hidden mb-6">
              <div
                className="absolute left-0 top-0 h-full bg-gradient-to-r from-orange-500 to-orange-600 rounded-full transition-all duration-1500 ease-out"
                style={{ width: `${progress}%` }}
              />
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
            </div>

            <div className="text-center">
              <p className="text-gray-300 text-lg mb-2">
                Only <span className="text-white font-bold">{totalSeats - seatsTaken} seats remaining</span> at 50% founder rate
              </p>
              <p className="text-gray-500 text-sm">
                Lock in £99.99/mo forever (normally £199.99/mo)
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// DASHBOARD PREVIEW - Premium screenshot frame
// ============================================================================
const DashboardPreviewSection = () => (
  <section className="relative py-32 px-4">
    <div className="max-w-7xl mx-auto">
      <div className="text-center mb-16 animate-spring-in">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-premium border border-white/10 mb-6">
          <Eye className="w-4 h-4 text-orange-400" />
          <span className="text-white/80 font-medium text-sm uppercase tracking-wider">See it in action</span>
        </div>
        <h2 className="text-5xl md:text-6xl font-black text-white mb-6 leading-tight">
          One Dashboard.<br />
          <span className="text-gray-400">Complete Control.</span>
        </h2>
      </div>

      {/* Premium dashboard frame */}
      <div className="relative animate-spring-in" style={{ animationDelay: '200ms' }}>
        <div className="relative glass-premium rounded-3xl p-3 border border-white/20 shadow-[0_40px_120px_rgba(0,0,0,0.5)]">
          {/* Browser chrome */}
          <div className="flex items-center gap-2 px-4 py-3 bg-white/5 rounded-t-2xl border-b border-white/10">
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-400/60" />
              <div className="w-3 h-3 rounded-full bg-yellow-400/60" />
              <div className="w-3 h-3 rounded-full bg-green-400/60" />
            </div>
            <div className="flex-1 text-center">
              <div className="inline-block px-6 py-1.5 bg-white/5 rounded-lg text-gray-400 text-sm">
                app.rekindlepro.com/dashboard
              </div>
            </div>
          </div>

          {/* Dashboard preview */}
          <div className="relative aspect-[16/9] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-b-2xl overflow-hidden">
            <div className="absolute inset-0 linear-grid opacity-10" />

            {/* Metrics cards */}
            <div className="absolute inset-0 p-8">
              <div className="grid grid-cols-3 gap-6 mb-8">
                {[
                  { label: 'Active Sequences', value: '12', icon: Zap, color: 'text-blue-400' },
                  { label: 'Meetings Booked', value: '47', icon: Calendar, color: 'text-green-400' },
                  { label: 'Response Rate', value: '18.4%', icon: TrendingUp, color: 'text-orange-400' }
                ].map((stat, idx) => (
                  <div key={idx} className="glass-card rounded-2xl p-6 hover:scale-105 transition-transform">
                    <div className="flex items-center gap-3 mb-3">
                      <stat.icon className={`w-5 h-5 ${stat.color}`} />
                      <div className="text-gray-400 text-sm">{stat.label}</div>
                    </div>
                    <div className="text-white text-4xl font-bold">{stat.value}</div>
                  </div>
                ))}
              </div>

              {/* Activity chart placeholder */}
              <div className="glass-card rounded-2xl p-6">
                <div className="text-white font-semibold mb-4">Engagement Timeline</div>
                <div className="h-32 flex items-end gap-1">
                  {Array.from({ length: 24 }).map((_, idx) => (
                    <div
                      key={idx}
                      className="flex-1 bg-gradient-to-t from-orange-500/80 to-orange-600/60 rounded-t transition-all hover:opacity-100"
                      style={{
                        height: `${Math.random() * 80 + 20}%`,
                        opacity: 0.6 + Math.random() * 0.4
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Ambient glow */}
        <div className="absolute -inset-8 bg-gradient-to-br from-orange-500/20 via-purple-500/10 to-blue-500/10 blur-3xl -z-10" />
      </div>
    </div>
  </section>
);

// ============================================================================
// HOW IT WORKS - 4-step diagram (Stripe-style)
// ============================================================================
const HowItWorksSection = () => {
  const steps = [
    {
      number: '01',
      title: 'Upload Your Leads',
      description: 'CSV or CRM sync. We enrich and validate every contact automatically.',
      icon: Users,
      color: 'from-blue-500 to-blue-600'
    },
    {
      number: '02',
      title: 'AI Personalizes Everything',
      description: 'Every message is crafted for your ICP using real-time data signals.',
      icon: Zap,
      color: 'from-orange-500 to-orange-600'
    },
    {
      number: '03',
      title: 'Multi-Channel Outreach',
      description: 'Email, SMS, LinkedIn, WhatsApp, Voice—until they respond.',
      icon: MessageSquare,
      color: 'from-purple-500 to-purple-600'
    },
    {
      number: '04',
      title: 'Meetings Auto-Booked',
      description: 'Qualified leads book directly. You show up and close.',
      icon: Award,
      color: 'from-green-500 to-green-600'
    }
  ];

  return (
    <section className="relative py-32 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-20 animate-spring-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-premium border border-white/10 mb-6">
            <Target className="w-4 h-4 text-orange-400" />
            <span className="text-white/80 font-medium text-sm uppercase tracking-wider">How it works</span>
          </div>
          <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
            Four Steps to<br />
            <span className="bg-gradient-to-r from-orange-400 to-orange-600 bg-clip-text text-transparent">Full Automation</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Set it up once. Let Rekindle handle the rest.
          </p>
        </div>

        {/* Steps grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className="relative group animate-spring-in"
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              {/* Connection line (desktop only) */}
              {idx < steps.length - 1 && (
                <div className="hidden lg:block absolute top-16 left-full w-full h-px bg-gradient-to-r from-white/20 to-transparent z-0" />
              )}

              <div className="relative glass-premium rounded-3xl p-8 hover:scale-105 hover:border-orange-500/30 transition-all duration-500 border border-white/10">
                {/* Step number watermark */}
                <div className="absolute top-4 right-4 text-7xl font-black text-white/5">{step.number}</div>

                {/* Icon */}
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg`}>
                  <step.icon className="w-8 h-8 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                <p className="text-gray-400 leading-relaxed">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// PRICING SECTION - Stripe-quality tier cards
// ============================================================================
const PricingSection = () => {
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const plans = [
    {
      name: 'Starter',
      description: 'Perfect for small teams testing the waters',
      originalPrice: '£29.99',
      founderPrice: '£14.99',
      discount: '50%',
      features: [
        'Up to 500 leads/month',
        'Email & SMS outreach',
        'AI personalization',
        'Basic analytics',
        'Email support'
      ],
      icon: Users,
      gradient: 'from-blue-500 to-blue-600'
    },
    {
      name: 'Pro',
      description: 'Most popular for scaling teams',
      originalPrice: '£199.99',
      founderPrice: '£99.99',
      discount: '50%',
      isPopular: true,
      features: [
        'Up to 5,000 leads/month',
        'All 5 channels (Email, SMS, LinkedIn, WhatsApp, Voice)',
        'Advanced AI personalization',
        'Real-time analytics',
        'CRM integrations',
        'Priority support',
        'Dedicated success manager'
      ],
      icon: Award,
      gradient: 'from-orange-500 to-orange-600'
    },
    {
      name: 'Enterprise',
      description: 'Custom solution for high-volume teams',
      originalPrice: 'Custom',
      founderPrice: 'Custom',
      discount: '50%',
      features: [
        'Unlimited leads',
        'White-label option',
        'Custom integrations',
        'Dedicated infrastructure',
        'SLA guarantees',
        'Advanced security & compliance',
        '24/7 enterprise support'
      ],
      icon: Building2,
      gradient: 'from-purple-500 to-purple-600'
    }
  ];

  return (
    <section className="relative py-32 px-4" id="pricing">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />
      <div className="absolute top-1/3 left-0 w-[500px] h-[500px] bg-gradient-to-br from-green-500/10 to-transparent rounded-full blur-[120px]" />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-20 animate-spring-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-premium border border-white/10 mb-6">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-white/80 font-medium text-sm uppercase tracking-wider">Pilot Program Pricing</span>
          </div>

          <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
            Simple, Transparent<br />
            <span className="bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">Performance Pricing</span>
          </h2>

          <p className="text-xl text-gray-300 max-w-4xl mx-auto mb-6">
            <span className="text-white font-bold">30 days free.</span> Then pay only{' '}
            <span className="text-orange-400 font-bold">2.5% of deal value</span> per booked meeting.{' '}
            <span className="text-emerald-400 font-semibold">No meetings = no performance fee.</span>
          </p>

          {/* Pilot notice */}
          <div className="inline-flex items-center gap-3 px-6 py-3 glass-card border-2 border-orange-500/40 rounded-2xl">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500" />
            </span>
            <span className="text-white font-bold text-sm">EXCLUSIVE PILOT PROGRAM • 50% OFF FOREVER</span>
          </div>
        </div>

        {/* Pricing cards */}
        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          {plans.map((plan, idx) => (
            <div
              key={plan.name}
              className={`relative rounded-3xl p-8 animate-spring-in ${
                plan.isPopular
                  ? 'glass-premium border-2 border-orange-500/50 transform lg:scale-105 shadow-[0_20px_80px_rgba(255,107,53,0.3)]'
                  : 'glass-premium border border-white/10'
              }`}
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              {/* Popular badge */}
              {plan.isPopular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="glass-card border-2 border-white/30 rounded-full px-6 py-2">
                    <span className="text-sm font-black text-white">MOST POPULAR</span>
                  </div>
                </div>
              )}

              {/* Icon */}
              <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${plan.gradient} flex items-center justify-center mb-6`}>
                <plan.icon className="w-7 h-7 text-white" />
              </div>

              {/* Plan name & description */}
              <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
              <p className="text-gray-400 text-sm mb-6">{plan.description}</p>

              {/* Pricing */}
              <div className="mb-8">
                {plan.originalPrice !== 'Custom' ? (
                  <>
                    <div className="flex items-baseline gap-3 mb-2">
                      <span className="text-gray-500 text-xl line-through">{plan.originalPrice}</span>
                      <div className="px-2 py-1 bg-green-500/20 border border-green-500/40 rounded-lg">
                        <span className="text-green-400 text-xs font-bold">SAVE {plan.discount}</span>
                      </div>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className={`text-5xl font-black ${plan.isPopular ? 'text-white' : 'text-orange-400'}`}>
                        {plan.founderPrice}
                      </span>
                      <span className="text-gray-400">/month</span>
                    </div>
                    <p className="text-gray-500 text-sm mt-2">after 30 days free + 2.5% per meeting</p>
                  </>
                ) : (
                  <div className="text-5xl font-black text-white mb-2">Let's Talk</div>
                )}
              </div>

              {/* Features */}
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, fIdx) => (
                  <li key={fIdx} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <PremiumButton
                variant={plan.isPopular ? 'primary' : 'secondary'}
                size="md"
                onClick={() => navigate('/pilot-application')}
              >
                {plan.originalPrice === 'Custom' ? 'Contact Sales' : 'Start Free Trial'}
                <ArrowRight className="w-4 h-4" />
              </PremiumButton>
            </div>
          ))}
        </div>

        {/* Billing transparency */}
        <p className="text-center text-gray-500 text-sm">
          All prices in GBP. Cancel anytime. No hidden fees. Full transparency.
        </p>
      </div>
    </section>
  );
};

// ============================================================================
// GUARANTEE SECTION - Trust builder
// ============================================================================
const GuaranteeSection = () => (
  <section className="relative py-32 px-4">
    <div className="max-w-5xl mx-auto">
      <div className="glass-premium rounded-3xl p-12 border-2 border-green-500/30 relative overflow-hidden">
        {/* Glow */}
        <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 via-transparent to-transparent" />

        <div className="relative flex flex-col md:flex-row items-center gap-8">
          {/* Badge */}
          <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-green-500/30 to-emerald-500/20 flex items-center justify-center flex-shrink-0 shadow-[0_20px_50px_rgba(34,197,94,0.2)]">
            <Shield className="w-12 h-12 text-green-400" />
          </div>

          {/* Content */}
          <div className="flex-1 text-center md:text-left">
            <h3 className="text-3xl font-black text-white mb-3">30-Day Performance Guarantee</h3>
            <p className="text-gray-300 text-lg leading-relaxed">
              If Rekindle doesn't book at least <span className="text-white font-semibold">5 qualified meetings</span> in your first 30 days,
              we'll <span className="text-green-400 font-semibold">refund your entire subscription</span> and work for free until you hit your goal.
            </p>
          </div>

          {/* Badge circle */}
          <div className="hidden lg:flex w-28 h-28 rounded-full bg-green-500/10 border-2 border-green-500/30 items-center justify-center flex-shrink-0">
            <div className="text-center">
              <div className="text-green-400 font-black text-3xl">100%</div>
              <div className="text-green-400 text-xs">Guarantee</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
);

// ============================================================================
// FOUNDER'S NOTE - Human touch
// ============================================================================
const FoundersNoteSection = () => (
  <section className="relative py-32 px-4">
    <div className="max-w-4xl mx-auto">
      <div className="glass-premium rounded-3xl p-12 border border-white/10">
        <div className="flex flex-col md:flex-row items-start gap-8">
          {/* Avatar */}
          <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-orange-500/30 to-orange-600/20 flex-shrink-0 flex items-center justify-center text-5xl shadow-lg">
            👤
          </div>

          {/* Content */}
          <div className="flex-1">
            <div className="text-sm text-gray-400 uppercase tracking-wider mb-3">A Note from the Founder</div>
            <h3 className="text-3xl font-black text-white mb-6">Why We Built Rekindle</h3>

            <div className="text-gray-300 leading-relaxed space-y-4 text-lg">
              <p>
                After watching countless sales teams struggle with dead pipelines and inconsistent follow-up,
                I realized the problem wasn't laziness—<span className="text-white font-semibold">it was impossible logistics.</span>
              </p>
              <p>
                SDRs are drowning in manual work. Marketing spends millions on leads that rot.
                The tech stack is fragmented. Nobody can keep up.
              </p>
              <p>
                <span className="text-white font-semibold">Rekindle automates what should have been automated years ago</span>:
                intelligent, multi-channel follow-up that never stops until the lead responds or opts out.
              </p>
              <p>
                This is the system I wish I had when I was grinding cold outreach at 2 AM.
              </p>
              <p className="text-gray-400 italic pt-4">
                — Alex Chen, CEO & Founder
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
);

// ============================================================================
// FOOTER - Trust signals & links
// ============================================================================
const Footer = () => (
  <footer className="relative py-20 px-4 border-t border-white/10">
    <div className="max-w-7xl mx-auto">
      <div className="grid md:grid-cols-4 gap-12 mb-16">
        {/* Brand */}
        <div>
          <div className="text-2xl font-black text-white mb-4">RekindlePro</div>
          <p className="text-gray-400 mb-6">
            Intelligent multi-channel follow-up that never stops.
          </p>
          {/* Trust badges */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-gray-500 text-sm">
              <Shield className="w-4 h-4" />
              <span>SOC 2 Type II</span>
            </div>
            <div className="flex items-center gap-2 text-gray-500 text-sm">
              <Lock className="w-4 h-4" />
              <span>GDPR Compliant</span>
            </div>
            <div className="flex items-center gap-2 text-gray-500 text-sm">
              <Shield className="w-4 h-4" />
              <span>Brand Protection</span>
            </div>
          </div>
        </div>

        {/* Product */}
        <div>
          <div className="text-white font-semibold mb-4">Product</div>
          <ul className="space-y-2 text-gray-400">
            <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
            <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Case Studies</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Integration</a></li>
          </ul>
        </div>

        {/* Company */}
        <div>
          <div className="text-white font-semibold mb-4">Company</div>
          <ul className="space-y-2 text-gray-400">
            <li><a href="#" className="hover:text-white transition-colors">About</a></li>
            <li><a href="/blog" className="hover:text-white transition-colors">Blog</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
          </ul>
        </div>

        {/* Legal */}
        <div>
          <div className="text-white font-semibold mb-4">Legal</div>
          <ul className="space-y-2 text-gray-400">
            <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Data Processing</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
          </ul>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
        <p className="text-gray-500 text-sm">© 2025 RekindlePro. All rights reserved.</p>
        <div className="flex items-center gap-6 text-gray-500 text-sm">
          <span>Made with care in London</span>
          <div className="w-px h-4 bg-white/10" />
          <span>Your domain, your brand</span>
        </div>
      </div>
    </div>
  </footer>
);

// ============================================================================
// MAIN LANDING PAGE COMPONENT
// ============================================================================
export default function LandingPagePremium() {
  return (
    <div className="bg-slate-950 min-h-screen">
      <HeroSection />
      <PilotProgressSection />
      <DashboardPreviewSection />
      <HowItWorksSection />
      <PricingSection />
      <GuaranteeSection />
      <FoundersNoteSection />
      <Footer />
    </div>
  );
}
