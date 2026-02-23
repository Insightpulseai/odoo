# Supabase Email Events Pack

**Complete integration layer for email events between Odoo, Mailgun, and Supabase**

## Overview

The Supabase Email Events Pack extends the Odoo Email Parity Pack by creating a centralized event storage and analytics layer in Supabase. This enables:

- **Centralized Event Storage**: All email events across systems in one place
- **Real-time Dashboards**: Live email performance monitoring
- **BI Analytics**: Advanced analytics and reporting with SQL
- **Cross-System Integration**: Connect Odoo, n8n, MCP, and other services
- **Recipient Intelligence**: Engagement scoring and quality metrics

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     TBWA Email Infrastructure                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Odoo Mail                                                              │
│   (Email Parity Pack)                                                    │
│         │                                                                │
│         ├──► Mailgun                                                     │
│         │    (send emails)                                               │
│         │         │                                                      │
│         │         ├──► Webhook Events                                    │
│         │         │         │                                            │
│         │         │         ├──► Supabase Edge Function                 │
│         │         │         │    (mailgun-events-proxy)                 │
│         │         │         │         │                                  │
│         │         │         │         ├──► HMAC Signature Verification  │
│         │         │         │         │                                  │
│         │         │         │         └──► PostgreSQL (email schema)    │
│         │         │         │                   │                        │
│         │         │         │                   ├──► email.events       │
│         │         │         │                   │    (raw events)        │
│         │         │         │                   │                        │
│         │         │         │                   ├──► Trigger            │
│         │         │         │                   │    (auto-aggregate)    │
│         │         │         │                   │                        │
│         │         │         │                   ├──► email.recipient_engagement │
│         │         │         │                   │    (quality scoring)   │
│         │         │         │                   │                        │
│         │         │         │                   └──► email.daily_stats  │
│         │         │         │                        (daily rollups)     │
│         │         │         │                                            │
│         │         │         └──► Realtime Broadcast                     │
│         │         │                   │                                  │
│         │         │                   ├──► Live Dashboards              │
│         │         │                   ├──► n8n Workflows                │
│         │         │                   └──► MCP Integrations             │
│         │         │                                                      │
│         │         └──► BI Queries                                        │
│         │              (daily_performance materialized view)             │
│         │                                                                │
│         └──► Sync Back (optional)                                        │
│              (update Odoo with engagement scores)                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

1. **Supabase Project**: Active project with credentials
2. **Mailgun Account**: API key and domain configured
3. **Odoo Email Parity Pack**: Installed and operational
4. **Supabase CLI**: Installed (`brew install supabase/tap/supabase`)
5. **Environment Variables**: All credentials configured

### Environment Setup

```bash
# Supabase
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export SUPABASE_PROJECT_REF="spdtwktxdalcfigzeqrz"

# Mailgun
export MAILGUN_WEBHOOK_SIGNING_KEY="your-webhook-signing-key"
export MAILGUN_API_KEY="your-api-key"
export MAILGUN_DOMAIN="your-domain.com"

# PostgreSQL (Supabase direct connection)
export POSTGRES_URL="postgresql://postgres.[ref]:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
```

### Installation

#### 1. Deploy Database Schema

```bash
# Using psql (recommended)
psql "$POSTGRES_URL" -f db/migrations/20260128_email_events_schema.sql

# OR using Supabase CLI
cd db/migrations
supabase db push
```

**What Gets Created**:
- `email` schema
- `email.events` table (raw events with JSONB)
- `email.daily_stats` table (daily aggregations)
- `email.recipient_engagement` table (quality scoring)
- RLS policies (service role full access, authenticated read-only)
- Indexes (GIN for JSONB, B-tree for queries)
- Functions (`calculate_engagement_score`, `refresh_daily_stats`)
- Triggers (auto-update recipient engagement)

#### 2. Deploy Edge Function

```bash
# Login to Supabase CLI (if not already)
supabase login

# Link to project
supabase link --project-ref $SUPABASE_PROJECT_REF

# Set Edge Function secrets
supabase secrets set MAILGUN_WEBHOOK_SIGNING_KEY="$MAILGUN_WEBHOOK_SIGNING_KEY"

# Deploy Edge Function
cd db/functions/mailgun-events-proxy
supabase functions deploy mailgun-events-proxy
```

**Function URL**: `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/mailgun-events-proxy`

#### 3. Configure Mailgun Webhook

```bash
# Set webhook URL in Mailgun
curl -u "api:${MAILGUN_API_KEY}" \
    https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/webhooks \
    -F id=tracking \
    -F url="https://${SUPABASE_PROJECT_REF}.supabase.co/functions/v1/mailgun-events-proxy"
```

#### 4. Verify Installation

```bash
# Run verification script
./scripts/supabase/verify-integration.sh

# Test webhook delivery
./scripts/supabase/test-webhook.sh
```

---

## Database Schema

### Tables

#### `email.events` - Raw Email Events

Primary storage for all Mailgun webhook events.

```sql
CREATE TABLE email.events (
    id UUID PRIMARY KEY,
    event_type TEXT NOT NULL,           -- delivered, opened, clicked, bounced, etc.
    event_timestamp TIMESTAMPTZ NOT NULL,
    message_id TEXT NOT NULL,
    recipient TEXT NOT NULL,
    sender TEXT,
    subject TEXT,

    -- Mailgun metadata
    mailgun_id TEXT,
    mailgun_timestamp BIGINT,
    mailgun_token TEXT,
    mailgun_signature TEXT,

    -- Delivery data
    delivery_status TEXT,
    delivery_code INTEGER,
    delivery_description TEXT,
    delivery_message TEXT,

    -- Engagement data (opens/clicks)
    client_type TEXT,                   -- web, mobile, desktop
    client_os TEXT,                     -- iOS, Android, Windows, macOS
    client_name TEXT,                   -- Gmail, Outlook, Apple Mail
    device_type TEXT,                   -- mobile, desktop, tablet
    user_agent TEXT,
    ip_address INET,
    country TEXT,
    region TEXT,
    city TEXT,

    -- Link tracking (clicks)
    url TEXT,

    -- Error data (bounces/failures)
    error_code TEXT,
    error_reason TEXT,
    severity TEXT,                      -- permanent, temporary

    -- Campaign tracking
    tags TEXT[],                        -- Mailgun tags
    campaigns TEXT[],                   -- Campaign IDs
    user_variables JSONB,               -- Custom variables

    -- Full payload (for reprocessing)
    raw_payload JSONB NOT NULL,

    -- Housekeeping
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,

    CONSTRAINT unique_mailgun_event UNIQUE (mailgun_id, event_type, event_timestamp)
);
```

**Indexes**:
- `message_id` - Fast lookups by message
- `recipient` - Fast lookups by recipient
- `event_type` - Filter by event type
- `event_timestamp` - Time-range queries
- `tags` (GIN) - Array contains queries
- `raw_payload` (GIN) - JSONB queries

#### `email.daily_stats` - Daily Aggregations

Pre-computed daily statistics for performance.

```sql
CREATE TABLE email.daily_stats (
    id UUID PRIMARY KEY,
    stat_date DATE NOT NULL,

    -- Volume metrics
    total_sent INTEGER DEFAULT 0,
    total_delivered INTEGER DEFAULT 0,
    total_failed INTEGER DEFAULT 0,
    total_bounced INTEGER DEFAULT 0,
    total_complained INTEGER DEFAULT 0,

    -- Engagement metrics
    total_opened INTEGER DEFAULT 0,
    total_clicked INTEGER DEFAULT 0,
    unique_opens INTEGER DEFAULT 0,     -- Distinct message_ids
    unique_clicks INTEGER DEFAULT 0,

    -- Calculated rates (%)
    delivery_rate NUMERIC(5,2),
    bounce_rate NUMERIC(5,2),
    open_rate NUMERIC(5,2),
    click_rate NUMERIC(5,2),
    complaint_rate NUMERIC(5,2),

    -- Optional segmentation
    sender TEXT,
    campaign TEXT,
    tags TEXT[],

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_daily_stat UNIQUE (stat_date, sender, campaign)
);
```

#### `email.recipient_engagement` - Recipient Quality Scoring

Per-recipient engagement metrics and quality scoring.

```sql
CREATE TABLE email.recipient_engagement (
    id UUID PRIMARY KEY,
    recipient TEXT UNIQUE NOT NULL,

    -- Lifetime metrics
    total_received INTEGER DEFAULT 0,
    total_delivered INTEGER DEFAULT 0,
    total_bounced INTEGER DEFAULT 0,
    total_opened INTEGER DEFAULT 0,
    total_clicked INTEGER DEFAULT 0,
    total_complained INTEGER DEFAULT 0,
    total_unsubscribed INTEGER DEFAULT 0,

    -- Last activity timestamps
    last_sent_at TIMESTAMPTZ,
    last_delivered_at TIMESTAMPTZ,
    last_opened_at TIMESTAMPTZ,
    last_clicked_at TIMESTAMPTZ,
    last_bounced_at TIMESTAMPTZ,
    last_complained_at TIMESTAMPTZ,

    -- Calculated engagement score (0-100)
    engagement_score INTEGER DEFAULT 50,

    -- Status flags
    is_valid BOOLEAN DEFAULT TRUE,
    is_suppressed BOOLEAN DEFAULT FALSE,
    suppression_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Functions

#### `calculate_engagement_score(recipient_email TEXT) → INTEGER`

Calculates engagement quality score (0-100) for a recipient.

**Algorithm**:
```
Base Score: 50 (neutral)
+ Open Rate × 30 (up to +30)
+ Click Rate × 40 (up to +40)
- Bounce Rate × 50 (up to -50)
- Complaint Rate × 100 (up to -100)
= Final Score (clamped 0-100)
```

**Usage**:
```sql
SELECT email.calculate_engagement_score('user@example.com');
-- Returns: 75
```

#### `refresh_daily_stats(target_date DATE DEFAULT CURRENT_DATE)`

Recalculates daily statistics for a specific date.

**Usage**:
```sql
-- Refresh today's stats
SELECT email.refresh_daily_stats();

-- Refresh specific date
SELECT email.refresh_daily_stats('2026-01-28');

-- Schedule with pg_cron (runs at 1 AM daily)
SELECT cron.schedule(
    'refresh-email-stats',
    '0 1 * * *',
    $$SELECT email.refresh_daily_stats(CURRENT_DATE - INTERVAL '1 day')$$
);
```

### Triggers

#### `update_recipient_engagement_trigger`

Automatically updates `email.recipient_engagement` when new events are inserted.

**Behavior**:
- Increments counters based on event type
- Updates last activity timestamps
- Recalculates engagement score
- Creates recipient record if not exists

---

## Edge Function

### `mailgun-events-proxy`

Deno-based Edge Function that receives Mailgun webhooks and stores events in Supabase.

**Endpoint**: `https://[project-ref].supabase.co/functions/v1/mailgun-events-proxy`

**Features**:
- ✅ HMAC-SHA256 signature verification
- ✅ Event transformation (Mailgun → Supabase schema)
- ✅ CORS support
- ✅ Error handling with detailed logs
- ✅ Service role authentication
- ✅ Full payload preservation (raw_payload JSONB)

**Signature Verification**:
```typescript
function verifyMailgunSignature(
  timestamp: string,
  token: string,
  signature: string,
  signingKey: string
): boolean {
  const hmac = createHmac('sha256', signingKey)
  hmac.update(`${timestamp}${token}`)
  const digest = hmac.digest('hex')
  return digest === signature
}
```

**Event Transformation**:
```typescript
function transformEvent(webhook: MailgunWebhook): EmailEventInsert {
  const eventData = webhook['event-data']
  return {
    event_type: eventData.event,
    event_timestamp: new Date(eventData.timestamp * 1000).toISOString(),
    message_id: eventData['Message-Id'],
    recipient: eventData.recipient,
    // ... all other fields
    raw_payload: webhook
  }
}
```

**Testing**:
```bash
# Test with sample payload
./scripts/supabase/test-webhook.sh

# View Edge Function logs
supabase functions logs mailgun-events-proxy --follow
```

---

## TypeScript Types

Location: `db/types/email_events.ts`

### Core Types

```typescript
export type EmailEventType =
  | 'delivered'
  | 'failed'
  | 'opened'
  | 'clicked'
  | 'unsubscribed'
  | 'complained'
  | 'stored'
  | 'accepted'
  | 'rejected'
  | 'permanent_fail'
  | 'temporary_fail'

export interface EmailEvent {
  id: string
  event_type: EmailEventType
  event_timestamp: string
  message_id: string
  recipient: string
  sender?: string
  subject?: string
  // ... all other fields
  raw_payload: Record<string, any>
  created_at: string
  processed: boolean
}

export interface EmailDailyStat {
  id: string
  stat_date: string
  total_sent: number
  total_delivered: number
  // ... all metrics
  delivery_rate: number
  open_rate: number
  click_rate: number
}

export interface RecipientEngagement {
  id: string
  recipient: string
  total_received: number
  total_opened: number
  total_clicked: number
  engagement_score: number
  is_valid: boolean
  is_suppressed: boolean
}
```

### Database Type

```typescript
export interface Database {
  email: {
    Tables: {
      events: {
        Row: EmailEvent
        Insert: EmailEventInsert
        Update: Partial<EmailEventInsert>
      }
      daily_stats: {
        Row: EmailDailyStat
        Insert: Omit<EmailDailyStat, 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Omit<EmailDailyStat, 'id' | 'created_at'>>
      }
      recipient_engagement: {
        Row: RecipientEngagement
        Insert: Omit<RecipientEngagement, 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Omit<RecipientEngagement, 'id' | 'created_at'>>
      }
    }
    Functions: {
      calculate_engagement_score: {
        Args: { recipient_email: string }
        Returns: number
      }
      refresh_daily_stats: {
        Args: { target_date?: string }
        Returns: void
      }
    }
  }
}
```

### Usage in Applications

```typescript
import { createClient } from '@supabase/supabase-js'
import type { Database, EmailEvent } from './types/email_events'

const supabase = createClient<Database>(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
)

// Type-safe query
const { data, error } = await supabase
  .from('email.events')
  .select('*')
  .eq('event_type', 'delivered')
  .gte('event_timestamp', '2026-01-01')

if (data) {
  const events: EmailEvent[] = data
  console.log(`Found ${events.length} delivered events`)
}
```

---

## Realtime Subscriptions

Location: `db/examples/realtime_subscription.ts`

### Basic Subscription

```typescript
import { createClient } from '@supabase/supabase-js'
import type { Database, EmailEvent } from '../types/email_events'

const supabase = createClient<Database>(SUPABASE_URL, SUPABASE_ANON_KEY)

// Subscribe to all new events
export function subscribeToAllEvents(
  onEvent: (event: EmailEvent) => void
) {
  const channel = supabase
    .channel('email-events-all')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'email',
        table: 'events',
      },
      (payload) => {
        console.log('New email event:', payload.new)
        onEvent(payload.new as EmailEvent)
      }
    )
    .subscribe()

  return () => channel.unsubscribe()
}

// Usage
const unsubscribe = subscribeToAllEvents((event) => {
  console.log('Received event:', event.event_type, event.recipient)
})
```

### Filtered Subscription

```typescript
// Subscribe to specific event type
export function subscribeToEventType(
  eventType: string,
  onEvent: (event: EmailEvent) => void
) {
  const channel = supabase
    .channel(`email-events-${eventType}`)
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'email',
        table: 'events',
        filter: `event_type=eq.${eventType}`,
      },
      (payload) => {
        onEvent(payload.new as EmailEvent)
      }
    )
    .subscribe()

  return () => channel.unsubscribe()
}

// Usage
const unsubscribe = subscribeToEventType('bounced', (event) => {
  alert(`Email to ${event.recipient} bounced!`)
})
```

### Live Dashboard Stats

```typescript
interface LiveStats {
  total: number
  delivered: number
  failed: number
  bounced: number
  opened: number
  clicked: number
}

export function subscribeToDashboardStats(
  onStatsUpdate: (stats: LiveStats) => void,
  intervalMs: number = 5000
) {
  let stats: LiveStats = {
    total: 0,
    delivered: 0,
    failed: 0,
    bounced: 0,
    opened: 0,
    clicked: 0,
  }

  // Subscribe to new events
  const channel = supabase
    .channel('email-dashboard-stats')
    .on('postgres_changes', { ... }, (payload) => {
      const event = payload.new as EmailEvent
      stats.total++
      switch (event.event_type) {
        case 'delivered': stats.delivered++; break
        case 'failed': stats.failed++; break
        case 'bounced': stats.bounced++; break
        case 'opened': stats.opened++; break
        case 'clicked': stats.clicked++; break
      }
      onStatsUpdate({ ...stats })
    })
    .subscribe()

  // Also refresh from database periodically
  const refreshInterval = setInterval(async () => {
    const { data } = await supabase
      .from('email.events')
      .select('event_type')
      .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())

    // Recalculate stats
    onStatsUpdate({ ...stats })
  }, intervalMs)

  return () => {
    channel.unsubscribe()
    clearInterval(refreshInterval)
  }
}
```

### React Hook Integration

```typescript
import React from 'react'

export function useRealtimeEmailEvents(
  eventType?: string,
  recipient?: string
): EmailEvent[] {
  const [events, setEvents] = React.useState<EmailEvent[]>([])

  React.useEffect(() => {
    let channelName = 'email-events'
    let filter: any = {
      event: 'INSERT',
      schema: 'email',
      table: 'events',
    }

    if (eventType) {
      channelName += `-${eventType}`
      filter.filter = `event_type=eq.${eventType}`
    } else if (recipient) {
      channelName += `-${recipient}`
      filter.filter = `recipient=eq.${recipient}`
    }

    const channel = supabase
      .channel(channelName)
      .on('postgres_changes', filter, (payload) => {
        setEvents((prev) => [payload.new as EmailEvent, ...prev].slice(0, 100))
      })
      .subscribe()

    return () => channel.unsubscribe()
  }, [eventType, recipient])

  return events
}

// Usage in React component
function EmailDashboard() {
  const events = useRealtimeEmailEvents()
  const bounces = useRealtimeEmailEvents('bounced')

  return (
    <div>
      <h2>Recent Events: {events.length}</h2>
      <h2>Recent Bounces: {bounces.length}</h2>
      {events.map(event => (
        <div key={event.id}>{event.event_type} - {event.recipient}</div>
      ))}
    </div>
  )
}
```

---

## BI Queries

Location: `db/sql/bi_queries.sql`

Ready-to-use SQL queries for dashboards and analytics.

### Daily Trends

```sql
-- Daily email volume trend (last 30 days)
SELECT
    DATE(event_timestamp) AS date,
    COUNT(*) FILTER (WHERE event_type IN ('delivered', 'failed', 'bounced')) AS sent,
    COUNT(*) FILTER (WHERE event_type = 'delivered') AS delivered,
    COUNT(*) FILTER (WHERE event_type IN ('failed', 'temporary_fail')) AS failed,
    COUNT(*) FILTER (WHERE event_type IN ('bounced', 'permanent_fail')) AS bounced,
    COUNT(*) FILTER (WHERE event_type = 'opened') AS opened,
    COUNT(*) FILTER (WHERE event_type = 'clicked') AS clicked
FROM email.events
WHERE event_timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE(event_timestamp)
ORDER BY date DESC;
```

### Engagement Funnel

```sql
-- Overall engagement funnel (last 7 days)
WITH funnel AS (
    SELECT
        COUNT(*) FILTER (WHERE event_type IN ('delivered', 'failed', 'bounced')) AS sent,
        COUNT(*) FILTER (WHERE event_type = 'delivered') AS delivered,
        COUNT(DISTINCT message_id) FILTER (WHERE event_type = 'opened') AS opened,
        COUNT(DISTINCT message_id) FILTER (WHERE event_type = 'clicked') AS clicked
    FROM email.events
    WHERE event_timestamp >= NOW() - INTERVAL '7 days'
)
SELECT
    sent,
    delivered,
    opened,
    clicked,
    ROUND((delivered::NUMERIC / NULLIF(sent, 0)) * 100, 2) AS delivery_rate,
    ROUND((opened::NUMERIC / NULLIF(delivered, 0)) * 100, 2) AS open_rate,
    ROUND((clicked::NUMERIC / NULLIF(delivered, 0)) * 100, 2) AS click_rate
FROM funnel;
```

### Sender Performance

```sql
-- Top senders by volume (last 30 days)
SELECT
    sender,
    COUNT(*) FILTER (WHERE event_type = 'delivered') AS emails_sent,
    COUNT(DISTINCT message_id) FILTER (WHERE event_type = 'opened') AS unique_opens,
    COUNT(DISTINCT message_id) FILTER (WHERE event_type = 'clicked') AS unique_clicks,
    ROUND(
        (COUNT(DISTINCT message_id) FILTER (WHERE event_type = 'opened')::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'delivered'), 0)) * 100,
        2
    ) AS open_rate
FROM email.events
WHERE event_timestamp >= NOW() - INTERVAL '30 days'
    AND sender IS NOT NULL
GROUP BY sender
ORDER BY emails_sent DESC
LIMIT 10;
```

### Top Engaged Recipients

```sql
-- Top engaged recipients (last 30 days)
SELECT
    recipient,
    COUNT(*) FILTER (WHERE event_type = 'delivered') AS emails_received,
    COUNT(*) FILTER (WHERE event_type = 'opened') AS total_opens,
    COUNT(*) FILTER (WHERE event_type = 'clicked') AS total_clicks,
    MAX(event_timestamp) FILTER (WHERE event_type = 'opened') AS last_opened_at
FROM email.events
WHERE event_timestamp >= NOW() - INTERVAL '30 days'
GROUP BY recipient
HAVING COUNT(*) FILTER (WHERE event_type = 'opened') > 0
ORDER BY total_opens DESC, total_clicks DESC
LIMIT 20;
```

### Bounce Analysis

```sql
-- Bounce reasons (last 30 days)
SELECT
    error_reason,
    severity,
    COUNT(*) AS count,
    COUNT(DISTINCT recipient) AS unique_recipients
FROM email.events
WHERE event_timestamp >= NOW() - INTERVAL '30 days'
    AND event_type IN ('failed', 'bounced', 'permanent_fail', 'temporary_fail')
    AND error_reason IS NOT NULL
GROUP BY error_reason, severity
ORDER BY count DESC
LIMIT 20;
```

### Materialized View for Performance

```sql
-- Create materialized view for faster dashboard queries
CREATE MATERIALIZED VIEW IF NOT EXISTS email.daily_performance AS
SELECT
    DATE(event_timestamp) AS date,
    COUNT(*) FILTER (WHERE event_type IN ('delivered', 'failed', 'bounced')) AS sent,
    COUNT(*) FILTER (WHERE event_type = 'delivered') AS delivered,
    COUNT(DISTINCT message_id) FILTER (WHERE event_type = 'opened') AS unique_opens,
    COUNT(DISTINCT message_id) FILTER (WHERE event_type = 'clicked') AS unique_clicks,
    ROUND(
        (COUNT(*) FILTER (WHERE event_type = 'delivered')::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE event_type IN ('delivered', 'failed', 'bounced')), 0)) * 100,
        2
    ) AS delivery_rate
FROM email.events
GROUP BY DATE(event_timestamp);

-- Create index
CREATE UNIQUE INDEX idx_daily_performance_date ON email.daily_performance(date DESC);

-- Refresh daily via pg_cron
SELECT cron.schedule(
    'refresh-materialized-view',
    '0 2 * * *',  -- 2 AM daily
    $$REFRESH MATERIALIZED VIEW CONCURRENTLY email.daily_performance$$
);
```

---

## Integration Patterns

### Odoo Integration

Sync engagement scores back to Odoo for email validation and marketing campaigns.

```python
# Odoo module: mail.parity.supabase_sync

import requests
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    email_engagement_score = fields.Integer(
        string='Email Engagement Score',
        help='Score from 0-100 based on email interaction history',
        readonly=True
    )
    email_is_valid = fields.Boolean(
        string='Email Valid',
        default=True,
        readonly=True
    )
    email_is_suppressed = fields.Boolean(
        string='Email Suppressed',
        default=False,
        readonly=True
    )

    def _cron_sync_email_engagement(self):
        """Sync engagement scores from Supabase"""
        supabase_url = self.env['ir.config_parameter'].sudo().get_param('supabase.url')
        supabase_key = self.env['ir.config_parameter'].sudo().get_param('supabase.service_role_key')

        for partner in self.search([('email', '!=', False)]):
            response = requests.get(
                f"{supabase_url}/rest/v1/email.recipient_engagement",
                params={'recipient': f'eq.{partner.email}', 'select': '*'},
                headers={
                    'apikey': supabase_key,
                    'Authorization': f'Bearer {supabase_key}'
                }
            )

            if response.status_code == 200 and response.json():
                data = response.json()[0]
                partner.write({
                    'email_engagement_score': data['engagement_score'],
                    'email_is_valid': data['is_valid'],
                    'email_is_suppressed': data['is_suppressed']
                })
```

### n8n Workflow Integration

Trigger n8n workflows on specific email events.

```json
{
  "name": "Email Event Handler",
  "nodes": [
    {
      "parameters": {
        "url": "={{$env.SUPABASE_URL}}/rest/v1/email.events",
        "authentication": "headerAuth",
        "headerAuth": {
          "name": "apikey",
          "value": "={{$env.SUPABASE_SERVICE_ROLE_KEY}}"
        },
        "options": {
          "realtimeDatabase": true
        }
      },
      "name": "Supabase Realtime",
      "type": "n8n-nodes-base.supabaseTrigger"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json.event_type}}",
              "value2": "bounced"
            }
          ]
        }
      },
      "name": "Is Bounce?",
      "type": "n8n-nodes-base.if"
    },
    {
      "parameters": {
        "url": "={{$env.ODOO_URL}}/xmlrpc/2/object",
        "method": "POST",
        "jsonParameters": true,
        "options": {},
        "bodyParametersJson": "={{\n  \"params\": {\n    \"db\": \"odoo_core\",\n    \"uid\": 2,\n    \"password\": \"{{$env.ODOO_API_KEY}}\",\n    \"model\": \"res.partner\",\n    \"method\": \"search_read\",\n    \"args\": [\n      [[\"email\", \"=\", \"{{$json.recipient}}\"]],\n      [\"id\", \"name\", \"email\"]\n    ]\n  }\n}}"
      },
      "name": "Find Partner in Odoo",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "parameters": {
        "url": "={{$env.ODOO_URL}}/xmlrpc/2/object",
        "method": "POST",
        "jsonParameters": true,
        "bodyParametersJson": "={{\n  \"params\": {\n    \"db\": \"odoo_core\",\n    \"uid\": 2,\n    \"password\": \"{{$env.ODOO_API_KEY}}\",\n    \"model\": \"res.partner\",\n    \"method\": \"write\",\n    \"args\": [\n      [{{$json.id}}],\n      {\"email_is_valid\": false, \"email_is_suppressed\": true}\n    ]\n  }\n}}"
      },
      "name": "Mark Email Invalid in Odoo",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### MCP Server Integration

Create MCP server for email analytics queries.

```typescript
// mcp/servers/email-analytics-server/index.ts

import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { createClient } from '@supabase/supabase-js'
import type { Database } from './types/email_events'

const supabase = createClient<Database>(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

const server = new Server({
  name: 'email-analytics-server',
  version: '1.0.0'
})

server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'get_email_stats',
      description: 'Get email statistics for a date range',
      inputSchema: {
        type: 'object',
        properties: {
          start_date: { type: 'string' },
          end_date: { type: 'string' },
          sender: { type: 'string' }
        },
        required: ['start_date', 'end_date']
      }
    },
    {
      name: 'get_recipient_engagement',
      description: 'Get engagement score for a recipient',
      inputSchema: {
        type: 'object',
        properties: {
          email: { type: 'string' }
        },
        required: ['email']
      }
    }
  ]
}))

server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'get_email_stats') {
    const { start_date, end_date, sender } = request.params.arguments

    let query = supabase
      .from('email.events')
      .select('event_type')
      .gte('event_timestamp', start_date)
      .lte('event_timestamp', end_date)

    if (sender) {
      query = query.eq('sender', sender)
    }

    const { data, error } = await query

    if (error) throw error

    const stats = {
      total: data.length,
      delivered: data.filter(e => e.event_type === 'delivered').length,
      opened: data.filter(e => e.event_type === 'opened').length,
      clicked: data.filter(e => e.event_type === 'clicked').length,
      bounced: data.filter(e => e.event_type === 'bounced').length
    }

    return {
      content: [{ type: 'text', text: JSON.stringify(stats, null, 2) }]
    }
  }

  if (request.params.name === 'get_recipient_engagement') {
    const { email } = request.params.arguments

    const { data, error } = await supabase
      .from('email.recipient_engagement')
      .select('*')
      .eq('recipient', email)
      .single()

    if (error) throw error

    return {
      content: [{ type: 'text', text: JSON.stringify(data, null, 2) }]
    }
  }

  throw new Error('Unknown tool')
})
```

---

## Testing

### Verification Script

```bash
# Full verification
./scripts/supabase/verify-integration.sh

# Expected output:
# ✓ SUPABASE_URL is set
# ✓ SUPABASE_ANON_KEY is set
# ✓ SUPABASE_SERVICE_ROLE_KEY is set
# ✓ Supabase CLI installed
# ✓ email schema exists
# ✓ email.events table exists
# ✓ email.daily_stats table exists
# ✓ email.recipient_engagement table exists
# ✓ mailgun-events-proxy function is deployed
# ✓ Test event inserted successfully
# ✓ All critical checks passed!
```

### Webhook Test

```bash
# Test webhook delivery
./scripts/supabase/test-webhook.sh

# Expected output:
# Testing Mailgun Events Proxy Edge Function
# URL: https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/mailgun-events-proxy
#
# Sending test webhook...
#
# Response:
# HTTP Status: 200
# Body: {"ok":true,"event_id":"...","event_type":"delivered","recipient":"test@example.com"}
#
# ✓ Webhook test successful!
```

### Manual Testing

```bash
# 1. Send test email via Odoo
# (Odoo Mail Parity Pack must be installed)

# 2. Check Mailgun logs
curl -u "api:${MAILGUN_API_KEY}" \
    https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/events

# 3. Check Supabase events table
psql "$POSTGRES_URL" -c "
SELECT id, event_type, recipient, event_timestamp
FROM email.events
ORDER BY created_at DESC
LIMIT 10;
"

# 4. Check engagement score
psql "$POSTGRES_URL" -c "
SELECT recipient, engagement_score, total_opened, total_clicked
FROM email.recipient_engagement
WHERE recipient = 'test@example.com';
"
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Supabase project provisioned
- [ ] PostgreSQL connection string obtained
- [ ] Mailgun webhook signing key obtained
- [ ] Environment variables configured
- [ ] Database schema deployed and verified
- [ ] Edge Function deployed and tested
- [ ] Mailgun webhook configured and tested
- [ ] RLS policies verified
- [ ] Monitoring configured (pg_cron, dashboards)
- [ ] Backup strategy in place

### Deployment Steps

```bash
# 1. Set production environment variables
export SUPABASE_URL="https://[prod-ref].supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="[prod-service-role-key]"
export MAILGUN_WEBHOOK_SIGNING_KEY="[prod-signing-key]"

# 2. Deploy database schema
psql "$POSTGRES_URL" -f db/migrations/20260128_email_events_schema.sql

# 3. Deploy Edge Function
supabase functions deploy mailgun-events-proxy --project-ref [prod-ref]

# 4. Set Edge Function secrets
supabase secrets set MAILGUN_WEBHOOK_SIGNING_KEY="$MAILGUN_WEBHOOK_SIGNING_KEY" \
    --project-ref [prod-ref]

# 5. Configure Mailgun webhook
curl -u "api:${MAILGUN_API_KEY}" \
    https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/webhooks \
    -F id=tracking \
    -F url="https://[prod-ref].supabase.co/functions/v1/mailgun-events-proxy"

# 6. Verify deployment
./scripts/supabase/verify-integration.sh
./scripts/supabase/test-webhook.sh

# 7. Configure pg_cron for daily stats
psql "$POSTGRES_URL" -c "
SELECT cron.schedule(
    'refresh-email-stats',
    '0 1 * * *',
    \$\$SELECT email.refresh_daily_stats(CURRENT_DATE - INTERVAL '1 day')\$\$
);

SELECT cron.schedule(
    'refresh-materialized-view',
    '0 2 * * *',
    \$\$REFRESH MATERIALIZED VIEW CONCURRENTLY email.daily_performance\$\$
);
"

# 8. Enable Supabase Realtime
# Dashboard → Database → Replication → Enable realtime for email schema
```

### Monitoring

```sql
-- Check event ingestion rate
SELECT
    DATE_TRUNC('hour', created_at) AS hour,
    COUNT(*) AS events_per_hour
FROM email.events
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- Check Edge Function errors (requires logs access)
-- supabase functions logs mailgun-events-proxy --filter "error"

-- Check recipient engagement distribution
SELECT
    CASE
        WHEN engagement_score >= 80 THEN 'High (80-100)'
        WHEN engagement_score >= 60 THEN 'Medium (60-79)'
        WHEN engagement_score >= 40 THEN 'Low (40-59)'
        ELSE 'Very Low (0-39)'
    END AS engagement_tier,
    COUNT(*) AS recipient_count
FROM email.recipient_engagement
GROUP BY engagement_tier
ORDER BY MIN(engagement_score) DESC;

-- Check suppressed recipients
SELECT COUNT(*) AS suppressed_count
FROM email.recipient_engagement
WHERE is_suppressed = true;
```

---

## Troubleshooting

### Edge Function Not Receiving Webhooks

**Symptoms**: No events in `email.events` table

**Diagnosis**:
```bash
# 1. Check Mailgun webhook configuration
curl -u "api:${MAILGUN_API_KEY}" \
    https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/webhooks

# 2. Check Edge Function logs
supabase functions logs mailgun-events-proxy --tail

# 3. Test Edge Function directly
./scripts/supabase/test-webhook.sh
```

**Solutions**:
- Verify webhook URL in Mailgun matches Edge Function URL
- Check MAILGUN_WEBHOOK_SIGNING_KEY is set in Edge Function secrets
- Verify Edge Function is deployed (`supabase functions list`)

### Signature Verification Failing

**Symptoms**: HTTP 403 "Invalid signature" from Edge Function

**Diagnosis**:
```bash
# Check webhook signing key
supabase secrets list | grep MAILGUN_WEBHOOK_SIGNING_KEY
```

**Solutions**:
- Verify signing key matches Mailgun domain webhook signing key
- For testing, temporarily disable signature verification in Edge Function
- Check Mailgun webhook format (should be "JSON" not "Legacy")

### Missing Events

**Symptoms**: Some events not appearing in database

**Diagnosis**:
```sql
-- Check for constraint violations
SELECT COUNT(*) FROM email.events;

-- Check for duplicate events (would be rejected by unique constraint)
SELECT mailgun_id, event_type, event_timestamp, COUNT(*)
FROM email.events
GROUP BY mailgun_id, event_type, event_timestamp
HAVING COUNT(*) > 1;
```

**Solutions**:
- Check Edge Function logs for insertion errors
- Verify database constraints are not too restrictive
- Check for network issues between Mailgun and Supabase

### Engagement Score Not Updating

**Symptoms**: Recipient engagement score stays at 50 (neutral)

**Diagnosis**:
```sql
-- Check trigger function
SELECT tgname, tgtype, tgenabled
FROM pg_trigger
WHERE tgname = 'update_recipient_engagement_trigger';

-- Check function exists
SELECT proname FROM pg_proc WHERE proname = 'update_recipient_engagement';
```

**Solutions**:
- Verify trigger is enabled
- Check trigger function logic in migration SQL
- Manually call `SELECT email.calculate_engagement_score('test@example.com')`

### Performance Issues

**Symptoms**: Slow queries, high database load

**Diagnosis**:
```sql
-- Check query performance
EXPLAIN ANALYZE
SELECT * FROM email.events
WHERE recipient = 'test@example.com'
  AND event_timestamp >= NOW() - INTERVAL '30 days';

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'email'
ORDER BY idx_scan;
```

**Solutions**:
- Verify indexes are present (`\di email.*` in psql)
- Use materialized views for dashboard queries
- Implement table partitioning for large datasets
- Schedule VACUUM ANALYZE during off-peak hours

---

## Best Practices

### Security

1. **Always verify Mailgun signatures in production**
2. **Use service role key only in Edge Functions, never client-side**
3. **Enable RLS policies on all tables**
4. **Rotate signing keys periodically**
5. **Monitor for unusual event patterns (potential abuse)**

### Performance

1. **Use materialized views for frequently-accessed aggregations**
2. **Schedule pg_cron jobs during off-peak hours**
3. **Implement table partitioning for >1M events**
4. **Use connection pooling (Supavisor) for high-volume applications**
5. **Cache frequently-accessed queries in application layer**

### Data Quality

1. **Monitor for missing critical fields (message_id, recipient)**
2. **Validate event_type against expected values**
3. **Check for duplicate events (unique constraint violations)**
4. **Audit engagement score calculations periodically**
5. **Review suppression list regularly**

### Integration

1. **Use TypeScript types for compile-time safety**
2. **Implement retry logic in n8n workflows**
3. **Log all external API calls for debugging**
4. **Use Realtime for live updates, not polling**
5. **Sync engagement scores to Odoo daily, not real-time**

---

## FAQ

**Q: How do I handle duplicate webhook deliveries from Mailgun?**
A: The unique constraint on `(mailgun_id, event_type, event_timestamp)` prevents duplicates. Duplicate webhook deliveries will be silently ignored.

**Q: Can I reprocess events from raw_payload?**
A: Yes, all webhook data is preserved in `raw_payload` JSONB column. You can write a function to extract additional fields if needed.

**Q: How do I partition the events table for better performance?**
A: Implement monthly partitioning by `event_timestamp`. See PostgreSQL partitioning documentation.

**Q: Can I use this with multiple Mailgun domains?**
A: Yes, configure separate webhooks for each domain, or use a single Edge Function and differentiate by domain in the payload.

**Q: How do I export data for external BI tools?**
A: Use Supabase REST API, PostgREST, or direct PostgreSQL connection. All BI queries in `db/sql/bi_queries.sql` are ready to use.

**Q: What's the recommended retention policy?**
A: Keep raw events for 90 days, daily stats for 2 years, recipient engagement indefinitely. Implement automated archival with pg_cron.

---

## Support & Resources

- **Odoo Email Parity Pack**: `docs/runbooks/EMAIL_PARITY_PACK.md`
- **Supabase Documentation**: https://supabase.com/docs
- **Mailgun Documentation**: https://documentation.mailgun.com/
- **PostgreSQL Triggers**: https://www.postgresql.org/docs/current/plpgsql-trigger.html
- **Supabase Realtime**: https://supabase.com/docs/guides/realtime

---

**Version**: 1.0.0
**Last Updated**: 2026-01-28
**Status**: Production Ready
