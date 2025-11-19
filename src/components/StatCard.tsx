import { LucideIcon } from 'lucide-react';
import { useCountUp } from '../hooks/useCountUp';

interface StatCardProps {
  title: string;
  value: string | number;
  numericValue?: number;
  icon: LucideIcon;
  gradient: string;
  description?: string;
  trend?: 'up' | 'down' | null;
  trendValue?: string;
  delay?: number;
  onClick?: () => void;
}

export function StatCard({
  title,
  value,
  numericValue,
  icon: Icon,
  gradient,
  description,
  trend,
  trendValue,
  delay = 0,
  onClick
}: StatCardProps) {
  const animatedValue = numericValue !== undefined ? useCountUp({ end: numericValue, duration: 2000 }) : null;
  const displayValue = animatedValue !== null ? animatedValue.toLocaleString() : value;

  return (
    <div
      className={`glass-card glass-card-hover p-8 h-full animate-fade-in group relative overflow-hidden ${onClick ? 'cursor-pointer' : ''}`}
      style={{ animationDelay: `${delay}ms` }}
      onClick={onClick}
    >
      {/* Gradient glow on hover */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">
              {title}
            </p>
            <div className="flex items-baseline gap-2 mb-2">
              <p className="text-4xl font-black text-white">
                {displayValue}
              </p>
              {trend && trendValue && (
                <span className={`text-sm font-semibold ${trend === 'up' ? 'text-green-400' : 'text-red-400'} flex items-center gap-1`}>
                  {trend === 'up' ? '↑' : '↓'}
                  {trendValue}
                </span>
              )}
            </div>
            {description && (
              <p className="text-sm text-gray-400 font-medium">
                {description}
              </p>
            )}
          </div>
          <div className={`p-5 bg-gradient-to-br ${gradient} rounded-2xl transition-all duration-500 group-hover:scale-110 group-hover:rotate-12 shadow-lg group-hover:shadow-2xl animate-float`} style={{ animationDelay: `${delay * 0.5}ms` }}>
            <Icon className="w-10 h-10 text-white" />
          </div>
        </div>
      </div>
    </div>
  );
}

