# Platform Kit Implementation Plan

**Version:** 1.0.0
**Last Updated:** 2026-01-27
**Status:** Planning

---

## Overview

This plan details the phased implementation of Platform Kit, organized by milestone with dependencies, acceptance criteria, and rollout strategy.

---

## Milestone Breakdown

```
M0 (Complete) → M1 (8 weeks) → M2 (6 weeks) → M3 (8 weeks) → M4 (6 weeks)
    ↓              ↓               ↓               ↓               ↓
Foundation    Supabase Kit    Governance     Connectors     UI Console
```

---

## M0: Foundation (Complete)

**Status:** ✅ Complete

**Deliverables:**
- [x] Parity agent spec bundle (`spec/parity-agent/`)
- [x] Capability schema (`kb/parity/capability_schema.json`)
- [x] Parity matrix schema (`kb/parity/parity_matrix.schema.json`)
- [x] Contract test harness (`harness/runners/run_parity_checks.sh`)
- [x] CI workflow (`parity.yml`)
- [x] Schema validator (`scripts/validate_json_schema.mjs`)

**Evidence:**
- Nightly parity checks running
- Schema validation passing
- Contract test framework operational

---

## M1: Supabase Platform Kit (8 weeks)

**Goal:** Establish introspection engine + security hardening baseline

### Phase 1.1: Control Plane Schema (Week 1-2)

**Tasks:**
1. Create `ops` schema migration
   - Tables: `platform_projects`, `inventory_scans`, `inventory_objects`, `parity_definitions`, `parity_results`, `risk_register`, `remediation_plans`
   - Indexes: All primary keys, foreign keys, scan_id/project_id lookups
   - RLS: Service role only (control plane is server-side)

2. Seed baseline parity definitions
   - File: `supabase/seed/ops_parity_baseline.sql`
   - Source: 17 EE features from `config/ee_parity/ee_feature_catalog.yml`

**Acceptance Criteria:**
- [ ] Migration applies cleanly on fresh Supabase project
- [ ] All tables have RLS enabled (service role only)
- [ ] Seed data loads without errors

**Outputs:**
- `supabase/migrations/20260127_ops_schema.sql`
- `supabase/seed/ops_parity_baseline.sql`

### Phase 1.2: Introspection Runner (Week 3-4)

**Tasks:**
1. Edge Function: `introspection-runner`
   - **Input:** `{ project_id, source: 'supabase' | 'github' | 'connector' }`
   - **Logic:**
     - Supabase: Query `pg_catalog` for schemas/tables/views/functions/extensions/policies
     - GitHub: Use GitHub API to list repos, workflows, structure
     - Connector: Call connector's `inventory()` method
   - **Output:** Insert to `ops.inventory_objects` with `scan_id`

2. Security checks module
   - Check RLS coverage: `SELECT * FROM pg_class WHERE relrowsecurity = false`
   - Check function security: `SELECT * FROM pg_proc WHERE prosecdef = true AND proconfig IS NULL`
   - Check extensions schema: `SELECT * FROM pg_extension WHERE extnamespace != 'extensions'::regnamespace`
   - Check slow queries: Query Supabase logs API (if available)

**Acceptance Criteria:**
- [ ] Edge Function deploys successfully
- [ ] Supabase scan populates `inventory_objects` with tables/functions/policies
- [ ] Security checks flag known issues (test with unsafe schema)
- [ ] Scan duration logged to `ops.metrics`

**Outputs:**
- `supabase/functions/introspection-runner/index.ts`
- `supabase/functions/introspection-runner/security-checks.ts`

### Phase 1.3: Remediation Applier (Week 5-6)

**Tasks:**
1. Edge Function: `remediation-applier`
   - **Input:** `{ plan_id, dry_run: boolean }`
   - **Logic:**
     - Fetch plan from `ops.remediation_plans`
     - Validate SQL patch (parse, check for DROP/TRUNCATE without safeguards)
     - Apply patch via service role connection
     - Log outcome to `ops.audit_log`
   - **Output:** Update `remediation_plans.status` to `applied` or `failed`

2. Autofix migrations library
   - RLS enablement: `ALTER TABLE <name> ENABLE ROW LEVEL SECURITY`
   - Extensions move: `ALTER EXTENSION <name> SET SCHEMA extensions`
   - Search path hardening: `ALTER FUNCTION <name> SET search_path = pg_catalog, public`

**Acceptance Criteria:**
- [ ] Dry run mode generates preview without applying
- [ ] Applied patches are idempotent (re-running safe)
- [ ] Audit log captures who/what/when
- [ ] Rollback plan documented for each patch type

**Outputs:**
- `supabase/functions/remediation-applier/index.ts`
- `supabase/functions/remediation-applier/autofixes.ts`

### Phase 1.4: CI Integration (Week 7-8)

**Tasks:**
1. Workflow: `supabase-introspection.yml`
   - Trigger: Nightly + on-demand
   - Steps:
     1. Call `introspection-runner` Edge Function
     2. Fetch results from `ops.inventory_scans`
     3. Generate compliance report (Markdown)
     4. Post to GitHub issue if critical issues found
     5. Generate remediation plan (SQL patches)

2. Pre-deployment gate: `supabase-schema-check.yml`
   - Trigger: On PR with `supabase/migrations/` changes
   - Steps:
     1. Validate migration syntax (dry-run on shadow DB)
     2. Check for unsafe operations (DROP without backfill, ALTER without DEFAULT)
     3. Run migration on test DB
     4. Run introspection + security checks
     5. Fail if new RLS gaps or function security issues

**Acceptance Criteria:**
- [ ] Nightly workflow runs successfully
- [ ] Compliance report generated and posted to GitHub
- [ ] PR gate blocks unsafe migrations
- [ ] Test DB cleaned up after PR check

**Outputs:**
- `.github/workflows/supabase-introspection.yml`
- `.github/workflows/supabase-schema-check.yml`

---

## M2: Org Kit + Enterprise Kit (6 weeks)

**Goal:** Governance-as-code for repos + GitHub Enterprise

### Phase 2.1: Spec Bundle Enforcement (Week 1-2)

**Tasks:**
1. Workflow: `spec-kit-enforce.yml` (enhance existing)
   - Check: All significant features have spec bundle (`spec/<feature>/`)
   - Required files: `constitution.md`, `prd.md`, `plan.md`, `tasks.md`
   - Validation: Parse frontmatter, check completeness
   - Fail: If PR adds >500 LOC without spec bundle

2. Repo templates
   - `templates/repo-app/` - Application repo structure
   - `templates/repo-service/` - Microservice repo structure
   - `templates/repo-lib/` - Library repo structure
   - `templates/repo-connector/` - Connector repo structure
   - Include: `.github/workflows/`, `spec/`, `docs/`, baseline `CLAUDE.md`

**Acceptance Criteria:**
- [ ] PR with major feature blocked if spec missing
- [ ] Template repos generate cleanly via GitHub template button
- [ ] All templates pass CI checks out-of-box

**Outputs:**
- `.github/workflows/spec-kit-enforce.yml` (enhanced)
- `templates/repo-*/` directories

### Phase 2.2: Deterministic Diagrams (Week 2-3)

**Tasks:**
1. Workflow: `diagrams-ci.yml`
   - Trigger: On PR with `docs/architecture/*.drawio` changes
   - Steps:
     1. Install draw.io CLI (`@hediet/node-drawio`)
     2. Export all `.drawio` files to `.png`
     3. Compare exported PNGs with committed PNGs (image diff)
     4. Fail if diff >5% (manual edit detected)
     5. Auto-commit updated PNGs if `.drawio` changed

2. Pre-commit hook template
   - Hook: Block commits of `.png` files if corresponding `.drawio` modified
   - Message: "Regenerate diagrams via CI (do not manually edit PNGs)"

**Acceptance Criteria:**
- [ ] CI regenerates PNGs from `.drawio` sources
- [ ] Manual PNG edits rejected
- [ ] Diagram exports reproducible (same input → same output)

**Outputs:**
- `.github/workflows/diagrams-ci.yml`
- `.github/hooks/pre-commit-diagrams.sh` (template)

### Phase 2.3: Doc Tri-Sync (Week 3-4)

**Tasks:**
1. Workflow: `doc-sync-check.yml`
   - Trigger: On PR with `CLAUDE.md`, `GEMINI.md`, or `CODEX.md` changes
   - Steps:
     1. Parse all three docs (Markdown AST)
     2. Compare section structure (headings, key rules)
     3. Calculate drift score (% of content unique to one file)
     4. Fail if drift >10%
     5. Generate sync suggestions (which sections to copy)

2. Doc sync CLI tool
   - Command: `npm run doc-sync --from=CLAUDE.md --to=GEMINI.md,CODEX.md`
   - Logic: Copy specified sections with AI-context-specific adjustments
   - Interactive: Prompt for section selection if not specified

**Acceptance Criteria:**
- [ ] Drift detection accurate (test with known divergent docs)
- [ ] CLI tool syncs docs correctly (manual verification)
- [ ] PR blocked if drift excessive

**Outputs:**
- `.github/workflows/doc-sync-check.yml`
- `scripts/doc-sync.ts`

### Phase 2.4: Enterprise README Generator (Week 4-6)

**Tasks:**
1. Script: `generate_enterprise_readme.ts`
   - **Input:** Query `ops.inventory_objects` for all repos
   - **Logic:**
     - Group repos by category (apps, services, libs, connectors)
     - Extract metadata: maturity score, CI status, last deploy
     - Fetch governance controls: branch protection, required checks, secret scanning
     - Render via template (`templates/enterprise-readme.md.j2`)
   - **Output:** `README.md` in org profile repo

2. Workflow: `generate-enterprise-readme.yml`
   - Trigger: Nightly + on inventory scan completion
   - Steps:
     1. Run `generate_enterprise_readme.ts`
     2. Commit updated README to org profile repo
     3. Open PR if manual review required (breaking changes)

**Acceptance Criteria:**
- [ ] README generated with accurate repo inventory
- [ ] Governance controls reflected correctly
- [ ] Manual edits overwritten (edit template, not output)

**Outputs:**
- `scripts/generate_enterprise_readme.ts`
- `.github/workflows/generate-enterprise-readme.yml`
- `templates/enterprise-readme.md.j2`

---

## M3: Connector Kit (8 weeks)

**Goal:** Standard connector interface + integration with n8n/Superset/Odoo

### Phase 3.1: Connector Interface SDK (Week 1-2)

**Tasks:**
1. Package: `@platform-kit/connector-sdk`
   - **Exports:**
     - `ConnectorBase` - Abstract class with standard interface
     - `inventory()` - Return list of objects
     - `health()` - Return status + latency
     - `capabilities()` - Return supported features
     - `contract_tests()` - Run self-validation
   - **Utilities:**
     - Event outbox/inbox helpers
     - Retry with exponential backoff
     - Idempotency key generation
     - Secrets loading (from Supabase Vault)

2. TypeScript types
   - `Connector`, `InventoryObject`, `HealthStatus`, `Capability`, `ContractTestResult`
   - JSON schema for each type (validation)

**Acceptance Criteria:**
- [ ] SDK publishes to npm
- [ ] Example connector compiles and type-checks
- [ ] Utilities tested (outbox, retry, idempotency)

**Outputs:**
- `packages/connector-sdk/` package
- `packages/connector-sdk/examples/` sample connector

### Phase 3.2: n8n Connector (Week 3-4)

**Tasks:**
1. Edge Function: `connector-n8n`
   - **Inventory:**
     - List workflows via n8n API (`GET /workflows`)
     - List executions (`GET /executions`)
     - Extract: workflow name, active status, last execution, error rate
   - **Health:**
     - Call n8n health endpoint (`GET /health`)
     - Measure latency
   - **Capabilities:**
     - Return: `['workflow_trigger', 'webhook_ingress', 'execution_history']`
   - **Contract Tests:**
     - Test workflow trigger (send test payload)
     - Verify webhook response (200 OK)
     - Check execution history (verify test run logged)

2. Event contracts
   - Outbox: Workflow completed events → Supabase `ops.run_events`
   - Inbox: Trigger workflow via webhook (idempotent)

**Acceptance Criteria:**
- [ ] Inventory populates `ops.inventory_objects` with workflows
- [ ] Health check reports latency + status
- [ ] Contract tests pass (webhook trigger + execution verified)

**Outputs:**
- `supabase/functions/connector-n8n/index.ts`
- `supabase/functions/connector-n8n/contract-tests.ts`

### Phase 3.3: Superset Connector (Week 5-6)

**Tasks:**
1. Edge Function: `connector-superset`
   - **Inventory:**
     - List dashboards via Superset API (`GET /api/v1/dashboard/`)
     - List datasets (`GET /api/v1/dataset/`)
     - Extract: dashboard name, owner, charts count, last viewed
   - **Health:**
     - Call Superset health endpoint (`GET /health`)
   - **Capabilities:**
     - Return: `['dashboard_embed', 'dataset_query', 'chart_export']`
   - **Contract Tests:**
     - Query dataset (verify schema)
     - Fetch dashboard metadata (verify charts list)

2. Event contracts
   - Outbox: Dashboard viewed events → Supabase analytics
   - Inbox: Dataset refresh trigger (via Superset webhook)

**Acceptance Criteria:**
- [ ] Inventory populates dashboards + datasets
- [ ] Health check reports Superset status
- [ ] Contract tests pass (query + metadata fetch)

**Outputs:**
- `supabase/functions/connector-superset/index.ts`
- `supabase/functions/connector-superset/contract-tests.ts`

### Phase 3.4: Odoo Connector (Week 7-8)

**Tasks:**
1. Edge Function: `connector-odoo`
   - **Inventory:**
     - List modules via XML-RPC (`ir.module.module.search_read`)
     - List models (`ir.model.search_read`)
     - Extract: module name, state, installed version
   - **Health:**
     - Call Odoo health endpoint (custom route `/web/health`)
   - **Capabilities:**
     - Return: `['module_install', 'data_sync', 'webhook_receiver']`
   - **Contract Tests:**
     - Query partner model (verify RPC works)
     - Trigger webhook (verify received)

2. Event contracts
   - Outbox: Record created events → Supabase (via Odoo webhook)
   - Inbox: Sync data from Supabase → Odoo (via scheduled job)

**Acceptance Criteria:**
- [ ] Inventory populates Odoo modules
- [ ] Health check works (test against live Odoo instance)
- [ ] Contract tests pass (RPC + webhook)

**Outputs:**
- `supabase/functions/connector-odoo/index.ts`
- `supabase/functions/connector-odoo/contract-tests.ts`

---

## M4: UI Platform Console (6 weeks)

**Goal:** Admin dashboard for introspection + governance + connectors

### Phase 4.1: Console Foundation (Week 1-2)

**Tasks:**
1. Next.js app: `packages/platform-console/`
   - Framework: Next.js 15 + TypeScript + Tailwind + shadcn/ui
   - Auth: Supabase Auth (service role for admin, user accounts for read-only)
   - Layout: Databricks-style sidebar (Projects, Jobs, Catalogs, Runs, Artifacts)
   - Theme: Platform Kit design tokens (`tokens.json`)

2. Core routes
   - `/` - Dashboard (overview stats)
   - `/projects` - List all platform projects
   - `/inventory` - Inventory browser
   - `/risks` - Risk register viewer
   - `/remediation` - Fix plan viewer

**Acceptance Criteria:**
- [ ] App deploys to Vercel
- [ ] Auth works (service role admin + user read-only)
- [ ] Layout renders with sidebar navigation

**Outputs:**
- `packages/platform-console/` Next.js app

### Phase 4.2: Inventory Browser (Week 2-3)

**Tasks:**
1. Page: `/inventory`
   - **View:** Tree view of projects → schemas → tables/views/functions/policies
   - **Data:** Query `ops.inventory_objects` grouped by project_id + object_type
   - **Filters:** By project, by object type, by risk flags
   - **Details:** Click object → view full JSON + risk flags + remediation suggestions

2. Risk highlights
   - Visual: Red badge for critical, orange for high, yellow for medium
   - Tooltip: Show risk description on hover

**Acceptance Criteria:**
- [ ] Tree view renders with all projects
- [ ] Filters work (test with multiple projects)
- [ ] Risk badges visible and correct

**Outputs:**
- `packages/platform-console/app/inventory/page.tsx`
- `packages/platform-console/components/inventory-tree.tsx`

### Phase 4.3: Remediation Viewer (Week 3-4)

**Tasks:**
1. Page: `/remediation`
   - **View:** List of remediation plans grouped by severity
   - **Data:** Query `ops.remediation_plans` with join to `ops.inventory_objects`
   - **Actions:**
     - Preview patch (syntax-highlighted SQL diff)
     - Apply patch (dry-run first, then real apply)
     - Mark as applied or deferred
   - **Audit:** Show who applied, when, and outcome

2. Apply flow
   - Confirm dialog (show patch, warn about irreversibility)
   - Call `remediation-applier` Edge Function
   - Poll status, show progress
   - Display result (success/failure with logs)

**Acceptance Criteria:**
- [ ] Plans listed correctly by severity
- [ ] Patch preview renders (syntax highlighting)
- [ ] Apply flow works (test with safe patch)
- [ ] Audit log updated after apply

**Outputs:**
- `packages/platform-console/app/remediation/page.tsx`
- `packages/platform-console/components/patch-preview.tsx`

### Phase 4.4: Jobs & Runs Viewer (Week 4-5)

**Tasks:**
1. Page: `/jobs`
   - **View:** Table of jobs (introspection scans, contract test runs, deployments)
   - **Data:** Query `ops.contract_test_runs`, `ops.inventory_scans`, `ops.deployments`
   - **Filters:** By status (queued, running, completed, failed), by project
   - **Details:** Click job → view run events, artifacts, logs

2. Databricks-style timeline
   - Gantt chart for job runs (start time, duration, dependencies)
   - Real-time updates (via Supabase Realtime)

**Acceptance Criteria:**
- [ ] Jobs table populated with runs
- [ ] Filters work correctly
- [ ] Timeline renders (test with multiple overlapping jobs)
- [ ] Real-time updates work (trigger scan, see it appear)

**Outputs:**
- `packages/platform-console/app/jobs/page.tsx`
- `packages/platform-console/components/job-timeline.tsx`

### Phase 4.5: Connector Status (Week 5-6)

**Tasks:**
1. Page: `/connectors`
   - **View:** Card grid of connectors (n8n, Superset, Odoo, etc.)
   - **Data:** Query `ops.inventory_objects` filtered by `object_type = 'connector'`
   - **Metrics:** Last sync time, latency, success rate, error count
   - **Actions:**
     - Trigger sync (call connector's `inventory()`)
     - View logs (link to `ops.run_events`)
     - Test health (call `health()`)

2. Health indicators
   - Green: Last sync <1h, success rate >95%
   - Yellow: Last sync 1-24h, success rate 80-95%
   - Red: Last sync >24h or success rate <80%

**Acceptance Criteria:**
- [ ] Connectors listed with correct status
- [ ] Trigger sync works (test with n8n connector)
- [ ] Health indicators accurate

**Outputs:**
- `packages/platform-console/app/connectors/page.tsx`
- `packages/platform-console/components/connector-card.tsx`

---

## Cross-Cutting Concerns

### Testing Strategy

**Unit Tests:**
- All utility functions (Edge Functions, SDK)
- Coverage target: >80%
- Framework: Vitest (TS), pytest (Python)

**Integration Tests:**
- Edge Functions (against local Supabase)
- Connectors (against test instances)
- Framework: Playwright + Supabase CLI

**Contract Tests:**
- API contracts (OpenAPI validation)
- Data contracts (schema invariants)
- Event contracts (outbox/inbox delivery)
- Behavior contracts (end-to-end user journeys)

**CI Integration:**
- Run on every PR
- Fail fast on first error
- Cache test dependencies

### Security Hardening

**Supabase:**
- All migrations reviewed for RLS coverage
- All functions reviewed for search_path hardening
- Secret scanning in CI (pre-commit + PR gate)

**GitHub:**
- Branch protection on main/master
- Required checks: lint, test, security, parity
- CODEOWNERS for sensitive paths

### Documentation

**Auto-Generated:**
- API docs (TypeDoc for TS, Sphinx for Python)
- Schema docs (from `ops` schema comments)
- Changelog (from conventional commits)

**Manual:**
- Architecture decisions (ADRs in `docs/adr/`)
- Runbooks (in `docs/runbooks/`)
- Troubleshooting guide (`docs/TROUBLESHOOTING.md`)

---

## Dependencies & Risks

### Critical Dependencies

1. **Supabase CLI** - For migrations, Edge Function deployment
2. **GitHub API** - For repo introspection, workflow status
3. **Connector APIs** - n8n, Superset, Odoo (external systems)
4. **Pulser SDK** - For agent orchestration (cross-dependency)

### Known Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Supabase API rate limits | High | Implement backoff, cache results |
| Connector API changes | Medium | Version API clients, test against latest |
| Large schema introspection slow | Medium | Paginate queries, run async |
| RLS policy complexity | High | Provide templates, test thoroughly |
| Migration rollback complexity | High | Require rollback plan for breaking changes |

---

## Rollout Strategy

### Phase 1: Internal Dogfooding (M1 completion)

- Deploy to internal Supabase project
- Run introspection scans
- Apply remediation patches
- Collect feedback on usability

### Phase 2: Pilot Projects (M2-M3)

- Onboard 2-3 pilot projects
- Run governance checks
- Validate connector integrations
- Iterate based on feedback

### Phase 3: General Availability (M4 completion)

- Public documentation release
- Template repo publishing
- Enterprise README generation live
- Support channels active

---

## Success Metrics

### M1 Success

- [ ] Introspection scans 10+ Supabase projects
- [ ] Identifies >1000 security issues
- [ ] Auto-generates remediation plans
- [ ] Applies 100+ patches successfully

### M2 Success

- [ ] 50+ repos use spec bundle enforcement
- [ ] Deterministic diagrams adopted (10+ repos)
- [ ] Enterprise README reflects current state
- [ ] Doc sync reduces drift to <5%

### M3 Success

- [ ] 3 connectors operational (n8n, Superset, Odoo)
- [ ] Contract tests pass >95% rate
- [ ] Event delivery >99.9% reliability
- [ ] Connector health dashboard live

### M4 Success

- [ ] Platform console has 10+ active users
- [ ] Remediation applies 500+ patches via UI
- [ ] Jobs/runs viewer tracks 1000+ executions
- [ ] Connector status dashboard used daily

---

**Version History:**

* v1.0.0 (2026-01-27): Initial implementation plan
