# Releases & Changelog

This page summarizes **what is running in production** on https://erp.insightpulseai.com.

Source of truth:

1. `docs/releases/WHAT_DEPLOYED_prod-*.md` – human-readable release notes
2. `docs/releases/WHAT_DEPLOYED_prod-*.json` – machine-readable inventory
3. GitHub Deployments – mapping PR → deployment ID → environment

---

## Release Log (Production)

> Format: newest first. Each entry maps 1:1 to a `WHAT_DEPLOYED_*` file and a GitHub deployment.

| Date (UTC) | Release ID | Key Changes | PRs / Commits | Evidence |
|-----------|------------|------------|---------------|----------|
| 2026-01-12 | `prod-20260112-XXXX` | `feat(ipai_copilot_ui)`, `feat(ipai_theme_custom)`, `feat(ipai_finance_okr)` | #209, #210, #204, #205 | pending |
| 2026-01-09 | `prod-20260109-2248` | docs + tooling only (no Odoo modules or Supabase migrations) | #191, #192 | `docs/releases/WHAT_DEPLOYED.md` |
| 2026-01-09 | `prod-20260109-2219` | Supabase verification tooling | #191 | `docs/releases/WHAT_DEPLOYED_prod-20260109-2219.md` |
| 2026-01-06 | `prod-20260106-1741` | React Fluent UI, IPAI AI Platform spec, DiagramFlow tool | #165 | `docs/releases/WHAT_SHIPPED.md` |
| 2026-01-06 | `prod-20260106-1643` | Prior baseline | - | - |

> **Rule:** if it's not listed here with a `WHAT_DEPLOYED_*` file, it is **not considered deployed** to production.

---

## Recent Commits on Main

Key changes since last documented release:

| Commit | Description | PR |
|--------|-------------|-----|
| `7a9b397` | `feat(theme): align design tokens with Scout dashboard spec` | #210 |
| `e82cd10` | `feat(ipai_copilot_ui): add M365 Copilot-inspired UI module for Odoo 18` | #209 |
| `1552e6e` | `chore(deps): sync lockfile and fix Vercel install command` | #208 |
| `918ad29` | `feat(ipai_theme_custom): add custom theme module with configurable colors` | #204 |
| `d9e9771` | `docs(evidence): add GitHub Projects bulk import verification` | #207 |
| `c9589b3` | `feat(superset): add production embedding infrastructure and agent skills` | #206 |
| `a3417d1` | `feat(ipai_finance_okr): add OKR + PMBOK + WBS governance module` | #205 |
| `37d7708` | Create governance data model for Odoo finance module | #203 |
| `9376237` | Automate ERD creation and export | #202 |
| `2854b84` | `feat(deploy): add deterministic SCSS troubleshooting framework` | #201 |

---

## Per-Release Detail Template

For each release, the corresponding file `docs/releases/WHAT_DEPLOYED_prod-YYYYMMDD-HHMM.md` should follow this structure:

```md
# prod-YYYYMMDD-HHMM – Release Notes

## Summary

- Environment: `production`
- Deployed via: `Deploy to Production #NNN`
- Deployed at: `YYYY-MM-DD HH:MM UTC`
- Commit range: `<old_sha>...<new_sha>`

## Changes

### Features
- `feat(ipai_copilot_ui): add M365 Copilot-inspired UI module for Odoo 18`
- `feat(ipai_theme_custom): add custom theme module with configurable colors`
- `feat(ipai_finance_okr): add OKR + PMBOK + WBS governance module`

### Fixes
- `fix(ipai_grid_view): correct XML data file loading order`
- ...

### Chores / Tooling
- `chore(deps): sync lockfile and fix Vercel install command`
- `docs(evidence): add GitHub Projects bulk import verification`
- ...

## Verification

- Odoo upgrades: `-u all` run with no blocking errors
- Supabase migrations: applied and verified
- Smoke tests: login, main menus, critical flows
- Evidence: see `docs/releases/DEPLOYMENT_PROOFS/prod-YYYYMMDD-HHMM/README.md`
```

---

## Deployment Workflow

Production deployments use the `Deploy to Production` workflow:

1. Pre-flight checks (verify image exists)
2. SSH to production server
3. `git fetch origin main && git checkout main && git pull origin main`
4. `git submodule update --init --recursive`
5. `docker compose pull`
6. `docker compose up -d --force-recreate`
7. Health check: `curl -sf http://localhost:8069/web/health`
8. Create release tag

---

## Related Documentation

- [WHAT_SHIPPED.md](https://github.com/jgtolentino/odoo-ce/blob/main/docs/releases/WHAT_SHIPPED.md) - Detailed release inventory
- [GO_LIVE_MANIFEST.md](https://github.com/jgtolentino/odoo-ce/blob/main/docs/releases/GO_LIVE_MANIFEST.md) - Go-live checklist
- [DEPLOYMENT_PROOFS/](https://github.com/jgtolentino/odoo-ce/tree/main/docs/releases/DEPLOYMENT_PROOFS) - Evidence artifacts
