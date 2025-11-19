import { X, Mail, Phone, Building2, Calendar, TrendingUp, MessageSquare } from 'lucide-react';

interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  company: string | null;
  job_title: string | null;
  status: string;
  lead_score: number;
  last_contact_date: string | null;
  total_messages_sent: number;
  created_at: string;
}

interface LeadQuickViewProps {
  lead: Lead;
  onClose: () => void;
}

export function LeadQuickView({ lead, onClose }: LeadQuickViewProps) {
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
      contacted: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
      engaged: 'bg-purple-500/20 text-purple-400 border-purple-500/50',
      qualified: 'bg-green-500/20 text-green-400 border-green-500/50',
      meeting_booked: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50',
      converted: 'bg-teal-500/20 text-teal-400 border-teal-500/50',
      unresponsive: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
      opted_out: 'bg-red-500/20 text-red-400 border-red-500/50',
    };
    return colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/50';
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center px-4 animate-fade-in"
      onClick={onClose}
    >
      <div
        className="glass-card rounded-3xl p-8 max-w-2xl w-full relative animate-scale-in shadow-2xl border-2 border-white/20"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 glass-morphism rounded-full hover:bg-white/20 transition-all group"
        >
          <X className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
        </button>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">
                {lead.first_name} {lead.last_name}
              </h2>
              {lead.job_title && (
                <p className="text-gray-400 text-lg">{lead.job_title}</p>
              )}
            </div>
            <div className={`px-4 py-2 rounded-xl border-2 ${getStatusColor(lead.status)} font-semibold text-sm`}>
              {lead.status.replace('_', ' ').toUpperCase()}
            </div>
          </div>

          {/* Score badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 glass-morphism rounded-xl border border-white/10">
            <TrendingUp className={`w-5 h-5 ${getScoreColor(lead.lead_score)}`} />
            <span className="text-white font-semibold">Lead Score:</span>
            <span className={`text-2xl font-black ${getScoreColor(lead.lead_score)}`}>
              {lead.lead_score}
            </span>
          </div>
        </div>

        {/* Contact Info */}
        <div className="space-y-4 mb-8">
          <div className="flex items-center gap-3 glass-morphism p-4 rounded-xl group hover:bg-white/10 transition-all">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg">
              <Mail className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="text-sm text-gray-400">Email</div>
              <a href={`mailto:${encodeURIComponent(lead.email)}`} className="text-white font-medium hover:text-orange-400 transition-colors">
                {lead.email}
              </a>
            </div>
          </div>

          {lead.phone && (
            <div className="flex items-center gap-3 glass-morphism p-4 rounded-xl group hover:bg-white/10 transition-all">
              <div className="p-2 bg-gradient-to-br from-green-500 to-green-600 rounded-lg">
                <Phone className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="text-sm text-gray-400">Phone</div>
                <a href={`tel:${encodeURIComponent(lead.phone)}`} className="text-white font-medium hover:text-orange-400 transition-colors">
                  {lead.phone}
                </a>
              </div>
            </div>
          )}

          {lead.company && (
            <div className="flex items-center gap-3 glass-morphism p-4 rounded-xl group hover:bg-white/10 transition-all">
              <div className="p-2 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="text-sm text-gray-400">Company</div>
                <div className="text-white font-medium">{lead.company}</div>
              </div>
            </div>
          )}
        </div>

        {/* Engagement Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="glass-morphism p-4 rounded-xl text-center">
            <MessageSquare className="w-6 h-6 text-orange-400 mx-auto mb-2" />
            <div className="text-2xl font-black text-white mb-1">{lead.total_messages_sent || 0}</div>
            <div className="text-sm text-gray-400">Messages Sent</div>
          </div>

          <div className="glass-morphism p-4 rounded-xl text-center">
            <Calendar className="w-6 h-6 text-blue-400 mx-auto mb-2" />
            <div className="text-2xl font-black text-white mb-1">
              {lead.last_contact_date
                ? new Date(lead.last_contact_date).toLocaleDateString()
                : 'Never'}
            </div>
            <div className="text-sm text-gray-400">Last Contact</div>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-8 flex gap-3">
          <button
            onClick={() => {
              // Sanitize email to prevent XSS via mailto: injection
              const sanitizedEmail = encodeURIComponent(lead.email.replace(/[^\w@.\-+]/g, ''));
              window.location.href = `mailto:${sanitizedEmail}`;
            }}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-bold rounded-xl hover:shadow-2xl hover:shadow-blue-500/50 transition-all hover:scale-105"
          >
            Send Email
          </button>
          <button
            onClick={onClose}
            className="px-6 py-3 glass-morphism text-white font-bold rounded-xl hover:bg-white/20 transition-all"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

