# IPAI SaaS Platform Kit - Constitution

## Core Principles

### 1. Supabase-First Architecture
- **ALL** backend operations use Supabase (PostgreSQL + RLS + Edge Functions + Realtime + Storage + Vault)
- PostgreSQL serves as single source of truth for application state
- Edge Functions handle business logic, webhooks, and async operations
- Realtime channels for live updates (approval notifications, usage meters)
- Storage buckets for file operations with RLS policies
- Vault for secrets management (API keys, service credentials)

### 2. No External SaaS Dependencies (Except Stripe)
- **NO** external CMS platforms (Contentful, Strapi, etc.)
- **NO** external authentication SaaS (Auth0, Clerk, etc.) — Supabase Auth only
- **NO** external queue services (BullMQ, Celery) — Supabase pg_cron + queue tables
- **EXCEPTION**: Stripe for billing/payments (industry standard, required for compliance)

### 3. Multi-Tenant RLS Security Model
- **EVERY** table has `org_id` column
- **ALL** queries filtered by authenticated user's organization
- **ZERO** trust between organizations
- Service role keys for admin operations ONLY (monitored, logged)
- User-scoped API keys inherit org_id automatically

### 4. Technology Stack Locked
- **Backend**: Supabase (PostgreSQL 15+ with pgvector, pg_cron, extensions)
- **Frontend**: Next.js 14+ (App Router, Server Components, Tailwind CSS)
- **Admin**: Odoo CE 19.0 (custom IPAI modules for billing/CMS management)
- **Billing**: Stripe (webhooks, subscriptions, usage-based pricing)
- **Deployment**: DigitalOcean (Odoo), Vercel (Next.js), Supabase (managed)
- **CI/CD**: GitHub Actions (162 workflows, 4-stage pipeline)

---

## Scope Boundaries

### In Scope (MVP - 6 Weeks)

**Billing & Subscriptions:**
- ✅ Stripe webhook handler (idempotent event processing)
- ✅ Single "Pro" plan ($99/mo + $0.10/AI run overage)
- ✅ Usage tracking (AI runs, CMS items, users)
- ✅ Entitlement enforcement (check limits before operations)
- ✅ Invoice history display in Odoo
- ✅ Subscription management UI in Odoo

**CMS Workflows:**
- ✅ Content types registry (page, post, case_study)
- ✅ Version history (track all changes)
- ✅ Approval workflow (draft → pending → approved → published)
- ✅ Scheduled publishing (pg_cron + Edge Function)
- ✅ Side-by-side diff view in Odoo
- ✅ Realtime notifications on approval/publish

**Odoo Integration:**
- ✅ `ipai_saas_billing` module (billing dashboard, usage meters)
- ✅ `ipai_platform_cms` module (content editor, approval queue)
- ✅ `ipai_platform_admin` module (org settings, team management)

**Infrastructure:**
- ✅ Staging environment (staging.insightpulseai.com)
- ✅ RLS policies for all new tables
- ✅ Supabase migrations (6 new migrations)
- ✅ Edge Functions (3 new functions)

### Out of Scope (Future Releases)

**Phase 3 (Weeks 7-10):**
- ⏭️ Standalone Next.js admin application
- ⏭️ Platform Kit UI component library
- ⏭️ "Bank-Grade Calm" design system tokens
- ⏭️ Supabase Storage activation (buckets, upload UI)
- ⏭️ Supabase Queues & Analytics Buckets

**Phase 4 (Weeks 11-14):**
- ⏭️ Odoo.sh-equivalent delivery automation
- ⏭️ GitHub workflows for staging/production promotion
- ⏭️ Health monitoring Edge Function with Slack alerts
- ⏭️ Automated database backup before prod deploy
- ⏭️ Zero-downtime production promotion scripts

**Explicitly Excluded:**
- ❌ White-label multi-tenant (single brand only)
- ❌ SSO/SAML integration (Supabase Auth + email/password only)
- ❌ Multi-region deployment (Singapore only)
- ❌ Custom domain per tenant (insightpulseai.com only)
- ❌ Marketplace/plugin system
- ❌ Mobile native apps (web-responsive only)

---

## Security Policy

### 1. Row-Level Security (RLS)
- **MANDATORY** on ALL application tables
- Policies enforce `auth.uid()` and `org_id` filtering
- Service role operations logged with justification
- Automated RLS testing in CI (cross-org access blocked)

### 2. Secrets Management
- **NEVER** hardcode secrets in source code
- Supabase Vault for sensitive credentials
- GitHub Actions secrets for CI/CD
- `.env*` files for local development (gitignored)
- Rotate secrets every 90 days (automated reminder)

### 3. Webhook Security
- HMAC signature verification (Stripe webhook signing secret)
- Replay attack prevention (timestamp validation)
- Idempotency keys (Stripe event IDs)
- Rate limiting on webhook endpoints (100 req/min)

### 4. Data Protection
- PostgreSQL RLS prevents cross-org data leaks
- Audit trail for sensitive operations (plan changes, user additions)
- Soft deletes with archival (30-day retention)
- GDPR compliance (data export, account deletion)

---

## Quality Gates

### Code Quality
- **80% test coverage** (unit + integration)
- Linting passes (ESLint, Flake8)
- Type checking passes (TypeScript strict mode, mypy)
- Pre-commit hooks enforce formatting (Prettier, Black)

### Security
- **Zero P0/P1 vulnerabilities** in production
- RLS policies validated (automated cross-org tests)
- Dependency audit passes (npm audit, safety)
- Secrets scanning (no exposed keys in commits)

### Performance
- Stripe webhook processing <500ms p99
- Entitlement check <100ms p95
- CMS approval workflow <5s end-to-end
- Scheduled publish accuracy ±1min

### Deployment
- Staging validation required before production
- Smoke tests pass on staging (health checks, critical paths)
- Database migrations reversible (rollback tested)
- Zero-downtime deployment (verified with health checks)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-11 | MVP timeline reduced to 6 weeks | Focus on billing + CMS core, defer UI/automation to future releases |
| 2026-02-11 | Single "Pro" plan for MVP | Simplify billing logic, validate usage-based pricing before tiered plans |
| 2026-02-11 | Odoo as admin interface | Leverage existing Odoo deployment, defer standalone Next.js admin |
| 2026-02-11 | Staging droplet required | Validate workflows before production, zero-downtime promotion strategy |
| 2026-02-11 | pg_cron for scheduled publishing | Native PostgreSQL extension, no external scheduler dependencies |
| 2026-02-11 | Stripe webhooks via Edge Functions | Idempotent event processing, handles retries, validates HMAC |

---

## Non-Negotiables

1. **Supabase PostgreSQL is single source of truth** — NO external databases
2. **RLS on ALL application tables** — NO bypassing multi-tenancy security
3. **Stripe for billing ONLY** — NO other payment processors
4. **Odoo CE 19.0** — NO Enterprise edition (EE parity via OCA + IPAI modules)
5. **80% test coverage** — NO merging untested code
6. **Staging validation before production** — NO direct-to-prod deployments

---

*Last updated: 2026-02-11*
