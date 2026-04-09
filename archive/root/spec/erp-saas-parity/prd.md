# PRD: ERP SaaS Parity (OCA + IPAI Module Gap Closure)

## Problem Statement

Insightpulseai runs Odoo 18 CE with 383 installed modules. The target is
≥80% feature parity with Odoo Enterprise Edition using only CE + OCA + custom
`ipai_*` bridges. A deterministic gap analysis identified 9 OCA modules and
7 IPAI bridges at P0 priority that are **not yet installed** in production.

## Parity Definition

**Parity** means a user performing a standard ERP workflow (finance close,
expense submission, helpdesk ticket, document management, multi-level approval,
project planning) can complete it end-to-end without needing an EE licence.

## Acceptance Criteria

1. All 9 P0 OCA modules listed in `ssot/odoo/parity/oca_p0_allowlist.yaml`
   are installed and functional in production (`state = 'installed'`).
2. Each P0 OCA module has a smoke test (manual or scripted) confirming core
   EE-replacement functionality works.
3. IPAI bridge modules are scaffolded with `__manifest__.py` and registered
   in `ssot/odoo/parity/erp_saas.yaml` (functional implementation is separate
   spec bundles per module).
4. Parity score per domain meets or exceeds the `parity_targets` in the
   SSOT YAML.
5. No data loss or downtime during installation (rollback plan executed if
   any module install fails).

## P0 OCA Modules (Must Install)

| # | Module | OCA Repo | Replaces EE |
|---|--------|----------|-------------|
| 1 | `account_reconcile_oca` | OCA/account-reconcile | `account_accountant` |
| 2 | `account_asset_management` | OCA/account-financial-tools | `account_asset` |
| 3 | `dms` | OCA/dms | `documents` |
| 4 | `dms_field` | OCA/dms | `documents` |
| 5 | `helpdesk_mgmt` | OCA/helpdesk | `helpdesk` |
| 6 | `helpdesk_mgmt_sla` | OCA/helpdesk | `helpdesk` |
| 7 | `base_tier_validation` | OCA/server-ux | `approvals` |
| 8 | `base_tier_validation_formula` | OCA/server-ux | `approvals` |
| 9 | `project_task_dependency` | OCA/project | `project` (task deps) |

## P0 IPAI Bridges (Planned — Separate Implementation)

| Module | Replaces EE |
|--------|-------------|
| `ipai_approvals` | `approvals` (workflow engine) |
| `ipai_slack_connector` | `mail_enterprise` / Discuss |
| `ipai_ocr_paddleocr` | EE IAP OCR |
| `ipai_hr_payroll_ph` | `hr_payroll` (PH locale) |
| `ipai_bir_1601c` | PH BIR compliance |
| `ipai_bir_2316` | PH BIR compliance |
| `ipai_bir_alphalist` | PH BIR compliance |

## Out of Scope

- Odoo Enterprise licence procurement
- odoo.com IAP service subscriptions
- EE-only non-module SaaS features (Odoo.sh hosting, Odoo Studio full)
- Mobile app (tracked separately in `spec/mobile-app/`)
- Electronic signatures (accepted gap — deferred to P2)
- P1/P2 module installation (separate future PR)

## SSOT Reference

- `ssot/odoo/parity/erp_saas.yaml` — authoritative gap report
- `ssot/odoo/parity/oca_p0_allowlist.yaml` — P0 OCA module allowlist
- `ssot/odoo/oca_repos.yaml` — OCA repo registry with vendoring status
