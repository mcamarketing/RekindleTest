import { useState, useEffect } from 'react';
import { Navigation } from '../components/Navigation';
import { Shield, Search, Download, Upload, Trash2, Plus, AlertTriangle, CheckCircle } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface SuppressionEntry {
  id: string;
  email: string;
  reason: string;
  reason_text: string;
  suppressed_at: string;
  suppressed_via: string;
}

export function SuppressionList() {
  const { user } = useAuth();
  const [entries, setEntries] = useState<SuppressionEntry[]>([]);
  const [filteredEntries, setFilteredEntries] = useState<SuppressionEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [newReason, setNewReason] = useState('');
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  useEffect(() => {
    if (user) {
      loadSuppressionList();
    }
  }, [user]);

  useEffect(() => {
    if (searchQuery) {
      setFilteredEntries(
        entries.filter(entry => 
          entry.email.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    } else {
      setFilteredEntries(entries);
    }
  }, [searchQuery, entries]);

  const loadSuppressionList = async () => {
    try {
      const { data, error } = await supabase
        .from('suppression_list')
        .select('*')
        .order('suppressed_at', { ascending: false });

      if (error) {
        console.error('Error loading suppression list:', error);
        setMessage({ type: 'error', text: 'Failed to load suppression list' });
      } else {
        setEntries(data || []);
      }
    } catch (err) {
      console.error('Error:', err);
      setMessage({ type: 'error', text: 'An error occurred' });
    } finally {
      setLoading(false);
    }
  };

  const handleAddEmail = async () => {
    if (!newEmail) {
      setMessage({ type: 'error', text: 'Email address is required' });
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newEmail)) {
      setMessage({ type: 'error', text: 'Invalid email format' });
      return;
    }

    setAdding(true);
    setMessage(null);

    try {
      const { error } = await supabase.rpc('add_to_suppression_list', {
        p_email: newEmail.toLowerCase(),
        p_reason: 'manual',
        p_reason_text: newReason || 'Manually added by admin',
        p_via: 'manual'
      });

      if (error) {
        console.error('Error adding to suppression list:', error);
        setMessage({ type: 'error', text: 'Failed to add email' });
      } else {
        setMessage({ type: 'success', text: `Added ${newEmail} to suppression list` });
        setNewEmail('');
        setNewReason('');
        setShowAddModal(false);
        await loadSuppressionList();
      }
    } catch (err) {
      console.error('Error:', err);
      setMessage({ type: 'error', text: 'An error occurred' });
    } finally {
      setAdding(false);
    }
  };

  const handleRemove = async (id: string, email: string) => {
    if (!confirm(`Remove ${email} from suppression list? They will be able to receive emails again.`)) {
      return;
    }

    try {
      const { error } = await supabase
        .from('suppression_list')
        .delete()
        .eq('id', id);

      if (error) {
        console.error('Error removing from suppression list:', error);
        setMessage({ type: 'error', text: 'Failed to remove email' });
      } else {
        setMessage({ type: 'success', text: `Removed ${email} from suppression list` });
        await loadSuppressionList();
      }
    } catch (err) {
      console.error('Error:', err);
      setMessage({ type: 'error', text: 'An error occurred' });
    }
  };

  const handleExport = () => {
    const csv = [
      ['Email', 'Reason', 'Details', 'Suppressed Date', 'Method'].join(','),
      ...entries.map(entry => [
        entry.email,
        entry.reason,
        entry.reason_text || '',
        new Date(entry.suppressed_at).toLocaleString(),
        entry.suppressed_via
      ].join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `suppression-list-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    const lines = text.split('\n').filter(line => line.trim());
    
    // Skip header
    const emails = lines.slice(1).map(line => {
      const parts = line.split(',');
      return parts[0]?.trim().toLowerCase();
    }).filter(email => email);

    let successCount = 0;
    let errorCount = 0;

    for (const email of emails) {
      try {
        const { error } = await supabase.rpc('add_to_suppression_list', {
          p_email: email,
          p_reason: 'manual',
          p_reason_text: 'Imported from CSV',
          p_via: 'api'
        });

        if (error) {
          errorCount++;
        } else {
          successCount++;
        }
      } catch {
        errorCount++;
      }
    }

    setMessage({ 
      type: successCount > 0 ? 'success' : 'error', 
      text: `Imported ${successCount} emails, ${errorCount} failed` 
    });
    await loadSuppressionList();
  };

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden animate-fade-in">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
      </div>

      <Navigation currentPage="compliance" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-4 bg-gradient-to-br from-red-500 to-red-600 rounded-2xl shadow-lg">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-5xl font-bold text-white">Suppression List</h1>
              <p className="text-xl text-gray-400 mt-2">
                Manage unsubscribed and blocked email addresses
              </p>
            </div>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-xl border-2 flex items-center gap-3 animate-slide-up ${
            message.type === 'success' 
              ? 'bg-green-500/20 border-green-500/30' 
              : 'bg-red-500/20 border-red-500/30'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-400" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-red-400" />
            )}
            <span className={message.type === 'success' ? 'text-green-300' : 'text-red-300'}>
              {message.text}
            </span>
          </div>
        )}

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">Total Suppressed</p>
                <p className="text-3xl font-bold text-white">{entries.length}</p>
              </div>
              <Shield className="w-12 h-12 text-red-400" />
            </div>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">User Requests</p>
                <p className="text-3xl font-bold text-white">
                  {entries.filter(e => e.reason === 'user_request').length}
                </p>
              </div>
              <AlertTriangle className="w-12 h-12 text-yellow-400" />
            </div>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">Bounces/Spam</p>
                <p className="text-3xl font-bold text-white">
                  {entries.filter(e => ['bounce', 'spam_complaint'].includes(e.reason)).length}
                </p>
              </div>
              <Trash2 className="w-12 h-12 text-red-400" />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="glass-card p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FF6B35] focus:border-transparent"
              />
            </div>

            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-semibold rounded-xl hover:shadow-2xl hover:shadow-[#FF6B35]/40 transition-all duration-300"
            >
              <Plus className="w-5 h-5" />
              Add Email
            </button>

            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-6 py-3 bg-white/10 border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300"
            >
              <Download className="w-5 h-5" />
              Export
            </button>

            <label className="flex items-center gap-2 px-6 py-3 bg-white/10 border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300 cursor-pointer">
              <Upload className="w-5 h-5" />
              Import
              <input
                type="file"
                accept=".csv"
                onChange={handleImport}
                className="hidden"
              />
            </label>
          </div>
        </div>

        {/* Table */}
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-white/5 border-b border-white/10">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Reason
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Details
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Method
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-400">
                      Loading...
                    </td>
                  </tr>
                ) : filteredEntries.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-400">
                      No suppressed emails found
                    </td>
                  </tr>
                ) : (
                  filteredEntries.map((entry) => (
                    <tr key={entry.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-white font-medium">
                        {entry.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          entry.reason === 'user_request' ? 'bg-yellow-500/20 text-yellow-300' :
                          entry.reason === 'bounce' ? 'bg-red-500/20 text-red-300' :
                          entry.reason === 'spam_complaint' ? 'bg-red-600/20 text-red-400' :
                          'bg-gray-500/20 text-gray-300'
                        }`}>
                          {entry.reason.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-400 text-sm max-w-xs truncate">
                        {entry.reason_text || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-400 text-sm">
                        {new Date(entry.suppressed_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-400 text-sm">
                        {entry.suppressed_via}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <button
                          onClick={() => handleRemove(entry.id, entry.email)}
                          className="text-red-400 hover:text-red-300 transition-colors"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Add Email Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="glass-card p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold text-white mb-6">Add to Suppression List</h2>
              
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    placeholder="email@example.com"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FF6B35]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    Reason (optional)
                  </label>
                  <input
                    type="text"
                    value={newReason}
                    onChange={(e) => setNewReason(e.target.value)}
                    placeholder="Why is this email being suppressed?"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FF6B35]"
                  />
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleAddEmail}
                  disabled={adding}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-semibold rounded-xl hover:shadow-2xl disabled:opacity-50 transition-all duration-300"
                >
                  {adding ? 'Adding...' : 'Add Email'}
                </button>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-6 py-3 bg-white/10 border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

