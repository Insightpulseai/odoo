# Plan: ERP SaaS Parity — P0 OCA Module Installation

## Pre-requisites

1. Production backup exists (pg_dump of `odoo_prod`).
2. OCA/helpdesk submodule vendored under `addons/oca/helpdesk`.
3. `addons_path` in `odoo.conf` includes all OCA repo directories.
4. Odoo service can be restarted without user impact (maintenance window).

## Dependency Graph (Text)

```
account
├── account_reconcile_oca        [1]
└── account_asset_management     [2]

base
├── dms                          [3]
│   └── dms_field                [4]
├── base_tier_validation         [7]
│   └── base_tier_validation_formula  [8]
└── (no further deps)

mail
├── helpdesk_mgmt                [5]
│   └── helpdesk_mgmt_sla        [6]
└── (no further deps)

project
└── project_task_dependency      [9]
```

Numbers in brackets = install_order from `oca_p0_allowlist.yaml`.

## Install Order (Dependency-Safe)

### Phase A: Vendor missing submodule

```bash
# On local dev machine (NOT production)
cd /path/to/repo
git submodule add -b 19.0 https://github.com/OCA/helpdesk addons/oca/helpdesk
git add .gitmodules addons/oca/helpdesk
git commit -m "chore(oca): vendor OCA/helpdesk submodule for P0 parity"
git push origin <branch>
```

### Phase B: Update addons_path

Add `addons/oca/helpdesk` to the comma-separated `addons_path` in
`config/odoo/odoo.conf` (or the Docker-mounted equivalent).

### Phase C: Install modules (production)

Install in dependency order. Each install is atomic — if it fails,
skip remaining and execute rollback.

```bash
# SSH into droplet, exec into container
ssh root@178.128.112.214
docker exec -it odoo-prod bash

# Install one-by-one (safest) or batch if confident
odoo-bin -d odoo_prod -i account_reconcile_oca --stop-after-init
odoo-bin -d odoo_prod -i account_asset_management --stop-after-init
odoo-bin -d odoo_prod -i dms,dms_field --stop-after-init
odoo-bin -d odoo_prod -i helpdesk_mgmt,helpdesk_mgmt_sla --stop-after-init
odoo-bin -d odoo_prod -i base_tier_validation,base_tier_validation_formula --stop-after-init
odoo-bin -d odoo_prod -i project_task_dependency --stop-after-init
```

### Phase D: Restart and verify

```bash
docker restart odoo-prod
# Wait 30s for startup
sleep 30
# Verify all 9 modules installed
docker exec odoo-prod python3 -c "
import psycopg2
conn = psycopg2.connect(...)
cur = conn.cursor()
cur.execute(\"SELECT name, state FROM ir_module_module WHERE name IN (
  'account_reconcile_oca','account_asset_management',
  'dms','dms_field',
  'helpdesk_mgmt','helpdesk_mgmt_sla',
  'base_tier_validation','base_tier_validation_formula',
  'project_task_dependency'
) ORDER BY name\")
for r in cur.fetchall():
    assert r[1] == 'installed', f'{r[0]} not installed: {r[1]}'
    print(f'OK: {r[0]} = {r[1]}')
conn.close()
"
```

## Rollback Strategy

If **any** module install fails:

1. **Do not restart Odoo** — the failed module is not loaded yet.
2. Restore database from pre-install backup:
   ```bash
   pg_restore --clean --if-exists -d odoo_prod /backups/odoo_prod_pre_parity.dump
   ```
3. Remove the failed module from the install list.
4. Investigate error logs (`/var/log/odoo/odoo.log`).
5. File issue and retry after fix.

If Odoo was already restarted and is broken:

1. Stop container: `docker stop odoo-prod`
2. Restore DB from backup.
3. Start container: `docker start odoo-prod`
4. Verify clean state with module count check (should be 383).

## Validation Checks

| Check | Command | Expected |
|-------|---------|----------|
| Module count | `SELECT count(*) FROM ir_module_module WHERE state='installed'` | 392 (383 + 9) |
| All P0 installed | Query above in Phase D | All 9 = 'installed' |
| No broken modules | `SELECT name FROM ir_module_module WHERE state='to upgrade'` | Empty |
| Odoo health | `curl -s https://erp.insightpulseai.com/web/login` | HTTP 200 |
| Bank recon menu | Login → Accounting → Bank Reconciliation visible | Menu exists |
| DMS menu | Login → Documents menu visible | Menu exists |
| Helpdesk menu | Login → Helpdesk menu visible | Menu exists |
