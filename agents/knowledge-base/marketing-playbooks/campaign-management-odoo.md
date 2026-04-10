---
title: "Campaign Management in Odoo"
kb_scope: "marketing-playbooks"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Campaign Management in Odoo

## Overview

This guide covers how to set up, execute, and measure marketing campaigns using Odoo CE 18.0. While Odoo Enterprise includes a dedicated Marketing Automation module, CE provides campaign management through the CRM, Email Marketing, and Sales modules, supplemented by n8n workflow automation for advanced use cases.

---

## Campaign Planning

### Defining a Campaign

A marketing campaign in Odoo is organized around:

1. **Objective**: What outcome the campaign targets (leads, sales, signups, event attendance)
2. **Audience**: Who the campaign targets (segment, geography, industry, company size)
3. **Channels**: How the campaign reaches the audience (email, website, social, events, referral)
4. **Timeline**: Start date, end date, and key milestones
5. **Budget**: Planned spend by channel
6. **KPIs**: Measurable targets (leads generated, conversion rate, cost per lead, revenue attributed)

### Campaign Structure in Odoo

Since Odoo CE does not have a native campaign management module, use the following structure:

1. **Campaign Tag**: Create a tag in CRM > Configuration > Tags for each campaign (e.g., "Q1-2026-Product-Launch")
2. **UTM Source/Medium/Campaign**: Use Odoo's built-in UTM tracking for attribution:
   - Source: Where the traffic comes from (google, facebook, newsletter)
   - Medium: The marketing medium (cpc, email, social, banner)
   - Campaign: The campaign name (matches the tag above)
3. **Sales Team**: Optionally create a sales team for campaign-specific lead handling

### UTM Setup

Navigate to Settings > Technical > UTM to manage tracking parameters:

| UTM Field | Purpose | Examples |
|-----------|---------|---------|
| Source | Origin of the traffic | google, facebook, linkedin, referral, direct |
| Medium | Marketing medium | cpc, cpm, email, social, organic, banner |
| Campaign | Specific campaign | q1-product-launch, year-end-promo, webinar-march |

UTM parameters are appended to URLs:
```
https://insightpulseai.com/demo?utm_source=linkedin&utm_medium=social&utm_campaign=q1-product-launch
```

When a lead is created through the website form, Odoo automatically captures these UTM parameters on the lead record.

---

## Campaign Execution Channels

### Email Campaigns

Odoo CE includes an Email Marketing module for mass email campaigns.

#### Setting Up an Email Campaign

1. **Create a Mailing List**
   - Navigate to Email Marketing > Mailing Lists
   - Create a list (e.g., "Q1 Product Launch Targets")
   - Import contacts from CSV or add from existing Odoo contacts
   - Segment by industry, country, company size, or custom fields

2. **Design the Email**
   - Navigate to Email Marketing > Mailings > Create
   - Select the mailing list as recipients
   - Choose a template or design from scratch using the drag-and-drop editor
   - Include UTM parameters in all links for tracking
   - Add a clear call-to-action (CTA) linked to a landing page

3. **Configure Sending**
   - Set the "From" address (must be authenticated via SPF/DKIM for deliverability)
   - Zoho SMTP configuration: `smtp.zoho.com:587` with STARTTLS
   - Set the sending schedule (immediate or scheduled)
   - Enable A/B testing if sending to a large list (test subject lines or content)

4. **Send and Monitor**
   - Send a test email first to verify rendering
   - Click "Send" or schedule for later
   - Monitor delivery, open rates, and click rates in the mailing statistics

#### Email Performance Metrics

| Metric | Definition | Benchmark |
|--------|-----------|-----------|
| Delivery Rate | Emails delivered / emails sent | > 95% |
| Open Rate | Unique opens / emails delivered | 15-25% |
| Click Rate | Unique clicks / emails delivered | 2-5% |
| Click-to-Open Rate | Unique clicks / unique opens | 15-25% |
| Unsubscribe Rate | Unsubscribes / emails delivered | < 0.5% |
| Bounce Rate | Bounced / emails sent | < 3% |

#### Email Best Practices

1. **Subject Lines**: Keep under 50 characters. Use personalization (recipient name, company name).
2. **Sender Name**: Use a person's name, not just the company name (e.g., "Maria from InsightPulse AI").
3. **Preheader Text**: Customize the preview text that appears after the subject line.
4. **Mobile Optimization**: 60%+ of emails are opened on mobile. Use single-column layouts.
5. **CTA**: One primary CTA per email. Make it a button, not a text link.
6. **Timing**: Tuesday-Thursday, 9-11 AM local time typically performs best for B2B.
7. **Frequency**: Do not email the same list more than once per week without consent.
8. **Compliance**: Include an unsubscribe link in every email (Odoo adds this automatically).

### Website Landing Pages

Create campaign-specific landing pages using Odoo's Website module:

1. **Create the Page**
   - Navigate to Website > Pages > New Page
   - Use the drag-and-drop editor to build the landing page
   - Include: headline, value proposition, benefits, social proof, form, CTA

2. **Add a Lead Form**
   - Drag the "Form" building block onto the page
   - Configure fields: Name, Email, Company, Phone, Message
   - Set the form action to create a CRM lead
   - Add the campaign UTM parameters as hidden fields

3. **Tracking**
   - All form submissions automatically create leads with UTM data
   - The lead source, medium, and campaign are populated from the URL parameters

### Social Media Integration

Odoo CE does not include native social media posting. Use n8n workflows for automation:

1. **Content Calendar**: Maintain in a Google Sheet or Odoo spreadsheet
2. **Posting Automation**: n8n workflow that posts to LinkedIn, Facebook, and Twitter on schedule
3. **Link Tracking**: All links in social posts use UTM parameters pointing to Odoo landing pages
4. **Lead Capture**: Social traffic arrives at landing pages with UTM tracking, creating attributed leads

### Event-Based Campaigns

Use Odoo Events module for webinars, trade shows, and workshops:

1. **Create an Event**
   - Navigate to Events > Events > Create
   - Set event details: name, date, venue (or online link), ticket types

2. **Registration Tracking**
   - Enable online registration via the website
   - Each registration creates a contact and optionally a CRM lead

3. **Follow-Up Automation**
   - Use n8n to send confirmation emails, reminders, and post-event follow-ups
   - Track conversion from attendee to opportunity

---

## Lead Attribution and ROI

### Attribution Model

Odoo uses **first-touch attribution** by default: the UTM parameters captured when the lead was first created determine the campaign attribution.

For more sophisticated attribution:

1. **First Touch**: Credit goes to the campaign that first captured the lead (Odoo default)
2. **Last Touch**: Credit to the last campaign interaction before conversion (requires custom tracking)
3. **Multi-Touch**: Distribute credit across all touchpoints (requires external analytics like Superset)

### Tracking Campaign ROI

#### Revenue Attribution

1. **Tag all campaign leads**: Ensure the campaign tag is applied to every lead from the campaign
2. **Track conversion**: Monitor leads through the pipeline to Won stage
3. **Calculate revenue**: Sum the expected revenue of all Won opportunities with the campaign tag

```
Campaign ROI = (Revenue from Campaign - Campaign Cost) / Campaign Cost x 100%
```

#### Cost Tracking

Track campaign costs using the Accounting module:

1. Create an analytic account for each campaign
2. Record all campaign expenses (ads, content, events, tools) against this analytic account
3. Generate an analytic report to see total campaign spend

| Cost Category | Examples | Tracking Method |
|--------------|---------|----------------|
| Advertising | Google Ads, Facebook Ads, LinkedIn Ads | Vendor bill with campaign analytic account |
| Content | Copywriting, design, video production | Vendor bill or employee timesheet |
| Events | Venue, catering, speakers, prizes | Vendor bills with event tag |
| Tools | Email platform, landing page builder, analytics | Software subscription allocation |
| Internal | Salesperson time, marketing team time | Timesheets with campaign analytic account |

#### Performance Dashboard

Build a campaign performance dashboard in Apache Superset:

| Widget | Data Source | Metric |
|--------|-----------|--------|
| Leads by Campaign | CRM leads with campaign tag | Count of leads, trend over time |
| Conversion Funnel | CRM opportunities by stage | Conversion rate per stage |
| Revenue by Campaign | Won opportunities | Total and average deal size |
| Cost per Lead | Accounting analytic + CRM count | Total cost / total leads |
| Cost per Acquisition | Accounting analytic + Won count | Total cost / won customers |
| ROI by Campaign | Revenue - Cost / Cost | Percentage return |

---

## Campaign Templates

### Template 1: Product Launch Campaign

**Objective**: Generate 100 qualified leads in 30 days

| Channel | Activity | Timeline | Budget |
|---------|----------|----------|--------|
| Email | 3-email sequence to existing contacts | Week 1-3 | PHP 0 (organic) |
| Website | Landing page with demo request form | Week 1 (prep) | PHP 0 |
| LinkedIn | 4 posts + 2 articles about the product | Week 1-4 | PHP 15,000 (sponsored) |
| Webinar | Product demo webinar | Week 3 | PHP 5,000 |
| Referral | Existing customer referral incentive | Week 2-4 | PHP 10,000 |

### Template 2: Year-End Promo Campaign

**Objective**: Close PHP 5M in revenue from existing pipeline

| Channel | Activity | Timeline | Budget |
|---------|----------|----------|--------|
| Email | Limited-time offer to active quotes | Week 1 | PHP 0 |
| Sales | Direct outreach to warm opportunities | Week 1-2 | Salesperson time |
| Website | Promo banner on homepage | Week 1-3 | PHP 0 |
| Slack | Announcement in customer channels | Week 1 | PHP 0 |

### Template 3: Content Marketing (Ongoing)

**Objective**: Generate 20 inbound leads per month

| Channel | Activity | Frequency | Budget |
|---------|----------|-----------|--------|
| Blog | Publish 2 articles per month on Odoo use cases | Bi-weekly | PHP 10,000/month |
| Email | Newsletter digest to subscriber list | Monthly | PHP 0 |
| LinkedIn | Share blog posts + industry insights | 3x per week | PHP 5,000/month |
| Website | SEO optimization of key pages | Ongoing | PHP 5,000/month |

---

## Measuring Success

### Campaign Report Template

At the end of each campaign (or monthly for ongoing campaigns), generate this report:

**Campaign Summary**
- Campaign name and dates
- Total budget allocated vs. spent
- Channels used

**Lead Metrics**
- Total leads generated
- Leads by source/medium
- Lead quality score distribution (if using lead scoring)

**Pipeline Metrics**
- Leads converted to opportunities
- Opportunity value in pipeline
- Stage distribution

**Revenue Metrics**
- Opportunities won
- Revenue closed
- Average deal size
- Sales cycle length

**ROI Calculation**
- Total cost
- Total revenue attributed
- Return on investment (%)
- Cost per lead
- Cost per acquisition

**Learnings**
- What worked (highest performing channel/message)
- What did not work
- Recommendations for next campaign

---

## Automation with n8n

### Automated Lead Nurture Sequence

Configure n8n to automatically nurture leads based on their stage:

1. **New Lead** (Day 0): Welcome email with company overview
2. **No Response** (Day 3): Follow-up email with case study
3. **No Response** (Day 7): Third email with demo offer
4. **Still No Response** (Day 14): Mark lead as "cold" and reassign

### Automated Reporting

1. **Weekly**: n8n generates a lead summary and posts to Slack #marketing channel
2. **Monthly**: n8n generates a campaign performance report and emails to the marketing team
3. **Quarterly**: n8n generates ROI analysis for all active campaigns

### Lead Scoring Automation

n8n can compute a lead score based on:

| Factor | Points | Criteria |
|--------|--------|---------|
| Company size | 0-20 | Based on employee count field |
| Industry fit | 0-15 | Target industries get max points |
| Engagement | 0-25 | Email opens, link clicks, page visits |
| Budget | 0-20 | Self-reported budget range |
| Timeline | 0-20 | Self-reported implementation timeline |

Leads scoring 70+ are automatically promoted to "Hot" and assigned to senior sales.
