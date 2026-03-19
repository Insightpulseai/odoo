# Automations Sweep

**Status**: ACTIVE
**Spec**: `spec/ops-automation-sweep/`
**Scripts**: `scripts/automations/`

---

## What Is Scanned

The sweep covers the entire monorepo (excluding `.git/`, `node_modules/`, `__pycache__/`, `.cache/`, `.gemini/`):

| Category | Paths | What's Detected |
|----------|-------|-----------------|
| n8n workflow JSONs | `automations/n8n/**`, `n8n/**`, stray locations | Shape validation, classification, deduplication |
| Script references | `scripts/**/*.sh`, `*.py` | n8n URL refs, API key usage, automation patterns |
| GitHub Actions | `.github/workflows/**/*.yml` | n8n references, orphaned dispatchers |
| MCP configs | `mcp/**/*.yaml`, `.claude/mcp-servers.json` | Server configs, consumer mapping |
| Stale references | All files | Deprecated domains (`.net`), old paths (`odoo-ce`) |

### Workflow Classification

| Class | Meaning |
|-------|---------|
| `canonical` | In `automations/n8n/` — authoritative |
| `stray` | Valid n8n JSON outside canonical path — must be moved |
| `duplicate` | Same SHA256 hash as another file |
| `stale_reference` | Referenced in code but file not found |
| `unreferenced` | Exists but never referenced anywhere |

---

## Required Environment Variables

| Variable | Required For | Source |
|----------|-------------|--------|
| `N8N_BASE_URL` | Deploy (--apply) | `~/.zshrc` or CI secret |
| `N8N_API_KEY` | Deploy (--apply) | `~/.zshrc` or CI secret |
| `GITHUB_TOKEN` | CI artifact upload | Auto-injected in GH Actions |

**Audit-only** (no `--apply`) requires **no secrets**.

---

## How to Run

### Audit Only (safe, no changes)

```bash
python scripts/automations/sweep_repo.py \
  --env stage \
  --out out/automation_sweep \
  --verbose
```

Outputs:
- `out/automation_sweep/inventory.json`
- `out/automation_sweep/report.md`
- `out/automation_sweep/backlog.md`
- `out/automation_sweep/patches/*.diff`

### Apply Mode (deploy canonical workflows)

```bash
# Set env vars first
export N8N_BASE_URL="https://n8n.insightpulseai.com"
export N8N_API_KEY="<token>"

python scripts/automations/sweep_repo.py \
  --env prod \
  --out out/automation_sweep \
  --apply \
  --verbose
```

Also produces:
- `out/automation_sweep/deploy_results.json`

### Deploy Only (without full sweep)

```bash
python scripts/automations/deploy_n8n_all.py \
  --env stage \
  --dry-run

python scripts/automations/deploy_n8n_all.py \
  --env prod \
  --apply
```

---

## Failure Modes

| Error | Cause | Fix |
|-------|-------|-----|
| Exit 1 (audit) | Stale refs or stray workflows found | Review `backlog.md`, move files, fix refs |
| Exit 1 (deploy) | `N8N_BASE_URL`/`N8N_API_KEY` missing | Export env vars before running `--apply` |
| Exit 2 (deploy) | One or more workflow deploys failed | Check `deploy_results.json` for per-workflow errors |
| `SKIP: not a valid n8n workflow shape` | JSON file lacks `name`/`nodes`/`connections` | Fix JSON or remove from `automations/n8n/` |
| `WARN: duplicate name` | Two canonical files with same workflow name | Rename or deduplicate |
| Conflict (stray differs from canonical) | Same name, different content | Manual review — do NOT auto-merge |

---

## CI Integration

GitHub Actions workflow: `.github/workflows/automation-sweep.yml`

Triggered on PRs touching: `automations/**`, `scripts/**`, `infra/**`

- Runs audit-only (no `--apply`)
- Uploads `inventory.json`, `report.md`, `backlog.md` as artifacts
- Exits non-zero if P0 stale references or stray workflows found

---

## Relationship to `n8n-gitops.sh`

`scripts/n8n-gitops.sh` handles GitOps-style sync (watch + push). `deploy_n8n_all.py` handles:
- Batch initial deployment of all canonical workflows
- Diff-based update (skip identical)
- JSON validation before push
- Structured `deploy_results.json` output for CI

Both can coexist. `n8n-gitops.sh` for continuous sync; `deploy_n8n_all.py` for one-shot bulk deploy.

---

## Canonical Locations

| Artifact | Canonical Path |
|----------|---------------|
| Workflow JSONs | `automations/n8n/workflows/` |
| Sweep script | `scripts/automations/sweep_repo.py` |
| Deploy script | `scripts/automations/deploy_n8n_all.py` |
| Spec | `spec/ops-automation-sweep/` |
| Artifacts | `out/automation_sweep/` |
| Architecture doc | `docs/architecture/AUTOMATIONS_SWEEP.md` (this file) |
