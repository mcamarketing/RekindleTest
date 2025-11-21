# Rekindle Scheduler Worker

Production-grade BullMQ worker that sends messages via SendGrid (email), Twilio (SMS/WhatsApp), and other channels.

## Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Environment Variables**
   Create `.env` file:
   ```bash
   # Supabase
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=xxx

   # Redis
   REDIS_HOST=127.0.0.1
   REDIS_PORT=6379
   REDIS_PASSWORD=xxx
   REDIS_SCHEDULER_QUEUE=message_scheduler_queue

   # SendGrid
   SENDGRID_API_KEY=SG.xxx
   SENDGRID_FROM_EMAIL=noreply@rekindle.ai
   SENDGRID_UNSUBSCRIBE_GROUP_ID=12345

   # Twilio
   TWILIO_ACCOUNT_SID=ACxxx
   TWILIO_AUTH_TOKEN=xxx
   TWILIO_PHONE_NUMBER=+1234567890
   TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

   # Worker Config
   WORKER_CONCURRENCY=10
   WORKER_MAX_JOBS=100
   NODE_INSTANCE_ID=worker-001
   LOG_LEVEL=info
   NODE_ENV=production
   ```

3. **Start Worker**
   ```bash
   npm start
   ```

## Job Format

Jobs are added to the Redis queue with this format:

```javascript
{
    lead_id: "uuid",
    campaign_id: "uuid",
    user_id: "uuid",
    channel: "email|sms|whatsapp|push|voicemail",
    to: "email@example.com" or "+1234567890",
    from: "sender@example.com" (optional, for email),
    subject: "Subject line" (for email),
    body: "Message body",
    html: "<html>...</html>" (for email),
    text: "Plain text" (for email)
}
```

## Features

- ✅ Multi-channel support (email, SMS, WhatsApp, push, voicemail)
- ✅ Exponential backoff retries
- ✅ Structured logging (Winston)
- ✅ Database updates (lead status, message logging)
- ✅ Graceful shutdown
- ✅ Rate limiting
- ✅ Error handling

## Monitoring

Logs are written to:
- Console (all environments)
- `logs/worker-error.log` (production, errors only)
- `logs/worker-combined.log` (production, all logs)

## Production Deployment

Use PM2 or similar process manager:

```bash
pm2 start worker.js --name rekindle-worker
pm2 logs rekindle-worker
```








