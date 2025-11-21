import { useState } from 'react';
import { ArrowLeft, CheckCircle, AlertCircle, Loader, ArrowRight, Zap, Target, Users } from 'lucide-react';
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
      <div className="min-h-screen bg-[#f6f9fc] flex items-center justify-center px-4">
        <div className="max-w-2xl w-full bg-white border border-[#e3e8ee] rounded-lg p-12 text-center shadow-sm">
          <div className="w-20 h-20 rounded-full bg-green-50 border border-green-200 flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>

          <h1 className="text-4xl font-bold text-[#0a2540] mb-4 tracking-tight">
            Application Received!
          </h1>

          <p className="text-xl text-[#425466] mb-8 leading-relaxed">
            Thank you for applying to the RekindlePro Pilot Program. We review applications within 24 hours.
          </p>

          <div className="bg-[#f6f9fc] rounded-lg p-6 border border-[#e3e8ee] mb-8">
            <h3 className="text-[#0a2540] font-semibold mb-4">What Happens Next:</h3>
            <div className="text-left space-y-3 text-[#425466] text-sm">
              <div className="flex items-start gap-3">
                <span className="text-[#0a2540] font-bold">1.</span>
                <span>Our team reviews your application (within 24 hours)</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#0a2540] font-bold">2.</span>
                <span>If approved, you receive onboarding email with setup instructions</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#0a2540] font-bold">3.</span>
                <span>Month 1 platform access complimentary (performance fee only)</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#0a2540] font-bold">4.</span>
                <span>We reactivate your dormant leads and book qualified meetings</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/')}
              className="px-8 py-3 bg-[#0a2540] text-white font-medium rounded-md hover:bg-[#0d2d52] transition-colors"
            >
              Return to Home
            </button>
            <button
              onClick={() => navigate('/blog')}
              className="px-8 py-3 bg-white border border-[#e3e8ee] text-[#0a2540] font-medium rounded-md hover:border-[#0a2540] transition-all"
            >
              Read Our Blog
            </button>
          </div>

          <p className="mt-8 text-sm text-[#727f96]">
            Questions? Email us at <a href="mailto:pilot@rekindlepro.ai" className="text-[#0a2540] hover:underline">pilot@rekindlepro.ai</a>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f6f9fc]">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Back button */}
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 text-[#0a2540] hover:text-[#0d2d52] mb-8 transition-colors font-medium"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </button>

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-white border border-[#e3e8ee] rounded-full mb-6 shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
            </span>
            <span className="text-sm text-[#0a2540] font-semibold">Founding Pilot Program</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-[#0a2540] mb-6 tracking-tight">
            Request Pilot Access
          </h1>

          <p className="text-xl text-[#425466] max-w-3xl mx-auto mb-4 leading-relaxed">
            Join the founding pilot program. Month 1 platform access complimentary. Lock in founding member rates permanently.
          </p>

          <p className="text-sm text-[#727f96]">
            Applications reviewed within 24 hours. All company sizes welcome.
          </p>
        </div>

        {/* Application Form */}
        <form onSubmit={handleSubmit} className="bg-white border border-[#e3e8ee] rounded-lg p-10 shadow-sm">
          {error && (
            <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          {/* Company Information */}
          <div className="mb-10">
            <h2 className="text-2xl font-bold text-[#0a2540] mb-6 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-[#f6f9fc] border border-[#e3e8ee] flex items-center justify-center text-[#0a2540] font-bold text-sm">
                1
              </span>
              Company Information
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Company Name *</label>
                <input
                  type="text"
                  name="companyName"
                  value={formData.companyName}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white border border-[#e3e8ee] rounded-md text-[#0a2540] placeholder-[#727f96] focus:border-[#0a2540] focus:outline-none focus:ring-2 focus:ring-[#0a2540] transition-all"
                  placeholder="Acme Corp"
                />
              </div>

              <div>
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Company Website *</label>
                <input
                  type="url"
                  name="companyWebsite"
                  value={formData.companyWebsite}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white border border-[#e3e8ee] rounded-md text-[#0a2540] placeholder-[#727f96] focus:border-[#0a2540] focus:outline-none focus:ring-2 focus:ring-[#0a2540] transition-all"
                  placeholder="https://acmecorp.com"
                />
              </div>

              <div>
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Company Size *</label>
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
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Industry *</label>
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
            <h2 className="text-2xl font-bold text-[#0a2540] mb-6 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-[#f6f9fc] border border-[#e3e8ee] flex items-center justify-center text-[#0a2540] font-bold text-sm">
                2
              </span>
              Your Information
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">First Name *</label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white border border-[#e3e8ee] rounded-md text-[#0a2540] placeholder-[#727f96] focus:border-[#0a2540] focus:outline-none focus:ring-2 focus:ring-[#0a2540] transition-all"
                  placeholder="John"
                />
              </div>

              <div>
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Last Name *</label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white border border-[#e3e8ee] rounded-md text-[#0a2540] placeholder-[#727f96] focus:border-[#0a2540] focus:outline-none focus:ring-2 focus:ring-[#0a2540] transition-all"
                  placeholder="Smith"
                />
              </div>

              <div>
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Work Email *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white border border-[#e3e8ee] rounded-md text-[#0a2540] placeholder-[#727f96] focus:border-[#0a2540] focus:outline-none focus:ring-2 focus:ring-[#0a2540] transition-all"
                  placeholder="john@acmecorp.com"
                />
              </div>

              <div>
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Phone Number *</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white border border-[#e3e8ee] rounded-md text-[#0a2540] placeholder-[#727f96] focus:border-[#0a2540] focus:outline-none focus:ring-2 focus:ring-[#0a2540] transition-all"
                  placeholder="+44 7700 900000"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Your Role *</label>
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
            <h2 className="text-2xl font-bold text-[#0a2540] mb-6 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-[#f6f9fc] border border-[#e3e8ee] flex items-center justify-center text-[#0a2540] font-bold text-sm">
                3
              </span>
              Qualification
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Average Deal Value (ACV) *</label>
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
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Dormant Leads in CRM *</label>
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
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Current CRM *</label>
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
                <label className="block text-[#0a2540] font-medium mb-2 text-sm">Primary Challenge *</label>
                <textarea
                  name="primaryChallenge"
                  value={formData.primaryChallenge}
                  onChange={handleChange}
                  required
                  rows={4}
                  className="w-full px-4 py-3 bg-white border border-[#e3e8ee] rounded-md text-[#0a2540] placeholder-[#727f96] focus:border-[#0a2540] focus:outline-none focus:ring-2 focus:ring-[#0a2540] transition-all resize-none"
                  placeholder="What is your biggest challenge with lead reactivation right now? (Be specific - this helps us tailor your pilot)"
                />
              </div>
            </div>
          </div>

          {/* Pilot Terms Agreement */}
          <div className="mb-10">
            <h2 className="text-2xl font-bold text-[#0a2540] mb-6 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-[#f6f9fc] border border-[#e3e8ee] flex items-center justify-center text-[#0a2540] font-bold text-sm">
                4
              </span>
              Pilot Program Terms
            </h2>

            <div className="bg-green-50 rounded-lg p-6 border border-green-200 mb-6">
              <h3 className="text-[#0a2540] font-bold mb-4 text-lg">Founding Pilot Benefits:</h3>
              <div className="space-y-3 text-[#425466] text-sm">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span>Month 1 platform access complimentary (performance fee only)</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span>Only pay for confirmed meetings with decision-makers</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span>Lock in <span className="text-[#0a2540] font-semibold">founding member rates permanently</span></span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span>5+ meetings in 30 days or £500 account credit guarantee</span>
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
                  className="w-5 h-5 rounded border-2 border-[#e3e8ee] bg-white text-[#0a2540] focus:ring-2 focus:ring-[#0a2540] mt-0.5"
                />
                <span className="text-[#425466] text-sm group-hover:text-[#0a2540] transition-colors">
                  I commit to testing RekindlePro for the full 30-day pilot period to allow the AI time to learn and optimize campaigns. *
                </span>
              </label>

              <label className="flex items-start gap-3 cursor-pointer group">
                <input
                  type="checkbox"
                  name="agreedToPerformanceFee"
                  checked={formData.agreedToPerformanceFee}
                  onChange={handleChange}
                  className="w-5 h-5 rounded border-2 border-[#e3e8ee] bg-white text-[#0a2540] focus:ring-2 focus:ring-[#0a2540] mt-0.5"
                />
                <span className="text-[#425466] text-sm group-hover:text-[#0a2540] transition-colors">
                  I understand and agree to the performance-based pricing model (pay per qualified meeting, founding member rates locked permanently). *
                </span>
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full px-8 py-3 bg-[#0a2540] text-white font-semibold rounded-md hover:bg-[#0d2d52] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
          >
            {isSubmitting ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Submitting application...</span>
              </>
            ) : (
              <>
                <span>Submit application</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>

          <p className="mt-6 text-center text-sm text-[#727f96]">
            By submitting, you agree to our <button onClick={() => navigate('/terms')} className="text-[#0a2540] hover:underline">Terms of Service</button> and <button onClick={() => navigate('/privacy')} className="text-[#0a2540] hover:underline">Privacy Policy</button>
          </p>
        </form>

        {/* Why Apply Section */}
        <div className="mt-16 bg-white border border-[#e3e8ee] rounded-lg p-10 shadow-sm">
          <h3 className="text-2xl font-bold text-[#0a2540] mb-6 text-center">
            Why Apply for the Pilot?
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="flex items-center justify-center mb-3">
                <Zap className="w-10 h-10 text-[#0a2540]" />
              </div>
              <div className="text-[#0a2540] font-semibold mb-2">Founding Member Rates</div>
              <div className="text-sm text-[#727f96]">Lock in permanent pricing. No future increases.</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-3">
                <Target className="w-10 h-10 text-[#0a2540]" />
              </div>
              <div className="text-[#0a2540] font-semibold mb-2">Performance-Based</div>
              <div className="text-sm text-[#727f96]">Only pay for confirmed meetings. No meetings = £0.</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-3">
                <Users className="w-10 h-10 text-[#0a2540]" />
              </div>
              <div className="text-[#0a2540] font-semibold mb-2">Dedicated Support</div>
              <div className="text-sm text-[#727f96]">Work directly with our team to optimize campaigns</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

