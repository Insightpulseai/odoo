---
name: azure-ai-evals-governance
description: Validate AI evaluation pipelines, content safety filters, monitoring integration, and responsible AI stage gates for Foundry agents
version: "1.0"
compatibility:
  hosts: [github-copilot, claude-code, codex-cli, cursor, gemini-cli]
tags: [evals, foundry, governance, observability]
---

# azure-ai-evals-governance

**Impact tier**: P1 -- Operational Readiness

## Purpose

Validate AI evaluation pipelines, monitoring integration, content safety
configuration, and governance controls for Foundry agents. Ensures evaluation
datasets exist for each production agent, cloud evals run on a cadence, Azure
Monitor is wired to capture token usage and latency, content filtering is
applied at the correct severity thresholds, and the responsible AI gates in
`ssot/agent-platform/stage_gates.yaml` are enforced before any agent is
promoted to production.

## When to Use

- Before promoting any agent from staging to production.
- After adding a new agent tool or capability (regression eval required).
- When content safety incidents occur (review and tighten filter thresholds).
- During quarterly responsible AI governance reviews.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `scripts/foundry/run_cloud_eval.py` | Eval dataset path, metric names, pass/fail threshold, output format |
| `scripts/foundry/run_retrieval_eval.py` | Retrieval-specific metrics, groundedness threshold |
| `scripts/foundry/enable_monitoring.py` | Azure Monitor workspace ID, diagnostic settings, metric names |
| `agents/evals/` | Eval datasets per agent (`.jsonl` files with query/expected pairs) |
| `ssot/agent-platform/stage_gates.yaml` | Gate definitions: which eval metrics block promotion |
| `ssot/agent-platform/agent_maturity_model.yaml` | Maturity levels per agent, current level, target level |

## Microsoft Learn MCP Usage

Run at least these queries:

1. `microsoft_docs_search("Azure AI Foundry evaluation SDK cloud eval pipeline Python")`
   -- retrieves `EvaluatorClient`, dataset format, built-in evaluators, async eval jobs.
2. `microsoft_docs_search("Azure Monitor AI Foundry agent metrics logging diagnostic")`
   -- retrieves diagnostic settings for Foundry, Log Analytics workspace integration.
3. `microsoft_docs_search("Azure AI content safety filter severity threshold Foundry")`
   -- retrieves content filter categories, severity levels (safe/low/medium/high), API config.
4. `microsoft_docs_search("Azure AI responsible AI dashboard evaluation governance")`
   -- retrieves RAI dashboard components, fairness metrics, model card generation.

Optional:

5. `microsoft_code_sample_search("azure foundry evaluation python cloud eval", language="python")`
6. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/evaluations")`

## Workflow

1. **Inspect repo** -- Read `ssot/agent-platform/stage_gates.yaml` and
   `agents/evals/`. Record: which agents have eval datasets, the current
   gate thresholds, and whether `run_cloud_eval.py` references a valid
   Foundry project endpoint. Check `enable_monitoring.py` for the Log
   Analytics workspace ID.
2. **Query MCP** -- Run queries 1-4. Capture: the eval job API shape
   (`client.evaluations.create`), recommended minimum dataset size (>= 50
   items for statistical significance), content filter severity thresholds
   for enterprise ERP (hate: low, violence: low, self-harm: low, sexual: low),
   and diagnostic setting category names.
3. **Compare** -- Identify: (a) agents in production without an eval dataset
   in `agents/evals/`, (b) stage gates with no numeric threshold (incomplete
   gate), (c) content filter not configured or set to `none` severity,
   (d) monitoring not wired (Log Analytics workspace missing from diagnostic
   settings), (e) eval run output not committed to evidence directory.
4. **Patch** -- Create missing eval datasets (minimum 50 query/answer pairs
   per agent). Update `stage_gates.yaml` with numeric thresholds. Wire
   `enable_monitoring.py` to the Log Analytics workspace ID from SSOT.
   Run `run_cloud_eval.py` for each production agent and commit results
   to `docs/evidence/`.
5. **Verify** -- All production agents have `agents/evals/<agent-name>.jsonl`
   with >= 50 items. `stage_gates.yaml` has numeric thresholds for
   groundedness, relevance, and safety. Cloud eval run PASS/FAIL output
   is in evidence directory. Monitoring diagnostic settings include
   `AllLogs` category.

## Outputs

| File | Change |
|------|--------|
| `agents/evals/<agent-name>.jsonl` | Eval dataset: 50+ query/expected/context triples |
| `ssot/agent-platform/stage_gates.yaml` | Numeric thresholds for all gate metrics |
| `ssot/agent-platform/agent_maturity_model.yaml` | Updated maturity level after eval |
| `scripts/foundry/enable_monitoring.py` | Log Analytics workspace ID, diagnostic categories |
| `scripts/foundry/run_cloud_eval.py` | Confirmed dataset path, threshold, output path |
| `docs/evidence/<stamp>/azure-ai-evals-governance/` | Eval scores, content filter config, monitor setup |

## Completion Criteria

- [ ] Every agent with `environment: production` in `ssot/ai/agents.yaml` has an eval dataset in `agents/evals/` with >= 50 items.
- [ ] `stage_gates.yaml` defines numeric thresholds (not empty) for groundedness, relevance, and safety for each production gate.
- [ ] Content safety filter is set to `low` or stricter severity for all four categories (hate, violence, self-harm, sexual).
- [ ] `enable_monitoring.py` references the correct Log Analytics workspace ID and includes `AllLogs` diagnostic category.
- [ ] At least one cloud eval run result is committed to `docs/evidence/` with PASS/FAIL per metric.
- [ ] Agent maturity model reflects the current eval-validated level in `agent_maturity_model.yaml`.
- [ ] Evidence directory contains eval output and MCP excerpts.
