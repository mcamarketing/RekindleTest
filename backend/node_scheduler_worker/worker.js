/**
 * Node.js Scheduler Worker - The Message Sender
 * 
 * Production-grade BullMQ worker that:
 * - Consumes jobs from Redis queue
 * - Sends messages via SendGrid (email), Twilio (SMS/WhatsApp)
 * - Handles retries with exponential backoff
 * - Logs all operations
 * - Updates lead status in database
 */

const { Worker, Queue } = require('bullmq');
const { createClient } = require('@supabase/supabase-js');
const sgMail = require('@sendgrid/mail');
const twilio = require('twilio');
const winston = require('winston');
require('dotenv').config();

// ============================================================================
// FAIL-FAST: VERIFY CRITICAL ENVIRONMENT VARIABLES
// ============================================================================

const REQUIRED_ENV_VARS = [
    'SUPABASE_URL',
    'SUPABASE_SERVICE_ROLE_KEY',
    'SENDGRID_API_KEY'
];

const missingVars = REQUIRED_ENV_VARS.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
    console.error(`FATAL: Missing required environment variables: ${missingVars.join(', ')}`);
    console.error('Application cannot start without these variables. Exiting...');
    process.exit(1);
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const REDIS_CONFIG = {
    host: process.env.REDIS_HOST || '127.0.0.1',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    password: process.env.REDIS_PASSWORD || undefined,
    maxRetriesPerRequest: 3,
    retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
    }
};

const QUEUE_NAME = process.env.REDIS_SCHEDULER_QUEUE || 'message_scheduler_queue';

// Initialize Supabase
const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
);

// Initialize SendGrid
if (process.env.SENDGRID_API_KEY) {
    sgMail.setApiKey(process.env.SENDGRID_API_KEY);
}

// Initialize Twilio
let twilioClient = null;
if (process.env.TWILIO_ACCOUNT_SID && process.env.TWILIO_AUTH_TOKEN) {
    twilioClient = twilio(
        process.env.TWILIO_ACCOUNT_SID,
        process.env.TWILIO_AUTH_TOKEN
    );
}

// ============================================================================
// LOGGING
// ============================================================================

const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    defaultMeta: {
        service: 'rekindle-scheduler-worker',
        instance: process.env.NODE_INSTANCE_ID || 'worker-001'
    },
    transports: [
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.simple()
            )
        })
    ]
});

// Add file transport in production
if (process.env.NODE_ENV === 'production') {
    logger.add(new winston.transports.File({
        filename: 'logs/worker-error.log',
        level: 'error'
    }));
    logger.add(new winston.transports.File({
        filename: 'logs/worker-combined.log'
    }));
}

// ============================================================================
// MESSAGE SENDING FUNCTIONS
// ============================================================================

/**
 * Send email via SendGrid
 */
async function sendEmail(messageData) {
    const {
        to,
        from,
        subject,
        html,
        text,
        lead_id,
        campaign_id,
        user_id
    } = messageData;

    if (!process.env.SENDGRID_API_KEY) {
        throw new Error('SENDGRID_API_KEY not configured');
    }

    try {
        const msg = {
            to,
            from: from || process.env.SENDGRID_FROM_EMAIL || 'noreply@rekindle.ai',
            subject,
            html: html || text,
            text: text || html,
            // Custom tracking
            customArgs: {
                lead_id,
                campaign_id,
                user_id
            },
            // Unsubscribe link
            asm: {
                groupId: parseInt(process.env.SENDGRID_UNSUBSCRIBE_GROUP_ID || '0'),
                groupsToDisplay: [parseInt(process.env.SENDGRID_UNSUBSCRIBE_GROUP_ID || '0')]
            }
        };

        const [response] = await sgMail.send(msg);

        logger.info('WORKER_DELIVERY_SUCCESS', {
            channel: 'email',
            lead_id,
            campaign_id,
            to,
            message_id: response.headers['x-message-id'],
            timestamp: new Date().toISOString()
        });

        return {
            success: true,
            channel: 'email',
            message_id: response.headers['x-message-id'],
            sent_at: new Date().toISOString()
        };
    } catch (error) {
        logger.error('Email send error', {
            lead_id,
            campaign_id,
            to,
            error: error.message,
            stack: error.stack
        });
        throw error;
    }
}

/**
 * Send SMS via Twilio
 */
async function sendSMS(messageData) {
    const {
        to,
        body,
        lead_id,
        campaign_id,
        user_id
    } = messageData;

    if (!twilioClient) {
        throw new Error('Twilio not configured');
    }

    try {
        const message = await twilioClient.messages.create({
            body,
            from: process.env.TWILIO_PHONE_NUMBER,
            to
        });

        logger.info('WORKER_DELIVERY_SUCCESS', {
            channel: 'sms',
            lead_id,
            campaign_id,
            to,
            message_sid: message.sid,
            timestamp: new Date().toISOString()
        });

        return {
            success: true,
            channel: 'sms',
            message_id: message.sid,
            sent_at: new Date().toISOString()
        };
    } catch (error) {
        logger.error('SMS send error', {
            lead_id,
            campaign_id,
            to,
            error: error.message,
            stack: error.stack
        });
        throw error;
    }
}

/**
 * Send WhatsApp via Twilio
 */
async function sendWhatsApp(messageData) {
    const {
        to,
        body,
        lead_id,
        campaign_id,
        user_id
    } = messageData;

    if (!twilioClient) {
        throw new Error('Twilio not configured');
    }

    try {
        // Twilio WhatsApp format: whatsapp:+1234567890
        const whatsappTo = to.startsWith('whatsapp:') ? to : `whatsapp:${to}`;
        const whatsappFrom = process.env.TWILIO_WHATSAPP_NUMBER || 
            `whatsapp:${process.env.TWILIO_PHONE_NUMBER}`;

        const message = await twilioClient.messages.create({
            body,
            from: whatsappFrom,
            to: whatsappTo
        });

        logger.info('WORKER_DELIVERY_SUCCESS', {
            channel: 'whatsapp',
            lead_id,
            campaign_id,
            to,
            message_sid: message.sid,
            timestamp: new Date().toISOString()
        });

        return {
            success: true,
            channel: 'whatsapp',
            message_id: message.sid,
            sent_at: new Date().toISOString()
        };
    } catch (error) {
        logger.error('WhatsApp send error', {
            lead_id,
            campaign_id,
            to,
            error: error.message,
            stack: error.stack
        });
        throw error;
    }
}

/**
 * Send push notification (placeholder - would integrate with FCM/APNs)
 */
async function sendPush(messageData) {
    const {
        to,
        title,
        body,
        lead_id,
        campaign_id,
        user_id
    } = messageData;

    // Placeholder - would integrate with Firebase Cloud Messaging or Apple Push Notification Service
    logger.info('Push notification (placeholder)', {
        lead_id,
        campaign_id,
        to,
        title,
        body
    });

    return {
        success: true,
        channel: 'push',
        message_id: `push_${Date.now()}`,
        sent_at: new Date().toISOString()
    };
}

/**
 * Send voicemail drop (placeholder - would integrate with Twilio Voice API)
 */
async function sendVoicemail(messageData) {
    const {
        to,
        message_text,
        lead_id,
        campaign_id,
        user_id
    } = messageData;

    // Placeholder - would integrate with Twilio Voice API
    logger.info('Voicemail drop (placeholder)', {
        lead_id,
        campaign_id,
        to,
        message_text
    });

    return {
        success: true,
        channel: 'voicemail',
        message_id: `voicemail_${Date.now()}`,
        sent_at: new Date().toISOString()
    };
}

// ============================================================================
// MESSAGE ROUTER
// ============================================================================

/**
 * Route message to appropriate channel handler
 */
async function sendMessage(messageData) {
    const { channel } = messageData;

    switch (channel) {
        case 'email':
            return await sendEmail(messageData);
        case 'sms':
            return await sendSMS(messageData);
        case 'whatsapp':
            return await sendWhatsApp(messageData);
        case 'push':
            return await sendPush(messageData);
        case 'voicemail':
            return await sendVoicemail(messageData);
        default:
            throw new Error(`Unsupported channel: ${channel}`);
    }
}

// ============================================================================
// DATABASE UPDATES
// ============================================================================

/**
 * Update lead status after message sent
 */
async function updateLeadStatus(leadId, status, messageData) {
    try {
        // Get current count first, then update
        const { data: currentLead } = await supabase
            .from('leads')
            .select('total_messages_sent')
            .eq('id', leadId)
            .single();
        
        const currentCount = currentLead?.total_messages_sent || 0;
        
        const { error } = await supabase
            .from('leads')
            .update({
                status,
                last_contact_date: new Date().toISOString(),
                total_messages_sent: currentCount + 1
            })
            .eq('id', leadId);

        if (error) {
            logger.error('Failed to update lead status', {
                lead_id: leadId,
                error: error.message
            });
        } else {
            logger.info('Lead status updated', {
                lead_id: leadId,
                status
            });
        }
    } catch (error) {
        logger.error('Update lead status error', {
            lead_id: leadId,
            error: error.message
        });
    }
}

/**
 * Log message to database
 */
async function logMessage(messageData, result) {
    try {
        const { error } = await supabase
            .from('messages')
            .insert({
                lead_id: messageData.lead_id,
                campaign_id: messageData.campaign_id,
                user_id: messageData.user_id,
                channel: messageData.channel,
                subject: messageData.subject,
                body: messageData.body || messageData.html || messageData.text,
                status: result.success ? 'sent' : 'failed',
                external_message_id: result.message_id,
                sent_at: result.sent_at,
                created_at: new Date().toISOString()
            });

        if (error) {
            logger.error('Failed to log message', {
                lead_id: messageData.lead_id,
                error: error.message
            });
        }
    } catch (error) {
        logger.error('Log message error', {
            lead_id: messageData.lead_id,
            error: error.message
        });
    }
}

// ============================================================================
// WORKER SETUP
// ============================================================================

const messageQueue = new Queue(QUEUE_NAME, {
    connection: REDIS_CONFIG
});

const worker = new Worker(
    QUEUE_NAME,
    async (job) => {
        const { data: messageData } = job;
        const { lead_id, channel, to } = messageData;

        logger.info('WORKER_JOB_START', {
            job_id: job.id,
            lead_id,
            channel,
            to,
            timestamp: new Date().toISOString()
        });

        try {
            // Send message
            const result = await sendMessage(messageData);
            
            // Log delivery success
            logger.info('WORKER_DELIVERY_SUCCESS', {
                job_id: job.id,
                lead_id,
                channel,
                to,
                message_id: result.message_id,
                sent_at: result.sent_at,
                timestamp: new Date().toISOString()
            });

            // Update lead status
            await updateLeadStatus(lead_id, 'campaign_active', messageData);

            // Log message to database
            await logMessage(messageData, result);

            logger.info('WORKER_JOB_SUCCESS', {
                job_id: job.id,
                lead_id,
                channel,
                success: true,
                message_id: result.message_id,
                timestamp: new Date().toISOString()
            });

            return result;
        } catch (error) {
            logger.error('Message job failed', {
                job_id: job.id,
                lead_id,
                channel,
                error: error.message,
                stack: error.stack,
                attempts: job.attemptsMade
            });

            // Update lead status on failure
            await updateLeadStatus(lead_id, 'campaign_error', messageData);

            // Re-throw to trigger retry
            throw error;
        }
    },
    {
        connection: REDIS_CONFIG,
        concurrency: parseInt(process.env.WORKER_CONCURRENCY || '10'),
        limiter: {
            max: parseInt(process.env.WORKER_MAX_JOBS || '100'),
            duration: 60000 // 1 minute
        },
        removeOnComplete: {
            age: 3600, // Keep completed jobs for 1 hour
            count: 1000 // Keep last 1000 completed jobs
        },
        removeOnFail: {
            age: 86400 // Keep failed jobs for 24 hours
        },
        settings: {
            // PRODUCTION-GRADE RETRY STRATEGY: Exponential backoff
            attempts: 5, // Retry up to 5 times
            backoff: {
                type: 'exponential',
                delay: 2000 // Start with 2 seconds, doubles each time (2s, 4s, 8s, 16s, 32s)
            }
        }
    }
);

// ============================================================================
// WORKER EVENT HANDLERS
// ============================================================================

worker.on('completed', (job) => {
    logger.info('Job completed', {
        job_id: job.id,
        lead_id: job.data.lead_id
    });
});

worker.on('failed', (job, err) => {
    logger.error('Job failed', {
        job_id: job.id,
        lead_id: job.data?.lead_id,
        error: err.message,
        attempts: job.attemptsMade
    });
});

worker.on('error', (err) => {
    logger.error('Worker error', {
        error: err.message,
        stack: err.stack
    });
});

// ============================================================================
// GRACEFUL SHUTDOWN
// ============================================================================

process.on('SIGTERM', async () => {
    logger.info('SIGTERM received, shutting down gracefully...');
    await worker.close();
    await messageQueue.close();
    process.exit(0);
});

process.on('SIGINT', async () => {
    logger.info('SIGINT received, shutting down gracefully...');
    await worker.close();
    await messageQueue.close();
    process.exit(0);
});

// ============================================================================
// STARTUP
// ============================================================================

logger.info('Rekindle Scheduler Worker starting...', {
    queue_name: QUEUE_NAME,
    redis_host: REDIS_CONFIG.host,
    redis_port: REDIS_CONFIG.port,
    concurrency: parseInt(process.env.WORKER_CONCURRENCY || '10')
});

logger.info('Worker started successfully');

