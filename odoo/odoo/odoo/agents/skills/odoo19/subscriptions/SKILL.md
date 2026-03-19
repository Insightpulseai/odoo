---
name: subscriptions
description: Recurring billing and subscription management with renewals, upselling, and churn tracking
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# subscriptions -- Odoo 19.0 Skill Reference

## Overview

Odoo Subscriptions manages recurring revenue products and services. It handles subscription creation, automatic invoicing, renewals, upselling, closures, and MRR/ARR reporting. Subscriptions are built on top of Sales Orders with recurring billing plans. Used by subscription-based businesses (SaaS, memberships, rentals, services) to manage the lifecycle from sign-up through renewal or churn.

## Key Concepts

- **Subscription**: A sales order with a recurring plan attached, generating periodic invoices.
- **Recurring Plan**: Defines the billing cadence (Monthly, Quarterly, Yearly, Weekly, etc.).
- **MRR (Monthly Recurring Revenue)**: Normalized monthly value of all active subscriptions.
- **ARR (Annual Recurring Revenue)**: MRR multiplied by 12.
- **Renewal**: The process of extending a subscription, either automatically or via a renewal quotation.
- **Upselling**: Adding products or upgrading a subscription mid-cycle via an upsell quotation.
- **Churn**: Loss of subscriptions due to cancellation or non-renewal.
- **Close Reason**: Categorized reason for subscription termination (voluntary churn, involuntary churn).
- **Automatic Payment**: Recurring charge processed via a registered payment token (credit card, direct debit).
- **Subscription Product**: A product configured with a recurring price on a pricelist.

## Core Workflows

### 1. Create a Subscription

1. Navigate to **Subscriptions > Orders > Quotations**, click **New**.
2. Select a **Customer**.
3. Select a **Recurring Plan** (e.g., Monthly, Yearly).
4. Add subscription products in the **Order Lines** tab. Products must have recurring prices configured on the pricelist.
5. Send the quotation; upon confirmation, the subscription becomes active.
6. Invoices are generated automatically according to the recurring plan.

### 2. Renew a Subscription

1. Open the subscription from **Subscriptions > Subscriptions**.
2. Click **Renew** to create a renewal quotation.
3. The renewal quotation pre-fills with the current subscription products.
4. Adjust products, quantities, or plan as needed.
5. Send and confirm the renewal quotation. The subscription period extends.

### 3. Upsell on a Subscription

1. Open an active subscription.
2. Click **Upsell** to create an upsell quotation.
3. Add new products or increase quantities.
4. Send and confirm the upsell quotation. New items are added to the subscription.

### 4. Close a Subscription

1. Open the subscription.
2. Click **Close** (or the subscription reaches its end date).
3. Select a **Close Reason** from the predefined list.
4. The subscription status changes to closed; recurring invoicing stops.

### 5. Configure Automatic Payments

1. Ensure an online payment provider is configured (Stripe, etc.).
2. The customer saves a payment token during their first payment.
3. On subsequent billing cycles, Odoo automatically charges the saved token.
4. Failed payments trigger retry logic and notifications.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `sale.order` | Subscriptions (extended SO with recurring fields) |
| `sale.order.line` | Subscription line items |
| `sale.temporal.recurrence` | Recurring plan definitions |
| `sale.order.close.reason` | Close/churn reasons |

### Key Fields on `sale.order` (Subscription-Specific)

| Field | Type | Description |
|-------|------|-------------|
| `is_subscription` | Boolean | Marks SO as a subscription |
| `recurrence_id` | Many2one | Recurring plan |
| `start_date` | Date | Subscription start |
| `next_invoice_date` | Date | Next billing date |
| `end_date` | Date | Subscription end date (if set) |
| `close_reason_id` | Many2one | Reason for closure |
| `subscription_state` | Selection | Subscription lifecycle state |
| `payment_token_id` | Many2one | Saved payment method for auto-billing |
| `recurring_monthly` | Monetary | MRR value |

### Reports

- **Subscriptions Analysis**: MRR, ARR, churn rate, retention.
- **Revenue KPIs**: Net new MRR, expansion MRR, churned MRR.
- **Renewal pipeline**: Subscriptions approaching renewal date.

### Menu Paths

- Subscriptions: `Subscriptions > Subscriptions`
- Quotations: `Subscriptions > Orders > Quotations`
- Close Reasons: `Subscriptions > Configuration > Close Reasons`
- Recurring Plans: `Subscriptions > Configuration > Recurring Plans`
- Reporting: `Subscriptions > Reporting`

## API / RPC Patterns

<!-- TODO: Subscription-specific external API examples not found in docs -->

Standard ORM access:

```python
# Search active subscriptions
env['sale.order'].search([('is_subscription', '=', True), ('subscription_state', '=', '3_progress')])

# Trigger manual invoice generation
subscription._create_recurring_invoice()
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not documented in the reviewed RST files. -->

- Subscriptions are fully integrated into `sale.order` (not a separate model). The `is_subscription` boolean flag distinguishes them.
- Recurring plans are configured via pricelists using the **Recurring Prices** tab.
- Automatic payment processing requires an online payment provider with tokenization support.

## Common Pitfalls

- **Products must have recurring pricelist rules**: A product without a recurring price entry on the pricelist will not bill correctly on subscriptions.
- **Payment token expiration**: If a customer's payment token expires or is revoked, automatic payments fail silently unless notifications are configured.
- **Close reason required for analytics**: Closing without a reason degrades churn reporting quality.
- **MRR normalization**: MRR is calculated by normalizing all plans to monthly; a yearly plan at $1200 shows $100 MRR.
- **Upsell vs. renewal confusion**: Upsell adds items to the current period; renewal extends the subscription period. Using the wrong action leads to billing errors.
