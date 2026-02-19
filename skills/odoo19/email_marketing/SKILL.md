---
name: email_marketing
description: Mass mailing application with drag-and-drop email builder, A/B testing, mailing lists, and campaign analytics.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# email_marketing — Odoo 19.0 Skill Reference

## Overview

The Email Marketing application enables users to create, send, schedule, and analyze mass email campaigns. It provides a drag-and-drop email builder with pre-built templates, mailing list management, A/B testing, recipient filtering with domain rules, blacklist/unsubscribe management, and detailed reporting metrics (open rate, click rate, reply rate, bounce rate). Used by marketing teams to execute email campaigns, nurture leads, and reactivate lost opportunities.

## Key Concepts

- **Mailing**: A single mass email send operation; progresses through Draft > In Queue > Sending > Sent stages.
- **Mailing List**: A curated group of contacts (Mailing Contacts) who receive targeted emails. Managed under Mailing Lists > Mailing Lists.
- **Mailing Contact**: A contact subscribed to one or more mailing lists; distinct from a Contacts record. Accessible at Mailing Lists > Mailing List Contacts.
- **Mailing Campaign**: An umbrella grouping for related mailings, SMS, and social posts; enables cross-channel revenue/quotation/opportunity tracking via smart buttons. Requires the "Mailing Campaigns" setting.
- **A/B Testing**: Sends variant emails to a percentage of recipients, then sends the winning version (by open rate, click rate, reply rate, leads, quotations, or revenues) to the rest.
- **Blacklist**: Recipients who have excluded themselves from all marketing emails. Managed at Configuration > Blacklisted Email Addresses.
- **Opt-out**: Unsubscription from a specific mailing list (not all emails).
- **Recipient Filter / Domain**: Rule-based targeting that filters records (Contacts, Leads, Event Registrations, Sales Orders, Mailing Contacts) using configurable equation-like conditions.
- **Preview Text**: Short text displayed beside the subject line in recipients' inboxes.
- **Lost Leads Reactivation Email**: A targeted email campaign using Lead/Opportunity as the recipient model, filtering by lost reasons, stages, and active/inactive status.

## Core Workflows

### 1. Create and Send a Mailing

1. Navigate to Email Marketing app.
2. Click **New** on the Mailings dashboard.
3. Enter a **Subject** (mandatory).
4. Select **Recipients** (Mailing List, Contact, Lead/Opportunity, Event Registration, Mailing Contact, or Sales Order).
5. If not Mailing List, configure filter rules beneath the Recipients field.
6. In the **Mail Body** tab, select a template or use Plain Text.
7. Customize with drag-and-drop building blocks (Blocks, Customize, Design).
8. Configure **Settings** tab: Preview Text, Send From, Reply To, Attachments, Responsible, Campaign (if enabled).
9. Click **Send** (immediate), **Schedule** (future date), or **Test** (send to test addresses).

### 2. Create and Manage Mailing Lists

1. Navigate to Email Marketing > Mailing Lists > Mailing Lists > **New**.
2. Enter a **Mailing List** name.
3. Optionally tick **Show In Preferences** for subscription management visibility.
4. Add contacts via: Recipients smart button, Import Contacts button, or Mailing List Contacts page.
5. Contacts can be imported via copy/paste or file upload in the Import Mailing Contacts popup.
6. Link mailing lists to the website using Newsletter building blocks (Newsletter Block, Newsletter Popup, Newsletter).

### 3. Set Up A/B Testing

1. On the email form, open the **A/B Tests** tab.
2. Tick **Allow A/B Testing**.
3. Set the test percentage in the **on (%)** field.
4. Choose **Winner Selection** criteria (Manual, Highest Open Rate, Highest Click Rate, Highest Reply Rate, Leads, Quotations, Revenues).
5. Set the **Send Final On** date for automatic winner determination.
6. Click **Create an Alternative Version** to build the variant.

### 4. Create a Mailing Campaign

1. Enable **Mailing Campaigns** in Email Marketing > Configuration > Settings.
2. Navigate to Email Marketing > Campaigns > **New**.
3. Enter Campaign Name, Responsible, Tags.
4. Use **Send Mailing**, **Send SMS**, **Add Post**, **Add Push** buttons to attach communications.
5. Monitor via Revenues, Quotations, Opportunities, Clicks smart buttons.

### 5. Manage Unsubscriptions and Blacklists

1. Enable **Blacklist Option when Unsubscribing** in Settings.
2. Default unsubscribe link is included in mailing templates (except Start From Scratch — add `/unsubscribe_from_list` manually or use a Footer block).
3. View blacklisted addresses at Configuration > Blacklisted Email Addresses.
4. To unblacklist: open the blacklisted record and click **Unblacklist**.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `mailing.mailing` | Email mailing record |
| `mailing.list` | Mailing list |
| `mailing.contact` | Mailing list contact |
| `mailing.campaign` | Mailing campaign |
| `mail.blacklist` | Blacklisted email addresses |

### Key Fields (mailing.mailing)

- `subject` — Email subject line (required)
- `mailing_model_id` — Target model (Mailing List, Contact, Lead/Opportunity, etc.)
- `contact_list_ids` — Many2many to mailing lists
- `mailing_domain` — Domain filter for recipients
- `state` — draft, in_queue, sending, done
- `ab_testing_enabled` — Boolean for A/B test
- `ab_testing_pc` — A/B test percentage
- `ab_testing_winner_selection` — Winner criteria
- `campaign_id` — Link to mailing campaign
- `preview` — Preview text
- `email_from` — Sender address
- `reply_to` — Reply-to address

### Key Menu Paths

- `Email Marketing > Mailings` — Main dashboard
- `Email Marketing > Campaigns` — Campaign management (requires Mailing Campaigns setting)
- `Email Marketing > Mailing Lists > Mailing Lists` — List management
- `Email Marketing > Mailing Lists > Mailing List Contacts` — Contact management
- `Email Marketing > Configuration > Settings` — App settings
- `Email Marketing > Configuration > Blacklisted Email Addresses` — Blacklist
- `Email Marketing > Configuration > Optout Reasons` — Unsubscribe reasons
- `Email Marketing > Reporting > Mass Mailing Analysis` — Cross-campaign metrics

### Settings

| Setting | Effect |
|---------|--------|
| Mailing Campaigns | Enables Campaigns menu and campaign field on mailings |
| Blacklist Option when Unsubscribing | Allows recipients to blacklist themselves |
| Dedicated Server | Use a separate SMTP server for mailings |
| 24H Stat Mailing Reports | Enables 24-hour post-send performance reports |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18.0 vs 19.0 breaking changes documented -->

## Common Pitfalls

- **Daily sending limit**: A global daily limit applies across all applications. Remaining emails after the limit are not automatically retried the next day; users must click **Retry** on the mailing.
- **Start From Scratch template missing unsubscribe link**: The unsubscribe link is not included by default; manually add `/unsubscribe_from_list` or use a Footer building block.
- **Blacklisted contacts still receive transactional emails**: Blacklisting only blocks marketing mailings, not order confirmations or shipping notifications.
- **Lost leads filter requires both Active states**: Omitting either active or inactive leads drastically reduces the target audience. Always add a branch with `Active is set` OR `Active is not set`.
- **A/B test recipients receive only one version**: With A/B testing enabled, each recipient gets exactly one variant — no duplicates are sent.
