# Odoo Copilot — Publishable State

> Version: 1.0.0
> Last updated: 2026-03-14
> Parent: `agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md` (C-30)

## Current Publish State

**Internal Prototype Only**

| Criterion | Status |
|-----------|--------|
| Runtime exists | Yes — Foundry project `data-intel-ph`, agent defined |
| Agent exists | Yes — `chat_completion()` implemented, threads/runs API |
| Evaluations exist | **No — Foundry Evaluations is empty** |
| Quality eval | Not started |
| Safety eval | Not started |
| Grounding eval | Not started |
| Runtime eval | Not started |
| Action eval | Not started |

## Publish Decision

| Level | Allowed | Reason |
|-------|---------|--------|
| Internal Prototype | **Yes** | Runtime works, no public claims |
| Advisory Release | **No** | No evaluation results exist |
| Guided Actions Beta | **No** | No tool routing eval, no action audit proof |
| GA / Broad Publish | **No** | No evals, no observability, no hardened auth |

## What Must Exist Before Advisory Release

1. Quality eval results (relevance, task adherence)
2. Safety eval results (hallucination, refusal, PII)
3. Grounding eval results (citation coverage/accuracy)
4. Runtime eval results (latency, error rate)
5. All thresholds in `evals/odoo-copilot/thresholds.yaml` passing
6. Evidence pack in `docs/evidence/<date>/odoo-copilot/eval-summary.md`
7. MFA enforced for admin users (identity gate)
8. Converged auth methods policy active (identity gate)

## Artifact Inventory

### Present

| Artifact | Path | Status |
|----------|------|--------|
| Runtime contract | **agents** `foundry/ipai-odoo-copilot-azure/runtime-contract.md` | Complete (v1.2.0) |
| Env modes | **agents** `foundry/ipai-odoo-copilot-azure/env-modes.md` | Complete |
| Metadata | **agents** `foundry/ipai-odoo-copilot-azure/metadata.yaml` | Complete |
| Auth policy | **infra** `docs/architecture/FOUNDRY_ODOO_AUTH_AND_ENDPOINT_POLICY.md` | Complete (v1.1.0) |
| Stage policy | **infra** `docs/architecture/COPILOT_RUNTIME_STAGE_POLICY.md` | Complete (v1.1.0) |
| Identity baseline | **infra** `docs/architecture/ENTRA_IDENTITY_BASELINE_FOR_COPILOT.md` | Complete |
| Azure runtime | **odoo** `docs/architecture/ODOO_COPILOT_AZURE_RUNTIME.md` | Complete |
| Publishable state | **odoo** `docs/architecture/ODOO_COPILOT_PUBLISHABLE_STATE.md` | This file |
| Eval thresholds | **agents** `evals/odoo-copilot/thresholds.yaml` | Complete |
| Eval rubric | **agents** `evals/odoo-copilot/rubric.md` | Complete |
| Eval dataset | **agents** `evals/odoo-copilot/dataset.jsonl` | Scaffold (needs real cases) |
| Runbook | **odoo** `docs/operations/ODOO_COPILOT_RUNBOOK.md` | Scaffold |

### Missing (required for Advisory Release)

| Artifact | Path | Blocker |
|----------|------|---------|
| Eval results | **agents** `evals/odoo-copilot/results/<build-id>.json` | No evaluations run yet |
| Eval summary | **odoo** `docs/evidence/<date>/odoo-copilot/eval-summary.md` | Blocked on eval results |
| Instructions doc | **agents** `foundry/ipai-odoo-copilot-azure/instructions.md` | Agent system prompt not formalized |
| Publish policy | **agents** `foundry/ipai-odoo-copilot-azure/publish-policy.md` | Not yet written |
| Target state | **odoo** `docs/architecture/ODOO_COPILOT_TARGET_STATE.md` | Not yet written |
| Current state | **odoo** `docs/architecture/ODOO_COPILOT_CURRENT_STATE.md` | Not yet written |

## Promotion Path

```
Internal Prototype (current)
  │
  ├── Run first eval set against Foundry agent
  ├── Record results in evals/odoo-copilot/results/
  ├── Generate eval-summary.md
  ├── Verify all thresholds pass
  │
  ▼
Advisory Release
  │
  ├── Enable tool contracts (read-only first)
  ├── Run action eval (tool routing, confirmation)
  ├── Prove audit ledger completeness
  │
  ▼
Guided Actions Beta
  │
  ├── Automate eval pipeline
  ├── Complete observability
  ├── Harden auth (managed identity only)
  │
  ▼
GA / Broad Publish
```
