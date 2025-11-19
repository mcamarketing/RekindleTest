# Rekindle: Product Requirements Document

**Version:** 1.0  
**Status:** ✅ APPROVED — Ready for Development  
**Build Stack:** Bolt.new (Frontend) → Cursor AI + Claude Code (Backend)  
**Timeline:** 4 weeks to MVP launch

---

## 🔥 Executive Summary

### What We're Building
**Rekindle** - AI that automatically revives your dead leads from 3-12 months ago.

**The Problem:** Every business has 100-500 dormant leads worth £20K-100K sitting in spreadsheets. They spent £2-5 each acquiring them, but never followed up because:
- It felt awkward ("It's been 6 months...")
- They didn't know what to say
- They were too busy

**Our Solution:** AI agents that score lead revivability, write empathetic messages acknowledging the time gap, send them at optimal times, and track replies — all for £0.02/lead.

**Brand Philosophy:** "Relationships don't expire. They just go quiet."

### Target Users
- **Solopreneurs:** 50-200 dormant leads in spreadsheets
- **Small agencies:** 200-500 "Closed-Lost" leads in HubSpot
- **SMB sales reps:** CRMs full of "No Response" leads

### Market Validation
- 73 survey responses: 89% have 100+ dormant leads
- 11 LOIs from agencies: £50K+ in dead pipeline
- Manual test: 11.2% revival rate (target: 10%)

---

## 🎯 Success Metrics (Month 3)

| Metric | Target |
|--------|--------|
| MRR | £3,000 |
| Users | 300 total (105 Pro, 10 Agency) |
| Activation | 50% send ≥10 messages in 7 days |
| Revival Rate | 10% (replies / messages sent) |
| Retention | 75% Month 1 → Month 2 |
| Operating Cost | <£50/month |
| Profit Margin | >95% |

---

## 💰 Pricing (INTELLIGENT VALUE-BASED: % of Your Lead Value)

**Philosophy:** We charge based on what YOUR leads are worth. Low monthly base, we win when you win.

**How It Works:**
1. You tell us your average deal value
2. We charge **2-3% of that** per meeting booked
3. Low monthly base keeps barrier to entry minimal

**Subscription Tiers:**

| Tier | Monthly Base | Per Meeting Booked | AI Lead Sourcing | Volume | What You Get |
|------|--------------|-------------------|------------------|---------|--------------|
| **Starter** | £19/mo | 3% of your lead value (min £5, max £50) | ❌ Not included | Up to 5K leads | Email + SMS + AI research |
| **Pro** | £99/mo | 2.5% of your lead value (min £8, max £150) | ✅ 100 leads/mo included, £0.10 each after | Up to 25K leads | All channels + Auto-ICP + Lead sourcing |
| **Enterprise** | £499/mo | 2% of your lead value (min £10, max £200) | ✅ 1,000 leads/mo included, £0.06 each after | Unlimited | White-label + dedicated infra + unlimited sourcing |

**Real Examples:**

**Example 1: Local Service Business (Plumber, HVAC)**
- Average job value: £500
- Starter tier: 3% = **£15 per meeting**
- 30 meetings booked = £19 + (30 × £15) = **£469/mo**
- Close rate 30% → 9 jobs × £500 = **£4,500 revenue**
- ROI: 9.6x
- Our revenue: £469 (mostly performance-based)

**Example 2: B2B SaaS (SMB Software)**
- Average deal value: £2,500/year
- Pro tier: 2.5% = **£62.50 per meeting** (capped at £75)
- 40 meetings booked = £99 + (40 × £62.50) = **£2,599/mo**
- Close rate 20% → 8 deals × £2,500 = **£20,000 revenue**
- ROI: 7.7x
- Our revenue: £2,599 (96% from performance)

**Example 3: Enterprise B2B (£50K deals)**
- Average deal value: £50,000
- Enterprise tier: 2% would be £1,000 (too high)
- **Capped at £150 per meeting** (0.3%)
- 25 meetings booked = £499 + (25 × £150) = **£4,249/mo**
- Close rate 15% → 4 deals × £50,000 = **£200,000 revenue**
- ROI: 47x
- Our revenue: £4,249 (88% from performance)

**Price Caps (Keeping It Fair):**
- Starter: £5 min, £50 max per meeting
- Pro: £8 min, £150 max per meeting  
- Enterprise: £10 min, £200 max per meeting

**Volume Discounts (Automatic):**
- 1-50 meetings: Standard rate
- 51-150 meetings: -10%
- 151-500 meetings: -20%
- 500+ meetings: -30%

**Why This Works:**
- ✅ Low barrier to entry (£19/mo to start)
- ✅ We make money when YOU make money
- ✅ Scales with YOUR business value
- ✅ Still cheaper than agencies (£50-200 per meeting)
- ✅ 96%+ of our revenue is performance-based

**Setup Process:**
1. During onboarding: "What's your average deal value?"
2. We calculate your per-meeting rate (2-3% with caps)
3. You approve the rate
4. Dashboard shows exact cost per meeting
5. No surprises, 100% transparent

**What Counts as a Meeting:**
- Calendar-confirmed appointment
- Minimum 15 minutes scheduled
- Lead shows up (no-shows = free retry)
- Tracked via calendar integration (Calendly, Google Calendar, etc.)

---

## 🤖 Auto-ICP + AI Lead Sourcing (Pro & Enterprise Only)

**The Problem:** You revive dead leads, book meetings, close deals. Then what? Where do you find MORE people just like them?

**The Solution:** After 25 successful revivals, Rekindle's AI automatically:
1. Analyzes your best leads (who replied, who booked meetings)
2. Extracts your Ideal Customer Profile (ICP): industry, company size, job titles, geography
3. Sources fresh leads matching this profile using our proprietary scraper
4. Enriches and verifies them (email validation, company research)
5. Injects them into your revival pipeline automatically

**Completely hands-off. Zero manual work.**

### How It Works (User Experience)

**Step 1: Revival Success Triggers Auto-ICP**
```
After 25 meetings booked:

┌────────────────────────────────────────┐
│ 🎯 AUTO-ICP DETECTED                   │
│                                        │
│ Your best leads look like:             │
│ • Industry: B2B SaaS                   │
│ • Company size: 10-50 employees        │
│ • Titles: Head of Growth, VP Marketing │
│ • Geography: UK, Ireland               │
│                                        │
│ Confidence: 87%                        │
│                                        │
│ [Edit ICP] [Start Auto-Sourcing] ✓    │
└────────────────────────────────────────┘
```

**Step 2: AI Sources Fresh Leads**
- Scrapes public sources (company websites, directories, job boards)
- Finds 100-1,000 leads matching your ICP
- Validates emails (80%+ verification rate)
- Enriches with company data, funding news, tech stack
- Scores each lead 0-100 for match quality

**Step 3: Auto-Queue for Revival**
```
┌────────────────────────────────────────┐
│ 📬 NEW LEADS READY                     │
│                                        │
│ We found 87 leads matching your ICP:   │
│ • 62 High-score (80+ match)            │
│ • 25 Medium-score (60-79 match)        │
│                                        │
│ Ready to launch revival campaign?      │
│ [Auto-Run] [Review First]              │
└────────────────────────────────────────┘
```
- Default: AUTO-RUN (hands-off)
- AI generates personalized messages for each lead
- Multi-channel sequence starts immediately
- You get notified when meetings are booked

### Pricing (AI Lead Sourcing)

**Pro Tier:**
- 100 AI-sourced leads/month **included**
- £0.10 per verified lead beyond quota
- Example: Need 150 leads? Pay £99 + (50 × £0.10) = £104/mo

**Enterprise Tier:**
- 1,000 AI-sourced leads/month **included**
- £0.06 per verified lead beyond quota
- Example: Need 2,000 leads? Pay £499 + (1,000 × £0.06) = £559/mo

**What You Pay For:**
- Only verified leads (email validated + enriched)
- Raw scrapes don't count
- Duplicates don't count
- Dashboard shows: "87 leads sourced → 71 verified → £7.10 charged"

### Sources We Use (Public Data Only)

✅ **Company websites** (career pages, team pages, press releases)
✅ **Public directories** (Crunchbase, Product Hunt, AngelList)
✅ **Job boards** (Indeed, LinkedIn Jobs public listings)
✅ **GitHub** (for developer tools/APIs)
✅ **Industry publications** (trade magazines, conference attendees)
⚠️ **LinkedIn profiles** (Phase 2, via official API with legal review)

**Compliance:**
- Respect robots.txt on all domains
- GDPR opt-out mechanism
- Suppression lists enforced
- Audit log for every sourced lead
- No aggressive scraping (5-second delays minimum)

### Why This is a Game-Changer

**Traditional lead generation:**
- Buy lists: £2-5 per lead (low quality)
- Hire SDR: £3,000-5,000/month + commission
- Use agency: £50-200 per meeting booked
- Manual research: 20-30 leads/day max

**Rekindle Auto-ICP:**
- Cost: £0.10 per verified lead (20-50x cheaper)
- Quality: Matches YOUR successful leads (not generic list)
- Speed: 100+ leads/day automatically
- Effort: Zero (completely hands-off after initial approval)

### Affiliate Marketplace (Hidden Feature)

**When sourced leads become customers:**
- AI sources lead → Revival campaign → They book meeting → They buy from you
- Some of those leads later sign up for Rekindle themselves
- **You get affiliate commission automatically**
- Pro users: 10% of their payments for 12 months
- Enterprise users: 20% of their payments for lifetime

**Example:**
- You source 1,000 leads over 6 months
- 5 of them become Rekindle customers (0.5% conversion)
- They pay avg £2,500/mo
- Your affiliate earnings: £1,250/mo passive income

**This creates a marketplace effect:**
- Best users (who close deals) source the best leads
- Those leads become customers and source MORE leads
- Network effects compound
- Everyone makes money

---

## 🏗️ System Architecture

```
USER (Bolt.new React UI)
  ↓ REST API
BACKEND (Cursor AI - Node.js + Python)
  ├─ Express.js API (auth, CRUD, webhooks)
  ├─ CrewAI Agents:
  │   ├─ Qualifier (scores revivability)
  │   ├─ Writer (generates messages via Claude API)
  │   ├─ Scheduler (sends emails, staggered timing)
  │   └─ Tracker (detects replies, sentiment analysis)
  ├─ Redis (job queue)
  └─ PostgreSQL (users, leads, messages)
  
EXTERNAL:
  ├─ Claude API (Sonnet 4.5) - £15/mo for 300 users
  ├─ Gmail API (user's email for sending)
  ├─ Stripe (subscription billing)
  └─ Google Sheets OAuth
```

---

## 🚀 4-Week Development Plan

### Week 1: Foundation (Bolt.new + Cursor Setup)
- **Bolt.new:** Landing page + onboarding wizard (4 steps)
- **Cursor:** Express.js API + PostgreSQL schema + auth (JWT)
- **Deliverable:** User can register, login, see empty dashboard

### Week 2: AI Agents (Cursor + Claude Code)
- **Qualifier Agent:** Score leads 0-100 (High/Medium/Low)
- **Writer Agent:** Generate personalized messages
- **Bolt.new:** Lead import (CSV upload) + field mapping UI
- **Deliverable:** Import leads → See revivability scores → Preview messages

### Week 3: Email Sending + Reply Tracking
- **Scheduler Agent:** Redis queue + Gmail API integration
- **Tracker Agent:** Inbound webhook + sentiment analysis
- **Bolt.new:** Complete dashboard (charts, hot leads table)
- **Deliverable:** End-to-end flow works (import → send → reply → notification)

### Week 4: Stripe + Polish + Beta Launch
- Stripe checkout + plan limits enforcement
- QA testing (50+ test cases)
- UI polish (loading states, animations)
- **Friday:** Beta launch with 20-30 users

---

## 📋 Core User Journey (10 Minutes)

1. **Sign-up** (30s): Email + password → No credit card
2. **Import leads** (2m): Upload CSV with 187 leads
3. **Lead age filter** (30s): System shows 162 qualify (30-365 days old)
4. **Revivability scoring** (45s): AI scores → 47 High, 89 Medium, 26 Low
5. **Message preview** (3m): AI generates samples → User approves
6. **Campaign launches** (1m): "47 emails sending over 48 hours"
7. **Dashboard:** Real-time counter shows messages sent

**Within 24-48 hours:** Leads start replying → User gets notifications 🔥

---

## 🤖 CrewAI Agent Specs

### Agent 1: Researcher (Lead Intelligence Agent) 🆕
**Input:** Lead (name, email, company, last_contact_date, notes)  
**Process:**
- Search LinkedIn profile (job title, recent posts, career changes)
- Scrape company website (recent news, product launches, funding)
- Check company LinkedIn (hiring, expansions, announcements)
- Search Google News for company mentions (last 90 days)
- Analyze tech stack (BuiltWith, similar tools)
- Compile "revival hooks" (budget refresh, new role, competitor issues, seasonal timing)
**Output:** {
  "current_role": "VP Marketing",
  "company_news": "Just raised Series B ($12M)",
  "pain_points": ["Scaling issues", "Team hiring"],
  "revival_hooks": ["New budget available", "Expanding marketing team"],
  "best_channel": "LinkedIn + Email"
}
**Performance:** 50 leads in ~2 minutes (parallel API calls)

### Agent 2: Qualifier (Revivability Scorer)
**Input:** Lead + Research data  
**Process:** 
- Calculate lead age: Today - last_contact_date
- Analyze notes quality (specific context vs. generic)
- Factor in research insights (job change = +30 points, funding = +20)
- Call Claude API: "Score this lead's revivability considering recent company funding..."
**Output:** {score: 92, tier: "High", reason: "Company raised funding 30 days ago, lead promoted to decision-maker"}  
**Performance:** 162 leads in <45 seconds

### Agent 3: Writer (Multi-Channel Message Generator) 🆕
**Input:** Lead + Research data + Channel (email/sms/whatsapp/push/voicemail script)  
**Process:**
- Analyze research: Extract top 2-3 revival hooks
- Determine optimal channel based on:
  - Lead preferences (if known)
  - Message urgency
  - Relationship warmth (cold = email, warm = SMS/WhatsApp)
- Call Claude API: "Write a personalized revival message using these hooks: [funding news, new role]. Channel: Email. Tone: Congratulatory..."
**Output:** 
```json
{
  "channel": "email",
  "subject": "Congrats on the Series B, Sarah!",
  "body": "Hi Sarah, Saw the exciting news about your £12M raise...",
  "fallback_channel": "linkedin",
  "alternative_sms": "Hi Sarah! Congrats on Series B 🎉 That website project we discussed..."
}
```
**Quality:** Includes specific, researched details (not generic)

### Agent 4: Scheduler (Multi-Channel Sender)
**Input:** Messages + optimal send times  
**Process:**
- **Email:** Send via Gmail API or SMTP (staggered)
- **SMS:** Send via Twilio API (immediate for warm leads)
- **WhatsApp:** Send via Twilio WhatsApp API (requires opt-in)
- **Push Notification:** Send via OneSignal (if lead installed your app)
- **Voicemail:** Drop pre-recorded message via Slybroadcast API
- Prioritize channels: Try email first → If no open in 48h, send SMS → If no reply, try WhatsApp
- Track delivery status per channel
**Output:** Multi-channel sequence executed over 5-7 days

### Agent 4: Tracker (Reply Monitor)
**Input:** Inbound email to reply-abc123@rekindle.ai  
**Process:**
- Match sender to lead in database
- Call Claude API: "Analyze sentiment + intent..."
- Update lead: Dormant → Revived
- Notify user (email + in-app)
**Output:** {sentiment: "Positive", intent: "Meeting Request"}

---

## 💾 Database Schema (PostgreSQL)

```sql
-- Core tables
users (id, email, password_hash, plan_tier, stripe_customer_id)
leads (id, user_id, email, name, company, last_contact_date, 
       lead_age_days, revivability_score, revivability_tier,
       notes, status, sentiment, intent)
campaigns (id, user_id, name, status, messages_sent, replies_received, revival_rate)
messages (id, campaign_id, lead_id, subject, body, scheduled_send_time, sent_at, status)
interactions (id, lead_id, message_id, type, content, sentiment, timestamp)
suppression_list (id, email, reason, added_at)
```

---

## 🎨 UI Components (Bolt.new Generates These)

**Landing Page:**
- Hero: "You spent £5,000 acquiring those leads. They went cold. What if they're ready now?"
- CTA: "Revive Your First 50 Leads Free"
- Color: Warm gradient (#FF6B35 → #F7931E)
- Font: Inter

**Onboarding Wizard (4 Steps):**
1. Import leads (drag-drop CSV, Google Sheets button)
2. Lead age filter (visual distribution chart)
3. Revivability scoring (progress bar: "Analyzing... 162/162")
4. Message preview (3 samples, Approve/Regenerate buttons)

**Dashboard:**
- Hero metrics: 4 cards (Leads in Revival, Messages Sent, Replies, Revival Rate %)
- Charts: Revival rate trend (line) + Lead status (pie)
- Hot Leads table: Name | Company | Replied | Sentiment | [Reply] button
- Recent Activity feed

**Key Components:**
- `<CSVUploadModal>` - Drag-drop with field mapping
- `<RevivabilityCard>` - Score badge (🔥 High / 🟡 Medium / 🔵 Low)
- `<MessagePreview>` - Subject + body + Approve/Edit/Regenerate
- `<MetricCard>` - Big number + WoW change indicator
- `<NotificationPanel>` - Real-time reply alerts

---

## 🔧 Development Commands

### Bolt.new Prompts

**1. Start Here:**
```
Create a landing page for Rekindle - an AI tool that revives dead leads.

Hero message: "You spent £5,000 acquiring those leads. They went cold. What if they're ready now?"

Sections:
- Hero with CTA "Revive Your First 50 Leads Free"
- Problem (leads going cold costs businesses £50K)
- Solution (AI agents that score, write, send, track)
- Pricing table (Free/Pro/Agency)
- Testimonials
- FAQ

Design:
- Warm gradient background (#FF6B35 to #F7931E)
- Inter font
- Modern, clean, professional
- Mobile responsive
```

**2. Then Build Onboarding:**
```
Create a 4-step onboarding wizard for Rekindle:

Step 1: Import Leads
- Drag-drop CSV upload
- Google Sheets connect button (OAuth)
- Show first 5 rows preview
- Field mapping (auto-detect: Name, Email, Last Contact Date, Notes)

Step 2: Lead Age Filter
- Display distribution chart (0-30, 30-90, 90-180, 180-365, 365+ days)
- Show how many in each bucket
- "162 leads qualify (30-365 days old)"

Step 3: Revivability Scoring
- Progress bar: "Analyzing revivability... 162/162"
- Results: 47 High (🔥), 89 Medium (🟡), 26 Low (🔵)
- "Start with High Only" or "Include All" buttons

Step 4: Message Preview
- Show 3 AI-generated sample messages
- Each with Subject + Body
- Buttons: Approve All | Edit Tone | Regenerate

Use TailwindCSS, warm color scheme, smooth transitions.
```

**3. Then Dashboard:**
```
Create analytics dashboard for Rekindle:

Top: 4 metric cards (grid)
- Leads in Revival: 47
- Messages Sent: 12/47 (progress bar)
- Replies: 6
- Revival Rate: 12.8% (green if >10%, gray if <10%)

Middle: 2 charts side-by-side
- Line chart: Revival rate trend (last 7 days)
- Pie chart: Lead status (Dormant, Revived, Opted Out, Bounced)

Bottom: Hot Leads table
- Columns: Name | Company | Replied | Sentiment (emoji) | Action
- Sortable, filterable
- [Reply in Gmail] button per row

Right sidebar: Notification panel
- Badge: "3 new replies"
- List: Recent replies with timestamps

Use Recharts for charts, real-time WebSocket updates.
```

### Cursor AI Prompts (Claude Code)

**1. Backend Foundation:**
```
Create Express.js API for Rekindle with:

Features:
- User auth (JWT + refresh tokens, bcrypt passwords)
- CRUD for leads, campaigns, messages
- Prisma ORM + PostgreSQL
- Rate limiting on auth
- Error handling middleware

Database schema:
users: id, email, password_hash, business_name, plan_tier, stripe_customer_id, created_at
leads: id, user_id, email, name, company, last_contact_date, lead_age_days, 
       revivability_score, revivability_tier, notes, status, sentiment, created_at
campaigns: id, user_id, name, status, total_leads, messages_sent, replies_received
messages: id, campaign_id, lead_id, subject, body, scheduled_send_time, sent_at, status
interactions: id, lead_id, message_id, type, content, sentiment, timestamp
suppression_list: id, email, reason, added_at

Endpoints:
POST /auth/register
POST /auth/login
POST /auth/refresh
GET /leads
POST /leads/import (accepts CSV file or Google Sheets URL)
GET /campaigns
POST /campaigns
POST /api/agents/qualify-leads
POST /api/agents/generate-messages
POST /api/webhooks/inbound-email
POST /api/webhooks/stripe

Include Prisma migrations.
```

**2. Qualifier Agent:**
```
Create Python CrewAI Qualifier Agent that scores lead revivability:

Input: Array of lead objects [{id, name, email, last_contact_date, notes}]

Process:
1. For each lead, calculate lead_age_days = today - last_contact_date
2. Analyze notes quality (length, specific keywords like "pricing", "Q4")
3. Call Claude API (Anthropic SDK) with prompt:

"Score this lead's revivability (0-100):
Lead: {name} at {company}
Last Contact: {lead_age_days} days ago
Notes: {notes}

Scoring criteria:
- 30-90 days ago: +30 points (optimal window)
- 90-180 days: +15 points
- 180-365 days: +5 points
- Has specific context in notes: +25 points
- Notes empty or generic: +0 points
- Company appears active: +10 points

Return JSON: {\"score\": 85, \"tier\": \"High\", \"reason\": \"Strong candidate - engaged 90 days ago with budget discussion\"}"

4. Parse response, update lead records with score + tier
5. Return summary: {high: 47, medium: 89, low: 26}

Performance: Batch 10 leads per API call, process 162 leads in <45 seconds.
Error handling: If Claude API fails, use rule-based fallback (age + notes length).

Use Anthropic Python SDK, async/await for speed.
```

**3. Writer Agent:**
```
Create Python CrewAI Writer Agent that generates revival messages:

Input: Lead object + user_profile {business_name, value_prop} + tone ("Professional"/"Friendly"/"Direct")

Process:
1. Calculate time_gap_human: e.g., "about 6 months" from last_contact_date
2. Extract key context from notes field
3. Call Claude API with prompt:

"Write a revival email for this lead:

Lead: {name} at {company}
Last spoke: {time_gap_human} ago ({last_contact_date})
Original context: {notes}
Your business: {user_business} - {value_proposition}
Tone: {tone}

Requirements:
1. Acknowledge time gap naturally (\"I know it's been {time_gap}...\")
2. Reference specific context from notes if available
3. Offer fresh reason to reconnect:
   - Budget may have refreshed
   - New quarter started
   - You helped similar clients recently
4. Keep conversational, not salesy
5. Soft CTA: \"Would you be open to...\" or \"What do you think?\"
6. Length: 100-150 words exactly
7. Subject line: 40-60 chars, reference original topic

Output JSON:
{
  \"subject\": \"Re: [topic] we discussed in [month]\",
  \"body\": \"Hi {name},\\n\\n[personalized message]\\n\\nBest,\\n[User Name]\"
}"

4. Parse response, validate (length, personalization present)
5. If quality check fails, regenerate or use fallback template
6. Store in messages table with status='pending'

Return: {subject, body}

Include 3 fallback templates for High/Medium/Low revivability if API fails.
Use async batch processing (10 leads/call).
```

**4. Scheduler + Tracker Agents:**
```
Create two Node.js services:

SCHEDULER AGENT:
- Uses Bull.js + Redis for job queue
- Endpoint: POST /api/campaigns/:id/launch
- Process:
  1. Get all pending messages for campaign
  2. Calculate staggered schedule:
     - 1 email per hour
     - Only weekdays 9 AM - 5 PM (user timezone)
     - Spread over 48 hours
  3. Create Redis jobs: {lead_id, message_id, scheduled_time}
  4. Cron (every 5 min): Process due jobs
     - Send via Gmail API (user's OAuth token)
     - Log sent_at timestamp
     - Update dashboard via WebSocket
  5. Error handling:
     - OAuth expired: Pause, notify user
     - Rate limit: Retry after 15 min
     - Bounce: Mark lead status='Bounced'

TRACKER AGENT:
- Webhook endpoint: POST /api/webhooks/inbound-email
- Process:
  1. Parse inbound email (from, subject, body)
  2. Match sender email to lead in database
  3. Call Claude API:
     "Analyze this reply:
      Original: {original_message}
      Reply: {reply_body}
      
      Return JSON: {
        \"sentiment\": \"Positive\" | \"Neutral\" | \"Negative\" | \"Opt-Out\",
        \"intent\": \"Meeting Request\" | \"Question\" | \"Interested\" | \"Not Interested\" | \"Out of Office\",
        \"reason\": \"Brief explanation\"
      }"
  4. Update lead: status='Revived', sentiment, intent, last_reply_at
  5. If sentiment='Opt-Out': Add to suppression_list
  6. Send notification:
     - WebSocket: {type: 'new_reply', lead_id}
     - Email to user: "🔥 Sarah replied!"
  7. Forward reply to user's actual inbox

Include auto-reply detection (X-Autoreply header).
```

**5. Stripe Integration:**
```
Add Stripe subscription billing to Express.js API:

Endpoints:
POST /api/stripe/create-checkout-session
- Creates Stripe Checkout for Pro (£19/mo) or Agency (£79/mo)
- Returns checkout URL

POST /api/webhooks/stripe
- Handles events:
  - customer.subscription.created: Update user plan_tier='pro'
  - customer.subscription.updated: Handle upgrades/downgrades
  - customer.subscription.deleted: Revert to plan_tier='free'
  - invoice.payment_failed: Send dunning email

Middleware: checkPlanLimits
- Free: 50 revivals/month, 1 campaign
- Pro: 500 revivals/month, 5 campaigns
- Agency: 2,500 revivals/month, unlimited campaigns
- Block requests if limit exceeded, return 402 Payment Required

Use Stripe Node SDK, verify webhook signatures.
Environment variables: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
```

---

## ✅ Testing Checklist (Week 4)

**Critical Path (Must Work):**
- [ ] User registers with email + password
- [ ] User uploads CSV with 162 leads
- [ ] System excludes leads <30 days and >365 days old
- [ ] Qualifier Agent scores 162 leads in <45 seconds
- [ ] Scores are accurate (manual review 10 samples)
- [ ] Writer Agent generates 47 messages in <15 seconds
- [ ] Messages are personalized (name + context)
- [ ] Messages are 100-150 words
- [ ] User approves messages
- [ ] Scheduler queues 47 jobs in Redis
- [ ] Messages send via Gmail API (not all at once)
- [ ] Test reply to reply-abc123@rekindle.ai triggers Tracker
- [ ] Tracker correctly classifies sentiment ("Positive")
- [ ] User receives in-app + email notification
- [ ] Dashboard updates in real-time (WebSocket)
- [ ] Opt-out reply adds to suppression list
- [ ] Stripe checkout upgrades user to Pro
- [ ] Plan limits enforced (51st revival blocked for free user)

**Edge Cases:**
- [ ] CSV missing email column → Error message
- [ ] All leads too recent → Warning
- [ ] Claude API timeout → Fallback template used
- [ ] Gmail OAuth expired → Prompt re-auth
- [ ] Email bounce → Lead marked 'Bounced'
- [ ] Out-of-office auto-reply → Ignored (not counted as reply)

---

## 🚀 Launch Day Checklist

**Friday Morning:**
- [ ] Merge to main, deploy to production
- [ ] Smoke test: Register → Import → Send → Reply
- [ ] Switch Stripe to live mode

**Friday Afternoon:**
- [ ] Send beta invites (30 users)
- [ ] Post on Product Hunt (12:01 AM PST)
- [ ] Tweet launch
- [ ] Post Indie Hackers + Reddit r/SaaS

**Monitor:**
- [ ] Error logs (Sentry)
- [ ] Sign-ups (goal: 20-30 in 24h)
- [ ] User feedback (email, Intercom)

---

## 📊 Week-by-Week Milestones

**Week 1 Success:**
- Landing page live
- User can register/login
- Dashboard shows empty state

**Week 2 Success:**
- User can import 162 leads
- See revivability scores (47 High)
- Preview AI-generated messages

**Week 3 Success:**
- User can launch campaign
- Messages send over 48 hours
- Dashboard shows real-time updates
- Reply triggers notification

**Week 4 Success:**
- Stripe checkout works
- 50+ tests pass
- 20-30 beta users active
- Product Hunt launch

---

## 💡 Key Insights for Builders

**Why This Will Work:**
1. **Real Pain:** Every business has dead leads (validated: 73 surveys)
2. **Immediate ROI:** £0.02/lead revival vs. £2-5 new acquisition
3. **Emotional Hook:** "Relationships don't expire" beats cold outreach tools
4. **Ultra-Lean:** £45/month costs, 98% margins
5. **Fast Build:** Claude Code writes everything, 4 weeks total

**Why This Will Fail If:**
- Revival rate <5% (AI messages too generic)
- Deliverability <90% (emails in spam)
- Activation <30% (onboarding too complex)
- We take >6 weeks (competitors launch first)

**The Edge:**
- **Niche focus:** We own "revival," they do "cold outreach"
- **Speed:** 4 weeks to market vs. their 6 months
- **Cost:** £19/mo vs. their £59/mo
- **Brand:** Warm, human vs. their aggressive, sales-y

---

## 🎯 First 100 Users Strategy

**Week 1-2 (Beta):**
- 30 users from LOI list
- Goal: 50% send ≥10 messages
- Daily feedback calls

**Week 3-4 (Private Alpha):**
- Invite 50 more from waitlist
- Iterate based on Week 1-2 feedback
- Testimonial videos

**Week 5-8 (Public Launch):**
- Product Hunt launch
- £500 Google Ads test
- Content: "How to revive dead leads" (SEO)
- Goal: 100 total users, 15 paid

---

## END OF PRD

**Status:** ✅ Ready for Development

**Next Steps:**
1. Open **Bolt.new** → Paste landing page prompt
2. Open **Cursor AI** → Paste backend foundation prompt
3. Ship in 4 weeks
4. Revenue in 6 weeks

**Remember:** Simple beats perfect. Launch fast. Iterate based on real users.

Now go build Rekindle. 🔥

---

**Questions? Contact:** [Your Email]  
**GitHub:** [Repo Link - Create After Week 1]  
**Figma:** [Design Link - Create Week 1]
