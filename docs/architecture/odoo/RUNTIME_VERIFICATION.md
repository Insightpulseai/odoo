# Odoo Runtime Verification Matrix

> Proof-based checklist for verifying the production Odoo deployment is architecturally correct.
> Each section requires deterministic evidence — not assumptions, not screenshots alone.

---

## Current Status Summary

| Layer | Status | Evidence |
|-------|--------|----------|
| Browser surface | **UP** | `https://erp.insightpulseai.com/web/login` loads, static assets serve |
| Ingress | **UNVERIFIED** | AFD routing not yet proven |
| Origin privacy | **UNVERIFIED** | Direct ACA FQDN bypass not tested |
| Database topology | **UNVERIFIED** | Private VNet access not confirmed |
| Worker/Cron split | **UNVERIFIED** | Separate ACA containers exist but health not confirmed |
| Filestore persistence | **UNVERIFIED** | Azure Files mount not confirmed |
| Backup/Restore | **UNVERIFIED** | PITR and filestore backup not tested |
| Branding | **INCOMPLETE** | Placeholder logo, default Odoo attribution visible |
| Security hardening | **UNVERIFIED** | dbfilter, list_db, admin_passwd, database manager not audited |

---

## 1. Browser Surface Proof

**What it proves:** Application is reachable and serving HTTP responses.

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| HTTPS resolves | `curl -sI https://erp.insightpulseai.com/web/login` | HTTP 200 | |
| TLS certificate valid | `echo \| openssl s_client -connect erp.insightpulseai.com:443 2>/dev/null \| openssl x509 -noout -dates` | Not expired, issued to `*.insightpulseai.com` or `erp.insightpulseai.com` | |
| Static assets load | `curl -so /dev/null -w "%{http_code}" https://erp.insightpulseai.com/web/assets/web/static/src/img/logo.png` | HTTP 200 | |
| Health endpoint | `curl -sf https://erp.insightpulseai.com/web/health` | `ok` or HTTP 200 | |

---

## 2. Ingress Proof (Azure Front Door)

**What it proves:** Traffic routes through AFD with WAF, not directly to origin.

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| AFD header present | `curl -sI https://erp.insightpulseai.com/ \| grep -i x-azure-ref` | `X-Azure-Ref` header exists | |
| AFD POP header | `curl -sI https://erp.insightpulseai.com/ \| grep -i x-cache` | Present (AFD cache behavior) | |
| DNS resolves to AFD | `dig +short erp.insightpulseai.com` | CNAME to `*.azurefd.net` | |
| WAF active | `az network front-door waf-policy show --name <policy> --resource-group rg-ipai-dev` | WAF mode = `Prevention` or `Detection` | |

---

## 3. Origin Privacy Proof

**What it proves:** Odoo ACA origin is not publicly bypassable.

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| Direct ACA FQDN blocked | `curl -sI https://ipai-odoo-dev-web.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io/web/login` | Connection refused, 403, or timeout (NOT 200) | |
| Ingress restriction | `az containerapp show -n ipai-odoo-dev-web -g rg-ipai-dev --query "properties.configuration.ingress"` | `allowInsecure: false`, IP restriction or AFD header check | |

---

## 4. Database Topology Proof

**What it proves:** PostgreSQL is private, HA-capable, correctly configured.

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| Server exists | `az postgres flexible-server show -n ipai-odoo-dev-pg -g rg-ipai-dev` | Server state = `Ready` | |
| Private networking | `az postgres flexible-server show -n ipai-odoo-dev-pg -g rg-ipai-dev --query "network.publicNetworkAccess"` | `Disabled` | |
| HA mode | `az postgres flexible-server show -n ipai-odoo-dev-pg -g rg-ipai-dev --query "highAvailability.mode"` | `ZoneRedundant` (preferred) or `SameZone` | |
| Database exists | `az postgres flexible-server db show -n ipai-odoo-dev-pg -g rg-ipai-dev -d odoo` | Database `odoo` exists | |
| No public bypass | `psql -h ipai-odoo-dev-pg.postgres.database.azure.com -U <user> -d odoo` (from outside VNet) | Connection refused or timeout | |

---

## 5. Worker/Cron Split Proof

**What it proves:** Background processing is isolated from web serving.

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| Web container running | `az containerapp show -n ipai-odoo-dev-web -g rg-ipai-dev --query "properties.runningStatus"` | `Running` | |
| Worker container running | `az containerapp show -n ipai-odoo-dev-worker -g rg-ipai-dev --query "properties.runningStatus"` | `Running` | |
| Cron container running | `az containerapp show -n ipai-odoo-dev-cron -g rg-ipai-dev --query "properties.runningStatus"` | `Running` | |
| Worker has no ingress | `az containerapp show -n ipai-odoo-dev-worker -g rg-ipai-dev --query "properties.configuration.ingress"` | `null` (no HTTP ingress) | |
| Cron has no ingress | `az containerapp show -n ipai-odoo-dev-cron -g rg-ipai-dev --query "properties.configuration.ingress"` | `null` (no HTTP ingress) | |

---

## 6. Filestore Persistence Proof

**What it proves:** Uploads/attachments survive container restarts.

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| Volume mount exists | `az containerapp show -n ipai-odoo-dev-web -g rg-ipai-dev --query "properties.template.volumes"` | Azure Files volume for `/var/lib/odoo` | |
| Shared across roles | Worker and cron mount same Azure Files share | Same share name in all three containers | |
| Survives restart | Upload file → restart container → file still accessible | File persists | |

---

## 7. Backup/Restore Proof

**What it proves:** Data can be recovered after failure.

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| Automated backup enabled | `az postgres flexible-server show -n ipai-odoo-dev-pg -g rg-ipai-dev --query "backup"` | `backupRetentionDays` >= 7, `geoRedundantBackup` status | |
| PITR works | Restore to point-in-time in test RG, verify data | Restored DB has recent data | |
| Filestore backup exists | Azure Files snapshot or Azure Backup vault | Snapshot schedule active | |

---

## 8. Branding Proof

**What it proves:** Custom enterprise identity is applied.

| Check | Method | Expected | Actual |
|-------|--------|----------|--------|
| Custom logo | Visual: `/web/login` page | InsightPulse AI logo, not "Your logo" placeholder | |
| Odoo debranding | Visual: login page footer | No "Powered by Odoo" (requires `mail_debrand` or custom) | |
| Favicon | `curl -sI https://erp.insightpulseai.com/favicon.ico` | Custom favicon, not default Odoo | |
| Page title | `curl -s https://erp.insightpulseai.com/web/login \| grep '<title>'` | Custom title, not "Odoo" | |

---

## 9. Security Hardening Proof

**What it proves:** Attack surface is minimized per Odoo deployment guide.

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| `proxy_mode` enabled | In `config/prod/odoo.conf` | `proxy_mode = True` | **YES** (confirmed in config) |
| `list_db` disabled | In `config/prod/odoo.conf` | `list_db = False` | **YES** (confirmed in config) |
| `admin_passwd` disabled | In `config/prod/odoo.conf` | `admin_passwd = False` | **YES** (confirmed in config) |
| `dbfilter` strict | In `config/prod/odoo.conf` | `dbfilter = ^odoo$` | **YES** (confirmed in config) |
| Database manager blocked | `curl -s https://erp.insightpulseai.com/web/database/manager` | 404 or redirect, NOT the manager UI | |
| Database selector blocked | `curl -s https://erp.insightpulseai.com/web/database/selector` | 404 or redirect | |
| Key Vault bindings | `az containerapp show -n ipai-odoo-dev-web -g rg-ipai-dev --query "properties.template.containers[0].env"` | Secrets reference Key Vault, not literal values | |
| Managed identity | `az containerapp identity show -n ipai-odoo-dev-web -g rg-ipai-dev` | System-assigned or user-assigned identity enabled | |

---

## 10. Websocket / Longpoll Proof

**What it proves:** Live chat and real-time features work correctly.

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| Longpoll endpoint | `curl -sI https://erp.insightpulseai.com/websocket/` | HTTP 101 Upgrade or valid response | |
| AFD websocket routing | Front Door routing rule for `/websocket/*` exists | Routes to web container's gevent port | |

---

## Verification Execution

Run all checks:

```bash
# From a machine with Azure CLI authenticated
./scripts/verify_prod_architecture.sh
```

Each check should output `PASS` or `FAIL` with evidence.
Results saved to `docs/evidence/<YYYYMMDD-HHMM>/prod-architecture/`.

---

## Phase Classification

| Phase | Criteria |
|-------|---------|
| `reachable` | Browser surface passes (section 1) |
| `ingress-verified` | AFD routing confirmed (sections 1-2) |
| `origin-private` | Direct bypass blocked (sections 1-3) |
| `data-hardened` | DB private, HA, backup proven (sections 4, 7) |
| `runtime-split` | Web/worker/cron isolated and healthy (section 5) |
| `production-ready` | All 10 sections pass |

**Current phase: `reachable` (upgrading to `ingress-verified` pending origin lockdown proof)**

---

## Azure Inventory Reconciliation from Resource Export

### Inventory-confirmed Odoo dev resources

Observed in Azure resource inventory (2026-03-18):

- Front Door: `ipai-fd-dev` (`rg-ipai-shared-dev`)
- Front Door WAF policy: `ipaiDevWafPolicy` (`rg-ipai-shared-dev`)
- Application Insights: `appi-ipai-dev` (`rg-ipai-shared-dev`)
- Log Analytics: `law-ipai-dev` (`rg-ipai-shared-dev`)
- Odoo Container Apps Environment: `ipai-odoo-dev-env` (`rg-ipai-dev`)
- Odoo app surfaces:
  - `ipai-odoo-dev-web`
  - `ipai-odoo-dev-worker`
  - `ipai-odoo-dev-cron`
- Odoo jobs:
  - `ipai-odoo-install`
  - `ipai-odoo-dev-wave1`
- Odoo Key Vault: `ipai-odoo-dev-kv` (`rg-ipai-dev`)
- Odoo PostgreSQL Flexible Server: `ipai-odoo-dev-pg` (`rg-ipai-dev`)
- Additional PostgreSQL Flexible Server: `pg-ipai-dev` (`rg-ipai-data-dev`)

### Interpretation

The Odoo dev runtime is not a single ad hoc resource. It already has:

- dedicated ingress tier
- dedicated WAF policy
- dedicated Container Apps environment
- split runtime roles (`web`, `worker`, `cron`)
- dedicated Odoo dev Key Vault
- dedicated Odoo dev PostgreSQL Flexible Server

However, the inventory also reveals topology drift:

- there are **two PostgreSQL Flexible Servers**: `ipai-odoo-dev-pg` and `pg-ipai-dev`
- Odoo app resources live primarily in `rg-ipai-dev`
- ingress/observability/shared identities live primarily in `rg-ipai-shared-dev`
- some agent/supabase resources live in `rg-ipai-agents-dev`
- network artifacts for PostgreSQL appear under `rg-ipai-ai-dev` (`nsg-pg-ipai-dev`), which is a cross-plane placement smell

### Inventory verification matrix

| Control | Evidence | Status | Notes |
|---|---|---|---|
| Front Door exists for dev ingress | `ipai-fd-dev` in `rg-ipai-shared-dev` | PASS | Public edge resource exists |
| WAF policy exists | `ipaiDevWafPolicy` in `rg-ipai-shared-dev` | PASS | Edge protection object exists |
| Odoo has dedicated Container Apps environment | `ipai-odoo-dev-env` in `rg-ipai-dev` | PASS | Runtime isolation confirmed |
| Odoo runtime split exists | `ipai-odoo-dev-web`, `worker`, `cron` | PASS | Correct app-role separation |
| Odoo install/init jobs exist | `ipai-odoo-install`, `ipai-odoo-dev-wave1` | PASS | Deployment/init path exists |
| Odoo-specific Key Vault exists | `ipai-odoo-dev-kv` | PASS | Secret boundary exists |
| Dedicated Odoo PostgreSQL server exists | `ipai-odoo-dev-pg` | PASS | Correct DB product and dedicated server |
| Single canonical dev PostgreSQL surface | `ipai-odoo-dev-pg` and `pg-ipai-dev` both exist | PARTIAL | DB surface duplication/drift |
| Resource-group boundaries clean | Odoo/shared/agents/data split across multiple RGs | PARTIAL | Document explicit ownership boundaries |
| Production-ready network posture | Not proven by inventory | PARTIAL | Edge objects exist, origin lockdown needs proof |

---

## Operator Connectivity Verification from VS Code

### Evidence

VS Code PostgreSQL extension connected to `ipai-odoo-dev-pg.postgres.database.azure.com`:

- visible databases: `azure_maintenance`, `azure_sys`, `odoo`, `odoo_staging`, `postgres`, `template0`, `template1`
- visible roles: `azure_pg_admin`, `pg_checkpoint`, `pg_database_owner`, `pg_monitor`, `pg_read_all_data`, `pg_write_all_data`
- Key Vault credential boundary confirmed: `ipai-odoo-dev-kv` secrets `pg-admin-login`, `pg-admin-password`, `pg-server-fqdn`

### Operator connectivity matrix

| Control | Evidence | Status | Notes |
|---|---|---|---|
| Azure PostgreSQL is operator-reachable | VS Code extension connected | PASS | Live authenticated client connectivity |
| Database enumeration works | `odoo`, `odoo_staging`, system DBs visible | PASS | Metadata inspection confirmed |
| Role enumeration works | Azure/system PG roles visible | PASS | Server-level inspection path exists |
| Key Vault credential boundary exists | `ipai-odoo-dev-kv` secrets observed | PASS | Secret location evidenced |
| Canonical dev DB naming aligned | active DB is `odoo` on dev server | PARTIAL | Should be `odoo_dev` |
| Staging isolation from dev | `odoo_staging` on dev server | PARTIAL | Environment boundary blurred |

---

## Azure PostgreSQL Runtime Verification

### Current observed evidence

- platform: Azure Database for PostgreSQL Flexible Server
- server: `ipai-odoo-dev-pg`
- public network access: enabled
- direct connection port: 5432
- databases: `postgres`, `odoo`, `odoo_staging`

### Database verification matrix

| Control | Evidence | Status | Notes |
|---|---|---|---|
| Azure PostgreSQL Flexible Server provisioned | Azure Portal + resource export | PASS | Correct product selected |
| Odoo-related databases provisioned | `odoo` and `odoo_staging` visible | PASS | DB surfaces exist |
| Dev database naming aligned | `odoo` instead of `odoo_dev` on dev server | PARTIAL | Canonical dev DB should be `odoo_dev` |
| Staging isolation from dev server | `odoo_staging` on `ipai-odoo-dev-pg` | PARTIAL | Should move to staging server |
| Production isolation from dev server | `odoo` on `ipai-odoo-dev-pg` | FAIL | Prod DB should not be on dev server |
| Public network access disabled for prod | Public access enabled | FAIL | Acceptable for dev only |
| Direct client connectivity available | Port 5432 accessible | PASS | Operator access path exists |
| Private-only network posture | No evidence | FAIL | Production target is private-access-only |

### Target topology

| Environment | Recommended server | Recommended database |
|---|---|---|
| Local dev | local PostgreSQL | `odoo_dev` |
| Azure dev | `ipai-odoo-dev-pg` | `odoo_dev` |
| Azure staging | `ipai-odoo-staging-pg` | `odoo_staging` |
| Azure production | `ipai-odoo-prod-pg` | `odoo` |

---

## Asset Bundling Verification

### Observed issue (2026-03-18)

`web.assets_frontend_lazy.min.js` (1.9MB) returns HTTP 404 "No database is selected" when browsers request with `Accept-Encoding: gzip/br`. This breaks Owl component initialization and hides the login form.

### Root cause

Missing pre-compressed asset variants in `ir_attachment`. When Odoo cannot find the `.gz`/`.br` variant, the request falls through to a handler without database context.

### Fix applied

Asset cache cleared from `ir_attachment` via direct psql to `ipai-odoo-dev-pg`. Odoo regenerates all bundles on next page load.

### Prevention

- `scripts/ci/check_prod_assets.sh` — verifies all login page assets serve HTTP 200 with compression
- `.github/workflows/prod-asset-health.yml` — daily scheduled check

---

*Last updated: 2026-03-18*
