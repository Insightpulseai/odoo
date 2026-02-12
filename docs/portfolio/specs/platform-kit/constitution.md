# Platform Kit Constitution

**Version:** 1.0.0
**Last Updated:** 2026-01-27

---

## Purpose

This document defines the **non-negotiable rules** for Platform Kit: architectural principles, security boundaries, governance requirements, and quality gates that cannot be violated.

---

## 1) Core Principles (Immutable)

### 1.1 Security-First Defaults

**Rule:** Every Supabase project scaffolded by Platform Kit MUST have:

* RLS enabled on all client-accessible tables (unless explicitly documented as public-read)
* Tenant-aware RLS policies by default (multi-tenant baseline)
* Fixed `search_path` on all SECURITY DEFINER functions
* Extensions installed in dedicated schema (NOT `public`)
* Secrets stored server-side only (Supabase Vault, CI secrets, never in repo)

**Non-Negotiable:** No exceptions without Security/Compliance Owner approval + audit trail.

### 1.2 Introspection-First Architecture

**Rule:** Platform Kit's source of truth is **observed state**, not declared state.

* All platform decisions (parity, compliance, remediation) MUST be based on introspection outputs
* Introspection runs nightly + on-demand (CI gates)
* Inventories persist to control plane (`ops` schema) with full lineage

**Non-Negotiable:** No "assume it's correct" patterns. Verify, then trust.

### 1.3 Governance-as-Code

**Rule:** All governance policies MUST be:

* Defined in version-controlled code (GitHub workflows, Supabase migrations, spec bundles)
* Enforced via CI gates (not manual review)
* Auditable with full change history

**Non-Negotiable:** No "please follow this guide" governance. Automate or don't claim it.

### 1.4 Idempotency Everywhere

**Rule:** All operations (migrations, job runs, remediation patches, scaffolding) MUST be idempotent.

* Re-running the same operation produces the same result
* No accidental duplicate data, duplicate policies, or conflicting state
* All database functions use `IF NOT EXISTS`, `ON CONFLICT`, or explicit checks

**Non-Negotiable:** No "run this once" scripts in production workflows.

### 1.5 Deterministic Builds

**Rule:** All artifacts (diagrams, docs, binaries) MUST be reproducible.

* Diagram exports (drawio → PNG) are CI-checked for drift
* Doc tri-sync (claude.md/gemini.md/codex.md) enforced via CI
* Build outputs match expected hash or schema

**Non-Negotiable:** No "works on my machine" artifacts in version control.

---

## 2) Security Boundaries (Enforced)

### 2.1 RLS Policy Requirements

**Minimum Standards:**

* All tables in `public` schema MUST have RLS enabled (unless explicitly exempted)
* "Allow-all" policies (WHERE true, WITH CHECK true) are PROHIBITED without justification
* Tenant isolation MUST be enforced at database level (no application-layer-only checks)
* Service role bypasses RLS; use ONLY for server-side operations

**Enforcement:**
* CI gate: `check_rls_coverage.sql` fails if tables lack RLS
* Nightly scan flags policy drift

### 2.2 Function Security Requirements

**Minimum Standards:**

* All SECURITY DEFINER functions MUST have fixed `search_path` (e.g., `SET search_path = pg_catalog, public`)
* SECURITY DEFINER usage MUST be justified in comments (why invoker privilege insufficient?)
* Function owners MUST be restricted (no broad grants to `anon`/`authenticated` for sensitive functions)

**Enforcement:**
* CI gate: `check_function_security.sql` fails if mutable search_path detected
* Pre-deployment validation blocks unsafe functions

### 2.3 Extension Placement

**Rule:** Extensions MUST NOT be installed in `public` schema.

* Use dedicated `extensions` schema
* Migration template moves existing extensions: `ALTER EXTENSION <name> SET SCHEMA extensions`

**Enforcement:**
* CI gate: `check_extensions_schema.sql` fails if extensions in `public`
* Autofix migration available

### 2.4 Secrets Handling

**Rule:** No secrets in repository, ever.

* Use Supabase Vault for application secrets
* Use GitHub Secrets for CI/CD secrets
* Use Edge Function environment variables (never hardcoded)
* Secret scanning enabled in all repos (GitHub Advanced Security)

**Enforcement:**
* Pre-commit hooks block common secret patterns
* CI secret scanning gate (fails on detection)

---

## 3) Governance Requirements (Mandatory)

### 3.1 Spec Bundle Enforcement

**Rule:** All significant projects MUST have a spec bundle:

* `spec/<project>/constitution.md` - Non-negotiables
* `spec/<project>/prd.md` - Requirements
* `spec/<project>/plan.md` - Implementation plan
* `spec/<project>/tasks.md` - Task checklist with status

**Enforcement:**
* CI gate: `spec-kit-enforce.yml` fails if bundle incomplete
* Pull requests without spec updates rejected for major features

### 3.2 Deterministic Diagrams

**Rule:** All architectural diagrams MUST be version-controlled and reproducible.

* Source: `.drawio` files in `docs/architecture/`
* Output: `.png` files auto-generated via CI
* Drift detection: CI fails if manual PNG edits detected

**Enforcement:**
* CI workflow: `diagrams-ci.yml` regenerates PNGs and diffs
* Manual PNG commits rejected

### 3.3 Doc Tri-Sync

**Rule:** Project documentation MUST be synchronized across three AI contexts:

* `CLAUDE.md` - Claude Code instructions
* `GEMINI.md` - Gemini Code Assist instructions
* `CODEX.md` - OpenAI Codex instructions

**Enforcement:**
* CI gate: `doc-sync-check.yml` fails if content drift >10%
* Automated sync suggestions generated on detected drift

### 3.4 Enterprise README

**Rule:** GitHub Enterprise organizations MUST have an auto-generated README.

* Source: Introspection inventories (`ops.inventory_objects`)
* Template: `templates/enterprise-readme.md.j2`
* Output: Root `README.md` in org profile repo

**Enforcement:**
* Nightly workflow: `generate-enterprise-readme.yml`
* Manual edits overwritten (edit template, not output)

---

## 4) Quality Gates (CI Enforcement)

### 4.1 Required CI Checks

All repos MUST pass these checks before merge:

1. **Lint:** Code style (ESLint, Prettier, Black, isort)
2. **Type Check:** Static analysis (TypeScript, mypy)
3. **Tests:** Unit tests (>80% coverage), integration tests
4. **Security:** Secret scanning, dependency review, SBOM validation
5. **Schema:** Migration validation, RLS coverage, function security
6. **Parity:** Contract tests (API/data/event/behavior)
7. **Spec:** Spec bundle completeness

**Enforcement:**
* Branch protection: Require all checks green
* No bypass without CODEOWNERS approval

### 4.2 Nightly Introspection

Platform Kit runs nightly introspection scans:

* Supabase projects (schemas, RLS, functions, extensions)
* GitHub repos (structure, workflows, compliance)
* Connectors (health, capabilities, latency)

**Outputs:**
* Updated `ops.inventory_objects`
* Compliance report (severity-ranked issues)
* Remediation plan (auto-generated patches)

**Enforcement:**
* Scan failures trigger alerts (n8n workflow, Mattermost notification)
* Critical issues block next deployment

### 4.3 Parity Gate

Contract tests run on every PR + nightly:

* API contracts (OpenAPI schema validation)
* Data contracts (schema invariants, RLS invariants)
* Event contracts (outbox/inbox delivery, idempotency)
* Behavior contracts (user journey end-to-end tests)

**Enforcement:**
* PR merge blocked if parity score drops >5%
* Regression alerts sent to responsible team

---

## 5) Data Integrity Rules

### 5.1 Tenancy Invariants

**Rule:** All multi-tenant data MUST enforce tenant isolation.

* Every tenant-scoped table MUST have `tenant_id` column (UUID, NOT NULL)
* RLS policies MUST filter by `auth.jwt() ->> 'tenant_id'`
* No cross-tenant queries without explicit service role + audit log

**Enforcement:**
* Schema linter: Flags missing `tenant_id` on new tables
* Contract tests: Verify cross-tenant access blocked

### 5.2 Foreign Key Constraints

**Rule:** All relationships MUST have explicit FK constraints.

* No "soft FKs" (unconstrained integer references)
* Cascades explicitly defined (CASCADE, SET NULL, RESTRICT)
* FK indexes created automatically (performance requirement)

**Enforcement:**
* Schema linter: Flags missing FKs on reference columns
* Migration template includes FK + index by default

### 5.3 Audit Trails

**Rule:** All state changes MUST be auditable.

* Use `created_at`, `updated_at` timestamps (UTC, NOT NULL)
* Critical tables use `created_by`, `updated_by` (user_id, NOT NULL)
* Destructive operations logged to `ops.audit_log`

**Enforcement:**
* Schema template includes audit columns by default
* Trigger-based audit logging for critical tables

---

## 6) Performance Requirements

### 6.1 Query Performance

**Rule:** All production queries MUST meet performance budgets.

* P95 latency <500ms for API endpoints
* P99 latency <2s for API endpoints
* Slow query threshold: >1s execution time

**Enforcement:**
* Nightly scan flags slow queries (from Supabase logs)
* Index recommendations auto-generated
* Remediation plan includes EXPLAIN ANALYZE results

### 6.2 Index Coverage

**Rule:** All frequently queried columns MUST have indexes.

* Foreign keys always indexed
* RLS policy columns indexed
* Common WHERE/ORDER BY columns indexed

**Enforcement:**
* Schema linter: Suggests missing indexes
* Introspection: Flags table scans in slow queries

---

## 7) Observability Requirements

### 7.1 Structured Logging

**Rule:** All platform components MUST use structured logs.

* Format: JSON with standard fields (`{ts, level, component, message, metadata}`)
* Levels: DEBUG, INFO, WARN, ERROR, FATAL
* Context: Include `project_id`, `scan_id`, `run_id` where applicable

**Enforcement:**
* Logging library required (pino for Node.js, structlog for Python)
* CI linter flags unstructured console.log/print statements

### 7.2 Metrics

**Rule:** All platform operations MUST emit metrics.

* Standard metrics: duration, count, error_rate, parity_score
* Connector metrics: latency, success_rate, queue_depth
* Custom metrics via `ops.metrics` table

**Enforcement:**
* Metrics client library required
* Dashboard templates provided (Vercel Observability, Supabase logs)

---

## 8) Versioning & Compatibility

### 8.1 Semantic Versioning

**Rule:** All Platform Kit modules use semantic versioning.

* Format: `MAJOR.MINOR.PATCH`
* Breaking changes: MAJOR bump
* New features (backward-compatible): MINOR bump
* Bug fixes: PATCH bump

**Enforcement:**
* CI validates changelog matches version bump
* Automated release notes generated

### 8.2 Migration Compatibility

**Rule:** All Supabase migrations MUST be forward-compatible.

* No DROP without data migration
* No ALTER without DEFAULT or backfill
* Rollback plan required for breaking changes

**Enforcement:**
* Migration linter: Flags unsafe operations
* Deployment gates: Require manual approval for breaking changes

---

## 9) Connector Contracts

### 9.1 Standard Interface

**Rule:** All connectors MUST implement standard interface:

* `inventory()` - Return list of objects
* `health()` - Return status + latency
* `capabilities()` - Return supported features
* `contract_tests()` - Run self-validation

**Enforcement:**
* Connector SDK enforces interface via TypeScript types
* CI gate: Connector tests fail if interface incomplete

### 9.2 Event Contracts

**Rule:** All connectors MUST support event patterns:

* Outbox pattern for reliable delivery
* Idempotency keys for deduplication
* Retry with exponential backoff
* Dead letter queue for failures

**Enforcement:**
* Connector SDK provides event utilities
* Contract tests verify idempotency + retry behavior

---

## 10) Exceptions & Waivers

### 10.1 Exception Process

**Rule:** Exceptions to this constitution require explicit approval.

**Process:**
1. Document exception in `docs/exceptions/<date>-<summary>.md`
2. Include: Rationale, risk assessment, mitigation plan, expiry date
3. Approval: Security/Compliance Owner + Platform Architect
4. Audit trail: Logged to `ops.exceptions` table

**Enforcement:**
* No undocumented exceptions allowed
* Expired exceptions auto-flagged for review

### 10.2 Temporary Waivers

**Rule:** Temporary waivers allowed for prototypes only.

* Duration: Max 30 days
* Scope: Non-production environments only
* Expiry: Must remediate or request extension

**Enforcement:**
* Waiver recorded in `ops.waivers` table
* Automated expiry reminders (7 days before)

---

## 11) Compliance & Audit

### 11.1 Audit Trail Requirements

**Rule:** All remediation changes MUST be auditable.

* Who: User/service account
* What: SQL patch, function patch, workflow patch
* When: Timestamp (UTC)
* Why: Linked to compliance issue or remediation plan

**Enforcement:**
* `ops.remediation_plans` table with full lineage
* Immutable audit log (no DELETE privilege)

### 11.2 Annual Review

**Rule:** Constitution reviewed annually + on major milestones.

* Review date: Q1 each year
* Participants: Platform Architect, Security Owner, Engineering Lead
* Output: Updated constitution + migration plan for new requirements

**Enforcement:**
* Calendar reminder + GitHub issue auto-created

---

## 12) Enforcement Summary

| Rule Category | Enforcement Mechanism | Consequence |
|---------------|----------------------|-------------|
| Security | CI gates, nightly scans | PR blocked, deployment blocked |
| Governance | Spec bundle check, doc sync | PR rejected |
| Quality | Required CI checks | Merge blocked |
| Data Integrity | Schema linter, contract tests | Migration rejected |
| Performance | Slow query scan, index linter | Remediation plan auto-created |
| Observability | Logging/metrics library required | CI lint failure |
| Connectors | Interface validation, contract tests | Connector registration blocked |

---

## 13) Amendment Process

**Rule:** Constitution changes require:

1. Proposal: Document in `spec/platform-kit/constitution-amendments/<date>-<summary>.md`
2. Review: Platform Architect + Security Owner approval
3. Implementation: Update constitution.md + enforcement mechanisms
4. Migration: Provide remediation plan for existing projects
5. Communication: Announce via changelog + team notification

**Enforcement:**
* Constitution changes are versioned
* Migration deadline: 90 days from approval

---

**Version History:**

* v1.0.0 (2026-01-27): Initial constitution
