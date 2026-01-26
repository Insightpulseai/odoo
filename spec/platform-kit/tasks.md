# Platform Kit Tasks

**Version:** 1.0.0
**Last Updated:** 2026-01-27
**Status:** In Progress

---

## Task Status Legend

- ✅ **Done**: Completed and verified
- 🔄 **In Progress**: Currently being worked on
- ⏳ **Backlog**: Not yet started
- 🚧 **Blocked**: Waiting on dependency or external factor
- ❌ **Cancelled**: No longer required

---

## M0: Foundation ✅

### Phase 0.1: Parity Agent Scaffolding ✅
- [x] **M0.1.1**: Create spec bundle structure
  - Status: ✅ Done
  - Files: `spec/platform-kit/{constitution,prd,plan,tasks}.md`
  - Acceptance: All 4 files present, valid markdown

- [x] **M0.1.2**: Create capability schema
  - Status: ✅ Done
  - Files: `kb/parity/capability_schema.json`
  - Acceptance: JSON validates, includes domain/capabilities/contracts structure

- [x] **M0.1.3**: Create parity matrix schema
  - Status: ✅ Done
  - Files: `kb/parity/parity_matrix_schema.json`
  - Acceptance: Supports scoring logic, evidence tracking

### Phase 0.2: Harness Runner ✅
- [x] **M0.2.1**: Create harness runner scaffold
  - Status: ✅ Done
  - Files: `harness/runners/parity_runner.py`
  - Acceptance: Executes capability checks, outputs results

- [x] **M0.2.2**: Create schema validator
  - Status: ✅ Done
  - Files: `scripts/validate_parity_schema.py`
  - Acceptance: Validates JSON against schema, reports errors

### Phase 0.3: CI Gates ✅
- [x] **M0.3.1**: Create parity gate workflow
  - Status: ✅ Done
  - Files: `.github/workflows/parity-gate.yml`
  - Acceptance: Runs on PR, blocks merge if parity score drops >5%

- [x] **M0.3.2**: Create schema validator workflow
  - Status: ✅ Done
  - Files: `.github/workflows/schema-validator.yml`
  - Acceptance: Validates all JSON schemas in `kb/parity/`

---

## M1: Supabase Platform Kit (8 weeks)

### Phase 1.1: Control Plane Schema (Week 1-2)

- [ ] **M1.1.1**: Create ops schema migration
  - Status: ⏳ Backlog
  - Assignee: Backend Engineer
  - Dependencies: None
  - Files: `supabase/migrations/20260127_ops_schema.sql`
  - Acceptance Criteria:
    - [ ] Migration applies cleanly to fresh Supabase project
    - [ ] All tables have RLS enabled
    - [ ] Foreign key constraints validated
    - [ ] Indexes created on frequently queried columns

- [ ] **M1.1.2**: Create RLS policies for ops schema
  - Status: ⏳ Backlog
  - Assignee: Backend Engineer
  - Dependencies: M1.1.1
  - Files: `supabase/migrations/20260127_ops_rls.sql`
  - Acceptance Criteria:
    - [ ] Service role can read/write all tables
    - [ ] Authenticated users can read own project data only
    - [ ] Anon role has no access

- [ ] **M1.1.3**: Seed parity definitions
  - Status: ⏳ Backlog
  - Assignee: Platform Architect
  - Dependencies: M1.1.1
  - Files: `supabase/seed/ops_parity_baseline.sql`
  - Acceptance Criteria:
    - [ ] Seed data includes all 7 core capabilities
    - [ ] Each capability has required_contracts defined
    - [ ] Severity scores assigned (1-5)

### Phase 1.2: Introspection Runner (Week 3-4)

- [ ] **M1.2.1**: Create introspection-runner Edge Function
  - Status: ⏳ Backlog
  - Assignee: Backend Engineer
  - Dependencies: M1.1.1
  - Files: `supabase/functions/introspection-runner/index.ts`
  - Acceptance Criteria:
    - [ ] Accepts `{ project_id, source }` payload
    - [ ] Supabase source queries pg_catalog correctly
    - [ ] GitHub source uses GitHub API with pagination
    - [ ] Connector source calls `inventory()` method
    - [ ] Inserts results to `ops.inventory_objects`
    - [ ] Returns scan_id on success

- [ ] **M1.2.2**: Create security checks module
  - Status: ⏳ Backlog
  - Assignee: Security Engineer
  - Dependencies: M1.2.1
  - Files: `supabase/functions/introspection-runner/security_checks.ts`
  - Acceptance Criteria:
    - [ ] Check RLS coverage (flags tables without RLS)
    - [ ] Check function security (flags mutable search_path)
    - [ ] Check extensions schema (flags public schema usage)
    - [ ] Returns array of security issues with severity

- [ ] **M1.2.3**: Test introspection with unsafe schema
  - Status: ⏳ Backlog
  - Assignee: QA Engineer
  - Dependencies: M1.2.2
  - Files: `tests/introspection/unsafe_schema_test.sql`
  - Acceptance Criteria:
    - [ ] Create test schema with known issues
    - [ ] Run introspection-runner
    - [ ] Verify all issues detected correctly
    - [ ] Verify severity scores match expectations

### Phase 1.3: Function Security Hardening (Week 5-6)

- [ ] **M1.3.1**: Create function security audit query
  - Status: ⏳ Backlog
  - Assignee: Security Engineer
  - Dependencies: None
  - Files: `scripts/audit/check_function_security.sql`
  - Acceptance Criteria:
    - [ ] Detects SECURITY DEFINER functions with mutable search_path
    - [ ] Outputs function name, schema, owner, proconfig status
    - [ ] Returns severity score (5=critical, 1=low)

- [ ] **M1.3.2**: Create function hardening migration template
  - Status: ⏳ Backlog
  - Assignee: Backend Engineer
  - Dependencies: M1.3.1
  - Files: `templates/migrations/harden_function.sql`
  - Acceptance Criteria:
    - [ ] Template includes ALTER FUNCTION SET search_path
    - [ ] Template includes COMMENT explaining change
    - [ ] Template preserves function signature

- [ ] **M1.3.3**: Generate autofix migration
  - Status: ⏳ Backlog
  - Assignee: Backend Engineer
  - Dependencies: M1.3.2
  - Files: `supabase/functions/remediation-applier/index.ts`
  - Acceptance Criteria:
    - [ ] Accepts `{ project_id, remediation_plan_id }` payload
    - [ ] Fetches SQL patch from `ops.remediation_plans`
    - [ ] Applies migration via Supabase Management API
    - [ ] Updates plan status to `applied` or `failed`

### Phase 1.4: Extensions Schema Enforcement (Week 7-8)

- [ ] **M1.4.1**: Create extensions audit query
  - Status: ⏳ Backlog
  - Assignee: Backend Engineer
  - Dependencies: None
  - Files: `scripts/audit/check_extensions_schema.sql`
  - Acceptance Criteria:
    - [ ] Detects extensions in public schema
    - [ ] Outputs extension name, current schema
    - [ ] Returns severity score

- [ ] **M1.4.2**: Create extensions migration template
  - Status: ⏳ Backlog
  - Assignee: Backend Engineer
  - Dependencies: M1.4.1
  - Files: `templates/migrations/move_extensions.sql`
  - Acceptance Criteria:
    - [ ] Template creates extensions schema if missing
    - [ ] Template includes ALTER EXTENSION SET SCHEMA
    - [ ] Template handles dependencies (e.g., pg_stat_statements)

- [ ] **M1.4.3**: Test extensions migration
  - Status: ⏳ Backlog
  - Assignee: QA Engineer
  - Dependencies: M1.4.2
  - Files: `tests/migrations/extensions_test.sql`
  - Acceptance Criteria:
    - [ ] Create test project with pgcrypto in public
    - [ ] Apply migration
    - [ ] Verify pgcrypto moved to extensions schema
    - [ ] Verify existing functions still work

---

## M2: Org Kit + Enterprise Kit (6 weeks)

### Phase 2.1: Repo Templates (Week 1-2)

- [ ] **M2.1.1**: Create app repo template
  - Status: ⏳ Backlog
  - Assignee: Platform Engineer
  - Dependencies: None
  - Files: `packages/governance/templates/app-repo/`
  - Acceptance Criteria:
    - [ ] Includes spec bundle placeholder
    - [ ] Includes CI workflow (lint, test, build)
    - [ ] Includes CODEOWNERS file
    - [ ] Includes dependabot.yml

- [ ] **M2.1.2**: Create service repo template
  - Status: ⏳ Backlog
  - Assignee: Platform Engineer
  - Dependencies: None
  - Files: `packages/governance/templates/service-repo/`
  - Acceptance Criteria:
    - [ ] Includes Dockerfile
    - [ ] Includes CI workflow (lint, test, build, deploy)
    - [ ] Includes health check endpoint template

- [ ] **M2.1.3**: Create lib repo template
  - Status: ⏳ Backlog
  - Assignee: Platform Engineer
  - Dependencies: None
  - Files: `packages/governance/templates/lib-repo/`
  - Acceptance Criteria:
    - [ ] Includes package.json with exports
    - [ ] Includes CI workflow (lint, test, publish)
    - [ ] Includes API documentation template

### Phase 2.2: Spec Bundle Enforcement (Week 3-4)

- [ ] **M2.2.1**: Create spec-kit-enforce workflow
  - Status: ⏳ Backlog
  - Assignee: DevOps Engineer
  - Dependencies: None
  - Files: `.github/workflows/spec-kit-enforce.yml`
  - Acceptance Criteria:
    - [ ] Runs on PR to main
    - [ ] Checks for spec/ directory
    - [ ] Validates constitution.md, prd.md, plan.md, tasks.md exist
    - [ ] Fails if spec bundle incomplete

- [ ] **M2.2.2**: Create spec bundle validator script
  - Status: ⏳ Backlog
  - Assignee: Platform Engineer
  - Dependencies: M2.2.1
  - Files: `scripts/validate_spec_bundle.py`
  - Acceptance Criteria:
    - [ ] Parses all 4 spec files
    - [ ] Checks for required sections
    - [ ] Validates markdown syntax
    - [ ] Returns exit code 0 (valid) or 1 (invalid)

### Phase 2.3: Deterministic Diagrams (Week 5-6)

- [ ] **M2.3.1**: Create diagrams-ci workflow
  - Status: ⏳ Backlog
  - Assignee: DevOps Engineer
  - Dependencies: None
  - Files: `.github/workflows/diagrams-ci.yml`
  - Acceptance Criteria:
    - [ ] Runs on PR touching .drawio files
    - [ ] Exports all .drawio to .png via draw.io CLI
    - [ ] Compares exported PNG with committed PNG
    - [ ] Fails if manual PNG edits detected

- [ ] **M2.3.2**: Create doc-sync-check workflow
  - Status: ⏳ Backlog
  - Assignee: DevOps Engineer
  - Dependencies: None
  - Files: `.github/workflows/doc-sync-check.yml`
  - Acceptance Criteria:
    - [ ] Runs on PR touching CLAUDE.md, GEMINI.md, CODEX.md
    - [ ] Computes content similarity (Levenshtein distance)
    - [ ] Fails if drift >10%
    - [ ] Suggests sync commands

---

## M3: Connector Kit (8 weeks)

### Phase 3.1: Connector Interface SDK (Week 1-2)

- [ ] **M3.1.1**: Create @platform-kit/connector-sdk package
  - Status: ⏳ Backlog
  - Assignee: Backend Engineer
  - Dependencies: None
  - Files: `packages/connector-sdk/src/index.ts`
  - Acceptance Criteria:
    - [ ] Exports ConnectorBase abstract class
    - [ ] Defines inventory(), health(), capabilities(), contract_tests() interface
    - [ ] Includes TypeScript types
    - [ ] Includes JSDoc documentation

- [ ] **M3.1.2**: Create connector test harness
  - Status: ⏳ Backlog
  - Assignee: QA Engineer
  - Dependencies: M3.1.1
  - Files: `packages/connector-sdk/src/test_harness.ts`
  - Acceptance Criteria:
    - [ ] Runs contract_tests() for any connector
    - [ ] Validates interface compliance
    - [ ] Reports pass/fail with evidence

### Phase 3.2: n8n Connector (Week 3-4)

- [ ] **M3.2.1**: Implement n8n connector
  - Status: ⏳ Backlog
  - Assignee: Integration Engineer
  - Dependencies: M3.1.1
  - Files: `supabase/functions/connector-n8n/index.ts`
  - Acceptance Criteria:
    - [ ] Implements ConnectorBase interface
    - [ ] inventory() returns list of workflows
    - [ ] health() pings n8n API
    - [ ] capabilities() returns supported features
    - [ ] contract_tests() validates idempotency

- [ ] **M3.2.2**: Test n8n connector end-to-end
  - Status: ⏳ Backlog
  - Assignee: QA Engineer
  - Dependencies: M3.2.1
  - Files: `tests/connectors/n8n_test.ts`
  - Acceptance Criteria:
    - [ ] Deploy connector to test Supabase project
    - [ ] Call inventory() and verify workflows returned
    - [ ] Call health() and verify status ok
    - [ ] Run contract_tests() and verify pass

### Phase 3.3: Superset Connector (Week 5-6)

- [ ] **M3.3.1**: Implement Superset connector
  - Status: ⏳ Backlog
  - Assignee: Integration Engineer
  - Dependencies: M3.1.1
  - Files: `supabase/functions/connector-superset/index.ts`
  - Acceptance Criteria:
    - [ ] Implements ConnectorBase interface
    - [ ] inventory() returns list of dashboards/datasets
    - [ ] health() pings Superset API
    - [ ] capabilities() returns supported features
    - [ ] contract_tests() validates data contracts

- [ ] **M3.3.2**: Test Superset connector end-to-end
  - Status: ⏳ Backlog
  - Assignee: QA Engineer
  - Dependencies: M3.3.1
  - Files: `tests/connectors/superset_test.ts`
  - Acceptance Criteria:
    - [ ] Deploy connector to test Supabase project
    - [ ] Call inventory() and verify dashboards returned
    - [ ] Call health() and verify status ok
    - [ ] Run contract_tests() and verify pass

### Phase 3.4: Odoo Connector (Week 7-8)

- [ ] **M3.4.1**: Implement Odoo connector
  - Status: ⏳ Backlog
  - Assignee: Integration Engineer
  - Dependencies: M3.1.1
  - Files: `supabase/functions/connector-odoo/index.ts`
  - Acceptance Criteria:
    - [ ] Implements ConnectorBase interface
    - [ ] inventory() returns list of modules/models
    - [ ] health() pings Odoo XML-RPC
    - [ ] capabilities() returns supported features
    - [ ] contract_tests() validates event contracts

- [ ] **M3.4.2**: Test Odoo connector end-to-end
  - Status: ⏳ Backlog
  - Assignee: QA Engineer
  - Dependencies: M3.4.1
  - Files: `tests/connectors/odoo_test.ts`
  - Acceptance Criteria:
    - [ ] Deploy connector to test Supabase project
    - [ ] Call inventory() and verify modules returned
    - [ ] Call health() and verify status ok
    - [ ] Run contract_tests() and verify pass

---

## M4: UI Platform Console (6 weeks)

### Phase 4.1: Console Scaffold (Week 1-2)

- [ ] **M4.1.1**: Create platform-console app
  - Status: ⏳ Backlog
  - Assignee: Frontend Engineer
  - Dependencies: None
  - Files: `packages/platform-console/`
  - Acceptance Criteria:
    - [ ] Next.js 14 app with App Router
    - [ ] Supabase Auth integration
    - [ ] Tailwind CSS + shadcn/ui
    - [ ] Layout with sidebar navigation

- [ ] **M4.1.2**: Create inventory browser page
  - Status: ⏳ Backlog
  - Assignee: Frontend Engineer
  - Dependencies: M4.1.1, M1.1.1
  - Files: `packages/platform-console/app/inventory/page.tsx`
  - Acceptance Criteria:
    - [ ] Displays projects list
    - [ ] Drill-down to project → schemas → tables → functions
    - [ ] Real-time updates via Supabase subscriptions
    - [ ] Search and filter

### Phase 4.2: Parity Dashboard (Week 3-4)

- [ ] **M4.2.1**: Create parity matrix page
  - Status: ⏳ Backlog
  - Assignee: Frontend Engineer
  - Dependencies: M4.1.1, M1.1.1
  - Files: `packages/platform-console/app/parity/page.tsx`
  - Acceptance Criteria:
    - [ ] Displays capability matrix (pass/fail/partial)
    - [ ] Color-coded by severity
    - [ ] Click to view evidence
    - [ ] Trend chart (historical parity scores)

- [ ] **M4.2.2**: Create remediation plan page
  - Status: ⏳ Backlog
  - Assignee: Frontend Engineer
  - Dependencies: M4.2.1, M1.3.3
  - Files: `packages/platform-console/app/remediation/page.tsx`
  - Acceptance Criteria:
    - [ ] Lists recommended patches grouped by severity
    - [ ] Preview SQL patch
    - [ ] One-click apply (calls remediation-applier)
    - [ ] Shows apply status (pending/applied/failed)

### Phase 4.3: Jobs Dashboard (Week 5-6)

- [ ] **M4.3.1**: Create jobs list page
  - Status: ⏳ Backlog
  - Assignee: Frontend Engineer
  - Dependencies: M4.1.1
  - Files: `packages/platform-console/app/jobs/page.tsx`
  - Acceptance Criteria:
    - [ ] Lists all jobs from `ops.job_queue`
    - [ ] Filter by status (pending/running/completed/failed)
    - [ ] Real-time status updates
    - [ ] Retry failed jobs

- [ ] **M4.3.2**: Create job detail page
  - Status: ⏳ Backlog
  - Assignee: Frontend Engineer
  - Dependencies: M4.3.1
  - Files: `packages/platform-console/app/jobs/[id]/page.tsx`
  - Acceptance Criteria:
    - [ ] Displays job payload
    - [ ] Displays run history (all attempts)
    - [ ] Displays artifacts with download links
    - [ ] Shows logs (stdout/stderr)

---

## Cross-Cutting Tasks

### Testing

- [ ] **T1**: Achieve >80% unit test coverage
  - Status: ⏳ Backlog
  - Assignee: QA Team
  - Dependencies: All implementation tasks
  - Acceptance Criteria:
    - [ ] packages/connector-sdk: >80%
    - [ ] supabase/functions/*: >80%
    - [ ] packages/platform-console: >80%

- [ ] **T2**: Create integration test suite
  - Status: ⏳ Backlog
  - Assignee: QA Engineer
  - Dependencies: M1, M2, M3, M4
  - Files: `tests/integration/`
  - Acceptance Criteria:
    - [ ] End-to-end test: introspection → parity check → remediation
    - [ ] End-to-end test: connector discovery → contract tests
    - [ ] All tests green in CI

### Security

- [ ] **S1**: Security review of all migrations
  - Status: ⏳ Backlog
  - Assignee: Security Team
  - Dependencies: All migration tasks
  - Acceptance Criteria:
    - [ ] All migrations reviewed for SQL injection
    - [ ] All RLS policies reviewed for bypass vulnerabilities
    - [ ] All Edge Functions reviewed for secret exposure

- [ ] **S2**: Enable branch protection rules
  - Status: ⏳ Backlog
  - Assignee: DevOps Engineer
  - Dependencies: M2.2.1
  - Acceptance Criteria:
    - [ ] Require spec-kit-enforce check
    - [ ] Require test coverage check
    - [ ] Require security scan check
    - [ ] Require 1 approval from CODEOWNERS

### Documentation

- [ ] **D1**: Create developer quickstart guide
  - Status: ⏳ Backlog
  - Assignee: Technical Writer
  - Dependencies: M1, M2
  - Files: `docs/quickstart.md`
  - Acceptance Criteria:
    - [ ] Covers project scaffolding
    - [ ] Covers introspection setup
    - [ ] Covers connector integration
    - [ ] Includes troubleshooting section

- [ ] **D2**: Create operator runbook
  - Status: ⏳ Backlog
  - Assignee: Technical Writer
  - Dependencies: M4
  - Files: `docs/runbook.md`
  - Acceptance Criteria:
    - [ ] Covers nightly introspection job
    - [ ] Covers remediation plan workflow
    - [ ] Covers incident response (parity drop)
    - [ ] Includes SLO definitions

### Observability

- [ ] **O1**: Instrument all Edge Functions
  - Status: ⏳ Backlog
  - Assignee: DevOps Engineer
  - Dependencies: M1, M3
  - Acceptance Criteria:
    - [ ] All functions emit structured logs (JSON)
    - [ ] All functions emit metrics (duration, count, error_rate)
    - [ ] Logs/metrics sent to external sink (optional)

- [ ] **O2**: Create monitoring dashboards
  - Status: ⏳ Backlog
  - Assignee: DevOps Engineer
  - Dependencies: O1
  - Files: `infra/dashboards/`
  - Acceptance Criteria:
    - [ ] Dashboard: Introspection job health
    - [ ] Dashboard: Parity score trends
    - [ ] Dashboard: Connector health
    - [ ] Alerts: Parity drop >5%, job failures >10%, connector downtime >5min

---

## Rollout Tasks

### Phase 1: Internal Dogfooding (M1 Complete)

- [ ] **R1.1**: Deploy to internal Supabase project
  - Status: ⏳ Backlog
  - Assignee: DevOps Engineer
  - Dependencies: M1
  - Acceptance Criteria:
    - [ ] Migrations applied
    - [ ] Edge Functions deployed
    - [ ] Introspection runs nightly
    - [ ] Reports accessible via console

- [ ] **R1.2**: Onboard 3 internal projects
  - Status: ⏳ Backlog
  - Assignee: Platform Team
  - Dependencies: R1.1
  - Acceptance Criteria:
    - [ ] Run introspection on each project
    - [ ] Generate remediation plans
    - [ ] Apply at least 1 autofix migration
    - [ ] Document feedback and pain points

### Phase 2: Pilot Projects (M2-M3 Complete)

- [ ] **R2.1**: Onboard 10 pilot projects
  - Status: ⏳ Backlog
  - Assignee: Platform Team
  - Dependencies: M2, M3
  - Acceptance Criteria:
    - [ ] Mix of apps, services, libs
    - [ ] Include at least 2 connectors (n8n, Superset, or Odoo)
    - [ ] Spec bundles created for all pilots
    - [ ] CI gates enabled

- [ ] **R2.2**: Collect pilot feedback
  - Status: ⏳ Backlog
  - Assignee: Product Manager
  - Dependencies: R2.1
  - Acceptance Criteria:
    - [ ] Survey all pilot teams
    - [ ] Document top 5 feature requests
    - [ ] Document top 5 pain points
    - [ ] Prioritize backlog for M4

### Phase 3: General Availability (M4 Complete)

- [ ] **R3.1**: Publish public documentation
  - Status: ⏳ Backlog
  - Assignee: Technical Writer
  - Dependencies: D1, D2
  - Acceptance Criteria:
    - [ ] Docs hosted at docs.platform-kit.dev
    - [ ] Includes API reference
    - [ ] Includes connector catalog
    - [ ] Includes video tutorials

- [ ] **R3.2**: Announce GA launch
  - Status: ⏳ Backlog
  - Assignee: Product Manager
  - Dependencies: R3.1
  - Acceptance Criteria:
    - [ ] Blog post published
    - [ ] Social media announcement
    - [ ] Community Discord channel created
    - [ ] Support process documented

---

## Success Metrics Tasks

- [ ] **M1**: Track new project scaffolding time
  - Status: ⏳ Backlog
  - Target: <10 minutes from template to first introspection run
  - Measurement: Time user from `create-platform-kit-project` to green CI

- [ ] **M2**: Track security issue detection rate
  - Status: ⏳ Backlog
  - Target: >95% of known security patterns detected
  - Measurement: Test against unsafe schema with known issues

- [ ] **M3**: Track parity score coverage
  - Status: ⏳ Backlog
  - Target: >90% of projects achieve parity score >80%
  - Measurement: Query `ops.parity_results` for projects with score >80

- [ ] **M4**: Track governance adoption rate
  - Status: ⏳ Backlog
  - Target: 100% of repos have spec bundles after onboarding
  - Measurement: CI check pass rate for spec-kit-enforce

- [ ] **M5**: Track Enterprise README accuracy
  - Status: ⏳ Backlog
  - Target: <5% manual edits required after auto-generation
  - Measurement: Survey org admins on README accuracy

- [ ] **M6**: Track connector contract compliance
  - Status: ⏳ Backlog
  - Target: 100% of connectors pass contract_tests()
  - Measurement: Nightly contract test runs, all green

---

## Blocked Tasks (External Dependencies)

- [ ] **B1**: Pulser SDK integration
  - Status: 🚧 Blocked
  - Blocker: Pulser SDK not yet published to npm
  - Dependencies: External team
  - Workaround: Stub out SDK interface for now

- [ ] **B2**: Supabase Management API rate limits
  - Status: 🚧 Blocked
  - Blocker: Current rate limits too low for bulk introspection
  - Dependencies: Supabase team
  - Workaround: Implement exponential backoff + retry

---

## Notes

**Task ID Format**: `M{milestone}.{phase}.{task}` (e.g., M1.2.1 = Milestone 1, Phase 2, Task 1)

**Assignee Roles**:
- Platform Architect: High-level design, capability definitions
- Backend Engineer: Migrations, Edge Functions, connectors
- Frontend Engineer: Console UI, dashboards
- Security Engineer: RLS policies, function hardening, audits
- QA Engineer: Test coverage, contract tests, end-to-end tests
- DevOps Engineer: CI workflows, deployment, monitoring
- Integration Engineer: Connector implementations
- Technical Writer: Documentation, runbooks

**Priority Order**:
1. M1 (Supabase Platform Kit) - Foundation, highest value
2. M2 (Org Kit) - Governance baseline
3. M3 (Connector Kit) - Integration breadth
4. M4 (UI Console) - User experience polish

**Dependencies**:
- Critical path: M0 → M1 → M2 → M3 → M4
- Parallelizable: M2 and M3 can partially overlap (after M1.1 complete)
- UI Console (M4) can start after M1.1 complete (control plane schema ready)

**Risks**:
- **High**: Supabase API rate limits may slow introspection for large projects
- **Medium**: Connector API changes may break integrations
- **Medium**: RLS policy complexity may require custom patterns per use case
- **Low**: Edge Function cold starts may impact performance (mitigated by keep-warm strategy)

---

**Last Updated:** 2026-01-27
**Total Tasks:** 94
**Completed:** 10 (M0)
**In Progress:** 0
**Backlog:** 82
**Blocked:** 2
