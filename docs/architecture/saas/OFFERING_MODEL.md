# Offering Artifact Model

> Version: 1.0.0
> Last updated: 2026-03-14

## Purpose

Define the canonical artifact bundle required for every publishable offering, organized by offering and by layer.

> **Note:** This doc is also mirrored in `docs/architecture/OFFERING_ARTIFACT_MODEL.md` (org-level portfolio index).

## Repo Ownership Split

| Artifact class | Canonical repo |
|----------------|---------------|
| Public offering copy, landing pages, CTA text, demo-page content | **`web`** |
| Odoo product/runtime specs, Odoo-facing architecture docs, Odoo runbooks, release evidence | **`odoo`** |
| Foundry agent contracts, prompts, guardrails, eval datasets/results | **`agents`** |
| Entra/Foundry auth policy, deployment topology, landing-zone, monitoring, identity/security docs | **`infra`** |
| Shared analytics / automations / control-plane service specs | **`platform`** |
| Org-level portfolio index only, no SSOT | **`docs`** |

**Simple rule:** User-facing copy → `web`. Odoo runtime truth → `odoo`. AI agent/eval truth → `agents`. Identity/deploy/monitoring → `infra`. Shared services → `platform`.

## Per-Offering Artifact Bundle (Minimum)

Every public offering must maintain this structure:

```
spec/<slug>/
  constitution.md
  prd.md
  plan.md
  tasks.md

docs/architecture/
  <OFFERING>_TARGET_STATE.md
  <OFFERING>_RUNTIME_BOUNDARY.md
  <OFFERING>_PUBLISHABLE_STATE.md

docs/operations/
  <OFFERING>_RUNBOOK.md
  <OFFERING>_INCIDENTS.md
  <OFFERING>_SUPPORT_MODEL.md

docs/evidence/<YYYY-MM-DD>/<slug>/
  release-summary.md
  screenshots/
  logs/
  validation/
  eval-summary.md

evals/<slug>/
  dataset.jsonl
  rubric.md
  thresholds.yaml
  results/
    <build-id>.json
    <build-id>.md
```

## Offerings

| Offering | Slug | Eval Required | Current State |
|----------|------|---------------|---------------|
| Odoo on Cloud | `odoo-on-cloud` | Operational (deploy, restore, health) | Partial artifacts |
| Odoo Copilot | `odoo-copilot` | AI quality + safety + grounding + runtime + action | Internal Prototype |
| Cloud Operations | `cloud-operations` | Operational (deploy, rollback, monitoring) | Partial artifacts |
| Analytics | `analytics` | Data quality (accuracy, freshness, reconciliation) | Partial artifacts |
| Automations | `automations` | Workflow (trigger, idempotency, audit) | Partial artifacts |
| Managed Operations | `managed-operations` | Service (SLA, runbook, reporting) | Not started |

## Layer Model

Each offering's artifacts span 8 layers. Each layer has its own publish gate.

### Layer 1 — Positioning / Packaging

| Artifact | Purpose |
|----------|---------|
| `docs/marketing/<offering>_ONE_PAGER.md` | Single-page value proposition |
| `docs/marketing/<offering>_MESSAGING.md` | Key messages and positioning |
| `docs/marketing/<offering>_LAUNCH_SCOPE.md` | What is included/excluded at launch |

**Gate:** No claims beyond implemented capability. All "live" features evidenced.

### Layer 2 — UX / Surface

| Artifact | Purpose |
|----------|---------|
| `docs/ux/<offering>_SURFACE_MAP.md` | UI entry points and interaction model |
| `docs/ux/<offering>_EMPTY_STATES.md` | Behavior when no data/results exist |
| `docs/ux/<offering>_ERROR_STATES.md` | Failure mode UX and recovery paths |

**Gate:** Empty states handled. Failure states handled. Trust/disclaimer copy correct. Escalation CTA exists.

### Layer 3 — Runtime / Backend

| Artifact | Purpose |
|----------|---------|
| `docs/architecture/<offering>_RUNTIME_BOUNDARY.md` | What runs where, ownership model |
| `docs/architecture/<offering>_AUTH_POLICY.md` | Authentication and authorization model |
| `docs/architecture/<offering>_ENDPOINT_POLICY.md` | API surface and access control |

**Gate:** Runtime surface documented. No forbidden direct client access. Auth path documented. Fallback behavior documented.

### Layer 4 — Data / Grounding

| Artifact | Purpose |
|----------|---------|
| `docs/architecture/RAG_DATA_PREPARATION_AND_GROUNDING_STRATEGY.md` | Grounding architecture |
| `docs/architecture/<offering>_SOURCE_POLICY.md` | Approved data sources |
| `docs/architecture/<offering>_CITATION_POLICY.md` | Citation requirements |

**Gate:** Approved source list exists. Citations required where promised. No fake "live data" claims.

### Layer 5 — Tools / Actions

| Artifact | Purpose |
|----------|---------|
| `docs/architecture/<offering>_TOOL_CONTRACTS.md` | Tool inventory and capabilities |
| `docs/architecture/<offering>_ACTION_GATES.md` | Confirmation and safety controls |

**Gate:** Tool inventory documented. Action confirmation policy documented. Read/write scope documented. Audit path documented.

### Layer 6 — Identity / Security

| Artifact | Purpose |
|----------|---------|
| `docs/architecture/ENTRA_IDENTITY_BASELINE_FOR_COPILOT.md` | Identity posture |
| `docs/architecture/FOUNDRY_ODOO_AUTH_AND_ENDPOINT_POLICY.md` | Auth and endpoint policy |
| `docs/architecture/<offering>_GUARDRAILS.md` | Safety guardrails |

**Gate:** MFA/admin posture documented. Service auth model documented. No browser-side secrets. Guardrail coverage documented.

### Layer 7 — Observability / Ops

| Artifact | Purpose |
|----------|---------|
| `docs/operations/<offering>_RUNBOOK.md` | Operational procedures |
| `docs/operations/<offering>_SLOS.md` | Service level objectives |
| `docs/operations/<offering>_ALERTS.md` | Alerting configuration |

**Gate:** Logs visible. Correlation IDs present. Incident path documented. SLO/SLA defined where needed.

### Layer 8 — Evaluation / Release Evidence

| Artifact | Purpose |
|----------|---------|
| `evals/<slug>/dataset.jsonl` | Test cases |
| `evals/<slug>/rubric.md` | Scoring criteria |
| `evals/<slug>/thresholds.yaml` | Pass/fail thresholds |
| `evals/<slug>/results/<build>.json` | Run results |
| `docs/evidence/<date>/<slug>/eval-summary.md` | Human-readable summary |

**Gate:** Latest eval run exists. Thresholds passed. Evidence stored. Release summary written.

## Publish Decision Matrix

| Level | Requirements |
|-------|-------------|
| **Internal Prototype** | Runtime works. No evaluations yet. No public claims beyond prototype. |
| **Advisory Release** | Quality + safety + grounding evals exist and pass. Advisory-only actions or confirmed drafts only. |
| **Guided Actions Beta** | Tool routing eval exists. Confirmation enforcement proven. Audit ledger proven. Action bypass = zero. All write paths bounded. |
| **GA / Broad Publish** | Evals automated. Observability complete. Durable state complete. Auth hardening complete. Release evidence reproducible. |
