# Go-Live & Production Checklist — Odoo CE + OCA + IPAI (Workbench)

Canonical docs base: https://jgtolentino.github.io/odoo-ce/
Production ERP: https://erp.insightpulseai.com

## 0) Scope (Authoritative)
- PH expense & travel management
- Equipment booking & inventory
- Finance month-end close and PH BIR tax filing task automation (Finance PPM)
- Canonical, versioned data-model artifacts (DBML / ERD / ORM maps) with CI-enforced drift gates
- CE-only, OCA-first, no EE/IAP dependencies

## 1) Pre-Go-Live Gates (CI + Repo)
- [ ] `main` is green on all required workflows
- [ ] Spec Kit enforcement: all bundles valid (4 files each)
- [ ] No EE/IAP gate passes (no enterprise deps, no upsell links)
- [ ] Data-model drift gate passes (DBML/ERD/ORM)
- [ ] Finance seed drift gate passes (XLSX -> seed regen is clean)
- [ ] `TREE.md` / `SITEMAP.md` generation is clean

## 2) Environment & Secrets (Production)
- [ ] `.env` secrets are NOT committed; production secrets only in server/CI secret store
- [ ] SMTP/Mailgun config verified (send test mail)
- [ ] OAuth settings verified (no login loop)
- [ ] Database connectivity verified (Odoo -> Postgres)
- [ ] Backups: DB + filestore backup job exists and restores are tested

## 3) Odoo App Install & Config (Deterministic)
- [ ] Install canonical stack (bridge + required bundles)
- [ ] Install Finance PPM modules + OCA Project suite dependencies
- [ ] Apply Finance PPM stage/state mapping (6 stages) via XML/CSV import artifacts
- [ ] Verify module state in `ir_module_module` is installed for required modules
- [ ] Verify access rules/groups present for Finance PPM operational roles

## 4) Finance PPM Validation
- [ ] Run seed generator from XLSX
- [ ] Run validation script (0 errors, 0 warnings)
- [ ] Verify task_code alignment for all records
- [ ] Verify stage mapping correctness
- [ ] Verify deadline and SLA rules reflect workbook spec

## 5) Superset BI (If enabled in this release)
- [ ] Superset service starts cleanly
- [ ] Superset has read-only credentials and can query analytics views
- [ ] Starter dashboards import without error
- [ ] Dashboards render without query failures

## 6) Supabase + n8n + MCP (If enabled in this release)
- [ ] Supabase migrations applied (ops schema present)
- [ ] n8n workflows imported and enabled
- [ ] MCP server tools respond; seed/validate and repo checks runnable
- [ ] Run logs/audit events are written and queryable

## 7) Production Verification (Smoke)
- [ ] Odoo web loads and login works
- [ ] Create + progress a sample Finance PPM task through all 6 stages
- [ ] Generate artifacts (exports/validation reports) and verify persistence
- [ ] Logs show no ERROR loops (Odoo + proxy + DB)

## 8) Observability & Incident Readiness
- [ ] Centralized logs (container logs + optional drain)
- [ ] Health checks exist for Odoo/DB/Reverse proxy
- [ ] Rollback plan documented (compose revert + tagged images)
