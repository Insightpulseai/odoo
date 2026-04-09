# Tasks: ERP SaaS Parity — P0 Module Installation

## Status (2026-03-02)

**Completed**: 5 IPAI modules installed (388 total, was 383)
**Blocked**: 9 OCA modules not ported to 19.0; 6 IPAI modules missing deps; 2 IPAI modules have bugs

## IPAI Module Installation (Completed)

- [x] Install `ipai_ai_platform` (AI Platform HTTP Client)
- [x] Install `ipai_expense_ocr` (OCR expense ingestion)
- [x] Install `ipai_auth_oidc` (OIDC SSO + TOTP MFA)
- [x] Install `ipai_theme_fluent2` (Fluent 2 multi-theme)
- [x] Install `ipai_web_icons_fluent` (Fluent System Icons)
- [x] Restart odoo-prod container
- [x] Verify HTTP 200 at erp.insightpulseai.com
- [x] Verify no broken modules (to upgrade / to install)

## IPAI Modules — Bug Fixes Required

- [ ] Fix `ipai_helpdesk`: Change `base.module_category_services_helpdesk` to CE category in security XML
- [ ] Fix `ipai_finance_close_seed`: Update `04_projects.xml` for Odoo 18 project.project model
- [ ] Fix `ipai_enterprise_bridge`: Remove `fetchmail` from depends (merged into `mail` in Odoo 18)
- [ ] Fix `ipai_zoho_mail`: Remove `fetchmail` from depends (same reason)

## IPAI Modules — Missing Dependencies (Scaffolding Required)

- [ ] Create `ipai_ai_core` module (blocks `ipai_ai_agents_ui` — the "Ask AI" panel)
- [ ] Create `ipai_workspace_core` module (blocks `ipai_finance_workflow`)
- [ ] Create `ipai_bir_tax_compliance` module (blocks `ipai_bir_notifications` + `ipai_hr_payroll_ph`)

## P0 OCA Module Installation (ALL BLOCKED)

All 9 P0 OCA modules are NOT yet ported to Odoo 18.0 in their OCA repos.

### Option A: Wait for OCA community

- [ ] Monitor OCA repos for 19.0 ports (check monthly)
- [ ] Subscribe to OCA/dms, OCA/helpdesk, OCA/server-ux, OCA/project migration issues

### Option B: Port modules using oca-port (recommended)

- [ ] Port `account_reconcile_oca` from 18.0 → 19.0 using `oca-port`
- [ ] Port `account_asset_management` from 18.0 → 19.0
- [ ] Port `dms` + `dms_field` from 18.0 → 19.0
- [ ] Port `base_tier_validation` + `base_tier_validation_formula` from 18.0 → 19.0
- [ ] Port `project_task_dependency` from 18.0 → 19.0
- [ ] Vendor `helpdesk_mgmt` + `helpdesk_mgmt_sla` (check 19.0 availability first)

### Option C: Write IPAI equivalents

- [ ] Evaluate whether `ipai_helpdesk` (after bug fix) covers helpdesk_mgmt needs
- [ ] Evaluate IPAI-native DMS vs waiting for OCA/dms port

## Post-Install Validation

- [x] Total installed module count = 388 (383 + 5)
- [x] No modules in `to upgrade` or `to install` state
- [x] `curl https://erp.insightpulseai.com/web/login` returns HTTP 200
- [x] Update `ssot/odoo/parity/erp_saas.yaml` status fields
- [x] Update `ssot/odoo/parity/oca_p0_allowlist.yaml` with port status

## Evidence

- Install log: `web/docs/evidence/20260302-1930+0800/ipai-p0-install/logs/install_results.txt`

## Verification Script

Re-dump installed modules from production:

```bash
ssh root@178.128.112.214 "docker exec odoo-prod python3 -c '
import psycopg2
conn = psycopg2.connect(
  host=\"private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com\",
  port=25060, dbname=\"odoo_prod\", user=\"doadmin\",
  password=\"<DB_PASSWORD>\", sslmode=\"require\")
cur = conn.cursor()
cur.execute(\"SELECT name, state FROM ir_module_module WHERE state=%s ORDER BY name\", (\"installed\",))
for r in cur.fetchall(): print(r[0] + \": \" + r[1])
print(\"Total: \" + str(cur.rowcount))
conn.close()
'"
```
