/**
 * Enhanced Pilot Application Form
 * Multi-step wizard with validation and better UX
 * Maintains RekindlePro branding
 */

import { useState } from 'react';
import { Check, ArrowRight, ArrowLeft, Loader, Building2, User, Mail, Phone, DollarSign, Users, Target, Briefcase } from 'lucide-react';

interface FormData {
  // Step 1: Company Info
  companyName: string;
  companyWebsite: string;
  companySize: string;
  industry: string;
  // Step 2: Contact Info
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role: string;
  // Step 3: Qualification
  averageDealValue: string;
  dormantLeadsCount: string;
  currentCRM: string;
  primaryChallenge: string;
  // Step 4: Commitment
  agreedTo30Days: boolean;
  agreedToPerformanceFee: boolean;
}

const STEPS = [
  { id: 1, title: 'Company', icon: Building2 },
  { id: 2, title: 'Contact', icon: User },
  { id: 3, title: 'Qualification', icon: Target },
  { id: 4, title: 'Commitment', icon: Briefcase },
];

export const EnhancedPilotForm = ({ onSubmit }: { onSubmit: (data: FormData) => Promise<void> }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    companyName: '',
    companyWebsite: '',
    companySize: '',
    industry: '',
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: '',
    averageDealValue: '',
    dormantLeadsCount: '',
    currentCRM: '',
    primaryChallenge: '',
    agreedTo30Days: false,
    agreedToPerformanceFee: false,
  });

  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});

  const validateStep = (step: number): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};

    if (step === 1) {
      if (!formData.companyName) newErrors.companyName = 'Company name is required';
      if (!formData.companyWebsite) newErrors.companyWebsite = 'Website is required';
      if (!formData.companySize) newErrors.companySize = 'Company size is required';
      if (!formData.industry) newErrors.industry = 'Industry is required';
    } else if (step === 2) {
      if (!formData.firstName) newErrors.firstName = 'First name is required';
      if (!formData.lastName) newErrors.lastName = 'Last name is required';
      if (!formData.email) newErrors.email = 'Email is required';
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = 'Invalid email format';
      if (!formData.phone) newErrors.phone = 'Phone is required';
      if (!formData.role) newErrors.role = 'Role is required';
    } else if (step === 3) {
      if (!formData.averageDealValue) newErrors.averageDealValue = 'Average deal value is required';
      if (!formData.dormantLeadsCount) newErrors.dormantLeadsCount = 'Dormant leads count is required';
      if (!formData.currentCRM) newErrors.currentCRM = 'Current CRM is required';
      if (!formData.primaryChallenge) newErrors.primaryChallenge = 'Primary challenge is required';
    } else if (step === 4) {
      if (!formData.agreedTo30Days) newErrors.agreedTo30Days = 'You must agree to the 30-day pilot';
      if (!formData.agreedToPerformanceFee) newErrors.agreedToPerformanceFee = 'You must agree to the performance fee structure';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep(4)) return;

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const updateField = (field: keyof FormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    setErrors(prev => ({ ...prev, [field]: undefined }));
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Step Indicator */}
      <div className="mb-12">
        <div className="flex items-center justify-between relative">
          {/* Progress Line */}
          <div className="absolute top-8 left-0 right-0 h-1 bg-gray-800">
            <div
              className="h-full bg-gradient-to-r from-[#FF6B35] to-[#F7931E] transition-all duration-500"
              style={{ width: `${((currentStep - 1) / (STEPS.length - 1)) * 100}%` }}
            />
          </div>

          {/* Step Circles */}
          {STEPS.map((step) => {
            const Icon = step.icon;
            const isCompleted = currentStep > step.id;
            const isCurrent = currentStep === step.id;

            return (
              <div key={step.id} className="relative flex flex-col items-center">
                <div
                  className={`w-16 h-16 rounded-full flex items-center justify-center border-4 transition-all duration-300 ${
                    isCompleted
                      ? 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E] border-transparent'
                      : isCurrent
                      ? 'bg-[#1A1F2E] border-[#FF6B35] shadow-lg shadow-[#FF6B35]/50'
                      : 'bg-[#242938] border-gray-700'
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-8 h-8 text-white" />
                  ) : (
                    <Icon className={`w-8 h-8 ${isCurrent ? 'text-[#FF6B35]' : 'text-gray-600'}`} />
                  )}
                </div>
                <span
                  className={`mt-3 text-sm font-semibold ${
                    isCurrent ? 'text-white' : isCompleted ? 'text-[#FF6B35]' : 'text-gray-600'
                  }`}
                >
                  {step.title}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Form Content */}
      <div className="bg-gradient-to-br from-[#1A1F2E] to-[#242938] rounded-2xl p-8 border border-gray-800">
        {/* Step 1: Company Info */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-fade-in">
            <h2 className="text-3xl font-bold text-white mb-6">Company Information</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Company Name *</label>
                <input
                  type="text"
                  value={formData.companyName}
                  onChange={(e) => updateField('companyName', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.companyName ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white placeholder-gray-500 focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                  placeholder="Acme Corp"
                />
                {errors.companyName && <p className="mt-1 text-sm text-red-500">{errors.companyName}</p>}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Company Website *</label>
                <input
                  type="url"
                  value={formData.companyWebsite}
                  onChange={(e) => updateField('companyWebsite', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.companyWebsite ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white placeholder-gray-500 focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                  placeholder="https://acmecorp.com"
                />
                {errors.companyWebsite && <p className="mt-1 text-sm text-red-500">{errors.companyWebsite}</p>}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Company Size *</label>
                <select
                  value={formData.companySize}
                  onChange={(e) => updateField('companySize', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.companySize ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                >
                  <option value="">Select size</option>
                  <option value="1-10">1-10 employees</option>
                  <option value="11-50">11-50 employees</option>
                  <option value="51-200">51-200 employees</option>
                  <option value="201-1000">201-1000 employees</option>
                  <option value="1000+">1000+ employees</option>
                </select>
                {errors.companySize && <p className="mt-1 text-sm text-red-500">{errors.companySize}</p>}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Industry *</label>
                <select
                  value={formData.industry}
                  onChange={(e) => updateField('industry', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.industry ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                >
                  <option value="">Select industry</option>
                  <option value="SaaS">SaaS</option>
                  <option value="Technology">Technology</option>
                  <option value="Financial Services">Financial Services</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Manufacturing">Manufacturing</option>
                  <option value="Professional Services">Professional Services</option>
                  <option value="Other">Other</option>
                </select>
                {errors.industry && <p className="mt-1 text-sm text-red-500">{errors.industry}</p>}
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Contact Info */}
        {currentStep === 2 && (
          <div className="space-y-6 animate-fade-in">
            <h2 className="text-3xl font-bold text-white mb-6">Contact Information</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">First Name *</label>
                <input
                  type="text"
                  value={formData.firstName}
                  onChange={(e) => updateField('firstName', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.firstName ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white placeholder-gray-500 focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                  placeholder="John"
                />
                {errors.firstName && <p className="mt-1 text-sm text-red-500">{errors.firstName}</p>}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Last Name *</label>
                <input
                  type="text"
                  value={formData.lastName}
                  onChange={(e) => updateField('lastName', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.lastName ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white placeholder-gray-500 focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                  placeholder="Smith"
                />
                {errors.lastName && <p className="mt-1 text-sm text-red-500">{errors.lastName}</p>}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Email *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => updateField('email', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.email ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white placeholder-gray-500 focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                  placeholder="john@acmecorp.com"
                />
                {errors.email && <p className="mt-1 text-sm text-red-500">{errors.email}</p>}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Phone *</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => updateField('phone', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.phone ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white placeholder-gray-500 focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                  placeholder="+1 (555) 123-4567"
                />
                {errors.phone && <p className="mt-1 text-sm text-red-500">{errors.phone}</p>}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-gray-300 mb-2">Role *</label>
                <select
                  value={formData.role}
                  onChange={(e) => updateField('role', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.role ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                >
                  <option value="">Select role</option>
                  <option value="Founder/CEO">Founder/CEO</option>
                  <option value="VP Sales">VP Sales</option>
                  <option value="Head of Revenue">Head of Revenue</option>
                  <option value="Sales Director">Sales Director</option>
                  <option value="Marketing Director">Marketing Director</option>
                  <option value="Other">Other</option>
                </select>
                {errors.role && <p className="mt-1 text-sm text-red-500">{errors.role}</p>}
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Qualification */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-fade-in">
            <h2 className="text-3xl font-bold text-white mb-6">Qualification</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Average Deal Value *</label>
                <select
                  value={formData.averageDealValue}
                  onChange={(e) => updateField('averageDealValue', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.averageDealValue ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                >
                  <option value="">Select range</option>
                  <option value="<£5k">&lt;£5k</option>
                  <option value="£5k-£15k">£5k-£15k</option>
                  <option value="£15k-£50k">£15k-£50k</option>
                  <option value="£50k-£100k">£50k-£100k</option>
                  <option value="£100k+">£100k+</option>
                </select>
                {errors.averageDealValue && <p className="mt-1 text-sm text-red-500">{errors.averageDealValue}</p>}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Dormant Leads Count *</label>
                <select
                  value={formData.dormantLeadsCount}
                  onChange={(e) => updateField('dormantLeadsCount', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.dormantLeadsCount ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                >
                  <option value="">Select range</option>
                  <option value="<500">&lt;500</option>
                  <option value="500-2k">500-2,000</option>
                  <option value="2k-5k">2,000-5,000</option>
                  <option value="5k-10k">5,000-10,000</option>
                  <option value="10k+">10,000+</option>
                </select>
                {errors.dormantLeadsCount && <p className="mt-1 text-sm text-red-500">{errors.dormantLeadsCount}</p>}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-gray-300 mb-2">Current CRM *</label>
                <select
                  value={formData.currentCRM}
                  onChange={(e) => updateField('currentCRM', e.target.value)}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.currentCRM ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                >
                  <option value="">Select CRM</option>
                  <option value="Salesforce">Salesforce</option>
                  <option value="HubSpot">HubSpot</option>
                  <option value="Pipedrive">Pipedrive</option>
                  <option value="Close">Close</option>
                  <option value="Copper">Copper</option>
                  <option value="Other">Other</option>
                </select>
                {errors.currentCRM && <p className="mt-1 text-sm text-red-500">{errors.currentCRM}</p>}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-gray-300 mb-2">Primary Challenge *</label>
                <textarea
                  value={formData.primaryChallenge}
                  onChange={(e) => updateField('primaryChallenge', e.target.value)}
                  rows={4}
                  className={`w-full px-4 py-3 bg-[#0a0e1a] border ${
                    errors.primaryChallenge ? 'border-red-500' : 'border-gray-700'
                  } rounded-lg text-white placeholder-gray-500 focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all`}
                  placeholder="Describe your biggest challenge with dormant leads..."
                />
                {errors.primaryChallenge && <p className="mt-1 text-sm text-red-500">{errors.primaryChallenge}</p>}
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Commitment */}
        {currentStep === 4 && (
          <div className="space-y-6 animate-fade-in">
            <h2 className="text-3xl font-bold text-white mb-6">Pilot Program Terms</h2>

            <div className="space-y-6">
              {/* 30-Day Agreement */}
              <div className={`p-6 rounded-xl border-2 ${formData.agreedTo30Days ? 'border-[#FF6B35] bg-[#FF6B35]/5' : 'border-gray-700 bg-[#0a0e1a]'} transition-all`}>
                <label className="flex items-start gap-4 cursor-pointer">
                  <div className="relative flex-shrink-0 mt-1">
                    <input
                      type="checkbox"
                      checked={formData.agreedTo30Days}
                      onChange={(e) => updateField('agreedTo30Days', e.target.checked)}
                      className="w-6 h-6 border-2 border-gray-600 rounded bg-transparent checked:bg-[#FF6B35] checked:border-[#FF6B35] cursor-pointer"
                    />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white mb-2">30-Day Pilot Commitment</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">
                      I agree to participate in the 30-day pilot program. Month 1 platform access is complimentary.
                      Performance fee only applies to qualified meetings booked.
                    </p>
                  </div>
                </label>
                {errors.agreedTo30Days && <p className="mt-2 text-sm text-red-500">{errors.agreedTo30Days}</p>}
              </div>

              {/* Performance Fee Agreement */}
              <div className={`p-6 rounded-xl border-2 ${formData.agreedToPerformanceFee ? 'border-[#FF6B35] bg-[#FF6B35]/5' : 'border-gray-700 bg-[#0a0e1a]'} transition-all`}>
                <label className="flex items-start gap-4 cursor-pointer">
                  <div className="relative flex-shrink-0 mt-1">
                    <input
                      type="checkbox"
                      checked={formData.agreedToPerformanceFee}
                      onChange={(e) => updateField('agreedToPerformanceFee', e.target.checked)}
                      className="w-6 h-6 border-2 border-gray-600 rounded bg-transparent checked:bg-[#FF6B35] checked:border-[#FF6B35] cursor-pointer"
                    />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white mb-2">Performance Fee Structure</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">
                      I agree to the performance fee structure: pay only for qualified meetings booked.
                      No meetings = no cost. Transparent pricing disclosed during onboarding.
                    </p>
                  </div>
                </label>
                {errors.agreedToPerformanceFee && <p className="mt-2 text-sm text-red-500">{errors.agreedToPerformanceFee}</p>}
              </div>

              {/* Info Box */}
              <div className="p-6 rounded-xl bg-gradient-to-r from-[#FF6B35]/10 to-[#F7931E]/10 border border-[#FF6B35]/30">
                <h3 className="text-white font-bold mb-3">What Happens Next:</h3>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-[#FF6B35] font-bold mt-0.5">1.</span>
                    <span>Application review within 24 hours</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#FF6B35] font-bold mt-0.5">2.</span>
                    <span>Onboarding email with setup instructions</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#FF6B35] font-bold mt-0.5">3.</span>
                    <span>Platform access granted (complimentary month 1)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#FF6B35] font-bold mt-0.5">4.</span>
                    <span>AI agents begin reactivating dormant leads</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-700">
          <button
            onClick={handleBack}
            disabled={currentStep === 1}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              currentStep === 1
                ? 'opacity-0 pointer-events-none'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>

          {currentStep < 4 ? (
            <button
              onClick={handleNext}
              className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold rounded-lg hover:scale-105 transition-all shadow-lg hover:shadow-[#FF6B35]/50"
            >
              Next Step
              <ArrowRight className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold rounded-lg hover:scale-105 transition-all shadow-lg hover:shadow-[#FF6B35]/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  Submit Application
                  <Check className="w-5 h-5" />
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
