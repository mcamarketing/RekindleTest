// @ts-nocheck
import { supabase } from './supabase';

/**
 * Compliance Utilities for GDPR/CAN-SPAM
 */

export interface ComplianceCheck {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

/**
 * Check if an email is on the suppression list
 */
export async function isEmailSuppressed(email: string): Promise<boolean> {
  try {
    const { data, error } = await supabase
      .rpc('is_email_suppressed', { check_email: email.toLowerCase() });
    
    if (error) {
      console.error('Error checking suppression:', error);
      return false;
    }
    
    return data === true;
  } catch (err) {
    console.error('Error:', err);
    return false;
  }
}

/**
 * Add email to suppression list
 */
export async function suppressEmail(
  email: string,
  reason: 'user_request' | 'bounce' | 'spam_complaint' | 'manual' | 'gdpr_request' | 'legal_requirement' = 'user_request',
  reasonText?: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const { error } = await supabase.rpc('add_to_suppression_list', {
      p_email: email.toLowerCase(),
      p_reason: reason,
      p_reason_text: reasonText,
      p_via: 'api'
    });

    if (error) {
      return { success: false, error: error.message };
    }

    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}

/**
 * Record consent for email marketing
 */
export async function recordConsent(
  email: string,
  consentGiven: boolean,
  method: 'checkbox' | 'form_submission' | 'api' | 'import' | 'double_opt_in' = 'form_submission',
  ipAddress?: string,
  userAgent?: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const { error } = await supabase.rpc('record_consent', {
      p_email: email.toLowerCase(),
      p_consent_type: 'email_marketing',
      p_consent_given: consentGiven,
      p_method: method,
      p_ip_address: ipAddress,
      p_user_agent: userAgent
    });

    if (error) {
      return { success: false, error: error.message };
    }

    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}

/**
 * Generate unsubscribe token for an email
 */
export async function generateUnsubscribeToken(
  email: string,
  leadId?: string
): Promise<{ token?: string; error?: string }> {
  try {
    const { data, error } = await supabase
      .from('unsubscribe_tokens')
      .insert({
        email: email.toLowerCase(),
        lead_id: leadId
      })
      .select('token')
      .single();

    if (error) {
      return { error: error.message };
    }

    return { token: data.token };
  } catch (err: any) {
    return { error: err.message };
  }
}

/**
 * Get unsubscribe link for an email
 */
export async function getUnsubscribeLink(email: string, leadId?: string): Promise<string> {
  const { token } = await generateUnsubscribeToken(email, leadId);
  
  if (!token) {
    // Fallback to email-based unsubscribe
    return `${window.location.origin}/unsubscribe?email=${encodeURIComponent(email)}`;
  }
  
  return `${window.location.origin}/unsubscribe?token=${token}`;
}

/**
 * Get preference center link for an email
 */
export async function getPreferenceCenterLink(email: string): Promise<string> {
  try {
    // Get or create preference token
    const { data, error } = await supabase
      .from('email_preferences')
      .select('preference_token')
      .eq('email', email.toLowerCase())
      .single();

    if (error || !data) {
      // Create new preferences
      const { data: newData, error: insertError } = await supabase
        .from('email_preferences')
        .insert({ email: email.toLowerCase() })
        .select('preference_token')
        .single();

      if (insertError || !newData) {
        return `${window.location.origin}/preferences?email=${encodeURIComponent(email)}`;
      }

      return `${window.location.origin}/preferences?token=${newData.preference_token}`;
    }

    return `${window.location.origin}/preferences?token=${data.preference_token}`;
  } catch {
    return `${window.location.origin}/preferences?email=${encodeURIComponent(email)}`;
  }
}

/**
 * Check if email message is compliant with CAN-SPAM
 */
export function checkEmailCompliance(
  emailHTML: string,
  emailText: string,
  from: { name: string; email: string; address: string }
): ComplianceCheck {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Check for unsubscribe link
  const hasUnsubscribe = 
    emailHTML.toLowerCase().includes('unsubscribe') || 
    emailText.toLowerCase().includes('unsubscribe');
  
  if (!hasUnsubscribe) {
    errors.push('Missing unsubscribe link (CAN-SPAM requirement)');
  }

  // Check for physical address
  const hasAddress = 
    emailHTML.toLowerCase().includes(from.address) || 
    emailText.toLowerCase().includes(from.address);
  
  if (!hasAddress && from.address) {
    errors.push('Missing physical mailing address (CAN-SPAM requirement)');
  }

  // Check for deceptive subject
  if (emailHTML.includes('RE:') || emailHTML.includes('FWD:')) {
    warnings.push('Subject line appears to be a reply/forward - ensure it\'s not deceptive');
  }

  // Check for proper from name
  if (!from.name || from.name.trim().length === 0) {
    warnings.push('From name is empty - recipients should know who is sending');
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Get email footer with compliance info
 */
export async function getEmailFooter(
  recipientEmail: string,
  companyName: string = 'Rekindle.ai',
  companyAddress: string = '123 Innovation Drive, San Francisco, CA 94105'
): Promise<string> {
  const unsubscribeLink = await getUnsubscribeLink(recipientEmail);
  const preferencesLink = await getPreferenceCenterLink(recipientEmail);

  return `
    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; text-align: center;">
      <p style="margin-bottom: 10px;">
        This email was sent by ${companyName}<br/>
        ${companyAddress}
      </p>
      <p style="margin-bottom: 10px;">
        <a href="${unsubscribeLink}" style="color: #3b82f6; text-decoration: underline;">Unsubscribe</a> | 
        <a href="${preferencesLink}" style="color: #3b82f6; text-decoration: underline;">Update Preferences</a>
      </p>
      <p style="font-size: 11px; color: #9ca3af;">
        You're receiving this email because you signed up for ${companyName} or gave us permission to contact you.
      </p>
    </div>
  `;
}

/**
 * Batch check multiple emails against suppression list
 */
export async function batchCheckSuppression(emails: string[]): Promise<{
  email: string;
  suppressed: boolean;
}[]> {
  const results = await Promise.all(
    emails.map(async (email) => ({
      email,
      suppressed: await isEmailSuppressed(email)
    }))
  );
  
  return results;
}

/**
 * Get compliance status for a lead
 */
export async function getLeadComplianceStatus(leadId: string): Promise<{
  hasConsent: boolean;
  isSuppressed: boolean;
  consentDate?: string;
  lawfulBasis?: string;
}> {
  try {
    const { data: lead, error } = await supabase
      .from('leads')
      .select('email, consent_email, consent_given_at, gdpr_lawful_basis')
      .eq('id', leadId)
      .single();

    if (error || !lead) {
      return {
        hasConsent: false,
        isSuppressed: false
      };
    }

    const isSuppressed = await isEmailSuppressed(lead.email);

    return {
      hasConsent: lead.consent_email || false,
      isSuppressed,
      consentDate: lead.consent_given_at,
      lawfulBasis: lead.gdpr_lawful_basis
    };
  } catch {
    return {
      hasConsent: false,
      isSuppressed: false
    };
  }
}

