# Rekindle MVP - Performance-Only Pricing

**Ship tonight. Make money tomorrow.**

## Pricing Model
- £0 upfront
- £25 per booked meeting
- £0.10 per revived lead (replied with interest)

## Quick Start

### 1. Run Backend (MVP API)
```bash
cd backend
python mvp_api.py
```
API runs on http://localhost:3002

### 2. Run Frontend
```bash
npm run dev
```
Frontend runs on http://localhost:5174

### 3. Access MVP Console
Navigate to: http://localhost:5174/mvp

## MVP Workflow

### Step 1: Upload Leads CSV
- Click "Upload Leads CSV"
- Select CSV file (max 50 leads in demo mode)
- CSV format:
  ```
  name,email,company,phone,notes,last_contact
  John Doe,john@example.com,Acme Inc,+44...,Sales lead,2024-01-15
  ```
- Get batch_id

### Step 2: Generate Revival Messages
- Enter batch_id
- Select business type (generic, agency, real_estate, saas)
- Enter sender name and company name
- Click "Generate Messages"
- Copy first 3 sample messages
- **MANUALLY** send via Gmail/email client

### Step 3: Monitor Replies (Manual)
- Check your inbox
- For each reply, paste into "Paste Reply" form
- Enter lead email + message text
- Click "Classify Reply"
- System shows: interested/not_interested/unclear
- System suggests next action

### Step 4: Book Meetings (Manual)
- For qualified leads, send Calendly link manually
- Record booking in system (future feature)

### Step 5: Generate Report
- Enter batch_id
- Click "Generate Report"
- See metrics:
  - Leads contacted
  - Replies received
  - Interested count
  - Qualified count
  - Meetings booked
  - **Total fee in £GBP**

## API Endpoints

### POST /api/mvp/leads/upload
Upload CSV file
```bash
curl -X POST http://localhost:3002/api/mvp/leads/upload \
  -F "file=@leads.csv"
```

### POST /api/mvp/revival/start
Generate opener messages
```bash
curl -X POST http://localhost:3002/api/mvp/revival/start \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "abc123",
    "business_type": "saas",
    "sender_name": "Alice",
    "company_name": "Rekindle"
  }'
```

### POST /api/mvp/replies/ingest
Classify a reply
```bash
curl -X POST http://localhost:3002/api/mvp/replies/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "lead_email": "john@example.com",
    "message_text": "Yes, sounds interesting. Send me pricing",
    "batch_id": "abc123"
  }'
```

### POST /api/mvp/booking/create
Record booking attempt
```bash
curl -X POST http://localhost:3002/api/mvp/booking/create \
  -H "Content-Type: application/json" \
  -d '{
    "lead_email": "john@example.com",
    "meeting_type": "demo"
  }'
```

### GET /api/mvp/batches/{batch_id}/report
Get performance report with fees
```bash
curl http://localhost:3002/api/mvp/batches/abc123/report
```

## Skills System

Skills are located in `/skills/`:
- `opener_templates/` - Industry-specific message templates
- `reply_handling/` - Reply classification logic
- `qualification/` - Lead qualification rules
- `booking_rules/` - Meeting booking criteria
- `pricing/` - Fee calculation rules

### Using Skills in Code
```python
from rekindle_skills.loader import get_loader

loader = get_loader()

# Get opener template
template = loader.get_template('opener_templates', 'saas', variant=0)

# Fill placeholders
filled = loader.fill_template(template, {
    'name': 'John',
    'pain_point': 'lead gen'
})

# Get reply classification rules
rule = loader.get_rule('reply_handling', 'interested.send_qualifier')
```

## Manual Operations (MVP Phase)

### Email Sending
1. Generate messages via API
2. Copy message body + subject
3. Paste into Gmail compose
4. Send to lead email
5. Track in spreadsheet

### Reply Monitoring
1. Check inbox 2x per day
2. Copy reply text
3. Paste into /mvp console "Paste Reply" form
4. System classifies and suggests next action

### Meeting Booking
1. For qualified leads, copy your Calendly link
2. Send via email manually
3. Record booking in system

### Reporting
1. Generate report via API
2. Export CSV data
3. Email to client weekly

## Data Storage

MVP uses local JSON files in `backend/mvp_data/`:
- `batch_{batch_id}.json` - Lead batches and messages
- `replies.json` - All classified replies
- `bookings.json` - Meeting bookings

**No database required for MVP.**

## Limits

- Demo mode: 50 leads max per batch
- Internal mode: 5000 leads max (set flag in code)
- No rate limiting (add later)
- No authentication (mock auth works)

## Next Steps After Revenue

1. Add SendGrid integration for auto-sending
2. Add reply webhook from email provider
3. Add calendar integration for auto-booking
4. Migrate to real database (Supabase)
5. Add user authentication
6. Remove 50 lead limit

## Troubleshooting

**Backend won't start:**
```bash
pip install fastapi uvicorn python-multipart pydantic[email]
```

**Frontend can't reach backend:**
- Check backend is on port 3002
- Check CORS allows localhost:5174
- Update Vite proxy config if needed

**CSV upload fails:**
- Check CSV has headers: name,email
- Check email format is valid
- Check file size < 1MB

**Skills not loading:**
- Check `/skills/` directory exists
- Check JSON files are valid
- Check `rekindle_skills/loader.py` can import

## Production Deployment

**Backend:**
```bash
# Deploy to Railway/Render
# Set env: PRODUCTION=true
uvicorn mvp_api:app --host 0.0.0.0 --port 3002
```

**Frontend:**
```bash
# Deploy to Vercel
vercel --prod
# Update API URL in code to production backend
```

## Support

This is MVP code. It's meant to be ugly and fast.

If it makes money, we'll make it pretty.

If it doesn't, we'll pivot.

**Ship tonight. Iterate tomorrow.**
