# IPAI SaaS Platform Kit

**Status:** 🚧 Phase 2 - Implementation Started
**Target Launch:** 2026-03-25 (6 weeks from 2026-02-11)

---

## Quick Start

### For Implementers

```bash
# 1. Read the spec bundle
cd spec/ipai-saas-platform-kit/
cat constitution.md  # Non-negotiables and scope boundaries
cat prd.md           # Complete product requirements
cat plan.md          # Phase-by-phase implementation plan
cat tasks.md         # 48 tasks with estimates

# 2. Setup development environment
cd supabase/
supabase db reset  # Apply migrations locally
supabase functions serve  # Start Edge Functions locally

# 3. Install Odoo modules (after migrations complete)
./scripts/odoo_install.sh ipai_saas_billing
./scripts/odoo_install.sh ipai_platform_cms
./scripts/odoo_install.sh ipai_platform_admin

# 4. Run tests
cd supabase/functions/stripe-webhook && deno test
cd addons/ipai/ipai_saas_billing && python -m pytest
cd web/web && pnpm test:e2e
```

### For Stakeholders

**What:** Production-ready SaaS primitives (billing + CMS workflows) for InsightPulse AI

**Why:** Enable paying customers, track usage, manage content through approval workflows

**When:** 6-week MVP (billing + CMS core), Phase 3/4 deferred to future releases

**Success Metrics:**
- First paying customer onboarded within 1 week of launch
- 90% of content goes through approval workflow
- Stripe webhook processing <500ms p99
- Zero cross-org data leaks (automated RLS tests)

---

## Spec Bundle Structure

| File | Purpose | Audience |
|------|---------|----------|
| **constitution.md** | Non-negotiables, scope boundaries, decision log | All stakeholders |
| **prd.md** | Problem statement, goals, personas, architecture, API contract | Product, Engineering |
| **plan.md** | Phase-by-phase implementation timeline with risk mitigation | Engineering, Project Management |
| **tasks.md** | 48 tasks with deliverables, acceptance criteria, estimates | Engineering |
| **README.md** | This file - quick start and navigation guide | All audiences |

---

## Architecture Overview

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
│  PostgreSQL 15 + RLS (multi-tenant security)                    │
│  Edge Functions (stripe-webhook, entitlement-check, cms-publisher) │
│  pg_cron (usage refresh, scheduled publishing)                  │
│  Realtime (approval notifications, publish events)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                           │
├─────────────────────────────────────────────────────────────────┤
│  Stripe API (subscriptions, invoices, webhooks)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### ✅ Phase 1: Core SaaS Primitives (Weeks 1-2)
**Goal:** Stripe billing integration with usage tracking and entitlement enforcement

**Key Deliverables:**
- 6 Supabase migrations (billing tables, RLS policies, simple Pro plan)
- 2 Edge Functions (stripe-webhook, entitlement-check)
- 1 Odoo module (ipai_saas_billing)
- TypeScript types package (saas-types)

**Success Criteria:**
- Stripe webhook processing <500ms p99
- Entitlement check <100ms p95
- Zero double billing (idempotency verified)
- RLS blocks cross-org access

### 🔄 Phase 2: CMS Workflows + Odoo Integration (Weeks 3-5)
**Goal:** Approval workflows, version history, scheduled publishing, Odoo CMS admin

**Key Deliverables:**
- 4 Supabase migrations (CMS workflow tables, RLS policies, pg_cron, version triggers)
- 1 Edge Function (cms-publisher)
- 2 Odoo modules (ipai_platform_cms, ipai_platform_admin)
- Realtime notification channels

**Success Criteria:**
- CMS approval workflow <5s end-to-end
- Scheduled publish accuracy ±1min
- Version history with side-by-side diffs
- Realtime notifications <2s latency

### 🔄 Phase 2.5: Testing & Documentation (Week 6)
**Goal:** Comprehensive testing, staging validation, MVP launch readiness

**Key Deliverables:**
- Unit tests (Stripe idempotency, entitlement logic, CMS workflows)
- Integration tests (billing cycle, approval workflow, scheduled publishing)
- E2E tests (signup → subscription → content → publish)
- Staging environment (staging.insightpulseai.com)
- Spec bundle finalization

**Success Criteria:**
- 80% test coverage (unit + integration)
- Zero P0/P1 bugs in staging
- All E2E tests passing
- Staging deployment validated

### ⏭️ Phase 3: Platform Kit UI Blocks (Weeks 7-10)
**Deferred to Future Release**

**Goal:** Standalone Next.js admin application with "Bank-Grade Calm" design system

**Deliverables:**
- Next.js admin app package
- Design system tokens (Tailwind config)
- Admin components (BillingDashboard, CMSEditor, OrgSettings)
- Supabase Storage activation (buckets, upload UI)

### ⏭️ Phase 4: Odoo.sh-Equivalent Delivery (Weeks 11-14)
**Deferred to Future Release**

**Goal:** Automated staging/production promotion with zero-downtime deployments

**Deliverables:**
- GitHub workflows (staging-deploy, promote-to-prod, rollback)
- Health monitoring Edge Function
- Database backup automation
- Zero-downtime promotion scripts

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | Supabase (PostgreSQL 15+ with pgvector, pg_cron) | Single source of truth, multi-tenant RLS, no external SaaS |
| **Frontend** | Next.js 14+ (App Router, Server Components) | Modern React, server-side rendering, SEO |
| **Admin** | Odoo CE 19.0 (custom IPAI modules) | Existing deployment, EE parity via OCA + custom |
| **Billing** | Stripe (webhooks, subscriptions) | Industry standard, compliance, reliability |
| **Deployment** | DigitalOcean (Odoo), Vercel (Next.js), Supabase (managed) | Cost-optimized, proven infrastructure |
| **CI/CD** | GitHub Actions (162 workflows, 4-stage pipeline) | Existing mature pipeline |

---

## Quick Reference

### Supabase Migrations (6 new)

1. **`20260212000000_billing_usage_tracking.sql`** - Billing tables, usage events, materialized view
2. **`20260212000100_billing_rls.sql`** - RLS policies on billing tables
3. **`20260212000200_cms_workflows.sql`** - CMS workflow tables (versions, approvals, schedule)
4. **`20260212000300_cms_rls.sql`** - RLS policies on CMS workflow tables
5. **`20260212000400_activate_cron.sql`** - pg_cron jobs (usage refresh, scheduled publishing)
6. **`20260212000500_billing_simple_plan.sql`** - Seed free/pro plans

### Edge Functions (3 new)

1. **`stripe-webhook`** - Stripe event processing (idempotent, HMAC verified)
2. **`entitlement-check`** - Usage limit enforcement (<100ms p95)
3. **`cms-publisher`** - Scheduled publishing execution (±1min accuracy)

### Odoo Modules (3 new)

1. **`ipai_saas_billing`** - Billing dashboard, usage meters, Stripe Checkout integration
2. **`ipai_platform_cms`** - Content editor, approval queue, version history
3. **`ipai_platform_admin`** - Org dashboard, team management, settings

### Key Files

| File | Purpose |
|------|---------|
| `pkgs/saas-types/src/billing.ts` | TypeScript types for billing domain |
| `infra/do/staging-droplet.tf` | Terraform config for staging environment |
| `supabase/tests/rls_security.test.sql` | Automated RLS cross-org tests |
| `web/web/tests/e2e/billing.spec.ts` | E2E billing flow tests |
| `web/web/tests/e2e/cms_workflow.spec.ts` | E2E CMS workflow tests |

---

## Testing Strategy

### Unit Tests (80% coverage required)
- Stripe webhook idempotency (all event types)
- Entitlement check logic (edge cases: at limit, over limit)
- CMS publisher (scheduled actions, error handling)

### Integration Tests
- Billing cycle (signup → upgrade → invoice → usage)
- CMS workflow (draft → approval → published)
- Scheduled publishing (create → execute → verify)
- Team management (invite → accept → access control)

### E2E Tests (Playwright)
- User signup → Free plan → Billing dashboard
- Upgrade to Pro → Stripe Checkout → Webhook → Subscription synced
- Content creation → Request approval → Approve → Published
- Schedule publish → Wait → Verify execution

### Security Tests
- RLS cross-org access (all tables)
- Webhook signature verification (replay attack prevention)
- Service role audit logging

---

## Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Stripe webhook processing | <500ms p99 | Stripe requires <5s response |
| Entitlement check | <100ms p95 | Called on every AI run |
| CMS approval workflow | <5s end-to-end | User waits for approval |
| Scheduled publish accuracy | ±1min | Acceptable for content publishing |
| Test coverage | ≥80% | Quality gate for production |

---

## Security Model

### Row-Level Security (RLS)
- **ALL** application tables have `org_id` column
- **EVERY** query filtered by authenticated user's organization
- Service role operations logged with justification
- Automated cross-org access tests in CI

### Secrets Management
- Supabase Vault for sensitive credentials
- GitHub Actions secrets for CI/CD
- `.env*` files for local development (gitignored)
- Rotate secrets every 90 days

### Webhook Security
- HMAC signature verification (Stripe webhook signing secret)
- Replay attack prevention (timestamp validation)
- Idempotency keys (Stripe event IDs)
- Rate limiting (100 req/min)

---

## Deployment Strategy

### Staging Environment
- **URL:** staging.insightpulseai.com
- **Purpose:** Pre-production validation, smoke tests
- **Requirements:** All tests pass, zero P0/P1 bugs

### Production Promotion
- **Trigger:** Manual approval after staging validation
- **Steps:**
  1. Database backup (automated)
  2. Apply migrations (reversible)
  3. Deploy Edge Functions
  4. Update Odoo modules
  5. Smoke tests
  6. Health checks
  7. Rollback if failures

### Rollback Procedure
- Revert code (git rollback)
- Restore database (from backup)
- Verify health checks
- Post-mortem analysis

---

## Dependencies

### External (User Action Required)
- ✅ Stripe account (test + production keys) - **Week 1 Day 3**
- ✅ DigitalOcean staging droplet - **Week 6 Day 29**
- ✅ Cloudflare DNS (A record for staging) - **Week 6 Day 29**

### Internal (Already Provisioned)
- ✅ Supabase project (spdtwktxdalcfigzeqrz)
- ✅ Odoo 19 CE (erp.insightpulseai.com)
- ✅ GitHub Actions (162 workflows operational)

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Stripe webhook delays | Billing disputes | Medium | Idempotency, retry queue, monitoring |
| RLS performance | Slow queries | Low | Index optimization, materialized views |
| pg_cron failures | Delayed publishing | Low | Heartbeat monitoring, manual fallback |
| Schema drift | Type mismatches | Medium | Supabase type generation in CI |
| Scope creep | Timeline slippage | High | Constitution boundaries, weekly checkpoints |
| Testing gaps | Production bugs | Medium | 80% coverage CI gate, E2E tests |
| Documentation lag | Support burden | Medium | Inline docs, spec bundle as SSOT |

---

## Success Metrics

### Business Metrics
- First paying customer onboarded within **1 week** of MVP launch
- **90%** of content goes through approval workflow (down from 0%)
- **<5** support tickets per week related to billing/CMS

### Technical Metrics
- Stripe webhook processing **<500ms p99**
- Entitlement check **<100ms p95**
- CMS approval workflow **<5s end-to-end**
- Scheduled publish accuracy **±1min**

### Quality Metrics
- **80%** test coverage (unit + integration)
- **Zero P0/P1 bugs** in production
- **Zero cross-org data leaks** (automated RLS tests)

---

## Resources

### Documentation
- [Supabase Docs](https://supabase.com/docs)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Odoo CE 19.0 Developer Guide](https://www.odoo.com/documentation/19.0/developer.html)
- [Next.js 14 App Router](https://nextjs.org/docs/app)

### Internal References
- Main CLAUDE.md: `/Users/tbwa/Documents/GitHub/Insightpulseai/odoo/CLAUDE.md`
- OCA Workflow: `docs/ai/OCA_WORKFLOW.md`
- Architecture Diagram: `docs/ai/ARCHITECTURE.md`
- CI/CD Workflows: `docs/ai/CI_WORKFLOWS.md`

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-02-11 | Spec bundle created (constitution, PRD, plan, tasks) | Claude Code |
| 2026-02-11 | MVP scope finalized (6 weeks, billing + CMS core) | Claude Code |
| 2026-02-11 | Deferred Platform Kit UI (Phase 3) and Odoo.sh-equivalent (Phase 4) | Claude Code |

---

*Last updated: 2026-02-11*
