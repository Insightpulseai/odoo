# IPAI SaaS Platform Kit - Product Requirements Document

## Problem Statement

InsightPulse AI currently has:
- ✅ Multi-tenant authentication (Supabase Auth)
- ✅ Organization structure (orgs, teams, users)
- ✅ CMS foundation (pages, sections, use cases, artifacts)
- ✅ Agent infrastructure (10 canonical agents, 3 production flows)
- ✅ 133 SQL migrations deployed
- ✅ 40 Edge Functions live

**Missing critical SaaS primitives:**
- ❌ Billing integration (no subscription management, no usage metering)
- ❌ Content workflows (no approval process, no version history)
- ❌ Scheduled publishing (no automation)
- ❌ Entitlement enforcement (no usage limits)
- ❌ Admin interface for billing/CMS (manual SQL operations)

**Result:** Cannot onboard paying customers, track usage, or manage content through structured workflows.

---

## Goals

### Business Goals
1. **Monetize platform** — Enable Stripe subscriptions with usage-based pricing
2. **Reduce manual operations** — Automate billing sync, content approval, publishing
3. **Ensure compliance** — Audit trail, invoice history, usage transparency
4. **Scale efficiently** — Multi-tenant RLS, automated resource enforcement

### Technical Goals
1. **Stripe integration** — Webhook handler, subscription sync, usage metering
2. **CMS workflows** — Approval process, version history, scheduled publishing
3. **Odoo admin interface** — Billing dashboard, content editor, org settings
4. **RLS enforcement** — Multi-tenant security on all new tables
5. **Staging environment** — Validate workflows before production

### Success Metrics
- **Billing:** First paying customer onboarded within 1 week of MVP launch
- **CMS:** 90% of content goes through approval workflow (down from 0%)
- **Performance:** Stripe webhook processing <500ms p99
- **Quality:** Zero cross-org data leaks (automated RLS tests)

---

## Personas

### 1. Tenant Admin
**Role:** Organization owner responsible for billing and team management

**Goals:**
- View current subscription plan and usage
- Upgrade/downgrade plans
- Manage team members (invite, remove, roles)
- Access invoice history
- Monitor usage against limits

**Pain Points:**
- No visibility into usage consumption
- Cannot self-serve plan changes (requires manual SQL)
- No invoice history or payment method management

**Jobs to Be Done:**
- "When usage approaches limits, I need alerts so I can upgrade before operations are blocked"
- "When viewing invoices, I need itemized usage breakdown so I can audit billing"
- "When adding team members, I need role-based permissions so I can control access"

### 2. Content Editor
**Role:** Team member creating and managing CMS content

**Goals:**
- Create pages/posts/case studies
- Request approval from admin
- Schedule content for future publishing
- View version history and diffs
- Receive notifications when content is approved/rejected

**Pain Points:**
- No approval workflow (everyone publishes directly)
- No version history (cannot rollback changes)
- No scheduled publishing (manual cron jobs)
- No notifications on content status changes

**Jobs to Be Done:**
- "When I finish drafting content, I need to request approval so admins can review before publishing"
- "When reviewing edits, I need side-by-side diff so I can see what changed"
- "When scheduling content, I need reliability so launches happen on time"

### 3. Developer
**Role:** Engineer integrating with platform APIs

**Goals:**
- Check entitlements before operations
- Track usage events programmatically
- Understand RLS policies
- Test webhook flows locally
- Access TypeScript types for API contracts

**Pain Points:**
- No entitlement check function (manual queries)
- No usage event SDK (raw SQL inserts)
- Webhook testing requires production Stripe events
- TypeScript types out of sync with database schema

**Jobs to Be Done:**
- "When executing AI runs, I need to check entitlements so users are blocked at limits"
- "When logging usage, I need idempotent tracking so double-counting is prevented"
- "When testing webhooks, I need local simulation so I don't rely on Stripe production events"

---

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                          │
├─────────────────────────────────────────────────────────────────┤
│  Next.js Public Site  │  Odoo Admin Interface                   │
│  (erp.insightpulseai) │  (billing, CMS editor, org settings)    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Supabase Backend                            │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL 15 + RLS                                            │
│  ├─ Organizations, Teams, Users (existing)                      │
│  ├─ CMS Pages, Sections, Artifacts (existing)                  │
│  ├─ Billing Tables (NEW)                                       │
│  │  ├─ billing_customers (Stripe customer_id mapping)          │
│  │  ├─ subscriptions (plan, status, current_period)            │
│  │  ├─ usage_events (ai_runs, cms_items, users)               │
│  │  └─ org_usage_current (materialized view)                   │
│  ├─ CMS Workflow Tables (NEW)                                  │
│  │  ├─ content_types (page, post, case_study)                 │
│  │  ├─ cms_page_versions (version history)                     │
│  │  ├─ cms_approvals (pending/approved/rejected)              │
│  │  └─ cms_schedule (scheduled publish/unpublish)             │
│  └─ RLS Policies (ALL tables org-scoped)                       │
├─────────────────────────────────────────────────────────────────┤
│  Edge Functions                                                  │
│  ├─ stripe-webhook (Stripe event processing)                   │
│  ├─ entitlement-check (usage limit enforcement)                │
│  └─ cms-publisher (scheduled publishing via pg_cron)           │
├─────────────────────────────────────────────────────────────────┤
│  pg_cron Jobs                                                   │
│  ├─ refresh-org-usage (every 5 minutes)                        │
│  ├─ execute-scheduled-publications (every 1 minute)            │
│  └─ stuck-run-recovery (every 2 minutes)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                           │
├─────────────────────────────────────────────────────────────────┤
│  Stripe API (subscriptions, invoices, webhooks)                │
└─────────────────────────────────────────────────────────────────┘
```

### Data Model

#### Billing Tables

**billing_customers**
```sql
CREATE TABLE billing_customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  stripe_customer_id TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_billing_customers_org_id ON billing_customers(org_id);
```

**subscriptions**
```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  stripe_subscription_id TEXT NOT NULL UNIQUE,
  stripe_customer_id TEXT NOT NULL REFERENCES billing_customers(stripe_customer_id),
  plan_name TEXT NOT NULL, -- 'free', 'pro'
  status TEXT NOT NULL, -- 'active', 'canceled', 'past_due', 'trialing'
  current_period_start TIMESTAMPTZ NOT NULL,
  current_period_end TIMESTAMPTZ NOT NULL,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_subscriptions_org_id ON subscriptions(org_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

**usage_events**
```sql
CREATE TABLE usage_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  event_type TEXT NOT NULL, -- 'ai_run', 'cms_item', 'user_added'
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_usage_events_org_id ON usage_events(org_id);
CREATE INDEX idx_usage_events_created_at ON usage_events(created_at DESC);
CREATE INDEX idx_usage_events_type ON usage_events(event_type);
```

**org_usage_current** (Materialized View)
```sql
CREATE MATERIALIZED VIEW org_usage_current AS
SELECT
  org_id,
  COUNT(*) FILTER (WHERE event_type = 'ai_run') AS ai_runs_count,
  COUNT(*) FILTER (WHERE event_type = 'cms_item') AS cms_items_count,
  COUNT(*) FILTER (WHERE event_type = 'user_added') AS users_count,
  MAX(created_at) AS last_event_at
FROM usage_events
WHERE created_at >= DATE_TRUNC('month', NOW())
GROUP BY org_id;

CREATE UNIQUE INDEX idx_org_usage_current_org_id ON org_usage_current(org_id);
```

#### CMS Workflow Tables

**content_types**
```sql
CREATE TABLE content_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE, -- 'page', 'post', 'case_study'
  schema JSONB NOT NULL, -- JSON schema for validation
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**cms_page_versions**
```sql
CREATE TABLE cms_page_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id UUID NOT NULL REFERENCES cms_pages(id),
  org_id UUID NOT NULL,
  version_number INT NOT NULL,
  title TEXT NOT NULL,
  content_html TEXT,
  metadata JSONB,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_cms_page_versions_page_id ON cms_page_versions(page_id);
CREATE UNIQUE INDEX idx_cms_page_versions_unique ON cms_page_versions(page_id, version_number);
```

**cms_approvals**
```sql
CREATE TABLE cms_approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id UUID NOT NULL REFERENCES cms_pages(id),
  org_id UUID NOT NULL,
  version_id UUID NOT NULL REFERENCES cms_page_versions(id),
  status TEXT NOT NULL, -- 'pending', 'approved', 'rejected'
  requested_by UUID NOT NULL REFERENCES auth.users(id),
  reviewed_by UUID REFERENCES auth.users(id),
  comments TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_cms_approvals_org_id ON cms_approvals(org_id);
CREATE INDEX idx_cms_approvals_status ON cms_approvals(status);
```

**cms_schedule**
```sql
CREATE TABLE cms_schedule (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id UUID NOT NULL REFERENCES cms_pages(id),
  org_id UUID NOT NULL,
  action TEXT NOT NULL, -- 'publish', 'unpublish'
  scheduled_at TIMESTAMPTZ NOT NULL,
  executed_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'executed', 'failed'
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_cms_schedule_scheduled_at ON cms_schedule(scheduled_at) WHERE status = 'pending';
CREATE INDEX idx_cms_schedule_org_id ON cms_schedule(org_id);
```

### RLS Policies

**Principle:** Users can ONLY access data from their own organization.

**Example: subscriptions table**
```sql
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own org subscription"
  ON subscriptions FOR SELECT
  USING (
    org_id IN (
      SELECT org_id FROM user_organizations WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Service role can manage all subscriptions"
  ON subscriptions FOR ALL
  USING (auth.jwt()->>'role' = 'service_role');
```

---

## API Contract

### Edge Functions

#### 1. stripe-webhook

**Endpoint:** `POST /functions/v1/stripe-webhook`

**Request:**
```json
{
  "type": "customer.subscription.updated",
  "id": "evt_1234567890",
  "data": {
    "object": {
      "id": "sub_1234567890",
      "customer": "cus_1234567890",
      "status": "active",
      "current_period_start": 1707667200,
      "current_period_end": 1710259200,
      "plan": {
        "id": "price_pro_monthly",
        "nickname": "Pro"
      }
    }
  }
}
```

**Response (200 OK):**
```json
{
  "received": true,
  "event_id": "evt_1234567890"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "Invalid signature"
}
```

**Processing Logic:**
1. Verify HMAC signature using Stripe webhook secret
2. Check idempotency (event ID already processed?)
3. Extract subscription data
4. Upsert to `subscriptions` table
5. Log event to audit trail
6. Return 200 OK (Stripe requires <5s response)

#### 2. entitlement-check

**Endpoint:** `POST /functions/v1/entitlement-check`

**Request:**
```json
{
  "org_id": "uuid-here",
  "limit_type": "ai_runs"
}
```

**Response (allowed):**
```json
{
  "allowed": true,
  "current": 250,
  "max": 1000,
  "plan": "pro"
}
```

**Response (blocked):**
```json
{
  "allowed": false,
  "current": 1000,
  "max": 1000,
  "plan": "pro",
  "message": "Monthly AI run limit reached. Upgrade to continue."
}
```

**Processing Logic:**
1. Query `org_usage_current` materialized view
2. Get org's current plan from `subscriptions`
3. Compare usage against plan limits
4. Return decision with current/max values

#### 3. cms-publisher

**Trigger:** pg_cron (every 1 minute)

**Processing Logic:**
1. Query `cms_schedule` for pending actions where `scheduled_at <= NOW()`
2. For each action:
   - Create version snapshot (if publish)
   - Update `cms_pages.status`
   - Mark schedule row as executed
   - Send Realtime notification
3. Handle failures (retry logic, error logging)

### RPC Functions

**refresh_org_usage()**
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY org_usage_current;
```

**check_entitlement(p_org_id UUID, p_limit_type TEXT)**
```sql
RETURNS JSONB AS $$
  -- Returns { allowed: boolean, current: number, max: number, plan: string }
$$;
```

---

## Acceptance Criteria

### MVP Launch Requirements (Week 6)

**Billing:**
- [ ] User can sign up and be assigned free plan
- [ ] User can upgrade to Pro plan via Stripe Checkout
- [ ] Stripe webhook syncs subscription status to Supabase
- [ ] Odoo displays current plan, usage meters, invoice history
- [ ] Usage events logged for AI runs, CMS items, users
- [ ] Entitlement check blocks operations at limits
- [ ] Pro plan users see itemized usage on invoices

**CMS Workflows:**
- [ ] Content Editor creates page (status: draft)
- [ ] Content Editor requests approval
- [ ] Tenant Admin sees approval in Odoo queue
- [ ] Tenant Admin reviews side-by-side diff
- [ ] Tenant Admin approves/rejects with comments
- [ ] Page status updates to published on approval
- [ ] Realtime notification sent to editor
- [ ] Content Editor schedules page for future publish
- [ ] pg_cron executes publish at scheduled time (±1min)
- [ ] Version history shows all changes with diffs

**Security:**
- [ ] RLS blocks cross-org access (automated test)
- [ ] Webhook signature verification prevents replay attacks
- [ ] Service role operations logged with justification
- [ ] Secrets stored in Supabase Vault (not hardcoded)

**Performance:**
- [ ] Stripe webhook processing <500ms p99
- [ ] Entitlement check <100ms p95
- [ ] CMS approval workflow <5s end-to-end
- [ ] Scheduled publish accuracy ±1min

**Quality:**
- [ ] 80% test coverage (unit + integration)
- [ ] Zero P0/P1 bugs in staging
- [ ] All E2E tests passing
- [ ] Spec bundle complete and reviewed

---

## Implementation Phases

### Phase 1: Core SaaS Primitives (Weeks 1-2)
- Stripe webhook handler Edge Function
- Billing tables + RLS policies
- Usage tracking tables + materialized view
- Entitlement check RPC function
- Simple "Pro" plan configuration
- Odoo `ipai_saas_billing` module (basic UI)

### Phase 2: CMS Workflows + Odoo Integration (Weeks 3-5)
- CMS workflow tables + RLS policies
- CMS publisher Edge Function
- pg_cron jobs (usage refresh, scheduled publishing)
- Odoo `ipai_platform_cms` module (approval queue, editor)
- Odoo `ipai_platform_admin` module (org settings, team management)
- Version history and diff views
- Realtime notification channels

### Phase 2.5: Testing & Documentation (Week 6)
- Unit tests (webhook idempotency, entitlement logic)
- Integration tests (billing cycle, approval workflow)
- E2E tests (signup → subscription → content → publish)
- Staging deployment validation
- Smoke tests (health checks, critical paths)
- Spec bundle finalization

---

*Last updated: 2026-02-11*
