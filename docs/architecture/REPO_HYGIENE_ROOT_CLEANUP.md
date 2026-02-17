# Repo Hygiene — Root Cleanup

**Date**: 2026-02-17
**Branch**: `chore/root-hygiene-loose-files`
**PR**: `chore(repo): root cleanup (move loose files into canonical folders)`

---

## What Changed

Five loose root files were moved to canonical sub-directories, and one `.env` file
with hardcoded credentials was removed from git tracking.

### Files Moved

| File | New Location | Why moved |
|------|-------------|-----------|
| `COLIMA_SETUP_COMPLETE.md` | `docs/guides/COLIMA_SETUP_COMPLETE.md` | Setup doc; not a GitHub-conventional root file |
| `branch_protection.json` | `docs/architecture/branch_protection.json` | Architecture reference; no tooling requires root |
| `devserver.config.json` | `config/devserver.config.json` | Tool config; no root convention |
| `superclaude_bridge.yaml` | `.claude/superclaude_bridge.yaml` | Claude tooling; belongs in `.claude/` |
| `aiux_ship_manifest.yml` | `config/aiux_ship_manifest.yml` | App manifest; not a root convention |

### Security Fix

| File | Action | Why |
|------|--------|-----|
| `.env.production` | Removed from git, added to `.gitignore` | Duplicate of `.env.prod` with hardcoded production credentials |

> ⚠️ **Action required**: The credentials from `.env.production` were already in git history.
> Rotate `POSTGRES_PASSWORD` and `ODOO_ADMIN_PASSWORD` for the production environment.

---

## What Stays at Root (and Why)

These files were evaluated but **intentionally kept** at root due to tooling requirements:

| File | Reason |
|------|--------|
| `oca-aggregate.yml` | `scripts/validate_oca_aggregate_output.py` uses `ROOT_DIR / "oca-aggregate.yml"` |
| `oca.lock.json` | Multiple CI workflows read it from root |
| `addons.manifest.json` | `validate-addons-mounts.yml` and `verify-addons-mounts.sh` expect root |
| `llms.txt` / `llms-full.txt` | `llms.txt` convention + `llms-txt-check.yml` validates at root |
| All `.env.*` | Per repo policy: env files stay at root |
| All Python/Node tooling files | Required at root by their respective tools |

---

## New Guardrail

**CI Workflow**: `.github/workflows/root-allowlist-guard.yml`

- Runs on every PR to `main`
- Fails if any non-allowlisted file is introduced at repo root
- Allowlist is maintained in `.github/workflows/root-allowlist-guard.yml`
- Documentation: `docs/architecture/ROOT_ALLOWLIST.md`

To add a new root file legitimately:
1. Open PR with the file
2. Update `ALLOWED` in `root-allowlist-guard.yml`
3. Update `ROOT_ALLOWLIST.md` with the justification

---

## How to Find Things Now

| Looking for | Find it at |
|------------|-----------|
| Colima setup instructions | `docs/guides/COLIMA_SETUP_COMPLETE.md` |
| GitHub branch protection config | `docs/architecture/branch_protection.json` |
| Dev server configuration | `config/devserver.config.json` |
| SuperClaude bridge config | `.claude/superclaude_bridge.yaml` |
| AIUX ship manifest | `config/aiux_ship_manifest.yml` |
| Root allowlist rules | `docs/architecture/ROOT_ALLOWLIST.md` |
| Move history/manifest | `reports/repo_hygiene/root_file_moves_2026-02-17.json` |
