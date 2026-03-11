# DO → Azure Migration Plan

> **Status**: PARTIAL (4/9 services migrated, 4 DO-backed, 1 Azure VM)
> **Owner**: Platform Engineering
> **Last Updated**: 2026-03-11 (+08:00)
> **SSOT**: `infra/ssot/migration/do-to-azure-service-mapping.yaml`
> **Parent**: `infra/ssot/azure/PLATFORM_TARGET_STATE.md` (v1.5.0)
> **Cutover checklist**: `infra/ssot/azure/hostname-cutover-checklist.yaml`

## Scope
Decommission DigitalOcean runtime (`odoo-erp-prod` droplet `178.128.112.214`) after all production hostnames are served by Azure-native backends behind Azure Front Door, with Cloudflare remaining authoritative DNS.

## Evidence Baseline (Live)
- Azure subscription and resources are live (57 resources; ACA + Front Door deployed).
- DNS for canonical hostnames (`erp`, `auth`, `mcp`, `n8n`, `ocr`, `superset`, `plane`, `www`, apex) resolves to Azure Front Door endpoint `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net`.
- Front Door origins still referencing DO droplet:
  - `auth` -> `178.128.112.214`
  - `mcp-gateway` -> `178.128.112.214`
  - `ocr` -> `178.128.112.214`
  - `superset` -> `178.128.112.214`
- Front Door origins already Azure-native:
  - `odoo-web`, `plane`, `shelf`, `crm` -> ACA FQDNs
  - `n8n` -> `4.193.100.31` (Azure VM)
- DO App Platform active apps: none.
- DO droplets: one active droplet (`odoo-erp-prod`, `178.128.112.214`).

## Current-State Inventory (DO Runtime)
### Services currently on DO droplet (confirmed by SSOT + AFD origin refs)
- Odoo web ingress compatibility surface
- Auth service (`auth.insightpulseai.com`)
- MCP gateway (`mcp.insightpulseai.com`)
- OCR service (`ocr.insightpulseai.com`)
- Superset (`superset.insightpulseai.com`)
- Legacy reverse-proxy behavior (nginx TLS/origin assumptions)

### Droplet-bound hostnames, ports, and current backend assumptions
| Hostname | Service | Current DO Backend Port | Current Front Door Origin |
|---|---|---:|---|
| auth.insightpulseai.com | Auth service | 8080 | 178.128.112.214 |
| mcp.insightpulseai.com | MCP gateway | 8766 | 178.128.112.214 |
| ocr.insightpulseai.com | OCR service | 8001 | 178.128.112.214 |
| superset.insightpulseai.com | Superset | 8088 | 178.128.112.214 |

### Containers/compose and storage dependencies (repo-derived)
- Runtime compose references:
  - `infra/docker-compose.prod.yaml`
  - `infra/deploy/DROPLET_DEPLOYMENT.md` (`docker-compose.droplet.yml` operational path)
- Reverse proxy vhosts:
  - `infra/nginx/mcp.insightpulseai.com.conf`
  - `infra/nginx/ocr.insightpulseai.com.conf`
  - `infra/nginx/superset.insightpulseai.com.conf`
  - `infra/deploy/nginx/auth.insightpulseai.com.conf`
- Persistent volume references:
  - `infra/docker-compose.prod.yaml` named volume `odoo_data`
  - `infra/deploy/runtime/odoo-prod.docker_inspect.json` (`/var/lib/docker/volumes/deploy_odoo-web-data/_data`)
- Worker/cron surfaces:
  - Odoo worker/cron are already represented in Azure (`ipai-odoo-dev-worker`, `ipai-odoo-dev-cron`)
  - Legacy DO-side cron/systemd jobs are not fully discoverable from repo-only evidence and remain an explicit audit item before teardown.

### Runtime assumptions still tied to DO
- Origin host `178.128.112.214` used by four Front Door origin groups.
- Legacy nginx/certbot operational docs under `infra/nginx/**`, `infra/deploy/**`.
- Legacy DNS docs still describing direct A-record to DO in some SSOT files.

## Migration Waves (Deterministic)
1. Wave 1 (already cut): DNS/edge cutover to Front Door for all canonical hostnames.
2. Wave 2: Replace DO origins for non-core services (`mcp`, `ocr`, `auth`, `superset`) with Azure-native origins.
3. Wave 3: Validate no Front Door origin references `178.128.112.214`.
4. Wave 4: Stop DO runtime workloads; capture final snapshot/log references.
5. Wave 5: Decommission DO droplet and remove residual DO runtime references from SSOT/docs.

## Cutover Preconditions per Remaining DO Service
- Runtime deployed to Azure target and healthy at target health endpoint.
- Front Door origin switched to Azure target and `Enabled`.
- Smoke checks pass for public hostname through Cloudflare + Front Door.
- Rollback target retained for one stabilization window.

## Rollback Policy
- Route-level rollback only (Front Door origin swap back to DO origin host) until stabilization complete.
- DNS rollback is not primary since DNS already points to Front Door.
- Decommission gate requires rollback path retained until all post-cutover checks pass.

## Decommission Gates
DO droplet can be decommissioned only when all are true:
- No `az afd origin list` entry has `host == 178.128.112.214`.
- All canonical hostnames health checks pass via public URLs.
- Auth reachability and integration checks pass.
- OCR and Superset application smoke checks pass.
- Final report confirms no production traffic to DO.

## Deterministic Blockers

- Missing Azure-native runtime parity confirmation for `auth`, `mcp`, `ocr`, `superset`.
- Required infra/app manifests for these four surfaces are not yet aligned to active Azure origins in Front Door.
- Droplet decommission is blocked until origin migration is completed and validated.

---

## Architecture Decision: EXC-001 (Dual Odoo Deployment)

Two Odoo deployments exist on Azure. **Resolution: Deployment B is canonical.**

| | Deployment A (`rg-ipai-agents-dev`) | Deployment B (`rg-ipai-dev`) |
| - | ----------------------------------- | ---------------------------- |
| Roles | web + init (2) | web + worker + cron + install + wave1 (5) |
| Database | `pg-ipai-dev` (shared) | `ipai-odoo-dev-pg` (dedicated) |
| Registry | `cripaidev` (shared) | `ipaiodoodevacr` (dedicated) |
| Key Vault | None | `ipai-odoo-dev-kv` |

**Evidence**: Front Door routes `erp.insightpulseai.com` to `ipai-odoo-dev-web` (Deployment B). The 3-role spec matches `odoo-runtime.yaml` and `aca-odoo-services.bicep`. Deployment A is a retire candidate.

## Wave 2 Execution: Replace DO Origins with ACA

For each remaining DO-backed service, deploy an Azure Container App and swap the Front Door origin.

### 2a. Auth Service (Keycloak)

```bash
# Build and push
az acr build --registry ipaiodoodevacr \
  --image auth-keycloak:latest \
  --file docker/auth/Dockerfile .

# Deploy
az containerapp create \
  --name ipai-auth-dev \
  --resource-group rg-ipai-dev \
  --environment ipai-odoo-dev-env \
  --image ipaiodoodevacr.azurecr.io/auth-keycloak:latest \
  --target-port 8080 \
  --ingress external \
  --min-replicas 1 --max-replicas 2

# Swap Front Door origin
az afd origin update \
  --resource-group rg-ipai-shared-dev \
  --profile-name ipai-fd-dev \
  --origin-group-name auth \
  --origin-name auth-origin \
  --host-name ipai-auth-dev.<env>.southeastasia.azurecontainerapps.io
```

Pre-requisites: Export Keycloak realm config, migrate auth database, update OIDC discovery endpoints.

### 2b. MCP Gateway

```bash
az containerapp create \
  --name ipai-mcp-dev \
  --resource-group rg-ipai-dev \
  --environment ipai-odoo-dev-env \
  --image ipaiodoodevacr.azurecr.io/mcp-gateway:latest \
  --target-port 8766 \
  --ingress external \
  --min-replicas 1 --max-replicas 2
```

Pre-requisites: Update MCP tool registry endpoints, verify agent connectivity.

### 2c. OCR Service (PaddleOCR-VL)

```bash
az containerapp create \
  --name ipai-ocr-dev \
  --resource-group rg-ipai-dev \
  --environment ipai-odoo-dev-env \
  --image ipaiodoodevacr.azurecr.io/paddleocr:latest \
  --target-port 8001 \
  --ingress external \
  --cpu 2.0 --memory 4Gi \
  --min-replicas 1 --max-replicas 2
```

Pre-requisites: Upload PaddleOCR model files to Azure Blob Storage, mount as ACA volume.

Alternative: Replace PaddleOCR with Azure AI Document Intelligence (managed service). Evaluate cost/accuracy trade-off.

### 2d. Superset

```bash
az containerapp create \
  --name ipai-superset-dev \
  --resource-group rg-ipai-dev \
  --environment ipai-odoo-dev-env \
  --image ipaiodoodevacr.azurecr.io/superset:latest \
  --target-port 8088 \
  --ingress external \
  --min-replicas 1 --max-replicas 2
```

Pre-requisites: Migrate Superset metadata DB, update datasource connection strings to Azure PG.

Alternative: Retire Superset in favor of Databricks SQL dashboards. Evaluate coverage.

**Sequence**: Deploy all 4 in parallel, health-check each, then swap origins one-at-a-time (auth, mcp, ocr, superset).

## Wave 3 Validation

```bash
# Confirm no Front Door origins reference DO
az afd origin list-by-group \
  --resource-group rg-ipai-shared-dev \
  --profile-name ipai-fd-dev \
  --query "[].{group:originGroupName, host:hostName}" \
  -o table | grep -c "178.128.112.214"
# Expected: 0
```

## Wave 4: n8n Azure VM to ACA (Optimization)

n8n is on Azure VM `4.193.100.31`, not DO. This is an optimization, not a decommission blocker.

1. Export n8n workflows JSON + encrypted credentials
2. Build n8n container and push to ACR
3. Deploy to ACA with persistent storage volume
4. Import workflows and credentials
5. Swap Front Door origin from VM IP to ACA FQDN
6. Decommission Azure VM

## Database Migration (if needed)

| Database | Source | Target | Method |
| -------- | ------ | ------ | ------ |
| Odoo prod | DO managed PG `odoo-db-sgp1:25060` | Azure PG `ipai-odoo-dev-pg` | pg_dump/pg_restore |
| n8n | Azure VM or DO managed PG | Azure PG `pg-ipai-dev` | pg_dump/pg_restore |
| Superset metadata | DO managed PG | Azure PG `pg-ipai-dev` | pg_dump/pg_restore |

If Odoo ERP database is already on Azure PG (Deployment B has `ipai-odoo-dev-pg`), confirm data currency and skip migration.

## SSOT Cleanup (Post-Decommission)

Remove or archive residual DO references:

- `infra/deploy/PRODUCTION_SETUP.md` — archive
- `infra/deploy/DROPLET_DEPLOYMENT.md` — archive
- `infra/nginx/*` — archive
- `.claude/rules/infrastructure.md` — update IPs
- `infra/cloudflare/zones/insightpulseai.com/records.yaml` — remove A records for `178.128.112.214`
- `infra/terraform/cloudflare/insightpulseai.com/variables.tf` — remove `origin_ipv4`
- `infra/ssot/azure/service-matrix.yaml` — update hosting to `azure`

## Cost Impact

| Item | DO Monthly | Post-Migration | Savings |
| ---- | ---------- | -------------- | ------- |
| Droplet (`odoo-production`) | ~$48 | $0 | -$48 |
| Managed PG (`odoo-db-sgp1`) | ~$15 | $0 (Azure PG already provisioned) | -$15 |
| App Platform (if any remain) | ~$0-25 | $0 | -$0-25 |
| **Total** | **~$63-88** | **$0** | **-$63-88/mo** |

## Timeline

| Milestone | Target | Status |
| --------- | ------ | ------ |
| EXC-001 resolved | 2026-03-11 | **This commit** |
| Wave 2: ACA deployed for 4 DO services | T+3 days | Pending |
| Wave 2: Origins swapped | T+5 days | Pending |
| Wave 3: Zero DO origins validated | T+5 days | Pending |
| Wave 4: n8n VM to ACA | T+7 days | Pending (optional) |
| Database migration (if needed) | T+10 days | Pending |
| Droplet powered off | T+13 days | Pending |
| Droplet deleted (30-day hold) | T+43 days | Pending |

## Artifacts

| Artifact | Path | Status |
| -------- | ---- | ------ |
| Service mapping YAML | `infra/ssot/migration/do-to-azure-service-mapping.yaml` | Done |
| This migration plan | `infra/ssot/migration/DO_TO_AZURE_MIGRATION_PLAN.md` | Done |
| Hostname cutover checklist | `infra/ssot/azure/hostname-cutover-checklist.yaml` | Pre-existing |
| Front Door routes | `infra/ssot/azure/front-door-routes.yaml` | Pre-existing |
| Dual Odoo exception | `infra/ssot/azure/exceptions/dual-odoo-deployment.yaml` | Resolved (this commit) |
| Evidence logs | `web/docs/evidence/20260311-1955+0800/do-to-azure-migration/` | Done |
| Decommission report | `docs/evidence/<stamp>/do-decommission/` | Post-migration |
