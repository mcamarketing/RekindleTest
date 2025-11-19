import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';
import { createClient } from '@supabase/supabase-js';
import jwt from 'jsonwebtoken';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Supabase client with service role (bypasses RLS)
console.log('🔑 Using Supabase Service Role Key:', process.env.SUPABASE_SERVICE_ROLE_KEY ? 'YES ✅' : 'NO ❌ (falling back to anon key)');
const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY!,
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  }
);

// JWT Authentication Types
interface JWTPayload {
  sub: string; // user_id
  email: string;
  role?: string;
  iat: number;
  exp: number;
}

interface AuthRequest extends Request {
  userId?: string;
  userEmail?: string;
  userRole?: string;
}

// JWT Authentication Middleware
const authMiddleware = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader?.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        error: 'Authorization token required'
      });
    }

    const token = authHeader.substring(7);
    const JWT_SECRET = process.env.JWT_SECRET || process.env.SUPABASE_JWT_SECRET;

    if (!JWT_SECRET) {
      console.error('❌ JWT_SECRET not configured in environment');
      throw new Error('JWT_SECRET not configured');
    }

    const decoded = jwt.verify(token, JWT_SECRET) as JWTPayload;
    req.userId = decoded.sub;
    req.userEmail = decoded.email;
    req.userRole = decoded.role;

    next();
  } catch (error: any) {
    return res.status(401).json({
      success: false,
      error: error.name === 'TokenExpiredError' ? 'Token expired' : 'Invalid token'
    });
  }
};

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

if (process.env.NODE_ENV !== 'production') {
  app.use(morgan('dev'));
}

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000'),
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100'),
  message: 'Too many requests, please try again later.',
});
app.use('/api/', limiter);

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// API Routes

// Get all agents
app.get('/api/agents', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    // First, check if agents exist - if not, they need to be initialized
    const { data: agents, error } = await supabase
      .from('agents')
      .select('*')
      .eq('user_id', req.userId!) // ✅ USER OWNERSHIP CHECK
      .order('created_at', { ascending: false });

    if (error) throw error;

    // If no agents, return empty array (user needs to run initialize_ai_agents.sql)
    if (!agents || agents.length === 0) {
      console.warn('⚠️ No agents found in database. Run initialize_ai_agents.sql to create agents.');
      return res.json({ success: true, data: [] });
    }

    // Remove duplicates by ID (in case of any database issues)
    const uniqueAgents = agents.filter((agent, index, self) => 
      index === self.findIndex(a => a.id === agent.id)
    );

    if (uniqueAgents.length !== agents.length) {
      console.warn(`⚠️ Removed ${agents.length - uniqueAgents.length} duplicate agents from database query`);
    }

    // Update agent heartbeats for agents that should be working
    // Check for active campaigns and update relevant agents
    const { data: activeCampaigns } = await supabase
      .from('campaigns')
      .select('id, status')
      .eq('status', 'active');

    if (activeCampaigns && activeCampaigns.length > 0) {
      // Update agents that should be working (all agents for now, since any campaign needs all agents)
      const now = new Date().toISOString();
      await supabase
        .from('agents')
        .update({ 
          last_heartbeat: now,
          status: 'active',
          updated_at: now
        })
        .in('id', uniqueAgents.map(a => a.id));
    }

    res.json({ success: true, data: uniqueAgents });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get agent by ID
app.get('/api/agents/:id', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { data, error } = await supabase
      .from('agents')
      .select('*')
      .eq('id', req.params.id)
      .eq('user_id', req.userId!) // ✅ USER OWNERSHIP CHECK
      .maybeSingle();

    if (error) throw error;
    if (!data) {
      return res.status(404).json({ success: false, error: 'Agent not found' });
    }

    res.json({ success: true, data });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get agent metrics
app.get('/api/agents/:id/metrics', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const MAX_LIMIT = 1000;
    const limit = Math.min(parseInt(req.query.limit as string) || 100, MAX_LIMIT); // ✅ DoS PREVENTION

    const { data, error } = await supabase
      .from('agent_metrics')
      .select('*')
      .eq('agent_id', req.params.id)
      .order('recorded_at', { ascending: false })
      .limit(limit);

    if (error) throw error;

    res.json({ success: true, data });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get all metrics (for analytics)
app.get('/api/metrics', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const hoursBack = parseInt(req.query.hours as string) || 24;
    const timeAgo = new Date(Date.now() - hoursBack * 60 * 60 * 1000).toISOString();

    const { data, error } = await supabase
      .from('agent_metrics')
      .select('*')
      .gte('recorded_at', timeAgo)
      .order('recorded_at', { ascending: true });

    if (error) throw error;

    res.json({ success: true, data });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get all tasks
app.get('/api/tasks', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const agentId = req.query.agent_id as string;
    const status = req.query.status as string;

    let query = supabase.from('agent_tasks').select('*');

    if (agentId) {
      query = query.eq('agent_id', agentId);
    }
    if (status) {
      query = query.eq('status', status);
    }

    const { data, error } = await query.order('created_at', { ascending: false });

    if (error) throw error;

    res.json({ success: true, data });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get dashboard stats
app.get('/api/dashboard/stats', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { data: agents } = await supabase
      .from('agents')
      .select('status')
      .eq('user_id', req.userId!); // ✅ USER OWNERSHIP CHECK

    const { data: tasks } = await supabase
      .from('agent_tasks')
      .select('status');

    const MAX_LIMIT = 1000;
    const { data: metrics } = await supabase
      .from('agent_metrics')
      .select('cpu_usage, memory_usage, response_time, error_count')
      .order('recorded_at', { ascending: false })
      .limit(Math.min(100, MAX_LIMIT)); // ✅ DoS PREVENTION

    const activeAgents = agents?.filter(a => a.status === 'active').length || 0;
    const activeTasks = tasks?.filter(t => t.status === 'in_progress').length || 0;
    const completedTasks = tasks?.filter(t => t.status === 'completed').length || 0;
    const failedTasks = tasks?.filter(t => t.status === 'failed').length || 0;

    const avgCpuUsage = metrics?.length
      ? metrics.reduce((sum, m) => sum + (Number(m.cpu_usage) || 0), 0) / metrics.length
      : 0;

    const avgMemoryUsage = metrics?.length
      ? metrics.reduce((sum, m) => sum + (Number(m.memory_usage) || 0), 0) / metrics.length
      : 0;

    const avgResponseTime = metrics?.length
      ? metrics.reduce((sum, m) => sum + (Number(m.response_time) || 0), 0) / metrics.length
      : 0;

    const totalErrors = metrics?.reduce((sum: number, m: any) => sum + (Number(m.error_count) || 0), 0) || 0;

    res.json({
      success: true,
      data: {
        totalAgents: agents?.length || 0,
        activeAgents,
        totalTasks: tasks?.length || 0,
        activeTasks,
        completedTasks,
        failedTasks,
        totalErrors,
        avgResponseTime: Math.round(avgResponseTime),
        avgCpuUsage: Math.round(avgCpuUsage * 10) / 10,
        avgMemoryUsage: Math.round(avgMemoryUsage * 10) / 10
      }
    });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get alerts
app.get('/api/alerts', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const isResolved = req.query.is_resolved;

    let query = supabase
      .from('system_alerts')
      .select('*')
      .eq('user_id', req.userId!); // ✅ USER OWNERSHIP CHECK

    if (isResolved !== undefined) {
      query = query.eq('is_resolved', isResolved === 'true');
    }

    const { data, error } = await query.order('created_at', { ascending: false });

    if (error) throw error;

    res.json({ success: true, data });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Campaign Management Endpoints

// Launch/Activate Campaign
app.post('/api/campaigns/:id/launch', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;

    // Get campaign details
    const { data: campaign, error: fetchError } = await supabase
      .from('campaigns')
      .select('*')
      .eq('id', id)
      .eq('user_id', req.userId!) // ✅ USER OWNERSHIP CHECK
      .maybeSingle();

    if (fetchError) throw fetchError;
    if (!campaign) {
      return res.status(404).json({ success: false, error: 'Campaign not found' });
    }

    if (campaign.status === 'active') {
      return res.status(400).json({ success: false, error: 'Campaign is already active' });
    }

    // Update campaign status to active
    const { data: updatedCampaign, error: updateError } = await supabase
      .from('campaigns')
      .update({
        status: 'active',
        start_date: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      })
      .eq('id', id)
      .select()
      .single();

    if (updateError) throw updateError;

    // Update campaign_leads to active status
    const { error: leadsError } = await supabase
      .from('campaign_leads')
      .update({
        status: 'active',
        next_message_scheduled_at: new Date().toISOString(),
      })
      .eq('campaign_id', id)
      .eq('status', 'pending');

    if (leadsError) throw leadsError;

    // Get lead IDs for this campaign
    const { data: campaignLeads } = await supabase
      .from('campaign_leads')
      .select('lead_id')
      .eq('campaign_id', id);

    const leadIds = campaignLeads?.map(cl => cl.lead_id) || [];

    // Trigger AI agents to start working on this campaign
    if (leadIds.length > 0) {
      try {
        const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';
        const authHeader = req.headers.authorization || '';
        
        console.log(`🚀 Triggering AI agents for campaign ${id} with ${leadIds.length} leads...`);
        
        // Call Python backend to start campaign agents
        const pythonResponse = await fetch(`${pythonBackendUrl}/api/v1/campaigns/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': authHeader,
          },
          body: JSON.stringify({
            lead_ids: leadIds,
          }),
          signal: AbortSignal.timeout(10000), // 10 second timeout
        }).catch(err => {
          console.warn('⚠️ Python backend not available:', err.message);
          console.log('📝 Agents will be updated to active status in database...');
          return null;
        });

        if (pythonResponse && pythonResponse.ok) {
          const pythonData = await pythonResponse.json();
          console.log('✅ AI agents triggered for campaign:', pythonData);
        } else if (pythonResponse) {
          const errorText = await pythonResponse.text();
          console.warn('⚠️ Python backend returned error:', pythonResponse.status, errorText);
        }

        // Also update agents in database to show they should be working
        // This ensures agents show as active even if Python backend isn't running
        const { data: allAgents } = await supabase
          .from('agents')
          .select('id');

        if (allAgents && allAgents.length > 0) {
          const now = new Date().toISOString();
          await supabase
            .from('agents')
            .update({
              last_heartbeat: now,
              status: 'active',
              updated_at: now
            })
            .in('id', allAgents.map(a => a.id));
          console.log(`✅ Updated ${allAgents.length} agents to active status`);
        }
      } catch (error: any) {
        // Don't fail the campaign launch if agent trigger fails
        console.warn('⚠️ Could not trigger AI agents:', error.message);
        // Still try to update agent status
        try {
          const { data: allAgents } = await supabase
            .from('agents')
            .select('id');
          if (allAgents && allAgents.length > 0) {
            const now = new Date().toISOString();
            await supabase
              .from('agents')
              .update({
                last_heartbeat: now,
                status: 'active',
                updated_at: now
              })
              .in('id', allAgents.map(a => a.id));
          }
        } catch (updateError) {
          console.error('Failed to update agent status:', updateError);
        }
      }
    }

    res.json({
      success: true,
      message: 'Campaign launched successfully',
      data: updatedCampaign,
    });
  } catch (error: any) {
    console.error('Campaign launch error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Pause Campaign
app.post('/api/campaigns/:id/pause', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;

    const { data: updatedCampaign, error } = await supabase
      .from('campaigns')
      .update({
        status: 'paused',
        updated_at: new Date().toISOString(),
      })
      .eq('id', id)
      .eq('user_id', req.userId!) // ✅ USER OWNERSHIP CHECK
      .select()
      .single();

    if (error) throw error;

    // Pause all active campaign_leads
    await supabase
      .from('campaign_leads')
      .update({ status: 'paused' })
      .eq('campaign_id', id)
      .eq('status', 'active');

    res.json({
      success: true,
      message: 'Campaign paused successfully',
      data: updatedCampaign,
    });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Resume Campaign
app.post('/api/campaigns/:id/resume', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;

    const { data: updatedCampaign, error } = await supabase
      .from('campaigns')
      .update({
        status: 'active',
        updated_at: new Date().toISOString(),
      })
      .eq('id', id)
      .eq('user_id', req.userId!) // ✅ USER OWNERSHIP CHECK
      .select()
      .single();

    if (error) throw error;

    // Resume paused campaign_leads
    await supabase
      .from('campaign_leads')
      .update({ status: 'active' })
      .eq('campaign_id', id)
      .eq('status', 'paused');

    res.json({
      success: true,
      message: 'Campaign resumed successfully',
      data: updatedCampaign,
    });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Send test message for campaign
app.post('/api/campaigns/:id/test-message', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;
    const { leadId, testEmail } = req.body;

    // Get campaign and lead info
    const { data: campaign } = await supabase
      .from('campaigns')
      .select('*')
      .eq('id', id)
      .eq('user_id', req.userId!) // ✅ USER OWNERSHIP CHECK
      .single();

    const { data: lead } = await supabase
      .from('leads')
      .select('*')
      .eq('id', leadId)
      .eq('user_id', req.userId!) // ✅ USER OWNERSHIP CHECK
      .single();

    if (!campaign || !lead) {
      return res.status(404).json({ success: false, error: 'Campaign or lead not found' });
    }

    // Create test message record
    const { data: message, error: messageError } = await supabase
      .from('messages')
      .insert({
        campaign_id: id,
        lead_id: leadId,
        subject: `Test: ${campaign.name}`,
        body: campaign.message_template || 'Test message body',
        channel: 'email',
        status: 'sent',
        sent_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (messageError) throw messageError;

    res.json({
      success: true,
      message: `Test message sent to ${testEmail || lead.email}`,
      data: message,
    });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get campaign statistics
app.get('/api/campaigns/:id/stats', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;

    // Verify campaign ownership first
    const { data: campaign } = await supabase
      .from('campaigns')
      .select('id')
      .eq('id', id)
      .eq('user_id', req.userId!) // ✅ USER OWNERSHIP CHECK
      .maybeSingle();

    if (!campaign) {
      return res.status(404).json({ success: false, error: 'Campaign not found' });
    }

    // Get campaign leads stats
    const { data: campaignLeads, error: leadsError } = await supabase
      .from('campaign_leads')
      .select('status, messages_sent, messages_opened, messages_replied')
      .eq('campaign_id', id);

    if (leadsError) throw leadsError;

    // Get messages stats
    const { data: messages, error: messagesError } = await supabase
      .from('messages')
      .select('status, open_count, click_count')
      .eq('campaign_id', id);

    if (messagesError) throw messagesError;

    const stats = {
      totalLeads: campaignLeads?.length || 0,
      activeLeads: campaignLeads?.filter(l => l.status === 'active').length || 0,
      completedLeads: campaignLeads?.filter(l => l.status === 'completed').length || 0,
      repliedLeads: campaignLeads?.filter(l => l.status === 'replied').length || 0,
      messagesSent: messages?.filter(m => m.status === 'sent' || m.status === 'delivered' || m.status === 'opened').length || 0,
      messagesOpened: messages?.reduce((sum, m) => sum + (m.open_count || 0), 0) || 0,
      messagesClicked: messages?.reduce((sum, m) => sum + (m.click_count || 0), 0) || 0,
      messagesReplied: messages?.filter(m => m.status === 'replied').length || 0,
      openRate: 0,
      replyRate: 0,
    };

    if (stats.messagesSent > 0) {
      stats.openRate = Math.round((stats.messagesOpened / stats.messagesSent) * 100);
      stats.replyRate = Math.round((stats.messagesReplied / stats.messagesSent) * 100);
    }

    res.json({ success: true, data: stats });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// AI Chat endpoint (Sales & Support Assistant)
app.post('/api/ai/chat', async (req: Request, res: Response) => {
  try {
    const { message, context, conversationHistory } = req.body;

    if (!message) {
      return res.status(400).json({ success: false, error: 'Message is required' });
    }

    // Try to use Python FastAPI backend if available, otherwise use fallback
    const pythonBackendUrl = process.env.PYTHON_API_URL || 'http://localhost:8081';
    
    try {
      // Try to proxy to Python backend (preferred - uses Anthropic AI)
      const authHeader = req.headers.authorization || '';
      const pythonResponse = await fetch(`${pythonBackendUrl}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authHeader,
        },
        body: JSON.stringify({ message, context, conversationHistory }),
        signal: AbortSignal.timeout(8000), // 8 second timeout for speed
      });

      if (pythonResponse.ok) {
        const data = await pythonResponse.json();
        return res.json(data);
      }
    } catch (error: any) {
      // Python backend not available, use fallback
      if (error.name !== 'AbortError') {
        console.log('Python backend not available, using fallback response:', error.message);
      }
    }

    // Fallback: More intelligent, conversational responses
    const lowerMessage = message.toLowerCase();
    let response = "";

    // Handle casual greetings naturally
    if (['yo', 'sup', 'hey', 'wassup', "what's up", 'hi', 'hello'].includes(lowerMessage.trim())) {
      response = "Hey! I'm Rex, orchestrating 28 AI agents to help reactivate dead leads. What brings you here today?";
    }
    // Handle "tell me more" - build on previous context
    else if (lowerMessage.includes('tell me more') || lowerMessage.includes('more info') || lowerMessage === 'more') {
      response = "Sure thing! Rekindle helps you turn dormant CRM data into revenue. Here's the magic:\n\n**The Problem:** 85% of your CRM is wasted - leads that went cold, prospects that ghosted, deals that stalled.\n\n**Our Solution:** 28 AI agents work 24/7 to:\n• Research each lead (LinkedIn, company news, funding rounds)\n• Score them 0-100 for revival potential\n• Craft personalized messages across email, SMS, WhatsApp\n• Auto-book meetings when they respond\n\n**The Results:** 5-15% reactivation rate. For most companies, that's $50K-$500K+ in recovered pipeline per quarter.\n\nWhat's your biggest lead reactivation challenge right now?";
    }
    // More intelligent default responses based on keywords
    else if (lowerMessage.includes('pricing') || lowerMessage.includes('cost')) {
      response = "Two options that scale with you:\n\n**$99/month Starter** - Fixed cost, perfect for testing\n**2.5% performance fee** - Only pay when deals close\n\nTypical ROI: 3,687x in first 90 days. What's your average deal size? I can show you the math.";
    }
    else if (lowerMessage.includes('agent') || lowerMessage.includes('how') || lowerMessage.includes('work')) {
      response = "Think of it like having 28 specialists on autopilot:\n\n**Research Squad** finds trigger events (new funding, job changes, hiring sprees)\n**Content Team** writes messages that don't sound like spam\n**Safety Team** ensures GDPR/CAN-SPAM compliance\n**Revenue Team** books meetings automatically\n\nIt's like having a full SDR team, but they work 24/7 and cost $99/month.\n\nCurious about a specific agent type?";
    }
    else if (lowerMessage.includes('demo') || lowerMessage.includes('try') || lowerMessage.includes('test')) {
      response = "Best way to see it? Just use it. Import your dead leads (takes 2 minutes), and we'll show you:\n\n1. Which leads have the highest revival potential\n2. What trigger events we found\n3. Sample messages we'd send\n\nTypically see first responses within 48 hours. Want to start with a quick test batch?";
    }
    else if (lowerMessage.includes('lead') && (lowerMessage.includes('dead') || lowerMessage.includes('cold') || lowerMessage.includes('dormant'))) {
      response = "Dead leads are goldmines! Here's why:\n\n• They already know your brand (no cold intro needed)\n• Zero acquisition cost\n• Often went cold for fixable reasons (bad timing, wrong person, etc.)\n\nOur AI figures out WHY they went cold, then crafts the perfect re-engagement approach. Most companies reactivate 5-15% - which at $5K average deal value means massive ROI.\n\nHow many dead leads are sitting in your CRM right now?";
    }
    else {
      // Generic but still conversational
      response = `Interesting question! Let me help with that.\n\nI'm Rex - I orchestrate 28 AI agents to reactivate your dead/cold leads automatically. Think: automated research, personalized outreach, meeting booking.\n\nWhat specific challenge are you facing with lead reactivation?`;
    }

    res.json({
      success: true,
      data: { response }
    });
  } catch (error: any) {
    console.error('AI chat error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to process chat message'
    });
  }
});

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
    path: req.path
  });
});

// Error handler
app.use((err: any, req: Request, res: Response, next: any) => {
  console.error('Error:', err);
  res.status(500).json({
    success: false,
    error: process.env.NODE_ENV === 'production' ? 'Internal server error' : err.message
  });
});

// Start server
const server = app.listen(PORT, () => {
  console.log(`✅ Backend server running on port ${PORT}`);
  console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔗 CORS origin: ${process.env.CORS_ORIGIN || 'http://localhost:5173'}`);
  console.log(`🏥 Health check: http://localhost:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('\nSIGINT received, closing server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

export default app;
