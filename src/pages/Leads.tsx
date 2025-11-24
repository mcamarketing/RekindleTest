// @ts-nocheck
import { useEffect, useState } from 'react';
import { Navigation } from '../components/Navigation';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { useDebounce } from '../hooks/useDebounce';
import { LeadQuickView } from '../components/LeadQuickView';
import { Plus, Search, Download, Upload, Mail, Phone, Building2, Trash2, Eye, Users, Filter } from 'lucide-react';

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

export function Leads() {
  const { user } = useAuth();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedLeads, setSelectedLeads] = useState<Set<string>>(new Set());
  const [batchActionOpen, setBatchActionOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const leadsPerPage = 50; // Optimized for fast rendering
  const [quickViewLead, setQuickViewLead] = useState<Lead | null>(null);
  const [scoreFilter, setScoreFilter] = useState<[number, number]>([0, 100]);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Debounced search for better performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  useEffect(() => {
    loadLeads();

    // Keyboard shortcuts
    const handleKeyPress = (e: KeyboardEvent) => {
      // Press 'I' to import leads
      if (e.key === 'i' && !e.ctrlKey && !e.metaKey && document.activeElement?.tagName !== 'INPUT') {
        navigate('/leads/import');
      }
      // Press 'Escape' to close quick view
      if (e.key === 'Escape' && quickViewLead) {
        setQuickViewLead(null);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [quickViewLead]);

  const loadLeads = async () => {
    try {
      setLoading(true);
      // OPTIMIZED: Only load essential fields first for speed
      const { data, error } = await supabase
        .from('leads')
        .select('id, first_name, last_name, email, company, job_title, status, lead_score, created_at, last_contact_date')
        .order('created_at', { ascending: false })
        .limit(500); // Reasonable limit for performance

      if (error) throw error;
      setLeads(data || []);
    } catch (error) {
      console.error('Error loading leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteLead = async (leadId: string) => {
    if (!confirm('Are you sure you want to delete this lead?')) return;

    try {
      const { error } = await supabase
        .from('leads')
        .delete()
        .eq('id', leadId);

      if (error) throw error;
      setLeads(leads.filter(l => l.id !== leadId));
    } catch (error) {
      console.error('Error deleting lead:', error);
      alert('Failed to delete lead');
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  // BATCH ACTIONS
  const toggleLeadSelection = (leadId: string) => {
    const newSelected = new Set(selectedLeads);
    if (newSelected.has(leadId)) {
      newSelected.delete(leadId);
    } else {
      newSelected.add(leadId);
    }
    setSelectedLeads(newSelected);
  };

  const selectAllOnPage = () => {
    const pageLeads = paginatedLeads.map(l => l.id);
    setSelectedLeads(new Set(pageLeads));
  };

  const clearSelection = () => {
    setSelectedLeads(new Set());
  };

  const handleBatchAction = async (action: string) => {
    if (selectedLeads.size === 0) return;

    try {
      const updates: any = {};
      if (action === 'pause') updates.status = 'unresponsive';
      if (action === 'resume') updates.status = 'new';
      if (action === 'mark-qualified') updates.status = 'qualified';

      await supabase
        .from('leads')
        .update(updates)
        .in('id', Array.from(selectedLeads));

      await loadLeads();
      clearSelection();
      setBatchActionOpen(false);
    } catch (error) {
      console.error('Batch action error:', error);
      alert('Failed to perform batch action');
    }
  };

  // FILTERING & PAGINATION
  const filteredLeads = leads.filter(lead => {
    const matchesSearch =
      lead.first_name.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
      lead.last_name.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
      lead.email.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
      (lead.company || '').toLowerCase().includes(debouncedSearchQuery.toLowerCase());

    const matchesStatus = statusFilter === 'all' || lead.status === statusFilter;
    const matchesScore = lead.lead_score >= scoreFilter[0] && lead.lead_score <= scoreFilter[1];

    return matchesSearch && matchesStatus && matchesScore;
  });

  const totalPages = Math.ceil(filteredLeads.length / leadsPerPage);
  const startIndex = (currentPage - 1) * leadsPerPage;
  const endIndex = startIndex + leadsPerPage;
  const paginatedLeads = filteredLeads.slice(startIndex, endIndex);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      contacted: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      engaged: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      qualified: 'bg-green-500/20 text-green-400 border-green-500/30',
      meeting_booked: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      converted: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
      unresponsive: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      opted_out: 'bg-red-500/20 text-red-400 border-red-500/30',
    };
    return colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400 font-bold';
    if (score >= 60) return 'text-yellow-400 font-semibold';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
        <div className="absolute bottom-1/4 right-1/3 w-[700px] h-[700px] bg-green-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '7s' }} />
      </div>

      <Navigation currentPage="leads" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Header */}
        <div className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Leads</h1>
            <p className="text-gray-400 text-lg">
              Manage your dormant leads and track revival progress
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => navigate('/leads/import')}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-semibold rounded-xl hover:shadow-2xl hover:shadow-[#FF6B35]/40 transition-all duration-300 hover:scale-105 btn-shimmer"
            >
              <Upload className="w-5 h-5" />
              Import Leads
            </button>

            <button
              onClick={() => {
                const csv = [
                  ['First Name', 'Last Name', 'Email', 'Company', 'Status', 'Lead Score'].join(','),
                  ...filteredLeads.map(lead => [
                    lead.first_name,
                    lead.last_name,
                    lead.email,
                    lead.company || '',
                    lead.status,
                    lead.lead_score
                  ].join(','))
                ].join('\n');
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `leads-export-${new Date().toISOString().split('T')[0]}.csv`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="flex items-center gap-2 px-6 py-3 glass-card glass-card-hover text-white font-semibold rounded-xl transition-all duration-300"
            >
              <Download className="w-5 h-5" />
              Export
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="glass-card p-6 mb-8">
          <div className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search leads by name, email, or company..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3.5 bg-white/5 border border-white/10 text-white placeholder-gray-400 rounded-xl focus:ring-2 focus:ring-[#FF6B35] focus:border-transparent transition-all"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-6 py-3.5 bg-white/5 border border-white/10 text-white rounded-xl focus:ring-2 focus:ring-[#FF6B35] focus:border-transparent transition-all font-medium [&>option]:bg-slate-900 [&>option]:text-white"
            >
              <option value="all" className="bg-slate-900 text-white">All Status</option>
              <option value="new" className="bg-slate-900 text-white">New</option>
              <option value="contacted" className="bg-slate-900 text-white">Contacted</option>
              <option value="engaged" className="bg-slate-900 text-white">Engaged</option>
              <option value="qualified" className="bg-slate-900 text-white">Qualified</option>
              <option value="meeting_booked" className="bg-slate-900 text-white">Meeting Booked</option>
              <option value="converted" className="bg-slate-900 text-white">Converted</option>
              <option value="unresponsive" className="bg-slate-900 text-white">Unresponsive</option>
              <option value="opted_out" className="bg-slate-900 text-white">Opted Out</option>
            </select>

            <button
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className={`px-6 py-3.5 border rounded-xl font-medium transition-all flex items-center gap-2 ${showAdvancedFilters ? 'bg-[#FF6B35]/20 border-[#FF6B35] text-white' : 'bg-white/5 border-white/10 text-gray-300 hover:bg-white/10'}`}
            >
              <Filter className="w-5 h-5" />
              Filters
            </button>
          </div>

          {/* Advanced Filters */}
          {showAdvancedFilters && (
            <div className="p-6 glass-morphism rounded-xl border border-white/10 animate-fade-in">
              <div className="mb-4">
                <label className="block text-white font-semibold mb-3">Lead Score Range</label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={scoreFilter[0]}
                    onChange={(e) => setScoreFilter([parseInt(e.target.value), scoreFilter[1]])}
                    className="flex-1 h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-[#FF6B35]"
                  />
                  <span className="text-white font-mono text-lg w-12">{scoreFilter[0]}</span>
                  <span className="text-gray-400">to</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={scoreFilter[1]}
                    onChange={(e) => setScoreFilter([scoreFilter[0], parseInt(e.target.value)])}
                    className="flex-1 h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-[#FF6B35]"
                  />
                  <span className="text-white font-mono text-lg w-12">{scoreFilter[1]}</span>
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setScoreFilter([0, 100]);
                    setShowAdvancedFilters(false);
                  }}
                  className="px-4 py-2 glass-morphism text-gray-300 hover:text-white font-medium rounded-lg transition-all"
                >
                  Reset
                </button>
                <button
                  onClick={() => setShowAdvancedFilters(false)}
                  className="px-4 py-2 bg-[#FF6B35] text-white font-bold rounded-lg hover:bg-[#F7931E] transition-all"
                >
                  Apply
                </button>
              </div>
            </div>
          )}

          {/* BATCH ACTIONS BAR */}
          {selectedLeads.size > 0 && (
            <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-[#FF6B35]/20 to-[#F7931E]/20 border border-[#FF6B35]/30 rounded-xl">
              <div className="flex items-center gap-4">
                <span className="text-white font-bold">{selectedLeads.size} leads selected</span>
                <button
                  onClick={clearSelection}
                  className="text-sm text-gray-300 hover:text-white transition-colors"
                >
                  Clear selection
                </button>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleBatchAction('pause')}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-lg transition-all"
                >
                  Pause
                </button>
                <button
                  onClick={() => handleBatchAction('resume')}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-lg transition-all"
                >
                  Resume
                </button>
                <button
                  onClick={() => handleBatchAction('mark-qualified')}
                  className="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-300 font-semibold rounded-lg transition-all border border-green-500/30"
                >
                  Mark Qualified
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Leads List */}
        {loading ? (
          <div className="flex justify-center py-16">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-[#FF6B35]/30 rounded-full"></div>
              <div className="absolute inset-0 w-16 h-16 border-4 border-[#FF6B35] border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        ) : filteredLeads.length === 0 ? (
          <div className="glass-card p-12 text-center">
            <div className="p-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl w-fit mx-auto mb-6 shadow-2xl">
              <Users className="w-20 h-20 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">
              {searchQuery || statusFilter !== 'all' ? 'No leads found' : 'No leads yet'}
            </h3>
            <p className="text-gray-400 mb-8 text-lg">
              {searchQuery || statusFilter !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Get started by importing your first leads'}
            </p>
            {!searchQuery && statusFilter === 'all' && (
              <button
                onClick={() => navigate('/leads/import')}
                className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold rounded-xl hover:shadow-2xl hover:shadow-[#FF6B35]/40 transition-all duration-300 hover:scale-105 text-lg btn-shimmer"
              >
                <Plus className="w-6 h-6" />
                Import Leads
              </button>
            )}
          </div>
        ) : (
          <div className="glass-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-white/10">
                <thead className="bg-white/5">
                  <tr>
                    <th className="px-4 py-4 text-left">
                      <input
                        type="checkbox"
                        checked={selectedLeads.size === paginatedLeads.length && paginatedLeads.length > 0}
                        onChange={(e) => e.target.checked ? selectAllOnPage() : clearSelection()}
                        className="w-4 h-4 rounded border-gray-600 text-[#FF6B35] focus:ring-[#FF6B35]"
                      />
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                      Lead
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                      Messages
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-300 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                {paginatedLeads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-white/5 transition-all duration-200 group">
                    <td className="px-4 py-5">
                      <input
                        type="checkbox"
                        checked={selectedLeads.has(lead.id)}
                        onChange={() => toggleLeadSelection(lead.id)}
                        className="w-4 h-4 rounded border-gray-600 text-[#FF6B35] focus:ring-[#FF6B35]"
                      />
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-12 w-12 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                          <span className="text-white font-bold text-sm">
                            {lead.first_name[0]}{lead.last_name[0]}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-bold text-white">
                            {lead.first_name} {lead.last_name}
                          </div>
                          <div className="text-sm text-gray-400">
                            {lead.job_title || 'No title'}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <div className="flex flex-col gap-1.5">
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                          <Mail className="w-4 h-4 text-gray-500" />
                          {lead.email}
                        </div>
                        {lead.phone && (
                          <div className="flex items-center gap-2 text-sm text-gray-400">
                            <Phone className="w-4 h-4 text-gray-500" />
                            {lead.phone}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <div className="flex items-center gap-2 text-sm text-gray-300 font-medium">
                        <Building2 className="w-4 h-4 text-gray-500" />
                        {lead.company || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1.5 px-3 py-2 text-xs font-bold rounded-xl border ${getStatusColor(lead.status)}`}>
                        <span className="w-2 h-2 rounded-full bg-current animate-pulse"></span>
                        {lead.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <span className={`text-sm font-bold ${getScoreColor(lead.lead_score)}`}>
                        {lead.lead_score}/100
                      </span>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap text-sm text-white font-semibold">
                      {lead.total_messages_sent}
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => setQuickViewLead(lead)}
                          className="text-[#FF6B35] hover:text-[#F7931E] p-2.5 rounded-xl hover:bg-[#FF6B35]/10 active:scale-95 transition-all duration-200 hover:shadow-lg hover:shadow-[#FF6B35]/20"
                          title="Quick view"
                        >
                          <Eye className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => deleteLead(lead.id)}
                          className="text-red-400 hover:text-red-300 p-2.5 rounded-xl hover:bg-red-500/10 active:scale-95 transition-all duration-200 hover:shadow-lg hover:shadow-red-500/20"
                          title="Delete lead"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* PAGINATION CONTROLS */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t border-white/10 flex items-center justify-between">
              <div className="text-sm text-gray-400">
                Showing {startIndex + 1} to {Math.min(endIndex, filteredLeads.length)} of {filteredLeads.length} leads
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-all"
                >
                  Previous
                </button>
                <div className="flex items-center gap-1">
                  {[...Array(Math.min(5, totalPages))].map((_, i) => {
                    const pageNum = currentPage <= 3 ? i + 1 : currentPage - 2 + i;
                    if (pageNum > totalPages) return null;
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`w-10 h-10 rounded-lg font-semibold transition-all ${
                          currentPage === pageNum
                            ? 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white shadow-lg'
                            : 'bg-white/10 hover:bg-white/20 text-gray-300'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-all"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
        )}

        {/* Stats Footer */}
        {!loading && filteredLeads.length > 0 && (
          <div className="mt-6 flex justify-between items-center text-sm text-gray-600">
            <div>
              Showing {filteredLeads.length} of {leads.length} leads
            </div>
            <div className="flex gap-6">
              <div>
                <span className="font-semibold">{leads.filter(l => l.status === 'new').length}</span> New
              </div>
              <div>
                <span className="font-semibold">{leads.filter(l => l.status === 'contacted').length}</span> Contacted
              </div>
              <div>
                <span className="font-semibold">{leads.filter(l => l.status === 'engaged').length}</span> Engaged
              </div>
              <div>
                <span className="font-semibold">{leads.filter(l => l.status === 'meeting_booked').length}</span> Meetings
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Quick View Modal */}
      {quickViewLead && (
        <LeadQuickView lead={quickViewLead} onClose={() => setQuickViewLead(null)} />
      )}
    </div>
  );
}
