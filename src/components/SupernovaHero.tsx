// SUPERNOVA HERO SECTION - Maximum Emotional Impact & Conversion
import { useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { ShieldCheck, Shield, Zap } from 'lucide-react';
import { CountdownTimer, LiveSpotsCounter, MagneticCTA, TwoStepCTA } from './SupernovaEnhancements';

export function SupernovaHero() {
  const { scrollY } = useScroll();
  const opacity = useTransform(scrollY, [0, 300], [1, 0]);
  const scale = useTransform(scrollY, [0, 300], [1, 0.95]);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <section className="relative pt-32 md:pt-40 pb-20 px-4 overflow-hidden min-h-screen flex items-center">
      {/* Supernova Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />

      {/* Aurora effect orbs with enhanced animation */}
      <motion.div
        className="absolute top-1/4 left-10 w-96 h-96 bg-gradient-to-br from-orange-500/30 via-orange-600/20 to-transparent rounded-full blur-[100px]"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
          x: [0, 50, 0],
          y: [0, -30, 0],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute bottom-1/4 right-10 w-[500px] h-[500px] bg-gradient-to-br from-orange-400/20 via-orange-500/10 to-transparent rounded-full blur-[120px]"
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.2, 0.4, 0.2],
          x: [0, -40, 0],
          y: [0, 40, 0],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2,
        }}
      />
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-br from-orange-600/10 via-transparent to-orange-400/10 rounded-full blur-[150px]"
        animate={{
          scale: [1, 1.15, 1],
          opacity: [0.1, 0.3, 0.1],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
      />

      {/* Radial gradient overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,107,53,0.15),transparent_70%)]" />

      {/* Enhanced dot grid pattern with animation */}
      <motion.div
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px)',
          backgroundSize: '40px 40px',
          opacity,
        }}
      />

      <motion.div
        style={{ scale, opacity }}
        className="relative max-w-7xl mx-auto text-center"
      >
        {/* URGENCY: Countdown Timer */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex justify-center mb-8"
        >
          <CountdownTimer deadline="2025-12-31T23:59:59" />
        </motion.div>

        {/* FOMO: Live Spots Counter */}
        <motion.div
          initial={{ y: -10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex justify-center mb-10"
        >
          <LiveSpotsCounter initialSpots={47} />
        </motion.div>

        {/* Social Proof Badge */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="inline-flex items-center gap-2 px-6 py-3 glass-card rounded-full mb-10 border-2 border-orange-500/40 hover:border-orange-500/60 transition-all duration-300"
        >
          <Zap className="w-5 h-5 text-orange-400 animate-pulse" />
          <span className="text-sm text-white font-semibold">Join 10,000+ companies recovering dead pipeline</span>
        </motion.div>

        {/* HERO HEADLINE - Maximum Emotional Impact */}
        <motion.h1
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8, type: "spring", stiffness: 100 }}
          className="text-5xl md:text-6xl lg:text-7xl xl:text-[84px] font-black leading-[1.05] mb-8 tracking-tight"
        >
          <span className="block mb-4">
            <span className="bg-gradient-to-r from-white via-slate-100 to-white bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(255,255,255,0.3)] animate-holographic">
              You're Sitting On £500K-£2M in{' '}
              <motion.span
                className="bg-gradient-to-r from-red-400 via-red-500 to-red-600 bg-clip-text text-transparent"
                animate={{
                  textShadow: [
                    "0 0 20px rgba(239, 68, 68, 0.5)",
                    "0 0 40px rgba(239, 68, 68, 0.8)",
                    "0 0 20px rgba(239, 68, 68, 0.5)",
                  ],
                }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                DEAD
              </motion.span>{' '}
              Pipeline.
            </span>
          </span>
          <span className="block text-4xl md:text-5xl lg:text-6xl xl:text-7xl">
            <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent drop-shadow-[0_0_40px_rgba(255,107,53,0.5)] font-black animate-prismatic">
              We'll Resurrect It in 72 Hours—Or You Pay NOTHING.
            </span>
          </span>
        </motion.h1>

        {/* VALUE PROPOSITION Subheadline */}
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 1.2 }}
          className="text-xl md:text-2xl lg:text-3xl text-white max-w-5xl mx-auto mb-12 leading-tight font-bold"
        >
          <motion.span
            animate={{
              backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
            }}
            transition={{ duration: 5, repeat: Infinity }}
            className="bg-gradient-to-r from-orange-300 via-orange-400 to-orange-300 bg-clip-text text-transparent bg-[length:200%_auto]"
          >
            FREE 72-Hour Analysis
          </motion.span>
          {' → '}
          <span className="text-gray-200">Zero Platform Fee First 30 Days</span>
          {' → '}
          <span className="text-gray-200">Pay Only <strong className="text-orange-400">2.5% ACV</strong> Per Meeting</span>
        </motion.p>

        {/* TRUST BADGES */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 1.4 }}
          className="flex flex-wrap justify-center items-center gap-6 text-sm mb-12"
        >
          {/* SOC 2 Badge */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-3 glass-card px-5 py-3 rounded-xl border border-green-500/40 shadow-lg shadow-green-500/10 hover:border-green-500/60 transition-all cursor-pointer"
          >
            <ShieldCheck className="w-7 h-7 text-green-400" />
            <div className="text-left">
              <div className="text-white font-bold text-base">SOC 2 Type II</div>
              <div className="text-xs text-green-300">Enterprise Security</div>
            </div>
          </motion.div>

          {/* GDPR Badge */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-3 glass-card px-5 py-3 rounded-xl border border-blue-500/40 shadow-lg shadow-blue-500/10 hover:border-blue-500/60 transition-all cursor-pointer"
          >
            <Shield className="w-7 h-7 text-blue-400" />
            <div className="text-left">
              <div className="text-white font-bold text-base">GDPR Compliant</div>
              <div className="text-xs text-blue-300">EU Data Protection</div>
            </div>
          </motion.div>

          {/* Pilot Program Badge */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-3 glass-card px-5 py-3 rounded-xl border border-orange-500/40 shadow-lg hover:border-orange-500/60 transition-all cursor-pointer"
          >
            <div className="p-2 bg-orange-500/20 rounded-lg">
              <Shield className="w-5 h-5 text-orange-400" />
            </div>
            <div className="text-left">
              <div className="text-white font-bold text-sm">Invite-Only Pilot</div>
              <div className="text-xs text-orange-300">Qualified B2B teams only</div>
            </div>
          </motion.div>
        </motion.div>

        {/* PRIMARY CTA - Two-Step Micro-Commitment */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 1.6 }}
          className="mb-8"
        >
          <TwoStepCTA />
        </motion.div>

        {/* OR SEPARATOR */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8 }}
          className="flex items-center gap-4 max-w-2xl mx-auto mb-8"
        >
          <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-600 to-transparent" />
          <span className="text-gray-500 font-semibold text-sm">OR</span>
          <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-600 to-transparent" />
        </motion.div>

        {/* SECONDARY CTA - Apply Directly */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 2 }}
          className="flex justify-center mb-6"
        >
          <MagneticCTA
            variant="secondary"
            onClick={() => navigate('/pilot-application')}
          >
            Skip Analysis—Apply Directly for Pilot →
          </MagneticCTA>
        </motion.div>

        {/* MICRO-COPY: Trust Signals */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.2 }}
          className="flex flex-wrap justify-center gap-4 text-sm text-gray-400 mb-12"
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>No credit card required</span>
          </div>
          <span className="text-gray-600">•</span>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>72-hour turnaround</span>
          </div>
          <span className="text-gray-600">•</span>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>Cancel anytime</span>
          </div>
        </motion.div>

        {/* PROOF METRICS - Animated Stats */}
        <motion.div
          initial={{ y: 40, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-12"
        >
          {[
            { value: "15.2%", label: "Meeting Rate", highlight: true },
            { value: "72hr", label: "First Meeting", highlight: false },
            { value: "2.3x", label: "vs Industry Avg", highlight: true },
            { value: "98%", label: "SMS Open Rate", highlight: false },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ scale: 0.8, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
              whileHover={{ scale: 1.05 }}
              className="text-center group cursor-pointer"
            >
              <motion.div
                className={`text-4xl md:text-5xl font-black mb-2 ${
                  stat.highlight
                    ? 'bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent'
                    : 'text-white'
                }`}
                animate={{
                  textShadow: stat.highlight
                    ? [
                        "0 0 10px rgba(255,107,53,0.3)",
                        "0 0 20px rgba(255,107,53,0.5)",
                        "0 0 10px rgba(255,107,53,0.3)",
                      ]
                    : "none",
                }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {stat.value}
              </motion.div>
              <div className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">
                {stat.label}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>

      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-orange-400/30 rounded-full"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            animate={{
              y: [null, Math.random() * -500],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          />
        ))}
      </div>
    </section>
  );
}
