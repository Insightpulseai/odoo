# IPAI SaaS Platform Kit - Task Breakdown

**Total Tasks:** 48
**Duration:** 6 weeks (30 working days)
**Velocity:** ~8 tasks/week

---

## Phase 1: Core SaaS Primitives (16 tasks)

### Week 1: Foundation (Days 1-5)

#### Billing Infrastructure (Days 1-2)

**Task 1.1: Create billing_usage_tracking migration**
- **File:** `supabase/migrations/20260212000000_billing_usage_tracking.sql`
- **Deliverables:**
  - billing_customers table (org_id, stripe_customer_id, email)
  - subscriptions table (org_id, stripe_subscription_id, plan_name, status, periods)
  - usage_events table (org_id, event_type, metadata, created_at)
  - org_usage_current materialized view
  - refresh_org_usage() function
  - Indexes on org_id, created_at, event_type
- **Acceptance:** Migration runs without errors, tables created with correct schema
- **Estimate:** 4 hours

**Task 1.2: Create billing RLS policies migration**
- **File:** `supabase/migrations/20260212000100_billing_rls.sql`
- **Deliverables:**
  - RLS on billing_customers (users see own org only)
  - RLS on subscriptions (users see own org only)
  - RLS on usage_events (users see own org only)
  - Service role exception policies
  - Automated RLS test (cross-org access blocked)
- **Acceptance:** RLS tests pass, cross-org queries return empty
- **Estimate:** 3 hours

#### Stripe Integration (Days 3-4)

**Task 1.3: Create stripe-webhook Edge Function**
- **File:** `supabase/functions/stripe-webhook/index.ts`
- **Deliverables:**
  - HMAC signature verification (Stripe webhook secret)
  - Idempotency check (event ID already processed?)
  - Event handlers:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
  - Upsert to subscriptions table
  - Audit logging
  - Error handling (return 200 OK even on errors for Stripe retry)
- **Acceptance:** Webhook processes events in <500ms p99, idempotent
- **Estimate:** 6 hours

**Task 1.4: Create entitlement-check Edge Function**
- **File:** `supabase/functions/entitlement-check/index.ts`
- **Deliverables:**
  - Query org_usage_current materialized view
  - Get org's plan from subscriptions table
  - Compare current usage vs. plan limits
  - Return JSON: { allowed: boolean, current: number, max: number, plan: string }
  - Edge cases: exactly at limit, over limit, no subscription
- **Acceptance:** Entitlement check <100ms p95, correct decisions
- **Estimate:** 4 hours

**Task 1.5: Write unit tests for stripe-webhook**
- **File:** `supabase/functions/stripe-webhook/index.test.ts`
- **Deliverables:**
  - Test: Valid signature → process event
  - Test: Invalid signature → reject (400 Bad Request)
  - Test: Duplicate event ID → skip (idempotency)
  - Test: subscription.created → insert new row
  - Test: subscription.updated → update existing row
  - Test: subscription.deleted → mark canceled
- **Acceptance:** All tests pass, 80% coverage
- **Estimate:** 3 hours

**Task 1.6: Write unit tests for entitlement-check**
- **File:** `supabase/functions/entitlement-check/index.test.ts`
- **Deliverables:**
  - Test: Usage below limit → allowed = true
  - Test: Usage at limit → allowed = false
  - Test: Usage over limit → allowed = false
  - Test: No subscription → allowed = false (free plan limits)
  - Test: Invalid org_id → error
- **Acceptance:** All tests pass, 80% coverage
- **Estimate:** 2 hours

#### Simple Pro Plan (Day 5)

**Task 1.7: Create billing_simple_plan migration**
- **File:** `supabase/migrations/20260212000500_billing_simple_plan.sql`
- **Deliverables:**
  - plans table (id, name, price, limits JSONB)
  - Seed "free" plan (1000 AI runs/mo, 10 CMS items, 3 users)
  - Seed "pro" plan ($99/mo base + $0.10/AI run, 10,000 AI runs/mo, 50 CMS items, 10 users)
  - Default free plan assignment trigger (on org creation)
- **Acceptance:** Migration runs, plans seeded, new orgs get free plan
- **Estimate:** 2 hours

**Task 1.8: Create saas-types TypeScript package**
- **File:** `packages/saas-types/src/billing.ts`
- **Deliverables:**
  - StripeCustomer interface
  - Subscription interface (matches subscriptions table)
  - UsageEvent interface (matches usage_events table)
  - EntitlementCheckRequest/Response interfaces
  - Plan interface (matches plans table)
  - Export all types
- **Acceptance:** Types compile, no errors
- **Estimate:** 2 hours

### Week 2: Odoo Billing Module (Days 6-10)

#### Module Scaffolding (Days 6-7)

**Task 1.9: Create ipai_saas_billing Odoo module**
- **Files:**
  - `addons/ipai/ipai_saas_billing/__manifest__.py`
  - `addons/ipai/ipai_saas_billing/models/__init__.py`
  - `addons/ipai/ipai_saas_billing/controllers/__init__.py`
  - `addons/ipai/ipai_saas_billing/security/ir.model.access.csv`
- **Deliverables:**
  - OCA-compliant __manifest__.py (version, author, license, depends)
  - Depends: base, web, ipai_ops_connector
  - Category: InsightPulse AI / SaaS Platform
  - Models: subscription, usage_event (placeholders)
  - Security: access rights for user, admin roles
- **Acceptance:** Module installs without errors
- **Estimate:** 3 hours

**Task 1.10: Create subscription model**
- **File:** `addons/ipai/ipai_saas_billing/models/subscription.py`
- **Deliverables:**
  - Read-only model (data from Supabase via ipai_ops_connector)
  - Fields: plan_name, status, current_period_start/end, stripe_subscription_id
  - Computed field: days_until_renewal
  - Action: sync_from_supabase() (manual sync button)
- **Acceptance:** Model displays subscription data in tree/form views
- **Estimate:** 4 hours

**Task 1.11: Create usage_event model**
- **File:** `addons/ipai/ipai_saas_billing/models/usage_event.py`
- **Deliverables:**
  - Read-only model (log view)
  - Fields: event_type, metadata (JSONB), created_at
  - Filter: current month only (performance)
  - Search: by event_type, date range
- **Acceptance:** Model displays usage events in tree view
- **Estimate:** 3 hours

#### Billing Dashboard (Days 8-9)

**Task 1.12: Create billing dashboard view**
- **File:** `addons/ipai/ipai_saas_billing/views/billing_dashboard.xml`
- **Deliverables:**
  - Dashboard layout (current plan, usage meters, invoice history)
  - Current plan card (plan name, status, renewal date)
  - Usage meters:
    - AI runs (current/max, progress bar)
    - CMS items (current/max, progress bar)
    - Users (current/max, progress bar)
  - Upgrade button (visible if on free plan)
  - Invoice history table (date, amount, status, download link)
- **Acceptance:** Dashboard loads, displays mock data
- **Estimate:** 5 hours

**Task 1.13: Create Stripe Checkout controller**
- **File:** `addons/ipai/ipai_saas_billing/controllers/checkout.py`
- **Deliverables:**
  - Route: `/billing/checkout`
  - Generate Stripe Checkout session (server-side)
  - Pass org_id in session metadata
  - Redirect to Stripe hosted page
  - Success URL: /billing/success
  - Cancel URL: /billing/dashboard
- **Acceptance:** Clicking "Upgrade" redirects to Stripe Checkout
- **Estimate:** 4 hours

**Task 1.14: Create webhook test controller (dev only)**
- **File:** `addons/ipai/ipai_saas_billing/controllers/webhook_test.py`
- **Deliverables:**
  - Route: `/billing/webhook-test` (dev environment only)
  - Simulate Stripe webhook events
  - Test subscription.created, updated, deleted
  - Test invoice.payment_succeeded, failed
  - Display test results (pass/fail)
- **Acceptance:** Webhook test controller processes mock events
- **Estimate:** 3 hours

#### Testing & Validation (Day 10)

**Task 1.15: Write integration test: Billing cycle**
- **File:** `addons/ipai/ipai_saas_billing/tests/test_billing_cycle.py`
- **Deliverables:**
  - Test: User signs up → Free plan assigned
  - Test: User upgrades → Stripe Checkout → Webhook → Pro plan synced
  - Test: Invoice payment succeeds → Subscription active
  - Test: Invoice payment fails → Subscription past_due
  - Test: Usage event logged → Usage meter updated
- **Acceptance:** All tests pass
- **Estimate:** 5 hours

**Task 1.16: Deploy to staging and validate**
- **Files:** N/A (deployment)
- **Deliverables:**
  - Apply Supabase migrations to staging database
  - Deploy Edge Functions to staging
  - Install ipai_saas_billing module in staging Odoo
  - Run smoke tests:
    - Health check endpoint
    - Stripe webhook delivery (test mode)
    - Billing dashboard loads
    - Usage meters display
- **Acceptance:** Staging billing flow works end-to-end
- **Estimate:** 4 hours

---

## Phase 2: CMS Workflows + Odoo Integration (24 tasks)

### Week 3: CMS Infrastructure (Days 11-15)

#### Workflow Tables (Days 11-12)

**Task 2.1: Create cms_workflows migration**
- **File:** `supabase/migrations/20260212000200_cms_workflows.sql`
- **Deliverables:**
  - content_types table (name, schema JSONB)
  - cms_page_versions table (page_id, version_number, title, content_html, created_by)
  - cms_approvals table (page_id, version_id, status, requested_by, reviewed_by, comments)
  - cms_schedule table (page_id, action, scheduled_at, executed_at, status)
  - Unique constraint: (page_id, version_number)
  - Indexes on page_id, status, scheduled_at
- **Acceptance:** Migration runs, tables created with correct schema
- **Estimate:** 4 hours

**Task 2.2: Create cms RLS policies migration**
- **File:** `supabase/migrations/20260212000300_cms_rls.sql`
- **Deliverables:**
  - RLS on cms_approvals (org-scoped)
  - RLS on cms_page_versions (org-scoped)
  - RLS on cms_schedule (org-scoped)
  - Service role exception policies
  - Automated RLS test (cross-org access blocked)
- **Acceptance:** RLS tests pass, cross-org queries return empty
- **Estimate:** 3 hours

**Task 2.3: Seed content types**
- **File:** `supabase/migrations/20260212000201_seed_content_types.sql`
- **Deliverables:**
  - Seed "page" type (title, content_html, slug, meta_description)
  - Seed "post" type (title, content_html, author, published_at, tags)
  - Seed "case_study" type (title, content_html, industry, outcome, metrics)
  - JSON schemas for validation
- **Acceptance:** Content types seeded, schemas valid
- **Estimate:** 2 hours

#### Scheduled Publishing (Days 13-14)

**Task 2.4: Create activate_cron migration**
- **File:** `supabase/migrations/20260212000400_activate_cron.sql`
- **Deliverables:**
  - Enable pg_cron extension
  - Cron job: refresh-org-usage (every 5 minutes)
    - REFRESH MATERIALIZED VIEW CONCURRENTLY org_usage_current;
  - Cron job: execute-scheduled-publications (every 1 minute)
    - Call cms_publisher Edge Function via HTTP
  - Cron job: stuck-run-recovery (every 2 minutes)
    - Mark stuck jobs as failed (executed_at NULL, scheduled_at < NOW() - 10 minutes)
  - Monitoring: cron_job_runs table (logs execution history)
- **Acceptance:** Cron jobs execute on schedule
- **Estimate:** 4 hours

**Task 2.5: Create cms-publisher Edge Function**
- **File:** `supabase/functions/cms-publisher/index.ts`
- **Deliverables:**
  - Query cms_schedule for pending actions (scheduled_at <= NOW())
  - For each action:
    - If publish: Create version snapshot, update cms_pages.status = 'published'
    - If unpublish: Update cms_pages.status = 'draft'
    - Mark schedule row as executed (executed_at = NOW(), status = 'executed')
    - Send Realtime notification to org channel
  - Error handling: Log failures, mark as 'failed', retry on next run
  - Idempotency: Skip already executed actions
- **Acceptance:** Publisher executes scheduled actions within ±1min
- **Estimate:** 5 hours

**Task 2.6: Write unit tests for cms-publisher**
- **File:** `supabase/functions/cms-publisher/index.test.ts`
- **Deliverables:**
  - Test: Pending publish action → Status = published, executed_at set
  - Test: Pending unpublish action → Status = draft, executed_at set
  - Test: Already executed action → Skip (idempotency)
  - Test: Failed action → Log error, mark as failed
  - Test: Realtime notification sent
- **Acceptance:** All tests pass, 80% coverage
- **Estimate:** 3 hours

#### Version History (Day 15)

**Task 2.7: Create version snapshot trigger**
- **File:** `supabase/migrations/20260212000202_version_snapshot_trigger.sql`
- **Deliverables:**
  - Trigger on cms_pages (AFTER UPDATE OF status)
  - Create version snapshot in cms_page_versions
  - Increment version_number
  - Store full page content + metadata
  - Track created_by (from auth.uid())
- **Acceptance:** Version snapshot created on status change
- **Estimate:** 3 hours

**Task 2.8: Create version comparison function**
- **File:** `supabase/functions/cms-version-compare/index.ts`
- **Deliverables:**
  - RPC function: compare_versions(version_id_1, version_id_2)
  - Generate side-by-side diff HTML
  - Highlight added (green), removed (red), changed (yellow) content
  - Return JSONB: { diff_html: string, added_lines: number, removed_lines: number }
- **Acceptance:** Diff HTML renders correctly in Odoo
- **Estimate:** 4 hours

### Week 4: Odoo CMS Module (Days 16-20)

#### Module Scaffolding (Days 16-17)

**Task 2.9: Create ipai_platform_cms Odoo module**
- **Files:**
  - `addons/ipai/ipai_platform_cms/__manifest__.py`
  - `addons/ipai/ipai_platform_cms/models/__init__.py`
  - `addons/ipai/ipai_platform_cms/controllers/__init__.py`
  - `addons/ipai/ipai_platform_cms/security/ir.model.access.csv`
- **Deliverables:**
  - OCA-compliant __manifest__.py
  - Depends: ipai_saas_billing, ipai_ops_connector
  - Category: InsightPulse AI / CMS
  - Models: cms_page, cms_approval, cms_version (placeholders)
  - Security: access rights for editor, admin roles
- **Acceptance:** Module installs without errors
- **Estimate:** 3 hours

**Task 2.10: Create cms_page model**
- **File:** `addons/ipai/ipai_platform_cms/models/cms_page.py`
- **Deliverables:**
  - Sync from Supabase via ipai_ops_connector
  - Fields: title, content_html, status, content_type, slug, metadata
  - Computed field: current_version (latest version_number)
  - Actions: request_approval(), schedule_publish(datetime)
  - Status selection: draft, pending, approved, published
- **Acceptance:** Model displays CMS pages in tree/form views
- **Estimate:** 4 hours

**Task 2.11: Create cms_approval model**
- **File:** `addons/ipai/ipai_platform_cms/models/cms_approval.py`
- **Deliverables:**
  - Sync from Supabase
  - Fields: page_id, version_id, status, requested_by, reviewed_by, comments
  - Actions: approve(), reject(comments)
  - Status selection: pending, approved, rejected
  - Realtime subscription: Notify on status change
- **Acceptance:** Model displays approvals in Kanban/list views
- **Estimate:** 4 hours

**Task 2.12: Create cms_version model**
- **File:** `addons/ipai/ipai_platform_cms/models/cms_version.py`
- **Deliverables:**
  - Read-only model (version history)
  - Fields: page_id, version_number, title, content_html, created_by, created_at
  - Action: compare_with_previous() (shows diff)
  - Computed field: diff_summary (X lines added, Y removed)
- **Acceptance:** Model displays version history in tree view
- **Estimate:** 3 hours

#### CMS Editor Views (Days 18-19)

**Task 2.13: Create content editor view**
- **File:** `addons/ipai/ipai_platform_cms/views/cms_page_form.xml`
- **Deliverables:**
  - Form view: title (char), content_html (HTML editor widget), status (statusbar)
  - Tabs: Content, Metadata (slug, meta_description, tags), Version History
  - Buttons:
    - Request Approval (visible if status = draft)
    - Schedule Publish (datetime picker, visible if status = approved)
    - Save Draft
  - Statusbar widget: draft → pending → approved → published
- **Acceptance:** Form view loads, HTML editor functional
- **Estimate:** 5 hours

**Task 2.14: Create approval queue views**
- **File:** `addons/ipai/ipai_platform_cms/views/cms_approval_views.xml`
- **Deliverables:**
  - Kanban view: Cards grouped by status (pending, approved, rejected)
    - Card: Page title, requested_by, created_at
  - List view: Columns: Page, Status, Requested By, Date
    - Filters: My Requests, Pending Approvals
  - Form view:
    - Side-by-side diff (iframe with compare_versions output)
    - Approve button (green, visible if status = pending)
    - Reject button (red, opens comment modal)
    - Comments field (text area)
- **Acceptance:** Approval queue displays correctly, actions work
- **Estimate:** 6 hours

**Task 2.15: Create schedule publish action**
- **File:** `addons/ipai/ipai_platform_cms/models/cms_page.py` (method)
- **Deliverables:**
  - Action: schedule_publish(scheduled_at)
  - Insert into cms_schedule table (via Supabase RPC)
  - Validation: scheduled_at > NOW(), page status = approved
  - Toast notification: "Page scheduled for publish at {datetime}"
- **Acceptance:** Scheduling action creates cms_schedule row
- **Estimate:** 3 hours

#### Realtime Notifications (Day 20)

**Task 2.16: Subscribe to cms_approvals channel**
- **File:** `addons/ipai/ipai_platform_cms/static/src/js/realtime_notifications.js`
- **Deliverables:**
  - Supabase Realtime subscription: cms_approvals table
  - Filter: org_id = current user's org
  - On INSERT/UPDATE: Toast notification
    - "Your content was approved by {reviewer}"
    - "Your content was rejected: {comments}"
  - Link to page in notification
- **Acceptance:** Toast appears on approval/rejection
- **Estimate:** 4 hours

**Task 2.17: Subscribe to cms_schedule channel**
- **File:** `addons/ipai/ipai_platform_cms/static/src/js/realtime_notifications.js`
- **Deliverables:**
  - Supabase Realtime subscription: cms_schedule table
  - Filter: org_id = current user's org, status = executed
  - On UPDATE (status → executed): Toast notification
    - "Page '{title}' published successfully"
  - Refresh page list view
- **Acceptance:** Toast appears on successful publish
- **Estimate:** 3 hours

### Week 5: Platform Admin Module (Days 21-25)

#### Module Scaffolding (Days 21-22)

**Task 2.18: Create ipai_platform_admin Odoo module**
- **Files:**
  - `addons/ipai/ipai_platform_admin/__manifest__.py`
  - `addons/ipai/ipai_platform_admin/models/__init__.py`
  - `addons/ipai/ipai_platform_admin/controllers/__init__.py`
  - `addons/ipai/ipai_platform_admin/security/ir.model.access.csv`
- **Deliverables:**
  - OCA-compliant __manifest__.py
  - Depends: ipai_saas_billing, ipai_ops_connector
  - Category: InsightPulse AI / Platform Admin
  - Models: organization, team_member (placeholders)
  - Security: Admin role only
- **Acceptance:** Module installs without errors
- **Estimate:** 3 hours

**Task 2.19: Create organization model**
- **File:** `addons/ipai/ipai_platform_admin/models/organization.py`
- **Deliverables:**
  - Sync from Supabase
  - Fields: name, billing_email, timezone, created_at
  - Computed fields:
    - current_plan (from subscriptions table)
    - usage_summary (from org_usage_current view)
  - Action: sync_from_supabase() (manual sync button)
- **Acceptance:** Model displays org data in form view
- **Estimate:** 3 hours

**Task 2.20: Create team_member model**
- **File:** `addons/ipai/ipai_platform_admin/models/team_member.py`
- **Deliverables:**
  - Sync from Supabase (user_organizations table)
  - Fields: user_id, email, role, created_at
  - Actions:
    - invite_user(email, role) (calls Supabase Auth API)
    - remove_user(user_id)
  - Role selection: admin, editor, viewer
- **Acceptance:** Model displays team members in tree view
- **Estimate:** 4 hours

#### Org Dashboard (Days 23-24)

**Task 2.21: Create org dashboard view**
- **File:** `addons/ipai/ipai_platform_admin/views/org_dashboard.xml`
- **Deliverables:**
  - Dashboard layout:
    - Org details card (name, billing email, plan)
    - Usage metrics (AI runs, CMS items, users vs. limits)
    - Team members list (table with invite button)
    - Org settings link
  - Usage metrics: Progress bars (green if <80%, yellow 80-95%, red >95%)
  - Invite user button (opens modal with email input, role selector)
- **Acceptance:** Dashboard loads, displays mock data
- **Estimate:** 5 hours

**Task 2.22: Create invite user controller**
- **File:** `addons/ipai/ipai_platform_admin/controllers/invite_user.py`
- **Deliverables:**
  - Route: `/admin/invite-user`
  - Validation:
    - Email format check
    - Check user limit against plan (call entitlement-check)
    - Check if email already exists
  - Call Supabase Auth API: inviteUserByEmail(email)
  - Send invite email (Supabase handles this)
  - Toast notification: "Invite sent to {email}"
- **Acceptance:** Invite user sends email, creates user_organizations row
- **Estimate:** 4 hours

**Task 2.23: Create org settings view**
- **File:** `addons/ipai/ipai_platform_admin/views/org_settings_form.xml`
- **Deliverables:**
  - Form view: name, billing_email, timezone
  - Save button (calls Supabase RPC: update_organization)
  - Validation: Email format, timezone from dropdown
  - Toast notification: "Organization settings updated"
- **Acceptance:** Settings form saves correctly
- **Estimate:** 3 hours

**Task 2.24: Write integration tests: Team management**
- **File:** `addons/ipai/ipai_platform_admin/tests/test_team_management.py`
- **Deliverables:**
  - Test: Admin invites user → Email sent, user_organizations created
  - Test: Invite fails if user limit reached (entitlement check)
  - Test: Admin removes user → user_organizations deleted
  - Test: Non-admin cannot invite users (access control)
- **Acceptance:** All tests pass
- **Estimate:** 4 hours

#### Integration Testing (Day 25)

**Task 2.25: Write integration test: CMS approval workflow**
- **File:** `addons/ipai/ipai_platform_cms/tests/test_cms_workflow.py`
- **Deliverables:**
  - Test: Editor creates page (status = draft)
  - Test: Editor requests approval → cms_approval created, status = pending
  - Test: Admin approves → cms_pages.status = approved, notification sent
  - Test: Admin rejects → cms_pages.status = draft, comments stored
  - Test: Approved page scheduled → cms_schedule created
  - Test: pg_cron executes → status = published, notification sent
- **Acceptance:** All tests pass, workflow <5s end-to-end
- **Estimate:** 6 hours

**Task 2.26: Write integration test: Scheduled publishing**
- **File:** `addons/ipai/ipai_platform_cms/tests/test_scheduled_publishing.py`
- **Deliverables:**
  - Test: Create scheduled publish (scheduled_at = NOW() + 2 minutes)
  - Test: Wait for pg_cron execution
  - Test: Verify status = published, executed_at set
  - Test: Verify Realtime notification sent
  - Test: Verify publish accuracy ±1min
- **Acceptance:** All tests pass, accuracy within ±1min
- **Estimate:** 4 hours

**Task 2.27: Write integration test: Version history**
- **File:** `addons/ipai/ipai_platform_cms/tests/test_version_history.py`
- **Deliverables:**
  - Test: Page status change → Version snapshot created
  - Test: Version number increments
  - Test: compare_versions() returns diff HTML
  - Test: Diff highlights added/removed content
- **Acceptance:** All tests pass, diff accurate
- **Estimate:** 4 hours

**Task 2.28: Deploy to staging and validate**
- **Files:** N/A (deployment)
- **Deliverables:**
  - Apply CMS migrations to staging database
  - Deploy cms-publisher Edge Function
  - Install ipai_platform_cms, ipai_platform_admin modules
  - Run smoke tests:
    - CMS approval workflow (draft → approval → published)
    - Scheduled publishing (create → execute → verify)
    - Team member invite (send → receive → accept)
    - Version history (create → compare → diff)
- **Acceptance:** Staging CMS + admin flows work end-to-end
- **Estimate:** 5 hours

---

## Phase 2.5: Testing & Documentation (8 tasks)

### Week 6: Quality Assurance (Days 26-30)

#### Unit & Integration Tests (Days 26-27)

**Task 3.1: Write unit tests: All Stripe webhook event types**
- **File:** `supabase/functions/stripe-webhook/index.test.ts`
- **Deliverables:**
  - Test: customer.subscription.created → Insert
  - Test: customer.subscription.updated → Update
  - Test: customer.subscription.deleted → Cancel
  - Test: invoice.payment_succeeded → Mark active
  - Test: invoice.payment_failed → Mark past_due
  - Test: Unknown event type → Log, return 200 OK
- **Acceptance:** 100% event type coverage
- **Estimate:** 3 hours

**Task 3.2: Write unit tests: Entitlement edge cases**
- **File:** `supabase/functions/entitlement-check/index.test.ts`
- **Deliverables:**
  - Test: Exactly at limit (current = max) → allowed = false
  - Test: Over limit (current > max) → allowed = false
  - Test: No subscription (new org) → Free plan limits applied
  - Test: Invalid limit_type → Error
  - Test: Org not found → Error
- **Acceptance:** All edge cases covered
- **Estimate:** 2 hours

**Task 3.3: Write RLS security tests**
- **File:** `supabase/tests/rls_security.test.sql`
- **Deliverables:**
  - Test: Org A user queries Org B subscriptions → Empty result
  - Test: Org A user queries Org B usage_events → Empty result
  - Test: Org A user queries Org B cms_approvals → Empty result
  - Test: Org A user inserts into Org B tables → Error (blocked)
  - Test: Service role bypasses RLS → Success (logged)
- **Acceptance:** All tests pass, zero cross-org leaks
- **Estimate:** 4 hours

**Task 3.4: Write integration test: Complete billing cycle**
- **File:** `tests/integration/test_billing_cycle.ts`
- **Deliverables:**
  - Test: User signup → Org created → Free plan assigned
  - Test: User upgrades → Stripe Checkout → Webhook → Pro plan synced
  - Test: AI run triggered → Usage event logged → Meter updated
  - Test: Invoice generated → Payment succeeds → Subscription active
  - Test: User reaches limit → Entitlement blocks → Error message
- **Acceptance:** Full cycle <30s, all steps verified
- **Estimate:** 5 hours

#### E2E Tests (Day 28)

**Task 3.5: Write E2E test: Billing flow**
- **File:** `apps/web/tests/e2e/billing.spec.ts` (Playwright)
- **Deliverables:**
  - Test: Login → Navigate to billing dashboard
  - Test: Dashboard displays current plan, usage meters
  - Test: Click "Upgrade to Pro" → Redirected to Stripe Checkout
  - Test: Complete payment (Stripe test mode) → Redirected back
  - Test: Dashboard shows "Pro" plan, updated limits
  - Test: Invoice appears in history table
- **Acceptance:** E2E test passes, <60s runtime
- **Estimate:** 4 hours

**Task 3.6: Write E2E test: CMS workflow**
- **File:** `apps/web/tests/e2e/cms_workflow.spec.ts` (Playwright)
- **Deliverables:**
  - Test: Login as Editor → Create new page (status = draft)
  - Test: Click "Request Approval" → Approval created
  - Test: Login as Admin → Open approval queue → See pending approval
  - Test: Click "Approve" → Page status = published
  - Test: Realtime toast notification appears
  - Test: Page visible on public site
- **Acceptance:** E2E test passes, <45s runtime
- **Estimate:** 5 hours

**Task 3.7: Write E2E test: Scheduled publishing**
- **File:** `apps/web/tests/e2e/scheduled_publishing.spec.ts` (Playwright)
- **Deliverables:**
  - Test: Login as Editor → Create page → Request approval
  - Test: Login as Admin → Approve page
  - Test: Editor schedules for publish (NOW() + 2 minutes)
  - Test: Wait for pg_cron execution (poll status every 10s)
  - Test: Verify status = published, toast notification
  - Test: Page visible on public site
- **Acceptance:** E2E test passes, publish within ±1min
- **Estimate:** 4 hours

#### Staging Deployment & Documentation (Days 29-30)

**Task 3.8: Provision staging environment**
- **Files:** `infra/do/staging-droplet.tf` (Terraform)
- **Deliverables:**
  - Provision staging.insightpulseai.com droplet (2GB RAM, 50GB SSD)
  - Install Docker + docker-compose
  - Configure Odoo 19 CE (same setup as production)
  - Apply all Supabase migrations
  - Deploy all Edge Functions
  - Configure DNS (Cloudflare A record)
  - Configure SSL (Let's Encrypt)
- **Acceptance:** staging.insightpulseai.com accessible via HTTPS
- **Estimate:** 6 hours

---

**Total Effort Estimate:** 48 tasks × ~4 hours average = **192 hours** (6 weeks at 32 hours/week)

**Contingency Buffer:** 20% (38 hours) for debugging, scope adjustments, unforeseen issues

**Final Estimate:** 230 hours (7.2 weeks) → Fits within 6-week sprint with moderate crunch

---

*Last updated: 2026-02-11*
