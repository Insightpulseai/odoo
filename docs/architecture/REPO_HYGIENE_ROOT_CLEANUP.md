# Repo Hygiene — Root Cleanup

**Date**: 2026-02-17
**Branch**: `chore/root-cleanup-2026-02-17`
**PR**: `chore(repo): root cleanup (move loose files into canonical folders)`

---

## What Changed

Six loose root files moved to canonical sub-directories; one `.env` file with
hardcoded credentials removed from git tracking.

### Files Moved

| File | New Location | Why moved |
|------|-------------|-----------|
| `branch_protection.json` | `docs/architecture/branch_protection.json` | Architecture reference; no tooling requires root |
| `devserver.config.json` | `config/devserver.config.json` | Tool config; no root convention |
| `superclaude_bridge.yaml` | `.claude/superclaude_bridge.yaml` | Claude tooling; belongs in `.claude/` |
| `aiux_ship_manifest.yml` | `config/aiux_ship_manifest.yml` | App manifest; not a root convention |
| `figma.config.json` | `figma/figma.config.json` | Figma tooling; belongs in `figma/` |
| `figma-make-dev.yaml` | `figma/figma-make-dev.yaml` | Figma config; belongs in `figma/` |

### Reference Updates

| File | Change |
|------|--------|
| `.github/workflows/aiux-ship-gate.yml` | Path trigger updated: `aiux_ship_manifest.yml` → `config/aiux_ship_manifest.yml` |
| `scripts/design-sync.sh` | Comment updated: `figma.config.json` → `figma/figma.config.json` |

### Security Fix

| File | Action | Why |
|------|--------|-----|
| `.env.production` | Removed from git, added to `.gitignore` | Duplicate of `.env.prod` with hardcoded production credentials |

> ⚠️ **Action required**: The credentials from `.env.production` were already in git history.
> Rotate `POSTGRES_PASSWORD` and `ODOO_ADMIN_PASSWORD` for the production environment.

---

## What Stays at Root (and Why)

| File | Reason |
|------|--------|
| `oca-aggregate.yml` | `scripts/validate_oca_aggregate_output.py` uses `ROOT_DIR / "oca-aggregate.yml"` |
| `oca.lock.json` | Multiple CI workflows read it from root |
| `addons.manifest.json` | `validate-addons-mounts.yml` and `verify-addons-mounts.sh` expect root |
| All `.env.*` | Per repo policy: env files stay at root |
| All Python/Node tooling files | Required at root by their respective tools |

---

## New Guardrail

**CI Workflow**: `.github/workflows/root-allowlist-guard.yml`

- Runs on every PR to `main` and push to `main`
- Fails if any non-allowlisted file is introduced at repo root
- Allowlist: `.github/workflows/root-allowlist-guard.yml` (ALLOWED array)
- Documentation: `docs/architecture/ROOT_ALLOWLIST.md`

To add a new root file legitimately:
1. Open PR with the file
2. Update `ALLOWED` in `root-allowlist-guard.yml`
3. Update `ROOT_ALLOWLIST.md` with the justification
4. Get PR approved

---

## How to Find Things Now

| Looking for | Find it at |
|------------|-----------|
| GitHub branch protection config | `docs/architecture/branch_protection.json` |
| Dev server configuration | `config/devserver.config.json` |
| SuperClaude bridge config | `.claude/superclaude_bridge.yaml` |
| AIUX ship manifest | `config/aiux_ship_manifest.yml` |
| Figma configuration | `figma/figma.config.json` |
| Figma Make dev config | `figma/figma-make-dev.yaml` |
| Root allowlist rules | `docs/architecture/ROOT_ALLOWLIST.md` |
| Move history/manifest | `reports/repo_hygiene/root_file_moves_2026-02-17.json` |
