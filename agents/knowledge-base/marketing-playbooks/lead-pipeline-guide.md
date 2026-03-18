---
title: "Lead Pipeline Management Guide"
kb_scope: "marketing-playbooks"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Lead Pipeline Management Guide

## Overview

This guide covers the complete lead-to-customer journey in Odoo CE 19.0 CRM, including lead capture, qualification, pipeline management, lead scoring, conversion optimization, and reporting. The pipeline is configured for B2B SaaS sales with a typical cycle of 2-8 weeks.

---

## CRM Module Configuration

### Sales Teams

Configure sales teams to organize lead distribution and pipeline management:

| Team | Focus | Members | Lead Assignment |
|------|-------|---------|----------------|
| Inbound Sales | Website leads, demo requests, referrals | SDRs | Round-robin |
| Outbound Sales | Prospecting, cold outreach, events | BDRs | Manual assignment |
| Enterprise Sales | High-value accounts (>PHP 1M ARR) | Senior AEs | Manager assigned |
| Renewals | Existing customer expansion and renewal | CSMs | Account-based |

**Setup in Odoo:**
1. Navigate to CRM > Configuration > Sales Teams
2. Create each team with members and assignment rules
3. Set the team's pipeline stages (shared or team-specific)

### Pipeline Stages

Define the pipeline stages that reflect your actual sales process:

| Stage | Probability | Description | Exit Criteria |
|:------|:-----------|:------------|:-------------|
| New | 5% | Lead captured, not yet contacted | First contact made |
| Qualified | 15% | Need confirmed, budget exists, timeline known | Discovery call completed |
| Discovery | 30% | Requirements gathered, solution mapped | Demo scheduled |
| Demo/Proposal | 50% | Product demonstrated, proposal delivered | Proposal sent and received |
| Negotiation | 70% | Commercial terms under discussion | Verbal agreement or final objections addressed |
| Won | 100% | Deal closed, contract signed | Payment received or PO issued |
| Lost | 0% | Deal did not close | Reason documented |

**Setup in Odoo:**
1. Navigate to CRM > Configuration > Stages
2. Create each stage with the sequence, probability, and requirements
3. Stages are shared across all teams by default (or assign to specific teams)

### Lead Sources

Configure lead sources for attribution tracking:

| Source | Channel | Typical Volume | Expected Conversion |
|--------|---------|:--------------|:-------------------|
| Website Form | Organic / Paid | Medium | 5-10% |
| Demo Request | Website | Low | 15-25% |
| Referral | Word of mouth | Low | 20-30% |
| LinkedIn | Social | Medium | 3-8% |
| Event | Webinar / Conference | Burst | 5-15% |
| Cold Outreach | Email / Phone | High | 1-3% |
| Partner | Channel partner | Low-Medium | 10-20% |

---

## Lead Capture

### Website Lead Forms

Configure website forms to automatically create CRM leads:

1. **Contact Form** (insightpulseai.com/contact)
   - Fields: Name, Email, Company, Phone, Message
   - Creates: CRM Lead, assigned to Inbound Sales team
   - UTM tracking: Captured automatically from URL parameters

2. **Demo Request Form** (insightpulseai.com/demo)
   - Fields: Name, Email, Company, Phone, Company Size, Industry, Primary Interest
   - Creates: CRM Lead with "Demo Request" tag, high priority
   - Automation: Immediate Slack notification to #sales-alerts

3. **Resource Download Form** (gated content)
   - Fields: Name, Email, Company
   - Creates: CRM Lead with "Content Download" tag
   - Automation: Email drip sequence triggered via n8n

### Email Lead Capture

Emails to sales@insightpulseai.com or info@insightpulseai.com automatically create leads via Odoo's mail gateway:

1. Configure the mail alias in CRM > Configuration > Settings
2. Set the alias to create leads (not opportunities) for initial triage
3. The email sender becomes the lead contact
4. Email body becomes the lead description

### Manual Lead Creation

For leads from phone calls, events, or referrals:

1. Navigate to CRM > Leads (or CRM > Pipeline)
2. Click "Create"
3. Fill in: Contact Name, Company, Email, Phone, Source, Campaign
4. Add notes from the initial conversation
5. Assign to the appropriate salesperson and team

### Lead Import

For bulk lead import (event attendees, purchased lists, etc.):

1. Prepare a CSV with columns: Name, Email, Company, Phone, Source, Campaign
2. Navigate to CRM > Leads > Favorites > Import Records
3. Map columns to Odoo fields
4. Validate and import
5. Review imported leads for duplicates

---

## Lead Qualification

### BANT Framework

Use the BANT framework to qualify leads:

| Criterion | Questions to Ask | Qualification Threshold |
|-----------|-----------------|------------------------|
| **Budget** | What is your budget range? Have you allocated funds? | Budget identified, even if approximate |
| **Authority** | Who makes the purchasing decision? Are you the decision-maker? | Direct contact with decision-maker or strong champion |
| **Need** | What problem are you trying to solve? What is the impact of not solving it? | Clear, articulated pain point |
| **Timeline** | When do you need a solution? What is driving the timeline? | Implementation needed within 6 months |

### Qualification Process

1. **Initial Triage** (within 4 hours of lead creation)
   - SDR reviews the lead information
   - Check for completeness (email, phone, company)
   - Deduplicate against existing contacts and opportunities
   - Discard spam or clearly unqualified leads

2. **First Contact** (within 24 hours)
   - Call or email the lead
   - Introduce InsightPulse AI briefly
   - Ask qualifying questions (BANT)
   - Log the activity in Odoo (CRM > Lead > Log Activity)

3. **Qualification Decision**
   - If BANT criteria met: Convert to Opportunity, move to "Qualified" stage
   - If partially qualified: Schedule follow-up, keep as Lead
   - If unqualified: Mark as Lost with reason

### Converting Leads to Opportunities

1. Open the qualified lead in Odoo
2. Click "Convert to Opportunity"
3. Options:
   - **Convert to new opportunity**: Creates a fresh opportunity
   - **Merge with existing opportunity**: If the lead matches an existing opportunity for the same company
   - **Convert to existing customer**: Link to an existing partner record
4. Set the expected revenue, probability, and closing date
5. Assign to the appropriate salesperson

---

## Pipeline Management

### Daily Pipeline Discipline

Salespeople should follow these daily practices:

1. **Morning Review** (15 minutes)
   - Open CRM > Pipeline (Kanban view)
   - Review all opportunities by stage
   - Identify overdue activities (red clock icon)
   - Plan the day's calls and follow-ups

2. **Activity Execution**
   - Complete scheduled activities (calls, emails, meetings)
   - Log each activity with outcome notes
   - Schedule the next activity immediately

3. **End-of-Day Update** (10 minutes)
   - Update opportunity stages based on day's interactions
   - Update expected revenue if requirements changed
   - Schedule tomorrow's activities

### Pipeline Views in Odoo

| View | Purpose | Navigation |
|------|---------|-----------|
| Kanban | Visual pipeline overview, drag-and-drop stage changes | CRM > Pipeline (default) |
| List | Detailed opportunity listing with sorting and filtering | CRM > Pipeline > List View |
| Calendar | View scheduled activities and meetings by date | CRM > Pipeline > Calendar |
| Pivot | Analyze pipeline by dimensions (stage, team, salesperson, source) | CRM > Pipeline > Pivot |
| Graph | Visual charts of pipeline metrics | CRM > Pipeline > Graph |

### Pipeline Hygiene

Maintain pipeline accuracy with these practices:

1. **Weekly Pipeline Review** (sales manager + team)
   - Review each opportunity in Negotiation and Demo stages
   - Validate expected revenue and close dates
   - Challenge probability ratings (are they realistic?)
   - Identify stalled opportunities (no activity in 14+ days)

2. **Stale Opportunity Rules**
   - 14 days without activity: Yellow flag
   - 30 days without activity: Red flag, manager notification
   - 60 days without activity: Required action — advance, stall, or close

3. **Lost Opportunity Documentation**
   - When marking an opportunity as Lost, always select a reason:
     - Price too high
     - Chose competitor
     - No budget
     - Timeline delayed
     - No decision made
     - Technical requirements not met
     - Other (with explanation)
   - Lost reasons feed competitive intelligence and product roadmap

---

## Lead Scoring

### Scoring Model

Implement lead scoring to prioritize high-potential leads. Since Odoo CE does not have native lead scoring, use a combination of Odoo fields and n8n automation.

#### Demographic Score (0-50 points)

| Factor | Score | Criteria |
|--------|:-----:|---------|
| Company Size | 0-15 | 1-10 employees: 5, 11-50: 10, 51-200: 15, 200+: 12 |
| Industry Fit | 0-15 | Target industry: 15, Adjacent: 10, Other: 5 |
| Job Title | 0-10 | C-level: 10, VP/Director: 8, Manager: 5, Other: 2 |
| Geography | 0-10 | Metro Manila: 10, Major city: 8, Province: 5 |

#### Behavioral Score (0-50 points)

| Factor | Score | Criteria |
|--------|:-----:|---------|
| Demo Request | 20 | Requested a product demo |
| Pricing Page Visit | 10 | Visited the pricing page (tracked via UTM) |
| Content Download | 5 | Downloaded a resource (whitepaper, case study) |
| Email Engagement | 5-10 | Opened 3+ emails: 5, Clicked 2+ links: 10 |
| Event Attendance | 10 | Attended a webinar or event |
| Return Visit | 5 | Visited the website 3+ times |

#### Score Thresholds

| Score Range | Classification | Action |
|:-----------|:--------------|:-------|
| 0-30 | Cold | Nurture via email drip |
| 31-50 | Warm | SDR qualification call |
| 51-70 | Hot | Fast-track to AE |
| 71-100 | Priority | Immediate AE contact, manager notified |

### Implementing Scoring in Odoo

1. Create a custom field `x_lead_score` (Integer) on the CRM Lead model
2. Create priority tags: Cold, Warm, Hot, Priority
3. Use n8n workflow to:
   - Calculate score based on lead data fields
   - Update `x_lead_score` via Odoo API
   - Apply the appropriate priority tag
   - Notify the salesperson for Hot/Priority leads

---

## Conversion Optimization

### Stage-by-Stage Conversion Tactics

#### New to Qualified (Target: 30% conversion)

- **Speed to lead**: Contact within 4 hours of creation
- **Personalization**: Reference the lead's company and industry in the first email
- **Value proposition**: Focus on the specific pain point, not features
- **Multiple channels**: If email goes unanswered for 48 hours, try phone

#### Qualified to Discovery (Target: 60% conversion)

- **Schedule the discovery call**: Offer 2-3 time slots, use Calendly or Odoo Calendar
- **Pre-call research**: Review the company website, LinkedIn, news
- **Discovery agenda**: Share a brief agenda before the call to set expectations

#### Discovery to Demo (Target: 70% conversion)

- **Tailored demo**: Customize the demo to the prospect's industry and pain points
- **Include stakeholders**: Ask the champion to invite other decision-makers
- **Demo prep document**: Send a brief document outlining what will be covered

#### Demo to Negotiation (Target: 50% conversion)

- **Follow up within 24 hours**: Send a summary of the demo with next steps
- **Proposal**: Deliver a clear, concise proposal within 48 hours
- **Address objections**: Document objections during the demo and address them in the proposal

#### Negotiation to Won (Target: 70% conversion)

- **Create urgency**: Limited-time pricing, implementation slot availability
- **Remove friction**: Simplify the contract, offer flexible payment terms
- **Executive sponsor**: Introduce a senior person from your side for strategic alignment
- **Trial option**: Offer a paid pilot for risk-averse prospects

### Conversion Rate Benchmarks

| Stage Transition | Target Rate | Formula |
|:----------------|:-----------|:--------|
| Lead to Qualified | 30% | Qualified leads / Total leads |
| Qualified to Discovery | 60% | Discovery / Qualified |
| Discovery to Demo | 70% | Demo / Discovery |
| Demo to Negotiation | 50% | Negotiation / Demo |
| Negotiation to Won | 70% | Won / Negotiation |
| **Overall Lead to Won** | **~4.4%** | Won / Total Leads |

---

## Reporting and Analytics

### CRM Reports in Odoo

| Report | Navigation | Insights |
|--------|-----------|----------|
| Pipeline Analysis | CRM > Reporting > Pipeline | Revenue by stage, team, salesperson |
| Lead Analysis | CRM > Reporting > Leads | Lead volume, source, conversion rate |
| Activity Analysis | CRM > Reporting > Activities | Activity completion, types, frequency |

### Key Metrics to Track

**Volume Metrics:**
- Leads created per week/month
- Leads by source/medium/campaign
- Opportunities created per week/month
- Deals won per month

**Velocity Metrics:**
- Average time in each pipeline stage
- Total sales cycle length (lead to won)
- Time to first contact (speed to lead)
- Activity frequency per opportunity

**Value Metrics:**
- Average deal size
- Pipeline value by stage
- Weighted pipeline (value x probability)
- Revenue forecast (next 30/60/90 days)

**Efficiency Metrics:**
- Conversion rate per stage
- Win rate (won / (won + lost))
- Loss rate by reason
- Cost per lead / cost per acquisition

### Superset Dashboards

Build these CRM dashboards in Apache Superset:

1. **Pipeline Overview**: Current pipeline by stage, team, and salesperson
2. **Lead Flow**: Inbound lead volume over time, by source
3. **Conversion Funnel**: Visual funnel from lead to won with conversion rates
4. **Sales Forecast**: Weighted pipeline for next 30/60/90 days
5. **Activity Tracker**: Activities logged per salesperson per week
6. **Win/Loss Analysis**: Won and lost deals by reason, competitor, and deal size

---

## Automation Workflows

### Lead Assignment (n8n)

Trigger: New lead created in Odoo
1. Check lead source and company size
2. Assign to appropriate sales team based on rules
3. If demo request: assign to next available AE (round-robin)
4. Send Slack notification to assigned salesperson
5. Schedule first contact activity for 4 hours from now

### Stale Lead Alert (n8n)

Trigger: Daily at 9:00 AM
1. Query Odoo for leads with no activity in 14+ days
2. Group by salesperson
3. Send Slack DM to each salesperson with their stale leads
4. If 30+ days stale: also notify the sales manager

### Won Deal Notification (n8n)

Trigger: Opportunity stage changed to "Won"
1. Post celebration message to Slack #wins channel
2. Create onboarding project in Odoo Projects module
3. Send welcome email to customer
4. Create invoice (if auto-invoicing is enabled)
5. Notify the Customer Success team

### Lost Deal Analysis (n8n)

Trigger: Opportunity stage changed to "Lost"
1. Record the loss reason and competitor (if applicable)
2. Add to lost deal analytics dataset
3. If high-value opportunity (>PHP 500K): notify sales manager for review
4. Schedule re-engagement email in 90 days via email nurture sequence
