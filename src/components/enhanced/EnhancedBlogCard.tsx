/**
 * Enhanced Blog Card Component
 * Modern card design with hover effects and smooth transitions
 * Maintains RekindlePro branding
 */

import { Calendar, User, Clock, ArrowRight, TrendingUp } from 'lucide-react';

interface BlogCardProps {
  title: string;
  excerpt: string;
  author: string;
  date: string;
  readTime: string;
  category: string;
  image: string;
  onClick: () => void;
}

export const EnhancedBlogCard = ({
  title,
  excerpt,
  author,
  date,
  readTime,
  category,
  image,
  onClick
}: BlogCardProps) => {
  return (
    <article
      onClick={onClick}
      className="group cursor-pointer bg-gradient-to-br from-[#1A1F2E] to-[#242938] rounded-2xl overflow-hidden border border-gray-800 hover:border-[#FF6B35]/50 transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl hover:shadow-[#FF6B35]/20"
    >
      {/* Image Container */}
      <div className="relative h-56 overflow-hidden bg-gray-900">
        <img
          src={image}
          alt={title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        />

        {/* Category Badge */}
        <div className="absolute top-4 left-4 px-4 py-2 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white text-xs font-bold rounded-full shadow-lg backdrop-blur-sm">
          {category}
        </div>

        {/* Trending Badge (optional - can be conditional) */}
        <div className="absolute top-4 right-4 px-3 py-1.5 bg-black/60 text-white text-xs font-semibold rounded-full backdrop-blur-sm border border-white/20 flex items-center gap-1">
          <TrendingUp className="w-3 h-3" />
          <span>Trending</span>
        </div>

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#1A1F2E] via-transparent to-transparent opacity-60"></div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Title */}
        <h3 className="text-2xl font-bold text-white mb-3 leading-tight group-hover:text-[#FF6B35] transition-colors line-clamp-2">
          {title}
        </h3>

        {/* Excerpt */}
        <p className="text-gray-400 mb-4 line-clamp-3 leading-relaxed">
          {excerpt}
        </p>

        {/* Meta Information */}
        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <User className="w-4 h-4" />
              <span>{author}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4" />
              <span>{date}</span>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4" />
            <span>{readTime}</span>
          </div>
        </div>

        {/* Read More Link */}
        <div className="flex items-center text-[#FF6B35] font-semibold group-hover:text-[#F7931E] transition-colors">
          <span>Read Full Article</span>
          <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform" />
        </div>
      </div>

      {/* Bottom Accent Line */}
      <div className="h-1 bg-gradient-to-r from-[#FF6B35] via-[#F7931E] to-[#FF6B35] opacity-0 group-hover:opacity-100 transition-opacity"></div>
    </article>
  );
};

/**
 * Enhanced Blog Grid Container
 */
export const EnhancedBlogGrid = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {children}
    </div>
  );
};

/**
 * Enhanced Blog Header
 */
export const EnhancedBlogHeader = () => {
  return (
    <div className="text-center mb-16">
      <div className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#FF6B35]/10 to-[#F7931E]/10 border border-[#FF6B35]/30 rounded-full mb-6 backdrop-blur-sm">
        <span className="text-sm font-semibold text-white">REKINDLE INSIGHTS</span>
      </div>

      <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6 tracking-tight">
        Revenue <span className="bg-gradient-to-r from-[#FF6B35] to-[#F7931E] bg-clip-text text-transparent">Intelligence</span>
      </h1>

      <p className="text-xl text-gray-400 max-w-3xl mx-auto leading-relaxed">
        Data-driven insights on B2B sales, cold outreach, lead reactivation, and AI-powered revenue growth.
      </p>
    </div>
  );
};
