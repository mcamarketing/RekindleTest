import { useState, useEffect } from 'react';
import { Mail, CheckCircle2, XCircle, Loader2, ArrowLeft } from 'lucide-react';
import { supabase } from '../lib/supabase';

export function Unsubscribe() {
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');

  useEffect(() => {
    // Get token and email from URL params
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    const urlEmail = params.get('email');

    if (urlToken) {
      setToken(urlToken);
      verifyToken(urlToken);
    } else if (urlEmail) {
      setEmail(urlEmail);
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (tokenToVerify: string) => {
    try {
      const { data, error: fetchError } = await supabase
        .from('unsubscribe_tokens')
        .select('email, used, expires_at')
        .eq('token', tokenToVerify)
        .single();

      if (fetchError || !data) {
        setError('Invalid or expired unsubscribe link.');
        setLoading(false);
        return;
      }

      if (data.used) {
        setError('This unsubscribe link has already been used.');
        setLoading(false);
        return;
      }

      if (new Date(data.expires_at) < new Date()) {
        setError('This unsubscribe link has expired.');
        setLoading(false);
        return;
      }

      setEmail(data.email);
      setLoading(false);
    } catch (err) {
      console.error('Error verifying token:', err);
      setError('An error occurred. Please try again.');
      setLoading(false);
    }
  };

  const handleUnsubscribe = async () => {
    if (!email) {
      setError('Email address is required.');
      return;
    }

    setProcessing(true);
    setError('');

    try {
      // Call the stored procedure to add to suppression list
      const { error: suppressionError } = await supabase.rpc('add_to_suppression_list', {
        p_email: email.toLowerCase(),
        p_reason: 'user_request',
        p_reason_text: 'User clicked unsubscribe link',
        p_via: 'unsubscribe_link'
      });

      if (suppressionError) {
        console.error('Suppression error:', suppressionError);
        setError('Failed to unsubscribe. Please try again or contact support.');
        setProcessing(false);
        return;
      }

      // Mark token as used if we have one
      if (token) {
        await supabase
          .from('unsubscribe_tokens')
          .update({
            used: true,
            used_at: new Date().toISOString()
          })
          .eq('token', token);
      }

      // Record consent withdrawal
      await supabase.rpc('record_consent', {
        p_email: email.toLowerCase(),
        p_consent_type: 'email_marketing',
        p_consent_given: false,
        p_method: 'unsubscribe_link'
      });

      setSuccess(true);
    } catch (err) {
      console.error('Error unsubscribing:', err);
      setError('An error occurred. Please try again.');
    } finally {
      setProcessing(false);
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
          <p className="text-white text-lg">Verifying your request...</p>
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

      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 text-[#FF6B35] hover:text-[#F7931E] mb-8 transition-all duration-200 font-semibold hover:gap-3"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </button>

        <div className="glass-card p-8 md:p-12">
          {success ? (
            <div className="text-center">
              <div className="inline-flex p-6 bg-green-500/20 rounded-full mb-6">
                <CheckCircle2 className="w-16 h-16 text-green-400" />
              </div>
              <h1 className="text-3xl font-bold text-white mb-4">
                You've Been Unsubscribed
              </h1>
              <p className="text-gray-300 text-lg mb-6">
                We've removed <strong className="text-white">{email}</strong> from our mailing list.
                You won't receive any more marketing emails from us.
              </p>
              <p className="text-gray-400 text-sm mb-8">
                Note: You may still receive transactional emails related to your account or purchases.
              </p>
              <div className="space-y-4">
                <button
                  onClick={() => navigate('/preferences?email=' + encodeURIComponent(email))}
                  className="w-full px-6 py-3 bg-white/10 border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300"
                >
                  Manage Email Preferences
                </button>
                <button
                  onClick={() => navigate('/')}
                  className="w-full px-6 py-3 text-gray-400 hover:text-white font-semibold transition-colors"
                >
                  Return to Homepage
                </button>
              </div>
            </div>
          ) : error ? (
            <div className="text-center">
              <div className="inline-flex p-6 bg-red-500/20 rounded-full mb-6">
                <XCircle className="w-16 h-16 text-red-400" />
              </div>
              <h1 className="text-3xl font-bold text-white mb-4">
                Oops! Something Went Wrong
              </h1>
              <p className="text-gray-300 text-lg mb-8">
                {error}
              </p>
              <p className="text-gray-400 text-sm mb-8">
                If you continue to have issues, please contact us at{' '}
                <a href="mailto:support@rekindle.ai" className="text-[#FF6B35] hover:text-[#F7931E]">
                  support@rekindle.ai
                </a>
              </p>
              <button
                onClick={() => navigate('/')}
                className="px-6 py-3 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-semibold rounded-xl hover:shadow-2xl hover:shadow-[#FF6B35]/40 transition-all duration-300"
              >
                Return to Homepage
              </button>
            </div>
          ) : (
            <div>
              <div className="text-center mb-8">
                <div className="inline-flex p-6 bg-[#FF6B35]/20 rounded-full mb-6">
                  <Mail className="w-16 h-16 text-[#FF6B35]" />
                </div>
                <h1 className="text-3xl font-bold text-white mb-4">
                  Unsubscribe from Emails
                </h1>
                <p className="text-gray-300 text-lg">
                  We're sorry to see you go. Click below to unsubscribe from all marketing emails.
                </p>
              </div>

              <div className="mb-8 p-6 bg-white/5 border border-white/10 rounded-xl">
                <p className="text-sm text-gray-400 mb-2">Email Address:</p>
                <p className="text-white text-lg font-semibold">{email}</p>
              </div>

              <div className="space-y-4">
                <button
                  onClick={handleUnsubscribe}
                  disabled={processing}
                  className="w-full px-6 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white font-bold text-lg rounded-xl hover:shadow-2xl hover:shadow-red-500/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                >
                  {processing ? (
                    <span className="flex items-center justify-center gap-3">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Unsubscribing...
                    </span>
                  ) : (
                    'Unsubscribe from All Emails'
                  )}
                </button>

                <button
                  onClick={() => navigate('/preferences?email=' + encodeURIComponent(email))}
                  className="w-full px-6 py-3 bg-white/10 border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300"
                >
                  Just Update My Preferences Instead
                </button>
              </div>

              <div className="mt-8 p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                <p className="text-sm text-blue-300">
                  <strong>Changed your mind?</strong> You can always re-subscribe by signing up again or 
                  updating your preferences.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Why we're sorry section */}
        {!success && !error && (
          <div className="mt-8 glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">Before you go...</h3>
            <p className="text-gray-300 mb-4">
              We'd love to keep in touch! Instead of unsubscribing completely, you can:
            </p>
            <ul className="space-y-2 text-gray-400">
              <li className="flex items-start gap-2">
                <span className="text-[#FF6B35]">•</span>
                <span>Reduce email frequency to weekly or monthly digests</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#FF6B35]">•</span>
                <span>Choose only the types of emails you want to receive</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#FF6B35]">•</span>
                <span>Pause emails temporarily without unsubscribing</span>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

