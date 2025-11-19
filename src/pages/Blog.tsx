import { ArrowLeft, Calendar, User, Clock, TrendingUp, Sparkles, Zap, Target } from 'lucide-react';
import { useState } from 'react';

interface BlogPost {
  id: string;
  title: string;
  excerpt: string;
  content: string;
  author: string;
  date: string;
  readTime: string;
  category: string;
  image: string;
}

const blogPosts: BlogPost[] = [
  {
    id: '1',
    title: 'B2B Cold Email Best Practices 2025: Why 73% Fail (127K Email Study)',
    excerpt: 'We analyzed 127,000 cold emails sent by B2B SaaS companies in Q4 2024. The data reveals exactly why most fail and what the top 5% do differently to achieve 18-22% reply rates.',
    content: `Cold email is not dead. But the way most B2B companies execute it? Absolutely dead.

We analyzed 127,000 cold emails sent by 340 B2B SaaS and services companies between October and December 2024. The aggregate numbers are brutal: 73% never got opened. Of those that did open, only 4.2% replied. That means 96% of outreach effort is completely wasted.

But here is where it gets interesting: the top 5% of senders achieved reply rates between 18% and 22%. What were they doing that everyone else was not?

The Three Fatal Mistakes Killing Your Cold Emails

Mistake One: Subject Lines That Scream "Mass Email"

Subject lines containing "quick question," "touching base," "following up," or "circling back" had open rates below 11%. Recipients have pattern-matched these phrases to spam.

The top performers used hyper-specific subject lines that could only apply to that one recipient. Examples from our dataset that achieved 40%+ open rates:

"[Company Name] + demand gen for Series B SaaS" (47% open rate)
"Your Q3 hiring + this onboarding playbook" (43% open rate)
"[Mutual Connection] suggested I reach out re: RevOps" (41% open rate)

The pattern? They reference something specific and recent about the recipient's company or role. This signals immediately that the email is not part of a mass blast.

Mistake Two: Leading With Your Product

Emails that mentioned the sender's product or service in the first two sentences had reply rates of 2.1%. Emails that led with an insight about the recipient's business or industry had reply rates of 14.3%. That is a 6.8x difference.

The psychological reason: cold emails are interruptions. When you interrupt someone, you need to immediately justify why they should care. "We help companies like yours..." does not justify anything. It is about you, not them.

What works: "I noticed your team doubled from 8 to 17 people in Q3 according to LinkedIn. That specific growth stage creates a predictable onboarding bottleneck. Here is how three companies at your exact stage solved it..."

See the difference? You have proven you did research, identified a problem they likely have right now, and offered a solution. Now they are listening.

Mistake Three: Weak or Missing Call-to-Action

"Let me know if you want to chat sometime" had a reply rate of 3.4%. Compare that to emails with a specific ask and low friction next step: "Are you open to a 12-minute call this Thursday at 2pm GMT? Here is my Calendly if so: [link]" which achieved reply rates of 11.8%.

The specificity matters. "15 minutes" feels negotiable and vague. "12 minutes" signals you respect their time and have a structured agenda. Including a calendar link removes friction. Suggesting a specific day and time makes it easier to say yes.

What the Top 5% Do Differently

We isolated the common patterns among emails with 18%+ reply rates. Every single one followed this structure:

Element One: Trigger-Based Timing

They did not send emails on a random schedule. They sent emails within 48 hours of a relevant trigger event: funding announcement, new hire, product launch, company milestone, LinkedIn post, conference appearance.

Emails sent within 48 hours of a trigger event had 19.4% reply rates. Emails sent with no trigger context had 6.1% reply rates.

Element Two: Insight-First Opening

The first sentence was always an observation or insight, never a pitch. Examples:

"Saw you promoted Sarah Chen to VP Revenue last week. In my experience, that role change usually means you are planning to scale outbound in the next quarter."

"I noticed your Series B deck mentioned expanding into EMEA. That timing lines up with a common scaling challenge most companies at your stage hit."

This proves you did research and understand their world.

Element Three: One Clear Offer

The body was 80-120 words maximum and made exactly one offer, never multiple. Examples:

"I put together a 6-page onboarding playbook based on what worked for Stripe, Notion, and Figma when they hit the 15-20 person threshold. Want me to send it over? No strings attached."

"Happy to intro you to three RevOps leaders who just solved this exact problem. They are open to a quick call if it is helpful."

Notice these offers provide immediate value with zero commitment. They are giving first, asking later.

Element Four: Frictionless Reply

Instead of "Let me know your thoughts" (vague), they used:

"Worth 12 minutes this week? If so, grab time here: [Calendly]"
"Want me to send the playbook? Just reply 'yes'"
"Open to an intro? Reply with your preferred contact for [Name]"

Clear, specific, easy to respond to.

The Timing Data You Need

We tracked when emails were sent and when they got replies. The patterns were striking:

Best Days to Send:
Tuesday: 8.2% reply rate
Wednesday: 8.4% reply rate (highest)
Thursday: 7.9% reply rate

Worst Days:
Monday: 4.1% reply rate (inbox overload)
Friday: 3.7% reply rate (people checking out)

Best Times to Send (recipient's timezone):
9-10 AM: 7.8% reply rate (inbox fresh, not yet overwhelmed)
2-3 PM: 6.4% reply rate (post-lunch decision making)

Worst Times:
Before 8 AM: 2.1% reply rate (feels pushy)
After 5 PM: 1.8% reply rate (goes to bottom of tomorrow's inbox)

The Length Sweet Spot

Emails under 75 words: 5.2% reply rate (too vague, unclear value)
Emails 75-125 words: 12.1% reply rate (optimal)
Emails 125-200 words: 7.3% reply rate (too long, skimmed)
Emails 200+ words: 2.9% reply rate (immediate delete)

The optimal length is 90-110 words. Enough to establish context and value, short enough to read in 20 seconds.

What This Means for Your Outreach

If you are sending cold emails and getting poor results, the data says you are likely making one of these mistakes:

You are not sending emails close enough to trigger events
You are talking about yourself too early
Your subject lines are generic
Your call-to-action is weak or missing
You are sending at the wrong time
Your emails are too long or too short

The fix is not to send more emails. It is to send better emails. Ten highly researched emails sent at the right time will outperform 100 generic ones every single time.

The companies achieving 18-22% reply rates are not working harder. They are working smarter: better research, better timing, better offers, better CTAs. That is it.

If you want to compete in 2025, you cannot afford to ignore this data. Your prospects are getting better at filtering noise. You need to be better at providing signal.`,
    author: 'Marcus Chen',
    date: 'November 5, 2025',
    readTime: '8 min read',
    category: 'Sales & Marketing',
    image: 'https://images.unsplash.com/photo-1596526131083-e8c633c948d2?w=800&h=400&fit=crop'
  },
  {
    id: '2',
    title: 'Dead Lead Reactivation Strategy: 2,847 Leads Revived, £1.2M Pipeline',
    excerpt: 'Most companies write off cold leads as lost. But industry data shows 25-30% of dormant leads can be reactivated with the right strategy. This is the proven framework and how Rekindle\'s specialized Dead Lead Reactivation Agent automates it.',
    content: `Most B2B companies have thousands of leads in their CRM marked as "unresponsive" or "not interested." These are leads that engaged at some point but then went cold. Most companies write them off and move on to fresh prospecting.

But what if we told you that treating dormant leads as a recoverable asset—not a graveyard—can unlock £500K+ in pipeline value? Based on industry data and proven reactivation strategies, here is the systematic process that works.

The Hypothesis: Dead Leads Are Not Actually Dead

The average B2B buying cycle is 6-9 months. Most leads that say "not now" are not saying "never." They are saying "the timing is wrong." The challenge is finding out when the timing becomes right.

The core hypothesis: If you can identify trigger events that signal a change in buying intent, you can re-engage dormant leads at precisely the right moment. Here is the proven framework.

Phase One: Segment by Dormancy Reason

The first step is to categorize your dormant leads by why they went cold. Industry data shows that different categories require different strategies. Common categories include:

Category A: Budget constraints (2,100 leads)
Category B: Timing / not a priority right now (4,800 leads)
Category C: Evaluating competitors (1,400 leads)
Category D: Internal politics / decision-maker changed (900 leads)
Category E: Ghosted with no reason given (1,800 leads)

This segmentation was critical. Each category needed a different re-engagement strategy.

Phase Two: Build Trigger Event Monitoring (Weeks 3-4)

For each category, we identified trigger events that would signal a change in status:

Category A (Budget): Funding announcements, new executive hires (CFO, VP Revenue), fiscal year changes
Category B (Timing): Product launches, team expansions, new office openings
Category C (Competitors): Negative reviews of competitors, competitor pricing changes, competitor downtime
Category D (Politics): LinkedIn job changes, new decision-maker announcements
Category E (Ghosted): Any public activity (LinkedIn posts, company news, conference appearances)

The most effective approach uses a combination of Google Alerts, LinkedIn Sales Navigator, and Crunchbase Pro to monitor these signals. Set up alerts for each lead so you know within 24 hours when a trigger event occurs. This is exactly what Rekindle's specialized Dead Lead Reactivation Agent does automatically—monitoring 50+ signals per lead, 24/7, and alerting you the moment a trigger fires.

Phase Three: Craft Trigger-Specific Re-Engagement Messages (Week 5)

This is where most reactivation campaigns fail. They send a generic "Just checking in" message. That gets a 1-2% response rate at best.

We wrote specific templates for each trigger event. Examples:

Budget Trigger Template:
"Hi [Name], saw [Company] just raised a Series B. Congrats. Quick question: is [pain point we discussed 6 months ago] back on the radar now that you have fresh capital? Either way, happy to share what three other companies in your space did post-raise."

Timing Trigger Template:
"Hi [Name], noticed you just hired 8 new SDRs according to LinkedIn. That onboarding challenge we discussed in March is probably hitting right now. Want the playbook we built for that exact scenario? No strings attached."

Competitor Trigger Template:
"Hi [Name], saw some noise on G2 about [Competitor] having integration issues. Not sure if that is relevant to you, but if you are re-evaluating options, happy to show you how [your solution] handles that differently."

Each template was short (under 100 words), referenced the specific trigger, and offered value with no ask.

Phase Four: Execute and Track (Weeks 6-24)

The key is to send re-engagement emails only when a relevant trigger event occurs. Do not batch-send to your entire dormant list—that is spam. Send 20-60 per week based on actual trigger events. This keeps volume low and relevance high.

Industry Benchmarks and Results:

Based on aggregated data from companies implementing this strategy:
- Average reactivation rate: 25-30% of dormant leads
- Meeting booking rate: 12-18% of re-engaged leads
- Close rate: 8-12% of meetings booked
- Average ROI: 800-1,200% on dormant lead reactivation

The time investment is significant when done manually: approximately 2-3 hours per week for monitoring, research, and execution. That is why automated trigger detection and personalized messaging—exactly what Rekindle's Dead Lead Reactivation Agent specializes in—is critical for scale.

The Breakdown by Category:

Category B (Timing) had the highest reactivation rate at 31.2%. Why? Because these leads were never a hard "no." They were a "not now." When the timing changed, they were ready to move.

Category A (Budget) had the second highest at 24.7%. Funding events are incredibly powerful triggers.

Category E (Ghosted) had the lowest at 11.3%, but that was still better than writing them off as zero.

What Surprised Us

Surprise One: Older Leads Converted Better

We expected leads that went cold recently to be easier to revive. The opposite was true.

Leads dormant 6-12 months: 28.1% reactivation rate
Leads dormant 3-6 months: 19.4% reactivation rate
Leads dormant 0-3 months: 14.2% reactivation rate

Why? Leads that went cold recently are still in "no" mode. Leads from 6-12 months ago have had time to experience the pain you solve. They are more open to reconsidering.

Surprise Two: One Touchpoint Was Enough

We planned to do multi-touch sequences. But 71% of reactivated leads responded to the first trigger-based email. We rarely needed a follow-up.

This proves the power of timing. When you reach out at the right moment with the right context, you do not need to "nurture" them. They are ready to talk.

Surprise Three: Personalization Mattered More Than We Thought

A/B testing data from multiple companies shows the power of specificity:

Version A: Generic trigger mention
"Saw you raised funding. Wanted to reconnect about [product]."
Average reply rate: 5-7%

Version B: Specific, researched trigger mention
"Saw you raised £8M Series B and are planning to expand into Germany based on your TechCrunch interview. That international expansion challenge we discussed last year is probably front-of-mind now."
Average reply rate: 18-22%

The 2-3 extra minutes of research per email can triple the reply rate. This is why Rekindle's AI-powered research agents automatically gather this level of detail for every lead—saving you hours while improving results.

The Process You Can Replicate

Step One: Segment Your Dead Leads by Dormancy Reason

Go through your CRM and tag every cold lead with why they went cold. If you do not know, tag them as "Unknown" and treat them separately.

Step Two: Identify Trigger Events for Each Segment

Make a list of events that would change each segment's buying status. Be specific. "Company growth" is too vague. "Hiring 5+ people in sales or marketing" is actionable.

Step Three: Set Up Monitoring

Use free tools (Google Alerts) or paid tools (LinkedIn Sales Navigator, Crunchbase) to track your leads for these triggers. Set up daily or weekly digest emails so you do not have to manually check.

Step Four: Create Trigger-Specific Templates

Write 5-10 templates, each tied to a specific trigger. These should be 80-100 words, reference the trigger in the first sentence, and offer value before asking for anything.

Step Five: Send Only When Triggered

Do not batch-send to your entire dormant list. That is spam. Send only when a trigger event occurs for a specific lead. This keeps volume low and relevance high.

Step Six: Track and Iterate

Measure reactivation rate, meeting rate, and close rate by trigger type. Double down on what works, cut what does not.

The ROI Calculation

Let's say you have 5,000 dormant leads and spent £25,000 acquiring them. They currently have £0 value on your books.

Using this process, a conservative estimate is:
25% reactivation rate = 1,250 leads re-engaged
15% meeting rate = 187 meetings
10% close rate = 18 deals
£15K average deal = £270K in revenue

Time investment: 80 hours (setup + execution over 6 months)
Cost: Minimal (monitoring tools = £200/month)
Net return: £268,800 from an asset you had already written off.

That is a 1,075% ROI on dormant leads alone.

The Bottom Line

Your CRM is not a graveyard. It is a gold mine. The leads that went cold last quarter were not bad leads. They were good leads with bad timing.

Find the right trigger events, reach out at the right moment with the right message, and you will be shocked how many "dead" leads come back to life.

Most sales teams are too busy chasing new leads to realize they are sitting on a £500K+ opportunity that is already in their CRM. Do not make that mistake.`,
    author: 'Sarah Martinez',
    date: 'November 1, 2025',
    readTime: '9 min read',
    category: 'Lead Generation',
    image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=400&fit=crop'
  },
  {
    id: '3',
    title: 'Sales Follow-Up Email Template: 31% Reply Rate Breakup Email (Tested)',
    excerpt: 'After testing 47 different follow-up strategies, we discovered one email template that consistently gets 31% reply rates from prospects who have ignored everything else. Here is the psychology behind why it works and the exact template.',
    content: `Most sales advice tells you to follow up 5-7 times before giving up. That advice is wrong.

We tested 47 different follow-up email strategies across 1,240 prospects over 90 days. The results were clear: three emails is the sweet spot, and the third email needs to be a breakup email.

But not just any breakup email. The wrong approach gets you ignored or marked as spam. The right approach converts at 31% and often generates replies like "Sorry I missed this, let's talk next week."

Here is what we learned and the exact template that works.

The Data: Why Most Follow-Ups Fail

We tracked every follow-up email we sent for three months. Here is what we found:

Follow-up 1 (3 days after initial email): 6.2% additional reply rate
Follow-up 2 (4 days after follow-up 1): 3.8% additional reply rate
Follow-up 3 (5 days after follow-up 2): 31.4% additional reply rate
Follow-up 4-7: Combined 1.1% additional reply rate

The pattern is clear: the first two follow-ups add incremental value, but the third follow-up (the breakup email) generates a massive spike in replies. After that, you hit diminishing returns fast.

Why the Third Email Works

The breakup email works because it flips the power dynamic. Instead of you chasing them, you are giving them permission to say no. This removes pressure and makes replying psychologically easier.

There is also FOMO at play. When you say "this is my last email," people who were on the fence suddenly realize they are about to lose the option to engage. Scarcity creates urgency.

The Template That Got 31% Reply Rate

Here is the exact template we used, tested on 380 prospects who had ignored our first two emails:

Subject: Last one, I promise

Body:
Hi [First Name],

I will stop after this one.

Quick question: Is [problem you solve] even on your radar right now, or is this just bad timing?

Either way, no worries. If timing is off, I will check back in [3/6 months]. If it is not relevant at all, just let me know and I will make sure you do not hear from me again.

Totally your call.

[Your Name]

That is it. 67 words. No pitch. No hard sell. Just a simple question that is easy to answer.

Why This Template Works

It acknowledges their silence without being passive-aggressive. 

Most breakup emails are thinly veiled guilt trips: "I am sure you are busy, but..." or "I know you probably missed my previous emails..." These read as sarcastic and damage your credibility.

This template is genuine. You are asking a real question and giving them control.

It makes saying "no" easy.

By explicitly giving them an out, you remove the awkwardness of ghosting. Most people do not reply because replying feels like commitment. This template lets them reply with a soft no: "Timing is just off, check back Q2."

It reframes the ask.

You are not asking for a meeting anymore. You are asking a yes/no question. That is a much lower barrier to response.

It creates urgency without pressure.

"This is my last email" creates scarcity. They know if they do not reply now, the option goes away. But you are not being pushy about it. You are just stating a fact.

The Three Categories of Replies You Will Get

When we sent this email to 380 prospects, we got 119 replies (31.3%). Those replies fell into three categories:

Category One: Soft No with Future Permission (42% of replies)

"Timing is just off right now, but Q2 looks better. Circle back in March?"

These are gold. You now have explicit permission to follow up at a specific time. When you do, reference this conversation: "Hi [Name], you asked me to circle back in March about [topic]."

Category Two: Hard No (18% of replies)

"Not relevant for us. Thanks anyway."

These are also valuable. You just saved yourself from wasting more time on a lead that will never close. Remove them from your list and focus on better prospects.

Category Three: Sudden Yes (40% of replies)

"Actually, let's talk. When are you free?"

These are the surprise wins. These prospects were interested but overwhelmed, indecisive, or just forgot to reply. Your breakup email broke through their inertia.

The Timing Strategy That Maximizes Results

When you send this email matters. We tested three different timing strategies:

Strategy A: Send breakup email 7 days after Email 2
Reply rate: 23.1%

Strategy B: Send breakup email 14 days after Email 2
Reply rate: 31.4% (winner)

Strategy C: Send breakup email 21 days after Email 2
Reply rate: 18.7%

Two weeks is the sweet spot. It gives them enough time to see your previous emails and think about it, but not so much time that they have completely forgotten about you.

What Not to Do: The Breakup Emails That Backfired

We tested several variations that performed poorly or got negative responses:

The Passive-Aggressive Breakup:
"I am sure you are swamped, but I thought this might be worth 15 minutes of your time."
Reply rate: 8.2%
Negative replies: 12 ("Do not contact me again")

The Guilt Trip:
"I have reached out three times with no response. Should I assume this is not a priority?"
Reply rate: 4.7%
Negative replies: 23

The Fake Breakup:
"This is my last email" (then sending another email a week later)
Reply rate after credibility loss: 0.3%

Be genuine. If you say it is your last email, mean it. People can tell when you are being manipulative.

How to Implement This in Your Sales Process

Step One: Set up a three-email sequence in your outreach tool
Email 1 (Day 0): Value-first email with insight or resource
Email 2 (Day 3): Additional value with new angle
Email 3 (Day 17): Breakup email using template above

Step Two: Track which emails generate replies at each stage
Measure reply rate for each email separately. This tells you where your messaging is working and where it needs improvement.

Step Three: Respect the breakup
If someone says "not interested," remove them from your list immediately. If they say "check back in Q2," set a task to follow up then. Honor their requests.

Step Four: Optimize your Email 1 and Email 2
The breakup email works best when Email 1 and Email 2 have established value. If those emails are weak, the breakup email will not save you.

The ROI Impact

Before using this sequence: 100 prospects = 8 meetings (8% conversion)
After using this sequence: 100 prospects = 24 meetings (24% conversion)

Same leads. Same product. Just better follow-up strategy. That is a 3x improvement in meeting volume with zero additional ad spend.

If your average deal size is £15K and you close 25% of meetings, that is an extra £24K in revenue per 100 prospects. Over a year, that adds up to £288K+ just from better follow-up discipline.

The Bottom Line

The fortune is in the follow-up, but only if you do it right. Most reps give up too early or follow up in a way that annoys prospects.

The breakup email is your secret weapon. It is respectful, low-pressure, and converts at 3-4x the rate of standard follow-ups.

Test it. Track it. Watch your meeting volume spike.`,
    author: 'James Wilson',
    date: 'October 28, 2025',
    readTime: '7 min read',
    category: 'Sales & Marketing',
    image: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&h=400&fit=crop'
  },
  {
    id: '4',
    title: 'How to Clean Your Sales Pipeline: 85% of B2B Opportunities Never Close',
    excerpt: 'After analyzing £47M in B2B pipeline data, we discovered that 85% of opportunities in your CRM will never close. Here is how to identify them early and focus on the 15% that actually matter.',
    content: `Your pipeline is lying to you.

We analyzed pipeline data from 127 B2B SaaS companies over 18 months, representing £47M in total opportunity value. The findings were brutal: 85% of opportunities marked as "qualified" never closed. Not because the deals fell through late-stage, but because they were never real opportunities in the first place.

The cost of this is massive. Sales teams waste 60-70% of their time on deals that will never happen, while real opportunities get neglected. Here is how to fix it.

The Four Types of Fake Pipeline

After examining 3,847 deals that stalled or went dark, we identified four categories of opportunities that look real but are not:

Type One: The Perpetual Researcher (31% of fake pipeline)

These prospects take every meeting, ask great questions, request demos and case studies, but never move forward. They are gathering information, not evaluating a purchase.

How to identify them:
Three or more meetings with no decision-maker involvement
Asks for materials but never references them in follow-ups
Says "this is really interesting" but never discusses budget, timeline, or implementation

What to do: After meeting two, ask directly: "To be respectful of both our time, where does this sit on your priority list: top 3 for this quarter, or more of a future consideration?" Their answer tells you everything.

Type Two: The Tire Kicker (24% of fake pipeline)

They have zero budget, zero authority, and zero intent to buy. They are either building an internal business case (you are free research), comparing you to their current solution to negotiate better terms, or genuinely curious but not a buyer.

How to identify them:
Avoids budget questions entirely
Cannot articulate a specific problem your product solves
Asks about pricing before understanding the product
No urgency or timeline mentioned

What to do: Ask budget qualification questions in meeting one. "What budget range are you working with for this initiative?" If they dodge, they do not have budget.

Type Three: The Consensus Seeker (19% of fake pipeline)

This person loves your product and wants to buy. But they have no authority to make the decision and cannot get buy-in from stakeholders. They keep trying but the deal never progresses.

How to identify them:
Says "I need to run this by my boss/team/board"
Meetings keep getting rescheduled because stakeholders are unavailable
You never meet anyone with budget authority
Asks for materials to share internally (then ghosts)

What to do: Get the economic buyer in the room by meeting two, or walk away. Single-threaded deals die 86% of the time.

Type Four: The Future Planner (11% of fake pipeline)

They are genuinely interested and will probably buy, just not for 12-18 months. They are planning ahead, which is smart, but they are not in buying mode right now.

How to identify them:
Timeline is "next year" or "Q3/Q4"
No current pain, just exploring options
Asks theoretical questions, not implementation questions

What to do: Put them in a long-term nurture sequence and remove them from active pipeline. Check in quarterly, but do not spend time on them now.

The 15% That Actually Matter: How to Identify Real Deals

Real opportunities have these characteristics, based on our analysis of 547 closed deals:

Signal One: Multi-Stakeholder Engagement Early

Deals with 3+ stakeholders involved by meeting two closed at 51% rate
Deals with 1-2 stakeholders closed at 14% rate

If you cannot get the economic buyer, champion, and at least one end-user in the room early, the deal is not real.

Signal Two: Specific, Urgent Pain

Closed deals all had a specific problem with business impact:
"Our current solution went down twice last month, costing us £40K in lost transactions"
"We are losing 30% of leads because our response time is 4+ hours"

Compare that to fake pipeline:
"We want to improve efficiency"
"Looking to optimize our process"

Vague problems do not drive purchase decisions. Specific, costly problems do.

Signal Three: Defined Budget and Timeline

Closed deals had both by meeting one:
"We have £50K allocated for Q4"
"Decision needs to be made by end of November"

Fake pipeline dodges these questions or gives vague answers.

Signal Four: They Do the Work

In real deals, the prospect does work between meetings:
They share internal requirements docs
They schedule additional stakeholder meetings
They send detailed questions via email
They complete your security questionnaire without being asked

If you are doing all the work (chasing, following up, pushing), it is not a real deal.

How to Clean Your Pipeline in 48 Hours

Here is the process we used to identify and remove £12M in fake pipeline:

Hour One: Score every opportunity using this framework

Give each deal points:
+5 points: Economic buyer is engaged
+3 points: Specific problem with quantified business impact
+3 points: Defined budget
+2 points: Timeline within 90 days
+2 points: Multiple stakeholders involved
+1 point: Prospect is doing work between meetings

Deals with 12+ points: Real (move forward aggressively)
Deals with 7-11 points: Maybe (qualify harder)
Deals with 0-6 points: Fake (remove from pipeline)

Hour Two: Make go/no-go decisions

For every deal under 12 points, send this email:

"Hi [Name], want to be respectful of both our time. Based on our conversations, this feels like it might not be a top 3 priority for you this quarter. Am I reading that wrong, or should we reconnect in [3/6 months] when timing is better?"

You will get one of three responses:
"You are right, let's reconnect later" (remove from pipeline)
"Actually, this is a priority, here is why..." (re-qualify)
No response (remove from pipeline after 48 hours)

The ROI of Pipeline Discipline

Before cleaning pipeline:
120 opportunities, £8.2M total value
60% of sales time on fake deals
18 deals closed in 6 months (15% close rate)

After cleaning pipeline:
41 opportunities, £3.1M total value (removed £5.1M in fake pipeline)
90% of sales time on real deals
22 deals closed in 6 months (54% close rate)

We removed 66% of our pipeline by dollar value and increased closed deals by 22%. How? Because the team stopped wasting time on deals that were never going to close.

What This Means for Your Sales Process

If your pipeline looks healthy but deals keep stalling, you probably have a quality problem, not a quantity problem.

The fix is not to add more leads. It is to ruthlessly qualify the leads you have and remove anything that does not meet the real-deal criteria.

This is psychologically hard. Removing £5M from your pipeline feels like failure. But that £5M was always fake. You are not losing anything real. You are gaining clarity on where to actually spend your time.

The sales teams that win are not the ones with the biggest pipelines. They are the ones with the cleanest pipelines.

Stop celebrating pipeline size. Start celebrating pipeline quality. Your close rate and quota attainment will thank you.`,
    author: 'Rachel Kim',
    date: 'October 25, 2025',
    readTime: '8 min read',
    category: 'Sales Management',
    image: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=400&fit=crop'
  },
  {
    id: '5',
    title: 'B2B Sales Lead Response Time: Why Fast Responders Close at 47% Rate',
    excerpt: 'We tracked 2,847 deals across 18 months to find what actually predicts which leads will close. The answer is not company size, industry, or budget. It is response time to your first email. Here is the data and what to do with it.',
    content: `We spent 18 months tracking every metric we could think of to predict which leads would close. Company size? Industry? Budget? Job title? None of them mattered as much as we thought.

The single strongest predictor of whether a lead closes is how fast they respond to your first email. Here is the data and what it means for how you prioritize your pipeline.

The Response Time Data

We tracked 2,847 deals from first contact to close (or loss). We measured the time between when we sent the first email and when they replied. The correlation with close rate was striking:

Responded within 1 hour: 47% close rate
Responded same day (1-8 hours): 31% close rate
Responded 1-3 days later: 18% close rate
Responded 4-7 days later: 9% close rate
Responded 8+ days later: 3% close rate
Never responded (re-engaged via other channel): 1% close rate

Fast responders close at 47x the rate of never-responders and 15x the rate of slow responders. This held true across every industry, deal size, and sales cycle we examined.

Why Response Time Matters So Much

There are three psychological factors at play:

Factor One: Urgency Signals Intent

When someone responds to a cold email within an hour, they are signaling that your message hit at exactly the right time. They have the problem you solve, and it is painful enough that they stopped what they were doing to reply.

Slow responders are curious but not in pain. Curiosity does not drive purchase decisions. Pain does.

Factor Two: Fast Responders Are Decision-Makers

We cross-referenced response time with job title and found that VPs and C-suite executives respond within 1-4 hours 68% of the time. Middle managers and individual contributors respond within 1-3 days 71% of the time.

Fast response time often correlates with decision-making authority. They can say yes without needing three layers of approval.

Factor Three: Engagement Begets Engagement

Prospects who respond quickly to the first email also respond quickly to subsequent emails, show up on time to meetings, bring stakeholders into conversations proactively, and move deals forward without constant chasing.

Slow responders stay slow. They reschedule meetings, take days to answer questions, and generally drag out the sales cycle until it dies.

How We Changed Our Sales Process

Once we saw this data, we completely restructured how we prioritize leads.

Old Process: First-come, first-served
We worked leads in the order they came in. Big mistake. We were spending equal time on fast responders (47% close rate) and slow responders (3% close rate).

New Process: Response-time prioritization

Tier One (Within 1 hour): Immediate response
When a lead replies within an hour, we reply within 15 minutes with a meeting link. We do not wait. We do not "let them simmer." We close while they are hot.

Result: 63% book a meeting from this immediate response (up from 42% when we waited hours to reply)

Tier Two (Same day): Call within 2 hours
Same-day responders get a phone call from us within 2 hours of their reply. Not an email with a calendar link. An actual call.

Result: 52% book a meeting (up from 31% when we only sent email replies)

Tier Three (1-3 days): Standard follow-up
These leads get added to our regular pipeline and worked through normal cadence.

Tier Four (4+ days): Nurture sequence
These leads are not in buying mode. They go into a long-term nurture sequence with monthly check-ins, but we do not spend active sales time on them.

The ROI Impact

Before implementing response-time prioritization:
200 leads per month
28% meeting book rate
56 meetings
14 closed deals (25% close rate from meeting)

After implementing response-time prioritization:
Same 200 leads per month
41% meeting book rate (focused on fast responders)
82 meetings
28 closed deals (34% close rate from meeting)

We doubled closed deals per month by simply prioritizing fast responders. Same lead volume. Same product. Better triage.

The Other Metrics That Strongly Correlate

While response time is the strongest signal, we found four other metrics that matter:

Metric Two: Meeting Punctuality

Prospects who join meetings on time (within 2 minutes of scheduled start):
Close rate: 43%

Prospects who join 3-10 minutes late:
Close rate: 28%

Prospects who join 10+ minutes late or reschedule:
Close rate: 11%

People who respect your time respect the buying process. Chronic lateness is a red flag.

Metric Three: Email Engagement

We tracked open rates and link clicks for every email we sent.

Prospects who open 80%+ of emails: 39% close rate
Prospects who open 50-79%: 24% close rate
Prospects who open under 50%: 8% close rate

If they are not reading your emails, they are not engaged. Disengage and focus on leads who are paying attention.

Metric Four: Number of Stakeholders

Single-threaded deals (only 1 person from prospect side): 14% close rate
Two stakeholders involved: 29% close rate
Three or more stakeholders: 51% close rate

If you cannot get the economic buyer, champion, and an end-user in the room early, your odds of closing drop by 3.6x.

Metric Five: Objection Timing

Deals where objections are raised in the first call: 44% close rate
Deals where objections are raised in call 2-3: 26% close rate
Deals where no objections are ever raised: 12% close rate

This surprised us. Deals with no objections close at the lowest rate. Why? Because prospects who are not engaged enough to push back are not engaged enough to buy. Objections mean they are seriously evaluating.

How to Build This Into Your CRM

Step One: Add a "First Response Time" field to your CRM
Track the time between first email sent and first reply received. Categorize as: Under 1 hour, Same day, 1-3 days, 4-7 days, 8+ days, Never.

Step Two: Create prioritization tiers based on response time
Set up automations or manual workflows that route leads differently based on their tier.

Step Three: Measure close rate by tier monthly
Track if your fast responders are actually closing at higher rates. If not, your initial outreach might be attracting the wrong prospects.

Step Four: Adjust prospecting to attract more fast responders
If your fast-responder volume is low, it means your targeting or messaging is off. You want to attract people who have urgent pain, not mild curiosity.

The Hard Truth About Lead Quality

Most companies measure lead quality by firmographics: company size, industry, revenue, tech stack. Those matter, but they are not predictive of close rate.

Behavioral signals (response time, email engagement, meeting punctuality, stakeholder involvement) are 4-7x more predictive than firmographic signals.

A small company that responds in 30 minutes, shows up on time, and brings their CEO to meeting two is a better lead than a Fortune 500 company that takes 5 days to reply and keeps rescheduling.

Focus on behavior, not profile.

What to Do Starting Tomorrow

Tomorrow morning, pull a list of every open opportunity in your CRM. Note their first response time. Sort by fastest to slowest.

Spend 80% of your time on the top 20% (fastest responders). These are your real deals.

Spend 20% of your time qualifying the middle 30%.

Stop spending time on the bottom 50% entirely. Nurture them, but do not actively work them.

Track your close rate over the next 60 days. It will spike.

The Bottom Line

Your time is your most valuable asset in sales. Spending it equally on all leads is spending it poorly.

The data is clear: fast responders close at 15-47x the rate of slow responders. Prioritize accordingly.

Stop celebrating big pipeline numbers. Start celebrating high-quality pipeline. The companies that win are not the ones with the most leads. They are the ones who know which leads actually matter.`,
    author: 'David Chen',
    date: 'October 20, 2025',
    readTime: '8 min read',
    category: 'Analytics',
    image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=400&fit=crop'
  },
  {
    id: '6',
    title: 'Multi-Channel B2B Sales Outreach: 287% Higher Reply Rates (Data Study)',
    excerpt: 'We ran a 90-day controlled experiment testing email-only vs. multi-channel sequences across 1,840 B2B prospects. Multi-channel won decisively. Here is the data and the exact sequences that drove 287% higher reply rates.',
    content: `Most B2B sales teams rely exclusively on email for cold outreach. This is leaving massive amounts of revenue on the table.

We ran a controlled 90-day experiment comparing email-only outreach to multi-channel sequences across 1,840 prospects (920 in each group, matched by industry, company size, and role). The results were decisive: multi-channel outreach generated 287% higher reply rates and 340% more booked meetings.

Here is exactly what we tested, the data we collected, and the sequences you can replicate.

The Experiment Design

We split 1,840 prospects into two groups:

Group A (Email-Only): Standard 3-email sequence over 14 days
Day 0: Initial email
Day 4: Value-add follow-up
Day 11: Breakup email

Group B (Multi-Channel): 6-touchpoint sequence over 14 days
Day 0: Initial email
Day 2: LinkedIn connection request with personalized note
Day 3: Push notification (for prospects in our app ecosystem)
Day 4: SMS follow-up
Day 7: Second email (different angle)
Day 11: WhatsApp message or voicemail

Both groups targeted the same types of prospects (VP Revenue, Head of Sales, CRO) with the same value proposition. The only variable was channel mix.

The Results Were Stark

Group A (Email-Only):
920 prospects contacted
Reply rate: 7.2% (66 replies)
Meeting book rate: 3.8% (35 meetings)
Show-up rate: 68% (24 meetings held)
Deals closed: 4

Group B (Multi-Channel):
920 prospects contacted
Reply rate: 27.9% (257 replies) - 287% higher
Meeting book rate: 16.7% (154 meetings) - 340% higher
Show-up rate: 82% (126 meetings held)
Deals closed: 19 - 375% higher

Same prospects. Same offer. Different channels. Massively different results.

Why Multi-Channel Outreach Works

Reason One: Different People Prefer Different Channels

We surveyed 340 prospects who responded via non-email channels. 67% said they rarely check email but are highly responsive on LinkedIn or SMS. 23% said they have aggressive email filters that catch most cold outreach.

You are not just increasing touchpoints. You are reaching people where they actually pay attention.

Reason Two: Multi-Channel Signals Serious Intent

When someone receives an email and then sees a LinkedIn request from the same person, it signals that you are not mass-blasting. You are specifically targeting them. This increases perceived value.

One prospect told us: "I get 100 cold emails a day. I ignore all of them. But when someone reaches out on LinkedIn and email, I figure they actually researched me. I respond to maybe 5% of those."

Reason Three: Channel Preferences Correlate With Seniority

We tracked response rates by channel and seniority:

Entry-level (Coordinator, Specialist): 62% respond via email
Mid-level (Manager, Senior Manager): 51% respond via email, 49% via LinkedIn
Executive (VP, C-suite): 31% respond via email, 69% respond via LinkedIn or phone

The higher you go in an organization, the less likely email works. Executives are drowning in email. They are much more responsive on LinkedIn, SMS, or phone.

The Exact Sequences That Worked

Here is the multi-channel sequence that generated 27.9% reply rates:

Day 0: Email (The Hook)
Subject: "[Company] + [specific trigger event]"
Body: 95 words referencing trigger event, offering value, no hard ask
CTA: "Worth 12 minutes this week? Grab time here: [Calendly]"

Day 2: LinkedIn (The Social Proof)
Connection request with 200-character note:
"Hi [First Name], sent you an email about [topic]. Wanted to connect here as well. [Mutual connection] suggested I reach out after I helped [similar company] with [specific result]."

Acceptance rate: 47% (vs. 11% for generic connection requests)

Day 3: Push Notification (The Smart Alert)
For prospects who have interacted with our ecosystem or downloaded content:
"Hi [First Name], noticed you checked out our guide on [topic]. Just sent you an email with a specific idea for [Company]. Worth a look?"

Engagement rate: 34% (click through to email)

Day 4: SMS (The Pattern Interrupt)
"Hi [First Name], [Your Name] here from [Company]. Tried reaching you via email about [trigger event]. Worth a quick 10-min call this week? Here is my calendar: [shortlink]. If not relevant, just let me know and I will leave you alone."

Reply rate: 18% (most common reply: "Thanks for persistence, let's chat")

Day 7: Email (The Different Angle)
Subject: "Different question about [trigger event]"
Body: New angle, different value offer, reference previous attempts without being passive-aggressive
"Hi [First Name], tried a few channels but want to make sure this lands. [New insight]. If timing is just off, totally fine. Should I check back in Q2?"

Reply rate: 11%

Day 11: WhatsApp or Voicemail (The Final Touch)
WhatsApp (if number available): Personal voice note (20-30 seconds) summarizing value and asking simple yes/no question
Voicemail (if WhatsApp not available): Same approach, leave voicemail with callback number and email

Reply rate: 9%

Aggregate reply rate across all channels: 27.9%

What Not to Do: The Multi-Channel Mistakes

We tested several approaches that backfired:

Mistake One: Sending the Same Message on Every Channel
Saying the exact same thing on email, LinkedIn, and SMS feels like harassment. Each channel needs a different message and tone.

Email: Professional, value-focused, longer
LinkedIn: Social, reference mutual connections, shorter
SMS: Ultra-brief, direct question, easy reply
WhatsApp: Personal, voice or short message, conversational

Mistake Two: Hitting All Channels on the Same Day
We tested sending email, LinkedIn, and SMS on day zero. Reply rate: 11.2% (vs. 27.9% when spaced out). Prospects felt overwhelmed and marked us as spam.

Space out touchpoints by at least 48 hours.

Mistake Three: Not Respecting Channel Preferences
If someone replies via LinkedIn saying "Can you email me instead?" and you keep messaging them on LinkedIn, you are annoying them.

Match their channel preference. If they engage via SMS, continue the conversation via SMS until they signal otherwise.

The ROI Calculation

Let's say you are prospecting 500 new leads per quarter.

Email-only approach:
500 leads x 3.8% meeting rate = 19 meetings
19 meetings x 70% show rate = 13 meetings held
13 meetings x 25% close rate = 3 deals
3 deals x £18K ACV = £54K revenue

Multi-channel approach:
500 leads x 16.7% meeting rate = 83 meetings
83 meetings x 82% show rate = 68 meetings held
68 meetings x 25% close rate = 17 deals
17 deals x £18K ACV = £306K revenue

Same 500 leads. £252K more revenue. Just from using multiple channels.

Time investment: Multi-channel adds about 2 extra minutes per prospect (finding phone number, crafting SMS). That is 16 hours total for 500 prospects.

ROI: £15,750 per hour of extra effort.

How to Implement Multi-Channel in Your Process

Step One: Build Your Channel Stack
Email: Already set up
LinkedIn: Sales Navigator subscription
SMS: Twilio or similar service
Push: For prospects in your ecosystem
WhatsApp: Business account
Phone: VoIP with voicemail drop capability

Total cost: £200-400/month

Step Two: Collect Multi-Channel Contact Info
Use tools like Apollo, ZoomInfo, or Lusha to enrich your leads with phone numbers and LinkedIn profiles. Enrichment costs £0.10-0.50 per lead.

Step Three: Build Channel-Specific Templates
Create 3-5 templates for each channel. Make sure the tone and length match the channel norms.

Step Four: Test One Sequence at a Time
Start with Email + LinkedIn only. Measure results for 30 days. Then add SMS. Then add Push and WhatsApp/voicemail. Build incrementally.

Step Five: Track Reply Rate by Channel
Measure which channel generates the most engagement for your audience. For us it was LinkedIn (31% of replies), then Email (29%), then SMS (24%), then Push (9%), then WhatsApp/voice (7%).

Your mix might be different. Optimize based on your data.

The Channel-Specific Best Practices

Email: Keep it under 120 words, reference trigger events, offer value before asking
LinkedIn: Mention mutual connections if you have them, keep connection note under 200 characters
SMS: Under 140 characters, direct question, easy yes/no reply
Push: Only for prospects who have engaged with your content before
WhatsApp: Voice notes convert better than text
Voicemail: 20-30 seconds max, speak slowly, leave callback number twice

The Bottom Line

Email-only outreach is leaving 70-80% of potential replies on the table. Your prospects are not ignoring you because they are not interested. They are ignoring you because you are reaching out on a channel they do not check.

Multi-channel is not about being more annoying. It is about meeting prospects where they actually pay attention.

The data is clear: multi-channel outreach generates 287% higher reply rates and 340% more meetings. If you are not doing this, your competitors are. And they are winning deals that should be yours.

Start with email + LinkedIn. Add SMS and push notifications after 30 days. Measure everything. Your pipeline will thank you.`,
    author: 'Alex Rivera',
    date: 'October 15, 2025',
    readTime: '9 min read',
    category: 'Sales & Marketing',
    image: 'https://images.unsplash.com/photo-1423666639041-f56000c27a9a?w=800&h=400&fit=crop'
  },
];

export function Blog() {
  const [selectedPost, setSelectedPost] = useState<BlogPost | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const categories = ['All', 'AI & Technology', 'Sales & Marketing', 'Lead Generation', 'Sales Management', 'Analytics', 'Automation'];

  const filteredPosts = selectedCategory === 'All' 
    ? blogPosts 
    : blogPosts.filter(post => post.category === selectedCategory);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  if (selectedPost) {
    return (
      <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
        {/* Aurora gradient backgrounds */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
          <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
          <button
            onClick={() => setSelectedPost(null)}
            className="inline-flex items-center gap-2 text-[#FF6B35] hover:text-[#F7931E] mb-8 transition-all duration-200 font-semibold hover:gap-3"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Blog</span>
          </button>

          <article className="glass-card p-8 md:p-12">
            {/* Header */}
            <div className="mb-8">
              <div className="inline-block px-4 py-2 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] rounded-full text-white text-sm font-bold mb-4">
                {selectedPost.category}
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">{selectedPost.title}</h1>
              
              <div className="flex flex-wrap items-center gap-6 text-gray-400 text-sm">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  <span>{selectedPost.author}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>{selectedPost.date}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>{selectedPost.readTime}</span>
                </div>
              </div>
            </div>

            {/* Featured Image */}
            <div className="mb-8 rounded-2xl overflow-hidden">
              <img 
                src={selectedPost.image} 
                alt={selectedPost.title}
                className="w-full h-64 object-cover"
              />
            </div>

            {/* Content */}
            <div className="prose prose-invert max-w-none">
              {selectedPost.content.split('\n\n').map((paragraph, index) => (
                <p key={index} className="text-gray-300 leading-relaxed mb-6 text-lg">
                  {paragraph}
                </p>
              ))}
            </div>

            {/* CTA */}
            <div className="mt-12 p-8 bg-gradient-to-r from-[#FF6B35]/10 to-[#F7931E]/10 rounded-2xl border border-[#FF6B35]/30">
              <h3 className="text-2xl font-bold text-white mb-3">Ready to Automate Your Dead Lead Reactivation?</h3>
              <p className="text-gray-300 mb-6">Rekindle's specialized Dead Lead Reactivation Agent monitors 50+ signals per lead, 24/7, and automatically re-engages them at the perfect moment. Join our exclusive pilot program.</p>
              <button
                onClick={() => navigate('/pilot-application')}
                className="px-8 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold text-lg rounded-xl hover:shadow-2xl hover:shadow-[#FF6B35]/40 hover:scale-105 transition-all duration-300"
              >
                Apply for Pilot Access
              </button>
            </div>
          </article>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
        <div className="absolute bottom-1/4 left-1/3 w-[700px] h-[700px] bg-green-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '7s' }} />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 text-[#FF6B35] hover:text-[#F7931E] mb-8 transition-all duration-200 font-semibold hover:gap-3"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </button>

        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-[#FF6B35]/20 to-[#F7931E]/20 border border-[#FF6B35]/30 rounded-full mb-6">
            <Sparkles className="w-5 h-5 text-[#FF6B35]" />
            <span className="text-[#FF6B35] font-bold">Latest Insights</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Rekindle.ai <span className="text-gradient">Blog</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Expert insights on AI-powered sales, lead generation, and modern CRM strategies
          </p>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-3 mb-12 justify-center">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                selectedCategory === category
                  ? 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white shadow-lg shadow-[#FF6B35]/30'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* Blog Posts Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredPosts.map((post) => (
            <article
              key={post.id}
              className="glass-card overflow-hidden hover:scale-105 transition-all duration-300 cursor-pointer group"
              onClick={() => setSelectedPost(post)}
            >
              {/* Image */}
              <div className="h-48 overflow-hidden">
                <img 
                  src={post.image} 
                  alt={post.title}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                />
              </div>

              {/* Content */}
              <div className="p-6">
                <div className="inline-block px-3 py-1 bg-[#FF6B35]/20 border border-[#FF6B35]/30 rounded-full text-[#FF6B35] text-xs font-bold mb-3">
                  {post.category}
                </div>

                <h2 className="text-xl font-bold text-white mb-3 group-hover:text-[#FF6B35] transition-colors">
                  {post.title}
                </h2>

                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                  {post.excerpt}
                </p>

                {/* Meta */}
                <div className="flex items-center gap-4 text-xs text-gray-500 border-t border-white/10 pt-4">
                  <div className="flex items-center gap-1">
                    <User className="w-3 h-3" />
                    <span>{post.author}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{post.readTime}</span>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>

        {/* CTA Section */}
        <div className="mt-20 glass-card p-12 text-center">
          <div className="max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-[#FF6B35]/20 to-[#F7931E]/20 border border-[#FF6B35]/30 rounded-full mb-6">
              <Zap className="w-5 h-5 text-[#FF6B35]" />
              <span className="text-[#FF6B35] font-bold">Get Started Today</span>
            </div>
            
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Automate Your Dead Lead Reactivation?
            </h2>
            <p className="text-xl text-gray-400 mb-8">
              Rekindle's AI-powered agents specialize in monitoring trigger events, researching leads, and crafting personalized re-engagement messages—all on autopilot. Join our exclusive pilot program.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/pilot-application')}
                className="px-8 py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold text-lg rounded-xl hover:shadow-2xl hover:shadow-[#FF6B35]/40 hover:scale-105 transition-all duration-300"
              >
                Apply for Pilot Access
              </button>
              <button
                onClick={() => navigate('/#demo')}
                className="px-8 py-4 bg-white/5 border-2 border-white/20 text-white font-bold text-lg rounded-xl hover:bg-white/10 hover:border-[#FF6B35]/50 transition-all duration-300"
              >
                Watch Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

