// Supernova Landing Page Enhancements
// Conversion-optimized components with emotional engineering
import { useState, useEffect } from 'react';
import { Clock, TrendingUp, Zap, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

// URGENCY: Animated Countdown Timer
export const CountdownTimer = ({ deadline = "2025-12-31T23:59:59" }: { deadline?: string }) => {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  });

  useEffect(() => {
    const calculateTimeLeft = () => {
      const difference = +new Date(deadline) - +new Date();
      if (difference > 0) {
        setTimeLeft({
          days: Math.floor(difference / (1000 * 60 * 60 * 24)),
          hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
          minutes: Math.floor((difference / 1000 / 60) % 60),
          seconds: Math.floor((difference / 1000) % 60),
        });
      }
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);
    return () => clearInterval(timer);
  }, [deadline]);

  return (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="inline-flex items-center gap-4 px-6 py-4 bg-gradient-to-r from-red-500/20 via-orange-500/20 to-red-500/20 border-2 border-red-500/40 rounded-2xl backdrop-blur-sm"
    >
      <Clock className="w-6 h-6 text-red-400 animate-pulse" />
      <div className="flex items-center gap-3 text-white font-mono">
        <TimeBlock value={timeLeft.days} label="DAYS" />
        <Separator />
        <TimeBlock value={timeLeft.hours} label="HRS" />
        <Separator />
        <TimeBlock value={timeLeft.minutes} label="MIN" />
        <Separator />
        <TimeBlock value={timeLeft.seconds} label="SEC" />
      </div>
      <span className="text-red-400 font-bold text-sm animate-pulse">PILOT CLOSES SOON</span>
    </motion.div>
  );
};

const TimeBlock = ({ value, label }: { value: number; label: string }) => (
  <div className="flex flex-col items-center">
    <motion.div
      key={value}
      initial={{ y: -10, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="text-3xl font-black tabular-nums text-white drop-shadow-[0_0_10px_rgba(255,107,53,0.8)]"
    >
      {String(value).padStart(2, '0')}
    </motion.div>
    <div className="text-[10px] text-gray-400 font-semibold tracking-wider">{label}</div>
  </div>
);

const Separator = () => (
  <div className="text-2xl font-black text-orange-500 animate-pulse">:</div>
);

// SCARCITY: Live Spots Counter with Pulsing Animation
export const LiveSpotsCounter = ({ initialSpots = 47 }: { initialSpots?: number }) => {
  const [spots, setSpots] = useState(initialSpots);
  const [justChanged, setJustChanged] = useState(false);

  useEffect(() => {
    // Simulate spots decreasing every 12-20 seconds
    const interval = setInterval(() => {
      setSpots(prev => {
        const newSpots = Math.max(12, prev - Math.floor(Math.random() * 2 + 1));
        if (newSpots !== prev) {
          setJustChanged(true);
          setTimeout(() => setJustChanged(false), 2000);
        }
        return newSpots;
      });
    }, Math.random() * 8000 + 12000); // 12-20 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{
        scale: justChanged ? [1, 1.05, 1] : 1,
        opacity: 1
      }}
      transition={{ duration: 0.3 }}
      className={`inline-flex items-center gap-3 px-6 py-3 rounded-full ${
        justChanged
          ? 'bg-red-500/30 border-red-500 shadow-[0_0_30px_rgba(239,68,68,0.5)]'
          : 'bg-orange-500/10 border-orange-500/40'
      } border-2 transition-all duration-300`}
    >
      <span className="relative flex h-3 w-3">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
        <span className="relative inline-flex rounded-full h-3 w-3 bg-orange-500"></span>
      </span>
      <AlertCircle className="w-5 h-5 text-orange-400" />
      <span className="text-white font-bold">
        Only <span className="text-2xl text-orange-400 font-black animate-pulse mx-1">{spots}</span> spots left
      </span>
      <span className="text-orange-300 text-sm">at pilot pricing</span>
    </motion.div>
  );
};

// TRUST: Animated Stat Counter
export const AnimatedStat = ({
  end,
  prefix = '',
  suffix = '',
  duration = 2000,
  decimals = 0
}: {
  end: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
  decimals?: number;
}) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);

      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(end * easeOutQuart);

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration]);

  return (
    <motion.span
      initial={{ scale: 0.5, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5, type: "spring" }}
      className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent font-black drop-shadow-[0_0_20px_rgba(255,107,53,0.6)]"
    >
      {prefix}{count.toFixed(decimals)}{suffix}
    </motion.span>
  );
};

// ENGAGEMENT: Pulsing CTA Button with Magnetic Effect
export const MagneticCTA = ({
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
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    setMousePosition({ x: x * 0.3, y: y * 0.3 });
  };

  const handleMouseLeave = () => {
    setMousePosition({ x: 0, y: 0 });
    setIsHovered(false);
  };

  const baseClasses = "relative px-10 py-6 font-bold text-lg rounded-full transition-all duration-300 overflow-hidden group";
  const primaryClasses = "bg-gradient-to-r from-orange-500 via-orange-600 to-orange-500 bg-size-200 text-white shadow-[0_0_40px_rgba(255,107,53,0.4)] hover:shadow-[0_0_80px_rgba(255,107,53,0.7),0_0_120px_rgba(255,107,53,0.5)]";
  const secondaryClasses = "bg-transparent border-2 border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white shadow-[0_0_20px_rgba(255,107,53,0.2)]";

  return (
    <motion.button
      className={`${baseClasses} ${variant === 'primary' ? primaryClasses : secondaryClasses} ${className}`}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      animate={{
        x: mousePosition.x,
        y: mousePosition.y,
        scale: isHovered ? 1.05 : 1,
      }}
      transition={{ type: "spring", stiffness: 150, damping: 15 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Shimmer effect */}
      <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />

      {/* Glow pulse animation */}
      {variant === 'primary' && (
        <>
          <span className="absolute inset-0 bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500" />
          <span className="absolute -inset-1 bg-gradient-to-r from-orange-500 to-orange-600 opacity-0 group-hover:opacity-30 blur-2xl animate-pulse" />
        </>
      )}

      <span className="relative z-10 flex items-center justify-center gap-3">
        {children}
      </span>
    </motion.button>
  );
};

// SOCIAL PROOF: Scrolling Trust Badges
export const ScrollingTrustBadges = () => {
  const badges = [
    { metric: '15.2%', label: 'Meeting Rate', icon: TrendingUp, color: 'text-green-400' },
    { metric: '98%', label: 'SMS Open Rate', icon: Zap, color: 'text-blue-400' },
    { metric: '72hr', label: 'Time to First Meeting', icon: Clock, color: 'text-orange-400' },
    { metric: '2.3x', label: 'vs Industry Average', icon: TrendingUp, color: 'text-purple-400' },
  ];

  return (
    <div className="relative overflow-hidden py-6">
      <motion.div
        className="flex gap-6"
        animate={{ x: [0, -1000] }}
        transition={{
          x: {
            repeat: Infinity,
            repeatType: "loop",
            duration: 20,
            ease: "linear",
          },
        }}
      >
        {[...badges, ...badges, ...badges].map((badge, index) => {
          const Icon = badge.icon;
          return (
            <div
              key={index}
              className="flex-shrink-0 flex items-center gap-4 px-6 py-4 bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-xl hover:border-orange-500/50 transition-all duration-300"
            >
              <Icon className={`w-6 h-6 ${badge.color}`} />
              <div>
                <div className={`text-2xl font-black ${badge.color}`}>{badge.metric}</div>
                <div className="text-xs text-gray-400">{badge.label}</div>
              </div>
            </div>
          );
        })}
      </motion.div>
    </div>
  );
};

// URGENCY: Pricing Lock Guarantee Box
export const PricingLockGuarantee = ({ discount = "50%" }: { discount?: string }) => {
  return (
    <motion.div
      initial={{ scale: 0.95, opacity: 0, y: 20 }}
      whileInView={{ scale: 1, opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
      className="relative max-w-4xl mx-auto p-8 bg-gradient-to-br from-orange-500/20 via-red-500/20 to-orange-500/20 border-2 border-orange-500 rounded-3xl backdrop-blur-sm overflow-hidden"
    >
      {/* Animated background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 cyberpunk-grid" />
      </div>

      <div className="relative z-10 text-center">
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          className="inline-block mb-4"
        >
          <div className="text-6xl">🔒</div>
        </motion.div>

        <h3 className="text-3xl md:text-4xl font-black text-white mb-4">
          Lock In <span className="text-orange-400">{discount} OFF</span> Pilot Pricing Forever
        </h3>

        <p className="text-lg text-gray-300 mb-6 max-w-2xl mx-auto">
          <strong className="text-white">Founding members pay £99.99/mo forever.</strong> Original pricing is £199/mo.
          That's <span className="text-orange-400 font-bold">50% off for life</span>—locked in permanently after pilot.
        </p>

        <div className="flex items-center justify-center gap-4 text-sm text-gray-400">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
            <span>Founding rate: <strong className="text-white">£99.99/mo</strong></span>
          </div>
          <div className="text-gray-600">→</div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span>Original: <strong className="text-red-400 line-through">£199/mo</strong></span>
          </div>
        </div>

        <motion.div
          className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-orange-500/20 border border-orange-500/40 rounded-full text-orange-300 text-sm font-semibold"
          animate={{ scale: [1, 1.02, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Zap className="w-4 h-4" />
          Guaranteed for all pilot members—no price increases, ever
        </motion.div>
      </div>

      {/* Corner accent */}
      <div className="absolute top-4 right-4 w-20 h-20 bg-orange-500/20 rounded-full blur-2xl animate-pulse" />
      <div className="absolute bottom-4 left-4 w-24 h-24 bg-red-500/20 rounded-full blur-3xl animate-pulse delay-1000" />
    </motion.div>
  );
};

// CONVERSION: Two-Step Micro-Commitment CTA
export const TwoStepCTA = ({ onSubmit }: { onSubmit?: (email: string) => void }) => {
  const [step, setStep] = useState<'email' | 'confirm' | 'success'>('email');
  const [email, setEmail] = useState('');

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email && email.includes('@')) {
      setStep('confirm');
    }
  };

  const handleConfirm = () => {
    onSubmit?.(email);
    setStep('success');
    setTimeout(() => {
      window.location.href = '/pilot-application';
    }, 2000);
  };

  if (step === 'success') {
    return (
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="max-w-md mx-auto p-6 bg-green-500/20 border-2 border-green-500 rounded-2xl text-center"
      >
        <div className="text-5xl mb-3">✓</div>
        <div className="text-xl font-bold text-white mb-2">Check Your Inbox!</div>
        <div className="text-sm text-gray-300">Redirecting to application...</div>
      </motion.div>
    );
  }

  if (step === 'confirm') {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="max-w-md mx-auto p-6 bg-gray-900/80 backdrop-blur-sm border-2 border-orange-500 rounded-2xl"
      >
        <h4 className="text-xl font-bold text-white mb-4">Confirm Your Email</h4>
        <p className="text-gray-300 mb-4">Send FREE CRM analysis to:</p>
        <div className="px-4 py-3 bg-gray-800 rounded-lg text-white font-mono text-sm mb-6">
          {email}
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setStep('email')}
            className="flex-1 px-6 py-3 bg-gray-700 text-white rounded-full font-semibold hover:bg-gray-600 transition"
          >
            Change
          </button>
          <button
            onClick={handleConfirm}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-full font-bold hover:shadow-lg transition"
          >
            Confirm & Continue
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <form onSubmit={handleEmailSubmit} className="max-w-2xl mx-auto">
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex flex-col sm:flex-row gap-4"
      >
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@workemail.com"
          className="flex-1 px-6 py-5 bg-gray-900/80 backdrop-blur-sm border-2 border-gray-700 focus:border-orange-500 outline-none text-white rounded-full text-lg transition-all duration-300"
          required
        />
        <button
          type="submit"
          className="px-10 py-5 bg-gradient-to-r from-orange-500 via-orange-600 to-orange-500 text-white font-bold text-lg rounded-full hover:shadow-[0_0_40px_rgba(255,107,53,0.6)] transition-all duration-300 hover:scale-105"
        >
          Get FREE Analysis →
        </button>
      </motion.div>
      <p className="text-center text-gray-400 text-sm mt-4">
        ✓ No credit card required • ✓ 72-hour turnaround • ✓ Instant access
      </p>
    </form>
  );
};
