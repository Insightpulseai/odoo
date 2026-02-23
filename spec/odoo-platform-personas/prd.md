# PRD — Odoo Platform Personas & Expertise Registry

**Spec Bundle**: `spec/odoo-platform-personas/`
**Status**: Draft v1.0
**Date**: 2026-02-24

---

## Problem Statement

The InsightPulseAI Odoo platform is operated by a mix of human contributors and AI agents across development, QA, release management, and infrastructure. Without an explicit, shared role model:

- Release governance becomes dependent on individual judgment rather than defined role contracts
- Evidence requirements are inconsistently applied
- Agents cannot reliably identify which actions are permitted in a given context
- Platform incidents arising from role confusion or skipped controls are unreproducible and hard to prevent

This spec establishes a **canonical persona and expertise registry** as the SSOT for role-based operating contracts across all platform surfaces.

---

## Goals

1. Define four canonical platform personas with explicit outcomes, decision rights, and prohibited actions
2. Establish a 10-domain expertise taxonomy that maps skills and agent capabilities to personas
3. Define G1–G4 gate requirements as shared governance infrastructure
4. Make environment safety controls unambiguous and automatable
5. Provide a stable base for Supabase control-plane integration and CI enforcement

## Non-Goals

- This spec does not define the Supabase schema (covered by `spec/odoo-release-gates-control-plane/`)
- This spec does not define CI workflow YAML
- This spec does not replace OCA parity or Supabase SSOT strategies
- This spec does not define UI administration panels

---

## Functional Requirements

### FR-1: Canonical Persona Definitions

The platform MUST have exactly four canonical personas:

| Persona | Code | Primary Surface |
|---------|------|----------------|
| Odoo Platform Developer | `developer` | Feature branches, dev environment |
| Odoo QA / Release Tester | `qa_tester` | Staging, UAT |
| Odoo Release Manager | `release_manager` | Promotion, go/no-go |
| Odoo Platform SRE / Sys Admin | `sre` | Runtime, infra, monitoring |

Each persona MUST specify:
- Mission statement
- Primary outcomes (3–5)
- Decision rights (explicit list)
- Prohibited actions (explicit list)

### FR-2: Expertise Taxonomy

The platform MUST define exactly 10 canonical expertise domains:

| Domain | Scope |
|--------|-------|
| `odoo.devx.ci_cd` | CI/CD pipeline operation, build debugging |
| `odoo.devx.debugging` | Runtime debugging, trace analysis |
| `odoo.qa.automation` | Automated test authoring and maintenance |
| `odoo.qa.staging_validation` | UAT execution, acceptance criteria validation |
| `odoo.release.orchestration` | Promotion sequencing, scheduling |
| `odoo.release.governance` | Gate enforcement, go/no-go decisions |
| `odoo.sre.backup_recovery` | Backup validation, restore drills |
| `odoo.sre.monitoring_performance` | Alerting, performance profiling |
| `odoo.sre.network_dns_mail` | DNS, mail routing, network ops |
| `odoo.platform.environment_governance` | Environment lifecycle, safety controls |

**Taxonomy Rules**:
- A persona may require multiple expertise domains
- A single expertise domain may be shared across multiple personas
- Agent capabilities MUST map to expertise domains before mapping to persona contracts

### FR-3: G1–G4 Gate Model

The platform MUST define four sequential promotion gates as shared governance:

| Gate | Name | Blocks | Required Evidence |
|------|------|--------|------------------|
| G1 | Build Integrity | Entry to QA validation | Branch build log, required checks status |
| G2 | Validation Readiness | Entry to staging acceptance | Acceptance criteria map, defect register, test evidence |
| G3 | Promotion Readiness | Production promotion | Evidence package, rollback criteria/path, release notes, accountable signoff |
| G4 | Post-Deploy Operational Confirmation | Release closure | Health checks, monitoring baseline, incident fallback timer |

Gates are sequential. A gate MUST NOT be recorded as passed if its required evidence is absent, unless an active approved exception exists.

### FR-4: Environment Safety Controls

Each non-production environment MUST enforce:

| Control | Requirement |
|---------|------------|
| Mail suppression | Outbound email captured or suppressed by default |
| External integration safeguards | Non-prod endpoints use sandbox/blocked modes |
| Least-privilege access | Shell, log, runtime controls are scoped to role |
| Lifecycle/TTL policy | Non-prod environments have defined expiry or explicit keep |
| Data masking | Prod-derived data in staging must be masked per policy |

### FR-5: Evidence Requirements (Minimum per Activity)

| Activity | Minimum Evidence |
|----------|-----------------|
| Build | Build log + check status |
| QA/UAT | Validation summary, pass/fail, defect list |
| Promotion | Approval record, rollback plan, evidence package reference |
| Rollback | Rollback trigger, outcome, evidence captured |
| Incident | Incident timeline, recovery actions, outcome, post-event review |
| Backup/Restore drill | Drill log, restore result, success criteria met |

### FR-6: Exception Handling

Any deviation from gate requirements MUST be recorded with:
1. Exception type
2. Documented exception rationale
3. Accountable approver identity
4. Risk statement
5. Expiry / TTL
6. Impacted gate(s)
7. Post-event review requirement

Exceptions MUST NOT authorize promotions after their expiry.

---

## Persona KPIs and Failure Modes

### A. Odoo Platform Developer

**KPIs**:
- Merge-ready PR rate (passes all G1 checks)
- Time to first passing build on feature branch
- Dependency update cycle time

**Failure Modes**:
- Bypassing CI checks via `--no-verify` or equivalent
- Using non-prod credentials in development work
- Promoting to staging without meeting G1 criteria

---

### B. Odoo QA / Release Tester

**KPIs**:
- Defect detection rate before production promotion
- UAT completion rate per release cycle
- Evidence artifact completeness (G2)

**Failure Modes**:
- Signing off on unverified acceptance criteria
- Classifying defects below their actual severity
- Initiating UAT without G1 passing first

---

### C. Odoo Release Manager

**KPIs**:
- Promotion cycle time (dev → staging → prod)
- Rate of releases with complete G3 evidence packages
- Rollback execution time when triggered

**Failure Modes**:
- Promoting with failed mandatory gates
- Scheduling promotions without confirmed rollback criteria
- Collapsing role independence (e.g., approving own UAT signoff)

---

### D. Odoo Platform SRE / System Administrator

**KPIs**:
- Platform uptime and MTTR (mean time to recovery)
- Backup/restore drill frequency and success rate
- Monitoring alert coverage vs. coverage target

**Failure Modes**:
- Deploying application changes outside release governance
- Accepting unvalidated backups as "good"
- Disabling monitoring/alerting without documented exception

---

## Constraints and Dependencies

| Dependency | Required For |
|------------|-------------|
| `spec/odoo-release-gates-control-plane/` | Supabase persistence of gates and evidence |
| CI/CD pipeline (GitHub Actions) | G1 build integrity automation |
| Staging environment with mail catcher | FR-4 environment safety |
| Agent capability registry | FR-2 expertise domain mapping |

---

## Future Integration Targets

| Target | Scope |
|--------|-------|
| Supabase `ops.*` control plane | Gate outcomes and evidence persistence |
| CI gate enforcement (GitHub Actions) | G1 automated block on failed checks |
| Agent persona registry | Map agent IDs to persona operating contracts |
| Release runbook | Reference this spec for role definitions |

---

## Success Criteria

This PRD is complete when:
- All four persona contracts are authored and internally consistent with this PRD
- G1–G4 gate criteria are implemented in CI for at least G1 and G2
- At least one end-to-end release cycle is traced using this model as SSOT
- Supabase schema for `ops.releases` and `ops.release_gates` is live and accepting events
