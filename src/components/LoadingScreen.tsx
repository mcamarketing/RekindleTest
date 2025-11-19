import { useEffect, useState } from 'react';
import { Sparkles, Zap } from 'lucide-react';

interface LoadingScreenProps {
  onComplete?: () => void;
}

export function LoadingScreen({ onComplete }: LoadingScreenProps) {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState<'loading' | 'ready' | 'fadeout'>('loading');

  useEffect(() => {
    // Simulate loading progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setStage('ready');
          setTimeout(() => {
            setStage('fadeout');
            setTimeout(() => {
              onComplete?.();
            }, 600);
          }, 800);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div
      className={`fixed inset-0 z-[9999] flex items-center justify-center transition-opacity duration-500 ${
        stage === 'fadeout' ? 'opacity-0' : 'opacity-100'
      }`}
    >
      {/* Animated background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#1A1F2E] via-[#0F1419] to-[#1A1F2E]">
        {/* Aurora effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1200px] h-[1200px] bg-[#FF6B35] rounded-full blur-[200px] opacity-20 animate-pulse" />
          <div className="absolute top-1/4 right-1/4 w-[800px] h-[800px] bg-[#F7931E] rounded-full blur-[180px] opacity-15 animate-aurora" />
          <div className="absolute bottom-1/4 left-1/4 w-[600px] h-[600px] bg-purple-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '2s' }} />
        </div>

        {/* Grid pattern overlay */}
        <div className="absolute inset-0 opacity-[0.02]" style={{
          backgroundImage: 'linear-gradient(#FF6B35 1px, transparent 1px), linear-gradient(90deg, #FF6B35 1px, transparent 1px)',
          backgroundSize: '50px 50px'
        }} />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center">
        {/* Logo with epic animation */}
        <div className={`mb-12 transition-all duration-700 ${
          stage === 'loading' ? 'scale-100' : 'scale-110'
        }`}>
          <div className="relative">
            {/* Rotating glow rings */}
            <div className="absolute inset-0 -m-8">
              <div className="absolute inset-0 rounded-full border-2 border-[#FF6B35]/30 animate-spin" style={{ animationDuration: '3s' }} />
              <div className="absolute inset-0 rounded-full border-2 border-[#F7931E]/20 animate-spin" style={{ animationDuration: '4s', animationDirection: 'reverse' }} />
            </div>

            {/* Logo container */}
            <div className="relative bg-gradient-to-br from-[#FF6B35] to-[#F7931E] p-8 rounded-3xl shadow-2xl shadow-[#FF6B35]/50">
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-3xl" />
              <img
                src="/images/image copy copy.png"
                alt="Rekindle.ai"
                className="h-24 w-auto relative z-10"
              />
            </div>

            {/* Floating sparkles */}
            <div className="absolute -top-4 -right-4">
              <Sparkles className="w-8 h-8 text-[#FF6B35] animate-pulse" />
            </div>
            <div className="absolute -bottom-4 -left-4">
              <Zap className="w-6 h-6 text-[#F7931E] animate-bounce" />
            </div>
          </div>
        </div>

        {/* Loading text */}
        <div className="mb-8 text-center">
          <h2 className={`text-4xl font-black text-white mb-3 transition-all duration-500 ${
            stage === 'ready' ? 'scale-105' : 'scale-100'
          }`}>
            {stage === 'ready' ? 'Welcome Back!' : 'Preparing Your Dashboard'}
          </h2>
          <p className="text-gray-400 text-lg font-medium animate-pulse">
            {stage === 'ready'
              ? "Let's revive some leads"
              : 'Setting up your AI-powered workspace...'}
          </p>
        </div>

        {/* Progress bar */}
        <div className="w-80 h-2 bg-white/10 rounded-full overflow-hidden backdrop-blur-sm">
          <div
            className="h-full bg-gradient-to-r from-[#FF6B35] via-[#F7931E] to-[#FF6B35] rounded-full transition-all duration-300 ease-out shadow-lg shadow-[#FF6B35]/50"
            style={{
              width: `${progress}%`,
              backgroundSize: '200% 100%',
              animation: 'shimmer 2s infinite'
            }}
          />
        </div>

        {/* Percentage */}
        <div className="mt-4 text-2xl font-black text-white">
          {Math.round(progress)}%
        </div>

        {/* Fun loading messages */}
        <div className="mt-8 h-6">
          {progress < 30 && (
            <p className="text-sm text-gray-500 animate-fade-in">
              🔥 Firing up AI engines...
            </p>
          )}
          {progress >= 30 && progress < 60 && (
            <p className="text-sm text-gray-500 animate-fade-in">
              🎯 Loading your leads...
            </p>
          )}
          {progress >= 60 && progress < 90 && (
            <p className="text-sm text-gray-500 animate-fade-in">
              ⚡ Syncing campaigns...
            </p>
          )}
          {progress >= 90 && stage !== 'ready' && (
            <p className="text-sm text-gray-500 animate-fade-in">
              ✨ Almost there...
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
