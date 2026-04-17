# Copilot instructions — IPAI Odoo repo

<!-- Copilot reads this file the same way Claude Code reads CLAUDE.md.
     Keep in sync with CLAUDE.md. Copilot also reads .claude/rules/ automatically. -->

## Stack
- Odoo **18 CE** (not EE, not 19)
- OCA modules: `odoo/OCA/`
- Custom IPAI bridges: `odoo/custom/ipai_*/`
- ACA: `ipai-odoo-dev-web`, `ipai-odoo-dev-cron`, `ipai-odoo-dev-worker`
- PG Flex: `pg-ipai-odoo.postgres.database.azure.com` (SEA)

## Commands
- Tests: `python -m pytest odoo/tests/ -v`
- Lint: `ruff check odoo/custom/`
- Docker: `docker build -t ipai-odoo:dev .`

## Odoo 18 CE rules (non-negotiable)
- Views: `<list>` only — NEVER `<tree>`
- `view_mode="list,form"` — NEVER `view_mode="tree,form"`
- No `self._cr` / `self._uid` / `self._context` → use `self.env.*`
- No `osv.osv` → use `models.Model`
- `search_count()` requires explicit domain

## OCA-first
- Evaluate OCA modules before writing `ipai_*` code
- Order: configure → OCA → minimal `ipai_*` bridge with `_inherit`
- Never modify OCA source directly

## Security
- No `sudo()` without a justifying comment
- No raw SQL string concatenation
- Secrets via Azure Key Vault — never in code or git
