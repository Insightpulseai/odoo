# Tasks: ERP SaaS Parity — P0 Module Installation

## P0 OCA Module Installation

### Pre-install

- [ ] Take production DB backup (`pg_dump odoo_prod > odoo_prod_pre_parity.dump`)
- [ ] Vendor OCA/helpdesk submodule (`git submodule add -b 19.0`)
- [ ] Update `addons_path` to include `addons/oca/helpdesk`
- [ ] Verify all OCA repos in `oca_repos.yaml` have `status: ok` or `pinned`

### Finance modules

- [ ] Install `account_reconcile_oca` (OCA/account-reconcile)
- [ ] Verify: bank reconciliation widget accessible in Accounting
- [ ] Install `account_asset_management` (OCA/account-financial-tools)
- [ ] Verify: fixed asset depreciation schedules functional

### Document management

- [ ] Install `dms` (OCA/dms)
- [ ] Install `dms_field` (OCA/dms)
- [ ] Verify: Documents menu visible, directory creation works

### Helpdesk

- [ ] Install `helpdesk_mgmt` (OCA/helpdesk)
- [ ] Install `helpdesk_mgmt_sla` (OCA/helpdesk)
- [ ] Verify: Helpdesk menu visible, ticket creation works, SLA tracking active

### Approval workflows

- [ ] Install `base_tier_validation` (OCA/server-ux)
- [ ] Install `base_tier_validation_formula` (OCA/server-ux)
- [ ] Verify: tier validation available on purchase orders / expenses

### Project planning

- [ ] Install `project_task_dependency` (OCA/project)
- [ ] Verify: task dependency field visible on project tasks

### Post-install validation

- [ ] Total installed module count = 392 (383 + 9)
- [ ] No modules in `to upgrade` or `to install` state
- [ ] `curl https://erp.insightpulseai.com/web/login` returns HTTP 200
- [ ] Update `ssot/odoo/parity/erp_saas.yaml` status fields from `planned` → `installed`
- [ ] Update `ssot/odoo/oca_repos.yaml` helpdesk entry from `pending_vendor` → `ok`

## P0 IPAI Bridge Planning (No Scaffolding — Separate PRs)

- [ ] Create spec bundle `spec/ipai-approvals/` for `ipai_approvals`
- [ ] Create spec bundle `spec/ipai-slack-connector/` for `ipai_slack_connector`
- [ ] Create spec bundle `spec/ipai-ocr-paddleocr/` for `ipai_ocr_paddleocr`
- [ ] Create spec bundle `spec/ipai-hr-payroll-ph/` for `ipai_hr_payroll_ph`
- [ ] Create spec bundle `spec/ipai-bir-compliance/` for BIR modules (1601c, 2316, alphalist)

## Verification Script

Re-dump installed modules from production (no UI required):

```bash
ssh root@178.128.112.214 "docker exec odoo-prod python3 -c \"
import psycopg2
conn = psycopg2.connect(
  host='private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com',
  port=25060, dbname='odoo_prod', user='doadmin',
  password='\$DB_PASSWORD', sslmode='require')
cur = conn.cursor()
cur.execute('SELECT name, state FROM ir_module_module WHERE state=\\'installed\\' ORDER BY name')
for r in cur.fetchall(): print(f'{r[0]}: {r[1]}')
print(f'Total: {cur.rowcount}')
conn.close()
\""
```

## Prod Rollout Steps

1. Schedule maintenance window (low-traffic: Saturday 02:00 PHT)
2. Execute pre-install checklist above
3. Install modules in dependency order (plan.md Phase C)
4. Run post-install validation checklist
5. Monitor error logs for 1 hour
6. Update SSOT files and commit
