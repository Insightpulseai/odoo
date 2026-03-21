# CLAUDE.md — Odoo CE 19 Project Root

> Thin routing contract. Heavy content lives in `.claude/rules/*.md` (auto-loaded by Claude Code).
> Inherits monorepo-wide policy from parent `CLAUDE.md` files (operating contract, secrets policy,
> deprecated items, cross-repo invariants, agent workflow, common commands).

---

## Quick Reference

| Item | Value |
|------|-------|
| **Odoo** | CE 19.0 (no Enterprise, no odoo.com IAP) |
| **Python** | 3.12+ via pyenv `odoo-19-dev` virtualenv |
| **Database** | PostgreSQL 16 (Azure managed prod, Homebrew local dev) |
| **Hosting** | Azure Container Apps behind Azure Front Door |
| **ERP URL** | `erp.insightpulseai.com` |
| **Local dev** | Native Mac: `vendor/odoo/odoo-bin` + `localhost:5432` |
| **Docker dev** | `.devcontainer/` only. Never run Odoo Docker on host. |
| **Canonical setup** | `odoo19/` directory (`list_db=False`, single DB per env) |
| **Addons path** | `vendor/odoo/addons`, `addons/ipai`, `addons/oca` |

---

## Odoo Rules (Local Overrides)

- **CE only**: No Enterprise modules, no odoo.com IAP calls, no Odoo.sh references.
- **Module philosophy**: Config first, then OCA, then custom `ipai_*` as last resort.
- **OCA isolation**: Never modify OCA source. Use `_inherit` in an `ipai_*` module instead.
- **OCA path**: Always `addons/oca/` (slash). Never `addons-oca/` (hyphen).
- **Database naming**: `odoo_dev` (local), `odoo_staging` (staging), `odoo` (production). No others.
- **Test databases**: `test_<module>` (disposable). Never test against `odoo_dev`/`odoo_staging`/`odoo`.
- **Every Odoo task produces**: (1) module changes, (2) install/update CLI command, (3) health check.
- **No UI clickpaths**: CLI/CI only. Never "Go to Settings -> ...".
- **Mail**: Zoho SMTP only. Mailgun is deprecated.

---

## IPAI Module Naming

Pattern: `ipai_<domain>_<feature>`

| Domain | Example Module | Purpose |
|--------|---------------|---------|
| `finance` | `ipai_finance_ppm` | Finance/accounting features |
| `ai` | `ipai_ai_core` | AI integration core |
| `enterprise` | `ipai_enterprise_bridge` | EE parity bridge |
| `auth` | `ipai_auth_oidc` | Authentication/SSO |
| `connector` | `ipai_connector_vercel` | External service connectors |
| `bir` | `ipai_bir_tax_compliance` | PH BIR tax compliance |
| `hr` | `ipai_hr_payroll_ph` | PH HR/payroll |

Version: `19.0.x.y.z`. License: `LGPL-3`. Full naming rules in `~/.claude/rules/odoo19-coding.md`.

---

## Canonical Setup

The `odoo19/` directory is the recommended Odoo 19 runtime for all agent operations.
Single database per environment, `list_db=False`, version-controlled config, file-based secrets.

- Full setup docs: `odoo19/CANONICAL_SETUP.md`
- Quick reference: `odoo19/QUICK_REFERENCE.md`
- Local dev launch: see `~/.claude/rules/path-contract.md`

---

## Local Path Contract

| Path | Purpose |
|------|---------|
| `vendor/odoo/` | Upstream Odoo 19 root (read-only mirror) |
| `addons/ipai/` | Custom IPAI modules |
| `addons/oca/` | OCA community modules |
| `odoo19/` | Canonical setup (config, scripts, backups) |
| `scripts/odoo/` | Authoritative execution scripts |

Full path contract: `~/.claude/rules/path-contract.md`

---

## Deep Reference

| Topic | Location |
|-------|----------|
| Odoo CE 19 rules, testing, OCA workflow | `.claude/rules/odoo-rules.md` |
| Runtime, Docker, database, hosting | `.claude/rules/odoo-runtime.md` |
| Secrets, GHAS, allowed tools | `.claude/rules/odoo-security.md` |
| Module decision framework, EE parity | `.claude/rules/odoo-module-policy.md` |
| BIR tax compliance (PH) | `.claude/rules/odoo-bir-compliance.md` |
| Odoo addons manifest & governance | `.claude/rules/odoo-addons.md` |
| Odoo CI governance | `.claude/rules/odoo-ci-governance.md` |
| Odoo integrations | `.claude/rules/odoo-integrations.md` |
| Architecture, Docker, MCP servers | `.claude/rules/platform-architecture.md` |
| Security baseline | `.claude/rules/security-baseline.md` |
| SSOT platform rules | `.claude/rules/ssot-platform.md` |
| Repo topology & directory map | `.claude/rules/repo-topology.md` |
| GitHub governance, CI/CD, PR rules | `.claude/rules/github-governance.md` |
| EE parity strategy & tables | `.claude/rules/ee-parity.md` |
| Supabase usage | `.claude/rules/supabase-usage.md` |
| MCP Jobs system | `.claude/rules/mcp-jobs.md` |
| n8n automations | `.claude/rules/automations.md` |
| Spec kit structure | `.claude/rules/spec-kit.md` |
| Odoo 19 coding conventions | `~/.claude/rules/odoo19-coding.md` |
| OCA module governance | `~/.claude/rules/oca-governance.md` |
| Path contract (local/Docker/Azure) | `~/.claude/rules/path-contract.md` |

---

*Last updated: 2026-03-21*
