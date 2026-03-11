---
name: sms_marketing
description: SMS mass mailing application with campaign management, A/B testing, Twilio integration, and link tracking.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# sms_marketing — Odoo 19.0 Skill Reference

## Overview

The SMS Marketing application enables companies to create, send, schedule, and analyze mass SMS campaigns. It supports mailing list management, recipient filtering with domain rules, A/B testing, link tracking, blacklist management, and integration with Twilio for countries with stricter regulations. SMS is an IAP (In-App Purchase) service requiring prepaid credits. Used by marketing and sales teams to boost conversion rates and expand outreach beyond email.

## Key Concepts

- **SMS Mailing**: A mass SMS message; progresses through Draft > In Queue > Sending > Sent stages.
- **GSM7**: Standard SMS character encoding; 160 characters per message (153 in multi-part). Covers standard Latin characters and common symbols.
- **UNICODE**: Extended encoding triggered by special characters; 70 characters per message (67 in multi-part).
- **IAP Credits**: Prepaid credits purchased from Odoo required to send SMS. Credits do not expire.
- **Mailing List**: A curated group of contacts for SMS targeting. Shared with Email Marketing.
- **Blacklist**: Phone numbers opted out of all SMS communications. Managed at Configuration > Blacklisted Phone Numbers.
- **Link Tracker**: Automatic URL tracking for all links used in SMS messages. Accessible at Configuration > Link Tracker.
- **A/B Testing**: Send variant SMS messages to a percentage of recipients, then send the winner to the rest. Requires "Mailing Campaigns" setting.
- **Mailing Campaign**: Cross-channel campaign grouping shared with Email Marketing. Enables campaign-level analytics.
- **Twilio Integration**: Alternative SMS provider for countries where Odoo's default IAP does not work due to regulatory requirements. Module: `sms_twilio`.

## Core Workflows

### 1. Create and Send an SMS

1. Navigate to SMS Marketing app, click **Create**.
2. Enter a **Subject** for internal identification.
3. Select **Recipients**: Mailing List (default) or another model (Contact, Lead/Opportunity, etc.).
4. If Mailing List, select the target list. Otherwise, configure filter rules.
5. In the **SMS Content** tab, write the message. Monitor character count and SMS segment indicator.
6. Optionally click the **Information** icon to check per-country pricing.
7. In the **Settings** tab, optionally enable **Include opt-out link** and assign a **Responsible**.
8. Click **Send** (immediate), **Schedule** (future date/time), or **Test** (send to specific numbers, comma-separated).

### 2. Manage Mailing Lists

1. Navigate to Mailing Lists > Mailing Lists.
2. Click **Create** to add a new list; name it and optionally enable **Is Public** for subscription management access.
3. Add contacts directly or via Mailing List Contacts page.
4. View list metrics via smart buttons: Recipients, Mailings, etc.

### 3. Manage Blacklists

1. Navigate to Configuration > Blacklisted Phone Numbers.
2. Click **Create** to manually add a number; set Active status.
3. To remove from blacklist: open the record, click **Unblacklist**.
4. Import existing blacklists via Favorites > Import records.
5. Recipients auto-blacklist themselves by clicking Unsubscribe on the Subscription Management page.

### 4. Set Up A/B Testing

1. Enable **Mailing Campaigns** in Email Marketing > Configuration > Settings.
2. On the SMS template form, open the **A/B Tests** tab.
3. Tick **Allow A/B Testing**, set test percentage.
4. Choose **Winner Selection**: Manual, Highest Click Rate, Leads, Quotations, or Revenues.
5. Set **Send Final On** date for automatic winner dispatch.
6. Click **Create an Alternate Version** to build variants.

### 5. Set Up Twilio Integration

1. Install the **Twilio SMS** module (`sms_twilio`).
2. Go to Settings > General Settings > Contacts > Send SMS, select **Send via Twilio**, save.
3. Click **Configure Twilio Account**, paste Account SID and Auth Token from Twilio dashboard.
4. Click **Reload numbers** to import purchased phone numbers.
5. Reorder numbers by priority. Odoo matches sender number country to recipient country; falls back to the first available number.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `mailing.mailing` | SMS mailing record (shared with email marketing) |
| `mailing.list` | Mailing list (shared) |
| `mailing.contact` | Mailing list contact (shared) |
| `phone.blacklist` | Blacklisted phone numbers |
| `link.tracker` | URL tracking records |

### Key Fields (SMS mailing)

- `subject` — Internal subject/name
- `mailing_type` — `sms` for SMS mailings
- `mailing_model_id` — Target model
- `contact_list_ids` — Mailing lists
- `mailing_domain` — Recipient filter domain
- `body_plaintext` — SMS message content
- `state` — draft, in_queue, sending, done
- `ab_testing_enabled` — A/B test toggle
- `campaign_id` — Link to mailing campaign

### SMS Encoding Limits

| Encoding | Single SMS | Multi-part (per segment) |
|----------|-----------|------------------------|
| GSM7 | 160 chars | 153 chars |
| UNICODE | 70 chars | 67 chars |

### Key Menu Paths

- `SMS Marketing` — Main dashboard
- `SMS Marketing > Mailing Lists > Mailing Lists` — List management
- `SMS Marketing > Mailing Lists > Mailing List Contacts` — Contact management
- `SMS Marketing > Campaigns` — Campaign management (requires Mailing Campaigns setting)
- `SMS Marketing > Configuration > Link Tracker` — URL analytics
- `SMS Marketing > Configuration > Blacklisted Phone Numbers` — Blacklist
- `SMS Marketing > Reporting` — Graph/List/Cohort analytics

### SMS Templates (Developer Mode)

Accessible via Settings > Technical > SMS Templates. Templates are model-specific and can be reused in automation rules.

### Automation Rules Integration

Via developer mode: Settings > Technical > Automation Rules. Create rules that trigger "Send SMS" actions based on record events (creation, update, timing, webhooks).

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18.0 vs 19.0 breaking changes documented -->

## Common Pitfalls

- **Credits required**: SMS will not be sent without prepaid IAP credits. Purchase at Settings > Buy Credits.
- **Replies not supported**: Recipients cannot reply to SMS messages sent through Odoo's IAP service.
- **Insufficient credits block entire batch**: Multiple SMS sent at once count as a single transaction; if credits are insufficient for all, none are sent.
- **Invalid vs. wrong numbers**: Credits are not consumed for malformed numbers (wrong digit count), but are consumed for valid-format numbers that belong to wrong/fake recipients.
- **Twilio testing accounts**: Only send to verified phone numbers in Twilio's console. Some countries (US, Canada) require additional registration before sending.
