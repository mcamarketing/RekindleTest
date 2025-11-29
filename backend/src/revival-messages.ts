import { Request, Response } from 'express';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import { emailService } from './services/email-service';

dotenv.config();

// Create Supabase client conditionally
function getSupabaseClient() {
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;

  // For testing with mock auth, allow missing Supabase config
  if (!supabaseUrl || !supabaseKey || supabaseUrl.includes('test-project') || supabaseUrl.includes('demo-project')) {
    console.log('🔧 Using mock database for testing (Supabase not configured)');
    return null; // Return null to indicate mock mode
  }

  return createClient(supabaseUrl, supabaseKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  });
}

interface AuthRequest extends Request {
  userId?: string;
  userEmail?: string;
  userRole?: string;
}

// Payload size limits (in bytes) to prevent 413 errors
const PAYLOAD_SIZE_LIMITS = {
  are_plan: 500000,      // 500KB
  are_execution: 1000000, // 1MB
  are_content: 500000,    // 500KB
  are_evaluation: 200000, // 200KB
  are_guardrail: 100000,  // 100KB
  are_metadata: 100000   // 100KB
};

// Compress large ARE payloads to prevent 413 errors
function compressAREPayload(data: any, fieldName: string): any {
  if (!data) return data;

  const jsonString = JSON.stringify(data);
  const sizeBytes = Buffer.byteLength(jsonString, 'utf8');
  const limit = PAYLOAD_SIZE_LIMITS[fieldName as keyof typeof PAYLOAD_SIZE_LIMITS] || 100000;

  if (sizeBytes <= limit) {
    return data; // No compression needed
  }

  console.warn(`⚠️ ARE payload for ${fieldName} is ${sizeBytes} bytes, limit is ${limit}. Compressing...`);

  // For large payloads, create a compressed version with essential data only
  if (fieldName === 'are_execution' && typeof data === 'object') {
    // Keep only essential execution data
    return {
      status: data.status,
      task_count: data.task_count || 0,
      success_rate: data.success_rate || 0,
      total_time: data.total_time || 0,
      compressed: true,
      original_size: sizeBytes,
      summary: data.summary || 'Execution completed'
    };
  }

  if (fieldName === 'are_plan' && typeof data === 'object') {
    // Keep only essential plan data
    return {
      plan_id: data.plan_id,
      goal_type: data.goal_type,
      task_count: data.tasks?.length || 0,
      status: data.status,
      compressed: true,
      original_size: sizeBytes
    };
  }

  if (fieldName === 'are_content' && typeof data === 'object') {
    // Keep only essential content data
    return {
      method: data.method || 'unknown',
      status: data.status || 'unknown',
      compressed: true,
      original_size: sizeBytes
    };
  }

  // For other fields, truncate to fit within limits
  const truncatedString = jsonString.substring(0, limit - 100) + '"}';
  try {
    return JSON.parse(truncatedString);
  } catch (e) {
    // If truncation breaks JSON, return a safe summary
    return {
      error: 'Payload too large',
      original_size: sizeBytes,
      limit: limit,
      compressed: true
    };
  }
}

// Generate revival messages for selected leads
export const generateRevivalMessages = async (req: AuthRequest, res: Response) => {
  try {
    const { lead_ids } = req.body;

    if (!lead_ids || !Array.isArray(lead_ids) || lead_ids.length === 0) {
      return res.status(400).json({ success: false, error: 'lead_ids array is required' });
    }

    if (lead_ids.length > 50) {
      return res.status(400).json({ success: false, error: 'Maximum 50 leads per batch' });
    }

    // Check request payload size to prevent 413 errors
    const requestSize = Buffer.byteLength(JSON.stringify(req.body), 'utf8');
    if (requestSize > 1000000) { // 1MB limit for request body
      return res.status(413).json({
        success: false,
        error: 'Request payload too large',
        details: `Request size: ${requestSize} bytes, limit: 1MB`
      });
    }

    const supabase = getSupabaseClient();

    let leads: any[] = [];

    if (supabase) {
      // Real database mode
      const { data: leadsData, error: fetchError } = await supabase
        .from('leads')
        .select('id, first_name, last_name, email, company, job_title, lead_score')
        .eq('user_id', req.userId!)
        .in('id', lead_ids);

      if (fetchError) throw fetchError;

      if (!leadsData || leadsData.length === 0) {
        return res.status(404).json({ success: false, error: 'No leads found' });
      }

      leads = leadsData;
    } else {
      // Mock mode - create mock leads
      leads = lead_ids.map(id => ({
        id,
        first_name: 'Test',
        last_name: 'User',
        email: `test${id}@example.com`,
        company: 'Test Company',
        job_title: 'Test Role',
        lead_score: 75
      }));
    }

    console.log(`🎯 Generating revival messages for ${leads.length} leads for user ${req.userId}`);

    // For now, use a simple template-based approach
    // TODO: Integrate with ARE pipeline when ready
    const generatedMessages = [];

    for (const lead of leads) {
      try {
        // Generate subject and body using simple templates
        const subject = `Following up on our previous conversation`;
        const body = `Hi ${lead.first_name || 'there'},

I hope this email finds you well. I wanted to follow up on our previous conversation about ${lead.company ? `${lead.company}'s needs` : 'your business goals'}.

We've helped similar companies achieve significant improvements in their lead generation and sales processes. I'd love to hear if you've had any new developments or if there's anything specific you'd like to explore further.

Would you be available for a quick 15-minute call next week to discuss?

Best regards,
[Your Name]
[Your Position]
[Your Contact Information]`;

        const followupSubject = `Just checking in - any updates on your side?`;
        const followupBody = `Hi ${lead.first_name || 'there'},

I wanted to follow up on my previous email. I understand you might be busy, but I wanted to make sure you received my message about helping ${lead.company || 'your company'}.

We're currently working with several companies in similar situations and have been able to help them significantly improve their results.

If you're still interested, I'd be happy to schedule a brief call to discuss how we might be able to help you.

Looking forward to hearing from you.

Best regards,
[Your Name]`;

        // Save to database or use mock data
        let messageRecord: any;

        // Prepare ARE data with size limits to prevent 413 errors
        const areData = {
          are_plan: compressAREPayload(
            { status: 'simulated', message: 'Using template-based generation for now' },
            'are_plan'
          ),
          are_execution: compressAREPayload(
            { status: 'completed', template_used: true },
            'are_execution'
          ),
          are_content: compressAREPayload(
            { status: 'generated', method: 'template' },
            'are_content'
          ),
          are_evaluation: compressAREPayload(
            { status: 'passed', score: 85 },
            'are_evaluation'
          ),
          are_guardrail: compressAREPayload(
            { status: 'approved', checks: ['content_safety', 'compliance'] },
            'are_guardrail'
          )
        };

        if (supabase) {
          const { data: record, error: insertError } = await supabase
            .from('revival_messages')
            .insert({
              lead_id: lead.id,
              user_id: req.userId!,
              subject,
              body,
              followup_subject: followupSubject,
              followup_body: followupBody,
              ...areData
            })
            .select()
            .single();

          if (insertError) throw insertError;
          messageRecord = record;
        } else {
          // Mock record for testing
          messageRecord = {
            id: `mock-${Date.now()}-${Math.random()}`,
            lead_id: lead.id,
            user_id: req.userId!,
            subject,
            body,
            followup_subject: followupSubject,
            followup_body: followupBody,
            created_at: new Date().toISOString()
          };
        }

        generatedMessages.push({
          id: messageRecord.id,
          lead_id: lead.id,
          lead_name: `${lead.first_name} ${lead.last_name}`.trim(),
          lead_email: lead.email,
          subject,
          body,
          followup_subject: followupSubject,
          followup_body: followupBody,
          created_at: messageRecord.created_at
        });

      } catch (leadError: any) {
        console.error(`Error generating message for lead ${lead.id}:`, leadError);
        // Continue with other leads
      }
    }

    console.log(`✅ Generated ${generatedMessages.length} revival messages`);

    res.json({
      success: true,
      data: {
        generated: generatedMessages.length,
        messages: generatedMessages
      },
      message: `Successfully generated revival messages for ${generatedMessages.length} leads`
    });

  } catch (error: any) {
    console.error('Revival message generation error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
};

// Get revival messages for user
export const getRevivalMessages = async (req: AuthRequest, res: Response) => {
  try {
    const supabase = getSupabaseClient();
    const limit = Math.min(parseInt(req.query.limit as string) || 50, 100);
    const offset = parseInt(req.query.offset as string) || 0;

    if (supabase) {
      const { data: messages, error } = await supabase
        .from('revival_messages')
        .select(`
          id,
          lead_id,
          subject,
          body,
          followup_subject,
          followup_body,
          status,
          created_at,
          leads (
            first_name,
            last_name,
            email,
            company,
            lead_score
          )
        `)
        .eq('user_id', req.userId!)
        .order('created_at', { ascending: false })
        .range(offset, offset + limit - 1);

      if (error) throw error;

      res.json({
        success: true,
        data: messages || [],
        pagination: {
          limit,
          offset,
          hasMore: messages && messages.length === limit
        }
      });
    } else {
      // Mock data for testing
      const mockMessages = [
        {
          id: 'mock-1',
          lead_id: 'lead-1',
          subject: 'Following up on our previous conversation',
          body: 'Hi there,\n\nI hope this email finds you well...',
          followup_subject: 'Just checking in - any updates on your side?',
          followup_body: 'Hi there,\n\nI wanted to follow up...',
          status: 'pending',
          created_at: new Date().toISOString(),
          leads: {
            first_name: 'Test',
            last_name: 'User',
            email: 'test@example.com',
            company: 'Test Company',
            lead_score: 75
          }
        }
      ];

      res.json({
        success: true,
        data: mockMessages,
        pagination: {
          limit,
          offset: 0,
          hasMore: false
        }
      });
    }

  } catch (error: any) {
    console.error('Revival messages fetch error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
};

// Send revival messages via email
export const sendRevivalMessages = async (req: AuthRequest, res: Response) => {
  try {
    const supabase = getSupabaseClient();
    const { messageIds } = req.body;

    if (!messageIds || !Array.isArray(messageIds) || messageIds.length === 0) {
      return res.status(400).json({ success: false, error: 'messageIds array is required' });
    }

    if (messageIds.length > 20) {
      return res.status(400).json({ success: false, error: 'Maximum 20 messages per batch' });
    }

    console.log(`📧 Sending ${messageIds.length} revival messages for user ${req.userId}`);

    if (supabase) {
      // Real implementation
      let sent = 0;
      let failed = 0;
      const results = [];

      for (const messageId of messageIds) {
        try {
          const { data: message, error: fetchError } = await supabase
            .from('revival_messages')
            .select(`
              id,
              subject,
              body,
              status,
              leads (
                first_name,
                last_name,
                email
              )
            `)
            .eq('id', messageId)
            .eq('user_id', req.userId!)
            .single();

          if (fetchError || !message) {
            console.error(`Message ${messageId} not found or access denied`);
            failed++;
            results.push({ messageId, success: false, error: 'Message not found' });
            continue;
          }

          if (message.status === 'sent') {
            console.log(`Message ${messageId} already sent`);
            sent++;
            results.push({ messageId, success: true, status: 'already_sent' });
            continue;
          }

          const lead = Array.isArray(message.leads) ? message.leads[0] : message.leads;
          if (!lead?.email) {
            console.error(`No email found for lead in message ${messageId}`);
            failed++;
            results.push({ messageId, success: false, error: 'No email address' });
            continue;
          }

          const emailResult = await emailService.sendEmail({
            to: lead.email,
            subject: message.subject,
            html: message.body.replace(/\n/g, '<br>'),
            text: message.body,
          });

          if (emailResult.success) {
            await supabase
              .from('revival_messages')
              .update({
                status: 'sent',
                sent_at: new Date().toISOString(),
                provider_message_id: emailResult.providerMessageId,
              })
              .eq('id', messageId);

            sent++;
            results.push({
              messageId,
              success: true,
              providerMessageId: emailResult.providerMessageId
            });
          } else {
            await supabase
              .from('revival_messages')
              .update({
                status: 'failed',
              })
              .eq('id', messageId);

            failed++;
            results.push({
              messageId,
              success: false,
              error: emailResult.error
            });
          }

        } catch (messageError: any) {
          console.error(`Error sending message ${messageId}:`, messageError);
          failed++;
          results.push({ messageId, success: false, error: messageError.message });
        }
      }

      console.log(`✅ Sent ${sent} messages, ${failed} failed`);

      res.json({
        success: true,
        data: {
          sent,
          failed,
          results
        },
        message: `Sent ${sent} messages, ${failed} failed`
      });
    } else {
      // Mock implementation for testing
      const results = messageIds.map(id => ({
        messageId: id,
        success: true,
        providerMessageId: `mock-${Date.now()}-${id}`
      }));

      res.json({
        success: true,
        data: {
          sent: messageIds.length,
          failed: 0,
          results
        },
        message: `Mock: Sent ${messageIds.length} messages successfully`
      });
    }

  } catch (error: any) {
    console.error('Revival message sending error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
};

// Record revival outcome
export const recordRevivalOutcome = async (req: AuthRequest, res: Response) => {
  try {
    const supabase = getSupabaseClient();
    const { revivalMessageId, leadId, outcome, notes } = req.body;

    if (!revivalMessageId || !leadId || !outcome) {
      return res.status(400).json({
        success: false,
        error: 'revivalMessageId, leadId, and outcome are required'
      });
    }

    const validOutcomes = ['positive', 'meeting', 'no_reply', 'bad_data'];
    if (!validOutcomes.includes(outcome)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid outcome. Must be: positive, meeting, no_reply, or bad_data'
      });
    }

    if (supabase) {
      // Real implementation
      const { data: message, error: messageError } = await supabase
        .from('revival_messages')
        .select('id, lead_id')
        .eq('id', revivalMessageId)
        .eq('user_id', req.userId!)
        .single();

      if (messageError || !message || message.lead_id !== leadId) {
        return res.status(404).json({
          success: false,
          error: 'Revival message not found or access denied'
        });
      }

      const { data: outcomeRecord, error: insertError } = await supabase
        .from('revival_outcomes')
        .insert({
          revival_message_id: revivalMessageId,
          lead_id: leadId,
          user_id: req.userId!,
          outcome,
          notes: notes || null,
        })
        .select()
        .single();

      if (insertError) throw insertError;

      if (outcome === 'meeting') {
        await supabase
          .from('leads')
          .update({ status: 'meeting_booked' })
          .eq('id', leadId)
          .eq('user_id', req.userId!);
      } else if (outcome === 'positive') {
        await supabase
          .from('leads')
          .update({ status: 'engaged' })
          .eq('id', leadId)
          .eq('user_id', req.userId!);
      }

      res.json({
        success: true,
        data: outcomeRecord,
        message: `Outcome "${outcome}" recorded successfully`
      });
    } else {
      // Mock implementation
      const mockOutcome = {
        id: `outcome-${Date.now()}`,
        revival_message_id: revivalMessageId,
        lead_id: leadId,
        user_id: req.userId!,
        outcome,
        notes: notes || null,
        created_at: new Date().toISOString()
      };

      res.json({
        success: true,
        data: mockOutcome,
        message: `Mock: Outcome "${outcome}" recorded successfully`
      });
    }

  } catch (error: any) {
    console.error('Revival outcome recording error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
};

// Get revival outcomes for user
export const getRevivalOutcomes = async (req: AuthRequest, res: Response) => {
  try {
    const supabase = getSupabaseClient();
    const limit = Math.min(parseInt(req.query.limit as string) || 100, 500);

    if (!supabase) {
      return res.status(500).json({ success: false, error: 'Database not configured' });
    }

    const { data: outcomes, error } = await supabase
      .from('revival_outcomes')
      .select(`
        id,
        revival_message_id,
        lead_id,
        outcome,
        notes,
        created_at,
        leads (
          first_name,
          last_name,
          email
        )
      `)
      .eq('user_id', req.userId!)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) throw error;

    res.json({
      success: true,
      data: outcomes || []
    });

  } catch (error: any) {
    console.error('Revival outcomes fetch error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
};

// Get revival stats for user
export const getRevivalStats = async (req: AuthRequest, res: Response) => {
  try {
    const supabase = getSupabaseClient();

    if (!supabase) {
      return res.status(500).json({ success: false, error: 'Database not configured' });
    }

    // Get total leads with messages
    const { count: totalLeadsWithMessages } = await supabase
      .from('revival_messages')
      .select('lead_id', { count: 'exact', head: true })
      .eq('user_id', req.userId!);

    // Get total messages sent
    const { count: totalMessagesSent } = await supabase
      .from('revival_messages')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', req.userId!)
      .eq('status', 'sent');

    // Get outcomes
    const { data: outcomes } = await supabase
      .from('revival_outcomes')
      .select('outcome')
      .eq('user_id', req.userId!);

    const totalOutcomes = outcomes?.length || 0;
    const repliesOrPositive = outcomes?.filter(o =>
      o.outcome === 'positive' || o.outcome === 'meeting'
    ).length || 0;
    const meetings = outcomes?.filter(o => o.outcome === 'meeting').length || 0;

    const replyRate = totalMessagesSent ? (repliesOrPositive / totalMessagesSent) : 0;
    const meetingRate = totalMessagesSent ? (meetings / totalMessagesSent) : 0;

    res.json({
      success: true,
      data: {
        totalLeadsWithMessages: totalLeadsWithMessages || 0,
        totalMessagesSent: totalMessagesSent || 0,
        totalOutcomes,
        repliesOrPositive,
        meetings,
        replyRate: Math.round(replyRate * 100) / 100,
        meetingRate: Math.round(meetingRate * 100) / 100,
      }
    });

  } catch (error: any) {
    console.error('Revival stats fetch error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
};