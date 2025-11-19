import { useState } from 'react';
import { ArrowLeft, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { CustomSelect } from '../components/CustomSelect';

export function PilotApplication() {
  const [formData, setFormData] = useState({
    // Company Info
    companyName: '',
    companyWebsite: '',
    companySize: '',
    industry: '',
    
    // Contact Info
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: '',
    
    // Qualification
    averageDealValue: '',
    dormantLeadsCount: '',
    currentCRM: '',
    primaryChallenge: '',
    
    // Commitment
    agreedTo30Days: false,
    agreedToPerformanceFee: false,
  });

  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    // Validation
    if (!formData.agreedTo30Days || !formData.agreedToPerformanceFee) {
      setError('Please agree to both pilot terms to continue');
      setIsSubmitting(false);
      return;
    }

    // Insert into Supabase pilot_applications table
    try {
      const { error: insertError } = await supabase
        .from('pilot_applications')
        .insert([{
          company_name: formData.companyName,
          company_website: formData.companyWebsite,
          company_size: formData.companySize,
          industry: formData.industry,
          first_name: formData.firstName,
          last_name: formData.lastName,
          email: formData.email,
          phone: formData.phone,
          role: formData.role,
          average_deal_value: formData.averageDealValue,
          dormant_leads_count: formData.dormantLeadsCount,
          current_crm: formData.currentCRM,
          primary_challenge: formData.primaryChallenge,
              agreed_to_30_days: formData.agreedTo30Days,
          agreed_to_performance_fee: formData.agreedToPerformanceFee,
          status: 'pending'
        }]);

      if (insertError) {
        throw insertError;
      }
      
      setSubmitted(true);
    } catch (err: any) {
      console.error('Pilot application error:', err);
      if (err?.code === '23505') {
        // Unique constraint violation (duplicate email)
        setError('This email has already been used for a pilot application. Please use a different email or contact us at pilot@rekindle.ai');
      } else {
        setError('Something went wrong. Please try again or email us at pilot@rekindle.ai');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-[#1A1F2E] flex items-center justify-center px-4">
        <div className="max-w-2xl w-full glass-card p-12 text-center border-2 border-green-500/30">
          <div className="w-20 h-20 rounded-full bg-green-500/20 border-2 border-green-500/40 flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-400" />
          </div>
          
          <h1 className="text-4xl font-bold text-white mb-4">
            Application Received!
          </h1>
          
          <p className="text-xl text-gray-300 mb-8 leading-relaxed">
            Thank you for applying to the Rekindle.ai Pilot Program. We review applications within 24 hours.
          </p>
          
          <div className="glass-card rounded-2xl p-6 border border-white/10 mb-8">
            <h3 className="text-white font-semibold mb-4">What Happens Next:</h3>
            <div className="text-left space-y-3 text-gray-300 text-sm">
              <div className="flex items-start gap-3">
                <span className="text-orange-400 font-bold">1.</span>
                <span>Our team reviews your application (within 24 hours)</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-orange-400 font-bold">2.</span>
                <span>If approved, you receive onboarding email with setup instructions</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-orange-400 font-bold">3.</span>
                <span>First 30 days: Performance fee only (zero platform fee until you see results)</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-orange-400 font-bold">4.</span>
                <span>We revive your leads, book meetings, and prove ROI</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/')}
              className="px-8 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold text-lg rounded-xl hover:scale-105 transition-all"
            >
              Return to Home
            </button>
            <button
              onClick={() => navigate('/blog')}
              className="px-8 py-4 bg-white/10 border-2 border-white/20 text-white font-bold text-lg rounded-xl hover:bg-white/20 transition-all"
            >
              Read Our Blog
            </button>
          </div>

          <p className="mt-8 text-sm text-gray-500">
            Questions? Email us at <a href="mailto:pilot@rekindle.ai" className="text-[#FF6B35] hover:text-[#F7931E]">pilot@rekindle.ai</a>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Background gradients */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-orange-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
      </div>

      <div className="max-w-4xl mx-auto px-4 py-12 relative z-10">
        {/* Back button */}
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 text-[#FF6B35] hover:text-[#F7931E] mb-8 transition-all font-semibold hover:gap-3"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </button>

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 px-6 py-3 glass-card rounded-full mb-6 border-2 border-orange-500/40">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-orange-500"></span>
            </span>
            <span className="text-sm text-white font-bold">🎯 EXCLUSIVE PILOT PROGRAM</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            <span className="text-gradient">Claim Your Spot:</span> Lock In 50% Off <span className="text-white">Forever</span>
          </h1>

          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-4 leading-relaxed">
            <span className="text-white font-bold">Only 47 pilot spots left.</span> First 30 days: <span className="text-green-400 font-bold">zero platform fee</span>, pay <span className="text-orange-400 font-bold">only 2.5% ACV per booked meeting</span>. <span className="text-red-400 font-bold">No meetings = £0.</span> After pilot: <span className="text-white font-bold">50% off forever</span>. <span className="text-emerald-400 font-semibold">Guarantee: 5+ meetings in 30 days or £500 cash penalty.</span>
          </p>

          <p className="text-sm text-gray-500">
            Applications reviewed within 24 hours. Solopreneurs to enterprise teams welcome.
          </p>
        </div>

        {/* Application Form */}
        <form onSubmit={handleSubmit} className="glass-card p-10 border-2 border-white/10">
          {error && (
            <div className="mb-8 p-4 bg-red-500/10 border-2 border-red-500/30 rounded-xl flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          {/* Company Information */}
          <div className="mb-10">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-orange-400 font-black text-sm">
                1
              </span>
              Company Information
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-white font-semibold mb-2 text-sm">Company Name *</label>
                <input
                  type="text"
                  name="companyName"
                  value={formData.companyName}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-orange-500/50 focus:outline-none transition-all"
                  placeholder="Acme Corp"
                />
              </div>

              <div>
                <label className="block text-white font-semibold mb-2 text-sm">Company Website *</label>
                <input
                  type="url"
                  name="companyWebsite"
                  value={formData.companyWebsite}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-orange-500/50 focus:outline-none transition-all"
                  placeholder="https://acmecorp.com"
                />
              </div>

              <div>
                <label className="block text-white font-semibold mb-2 text-sm">Company Size *</label>
                <CustomSelect
                  name="companySize"
                  value={formData.companySize}
                  onChange={(value) => setFormData({ ...formData, companySize: value })}
                  placeholder="Select size"
                  required
                  options={[
                    { value: '1', label: 'Just me (Solopreneur)' },
                    { value: '2-10', label: '2-10 employees' },
                    { value: '11-50', label: '11-50 employees' },
                    { value: '51-200', label: '51-200 employees' },
                    { value: '201-1000', label: '201-1,000 employees' },
                    { value: '1000+', label: '1,000+ employees' },
                  ]}
                />
              </div>

              <div>
                <label className="block text-white font-semibold mb-2 text-sm">Industry *</label>
                <CustomSelect
                  name="industry"
                  value={formData.industry}
                  onChange={(value) => setFormData({ ...formData, industry: value })}
                  placeholder="Select industry"
                  required
                  options={[
                    { value: 'B2B SaaS', label: 'B2B SaaS' },
                    { value: 'B2B Services', label: 'B2B Services' },
                    { value: 'Consulting', label: 'Consulting' },
                    { value: 'Agency', label: 'Agency (Marketing, Design, Dev)' },
                    { value: 'Professional Services', label: 'Professional Services' },
                    { value: 'Other B2B', label: 'Other B2B' },
                  ]}
                />
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="mb-10">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-orange-400 font-black text-sm">
                2
              </span>
              Your Information
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-white font-semibold mb-2 text-sm">First Name *</label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-orange-500/50 focus:outline-none transition-all"
                  placeholder="John"
                />
              </div>

              <div>
                <label className="block text-white font-semibold mb-2 text-sm">Last Name *</label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-orange-500/50 focus:outline-none transition-all"
                  placeholder="Smith"
                />
              </div>

              <div>
                <label className="block text-white font-semibold mb-2 text-sm">Work Email *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-orange-500/50 focus:outline-none transition-all"
                  placeholder="john@acmecorp.com"
                />
              </div>

              <div>
                <label className="block text-white font-semibold mb-2 text-sm">Phone Number *</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-orange-500/50 focus:outline-none transition-all"
                  placeholder="+44 7700 900000"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-white font-semibold mb-2 text-sm">Your Role *</label>
                <CustomSelect
                  name="role"
                  value={formData.role}
                  onChange={(value) => setFormData({ ...formData, role: value })}
                  placeholder="Select your role"
                  required
                  options={[
                    { value: 'Founder / CEO', label: 'Founder / CEO' },
                    { value: 'VP Sales / CRO', label: 'VP Sales / CRO' },
                    { value: 'Head of Sales', label: 'Head of Sales' },
                    { value: 'Sales Manager', label: 'Sales Manager' },
                    { value: 'RevOps / Sales Ops', label: 'RevOps / Sales Ops' },
                    { value: 'SDR / BDR Manager', label: 'SDR / BDR Manager' },
                    { value: 'Other', label: 'Other' },
                  ]}
                />
              </div>
            </div>
          </div>

          {/* Qualification Questions */}
          <div className="mb-10">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-orange-400 font-black text-sm">
                3
              </span>
              Qualification
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-white font-semibold mb-2 text-sm">Average Deal Value (ACV) *</label>
                <CustomSelect
                  name="averageDealValue"
                  value={formData.averageDealValue}
                  onChange={(value) => setFormData({ ...formData, averageDealValue: value })}
                  placeholder="Select range"
                  required
                  options={[
                    { value: 'Under £2K', label: 'Under £2K' },
                    { value: '£2K-£5K', label: '£2K-£5K' },
                    { value: '£5K-£10K', label: '£5K-£10K' },
                    { value: '£10K-£25K', label: '£10K-£25K' },
                    { value: '£25K-£50K', label: '£25K-£50K' },
                    { value: '£50K+', label: '£50K+' },
                  ]}
                />
              </div>

              <div>
                <label className="block text-white font-semibold mb-2 text-sm">Dormant Leads in CRM *</label>
                <CustomSelect
                  name="dormantLeadsCount"
                  value={formData.dormantLeadsCount}
                  onChange={(value) => setFormData({ ...formData, dormantLeadsCount: value })}
                  placeholder="Select range"
                  required
                  options={[
                    { value: 'Under 100', label: 'Under 100' },
                    { value: '100-500', label: '100-500' },
                    { value: '500-1000', label: '500-1,000' },
                    { value: '1000-5000', label: '1,000-5,000' },
                    { value: '5000-10000', label: '5,000-10,000' },
                    { value: '10000+', label: '10,000+' },
                  ]}
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-white font-semibold mb-2 text-sm">Current CRM *</label>
                <CustomSelect
                  name="currentCRM"
                  value={formData.currentCRM}
                  onChange={(value) => setFormData({ ...formData, currentCRM: value })}
                  placeholder="Select your CRM"
                  required
                  options={[
                    { value: 'Salesforce', label: 'Salesforce' },
                    { value: 'HubSpot', label: 'HubSpot' },
                    { value: 'Pipedrive', label: 'Pipedrive' },
                    { value: 'Close', label: 'Close' },
                    { value: 'Copper', label: 'Copper' },
                    { value: 'Zoho', label: 'Zoho' },
                    { value: 'Excel/Sheets', label: 'Excel / Google Sheets' },
                    { value: 'Other', label: 'Other' },
                    { value: 'None', label: 'No CRM (manual tracking)' },
                  ]}
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-white font-semibold mb-2 text-sm">Primary Challenge *</label>
                <textarea
                  name="primaryChallenge"
                  value={formData.primaryChallenge}
                  onChange={handleChange}
                  required
                  rows={4}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-orange-500/50 focus:outline-none transition-all resize-none"
                  placeholder="What is your biggest challenge with lead reactivation right now? (Be specific - this helps us tailor your pilot)"
                />
              </div>
            </div>
          </div>

          {/* Pilot Terms Agreement */}
          <div className="mb-10">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-orange-400 font-black text-sm">
                4
              </span>
              Pilot Program Terms
            </h2>

            <div className="glass-card rounded-2xl p-6 border border-green-500/30 bg-green-500/5 mb-6">
              <h3 className="text-white font-bold mb-4 text-lg">Special Pilot Offer:</h3>
              <div className="space-y-3 text-gray-300 text-sm">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>First 30 days: <span className="text-white font-bold">Zero platform fee</span> (performance fee only)</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>Only pay when we book confirmed meetings (2.5-3% of your ACV)</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>After 30 days: <span className="text-white font-bold">50% off platform fee forever</span> (pioneer pricing)</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>Lock in pilot pricing for 6 months minimum (save 30-50% vs. future rates)</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <label className="flex items-start gap-3 cursor-pointer group">
                <input
                  type="checkbox"
                  name="agreedTo30Days"
                  checked={formData.agreedTo30Days}
                  onChange={handleChange}
                  className="w-5 h-5 rounded border-2 border-white/20 bg-white/5 text-orange-500 focus:ring-2 focus:ring-orange-500/50 mt-0.5"
                />
                <span className="text-gray-300 text-sm group-hover:text-white transition-colors">
                  I commit to testing Rekindle for the full 30-day pilot period to allow the AI time to learn and optimize campaigns. *
                </span>
              </label>

              <label className="flex items-start gap-3 cursor-pointer group">
                <input
                  type="checkbox"
                  name="agreedToPerformanceFee"
                  checked={formData.agreedToPerformanceFee}
                  onChange={handleChange}
                  className="w-5 h-5 rounded border-2 border-white/20 bg-white/5 text-orange-500 focus:ring-2 focus:ring-orange-500/50 mt-0.5"
                />
                <span className="text-gray-300 text-sm group-hover:text-white transition-colors">
                  I understand and agree to the performance-based pricing model (2.5-3% of ACV per booked meeting, zero platform fee for first 30 days, then 50% off platform fee forever). *
                </span>
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full px-12 py-5 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-black text-xl rounded-2xl hover:scale-105 transition-all duration-300 shadow-[0_0_40px_rgba(255,107,53,0.4)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-3"
          >
            {isSubmitting ? (
              <>
                <Loader className="w-6 h-6 animate-spin" />
                <span>Submitting Application...</span>
              </>
            ) : (
              <>
                <span>Submit Pilot Application</span>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </>
            )}
          </button>

          <p className="mt-6 text-center text-sm text-gray-500">
            By submitting, you agree to our <button onClick={() => navigate('/terms')} className="text-[#FF6B35] hover:text-[#F7931E] underline">Terms of Service</button> and <button onClick={() => navigate('/privacy')} className="text-[#FF6B35] hover:text-[#F7931E] underline">Privacy Policy</button>
          </p>
        </form>

        {/* Why Apply Section */}
        <div className="mt-16 glass-card p-10 border-2 border-white/10">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">
            Why Apply for the Pilot?
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl mb-3">⚡</div>
              <div className="text-white font-semibold mb-2">Zero Platform Fee (30 Days) + 50% Off Forever</div>
              <div className="text-sm text-gray-400">Only pay for booked meetings. No upfront cost.</div>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-3">🎯</div>
              <div className="text-white font-semibold mb-2">Locked Pricing</div>
              <div className="text-sm text-gray-400">Save 30-50% vs. future rates for 6 months minimum</div>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-3">🤝</div>
              <div className="text-white font-semibold mb-2">Dedicated Support</div>
              <div className="text-sm text-gray-400">Work directly with our team to optimize campaigns</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

