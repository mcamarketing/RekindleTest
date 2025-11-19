import { ArrowLeft, Target, Users, Zap, Heart, TrendingUp, Award } from 'lucide-react';

export function About() {
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 text-[#FF6B35] hover:text-[#F7931E] mb-8 transition-all duration-200 font-semibold hover:gap-3"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </button>

        <div className="glass-card p-8 md:p-12">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-white mb-4">About Rekindle.ai</h1>
            <p className="text-xl text-gray-300">
              We help B2B sales teams turn cold leads into hot prospects with intelligent automation.
            </p>
          </div>

          {/* Mission Statement */}
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-xl">
                <Target className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white">Our Mission</h2>
            </div>
            <p className="text-gray-300 text-lg leading-relaxed mb-6">
              Every sales team has a goldmine of leads that went cold. We built Rekindle to help you revive those relationships and turn missed opportunities into closed deals.
            </p>
            <p className="text-gray-300 text-lg leading-relaxed">
              We believe cold outreach should not feel cold. With intelligent research, personalized messaging, and smart follow-ups, we help you reconnect with leads in a way that feels genuine and gets results.
            </p>
          </section>

          {/* The Problem */}
          <section className="mb-12 p-8 bg-red-500/10 border border-red-500/30 rounded-2xl">
            <h2 className="text-2xl font-bold text-white mb-4">The Problem We Solve</h2>
            <p className="text-gray-300 text-lg leading-relaxed mb-4">
              73% of leads never convert on first contact. But that does not mean they are bad leads. Most sales teams just do not have the time or resources to properly follow up with everyone.
            </p>
            <p className="text-gray-300 text-lg leading-relaxed">
              Generic email templates get ignored. Manual personalization takes hours. And most CRMs make it harder, not easier, to stay on top of your pipeline.
            </p>
          </section>

          {/* The Solution */}
          <section className="mb-12 p-8 bg-green-500/10 border border-green-500/30 rounded-2xl">
            <h2 className="text-2xl font-bold text-white mb-4">Our Solution</h2>
            <p className="text-gray-300 text-lg leading-relaxed mb-4">
              Rekindle automates the busywork while keeping the human touch. We research each lead, craft personalized messages, send smart follow-ups, and track everything in real-time.
            </p>
            <p className="text-gray-300 text-lg leading-relaxed">
              The result? Sales teams book 3x more meetings from their existing lead lists without adding headcount. You focus on closing deals, we handle the outreach.
            </p>
          </section>

          {/* Values */}
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-xl">
                <Heart className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white">Our Values</h2>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
                <div className="flex items-center gap-3 mb-4">
                  <Users className="w-6 h-6 text-[#FF6B35]" />
                  <h3 className="text-xl font-bold text-white">People First</h3>
                </div>
                <p className="text-gray-300">
                  We build tools that make salespeople more effective, not tools that replace them. Automation should enhance human relationships, not eliminate them.
                </p>
              </div>

              <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
                <div className="flex items-center gap-3 mb-4">
                  <Zap className="w-6 h-6 text-[#FF6B35]" />
                  <h3 className="text-xl font-bold text-white">Results Over Hype</h3>
                </div>
                <p className="text-gray-300">
                  We care about real metrics: meetings booked, deals closed, revenue generated. No vanity metrics, no inflated promises.
                </p>
              </div>

              <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
                <div className="flex items-center gap-3 mb-4">
                  <TrendingUp className="w-6 h-6 text-[#FF6B35]" />
                  <h3 className="text-xl font-bold text-white">Continuous Improvement</h3>
                </div>
                <p className="text-gray-300">
                  We test everything, learn from the data, and ship improvements weekly. Your feedback directly shapes our roadmap.
                </p>
              </div>

              <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
                <div className="flex items-center gap-3 mb-4">
                  <Award className="w-6 h-6 text-[#FF6B35]" />
                  <h3 className="text-xl font-bold text-white">Transparency</h3>
                </div>
                <p className="text-gray-300">
                  No hidden fees, no bait-and-switch pricing, no shady practices. You only pay when we deliver value: meetings booked.
                </p>
              </div>
            </div>
          </section>

          {/* How We Started */}
          <section className="mb-12">
            <h2 className="text-3xl font-bold text-white mb-6">How We Started</h2>
            <p className="text-gray-300 text-lg leading-relaxed mb-4">
              Rekindle was born from frustration. Our founder spent years in B2B sales, watching thousands of good leads go cold simply because there was not enough time to follow up properly.
            </p>
            <p className="text-gray-300 text-lg leading-relaxed mb-4">
              After testing every CRM and outreach tool on the market, the problem was clear: existing tools focused on managing leads, not reviving them. They made it easier to track conversations but harder to actually start them.
            </p>
            <p className="text-gray-300 text-lg leading-relaxed">
              So we built what we wished existed: a system that does the research, writes the emails, sends the follow-ups, and books the meetings. All while staying compliant, respectful, and genuinely helpful to prospects.
            </p>
          </section>

          {/* By The Numbers */}
          <section className="mb-12 p-8 bg-gradient-to-br from-[#FF6B35]/10 to-[#F7931E]/10 border border-[#FF6B35]/30 rounded-2xl">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">Rekindle By The Numbers</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-5xl font-black text-[#FF6B35] mb-2">3x</div>
                <div className="text-gray-300">More meetings booked from existing leads</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-black text-[#FF6B35] mb-2">15%</div>
                <div className="text-gray-300">Average response rate (vs 3% industry average)</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-black text-[#FF6B35] mb-2">80%</div>
                <div className="text-gray-300">Time saved on manual outreach</div>
              </div>
            </div>
          </section>

          {/* Who We Serve */}
          <section className="mb-12">
            <h2 className="text-3xl font-bold text-white mb-6">Who We Serve</h2>
            <p className="text-gray-300 text-lg leading-relaxed mb-6">
              Rekindle is built for B2B sales teams who know their lead lists have potential but do not have time to manually follow up with everyone.
            </p>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-[#FF6B35] rounded-full mt-2"></div>
                <p className="text-gray-300 text-lg">
                  <strong className="text-white">Startups</strong> that need to maximize ROI from every lead without hiring a massive sales team
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-[#FF6B35] rounded-full mt-2"></div>
                <p className="text-gray-300 text-lg">
                  <strong className="text-white">Growth companies</strong> scaling their outbound motion and need automation that actually works
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-[#FF6B35] rounded-full mt-2"></div>
                <p className="text-gray-300 text-lg">
                  <strong className="text-white">Enterprise teams</strong> with thousands of leads and not enough SDRs to follow up with them all
                </p>
              </div>
            </div>
          </section>

          {/* CTA */}
          <section className="text-center p-8 bg-gradient-to-r from-[#FF6B35]/20 to-[#F7931E]/20 border border-[#FF6B35]/30 rounded-2xl">
            <h2 className="text-3xl font-bold text-white mb-4">Ready to Revive Your Leads?</h2>
            <p className="text-gray-300 text-lg mb-6">
              Join hundreds of sales teams using Rekindle to book more meetings from their existing lead lists.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/signup')}
                className="px-8 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold text-lg rounded-xl hover:shadow-2xl hover:shadow-[#FF6B35]/40 hover:scale-105 transition-all duration-300"
              >
                Start Free Trial
              </button>
              <button
                onClick={() => navigate('/blog')}
                className="px-8 py-4 bg-white/10 border-2 border-white/20 text-white font-bold text-lg rounded-xl hover:bg-white/20 hover:border-[#FF6B35]/50 transition-all duration-300"
              >
                Read Our Blog
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

