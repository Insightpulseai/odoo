# Billing Site Architecture

## Overview

The InsightPulse AI Billing Site is an Odoo-decoupled marketing and billing frontend built with:

- **Frontend**: Next.js 14 + React 18 + Tailwind CSS
- **Authentication**: Supabase Auth
- **Billing**: Paddle (checkout + subscription management)
- **Database**: Supabase PostgreSQL
- **Back-office**: Odoo CE (customer provisioning via JSON-RPC)
- **Automation**: n8n (optional workflow triggers)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Internet                                        │
│                                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│   │   Browser   │    │   Paddle    │    │    Odoo     │                     │
│   │   (User)    │    │  (Billing)  │    │  (ERP)      │                     │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                     │
│          │                  │                  │                             │
└──────────┼──────────────────┼──────────────────┼─────────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Vercel (Next.js App)                                 │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                        Next.js 14                                    │    │
│   │                                                                     │    │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │    │
│   │   │  Marketing   │  │    Auth      │  │   Account    │             │    │
│   │   │   Pages      │  │   Pages      │  │   Portal     │             │    │
│   │   └──────────────┘  └──────────────┘  └──────────────┘             │    │
│   │                                                                     │    │
│   │   ┌──────────────────────────────────────────────────────────────┐ │    │
│   │   │                    API Routes                                  │ │    │
│   │   │                                                                │ │    │
│   │   │   /api/webhooks/paddle    /api/provision/odoo                 │ │    │
│   │   │   (Webhook Handler)       (Odoo Sync)                         │ │    │
│   │   └──────────────────────────────────────────────────────────────┘ │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Supabase                                           │
│                                                                              │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│   │      Auth       │  │    Database     │  │   Edge Funcs    │             │
│   │   (Users)       │  │   (billing.*)   │  │   (Optional)    │             │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Sign Up Flow

```
User → Sign Up Page → Supabase Auth → Email Verification → Account Portal
```

### 2. Subscription Flow

```
User → Pricing Page → Select Plan → Paddle Checkout → Paddle Webhook →
  → Next.js Webhook Handler →
    → Supabase (billing.customers, billing.subscriptions) →
    → Odoo Provisioning (res.partner) →
    → Success Page
```

### 3. Webhook Processing

```
Paddle → POST /api/webhooks/paddle →
  1. Verify signature (HMAC-SHA256)
  2. Log event to billing.webhook_events
  3. Process event:
     - customer.created/updated → upsert billing.customers
     - subscription.created → create billing.subscriptions + provision Odoo
     - subscription.updated → update billing.subscriptions
     - subscription.canceled → mark as canceled
     - transaction.completed/paid → update billing.invoices
  4. Mark event as processed
```

## Database Schema

### billing.customers
- `paddle_customer_id` - Paddle customer ID (unique)
- `supabase_user_id` - Link to Supabase Auth user
- `email`, `name`, `company_name`
- `odoo_partner_id` - Link to Odoo res.partner

### billing.subscriptions
- `paddle_subscription_id` - Paddle subscription ID (unique)
- `customer_id` - FK to billing.customers
- `status` - trialing, active, paused, past_due, canceled
- `plan_name`, `price_id`, `product_id`
- `current_period_start`, `current_period_end`

### billing.invoices
- `paddle_transaction_id` - Paddle transaction ID (unique)
- `customer_id` - FK to billing.customers
- `status` - draft, ready, billed, paid, canceled, past_due
- `total`, `tax`, `currency_code`

## Security

### Row Level Security (RLS)

All billing tables have RLS enabled:
- Users can only read their own data (via `supabase_user_id`)
- Service role can read/write all data (for webhooks)

### Webhook Verification

Paddle webhooks are verified using HMAC-SHA256:
```
signature = HMAC-SHA256(timestamp + ":" + payload, webhook_secret)
```

### Odoo Authentication

JSON-RPC calls use:
1. Session authentication via `common.authenticate`
2. Credentials stored in environment variables
3. No secrets in codebase

## Integration Points

### Paddle → Next.js
- Webhook URL: `POST /api/webhooks/paddle`
- Events: customer.*, subscription.*, transaction.*

### Next.js → Supabase
- Auth: Supabase Auth (@supabase/ssr)
- Database: Supabase JS Client (service role for webhooks)

### Next.js → Odoo
- JSON-RPC: `POST /jsonrpc`
- Methods: `common.authenticate`, `object.execute_kw`
- Model: `res.partner` (customer records)

### Optional: n8n Integration
- Trigger: Supabase webhook on `billing.subscriptions` INSERT
- Actions:
  - Create Odoo customer (if webhook handler fails)
  - Create onboarding task in Odoo project
  - Trigger Databricks job for analytics

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |
| `NEXT_PUBLIC_PADDLE_CLIENT_TOKEN` | Paddle client token |
| `PADDLE_API_KEY` | Paddle API key (server-side) |
| `PADDLE_WEBHOOK_SECRET` | Paddle webhook signing secret |
| `NEXT_PUBLIC_PADDLE_PRICE_ID_*` | Paddle price IDs |
| `ODOO_BASE_URL` | Odoo instance URL |
| `ODOO_DB` | Odoo database name |
| `ODOO_USER` | Odoo API user email |
| `ODOO_PASSWORD` | Odoo API user password |

## Deployment

### Vercel
- Framework: Next.js
- Build Command: `pnpm build`
- Output Directory: `.next`

### Supabase
- Run migrations: `supabase db push`
- Deploy edge functions: `supabase functions deploy`

## Monitoring

### Key Metrics
- Webhook processing latency
- Subscription conversion rate
- Odoo provisioning success rate

### Error Tracking
- Failed webhooks logged to `billing.webhook_events.error`
- Odoo provisioning failures logged (non-blocking)
