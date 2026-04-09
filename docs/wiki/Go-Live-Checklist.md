# Odoo on Azure + Databricks Go-Live Checklist

Use this as the minimum production gate for the InsightPulse AI target stack.

---

## 1. Architecture Lock

- [ ] Odoo is the only transactional SoR for finance, inventory, projects, and operational master data
- [ ] Databricks is the system of intelligence only: ingestion, transforms, governed analytics, ML/context products
- [ ] Unity Catalog is enabled and authoritative for Databricks data governance
- [ ] Power BI is the semantic consumption layer; Fabric is optional

## 2. Public Edge and Routing

- [ ] Azure Front Door is the single public edge for all internet-facing app surfaces
- [ ] Front Door WAF is enabled with managed rules
- [ ] Host header behavior is validated end to end
- [ ] All hostnames in `ssot/network/public_endpoints.yaml` are classified (canonical/transitional/legacy)
- [ ] No silent Vercel / DigitalOcean / direct-IP drift

## 3. Odoo Tenancy and Database Routing

- [ ] `dbfilter` is explicitly set for production
- [ ] Hostname-to-database routing is tested for every intended tenant hostname
- [ ] External API clients are validated with correct Host behavior
- [ ] Multi-company vs database-per-tenant decision is documented

## 4. Odoo Application Readiness

- [ ] All custom modules install cleanly on target Odoo 18 build
- [ ] All cron jobs / server actions are green (no `analytic_account_id` drift or deprecated field errors)
- [ ] Login page, assets, branding, and core user journeys are smoke-tested on the real hostname
- [ ] Core business paths pass: sales/order, purchasing, invoicing, payments, projects/tasks, Finance PPM

## 5. PostgreSQL Production Readiness

- [ ] Authoritative Odoo PostgreSQL server is documented (`ipai-odoo-dev-pg`)
- [ ] Duplicate Odoo databases on non-authoritative servers are marked stale or removed
- [ ] PostgreSQL HA mode is chosen intentionally
- [ ] Geo-redundant backups are enabled where required
- [ ] Backup and restore are tested, not just configured
- [ ] Enhanced metrics and alerting are active

## 6. Identity, Secrets, and Least Privilege

- [ ] Human access is through Entra with named admin accounts and MFA
- [ ] Emergency access accounts exist and are tested (`admin@`, `emergency-admin@insightpulseai.com`)
- [ ] Databricks principals are provisioned at account level, not workspace-by-workspace
- [ ] Group definitions come from IdP and match intended role model
- [ ] All secrets are in Key Vault; no runtime secrets in repo or static config

## 7. Databricks Production Readiness

- [ ] Workspace networking is production-grade (VNet injection preferred)
- [ ] Unity Catalog catalogs/schemas/tables are permissioned for least privilege
- [ ] All required log categories are enabled (workspace, clusters, accounts, jobs, notebooks, UC audit)
- [ ] Log delivery to Log Analytics / observability sink is working
- [ ] Bronze / silver / gold layers are defined and documented
- [ ] Production jobs and schedules are enabled only after data quality checks pass

## 8. Data and Integration Contract Freeze

- [ ] Odoo to Databricks extract scope is frozen
- [ ] Gold datasets for finance / marketing / retail are named and versioned
- [ ] Reverse-write paths are bounded and documented
- [ ] No analytics or agent runtime has unconstrained write authority into Odoo

## 9. Observability and Alerting

- [ ] Odoo app logs are centralized
- [ ] PostgreSQL alerts are configured (availability, connections, IOPS, storage)
- [ ] Databricks alerts are configured (failed jobs, cluster failures, permission anomalies)
- [ ] Front Door / WAF logs are enabled
- [ ] One on-call dashboard exists showing edge to app to DB to Databricks health

## 10. Cutover and Rollback

- [ ] Cutover owner, rollback owner, and freeze window are named
- [ ] Pre-cutover backup is taken and restore-tested
- [ ] DNS / Front Door / hostname changes are reversible
- [ ] Rollback criteria are written in advance
- [ ] Post-cutover validation script exists for: login, core transactions, API calls, Databricks triggers, BI freshness

## 11. Go / No-Go Decision

Only go live when ALL of the above are true.

**Hard stop criteria** (do not go live if any remain):

- Multiple "authoritative" Odoo databases with unclear ownership
- Missing `dbfilter` in multi-database production
- Broken Odoo 18 custom jobs / fields / cron actions
- Databricks without Unity Catalog governance
- PostgreSQL without tested restore path
- Public edge without WAF
- Undocumented reverse-write path into Odoo
