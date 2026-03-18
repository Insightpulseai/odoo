# Go-Live & Production Checklist (Odoo 18 CE + OCA + IPAI)

**Scope:**
- Self-hosted Odoo 18 Community + OCA, with IPAI modules
- Focus: PH expense & travel, equipment booking & inventory, finance month-end close + PH BIR task automation (Finance PPM)
- Deterministic seeds + schema artifacts with CI drift gates

---

## 1. Release Readiness Gates (must be green)

- [ ] Main CI: lint/static checks/tests all PASS
- [ ] repo-structure gate PASS (TREE/SITEMAP consistent)
- [ ] data-model-drift PASS (DBML/ERD/ORM regenerated + no diff)
- [ ] seed-finance-close-drift PASS (xlsx → seed artifacts regenerated + no diff)
- [ ] guardrails PASS (no Enterprise/IAP/odoo.com upsells reintroduced)

---

## 2. Artifact Integrity (deterministic regeneration)

Run locally / CI runner:

```bash
# Data model drift check
python scripts/generate_odoo_dbml.py
git diff --exit-code docs/data-model/

# Finance PPM seed drift check
python scripts/seed_finance_close_from_xlsx.py --validate
git diff --exit-code addons/ipai/ipai_finance_close_seed

# Finance PPM data validation
python scripts/validate_finance_ppm_data.py
# Expected: 0 errors, 0 warnings
```

---

## 3. Module Installability (CE + OCA only)

On a fresh database:

- [ ] Install bridge: `ipai_enterprise_bridge`
- [ ] Install vertical bundle(s): `ipai_ces_bundle` (projects/timesheets) as needed
- [ ] Install finance seed module(s) and program modules required by Finance PPM
- [ ] Verify module states in `ir_module_module` = installed

```bash
# Verification command
docker compose exec -T db psql -U odoo -d odoo_core -c "
SELECT name, state FROM ir_module_module
WHERE name LIKE 'ipai_%' AND state = 'installed'
ORDER BY name;"
```

---

## 4. Finance PPM Functional Smoke (non-UI, automated)

- [ ] Stage model exists (6 canonical stages) with correct fold/state mapping
- [ ] Imported/generated tasks include deterministic `task_code`
- [ ] Required tags/labels exist (if used for reporting)
- [ ] Deadlines respect PH holidays/weekends where configured
- [ ] Validation script matches Excel "Data Validation" expectations

```bash
# Run validation
python scripts/validate_finance_ppm_data.py
```

---

## 5. Production Infrastructure & Config (droplet)

- [ ] Docker Compose prod stack is up (odoo/db/nginx as applicable)
- [ ] Database reachable, sslmode where required for managed DB
- [ ] Filestore persistent volume confirmed
- [ ] Backups configured (DB + filestore) with restore drill documented

```bash
# Health check
curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.com/web/health
# Expected: 200

# Container status
docker compose -f deploy/docker-compose.prod.yml ps
```

---

## 6. Security Baseline

- [ ] Admin accounts reviewed; least privilege enforced for operational users
- [ ] SMTP/Mail provider verified (send/receive test)
- [ ] Rate limits / auth hardening (where applicable) confirmed
- [ ] No secrets committed; production secrets only in `.env` or secret store

---

## 7. Observability & Operations

- [ ] Health checks: HTTP /web reachable + Odoo logs clean on startup
- [ ] Error budget: confirm no recurring tracebacks in logs after idle + scheduled jobs
- [ ] On-call runbook present: restart, rollback, restore, diagnose

```bash
# Check logs for errors
docker compose -f deploy/docker-compose.prod.yml logs --tail=100 odoo | grep -i error
```

---

## 8. Cutover Plan

- [ ] Data migration path defined (if moving from prior DB)
- [ ] Freeze window agreed (if needed)
- [ ] Rollback plan tested (redeploy previous tag + restore DB snapshot)

---

## 9. Post-Go-Live (first 72 hours)

- [ ] Monitor logs + performance
- [ ] Confirm finance close run completes end-to-end
- [ ] Capture issues as tickets and lock a hotfix cadence

---

## Rollback Procedure

```bash
# 1. Identify last known-good commit
git log --oneline -n 10

# 2. Checkout known-good state
git checkout <KNOWN_GOOD_COMMIT>

# 3. Redeploy
cd deploy
docker compose -f docker-compose.prod.yml up -d --remove-orphans

# 4. Verify
docker compose -f docker-compose.prod.yml logs -f --tail=200 odoo
```

---

*Last updated: 2026-01-21*
