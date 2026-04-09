# n8n Artifact Audit — 2026-03-21

> Evidence artifact preserving the results of the n8n estate crawl and classification.

## Summary

| Category | Count | Canonical Location |
|----------|-------|--------------------|
| Workflow JSONs (canonical) | 50 | `automations/n8n/workflows/` |
| Workflow JSONs (duplicate) | 50 | `odoo/automations/n8n/workflows/` (non-canonical) |
| Workflow JSONs (archived) | 4 | `archive/dot-github-repo/n8n/workflows/` |
| MCP API bridge | 1 impl | `agents/mcp/n8n-api-bridge/` |
| Odoo module | 1 module | `addons/ipai/ipai_n8n_connector/` |
| SSOT config files | 2 | `ssot/n8n/` (n8n.yaml, n8n_devops_templates.yaml) |
| CI workflows | 3 | `.github/workflows/n8n-*.yml` |
| Claude skills | 2 | `.claude/superclaude/skills/` |
| Infrastructure | 1 | nginx config |
| **Total active artifacts** | **78+** | |

## Domain Distribution (50 canonical workflows)

| Domain | Count |
|--------|-------|
| finance | 12 |
| github_ops | 9 |
| health | 2 |
| control_plane | 3 |
| integration_events | 12 |
| agent_runtime | 12 |

## System Role Distribution

| Role | Count |
|------|-------|
| orchestration | 20 |
| sync | 15 |
| notification | 4 |
| ingestion_edge | 4 |
| healthcheck | 7 |

## Duplication Findings

| Duplicate Cluster | Copy Count | Canonical Root | Decision |
|-------------------|------------|----------------|----------|
| `odoo/automations/n8n/workflows/` | 50 files | `automations/n8n/workflows/` | REMOVE in Pass 3 |
| `odoo/odoo/agents/mcp/n8n-api-bridge/` | Full dir | `agents/mcp/n8n-api-bridge/` | REMOVE in Pass 3 |
| `odoo/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/` | Full dir | `.claude/superclaude/skills/` | REMOVE in Pass 3 |
| `archive/dot-github-repo/n8n/workflows/` | 4 files | N/A (archived) | KEEP frozen |

## Classification Outcome

- n8n confirmed as **required orchestration plane** (Lane 4)
- n8n is **not** the analytical CDC backbone for any lane
- 50 active workflows organized into 6 domains
- 1 deprecated workflow (`vercel-drain-handler.json`)
- MCP bridge and Odoo connector are active integration surfaces
- No workflow claims analytical replication responsibility

## Registry Reconciliation (50 registered vs 55 discovered)

The crawl discovered **55 unique workflow JSON filenames** across all locations.
The registry contains **50 entries**, matching the 50 files in the canonical root (`automations/n8n/workflows/` including subdirectories).

**5 excluded from registry — reason:**

| Workflow | Location | Exclusion Reason |
|----------|----------|-----------------|
| `ai-agent-router.json` | `odoo/odoo/odoo/` (depth 3+ only) | Not present in canonical root; exists only in nested copies. Promote or delete in Pass 3. |
| `bir-rag-pipeline.json` | `odoo/odoo/odoo/` (depth 3+ only) | Not present in canonical root; exists only in nested copies. Promote or delete in Pass 3. |
| `channel-action-workflow.json` | `odoo/odoo/odoo/` (depth 3+ only) | Not present in canonical root; exists only in nested copies. Promote or delete in Pass 3. |
| `teams-bot-adapter.json` | `odoo/odoo/odoo/` (depth 3+ only) | Not present in canonical root; exists only in nested copies. Promote or delete in Pass 3. |
| `ipai_platform__reference_tool__v1.json` | `infra/n8n/workflows/platform/` | Infrastructure reference tool, not an n8n workflow in the standard sense. Separate governance. |

**Pass 3 action:** Evaluate the 4 depth-3-only workflows for promotion to `automations/n8n/workflows/` or deletion. If promoted, add to registry.

## Deferred Cleanup Items

1. Remove `odoo/automations/n8n/workflows/` (50 duplicate JSONs)
2. Remove `odoo/odoo/` nested n8n copies (MCP bridge, skills, prompts)
3. Consolidate `git_operations_hub.json` with `02-git-operations-hub.json` (potential duplicate)
4. Review `odoo/odoo/odoo/infra/ssot/automations/` for n8n SSOT references at depth 3
5. Add CI guard: `.github/workflows/n8n-registry-check.yml` to validate registry against filesystem

## Artifacts Created

| File | Purpose |
|------|---------|
| `ssot/n8n/workflow_registry.yaml` | Canonical workflow SSOT (50 entries) |
| `docs/architecture/N8N_DEDUP_PLAN.md` | Deduplication plan and cleanup schedule |
| `docs/architecture/N8N_RUNTIME_OWNERSHIP.md` | Runtime authority and operating model |
| `docs/evidence/N8N_ARTIFACT_AUDIT.md` | This file — audit evidence |

---

## Canonical Traceability SSOT

The n8n Tier-2 rollup entry was added to `odoo/odoo/odoo/infra/ssot/traceability/artifact_traceability.yaml`.
This is the **only** traceability index in the repo (confirmed via grep — no root-level or alternative copy exists).

**Depth-3 concern:** This file sits at `odoo/odoo/odoo/` (3 levels deep), following the same nesting pattern
as the duplicated n8n workflows. If a future repo-boundary cleanup moves governance SSOT files to the
monorepo root (e.g. `infra/ssot/traceability/`), the n8n entry must move with it.

**Current authority:** `odoo/odoo/odoo/infra/ssot/traceability/artifact_traceability.yaml` remains the
canonical governance traceability SSOT until explicitly relocated.

---

*Audit date: 2026-03-21*
*Auditor: Claude Code (automated crawl + manual classification)*
