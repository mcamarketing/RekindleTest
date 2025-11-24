// @ts-nocheck
import { useState, useEffect } from 'react';
import { Navigation } from '../components/Navigation';
import { RippleButton } from '../components/RippleButton';
import { useToast } from '../components/Toast';
import { supabase } from '../lib/supabase';
import { apiClient } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import {
  Mail, Users, Calendar, Send, ArrowRight, CheckCircle2,
  Sparkles, Wand2, Copy, Check, Loader2
} from 'lucide-react';

interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  company: string | null;
}

interface Message {
  id: string;
  content: string;
  sequenceNumber: number;
}

export function CreateCampaign() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [selectedLeads, setSelectedLeads] = useState<string[]>([]);
  const [showConfetti, setShowConfetti] = useState(false);
  const [generatingMessage, setGeneratingMessage] = useState(false);
  const [messageTone, setMessageTone] = useState<'professional' | 'casual' | 'friendly'>('professional');
  const [generatedMessage, setGeneratedMessage] = useState('');
  const [copiedMessage, setCopiedMessage] = useState(false);

  const [campaignData, setCampaignData] = useState({
    name: '',
    description: '',
    total_messages: 5,
    days_between_messages: 3,
  });

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    try {
      const { data, error } = await supabase
        .from('leads')
        .select('id, first_name, last_name, email, company')
        .in('status', ['new', 'contacted', 'unresponsive'])
        .order('created_at', { ascending: false });

      if (error) throw error;
      setLeads(data || []);
    } catch (error) {
      console.error('Error loading leads:', error);
      showToast({
        type: 'error',
        title: 'Failed to load leads',
        message: 'Please try again',
      });
    }
  };

  const toggleLeadSelection = (leadId: string) => {
    setSelectedLeads(prev =>
      prev.includes(leadId)
        ? prev.filter(id => id !== leadId)
        : [...prev, leadId]
    );
  };

  const selectAllLeads = () => {
    setSelectedLeads(leads.map(l => l.id));
    showToast({
      type: 'success',
      title: 'All leads selected',
      message: `${leads.length} leads added to campaign`,
    });
  };

  const deselectAllLeads = () => {
    setSelectedLeads([]);
  };

  const generateAIMessage = async () => {
    if (selectedLeads.length === 0) {
      showToast({
        type: 'warning',
        title: 'No leads selected',
        message: 'Please select at least one lead first',
      });
      return;
    }

    setGeneratingMessage(true);
    try {
      const firstLead = leads.find(l => l.id === selectedLeads[0]);

      const response = await apiClient.generateMessage({
        leadName: `${firstLead?.first_name} ${firstLead?.last_name}`,
        company: firstLead?.company || undefined,
        tone: messageTone,
        context: campaignData.description,
      });

      if (response.success && response.data) {
        setGeneratedMessage(response.data.message || 'Hey there! Just wanted to reach out and see if you\'re interested in reconnecting...');
        showToast({
          type: 'success',
          title: 'Message generated',
          message: 'AI created a personalized message for your campaign',
        });
      } else {
        throw new Error(response.error);
      }
    } catch (error: any) {
      setGeneratedMessage('Hey there! Just wanted to reach out and see if you\'re interested in reconnecting. Would love to catch up and discuss how we can help your business grow.');
      showToast({
        type: 'info',
        title: 'Using default message',
        message: 'Backend unavailable - showing example message',
      });
    } finally {
      setGeneratingMessage(false);
    }
  };

  const copyMessage = () => {
    navigator.clipboard.writeText(generatedMessage);
    setCopiedMessage(true);
    showToast({
      type: 'success',
      title: 'Copied to clipboard',
    });
    setTimeout(() => setCopiedMessage(false), 2000);
  };

  const handleCreateCampaign = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const { data: campaign, error: campaignError } = await supabase
        .from('campaigns')
        .insert({
          ...campaignData,
          user_id: user.id,
          status: 'draft',
          total_leads: selectedLeads.length,
        })
        .select()
        .single();

      if (campaignError) throw campaignError;

      const campaignLeads = selectedLeads.map(leadId => ({
        campaign_id: campaign.id,
        lead_id: leadId,
        status: 'pending',
      }));

      const { error: leadsError } = await supabase
        .from('campaign_leads')
        .insert(campaignLeads);

      if (leadsError) throw leadsError;

      setShowConfetti(true);
      showToast({
        type: 'success',
        title: 'Campaign created successfully!',
        message: `Your campaign "${campaignData.name}" is ready to launch`,
      });

      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (error: any) {
      console.error('Error creating campaign:', error);
      showToast({
        type: 'error',
        title: 'Failed to create campaign',
        message: error.message || 'Please try again',
      });
    } finally {
      setLoading(false);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return campaignData.name.trim().length > 0;
      case 2:
        return selectedLeads.length > 0;
      case 3:
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-purple-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '3s' }} />
        <div className="absolute bottom-0 left-1/2 w-[700px] h-[700px] bg-pink-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '6s' }} />
      </div>

      <Navigation currentPage="campaigns" />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <div className="mb-10 animate-fade-in">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-[#FF6B35] hover:text-[#F7931E] mb-4 inline-flex items-center gap-2 transition-colors font-semibold hover:gap-3 transition-all"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-white mb-2">Create Campaign</h1>
          <p className="text-gray-400 text-lg">
            Set up a new lead revival campaign
          </p>
        </div>

        <div className="glass-card p-8 mb-10 animate-fade-in">
          <div className="flex items-center justify-between">
            {[
              { num: 1, title: 'Campaign Details', icon: Mail },
              { num: 2, title: 'Select Leads', icon: Users },
              { num: 3, title: 'Review & Launch', icon: Send },
            ].map((s, idx) => (
              <div key={s.num} className="flex items-center">
                <div className="flex flex-col items-center">
                  <div
                    className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-300 ${
                      step >= s.num
                        ? 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white shadow-2xl shadow-[#FF6B35]/40 scale-110'
                        : 'bg-white/5 text-gray-500 border-2 border-white/10'
                    }`}
                  >
                    {step > s.num ? (
                      <CheckCircle2 className="w-8 h-8" />
                    ) : (
                      <s.icon className="w-7 h-7" />
                    )}
                  </div>
                  <span className={`text-sm font-bold mt-3 transition-colors ${
                    step >= s.num ? 'text-[#FF6B35]' : 'text-gray-500'
                  }`}>
                    {s.title}
                  </span>
                </div>
                {idx < 2 && (
                  <div
                    className={`w-24 h-1.5 mx-6 rounded-full transition-all duration-500 ${
                      step > s.num ? 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E]' : 'bg-white/10'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        <div key={step} className="glass-card p-10 mb-6 animate-slide-in">
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-8">Campaign Details</h2>

              <div className="space-y-8">
                <div>
                  <label className="block text-sm font-bold text-gray-300 mb-3">
                    Campaign Name *
                  </label>
                  <input
                    type="text"
                    value={campaignData.name}
                    onChange={(e) => setCampaignData({ ...campaignData, name: e.target.value })}
                    placeholder="e.g., Q1 Lead Revival"
                    className="w-full px-5 py-4 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-xl focus:ring-2 focus:ring-[#FF6B35] focus:border-transparent transition-all font-medium"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-gray-300 mb-3">
                    Description
                  </label>
                  <textarea
                    value={campaignData.description}
                    onChange={(e) => setCampaignData({ ...campaignData, description: e.target.value })}
                    placeholder="Optional campaign description"
                    rows={4}
                    className="w-full px-5 py-4 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-xl focus:ring-2 focus:ring-[#FF6B35] focus:border-transparent transition-all font-medium resize-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-bold text-gray-300 mb-3">
                      Total Messages
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={campaignData.total_messages}
                      onChange={(e) => setCampaignData({ ...campaignData, total_messages: parseInt(e.target.value) || 1 })}
                      className="w-full px-5 py-4 bg-white/5 border border-white/10 text-white rounded-xl focus:ring-2 focus:ring-[#FF6B35] focus:border-transparent font-bold text-center"
                    />
                    <p className="text-xs text-gray-500 mt-2">Number of follow-up messages (1-10)</p>
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-gray-300 mb-3">
                      Days Between Messages
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="14"
                      value={campaignData.days_between_messages}
                      onChange={(e) => setCampaignData({ ...campaignData, days_between_messages: parseInt(e.target.value) || 1 })}
                      className="w-full px-5 py-4 bg-white/5 border border-white/10 text-white rounded-xl focus:ring-2 focus:ring-[#FF6B35] focus:border-transparent font-bold text-center"
                    />
                    <p className="text-xs text-gray-500 mt-2">Delay between each message (1-14 days)</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-white">Select Leads</h2>
                  <p className="text-sm text-gray-400 mt-2">
                    Choose which leads to include in this campaign
                  </p>
                </div>
                <div className="flex gap-3">
                  <RippleButton
                    variant="outline"
                    size="sm"
                    onClick={selectAllLeads}
                    className="border-white/20 text-white hover:bg-white/10"
                  >
                    Select All
                  </RippleButton>
                  <RippleButton
                    variant="secondary"
                    size="sm"
                    onClick={deselectAllLeads}
                    className="bg-white/5 text-white hover:bg-white/10"
                  >
                    Deselect All
                  </RippleButton>
                </div>
              </div>

              <div className="mb-6 p-5 bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-2xl backdrop-blur-sm">
                <p className="text-sm text-blue-300 font-bold">
                  <strong className="text-2xl text-white">{selectedLeads.length}</strong> leads selected
                </p>
              </div>

              <div className="max-h-96 overflow-y-auto border border-white/10 rounded-2xl bg-white/5">
                {leads.map((lead, idx) => (
                  <div
                    key={lead.id}
                    onClick={() => toggleLeadSelection(lead.id)}
                    className={`p-5 flex items-center gap-4 cursor-pointer hover:bg-white/10 border-b border-white/5 last:border-0 transition-all duration-200 ${
                      selectedLeads.includes(lead.id) ? 'bg-[#FF6B35]/20 border-[#FF6B35]/30' : ''
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedLeads.includes(lead.id)}
                      onChange={() => {}}
                      className="w-5 h-5 text-[#FF6B35] rounded bg-white/5 border-white/20"
                    />
                    <div className="flex-1">
                      <div className="font-bold text-white">
                        {lead.first_name} {lead.last_name}
                      </div>
                      <div className="text-sm text-gray-400">{lead.email}</div>
                    </div>
                    {lead.company && (
                      <div className="text-sm text-gray-300 font-medium">{lead.company}</div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-8 p-8 bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-purple-500/20 rounded-2xl border border-purple-500/30 relative overflow-hidden">
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-pink-600/10 animate-gradient" />

                <div className="flex items-start gap-6 relative z-10">
                  <div className="p-4 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl shadow-2xl">
                    <Sparkles className="w-10 h-10 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-black text-white mb-3 text-xl">AI Message Generator</h3>
                    <p className="text-sm text-gray-300 mb-6">
                      Let AI create personalized messages for your campaign
                    </p>

                    <div className="flex gap-3 mb-6">
                      {(['professional', 'casual', 'friendly'] as const).map((tone) => (
                        <button
                          key={tone}
                          onClick={() => setMessageTone(tone)}
                          className={`px-6 py-3 rounded-xl text-sm font-bold transition-all duration-300 ${
                            messageTone === tone
                              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-2xl shadow-purple-500/40 scale-110'
                              : 'bg-white/10 text-gray-300 hover:bg-white/20 hover:text-white'
                          }`}
                        >
                          {tone.charAt(0).toUpperCase() + tone.slice(1)}
                        </button>
                      ))}
                    </div>

                    <RippleButton
                      variant="primary"
                      size="sm"
                      onClick={generateAIMessage}
                      disabled={generatingMessage || selectedLeads.length === 0}
                      className="bg-gradient-to-r from-purple-600 to-pink-600 hover:shadow-2xl hover:shadow-purple-500/40"
                    >
                      {generatingMessage ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Wand2 className="w-5 h-5" />
                          Generate Message
                        </>
                      )}
                    </RippleButton>

                    {generatedMessage && (
                      <div className="mt-6 p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 animate-fade-in">
                        <div className="flex justify-between items-start mb-3">
                          <p className="text-sm font-bold text-gray-300">Generated Message:</p>
                          <button
                            onClick={copyMessage}
                            className="text-purple-400 hover:text-purple-300 transition-colors p-2 hover:bg-white/10 rounded-lg"
                          >
                            {copiedMessage ? (
                              <Check className="w-5 h-5" />
                            ) : (
                              <Copy className="w-5 h-5" />
                            )}
                          </button>
                        </div>
                        <p className="text-sm text-white italic font-medium leading-relaxed">{generatedMessage}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-8">Review & Launch</h2>

              <div className="space-y-8">
                <div className="bg-white/5 border border-white/10 rounded-2xl p-8 space-y-6 backdrop-blur-sm">
                  <div>
                    <p className="text-sm font-bold text-gray-400 mb-2">Campaign Name</p>
                    <p className="text-2xl font-bold text-white">{campaignData.name}</p>
                  </div>

                  {campaignData.description && (
                    <div>
                      <p className="text-sm font-bold text-gray-400 mb-2">Description</p>
                      <p className="text-white font-medium">{campaignData.description}</p>
                    </div>
                  )}

                  <div className="grid grid-cols-3 gap-6 pt-6 border-t border-white/10">
                    <div className="text-center hover:scale-110 transition-transform glass-morphism p-6 rounded-2xl">
                      <p className="text-sm font-bold text-gray-400 mb-2">Leads</p>
                      <p className="text-4xl font-black text-[#FF6B35]">{selectedLeads.length}</p>
                    </div>
                    <div className="text-center hover:scale-110 transition-transform glass-morphism p-6 rounded-2xl">
                      <p className="text-sm font-bold text-gray-400 mb-2">Messages</p>
                      <p className="text-4xl font-black text-[#FF6B35]">{campaignData.total_messages}</p>
                    </div>
                    <div className="text-center hover:scale-110 transition-transform glass-morphism p-6 rounded-2xl">
                      <p className="text-sm font-bold text-gray-400 mb-2">Frequency</p>
                      <p className="text-4xl font-black text-[#FF6B35]">{campaignData.days_between_messages}d</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-2xl p-6 backdrop-blur-sm">
                  <p className="text-sm text-yellow-300 font-medium">
                    <strong className="text-white font-bold">Note:</strong> Your campaign will be created as a draft. You can review and activate it from your dashboard.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-between">
          <RippleButton
            variant="secondary"
            onClick={() => step > 1 ? setStep(step - 1) : navigate('/dashboard')}
            disabled={loading}
            className="bg-white/5 text-white hover:bg-white/10 border border-white/10"
          >
            {step === 1 ? 'Cancel' : 'Back'}
          </RippleButton>

          {step < 3 ? (
            <RippleButton
              variant="primary"
              onClick={() => setStep(step + 1)}
              disabled={!canProceed() || loading}
              className="bg-gradient-to-r from-[#FF6B35] to-[#F7931E] hover:shadow-2xl hover:shadow-[#FF6B35]/40"
            >
              Next
              <ArrowRight className="w-5 h-5" />
            </RippleButton>
          ) : (
            <RippleButton
              variant="primary"
              onClick={handleCreateCampaign}
              disabled={loading}
              className="bg-gradient-to-r from-[#FF6B35] to-[#F7931E] hover:shadow-2xl hover:shadow-[#FF6B35]/40"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Create Campaign
                </>
              )}
            </RippleButton>
          )}
        </div>
      </main>
    </div>
  );
}
