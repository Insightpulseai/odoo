# IPAI SaaS Platform Kit - Implementation Plan

## Timeline Overview

**Total Duration:** 6 weeks (MVP)
**Start Date:** 2026-02-11
**Target Launch:** 2026-03-25

---

## Phase 1: Core SaaS Primitives (Weeks 1-2)

**Goal:** Stripe billing integration with usage tracking and entitlement enforcement

### Week 1: Foundation

**Day 1-2: Billing Infrastructure**
- [ ] Create Supabase migration: `20260212000000_billing_usage_tracking.sql`
  - billing_customers table
  - subscriptions table
  - usage_events table
  - org_usage_current materialized view
  - refresh_org_usage() function
- [ ] Create Supabase migration: `20260212000100_billing_rls.sql`
  - RLS policies on billing tables
  - Service role exception policies
  - Cross-org access tests

**Day 3-4: Stripe Integration**
- [ ] Create Edge Function: `stripe-webhook`
  - HMAC signature verification
  - Idempotency with event IDs
  - Event handlers (subscription.created, updated, deleted)
  - Invoice handlers (payment_succeeded, failed)
  - Audit logging
- [ ] Create Edge Function: `entitlement-check`
  - Query org_usage_current view
  - Compare against plan limits
  - Return decision with current/max values

**Day 5: Simple Pro Plan**
- [ ] Create Supabase migration: `20260212000500_billing_simple_plan.sql`
  - Seed "free" plan (default for new orgs)
  - Seed "pro" plan ($99/mo + $0.10/AI run)
  - Plan entitlements table
- [ ] Create TypeScript package: `packages/saas-types/src/billing.ts`
  - Stripe customer types
  - Subscription types
  - Usage event types
  - Entitlement check types

### Week 2: Odoo Billing Module

**Day 6-7: Module Scaffolding**
- [ ] Create Odoo module: `addons/ipai/ipai_saas_billing/`
  - __manifest__.py (OCA-compliant)
  - models/subscription.py (read-only from Supabase)
  - models/usage_event.py (log view)
  - security/ir.model.access.csv
- [ ] Create Odoo views: billing dashboard
  - Current plan display
  - Usage meters (AI runs, CMS items, users)
  - Invoice history table
  - Upgrade button (redirect to Stripe Checkout)

**Day 8-9: Stripe Checkout Integration**
- [ ] Create controller: `/billing/checkout`
  - Generate Stripe Checkout session
  - Pass org_id in metadata
  - Redirect to Stripe hosted page
- [ ] Create controller: `/billing/webhook-test`
  - Simulate webhook locally (dev environment only)
  - Test idempotency and error handling

**Day 10: Testing & Validation**
- [ ] Unit tests: Stripe webhook idempotency
- [ ] Unit tests: Entitlement check logic
- [ ] Integration test: Signup → Free plan → Upgrade → Pro plan
- [ ] Integration test: Usage tracking → Entitlement block
- [ ] Staging deployment: Validate billing flow end-to-end

---

## Phase 2: CMS Workflows + Odoo Integration (Weeks 3-5)

**Goal:** Approval workflows, version history, scheduled publishing, Odoo CMS admin

### Week 3: CMS Infrastructure

**Day 11-12: Workflow Tables**
- [ ] Create Supabase migration: `20260212000200_cms_workflows.sql`
  - content_types table
  - cms_page_versions table
  - cms_approvals table
  - cms_schedule table
- [ ] Create Supabase migration: `20260212000300_cms_rls.sql`
  - RLS on cms_approvals (org-scoped)
  - RLS on cms_page_versions (org-scoped)
  - RLS on cms_schedule (org-scoped)

**Day 13-14: Scheduled Publishing**
- [ ] Create Supabase migration: `20260212000400_activate_cron.sql`
  - pg_cron extension activation
  - Cron job: refresh-org-usage (every 5 minutes)
  - Cron job: execute-scheduled-publications (every 1 minute)
  - Cron job: stuck-run-recovery (every 2 minutes)
- [ ] Create Edge Function: `cms-publisher`
  - Query pending scheduled actions
  - Create version snapshot before publish
  - Update cms_pages.status
  - Send Realtime notification
  - Mark schedule row as executed

**Day 15: Version History**
- [ ] Create version snapshot trigger
  - Automatically create version on status change
  - Store full page content + metadata
  - Track created_by user
- [ ] Create version comparison function
  - Generate side-by-side diff HTML
  - Highlight added/removed/changed content

### Week 4: Odoo CMS Module

**Day 16-17: Module Scaffolding**
- [ ] Create Odoo module: `addons/ipai/ipai_platform_cms/`
  - __manifest__.py (depends on ipai_saas_billing)
  - models/cms_page.py (sync from Supabase)
  - models/cms_approval.py
  - models/cms_version.py
  - security/ir.model.access.csv

**Day 18-19: CMS Editor Views**
- [ ] Create Odoo views: content editor
  - Page form view (title, content HTML editor, metadata)
  - Status field (draft, pending, approved, published)
  - Request approval button
  - Schedule publish button (datetime picker)
- [ ] Create Odoo views: approval queue
  - Kanban view (pending, approved, rejected)
  - List view with filters (org, status, date)
  - Form view with side-by-side diff
  - Approve/reject action buttons with comments

**Day 20: Realtime Notifications**
- [ ] Supabase Realtime channel: cms_approvals
  - Subscribe to status changes
  - Toast notification in Odoo on approval/rejection
- [ ] Supabase Realtime channel: cms_schedule
  - Subscribe to publish executions
  - Toast notification on successful publish

### Week 5: Platform Admin Module

**Day 21-22: Module Scaffolding**
- [ ] Create Odoo module: `addons/ipai/ipai_platform_admin/`
  - __manifest__.py
  - models/organization.py (sync from Supabase)
  - models/team_member.py
  - security/ir.model.access.csv

**Day 23-24: Org Dashboard**
- [ ] Create Odoo views: org dashboard
  - Usage metrics (current vs. limits)
  - Team member list (with roles)
  - Invite user button (send email invite)
  - Org settings (name, billing email, timezone)
- [ ] Create controller: `/admin/invite-user`
  - Validate email format
  - Check user limit against plan
  - Send Supabase Auth invite email

**Day 25: Integration Testing**
- [ ] Integration test: CMS approval workflow end-to-end
- [ ] Integration test: Scheduled publishing (±1min accuracy)
- [ ] Integration test: Version history and diff generation
- [ ] Integration test: Team member invite and access control
- [ ] Staging deployment: Validate all CMS + admin flows

---

## Phase 2.5: Testing & Documentation (Week 6)

**Goal:** Comprehensive testing, documentation, staging validation, MVP launch readiness

### Week 6: Quality Assurance

**Day 26-27: Unit & Integration Tests**
- [ ] Unit tests: Stripe webhook handlers (all event types)
- [ ] Unit tests: Entitlement check (edge cases: exactly at limit, over limit)
- [ ] Unit tests: CMS publisher (scheduled actions, error handling)
- [ ] Integration tests: Billing cycle (signup → upgrade → invoice → usage)
- [ ] Integration tests: CMS workflow (draft → approval → published)
- [ ] Integration tests: Scheduled publish (create → schedule → execute → verify)
- [ ] RLS security tests: Cross-org access blocked on all tables

**Day 28: E2E Tests (Playwright)**
- [ ] E2E test: User signup → Free plan assigned → Billing dashboard loads
- [ ] E2E test: Upgrade to Pro → Stripe Checkout → Webhook → Subscription synced
- [ ] E2E test: Content creation → Request approval → Admin approves → Published
- [ ] E2E test: Schedule publish → Wait for execution → Verify status change
- [ ] E2E test: Usage limit reached → Entitlement blocks operation → Error message

**Day 29: Staging Deployment**
- [ ] Provision staging droplet: staging.insightpulseai.com
  - Install Docker + docker-compose
  - Configure Odoo 19 CE
  - Apply Supabase migrations
  - Deploy Edge Functions
  - Configure DNS (Cloudflare A record)
- [ ] Run smoke tests on staging:
  - Health check endpoints
  - Stripe webhook delivery
  - CMS approval workflow
  - Scheduled publishing
  - Billing dashboard loads

**Day 30: Documentation & Launch Prep**
- [ ] Finalize spec bundle:
  - constitution.md (complete)
  - prd.md (complete)
  - plan.md (complete)
  - tasks.md (complete)
- [ ] Create deployment runbook:
  - Staging → Production promotion checklist
  - Database backup procedure
  - Rollback procedure
  - Health monitoring setup
- [ ] Create user documentation:
  - Billing: How to upgrade, view invoices, manage payment methods
  - CMS: How to request approval, schedule publishing, view version history
  - Admin: How to invite users, manage org settings, monitor usage
- [ ] MVP launch readiness review:
  - All acceptance criteria met
  - Zero P0/P1 bugs
  - 80% test coverage achieved
  - Staging validation passed

---

## Dependencies

### External Dependencies

**Stripe Account:**
- **Status:** Required for Phase 1 Day 3
- **Action:** Create Stripe account, obtain API keys (test + production)
- **Timeline:** 1 week for approval, verification
- **Owner:** Tenant Admin

**DigitalOcean Staging Droplet:**
- **Status:** Required for Phase 2.5 Day 29
- **Action:** Provision staging.insightpulseai.com (2GB RAM, 50GB SSD)
- **Timeline:** 2 days for provisioning, configuration
- **Owner:** DevOps Engineer

**Cloudflare DNS:**
- **Status:** Already configured (existing erp.insightpulseai.com)
- **Action:** Add A record for staging.insightpulseai.com
- **Timeline:** <1 hour
- **Owner:** DevOps Engineer

### Internal Prerequisites

**Supabase Project:**
- **Status:** Active (spdtwktxdalcfigzeqrz)
- **Action:** Verify sufficient quota (Edge Functions, Storage, Database)
- **Timeline:** N/A (already provisioned)

**Odoo 19 CE Deployment:**
- **Status:** Live (erp.insightpulseai.com)
- **Action:** Verify Odoo 19 CE running, addons/ipai/ directory writable
- **Timeline:** N/A (already deployed)

**CI/CD Workflows:**
- **Status:** 162 workflows operational
- **Action:** Verify staging deployment workflow exists
- **Timeline:** N/A (already configured)

---

## Risks & Mitigation

### Technical Risks

**Risk 1: Stripe Webhook Delays**
- **Impact:** Subscription status out of sync, billing disputes
- **Probability:** Medium (Stripe SLA: 99.99% uptime)
- **Mitigation:**
  - Idempotency with event IDs (prevents double processing)
  - Retry queue for failed webhook processing
  - Manual sync button in Odoo (fallback)
  - Monitoring alerts on webhook failures (>5 failures/hour)

**Risk 2: RLS Performance Degradation**
- **Impact:** Slow queries, poor user experience
- **Probability:** Low (PostgreSQL RLS optimized for multi-tenancy)
- **Mitigation:**
  - Index optimization on org_id columns
  - Query profiling in staging (EXPLAIN ANALYZE)
  - Materialized view for usage aggregation (pre-computed)
  - Connection pooling (pgBouncer in production)

**Risk 3: pg_cron Failures**
- **Impact:** Scheduled publishing delayed, usage metrics stale
- **Probability:** Low (pg_cron 99.9% reliability)
- **Mitigation:**
  - Heartbeat monitoring (alert if cron job doesn't run in 10 minutes)
  - Manual publish button in Odoo (fallback)
  - Stuck run recovery cron (auto-retry failed jobs)
  - Runbook for manual cron restart

**Risk 4: Schema Drift (Supabase ↔ TypeScript)**
- **Impact:** Type mismatches, runtime errors
- **Probability:** Medium (frequent schema changes)
- **Mitigation:**
  - Supabase type generation in CI (automated)
  - Migration CI gate (validate types after migration)
  - Schema diff validation (detect drift before deploy)
  - Lock step deployment (Supabase → TypeScript → Odoo)

### Execution Risks

**Risk 5: Scope Creep**
- **Impact:** Timeline slippage, incomplete MVP
- **Probability:** High (common in feature-rich projects)
- **Mitigation:**
  - Constitution non-negotiables (strict scope boundaries)
  - Daily scope review (block new features)
  - Defer Platform Kit UI to Phase 3 (explicit exclusion)
  - Weekly stakeholder checkpoint (alignment on priorities)

**Risk 6: Testing Gaps**
- **Impact:** Bugs in production, rollback required
- **Probability:** Medium (complex integration points)
- **Mitigation:**
  - 80% coverage CI gate (blocks merge if below threshold)
  - E2E tests for critical paths (billing, approval, publishing)
  - Staging validation required (no direct-to-prod)
  - Smoke tests before production promotion

**Risk 7: Documentation Lag**
- **Impact:** Poor onboarding, support burden
- **Probability:** Medium (documentation often deprioritized)
- **Mitigation:**
  - Inline documentation with code (JSDoc, docstrings)
  - Spec bundle as SSOT (constitution, PRD, plan)
  - Automated documentation generation (TypeDoc, Sphinx)
  - Day 30 dedicated to documentation finalization

---

## Success Criteria (Revisited)

### MVP Launch Requirements (Week 6)

**Billing (Must Have):**
- ✅ First paying customer onboarded within 1 week of MVP launch
- ✅ Stripe webhook processing <500ms p99
- ✅ Entitlement check <100ms p95
- ✅ Zero double billing (idempotency verified)
- ✅ RLS blocks cross-org access (automated test passes)

**CMS (Must Have):**
- ✅ 90% of content goes through approval workflow
- ✅ CMS approval workflow <5s end-to-end
- ✅ Scheduled publish accuracy ±1min
- ✅ Version history shows all changes with diffs
- ✅ Realtime notifications <2s latency

**Quality (Must Have):**
- ✅ 80% test coverage (unit + integration)
- ✅ Zero P0/P1 bugs in staging
- ✅ All E2E tests passing
- ✅ Spec bundle complete and reviewed

**Performance (Must Have):**
- ✅ Stripe webhook processing <500ms p99
- ✅ Entitlement check <100ms p95
- ✅ CMS approval workflow <5s end-to-end
- ✅ Scheduled publish accuracy ±1min

---

## Future Phases (Post-MVP)

### Phase 3: Platform Kit UI Blocks (Weeks 7-10)

**Goal:** Standalone Next.js admin application with "Bank-Grade Calm" design system

**Components:**
- BillingDashboard (usage meters, plan selector, invoice history)
- CMSEditor (WYSIWYG editor, approval request, schedule picker)
- CMSApprovalQueue (Kanban view, side-by-side diff, approve/reject)
- OrgSettings (team management, invite users, org details)

**Supabase Features:**
- Storage activation (4 buckets: documents, attachments, exports, public)
- Queues table (job queue for async operations)
- Analytics Buckets (event tracking with JSONB properties)

**Design System:**
- "Bank-Grade Calm" tokens (neutral blues/grays, conservative spacing)
- Tailwind CSS configuration
- Shadcn/ui components (customized)

### Phase 4: Odoo.sh-Equivalent Delivery (Weeks 11-14)

**Goal:** Automated staging/production promotion with zero-downtime deployments

**GitHub Workflows:**
- `staging-deploy.yml` (auto-deploy on push to develop)
- `promote-to-prod.yml` (manual approval, database backup, health checks)
- `rollback.yml` (revert to previous version, restore database)

**Scripts:**
- `health_check.sh` (HTTP health endpoint, database connectivity, service status)
- `smoke_test.sh` (critical path testing, synthetic transactions)
- `rollback.sh` (revert code, restore database, verify health)

**Monitoring:**
- Health monitoring Edge Function (periodic health checks, Slack alerts)
- Database backup automation (daily backups, 30-day retention)
- Zero-downtime promotion (blue-green deployment, gradual traffic shift)

---

*Last updated: 2026-02-11*
