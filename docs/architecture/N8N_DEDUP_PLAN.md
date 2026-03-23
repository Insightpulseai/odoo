# n8n Deduplication Plan

> Canonical root, stale copy locations, and keep/remove/migrate decisions.

## Canonical Roots

| Surface | Canonical Path | Authority |
|---------|---------------|-----------|
| Workflow JSONs | `automations/n8n/workflows/` | SSOT — all workflow edits happen here |
| MCP API bridge | `agents/mcp/n8n-api-bridge/` | SSOT — TypeScript MCP bridge implementation |
| Odoo connector | `addons/ipai/ipai_n8n_connector/` | SSOT — Odoo module for n8n integration |
| SSOT config | `ssot/n8n/` | SSOT — registry, config, devops templates |
| CI workflows | `.github/workflows/n8n-*.yml` | SSOT — deployment and validation pipelines |
| Skills | `.claude/superclaude/skills/claude-ai-n8n-connector/` | SSOT — Claude skill definitions |
| Infrastructure | `infra/nginx/n8n.conf` (if present) | SSOT — reverse proxy config |

## Duplicate Clusters

### Cluster 1: `odoo/automations/n8n/workflows/`

**Status**: NON-CANONICAL duplicate of `automations/n8n/workflows/`

| Finding | Detail |
|---------|--------|
| File count | 50 JSONs (exact mirror of canonical root) |
| Divergence | None detected — byte-identical copies |
| Risk | Edits to nested copy silently diverge from canonical root |
| Decision | **REMOVE** in Pass 3. Until then, mark as non-canonical. |

### Cluster 2: `odoo/odoo/` nested copies

**Status**: NON-CANONICAL — deep nested duplicates from monorepo nesting

| Path | Content | Decision |
|------|---------|----------|
| `odoo/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/` | Skill definitions | **REMOVE** — canonical is root `.claude/` |
| `odoo/odoo/agents/mcp/n8n-api-bridge/` | MCP bridge TypeScript | **REMOVE** — canonical is root `agents/mcp/` |
| `odoo/odoo/.claude/prompts/odoo-n8n-supabase-consolidation.md` | Prompt file | **REMOVE** — canonical is root `.claude/` |

### Cluster 3: `odoo/odoo/odoo/` triple-nested copies

**Status**: NON-CANONICAL — deepest nesting level

| Path | Decision |
|------|----------|
| `odoo/odoo/odoo/infra/ssot/automations/` (if contains n8n refs) | Review — may be intentional SSOT in nested repo |
| Any other n8n references at this depth | **REMOVE** unless explicitly designated |

### Cluster 4: `archive/dot-github-repo/n8n/workflows/`

**Status**: ARCHIVED — legacy copies predating current structure

| File | Decision |
|------|----------|
| `figma-webhook-receiver.json` | **KEEP in archive** — historical reference |
| `github-webhook-router.json` | **KEEP in archive** — historical reference |
| `plane-odoo-sync.json` | **KEEP in archive** — historical reference |
| `plane_odoo_sync.json` | **KEEP in archive** — historical reference |

## Rules

1. `automations/n8n/workflows/` is the **sole canonical root** for workflow JSONs
2. `odoo/automations/n8n/workflows/` is a non-canonical duplicate — do not edit
3. `odoo/odoo/...` nested copies are non-canonical unless explicitly designated in this document
4. `archive/` copies are frozen historical artifacts — never edit, never import from
5. All n8n SSOT files (`ssot/n8n/*.yaml`) reference canonical paths only
6. CI workflows must validate against canonical root, not nested copies

## Cleanup Schedule

| Phase | Action | Target Date |
|-------|--------|-------------|
| Pass 1 (this PR) | Document duplicates, create registry | 2026-03-21 |
| Pass 2 (this PR) | Patch docs, add traceability | 2026-03-21 |
| Pass 3 (next PR) | Remove `odoo/automations/n8n/workflows/` duplicate | TBD |
| Pass 3 (next PR) | Remove `odoo/odoo/` nested n8n copies | TBD |

---

*Created: 2026-03-21*
