import { Lead } from "./Leads";
import { Mail, Phone, Building2, Eye, Trash2 } from "lucide-react";

interface LeadCardProps {
  lead: Lead;
  onQuickView: (lead: Lead) => void;
  onDelete: (leadId: string) => void;
  isSelected: boolean;
  onSelect: (leadId: string) => void;
}

export function LeadCard({
  lead,
  onQuickView,
  onDelete,
  isSelected,
  onSelect,
}: LeadCardProps) {
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      new: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      contacted: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
      engaged: "bg-purple-500/20 text-purple-400 border-purple-500/30",
      qualified: "bg-green-500/20 text-green-400 border-green-500/30",
      meeting_booked:
        "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
      converted: "bg-teal-500/20 text-teal-400 border-teal-500/30",
      unresponsive: "bg-gray-500/20 text-gray-400 border-gray-500/30",
      opted_out: "bg-red-500/20 text-red-400 border-red-500/30",
    };
    return colors[status] || "bg-gray-500/20 text-gray-400 border-gray-500/30";
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-400 font-bold";
    if (score >= 60) return "text-yellow-400 font-semibold";
    if (score >= 40) return "text-orange-400";
    return "text-red-400";
  };
  return (
    <div
      className={`bg-white/5 border border-white/10 rounded-xl p-4 transition-all duration-200 hover:bg-white/10 ${
        isSelected ? "bg-blue-500/10 border-blue-500/30" : ""
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => onSelect(lead.id)}
            className="w-4 h-4 rounded border-gray-600 text-[#FF6B35] focus:ring-[#FF6B35]"
          />
          <div className="flex items-center">
            <div className="flex-shrink-0 h-12 w-12 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-sm">
                {lead.first_name[0]}
                {lead.last_name[0]}
              </span>
            </div>
            <div className="ml-4">
              <div className="text-sm font-bold text-white">
                {lead.first_name} {lead.last_name}
              </div>
              <div className="text-sm text-gray-400">
                {lead.job_title || "No title"}
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onQuickView(lead)}
            className="text-[#FF6B35] hover:text-[#F7931E] p-2.5 rounded-xl hover:bg-[#FF6B35]/10 active:scale-95 transition-all duration-200"
            title="Quick view"
          >
            <Eye className="w-5 h-5" />
          </button>
          <button
            onClick={() => onDelete(lead.id)}
            className="text-red-400 hover:text-red-300 p-2.5 rounded-xl hover:bg-red-500/10 active:scale-95 transition-all duration-200"
            title="Delete lead"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <div className="text-gray-400 mb-1">Contact</div>
          <div className="flex items-center gap-2 text-gray-300">
            <Mail className="w-4 h-4 text-gray-500" />
            {lead.email}
          </div>
          {lead.phone && (
            <div className="flex items-center gap-2 text-gray-400 mt-1">
              <Phone className="w-4 h-4 text-gray-500" />
              {lead.phone}
            </div>
          )}
        </div>
        <div>
          <div className="text-gray-400 mb-1">Company</div>
          <div className="flex items-center gap-2 text-gray-300 font-medium">
            <Building2 className="w-4 h-4 text-gray-500" />
            {lead.company || "N/A"}
          </div>
        </div>
        <div>
          <div className="text-gray-400 mb-1">Status</div>
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-2 text-xs font-bold rounded-xl border ${getStatusColor(
              lead.status
            )}`}
          >
            <span className="w-2 h-2 rounded-full bg-current"></span>
            {lead.status.replace("_", " ")}
          </span>
        </div>
        <div>
          <div className="text-gray-400 mb-1">Score</div>
          <span className={`text-sm font-bold ${getScoreColor(lead.lead_score)}`}>
            {lead.lead_score}/100
          </span>
        </div>
        <div>
          <div className="text-gray-400 mb-1">Messages</div>
          <span className="text-sm text-white font-semibold">
            {lead.total_messages_sent}
          </span>
        </div>
      </div>
    </div>
  );
}
