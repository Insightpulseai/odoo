# AI Evaluation Index

## Objective
Move GenAIOps from L2 Defined toward L3 Managed by operationalizing evaluation evidence.

## Prerequisites
- AI Search index populated (`srch-ipai-dev`) — SC-PH-18
- Content Safety resource deployed on `ipai-copilot-resource`
- Prompt versioning in `ssot/ai/prompts.yaml`

## Agent coverage

| Agent | Maturity | Eval dataset | Eval run | Score | Threshold | Status |
|---|---|---|---|---:|---:|---|
| ap-invoice-agent | L5 | ap-invoice-eval | 4/4 PASS | 1.0 | 0.9 | **Evidence exists** |
| bank-reconciliation-agent | L5 | bank-recon-soak | 5/5 PASS | 1.0 | 0.9 | **Evidence exists** |
| odoo-runtime | L3 | — | — | — | — | Needs eval dataset |
| foundry-agent | L1 | — | — | — | — | P0-blocked |
| ask-agent | L1 | — | — | — | — | Needs eval dataset |
| authoring-agent | L1 | — | — | — | — | Needs eval dataset |
| 6 others | L0 | — | — | — | — | Needs eval dataset |

## Evidence links
- AP invoice eval: `docs/evidence/ap-invoice-eval/`
- AP red-team: `docs/evidence/ap-redteam/`
- Foundry copilot eval: `docs/evidence/foundry-evals/`
- AP soak: `docs/evidence/ap-invoice-soak/`
- Bank recon soak: `docs/evidence/bank-reconciliation-agent-soak/`

## Promotion rule
No production promotion without eval evidence for impacted agents. See `ssot/agent-platform/agent_maturity_model.yaml` for L2+ thresholds (judge score >= 70).
