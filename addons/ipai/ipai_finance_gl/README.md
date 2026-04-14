# ipai_finance_gl

> **D365 Finance General Ledger parity overlay.** Wave-01 Epic #523, Issue: General Ledger and Financial Foundation.

## Purpose

Capture the D365 Finance GL parity surface as queryable records inside Odoo, without re-implementing GL behavior. Odoo CE `account` + OCA finance stack provide the runtime; this module documents the D365 → Odoo mapping for the 7 Wave-01 GL Tasks and exposes a parity-matrix UI.

## Scope

- **In scope:**
  - D365 GL concept inventory (chart of accounts, main accounts, fiscal calendar, financial dimensions, accounting structures, journals, periodic processes)
  - Parity records linking each D365 concept → Odoo CE/OCA equivalent
  - Light extensions only where CE+OCA composition leaves a gap
  - Parity-status reporting view
- **Non-goals:**
  - Re-implementing GL behavior (Odoo CE owns it)
  - Replacing OCA finance modules
  - Asset leasing (separate module — `ipai_asset_leasing` candidate)
  - Tax (separate module — `ipai_bir_tax`)
  - Subscription billing (separate module candidate)

## Module type

**overlay** — parity tracking record model + light view extension; no CRUD overrides on `account.*` core models.

## Dependencies

- Odoo CE modules: `base`, `account`, `analytic`
- OCA modules:
  - `account_financial_report` (OCA/account-financial-reporting)
  - `account_journal_lock_date` (OCA/account-financial-tools)
  - `mis_builder` (OCA/mis-builder)
- Other `ipai_*` modules: none (foundational)

## Installation

```bash
./scripts/odoo_install.sh -d odoo_dev -m ipai_finance_gl
```

## User flows

1. **Browse parity matrix:** Finance → Configuration → D365 Parity → GL Parity Map
2. **Add parity record:** Document a new D365 concept and its Odoo equivalent (with status: covered / partial / gap / out-of-scope)
3. **Generate parity report:** Export current parity status (CSV/PDF) for stakeholder reviews
4. **Filter by status:** View all `gap` records to see what still needs Odoo or `ipai_*` work

## Installed components

- **Models:**
  - `ipai.finance.gl.parity` — parity record (D365 concept ↔ Odoo equivalent + status)
  - `ipai.finance.gl.parity.category` — taxonomy (chart-of-accounts, fiscal-calendar, journal, etc.)
- **Views:**
  - GL parity tree/form/search/kanban
  - Top-level menu under Finance → Configuration
- **Security groups:**
  - `group_ipai_finance_gl_user` (read parity records)
  - `group_ipai_finance_gl_manager` (manage parity records)
- **Cron jobs:** none (M2 may add a sync job to refresh from `ssot/benchmarks/parity_matrix.yaml`)

## Upgrade notes

- This is the initial 18.0.1.0.0 release — no upgrade path yet.
- Dependencies on OCA modules require they are installed first (validated by `addons/oca/`).

## Required documentation

- [Module introspection](docs/MODULE_INTROSPECTION.md) — why this module exists
- [Technical guide](docs/TECHNICAL_GUIDE.md) — how it's built

## Owner

- Primary: finance-platform team
- Backup: odoo-platform team
- ADO: Epic #523 D365 Finance Parity
