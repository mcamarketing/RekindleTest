import { ArrowLeft } from 'lucide-react';

export function PrivacyPolicy() {
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
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Privacy Policy</h1>
          <p className="text-gray-400 mb-8">Last Updated: November 6, 2025</p>

          <div className="prose prose-invert max-w-none space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">1. Introduction</h2>
              <p className="text-gray-300 leading-relaxed">
                Welcome to Rekindle.ai ("we," "our," or "us"). We are committed to protecting your personal information 
                and your right to privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard 
                your information when you use our platform.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">2. Information We Collect</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Personal Information</h3>
                  <p className="text-gray-300 leading-relaxed">
                    We collect information that you provide directly to us, including:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 ml-4 mt-2 space-y-1">
                    <li>Name and contact information (email address, phone number)</li>
                    <li>Account credentials (username and password)</li>
                    <li>Company information</li>
                    <li>Lead data you upload or import</li>
                    <li>Billing and payment information</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Automatically Collected Information</h3>
                  <p className="text-gray-300 leading-relaxed">
                    When you use our platform, we automatically collect:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 ml-4 mt-2 space-y-1">
                    <li>Usage data and analytics</li>
                    <li>Device information (IP address, browser type, operating system)</li>
                    <li>Cookies and similar tracking technologies</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">3. How We Use Your Information</h2>
              <p className="text-gray-300 leading-relaxed mb-2">We use the information we collect to:</p>
              <ul className="list-disc list-inside text-gray-300 ml-4 space-y-1">
                <li>Provide, maintain, and improve our services</li>
                <li>Process transactions and send related information</li>
                <li>Send administrative information, updates, and security alerts</li>
                <li>Respond to your comments, questions, and customer service requests</li>
                <li>Analyze usage patterns and optimize user experience</li>
                <li>Detect, prevent, and address technical issues and fraudulent activity</li>
                <li>Comply with legal obligations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">4. Information Sharing and Disclosure</h2>
              <p className="text-gray-300 leading-relaxed mb-2">
                We do not sell your personal information. We may share your information in the following circumstances:
              </p>
              <ul className="list-disc list-inside text-gray-300 ml-4 space-y-1">
                <li><strong>Service Providers:</strong> With third-party vendors who perform services on our behalf</li>
                <li><strong>Business Transfers:</strong> In connection with any merger, sale, or acquisition</li>
                <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
                <li><strong>With Your Consent:</strong> When you explicitly consent to sharing</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">5. Security Measures and SOC 2 Compliance</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">SOC 2 Type II Certification</h3>
                  <p className="text-gray-300 leading-relaxed">
                    Rekindle.ai maintains <span className="text-green-400 font-bold">SOC 2 Type II certification</span>, demonstrating our commitment to enterprise-grade security controls. Our SOC 2 audit covers the Security, Availability, and Confidentiality Trust Services Criteria, ensuring that your data is protected by industry-leading security practices.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Data Protection Measures</h3>
                  <p className="text-gray-300 leading-relaxed mb-2">
                    We implement comprehensive technical and organizational measures to protect your personal information:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 ml-4 space-y-2">
                    <li><strong>Encryption:</strong> All data is encrypted at rest (AES-256) and in transit (TLS 1.3)</li>
                    <li><strong>Access Control:</strong> Role-based access control (RBAC) with principle of least privilege</li>
                    <li><strong>Monitoring:</strong> 24/7 security monitoring and automated threat detection</li>
                    <li><strong>Incident Response:</strong> Documented incident response procedures with &lt; 24 hour notification</li>
                    <li><strong>Vulnerability Management:</strong> Regular security assessments and penetration testing</li>
                    <li><strong>Audit Logging:</strong> Comprehensive audit trails retained for compliance purposes</li>
                    <li><strong>Data Segregation:</strong> Multi-tenant architecture with strict data isolation</li>
                    <li><strong>Backup & Recovery:</strong> Automated backups with point-in-time recovery capabilities</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Subprocessor Security</h3>
                  <p className="text-gray-300 leading-relaxed">
                    We partner exclusively with SOC 2 compliant or ISO 27001 certified infrastructure providers (Supabase for database, Vercel for hosting). All subprocessors undergo security due diligence and are contractually required to maintain security standards equivalent to our own.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Security Incident Notification</h3>
                  <p className="text-gray-300 leading-relaxed">
                    In the event of a security incident affecting your personal data, we will notify you within 72 hours via email to your registered account address, in compliance with GDPR Article 33 requirements. Notifications will include the nature of the breach, data affected, and remediation steps taken.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">6. Data Retention</h2>
              <p className="text-gray-300 leading-relaxed">
                We retain your personal information for as long as necessary to fulfill the purposes outlined in this 
                Privacy Policy, unless a longer retention period is required or permitted by law. When we no longer 
                need your information, we will securely delete or anonymize it.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">7. Your Privacy Rights</h2>
              <p className="text-gray-300 leading-relaxed mb-2">
                Depending on your location, you may have certain rights regarding your personal information:
              </p>
              <ul className="list-disc list-inside text-gray-300 ml-4 space-y-1">
                <li><strong>Access:</strong> Request access to your personal information</li>
                <li><strong>Correction:</strong> Request correction of inaccurate information</li>
                <li><strong>Deletion:</strong> Request deletion of your personal information</li>
                <li><strong>Portability:</strong> Request a copy of your data in a portable format</li>
                <li><strong>Objection:</strong> Object to processing of your personal information</li>
                <li><strong>Withdrawal:</strong> Withdraw consent at any time</li>
              </ul>
              <p className="text-gray-300 leading-relaxed mt-4">
                To exercise these rights, please contact us at{' '}
                <a href="mailto:privacy@rekindle.ai" className="text-[#FF6B35] hover:text-[#F7931E]">
                  privacy@rekindle.ai
                </a>
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">8. Cookies and Tracking</h2>
              <p className="text-gray-300 leading-relaxed">
                We use cookies and similar tracking technologies to collect and track information about your use of 
                our platform. You can instruct your browser to refuse all cookies or to indicate when a cookie is 
                being sent. However, if you do not accept cookies, you may not be able to use some portions of our service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">9. Third-Party Links</h2>
              <p className="text-gray-300 leading-relaxed">
                Our platform may contain links to third-party websites or services. We are not responsible for the 
                privacy practices of these third parties. We encourage you to review their privacy policies.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">10. Children's Privacy</h2>
              <p className="text-gray-300 leading-relaxed">
                Our service is not directed to children under the age of 13. We do not knowingly collect personal 
                information from children under 13. If you become aware that a child has provided us with personal 
                information, please contact us.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">11. International Data Transfers</h2>
              <p className="text-gray-300 leading-relaxed">
                Your information may be transferred to and processed in countries other than your own. These countries 
                may have different data protection laws. We ensure that appropriate safeguards are in place to protect 
                your information in accordance with this Privacy Policy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">12. Changes to This Privacy Policy</h2>
              <p className="text-gray-300 leading-relaxed">
                We may update this Privacy Policy from time to time. We will notify you of any changes by posting the 
                new Privacy Policy on this page and updating the "Last Updated" date. You are advised to review this 
                Privacy Policy periodically for any changes.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">13. Contact Us</h2>
              <p className="text-gray-300 leading-relaxed">
                If you have any questions about this Privacy Policy, please contact us:
              </p>
              <div className="mt-4 p-6 bg-white/5 rounded-xl border border-white/10">
                <p className="text-gray-300">
                  <strong className="text-white">Email:</strong>{' '}
                  <a href="mailto:privacy@rekindle.ai" className="text-[#FF6B35] hover:text-[#F7931E]">
                    privacy@rekindle.ai
                  </a>
                </p>
                <p className="text-gray-300 mt-2">
                  <strong className="text-white">Address:</strong> Rekindle.ai, 123 Innovation Drive, San Francisco, CA 94105
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">14. GDPR Compliance (EU Users)</h2>
              <p className="text-gray-300 leading-relaxed">
                If you are located in the European Economic Area (EEA), you have certain rights under the General Data 
                Protection Regulation (GDPR). Our lawful basis for processing your personal data includes consent, 
                contractual necessity, legal obligations, and legitimate interests. You have the right to lodge a 
                complaint with a supervisory authority.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-white mb-4">15. CCPA Compliance (California Users)</h2>
              <p className="text-gray-300 leading-relaxed">
                If you are a California resident, you have specific rights under the California Consumer Privacy Act 
                (CCPA), including the right to know what personal information is collected, the right to delete personal 
                information, and the right to opt-out of the sale of personal information. We do not sell personal information.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

