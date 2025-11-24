import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: "up" | "down" | null;
  trendValue?: string;
  delay?: number;
  onClick?: () => void;
}

export function StatCard({
  title,
  value,
  icon: Icon,
  description,
  delay = 0,
  onClick,
}: StatCardProps) {
  return (
    <div
      className={`bg-white border border-[#e3e8ee] rounded-lg p-6 hover:shadow-md transition-shadow duration-200 ${
        onClick ? "cursor-pointer" : ""
      }`}
      style={{ animationDelay: `${delay}ms` }}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs uppercase tracking-wider text-[#727f96] font-medium">
          {title}
        </span>
        <Icon className="w-4 h-4 text-[#727f96]" />
      </div>
      <div className="text-3xl font-bold text-[#0a2540] mb-1 tabular-nums">
        {value}
      </div>
      <div className="text-sm text-[#425466]">{description}</div>
    </div>
  );
}

