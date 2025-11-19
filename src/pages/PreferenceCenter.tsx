import { useState, useEffect } from 'react';
import { Settings, CheckCircle2, Loader2, ArrowLeft, Mail, MessageSquare, Bell } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface EmailPreferences {
  marketing_emails: boolean;
  transactional_emails: boolean;
  product_updates: boolean;
  newsletter: boolean;
  promotional_emails: boolean;
  frequency: 'realtime' | 'daily' | 'weekly' | 'monthly' | 'never';
  sms_enabled: boolean;
  phone_enabled: boolean;
}

export function PreferenceCenter() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [preferences, setPreferences] = useState<EmailPreferences>({
    marketing_emails: true,
    transactional_emails: true,
    product_updates: true,
    newsletter: true,
    promotional_emails: true,
    frequency: 'normal' as any,
    sms_enabled: false,
    phone_enabled: false
  });

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlEmail = params.get('email');
    const urlToken = params.get('token');

    if (urlEmail) {
      setEmail(urlEmail);
      loadPreferences(urlEmail);
    } else if (urlToken) {
      loadPreferencesByToken(urlToken);
    } else {
      setError('Email address or token is required.');
      setLoading(false);
    }
  }, []);

  const loadPreferences = async (emailToLoad: string) => {
    try {
      const { data, error: fetchError } = await supabase
        .from('email_preferences')
        .select('*')
        .eq('email', emailToLoad.toLowerCase())
        .single();

      if (fetchError) {
        // Create default preferences if they don't exist
        if (fetchError.code === 'PGRST116') {
          await createDefaultPreferences(emailToLoad);
        } else {
          console.error('Error loading preferences:', fetchError);
        }
      } else if (data) {
        setPreferences({
          marketing_emails: data.marketing_emails,
          transactional_emails: data.transactional_emails,
          product_updates: data.product_updates,
          newsletter: data.newsletter,
          promotional_emails: data.promotional_emails,
          frequency: data.frequency,
          sms_enabled: data.sms_enabled,
          phone_enabled: data.phone_enabled
        });
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to load preferences.');
    } finally {
      setLoading(false);
    }
  };

  const loadPreferencesByToken = async (token: string) => {
    try {
      const { data, error: fetchError } = await supabase
        .from('email_preferences')
        .select('*')
        .eq('preference_token', token)
        .single();

      if (fetchError || !data) {
        setError('Invalid preference link.');
        setLoading(false);
        return;
      }

      setEmail(data.email);
      setPreferences({
        marketing_emails: data.marketing_emails,
        transactional_emails: data.transactional_emails,
        product_updates: data.product_updates,
        newsletter: data.newsletter,
        promotional_emails: data.promotional_emails,
        frequency: data.frequency,
        sms_enabled: data.sms_enabled,
        phone_enabled: data.phone_enabled
      });
      setLoading(false);
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to load preferences.');
      setLoading(false);
    }
  };

  const createDefaultPreferences = async (emailToCreate: string) => {
    const { error: insertError } = await supabase
      .from('email_preferences')
      .insert({
        email: emailToCreate.toLowerCase(),
        ...preferences
      });

    if (insertError) {
      console.error('Error creating preferences:', insertError);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess(false);

    try {
      const { error: updateError } = await supabase
        .from('email_preferences')
        .upsert({
          email: email.toLowerCase(),
          ...preferences,
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'email'
        });

      if (updateError) {
        console.error('Error saving preferences:', updateError);
        setError('Failed to save preferences. Please try again.');
        setSaving(false);
        return;
      }

      // Record consent changes
      await supabase.rpc('record_consent', {
        p_email: email.toLowerCase(),
        p_consent_type: 'email_marketing',
        p_consent_given: preferences.marketing_emails,
        p_method: 'preference_center'
      });

      setSuccess(true);
      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      console.error('Error:', err);
      setError('An error occurred. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#1A1F2E] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-[#FF6B35] animate-spin mx-auto mb-4" />
          <p className="text-white text-lg">Loading your preferences...</p>
        </div>
      </div>
    );
  }

  if (error && !email) {
    return (
      <div className="min-h-screen bg-[#1A1F2E] flex items-center justify-center p-4">
        <div className="glass-card p-8 max-w-md text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-semibold rounded-xl hover:shadow-2xl transition-all duration-300"
          >
            Return to Homepage
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 text-[#FF6B35] hover:text-[#F7931E] mb-8 transition-all duration-200 font-semibold hover:gap-3"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </button>

        <div className="glass-card p-8 md:p-12">
          <div className="flex items-center gap-4 mb-8">
            <div className="p-4 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-2xl">
              <Settings className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Email Preferences</h1>
              <p className="text-gray-400">{email}</p>
            </div>
          </div>

          {success && (
            <div className="mb-6 p-4 bg-green-500/20 border border-green-500/30 rounded-xl flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-400" />
              <span className="text-green-300 font-semibold">Preferences saved successfully!</span>
            </div>
          )}

          {error && (
            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-xl">
              <span className="text-red-300">{error}</span>
            </div>
          )}

          {/* Email Types */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Mail className="w-5 h-5 text-[#FF6B35]" />
              <h2 className="text-xl font-bold text-white">Email Types</h2>
            </div>
            <div className="space-y-4">
              <label className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors cursor-pointer">
                <div>
                  <div className="text-white font-semibold">Marketing Emails</div>
                  <div className="text-sm text-gray-400">Product news, tips, and special offers</div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.marketing_emails}
                  onChange={(e) => setPreferences({ ...preferences, marketing_emails: e.target.checked })}
                  className="w-5 h-5 text-[#FF6B35] focus:ring-[#FF6B35] rounded"
                />
              </label>

              <label className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors cursor-pointer">
                <div>
                  <div className="text-white font-semibold">Product Updates</div>
                  <div className="text-sm text-gray-400">New features and improvements</div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.product_updates}
                  onChange={(e) => setPreferences({ ...preferences, product_updates: e.target.checked })}
                  className="w-5 h-5 text-[#FF6B35] focus:ring-[#FF6B35] rounded"
                />
              </label>

              <label className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors cursor-pointer">
                <div>
                  <div className="text-white font-semibold">Newsletter</div>
                  <div className="text-sm text-gray-400">Monthly digest and insights</div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.newsletter}
                  onChange={(e) => setPreferences({ ...preferences, newsletter: e.target.checked })}
                  className="w-5 h-5 text-[#FF6B35] focus:ring-[#FF6B35] rounded"
                />
              </label>

              <label className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors cursor-pointer">
                <div>
                  <div className="text-white font-semibold">Promotional Emails</div>
                  <div className="text-sm text-gray-400">Discounts and limited-time offers</div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.promotional_emails}
                  onChange={(e) => setPreferences({ ...preferences, promotional_emails: e.target.checked })}
                  className="w-5 h-5 text-[#FF6B35] focus:ring-[#FF6B35] rounded"
                />
              </label>

              <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <Bell className="w-4 h-4 text-blue-400" />
                  <div className="text-white font-semibold text-sm">Transactional Emails</div>
                </div>
                <div className="text-xs text-gray-400">
                  Account notifications, receipts, and important service updates (cannot be disabled)
                </div>
              </div>
            </div>
          </div>

          {/* Frequency */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <MessageSquare className="w-5 h-5 text-[#FF6B35]" />
              <h2 className="text-xl font-bold text-white">Email Frequency</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { value: 'realtime', label: 'Real-time' },
                { value: 'daily', label: 'Daily' },
                { value: 'weekly', label: 'Weekly' },
                { value: 'monthly', label: 'Monthly' }
              ].map((freq) => (
                <label
                  key={freq.value}
                  className={`p-4 border-2 rounded-xl text-center cursor-pointer transition-all duration-300 ${
                    preferences.frequency === freq.value
                      ? 'border-[#FF6B35] bg-[#FF6B35]/20 text-white'
                      : 'border-white/10 bg-white/5 text-gray-400 hover:border-white/30'
                  }`}
                >
                  <input
                    type="radio"
                    name="frequency"
                    value={freq.value}
                    checked={preferences.frequency === freq.value}
                    onChange={(e) => setPreferences({ ...preferences, frequency: e.target.value as any })}
                    className="hidden"
                  />
                  <div className="font-semibold">{freq.label}</div>
                </label>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 px-6 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold text-lg rounded-xl hover:shadow-2xl hover:shadow-[#FF6B35]/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
            >
              {saving ? (
                <span className="flex items-center justify-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Saving...
                </span>
              ) : (
                'Save Preferences'
              )}
            </button>
            <button
              onClick={() => navigate('/unsubscribe?email=' + encodeURIComponent(email))}
              className="px-6 py-4 bg-white/10 border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300"
            >
              Unsubscribe from All
            </button>
          </div>

          {/* Privacy Note */}
          <div className="mt-8 p-4 bg-white/5 border border-white/10 rounded-xl">
            <p className="text-sm text-gray-400">
              <strong className="text-white">Privacy Note:</strong> Your preferences are stored securely and used only to 
              customize your email experience. We never sell or share your information with third parties. 
              Learn more in our{' '}
              <button onClick={() => navigate('/privacy')} className="text-[#FF6B35] hover:text-[#F7931E] underline">
                Privacy Policy
              </button>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

