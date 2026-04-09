---
name: ship-readiness-gate
description: |
  WHEN: evaluating whether a feature, module, or service is ready to ship to production
  DO NOT USE WHEN: deploying modules (use deploy-odoo-modules-git), running tests (use odoo-test-runner-ops), backing up (use backup-odoo-environment), promoting staging→prod (use promote-staging-to-prod)
license: LGPL-3.0
metadata:
  author: InsightPulse AI
  version: 1.0.0
  plane: operations_automation
---

# SKILL: Ship-Readiness Gate

## Skill Type

Evaluative (Judgment)

## Purpose

Evaluate whether a feature passes all five ship-readiness gates before production deployment.
Produces a go/no-go decision with evidence. Prevents shipping features that are "implemented but not ready."

## Preconditions

1. Feature code is merged to the target branch
2. At least one test run exists for the feature
3. Staging environment is available for runtime validation

## Triggers

- Agent preparing a production deploy
- PR description references "ship-ready" or "release"
- User asks "is this ready to ship?" or "can we deploy this?"

## Rules

1. All five gates must be evaluated — no gate may be skipped
2. Each gate produces PASS, FAIL, or EXCEPTION
3. EXCEPTION requires explicit acceptance with owner name and time bound
4. A single FAIL blocks the ship decision
5. Evidence must be attached, not claimed

## The Five Gates

### 1. Product gate

The feature solves the intended problem.

| Check | Verification |
|-------|-------------|
| Acceptance criteria explicit | Read spec/PRD, confirm criteria exist |
| Behavior matches spec | Compare implementation against spec |
| Edge cases documented | Check for non-goals and boundary docs |
| No unresolved ambiguity | Confirm no open questions that change UX |

### 2. Correctness gate

The feature works under expected and failure cases.

| Check | Verification |
|-------|-------------|
| Unit tests pass | `TransactionCase` / pytest green |
| Integration tests pass | Cross-module or cross-service tests green |
| Browser/API tests pass | `HttpCase` / curl / API suite green |
| Negative fixtures correct | Error paths, invalid input, boundaries tested |
| No blocker defects | Issue tracker has no open blockers |

### 3. Runtime gate

The feature works in the real deployed environment.

| Check | Verification |
|-------|-------------|
| Staging deploy succeeded | Commit SHA deployed, revision healthy |
| Smoke tests pass | Health probe 200, login page responds |
| Dependencies reachable | DB, external APIs, Azure services respond |
| Auth works end-to-end | Entra / Odoo session through real edge |
| Ingress works | Azure Front Door → ACA → service responds |

### 4. Operational safety gate

The feature can fail safely.

| Check | Verification |
|-------|-------------|
| Rollback defined | Previous image/commit/DB backup identified |
| Deployment reversible | Can stop or revert without data loss |
| Observability wired | Logs, metrics, traces configured |
| Alerts configured | Failure scenarios have diagnostic coverage |
| Blast radius understood | Impact scope documented |

### 5. Evidence gate

The release decision is justified with artifacts.

| Check | Verification |
|-------|-------------|
| Test evidence attached | Log files with pass/fail counts |
| Smoke evidence attached | curl output, health probe response |
| Exceptions recorded | Each EXCEPTION has owner + time bound |
| Go/no-go owner explicit | Named person or role |

## Outputs

- `ship-readiness.md` — filled checklist with gate statuses
- `final-decision.json` — `{ "decision": "SHIP|NO-SHIP", "gates": {...}, "owner": "...", "date": "..." }`
- Evidence saved to: `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`

## Delegates To

| Concern | Skill |
|---------|-------|
| Running tests | `odoo-test-runner-ops` |
| Deploying to staging | `deploy-odoo-modules-git` |
| Promoting to prod | `promote-staging-to-prod` |
| Backup before deploy | `backup-odoo-environment` |
| Infrastructure validation | `azure-deployment-ops` |

## References

- [FEATURE_SHIP_READINESS_CHECKLIST.md](../../../docs/release/FEATURE_SHIP_READINESS_CHECKLIST.md)
- [feature-ship-readiness-gates.yaml](../../../ssot/release/feature-ship-readiness-gates.yaml)
