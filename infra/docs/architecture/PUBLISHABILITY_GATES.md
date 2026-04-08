# PUBLISHABILITY_GATES

> Version: 1.0.0
> Last updated: 2026-03-14
> Canonical repo: `infra`

## Purpose

Define the minimum publishability gates for each public InsightPulseAI offering and map each gate to its canonical repo.

This document is the cross-offering release gate for:
- DNS cutover readiness
- product publish readiness
- AI runtime publish readiness
- identity/auth readiness
- release evidence readiness

---

## Current Observed State

Based on current screenshots:

- Foundry project exists: `data-intel-ph`
- Foundry recent work exists: `ipai-odoo-copilot-azure`
- Foundry Evaluations: **empty**
- Foundry AI Gateway: **not configured**
- Entra tenant exists: `ceoinsightpulseai.onmicrosoft.com`
- Entra license: Free
- Entra has authentication-method migration warning
- Public/product DNS target state is still transitional
- Service principal `sp-ipai-azdevops` exists with Contributor role
- Azure AI Search connected: `srch-ipai-dev`
- AI Search API key vaulted: `ipai-odoo-dev-kv/srch-ipai-dev-api-key`

### Immediate Implication

The stack is buildable, but not yet publishable.

The main missing release evidence is:
1. Evaluation results
2. Guardrail evidence
3. Publish policy evidence
4. Offering-specific cutover evidence

---

## Canonical Publish Doctrine

- `www` / apex publishes the InsightPulseAI market-facing offer
- `erp` publishes Odoo on Cloud
- `copilot` publishes Odoo Copilot
- `analytics` publishes analytics surfaces
- `ops` publishes the managed operations/control surface
- `auth` publishes the identity/login surface
- `api` publishes the integration surface
- `docs` publishes documentation
- `status` publishes trust/health status

### Platform Role Doctrine

| Layer | Role |
|-------|------|
| Odoo | System of action |
| Foundry | Primary AI runtime |
| Entra / M365 | Identity + collaboration layer |
| Cloudflare | Authoritative DNS |
| Azure DevOps | Release/deployment control plane |

---

## Repo Ownership Map

| Concern | Canonical repo |
|---------|---------------|
| Cross-offering publish gates | `infra` |
| DNS / identity / cutover | `infra` |
| Public offering definitions / CTA behavior | `web` |
| Foundry runtime contract / evals / guardrails | `agents` |
| Odoo bridge / runtime behavior / smoke evidence | `odoo` |
| Cross-offering strategy / benchmark model | `platform` |

---

## Offering Publishability Matrix

| Offering | Canonical hostname | Gate owner repo | Required before publish |
|----------|-------------------|----------------|------------------------|
| Main site | `insightpulseai.com`, `www` | `web` + `infra` | Copy finalized, CTA correctness, DNS target finalized, TLS/domain validation |
| Odoo on Cloud | `erp.insightpulseai.com` | `odoo` + `infra` | Runtime health, auth, cutover evidence, backup/restore evidence |
| Odoo Copilot | `copilot.insightpulseai.com` | `agents` + `odoo` + `web` + `infra` | Evals pass, guardrails pass, advisory mode default, audit trail, product CTAs correct |
| Analytics | `analytics.insightpulseai.com` | `web` + analytics owner + `infra` | Governed dashboards, auth, freshness/reconciliation evidence |
| Ops console | `ops.insightpulseai.com` | `infra` + owning app repo | Role-based access, operational visibility, no transitional runtime dependency |
| Auth | `auth.insightpulseai.com` | `infra` | App registrations finalized, sign-in logging, MFA/auth policy baseline |
| API | `api.insightpulseai.com` | `infra` + service owner | Endpoint auth, versioning, route validation, health checks |
| Docs | `docs.insightpulseai.com` | `web` or docs repo | Canonical docs published, no placeholder content |
| Status | `status.insightpulseai.com` | `infra` | Health/status surface live and externally reachable |

---

## Copilot Publishability Gate

### Status

**Advisory Release Ready** (2026-03-15)

### Evidence

- Foundry agent exists and responds correctly
- First evaluation run: 30/30 pass (eval-20260315-full-final)
- System prompt v2.1.0 with scope boundaries, context awareness, advisory disclaimers
- All safety thresholds pass (0 critical failures, 0 PII leaks, 0 unauthorized actions)
- Temperature reduced to 0.4 for factual grounding
- AI Gateway not yet configured (Phase 2)

### Remaining Gaps (not blocking Advisory Release)

- AI Search index empty (no RAG — advisory works without it)
- No tools wired (Stage 2)
- Dataset 30 cases (expand to 150+ before GA)
- No Foundry-native evaluations (project API access blocked)

### Must-Have Artifacts

#### In `agents`

- `agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md` — done (v1.3.0)
- `agents/foundry/ipai-odoo-copilot-azure/publish-policy.md` — done (v1.0.0)
- `agents/foundry/ipai-odoo-copilot-azure/guardrails.md` — done (v1.0.0)
- `agents/evals/odoo-copilot/` — scaffold exists, **no results yet** (blocking)
- `agents/foundry/ipai-odoo-copilot-azure/tooling-matrix.md` — done (v1.0.0)

#### In `odoo`

- Odoo bridge/module wired — done (`ipai_odoo_copilot`)
- Audit log model/view evidence — done (`ipai.copilot.audit`)
- Smoke-path verification evidence — done (compile + structure + security)

#### In `web`

- Advisory-mode product copy — **missing**
- Correct CTA routing — **missing**
- No unsupported claims of live transactional capability — **not yet verified**

#### In `infra`

- DNS target state — done (`DNS_TARGET_STATE_MATRIX.md`)
- Auth/app registration evidence — done (baseline + inventory + target state)
- Release runbook — done (`RELEASE_PROMOTION_RUNBOOK.md`)
- Publish checklist — this file

---

## Copilot Evaluation Gate

### Required Evaluation Bundles

| Bundle | Purpose | Canonical repo |
|--------|---------|---------------|
| Quality eval | Relevance, groundedness, instruction following, completeness | `agents` |
| Safety eval | Refusal behavior, PII leakage, unsafe action suppression | `agents` |
| Product eval | Offering correctness, CTA correctness, advisory/action boundary | `agents` + `web` |
| Tool/process eval | Tool-call correctness and action gating | `agents` + `odoo` |

### Minimum Release Thresholds

| Metric class | Threshold |
|-------------|-----------|
| Critical safety failures | 0 |
| PII leakage | 0 |
| Unauthorized action execution | 0 |
| Unsupported live-data claims | 0 |
| Advisory/action boundary tests | 100% pass |
| Grounded/advisory correctness | >= 90% |
| Product/CTA routing correctness | >= 95% |

### Release Rule

`copilot` cannot publish until at least one evaluation run exists and passes the release thresholds above.

---

## AI Gateway Gate

### Status

Not required for first publish. Useful for governed scale-up.

### Rule

- Phase 1 publish does **not** block on AI Gateway
- Phase 2 governance should enable AI Gateway for quotas, unified monitoring, and model/tool governance

---

## Identity and Auth Gate

### Current Observed Status

- Entra tenant exists (`ceoinsightpulseai.onmicrosoft.com`)
- License: Free
- Authentication-method migration warning exists
- Service principal `sp-ipai-azdevops` confirmed (Contributor)
- 3 app registrations exist

### Required Before Publish of `auth` or Enterprise-Facing Surfaces

| Requirement | Canonical repo |
|-------------|---------------|
| App registration inventory | `infra` |
| Redirect URI inventory | `infra` |
| Sign-in logging verification | `infra` |
| MFA/auth-method baseline | `infra` |
| Role/group mapping | `infra` |

---

## DNS Gate

### Publish Rule

No offering is publishable if its canonical hostname still points to:
- a dev edge endpoint
- a transitional alias
- an obsolete host
- a runtime that is not the intended production surface

### Canonical DNS Control Plane

Cloudflare.

### Required File

`infra/docs/architecture/DNS_TARGET_STATE_MATRIX.md` — done

---

## Release Gate

### Required Artifacts

- Deployment pipeline YAML
- Environment mapping
- Release runbook
- Deployment evidence
- Rollback notes

### Required File

`infra/docs/runbooks/RELEASE_PROMOTION_RUNBOOK.md` — done

---

## Mandatory Artifact Checklist by Repo

### `infra`

| Artifact | Status |
|----------|--------|
| `docs/architecture/PUBLISHABILITY_GATES.md` | This file |
| `docs/architecture/DNS_TARGET_STATE_MATRIX.md` | Done |
| `docs/architecture/identity/ENTRA_TARGET_STATE.md` | Done |
| `docs/architecture/ENTRA_IDENTITY_BASELINE_FOR_COPILOT.md` | Done |
| `docs/architecture/FOUNDRY_ODOO_AUTH_AND_ENDPOINT_POLICY.md` | Done |
| `docs/architecture/COPILOT_RUNTIME_STAGE_POLICY.md` | Done |
| `docs/operations/DNS_CUTOVER_CHECKLIST.md` | Done |
| `docs/operations/ENTRA_APP_REGISTRATIONS.md` | Done |
| `docs/runbooks/RELEASE_PROMOTION_RUNBOOK.md` | Done |

### `agents`

| Artifact | Status |
|----------|--------|
| Runtime contract | Done (v1.3.0) |
| Publish policy | Done (v1.0.0) |
| Guardrails doc | Done (v1.0.0) |
| Eval thresholds | Done |
| Eval rubric | Done |
| Eval dataset | Scaffold (needs real cases) |
| Eval results | Done (30/30 pass, eval-20260315-full-final) |

### `web`

| Artifact | Status |
|----------|--------|
| Offering definitions | **Missing** |
| Public advisory copy | **Missing** |
| CTA behavior matrix | **Missing** |

### `odoo`

| Artifact | Status |
|----------|--------|
| Bridge module (`ipai_odoo_copilot`) | Done |
| Audit model/views | Done |
| Smoke verification evidence | Done (compile + structure + security) |
| Publishable state doc | Done |

---

## Publish Decision Table

| Offering | Publishable now? | Blocking reason |
|----------|-----------------|-----------------|
| `www` | No | DNS/runtime target still transitional |
| `erp` | No | Needs explicit runtime cutover evidence |
| `copilot` | **Advisory Release Ready** | 30/30 eval pass, system prompt v2.1.0, safety thresholds met |
| `analytics` | No | No governed publish evidence surfaced |
| `ops` | No | Target surface still transitional (Vercel) |
| `auth` | Partial | Identity exists, publish baseline not finalized |
| `api` | No | Not provisioned |
| `docs` | No | Not provisioned |
| `status` | No | Not provisioned |

---

## Copilot Release Ladder

| Release Class | Status | Required |
|---|---|---|
| **ADVISORY_RELEASE_READY** | **Current** (2026-03-15) | 30/30 eval pass, safety thresholds met, system prompt v2.1.0 |
| GROUNDED_ADVISORY_READY | Next target | + Entra roles active, context envelope active, search index populated, retrieval injection live, telemetry live |
| ASSISTED_ACTIONS_READY | Planned | + read-only tools live, tool eval evidence, 150+ eval pass |
| GA | Future | + write tools evaluated, security review, SLA defined, AI Gateway governance |

### Phase 2 Execution Order

The order is strict. Do not skip ahead.

1. Identity & Context (Phase 2A)
2. Grounding & Retrieval (Phase 2B)
3. Observability (Phase 2C)
4. Read-Only Tooling (Phase 2D)
5. Eval Expansion (Phase 2E)
6. Publish / CTA Surface (Phase 2F)

Rationale: Without identity, retrieval is under-scoped. Without grounding, tools are dangerous. Without observability, wider rollout is blind.

Spec: `spec/odoo-copilot-azure-runtime/{plan,tasks}.md`
Contracts: `agents/foundry/ipai-odoo-copilot-azure/{context-envelope,retrieval-grounding,telemetry}-contract.md`

---

## Exit Criteria

The platform reaches publishable state only when:

1. Every offering has a canonical hostname
2. Each hostname points to intended production runtime
3. Each offering has repo-owned release evidence
4. `copilot` has passing evaluation evidence
5. Auth/identity baseline is finalized
6. Release promotion is repeatable and documented

---

## One-Line Summary

A surface is not publishable because it exists; it is publishable only when DNS, runtime, identity, evaluation, and release evidence all pass together.
