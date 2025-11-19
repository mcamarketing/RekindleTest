import { useState, useEffect } from 'react';
import { getUnsubscribeLink, getPreferenceCenterLink } from '../lib/compliance';

interface EmailFooterProps {
  recipientEmail: string;
  companyName?: string;
  companyAddress?: string;
  inline?: boolean;
}

export function EmailFooter({
  recipientEmail,
  companyName = 'Rekindle.ai',
  companyAddress = '123 Innovation Drive, San Francisco, CA 94105',
  inline = false
}: EmailFooterProps) {
  const [unsubscribeLink, setUnsubscribeLink] = useState('');
  const [preferencesLink, setPreferencesLink] = useState('');

  useEffect(() => {
    async function loadLinks() {
      const unsub = await getUnsubscribeLink(recipientEmail);
      const prefs = await getPreferenceCenterLink(recipientEmail);
      setUnsubscribeLink(unsub);
      setPreferencesLink(prefs);
    }
    
    if (recipientEmail) {
      loadLinks();
    }
  }, [recipientEmail]);

  if (inline) {
    // Return HTML string for email templates
    return null;
  }

  // React component for preview
  return (
    <div className="mt-8 pt-6 border-t border-gray-200 text-xs text-gray-600 text-center">
      <p className="mb-3">
        This email was sent by {companyName}<br />
        {companyAddress}
      </p>
      <p className="mb-3">
        {unsubscribeLink && (
          <>
            <a href={unsubscribeLink} className="text-blue-600 hover:text-blue-700 underline">
              Unsubscribe
            </a>
            {' | '}
          </>
        )}
        {preferencesLink && (
          <a href={preferencesLink} className="text-blue-600 hover:text-blue-700 underline">
            Update Preferences
          </a>
        )}
      </p>
      <p className="text-gray-500 text-xs">
        You're receiving this email because you signed up for {companyName} or gave us permission to contact you.
      </p>
    </div>
  );
}

/**
 * Get email footer as HTML string for email templates
 */
export async function getEmailFooterHTML(
  recipientEmail: string,
  companyName: string = 'Rekindle.ai',
  companyAddress: string = '123 Innovation Drive, San Francisco, CA 94105'
): Promise<string> {
  const unsubscribeLink = await getUnsubscribeLink(recipientEmail);
  const preferencesLink = await getPreferenceCenterLink(recipientEmail);

  return `
<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-family: sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
      <td align="center" style="font-size: 12px; color: #6b7280; padding-bottom: 10px;">
        This email was sent by ${companyName}<br/>
        ${companyAddress}
      </td>
    </tr>
    <tr>
      <td align="center" style="font-size: 12px; color: #3b82f6; padding-bottom: 10px;">
        <a href="${unsubscribeLink}" style="color: #3b82f6; text-decoration: underline; margin: 0 10px;">Unsubscribe</a>
        <span style="color: #6b7280;">|</span>
        <a href="${preferencesLink}" style="color: #3b82f6; text-decoration: underline; margin: 0 10px;">Update Preferences</a>
      </td>
    </tr>
    <tr>
      <td align="center" style="font-size: 11px; color: #9ca3af; padding-bottom: 20px;">
        You're receiving this email because you signed up for ${companyName} or gave us permission to contact you.
      </td>
    </tr>
  </table>
</div>
  `.trim();
}

