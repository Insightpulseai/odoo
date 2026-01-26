# Product Requirements Document (PRD): Platform Kit

**Tagline:** The easiest way to build, govern, and scale platform products on top of Supabase—enterprise-ready by default.

---

## 1) Summary

**Platform Kit** is a composable "platform-in-a-box" toolkit that turns **Supabase + GitHub Enterprise** into a repeatable, governed, introspection-driven platform factory.

It ships as a set of versioned templates, CI policies, Supabase migrations/functions, and a **continuous introspection engine** that:

* inventories repos, schemas, policies, APIs, and workflows
* enforces platform contracts (security/performance/reliability)
* scaffolds "Org Kit" + "Enterprise Kit" governance from code
* enables a Supabase-based "control plane" for multi-project operations

---

## 2) Problem Statement

Teams building platforms on Supabase can ship fast, but platform maturity is typically blocked by:

* inconsistent project scaffolding and security defaults (RLS, roles, auth boundaries)
* fragmented governance across repos and environments (preview/prod drift, policy drift)
* lack of unified introspection across Supabase + GitHub + CI + connectors
* high operational toil to maintain parity across multiple workspaces/projects

**Platform Kit** resolves these issues by making **enterprise-grade defaults** and **continuous introspection** the baseline rather than the exception.

---

## 3) Goals and Non-Goals

### Goals

1. **One-command scaffolding** for platform projects on Supabase (DB, Edge Functions, Auth patterns, UI blocks).
2. **Org/Enterprise governance-as-code** for GitHub Enterprise: policies, controls, CI gates, spec enforcement, secret scanning, branch protections.
3. **Continuous introspection** across:
   * Supabase projects (schemas, RLS, functions, extensions, slow queries, security issues)
   * repos (structure, workflows, maturity scoring, spec compliance)
   * connectors (n8n/MCP/Databricks/Superset/Odoo/ERPNext/Mattermost)
4. **Contract testing** for API/data/event/behavior parity (platform correctness and compatibility).
5. **Platform control plane** on Supabase to manage inventories, status, and compliance.

### Non-Goals (v1)

* A full replacement for GitHub Enterprise UI/admin workflows.
* A monolithic "super-dashboard" replacing Studio; Platform Kit integrates, does not replace.
* A full marketplace or billing engine (future milestone).

---

## 4) Target Users and Personas

1. **Platform Architect (Jake / systems architect)**
   * needs deterministic scaffolding, CI enforcement, introspection, contract guarantees

2. **Platform Engineer**
   * needs repeatable templates, migrations, Edge Functions, connectors, observability

3. **Security/Compliance Owner**
   * needs RLS policy assurance, function hardening, secret scanning, audit trails

4. **Data Engineer**
   * needs Databricks-style workspace patterns, lineage, jobs, eventing, reproducibility

5. **Product/Operations**
   * needs environment health, deployment status, and standard operating controls

---

## 5) Core Concept: "Introspection-First Platforming"

Platform Kit's foundation is **introspection**: continuous discovery + verification that becomes the source of truth for governance and parity.

### Introspection Outputs

* **Inventory graph:** repos, packages, services, Supabase projects, schemas, endpoints, functions, policies
* **Parity map:** capability matrix and expected contracts vs. observed behavior
* **Risk register:** security/performance/compliance issues prioritized and tracked
* **Scaffold recommendations:** what to adopt from upstream, what to standardize, what to remediate
* **Autofix candidates:** safe, idempotent patches (e.g., RLS enablement, search_path hardening)

---

## 6) Product Scope (Modules)

### A) Supabase Platform Kit (SPK)

**Purpose:** Standardize Supabase project scaffolding for platform-grade development.

**Includes:**
* opinionated `supabase/` folder structure (migrations, seed, functions)
* baseline auth + RLS patterns (tenant-aware by default)
* Edge Functions templates: jobs, webhooks, connectors, exec worker
* "ops control plane" schema for introspection + job orchestration
* policy/lint checks for SQL/function security (search_path, SECURITY DEFINER, extensions schema)

### B) UI Platform Kit (UPK)

**Purpose:** Frontend blocks, admin tooling, and platform console UI patterns.

**Includes:**
* vendor strategy for Supabase UI Library blocks (chat, realtime, auth, upload)
* "Platform Console" starter: status, inventory, policies, deployments, incidents
* design tokens SSOT integration (tokens.json approach)
* Databricks-style workspace IA: projects, jobs, catalogs, runs, artifacts

### C) Org Kit (OK)

**Purpose:** Repo and org-level standards for platform development.

**Includes:**
* required spec bundle enforcement (constitution/prd/plan/tasks)
* repo templates (apps/services/libs/connectors)
* CI baselines: lint, tests, security, schema checks, migrations gates
* deterministic diagrams policy (drawio → PNG CI drift fail)
* doc tri-sync (claude.md/gemini.md/codex.md) drift checks

### D) Enterprise Kit (EK)

**Purpose:** GitHub Enterprise governance-as-code.

**Includes:**
* policy packs: branch protection, required checks, CODEOWNERS, signing rules
* security baselines: secret scanning policies, dependency review, SBOM gates
* audit artifacts: enterprise README generation, changelog conventions
* licensing/compliance posture mapping and reporting

### E) Connector Kit (CK)

**Purpose:** Standard connector contracts for systems that anchor your platform.

**Supported Connectors:**
* Odoo / ERPNext
* Superset
* n8n
* Mattermost
* Databricks workspace + jobs
* Supabase (multi-project federation)

**Includes:**
* unified connector interface: `inventory()`, `health()`, `capabilities()`, `contract_tests()`
* event contracts (outbox/inbox), retry policy, idempotency keys
* secrets handling patterns (server-side only)

### F) Parity + Contract Kit (PCK)

**Purpose:** Formalize parity checks: API/data/event/behavior for "platform guarantees."

**Includes:**
* contract test runners (CI + nightly)
* golden datasets and snapshots
* behavioral tests (e.g., "job enqueue must be idempotent")
* parity matrix engine that scores compliance and flags drift

---

## 7) Key User Flows

### 7.1 Create a New Platform Project on Supabase

1. Generate project via template repo
2. Apply baseline migrations + RLS + roles
3. Deploy Edge Functions (jobs, connectors, webhook ingress)
4. Provision UI console starter (platform control plane)
5. Start continuous introspection and compliance reporting

### 7.2 Onboard an Existing Supabase Project into Platform Kit

1. Run introspection crawler
2. Generate compliance report (RLS gaps, function security, extensions placement, slow queries)
3. Apply safe autofix migrations (idempotent)
4. Turn on parity gates in CI

### 7.3 Enterprise Governance

1. Org Kit enforces repo standards
2. Enterprise Kit enforces policies and required checks
3. Enterprise README generated from inventories + controls state

---

## 8) Functional Requirements

### 8.1 Introspection Engine

**Discover:**
* schemas/tables/views/functions/extensions
* RLS enablement + policy summaries
* SECURITY DEFINER usage
* role mutable `search_path` risks
* slow queries (from telemetry source if available)

**Persist:** to control plane tables (see Data Model)

**Generate:**
* compliance issues list with severity
* recommended migrations / patches
* maturity score per project and per repo

### 8.2 Parity Mapping Engine

**Inputs:**
* capability schema (what "should exist")
* observed inventories (what exists)
* contract test outcomes

**Output:**
* parity matrix (pass/fail/partial)
* score weighted by business criticality
* drift alerts (new risk or regression)

### 8.3 Contract Tests

Four categories:

* **API:** OpenAPI / endpoint response contracts, auth rules
* **Data:** schema invariants, RLS invariants, FK constraints, tenancy invariants
* **Event:** outbox/inbox delivery, idempotency, retry/backoff
* **Behavior:** user journeys (e.g., "create job → claim → run → artifact → complete")

### 8.4 Org/Enterprise Governance-as-Code

* Enforce spec bundle presence
* Enforce deterministic diagram pipeline
* Enforce CI required checks
* Enforce security baselines (secret scanning, dependency review)
* Generate **Enterprise README** from current inventories + controls

### 8.5 UI Platform Console

* Inventory browser: projects → schemas → functions → policies → risks
* "Fix plan" views: recommended patches grouped by severity
* Jobs/runs/artifacts viewer (Databricks-style)
* Connector status: last sync, latency, failures, DLQ

---

## 9) Non-Functional Requirements

* **Security-first defaults** (tenant-aware RLS, safe function search_path, least privilege)
* **Idempotency** for migrations and job runners
* **Observability**: logs + metrics + traces (where available)
* **Determinism**: builds and diagram exports reproducible
* **Scalability**: supports many Supabase projects and many repos (federation)

---

## 10) Data Model (Supabase Control Plane)

**Schema:** `ops` (recommended)

### Core tables

* `ops.platform_projects`
  * project_id, name, environment, created_at, updated_at

* `ops.inventory_scans`
  * scan_id, project_id, source (supabase/github/connector), status, started_at, finished_at

* `ops.inventory_objects`
  * scan_id, object_type (table/view/function/policy/extension/repo/workflow), object_key, object_json, risk_flags

* `ops.parity_definitions`
  * capability_id, domain, description, severity, required_contracts_json

* `ops.parity_results`
  * scan_id, capability_id, status, score, evidence_json

* `ops.contract_test_runs`
  * run_id, project_id, suite, status, started_at, finished_at

* `ops.contract_test_results`
  * run_id, test_id, status, evidence_json

* `ops.remediation_plans`
  * plan_id, project_id, severity, sql_patch, function_patch, workflow_patch, status

### Optional (recommended)

* `ops.risk_register`
* `ops.deployments`
* `ops.run_events`
* `ops.artifacts`

---

## 11) Security & Compliance Requirements

1. RLS enabled for any table exposed to client roles (unless explicitly exempted).
2. Eliminate role-mutable `search_path` patterns in functions (harden with fixed search_path).
3. Restrict `SECURITY DEFINER` usage; require justification + codeowners approval.
4. Move unsafe extensions out of `public` schema where possible (policy rule).
5. All secrets are server-side only (Edge Function secrets, CI secrets); never stored in repo.
6. Full audit trail for remediation changes (who/what/when via migrations + run logs).

---

## 12) Observability Requirements

* Standard event schema for logs: `{ts, level, project_id, scan_id/run_id, component, message, metadata}`

* **Metrics:**
  * scan duration, objects discovered, risks found, parity score
  * contract test pass rate, regression count
  * connector latency and error rate

* **Alerting integration points:**
  * Vercel Observability Plus (for UI)
  * Supabase logs + external sink (optional)
  * n8n workflow notifications (optional)

---

## 13) Delivery and Rollout Plan

### Milestone M0 (Complete)

* parity agent MVP scaffolded: spec bundle, schemas, harness runner, CI gates, schema validator

### Milestone M1: Supabase Platform Kit baseline

* ops schema + inventory ingestion
* function security ruleset + autofix migrations
* Edge Functions: scan runner + remediation applier

### Milestone M2: Org Kit + Enterprise Kit

* governance repos templates
* enterprise README generator (from inventory)
* CI enforcement packs

### Milestone M3: Connector Kit

* connector contracts (inventory/health/capabilities/tests)
* n8n + Superset + Odoo integration stubs

### Milestone M4: UI Platform Console

* inventory, risks, parity, runs, artifacts
* Databricks-style workspace IA for platform operations

---

## 14) Success Metrics (Enterprise "Done" Criteria)

**Platform Kit is considered enterprise-ready when:**

1. New platform project can be created with a single scaffold + CI gate pass.
2. Introspection finds and tracks security/performance issues (like RLS gaps, search_path risks).
3. Parity/contract tests run nightly and on PR with meaningful drift detection.
4. Governance-as-code is active for repos (spec enforcement, deterministic diagrams, docs sync).
5. The Enterprise README can be generated from inventories and reflects real controls state.
6. At least one connector (n8n or Superset) meets contract requirements end-to-end.

---

## 15) Repository Structure (Reference)

```text
platform-kit/
  spec/platform-kit/
    constitution.md
    prd.md
    plan.md
    tasks.md

  supabase/
    migrations/
    functions/
      introspection-runner/
      remediation-applier/
      connector-n8n/
      connector-superset/
    seed.sql
    config.toml

  packages/
    platform-console/          # UI app
    platform-sdk/              # TS/JS SDK for connectors + contracts
    contract-tests/            # test suites (api/data/event/behavior)
    governance/                # org+enterprise kit templates and policies

  scripts/
    scan_repos.sh
    scan_supabase.sh
    score_repos.py
    generate_enterprise_readme.ts

  .github/workflows/
    parity-gate.yml
    nightly-introspection.yml
    sync-upstream.yml
    diagrams-ci.yml
    spec-kit-enforce.yml
```

---

## 16) Pulser SDK Requirement

Platform Kit must include installation and integration instructions for the **Pulser SDK** as a first-class dependency (local + CI usage), including:

* standardized agent execution entrypoints
* job/run artifact persistence hooks
* failure classification + retry semantics

(Implementation specifics are defined in the plan/tasks artifacts, but the PRD requires that the SDK is included and used as the orchestration interface.)

---

## 17) Open Questions (Tracked, Not Blocking v1)

* Which connector is first "golden path" (n8n vs Superset) for contract completeness?
* Target deployment runtime for connector executors (Edge Functions vs external workers)?
* How to represent enterprise licensing posture in EK (informational vs enforcement)?

---

**Version:** 1.0.0
**Last Updated:** 2026-01-27
**Status:** Draft
