---
name: social_marketing
description: Social media management application for creating, scheduling, and analyzing posts across Facebook, Instagram, LinkedIn, Twitter, and YouTube.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# social_marketing — Odoo 19.0 Skill Reference

## Overview

The Social Marketing application provides a centralized dashboard to manage multiple social media business accounts, create and schedule posts, analyze content effectiveness, engage with followers, and run cross-channel marketing campaigns. Supports Facebook, Instagram, LinkedIn, Twitter (X), YouTube, and push notifications. Integrates with Sales, Invoicing, CRM, and Website for end-to-end campaign tracking. Used by content marketers and social media managers.

## Key Concepts

- **Stream**: A connected social media business account displayed as a column on the main dashboard feed. Personal profiles cannot be added.
- **Social Post**: Content created for one or more social media accounts and/or website push notifications. States: Draft, Scheduled, Posted.
- **Social Campaign**: A cross-channel campaign grouping that can include emails, SMS, social posts, and push notifications. Shares the campaign framework with Email Marketing.
- **Push Notification**: A web notification sent to website visitors. Requires "Enable Web Push Notifications" in the Website app settings.
- **Visitor**: A tracked website visitor viewable from Social Marketing > Visitors, with options to send Email or SMS.
- **Insights**: Platform-specific KPI analytics for each connected social media stream.
- **Lead from Comment**: The ability to create a CRM lead directly from a social media post comment.

## Core Workflows

### 1. Connect Social Media Accounts

1. Navigate to Social Marketing app, click **Add A Stream**.
2. Select platform: Facebook, Instagram, LinkedIn, Twitter, or YouTube.
3. Authorize Odoo on the platform's authorization page.
4. The account appears as a new stream column on the dashboard.
5. Alternative: go to Configuration > Social Media and click **Link account** for the desired platform.

### 2. Create and Publish a Social Post

1. Click **New Post** on the dashboard, or go to Posts > **New**.
2. In **Post on**, select one or more connected social media accounts and/or push notification targets.
3. Write the **Message**. Visual previews for each platform appear on the right.
4. Optionally **Attach Images**.
5. Optionally assign to a **Campaign**.
6. In **When**, choose **Send Now** (immediate) or **Schedule later** (set date/time).
7. Click **Post** (or **Schedule** if scheduling).

### 3. Create a Social Marketing Campaign

1. Navigate to Campaigns from the header menu.
2. Click **Create** or use the quick-add **+** in any Kanban stage.
3. Enter Campaign Name, Responsible, Tags.
4. On the campaign form, use action buttons: **Send New Mailing**, **Send SMS**, **Send Social Post**, **Push Notification**.
5. Each communication type appears in its own tab on the campaign form.
6. Monitor via smart buttons: Revenues, Quotations, Leads, etc.

### 4. Create Leads from Social Media Comments

1. Click a post from the dashboard to open the post popup.
2. Scroll to the desired comment.
3. Click the three vertical dots icon next to the comment, select **Create Lead**.
4. Choose: Create a new customer, Link to an existing customer, or Do not link.
5. Click **Convert** — a new lead detail form appears for processing.

### 5. Analyze Content Performance

1. View stream KPIs by clicking the **Insights** link at the top of each stream column.
2. View all posts at Social Marketing > Posts in Kanban, Calendar, List, or Pivot view.
3. For campaign-level analytics, open the campaign form and check smart button metrics (Revenues, Quotations, Leads, etc.).

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `social.post` | Social media post record |
| `social.account` | Connected social media account |
| `social.stream` | Dashboard stream |
| `social.media` | Social media platform definition |
| `utm.campaign` | Marketing campaign (shared) |

### Key Fields (social.post)

- `message` — Post content text
- `image_ids` — Attached images
- `account_ids` — Target social accounts
- `campaign_id` — Associated campaign
- `post_method` — now, scheduled
- `scheduled_date` — Schedule datetime
- `state` — draft, scheduled, posting, posted
- `push_notification_title` — Push notification title
- `push_notification_target_url` — Target page URL
- `push_notification_image` — Custom icon

### Supported Platforms

| Platform | Notes |
|----------|-------|
| Facebook | Business pages only. Admin account required for adding pages. |
| Instagram | Added via Facebook login (shared API). Must be linked to Facebook account. |
| LinkedIn | Business accounts. |
| Twitter (X) | Character limit applies to message field. |
| YouTube | Business accounts. |
| Push Notifications | Requires Website app with "Enable Web Push Notifications" enabled. |

### Key Menu Paths

- `Social Marketing` — Main feed dashboard
- `Social Marketing > Posts` — All posts (Kanban/Calendar/List/Pivot)
- `Social Marketing > Campaigns` — Campaign management
- `Social Marketing > Visitors` — Website visitor tracking
- `Social Marketing > Configuration > Social Media` — Platform connections
- `Social Marketing > Configuration > Social Accounts` — Linked account list
- `Social Marketing > Configuration > Social Streams` — Stream configuration

### Push Notification Options

- `Notification Title` — Custom push notification title
- `Target URL` — Page URL that triggers the notification
- `Icon Image` — Custom icon for the notification
- `Local Time` — Send in visitor's timezone (for scheduled posts)
- `Match all records` — Domain rules to target specific visitor segments

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18.0 vs 19.0 breaking changes documented -->

## Common Pitfalls

- **Personal profiles cannot be added**: Only business/page accounts work as streams. This is a platform API limitation.
- **Multi-company page de-authentication**: If not all pages are activated by all companies at once, a permission error occurs. In multi-company environments, add all pages for all companies simultaneously.
- **Large page quantities**: Odoo cannot handle a large number of pages (~40+) under the same company due to API constraints.
- **Instagram requires Facebook link**: Instagram accounts must be linked to a Facebook account to appear as a stream (they share the same API).
- **Mailing Campaigns setting required for Send New Mailing**: The button only appears on campaign templates if the Mailing Campaigns feature is enabled in Email Marketing > Configuration > Settings.
