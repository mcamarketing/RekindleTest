/**
 * Enhanced Hero Section with Advanced Animations
 * Maintains RekindlePro branding: #FF6B35 primary, #F7931E secondary, dark theme
 */

import { useState, useEffect } from 'react';
import { ArrowRight, Sparkles, TrendingUp, Zap, Target, Users, Brain } from 'lucide-react';

export const EnhancedHero = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);

    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 20 - 10,
        y: (e.clientY / window.innerHeight) * 20 - 10,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#1A1F2E] to-[#0a0e1a] overflow-hidden">
      {/* Animated Background Grid */}
      <div className="absolute inset-0 opacity-20">
        <div
          className="absolute inset-0 bg-[linear-gradient(rgba(255,107,53,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(255,107,53,0.1)_1px,transparent_1px)] bg-[size:50px_50px]"
          style={{
            transform: `translate(${mousePosition.x}px, ${mousePosition.y}px)`,
            transition: 'transform 0.3s ease-out',
          }}
        />
      </div>

      {/* Floating Gradient Orbs */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-[#FF6B35] rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse-slow" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#F7931E] rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse-slow" style={{ animationDelay: '2s' }} />
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#FF6B35] rounded-full mix-blend-multiply filter blur-3xl opacity-5 animate-pulse-slow" style={{ animationDelay: '4s' }} />

      {/* Content Container */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-20">
        <div className="text-center">
          {/* Badge */}
          <div
            className={`inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-[#FF6B35]/10 to-[#F7931E]/10 border border-[#FF6B35]/30 rounded-full mb-8 backdrop-blur-sm transition-all duration-700 ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            <div className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#FF6B35] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#FF6B35]"></span>
            </div>
            <span className="text-sm font-semibold text-white tracking-wide">
              AI-Powered Revenue Recovery Platform
            </span>
            <Sparkles className="w-4 h-4 text-[#F7931E]" />
          </div>

          {/* Main Headline */}
          <h1
            className={`text-5xl sm:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-[1.1] tracking-tight transition-all duration-700 delay-100 ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            Turn Dead Leads Into
            <br />
            <span className="relative inline-block mt-2">
              <span className="relative z-10 bg-gradient-to-r from-[#FF6B35] via-[#F7931E] to-[#FF6B35] bg-clip-text text-transparent animate-gradient">
                Revenue Machines
              </span>
              <span className="absolute bottom-0 left-0 right-0 h-3 bg-gradient-to-r from-[#FF6B35]/30 via-[#F7931E]/30 to-[#FF6B35]/30 blur-xl"></span>
            </span>
          </h1>

          {/* Subheadline */}
          <p
            className={`text-xl sm:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed transition-all duration-700 delay-200 ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            RekindlePro's 28-agent AI system reactivates dormant leads, books qualified meetings,
            and delivers pipeline—while you sleep. <span className="text-[#FF6B35] font-semibold">Zero upfront cost.</span>
            <span className="text-[#F7931E] font-semibold"> Performance fee only.</span>
          </p>

          {/* Stats Row */}
          <div
            className={`grid grid-cols-1 sm:grid-cols-3 gap-8 mb-12 max-w-4xl mx-auto transition-all duration-700 delay-300 ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            <div className="bg-gradient-to-br from-[#1A1F2E] to-[#242938] rounded-2xl p-6 border border-[#FF6B35]/20 hover:border-[#FF6B35]/50 transition-all hover:scale-105 group">
              <div className="text-4xl font-bold text-[#FF6B35] mb-2 group-hover:scale-110 transition-transform">
                18-22%
              </div>
              <div className="text-gray-400 text-sm">Reply Rate</div>
              <div className="text-gray-500 text-xs mt-1">vs 4% industry avg</div>
            </div>

            <div className="bg-gradient-to-br from-[#1A1F2E] to-[#242938] rounded-2xl p-6 border border-[#F7931E]/20 hover:border-[#F7931E]/50 transition-all hover:scale-105 group">
              <div className="text-4xl font-bold text-[#F7931E] mb-2 group-hover:scale-110 transition-transform">
                £1.2M+
              </div>
              <div className="text-gray-400 text-sm">Pipeline Created</div>
              <div className="text-gray-500 text-xs mt-1">from dead leads</div>
            </div>

            <div className="bg-gradient-to-br from-[#1A1F2E] to-[#242938] rounded-2xl p-6 border border-[#10B981]/20 hover:border-[#10B981]/50 transition-all hover:scale-105 group">
              <div className="text-4xl font-bold text-[#10B981] mb-2 group-hover:scale-110 transition-transform">
                2,847
              </div>
              <div className="text-gray-400 text-sm">Leads Revived</div>
              <div className="text-gray-500 text-xs mt-1">in 90 days</div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div
            className={`flex flex-col sm:flex-row items-center justify-center gap-6 mb-16 transition-all duration-700 delay-400 ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            <button
              onClick={() => navigate('/pilot-application')}
              className="group relative px-10 py-5 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold text-lg rounded-full transition-all duration-300 transform hover:scale-105 shadow-[0_0_50px_rgba(255,107,53,0.3)] hover:shadow-[0_0_60px_rgba(255,107,53,0.6)] overflow-hidden"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
              <span className="relative z-10 flex items-center gap-2">
                Start Pilot Program
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>

            <button
              onClick={() => {
                document.getElementById('how-it-works')?.scrollIntoView({
                  behavior: 'smooth'
                });
              }}
              className="group px-10 py-5 bg-transparent border-2 border-[#FF6B35] text-[#FF6B35] hover:bg-[#FF6B35] hover:text-white font-bold text-lg rounded-full transition-all duration-300 transform hover:scale-105"
            >
              <span className="flex items-center gap-2">
                Watch Demo
                <Zap className="w-5 h-5 group-hover:rotate-12 transition-transform" />
              </span>
            </button>
          </div>

          {/* Trust Indicators */}
          <div
            className={`transition-all duration-700 delay-500 ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            <p className="text-sm text-gray-500 mb-4">TRUSTED BY REVENUE TEAMS AT</p>
            <div className="flex flex-wrap items-center justify-center gap-8 opacity-60">
              <div className="text-gray-400 font-semibold text-lg">TechCorp</div>
              <div className="text-gray-400 font-semibold text-lg">SaaS Unicorn</div>
              <div className="text-gray-400 font-semibold text-lg">Enterprise Co</div>
              <div className="text-gray-400 font-semibold text-lg">Scale Inc</div>
            </div>
          </div>

          {/* Floating Feature Icons */}
          <div className="absolute top-40 left-20 hidden lg:block">
            <div className="w-16 h-16 bg-gradient-to-br from-[#FF6B35]/20 to-[#F7931E]/20 rounded-2xl border border-[#FF6B35]/30 flex items-center justify-center backdrop-blur-sm animate-float">
              <Brain className="w-8 h-8 text-[#FF6B35]" />
            </div>
          </div>

          <div className="absolute bottom-40 right-20 hidden lg:block">
            <div className="w-16 h-16 bg-gradient-to-br from-[#F7931E]/20 to-[#FF6B35]/20 rounded-2xl border border-[#F7931E]/30 flex items-center justify-center backdrop-blur-sm animate-float" style={{ animationDelay: '1s' }}>
              <TrendingUp className="w-8 h-8 text-[#F7931E]" />
            </div>
          </div>

          <div className="absolute top-60 right-40 hidden lg:block">
            <div className="w-16 h-16 bg-gradient-to-br from-[#10B981]/20 to-[#059669]/20 rounded-2xl border border-[#10B981]/30 flex items-center justify-center backdrop-blur-sm animate-float" style={{ animationDelay: '2s' }}>
              <Target className="w-8 h-8 text-[#10B981]" />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0a0e1a] to-transparent"></div>
    </div>
  );
};

// Add animation keyframes to index.css
/*
@keyframes gradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradient 3s ease infinite;
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
*/
