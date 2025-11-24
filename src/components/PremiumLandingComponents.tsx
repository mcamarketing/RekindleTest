// Premium Landing Page Components - Stripe/Linear/Apple Quality
import { useState, useEffect } from 'react';
import { Shield, Check, Lock, Zap, ArrowRight, Play, Eye, MessageSquare, TrendingUp, Users, Award, Clock } from 'lucide-react';

// ============================================================================
// TRUST BADGES - SOC 2, GDPR, etc.
// ============================================================================
export const TrustBadges = () => (
  <div className="flex items-center justify-center gap-8 opacity-60 hover:opacity-100 transition-opacity duration-300">
    <div className="flex items-center gap-2 text-gray-400 text-sm">
      <Shield className="w-4 h-4" />
      <span>SOC 2 Type II</span>
    </div>
    <div className="flex items-center gap-2 text-gray-400 text-sm">
      <Lock className="w-4 h-4" />
      <span>GDPR Compliant</span>
    </div>
    <div className="flex items-center gap-2 text-gray-400 text-sm">
      <Shield className="w-4 h-4" />
      <span>Brand Protection</span>
    </div>
  </div>
);

// ============================================================================
// PILOT COHORT PROGRESS BAR - 32/50 Seats Claimed
// ============================================================================
export const PilotProgress = () => {
  const [progress, setProgress] = useState(0);
  const seatsTaken = 32;
  const totalSeats = 50;
  const percentage = (seatsTaken / totalSeats) * 100;

  useEffect(() => {
    const timer = setTimeout(() => setProgress(percentage), 300);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="glass-premium rounded-2xl p-8 border border-white/10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-orange-500 animate-pulse" />
            <span className="text-white font-semibold text-lg">Founding Pilot Program</span>
          </div>
          <div className="text-orange-400 font-bold text-xl">{seatsTaken}/{totalSeats}</div>
        </div>

        <div className="relative w-full h-3 bg-white/5 rounded-full overflow-hidden mb-4">
          <div
            className="absolute left-0 top-0 h-full bg-gradient-to-r from-orange-500 to-orange-600 rounded-full transition-all duration-1000 ease-out"
            style={{ width: `${progress}%` }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
        </div>

        <p className="text-gray-400 text-sm text-center">
          Only <span className="text-white font-semibold">{totalSeats - seatsTaken} seats remaining</span> at founding rate
        </p>
      </div>
    </div>
  );
};

// ============================================================================
// DASHBOARD HERO SCREENSHOT - Premium Frame
// ============================================================================
export const DashboardPreview = () => (
  <div className="relative max-w-6xl mx-auto">
    <div className="relative glass-premium rounded-3xl p-4 border border-white/20 shadow-[0_40px_100px_rgba(0,0,0,0.4)]">
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

      {/* Placeholder dashboard image */}
      <div className="relative aspect-[16/10] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl overflow-hidden">
        {/* Grid pattern */}
        <div className="absolute inset-0 linear-grid opacity-20" />

        {/* Fake dashboard UI elements */}
        <div className="absolute inset-0 p-8">
          <div className="grid grid-cols-3 gap-6 mb-8">
            {[
              { label: 'Active Sequences', value: '12', trend: '+23%' },
              { label: 'Meetings Booked', value: '47', trend: '+34%' },
              { label: 'Response Rate', value: '18.4%', trend: '+12%' }
            ].map((stat, idx) => (
              <div key={idx} className="glass-card rounded-2xl p-6">
                <div className="text-gray-400 text-sm mb-2">{stat.label}</div>
                <div className="text-white text-3xl font-bold mb-1">{stat.value}</div>
                <div className="text-green-400 text-sm flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  {stat.trend}
                </div>
              </div>
            ))}
          </div>

          {/* Fake chart */}
          <div className="glass-card rounded-2xl p-6 h-48">
            <div className="text-white font-semibold mb-4">Engagement Over Time</div>
            <div className="h-32 flex items-end gap-2">
              {Array.from({ length: 12 }).map((_, idx) => (
                <div
                  key={idx}
                  className="flex-1 bg-gradient-to-t from-orange-500 to-orange-600 rounded-t-lg opacity-80"
                  style={{ height: `${Math.random() * 80 + 20}%` }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>

    {/* Glow effect */}
    <div className="absolute -inset-4 bg-gradient-to-br from-orange-500/20 via-purple-500/10 to-blue-500/20 blur-3xl -z-10" />
  </div>
);

// ============================================================================
// HOW IT WORKS - 4-Step Diagram (Stripe-style)
// ============================================================================
export const HowItWorks = () => {
  const steps = [
    {
      number: '01',
      title: 'Upload Your Leads',
      description: 'CSV or CRM sync. We intelligently enrich and validate every contact.',
      icon: Users
    },
    {
      number: '02',
      title: 'AI Personalizes Messages',
      description: 'Every touchpoint is crafted for your ICP using real-time data signals.',
      icon: Zap
    },
    {
      number: '03',
      title: 'Multi-Channel Outreach',
      description: 'Email, SMS, LinkedIn, WhatsApp, Voice—sequenced until they respond.',
      icon: MessageSquare
    },
    {
      number: '04',
      title: 'Meetings Auto-Booked',
      description: 'Qualified leads book directly to your calendar. You show up and close.',
      icon: Award
    }
  ];

  return (
    <div className="max-w-7xl mx-auto">
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
        {steps.map((step, idx) => (
          <div key={idx} className="relative group">
            {/* Connection line */}
            {idx < steps.length - 1 && (
              <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-orange-500/50 to-transparent -translate-y-1/2 z-0" />
            )}

            <div className="relative glass-premium rounded-3xl p-8 hover:scale-105 transition-all duration-500">
              {/* Step number */}
              <div className="text-6xl font-black text-white/5 absolute top-4 right-6">{step.number}</div>

              {/* Icon */}
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500/20 to-orange-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <step.icon className="w-8 h-8 text-orange-400" />
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
              <p className="text-gray-400 leading-relaxed">{step.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// GUARANTEE STRIP - Clean, Trustworthy
// ============================================================================
export const GuaranteeStrip = () => (
  <div className="max-w-4xl mx-auto">
    <div className="glass-premium rounded-3xl p-10 border-2 border-green-500/30 relative overflow-hidden">
      {/* Glow effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 via-transparent to-transparent" />

      <div className="relative flex items-center gap-6">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-green-500/30 to-emerald-500/20 flex items-center justify-center flex-shrink-0">
          <Shield className="w-10 h-10 text-green-400" />
        </div>

        <div className="flex-1">
          <h3 className="text-2xl font-bold text-white mb-2">30-Day Performance Guarantee</h3>
          <p className="text-gray-300 leading-relaxed">
            If Rekindle doesn't book at least <span className="text-white font-semibold">5 qualified meetings</span> in your first 30 days,
            we'll refund your entire subscription and work for free until you hit your goal.
          </p>
        </div>

        <div className="hidden md:block">
          <div className="w-24 h-24 rounded-full bg-green-500/10 border-2 border-green-500/30 flex items-center justify-center">
            <div className="text-green-400 font-black text-2xl">100%</div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// ============================================================================
// SECONDARY CTAs - Stripe-style soft CTAs
// ============================================================================
export const SecondaryCTAs = () => (
  <div className="flex flex-wrap items-center justify-center gap-4">
    <button className="group flex items-center gap-2 px-6 py-3 text-gray-300 hover:text-white transition-colors duration-300">
      <Play className="w-4 h-4" />
      <span>Watch 60s demo</span>
      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
    </button>

    <div className="w-px h-6 bg-white/10" />

    <button className="group flex items-center gap-2 px-6 py-3 text-gray-300 hover:text-white transition-colors duration-300">
      <Eye className="w-4 h-4" />
      <span>Preview dashboard</span>
      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
    </button>

    <div className="w-px h-6 bg-white/10" />

    <button className="group flex items-center gap-2 px-6 py-3 text-gray-300 hover:text-white transition-colors duration-300">
      <MessageSquare className="w-4 h-4" />
      <span>Talk to an expert</span>
      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
    </button>
  </div>
);

// ============================================================================
// FOUNDER'S NOTE - Tasteful, Human Touch
// ============================================================================
export const FoundersNote = () => (
  <div className="max-w-4xl mx-auto">
    <div className="glass-premium rounded-3xl p-12 border border-white/10">
      <div className="flex items-start gap-6">
        {/* Founder avatar placeholder */}
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500/30 to-orange-600/20 flex-shrink-0 flex items-center justify-center">
          <div className="text-3xl">👤</div>
        </div>

        <div className="flex-1">
          <div className="text-sm text-gray-400 uppercase tracking-wider mb-3">A Note from the Founder</div>
          <h3 className="text-2xl font-bold text-white mb-4">Why We Built Rekindle</h3>
          <div className="text-gray-300 leading-relaxed space-y-4">
            <p>
              After watching countless sales teams struggle with dead pipelines and inconsistent follow-up,
              I realized the problem wasn't laziness—it was impossible logistics.
            </p>
            <p>
              SDRs are drowning in manual work. Marketing spends millions on leads that rot.
              The tech stack is fragmented. Nobody can keep up.
            </p>
            <p>
              <span className="text-white font-semibold">Rekindle automates what should have been automated years ago</span>:
              intelligent, multi-channel follow-up that never stops until the lead responds or opts out.
            </p>
            <p className="text-sm text-gray-400">
              — Alex Chen, CEO & Founder
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// ============================================================================
// PILOT COHORT LOGOS - Anonymous Placeholders
// ============================================================================
export const PilotCohortLogos = () => {
  const logos = [
    'Company A', 'Company B', 'Company C', 'Company D',
    'Company E', 'Company F'
  ];

  return (
    <div className="max-w-5xl mx-auto">
      <div className="text-center mb-8">
        <p className="text-gray-400 text-sm uppercase tracking-wider">
          Trusted by founding pilot partners
        </p>
      </div>

      <div className="grid grid-cols-3 md:grid-cols-6 gap-8 items-center opacity-40 hover:opacity-70 transition-opacity">
        {logos.map((logo, idx) => (
          <div
            key={idx}
            className="glass-card rounded-xl p-4 aspect-square flex items-center justify-center"
          >
            <div className="text-gray-500 text-xs font-semibold text-center">{logo}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
