import { ArrowLeft } from 'lucide-react';

export function TermsOfService() {
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 text-[#FF6B35] hover:text-[#F7931E] mb-8 transition-all duration-200 font-semibold hover:gap-3"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </button>

        <div className="glass-card p-8 md:p-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Terms of Service</h1>
          <p className="text-gray-400 mb-8">Last Updated: November 6, 2025</p>

          <div className="prose prose-invert max-w-none space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">1. Agreement to Terms</h2>
              <p className="text-gray-300 leading-relaxed">
                By accessing or using Rekindle.ai ("the Service"), you agree to be bound by these Terms of Service 
                ("Terms"). If you disagree with any part of these Terms, you may not access the Service. These Terms 
                apply to all visitors, users, and others who access or use the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">2. Description of Service</h2>
              <p className="text-gray-300 leading-relaxed">
                Rekindle.ai is an AI-powered CRM and lead generation platform designed to help businesses manage leads, 
                automate outreach campaigns, and optimize sales processes. The Service includes access to our web 
                application, AI agents, analytics tools, and related features.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">3. User Accounts</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Account Creation</h3>
                  <p className="text-gray-300 leading-relaxed">
                    To use certain features of the Service, you must register for an account. You must provide accurate, 
                    complete, and current information during registration and keep your account information updated.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Account Security</h3>
                  <p className="text-gray-300 leading-relaxed">
                    You are responsible for safeguarding your account password and for all activities that occur under 
                    your account. You must notify us immediately of any unauthorized use of your account.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Account Termination</h3>
                  <p className="text-gray-300 leading-relaxed">
                    We reserve the right to suspend or terminate your account at any time for violations of these Terms 
                    or for any other reason at our sole discretion.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">4. Acceptable Use Policy</h2>
              <p className="text-gray-300 leading-relaxed mb-2">You agree not to:</p>
              <ul className="list-disc list-inside text-gray-300 ml-4 space-y-1">
                <li>Use the Service for any illegal purpose or in violation of any laws</li>
                <li>Upload or transmit viruses, malware, or other malicious code</li>
                <li>Attempt to gain unauthorized access to the Service or other users' accounts</li>
                <li>Interfere with or disrupt the Service or servers</li>
                <li>Use the Service to send spam or unsolicited communications</li>
                <li>Scrape, copy, or reverse engineer any portion of the Service</li>
                <li>Impersonate any person or entity or misrepresent your affiliation</li>
                <li>Violate any third-party rights, including privacy and intellectual property rights</li>
                <li>Use automated systems to access the Service without permission</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">5. Two-Part Pricing Model & Billing</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Pricing Structure</h3>
                  <p className="text-gray-300 leading-relaxed mb-4">
                    Rekindle.ai operates on a <span className="text-orange-400 font-bold">Two-Part Pricing Model</span>:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 ml-4 space-y-2">
                    <li>
                      <span className="font-bold text-white">Platform Access Fee:</span> A modest, fixed monthly fee (e.g., £19, £99, or £299 depending on your plan) that covers enterprise infrastructure (99.9% uptime), SOC 2 Type II security, dedicated account support, and real-time CRM integration. This fee is <span className="text-white font-bold">non-refundable</span> as it pays for real operational costs.
                    </li>
                    <li>
                      <span className="font-bold text-white">Performance Fee:</span> A variable fee equal to 2.5% of your Average Contract Value (ACV) per booked meeting. This fee is only charged when a meeting is successfully booked and confirmed on your calendar. The Performance Fee is <span className="text-green-400 font-bold">100% refundable</span> if the booked meeting results in a no-show.
                    </li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Billing Cycle</h3>
                  <p className="text-gray-300 leading-relaxed">
                    The Platform Access Fee is billed in advance on a monthly or annual basis. Performance Fees are calculated and billed at the end of each calendar month based on the number of booked meetings during that month. You authorize us to charge your payment method for all fees incurred.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Performance Fee Refund Policy</h3>
                  <p className="text-gray-300 leading-relaxed">
                    If a booked meeting results in a no-show by the prospect, you may request a full refund of the Performance Fee associated with that specific meeting within 7 days of the scheduled meeting time. Refund requests must be submitted via your account dashboard or by contacting support@rekindle.ai with meeting confirmation details.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Price Changes</h3>
                  <p className="text-gray-300 leading-relaxed">
                    We reserve the right to modify the Platform Access Fee or Performance Fee percentage at any time. Price changes will be communicated to you at least 30 days in advance and will take effect at the start of your next billing cycle. Continued use of the Service after the effective date constitutes acceptance of the new pricing.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Cancellation</h3>
                  <p className="text-gray-300 leading-relaxed">
                    You may cancel your subscription at any time. Cancellation will take effect at the end of your current billing period. The Platform Access Fee for the current period is non-refundable. Any Performance Fees accrued but not yet billed will be charged at the end of the billing period. You will retain access to the Service until the end of the paid period.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Fair Usage & Pilot Program</h3>
                  <p className="text-gray-300 leading-relaxed">
                    During our Exclusive Pilot Program phase, we reserve the right to adjust pricing structures for new customers. Existing customers will maintain their current pricing for a minimum of 6 months from signup date. We commit to transparent communication of any changes affecting your account.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">6. Intellectual Property Rights</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Our Content</h3>
                  <p className="text-gray-300 leading-relaxed">
                    The Service and its original content, features, and functionality are owned by Rekindle.ai and are 
                    protected by international copyright, trademark, patent, trade secret, and other intellectual 
                    property laws.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Your Content</h3>
                  <p className="text-gray-300 leading-relaxed">
                    You retain all rights to the content you upload to the Service. By uploading content, you grant us 
                    a worldwide, non-exclusive, royalty-free license to use, store, display, and process your content 
                    solely to provide the Service to you.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Feedback</h3>
                  <p className="text-gray-300 leading-relaxed">
                    Any feedback, suggestions, or ideas you provide to us become our property, and we may use them 
                    without any obligation to you.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">7. Data and Privacy</h2>
              <p className="text-gray-300 leading-relaxed">
                Your use of the Service is also governed by our Privacy Policy. Please review our Privacy Policy to 
                understand how we collect, use, and protect your personal information. By using the Service, you 
                consent to the collection and use of information as described in our Privacy Policy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">8. AI-Generated Content</h2>
              <p className="text-gray-300 leading-relaxed">
                Rekindle.ai uses artificial intelligence to generate email content, analyze leads, and provide 
                recommendations. While we strive for accuracy, AI-generated content may contain errors or inaccuracies. 
                You are responsible for reviewing and approving all AI-generated content before use. We are not 
                responsible for any consequences resulting from the use of AI-generated content.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">9. Third-Party Services</h2>
              <p className="text-gray-300 leading-relaxed">
                The Service may integrate with third-party services and APIs. We are not responsible for the 
                availability, accuracy, or content of these third-party services. Your use of third-party services 
                is subject to their own terms and conditions.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">10. Disclaimers and Limitations of Liability</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Service Availability</h3>
                  <p className="text-gray-300 leading-relaxed">
                    THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS 
                    OR IMPLIED. WE DO NOT GUARANTEE THAT THE SERVICE WILL BE UNINTERRUPTED, SECURE, OR ERROR-FREE.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Limitation of Liability</h3>
                  <p className="text-gray-300 leading-relaxed">
                    TO THE MAXIMUM EXTENT PERMITTED BY LAW, REKINDLE.AI SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, 
                    SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED 
                    DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Maximum Liability</h3>
                  <p className="text-gray-300 leading-relaxed">
                    Our total liability to you for all claims arising from or related to the Service shall not exceed 
                    the amount you paid us in the twelve (12) months preceding the claim.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">11. Indemnification</h2>
              <p className="text-gray-300 leading-relaxed">
                You agree to indemnify, defend, and hold harmless Rekindle.ai, its officers, directors, employees, 
                and agents from any claims, liabilities, damages, losses, and expenses, including reasonable attorneys' 
                fees, arising out of or in any way connected with your access to or use of the Service, your violation 
                of these Terms, or your violation of any third-party rights.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">12. Compliance with Laws</h2>
              <p className="text-gray-300 leading-relaxed">
                You agree to comply with all applicable laws, regulations, and rules when using the Service, including 
                but not limited to anti-spam laws (CAN-SPAM Act, GDPR, etc.), data protection laws, and intellectual 
                property laws. You are solely responsible for ensuring that your use of the Service complies with all 
                applicable laws in your jurisdiction.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">13. Dispute Resolution</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Informal Resolution</h3>
                  <p className="text-gray-300 leading-relaxed">
                    Before filing a claim, you agree to try to resolve the dispute informally by contacting us at{' '}
                    <a href="mailto:support@rekindle.ai" className="text-[#FF6B35] hover:text-[#F7931E]">
                      support@rekindle.ai
                    </a>
                    . We'll try to resolve the dispute informally within 60 days.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Arbitration</h3>
                  <p className="text-gray-300 leading-relaxed">
                    If we cannot resolve the dispute informally, any dispute arising from these Terms or the Service 
                    will be resolved through binding arbitration in accordance with the rules of the American Arbitration 
                    Association, rather than in court.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Class Action Waiver</h3>
                  <p className="text-gray-300 leading-relaxed">
                    You agree that any arbitration or proceeding shall be limited to the dispute between you and us 
                    individually. You waive your right to participate in a class action lawsuit or class-wide arbitration.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">14. Governing Law</h2>
              <p className="text-gray-300 leading-relaxed">
                These Terms shall be governed by and construed in accordance with the laws of the State of California, 
                United States, without regard to its conflict of law provisions. You agree to submit to the personal 
                jurisdiction of the state and federal courts located in San Francisco, California for any legal 
                proceedings.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">15. Changes to Terms</h2>
              <p className="text-gray-300 leading-relaxed">
                We reserve the right to modify or replace these Terms at any time at our sole discretion. We will 
                provide notice of material changes by posting the new Terms on this page and updating the "Last Updated" 
                date. Your continued use of the Service after such modifications constitutes your acceptance of the 
                updated Terms.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">16. Severability</h2>
              <p className="text-gray-300 leading-relaxed">
                If any provision of these Terms is held to be invalid or unenforceable by a court, the remaining 
                provisions will remain in effect. The invalid or unenforceable provision will be deemed modified to 
                the extent necessary to make it valid and enforceable.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">17. Entire Agreement</h2>
              <p className="text-gray-300 leading-relaxed">
                These Terms, together with our Privacy Policy, constitute the entire agreement between you and 
                Rekindle.ai regarding the Service and supersede all prior agreements and understandings.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">18. Contact Information</h2>
              <p className="text-gray-300 leading-relaxed">
                If you have any questions about these Terms, please contact us:
              </p>
              <div className="mt-4 p-6 bg-white/5 rounded-xl border border-white/10">
                <p className="text-gray-300">
                  <strong className="text-white">Email:</strong>{' '}
                  <a href="mailto:support@rekindle.ai" className="text-[#FF6B35] hover:text-[#F7931E]">
                    support@rekindle.ai
                  </a>
                </p>
                <p className="text-gray-300 mt-2">
                  <strong className="text-white">Address:</strong> Rekindle.ai, 123 Innovation Drive, San Francisco, CA 94105
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

