# Azure Bill of Materials — Minimum Production Set

> Resource-by-resource inventory with exact names, RG placement, and must-have/optional/off status.
> Reconciled against Azure Resource Graph (69 live resources, 2026-03-25).
> Cross-referenced by: `INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE.md`
> Validation: `scripts/ci/azure_resource_reconcile.py`
> Updated: 2026-03-25

---

## Design Principle

**Smallest serious production set.** Only deploy what supports: public entry, identity, Odoo runtime, Pulser runtime, document OCR, analytics, secrets, and observability.

---

## 1. Must-Have Resources (14 categories, ~25 ARM resources)

### 1.1 Edge & Public Entry

| Resource | Name | RG | Type | Status |
|----------|------|-----|------|--------|
| Front Door | `ipai-fd-dev` | TBD (`rg-ipai-edge-dev`) | Standard/Premium | **Missing** — must provision |
| Front Door Endpoint | `ipai-fd-dev-ep` | Via Front Door | Endpoint | **Missing** |
| WAF Policy | `ipaiDevWafPolicy` | Via Front Door | WAF | **Missing** |
| Custom Domains | `insightpulseai.com`, `www`, `erp` | Via Front Door | Managed TLS | **Missing** |
| Managed Certs | `mc-erp-insightpulseai`, `mc-www-insightpulseai`, `mc-insightpulseai-apex` | `rg-ipai-dev-odoo-runtime` | ACA Managed Cert | **Exist** (3 certs on ACA env) |

**Action**: Front Door is the **P0 gap** — no public ingress exists. Provision Front Door Standard/Premium with WAF, custom domains, and origin groups for ACA backends. ACA managed certs exist but Front Door manages its own TLS.

### 1.2 Identity

| Resource | Name | RG | Type | Status |
|----------|------|-----|------|--------|
| Entra App Registration (Odoo SSO) | `insightpulseai-odoo` | Tenant-level | App Registration | **Create** |
| Entra App Registration (Pulser Gateway) | `pulser-gateway` | Tenant-level | App Registration | **Create** |
| Entra App Registration (Pulser Agents) | `pulser-diva-agent`, etc. | Tenant-level | App Registration | **Create** |
| Managed Identity (Odoo) | `mi-ipai-odoo-dev` | `rg-ipai-shared-dev` | User-Assigned MI | **Exists** |
| Managed Identity (Lakehouse) | `mi-ipai-lakehouse-dev` | `rg-ipai-shared-dev` | User-Assigned MI | **Exists** |
| Managed Identity (Platform) | `mi-ipai-platform-dev` | `rg-ipai-shared-dev` | User-Assigned MI | **Exists** |
| Managed Identity (Agents) | `id-ipai-agents-dev` | `rg-ipai-shared-dev` | User-Assigned MI | **Exists** |
| Managed Identity (ACA) | `id-ipai-aca-dev` | `rg-ipai-agents-dev` | User-Assigned MI | **Exists** — orphaned RG, consider moving |
| Managed Identity (Databricks) | `id-ipai-databricks-dev` | `rg-ipai-ai-dev` | User-Assigned MI | **Exists** |

**Action**: Create 5-7 Entra app registrations per §7.1 of target-state architecture. Existing managed identities are sufficient.

### 1.3 Odoo Runtime

| Resource | Name | RG | Type | Status |
|----------|------|-----|------|--------|
| ACA Environment | `ipai-odoo-dev-env` | `rg-ipai-dev-odoo-runtime` | Container Apps Env | **Exists** — keep |
| Odoo Web | `ipai-odoo-dev-web` | `rg-ipai-dev-odoo-runtime` | Container App | **Exists** — keep |
| Odoo Worker | `ipai-odoo-dev-worker` | `rg-ipai-dev-odoo-runtime` | Container App | **Exists** — keep |
| Odoo Cron | `ipai-odoo-dev-cron` | `rg-ipai-dev-odoo-runtime` | Container App | **Exists** — keep |
| Container Registry | `acripaiodoo` | `rg-ipai-dev-odoo-runtime` | ACR | **Exists** — keep |
| PostgreSQL | `pg-ipai-odoo` | `rg-ipai-dev-odoo-data` | Flexible Server (GP) | **Exists** — keep (canonical, Fabric mirroring enabled) |
| Azure Files | — | `rg-ipai-dev-odoo-runtime` | Storage Account + File Share | **Create** — needed for Odoo filestore persistence |
| Odoo Storage | `stipaiodoodev` | `rg-ipai-dev-odoo-runtime` | StorageV2 | **Exists** — evaluate if convertible to Azure Files share |

**Action**: Ensure Azure Files share for Odoo filestore (`/var/lib/odoo/filestore`). `stipaiodoodev` may already serve this — verify mount type. Worker separation is non-optional.

### 1.4 Secrets & Certificates

| Resource | Name | RG | Type | Status |
|----------|------|-----|------|--------|
| Key Vault (dev) | `kv-ipai-dev` | `rg-ipai-dev-platform` | Key Vault | **Exists** — keep |
| Key Vault (staging) | `kv-ipai-staging` | `rg-ipai-shared-staging` | Key Vault | **Exists** — keep |
| Key Vault (prod) | `kv-ipai-prod` | `rg-ipai-shared-prod` | Key Vault | **Exists** — keep |
| Key Vault (Foundry) | `aifoundrkeyvault67125c7c` | `rg-ipai-ai-dev` | Key Vault (auto) | **Exists** — Foundry-managed |

**Action**: Provision all secrets listed in target-state §7.3. Two Key Vaults is fine (shared infra + Odoo-specific).

### 1.5 Pulser / Agent Runtime

| Resource | Name | RG | Type | Status |
|----------|------|-----|------|--------|
| Foundry Workspace | `aifoundry-ipai-dev` | `rg-ipai-ai-dev` | AI Foundry | **Exists** |
| Foundry Project | `proj-ipai-claude` | `rg-ipai-ai-dev` | Foundry Project | **Exists** |
| Copilot Gateway | `ipai-copilot-gateway` | `rg-ipai-dev-odoo-runtime` | Container App | **Exists** — keep |
| Azure OpenAI | `oai-ipai-dev` | `rg-ipai-ai-dev` | OpenAI (eastus) | **Exists** — keep |

**Action**: Deploy Foundry Agent Service instances for Pulser surfaces. Wire tool bindings per `ssot/contracts/foundry_tools.yaml`.

### 1.6 OCR / Document Intelligence

| Resource | Name | RG | Type | Status |
|----------|------|-----|------|--------|
| Document Intelligence | `docai-ipai-dev` | `rg-ipai-ai-dev` | Doc Intel (SEA) | **Exists** — keep |
| OCR Container | `ipai-ocr-dev` | `rg-ipai-dev-odoo-runtime` | Container App | **Exists** — keep |

**Action**: Build `ipai_doc_intelligence` Odoo module to call Doc Intel API.

### 1.7 Analytics

| Resource | Name | RG | Type | Status |
|----------|------|-----|------|--------|
| Databricks Workspace | `dbw-ipai-dev` | `rg-ipai-ai-dev` | Premium (SEA) | **Exists** — keep |
| SQL Warehouse | `e7d89eabce4c330c` | Via Databricks | PRO Serverless | **Exists** — keep |
| Unity Catalog | `dbw_ipai_dev` | Via Databricks | Default Catalog | **Exists** — keep |
| Data Lake Storage | `stipaidevlake` | `rg-ipai-ai-dev` | ADLS Gen2 | **Exists** — keep |
| Storage Credential | `ipai-lake-credential` | Via Databricks | External Location | **Exists** — keep |

**Action**: Configure JDBC extract from `pg-ipai-odoo`. Build DLT pipelines in `data-intelligence/`.

### 1.8 Observability

| Resource | Name | RG | Type | Status |
|----------|------|-----|------|--------|
| Application Insights | `appi-ipai-dev` | `rg-ipai-shared-dev` | App Insights | **Exists** — keep |
| Log Analytics | `law-ipai-dev` | `rg-ipai-shared-dev` | Log Analytics | **Exists** — keep |

**Action**: Wire ACA apps + Foundry agents to App Insights. Configure Azure Monitor alerts for critical paths.

---

## 2. Optional Resources (Deploy When Proven Needed)

| Resource | Name | When To Deploy | Current Status |
|----------|------|---------------|----------------|
| Azure AI Search | `srch-ipai-dev` | When Pulser needs production-grade indexed retrieval | **Exists** — keep but evaluate usage |
| Azure DNS Zone | `insightpulseai.com` in `rg-ipai-dev-odoo-runtime` | Zone provisioned; NS delegation still at Cloudflare | **Deployed** — needs NS cutover to activate |
| Private Endpoints | — | When hardening production network isolation | **Partial** (Databricks has private endpoint) |
| Private DNS Zones | `privatelink.postgres.database.azure.com` | With private endpoints | **Exists** for PG |
| VNet integration for ACA | — | When network isolation required | **Not configured** for ACA env |
| Language Service | `lang-ipai-dev` | If NER/sentiment needed beyond OpenAI | **Exists** — evaluate keep/remove |
| Computer Vision | `vision-ipai-dev` | If non-document image OCR needed | **Exists** — evaluate keep/remove |
| Microsoft Defender | — | For Container Apps & PostgreSQL security | **Not deployed** — high priority |
| Azure Backup | — | If managed service backup semantics insufficient | **Not deployed** |
| Power BI Workspace | — | When dashboard delivery begins | **Not deployed** — high priority gap |
| Microsoft Fabric | — | For PG mirroring + OneLake + semantic models | **Not deployed** |

---

## 3. Off / Delete (Do Not Deploy or Remove)

### 3.1 Deleted — Retired ACA Apps (Completed 2026-03-25)

| Resource | Name | RG | Status |
|----------|------|-----|--------|
| Keycloak | `ipai-auth-dev` | `rg-ipai-dev-odoo-runtime` | **Deleted** 2026-03-25 |
| Plane | `ipai-plane-dev` | `rg-ipai-dev-odoo-runtime` | **Deleted** 2026-03-25 |
| Shelf | `ipai-shelf-dev` | `rg-ipai-dev-odoo-runtime` | **Deleted** 2026-03-25 |
| Standalone CRM | `ipai-crm-dev` | `rg-ipai-dev-odoo-runtime` | **Deleted** 2026-03-25 |

### 3.2 Deleted — Supabase VM + n8n (Completed 2026-03-25)

| Resource | Name | RG | Status |
|----------|------|-----|--------|
| Supabase VM + all networking | `vm-ipai-supabase-dev` | `rg-ipai-agents-dev` | **Deleted** (RG empty) |
| n8n automation | (on Supabase VM) | `rg-ipai-agents-dev` | **Deleted** with VM |
| Legacy containers | `odoo-web`, `odoo-init`, `debug-odoo-ep` | `rg-ipai-agents-dev` | **Previously deleted** |

### 3.3 Evaluate — Keep or Remove

| Resource | Name | RG | Question |
|----------|------|-----|----------|
| Superset | `ipai-superset-dev` | `rg-ipai-dev-odoo-runtime` | Demoted to supplemental — keep if internal use justified |
| Website | `ipai-website-dev` | `rg-ipai-dev-odoo-runtime` | Evaluate: consolidate with Odoo website? |
| Login | `ipai-login-dev` | `rg-ipai-dev-odoo-runtime` | May overlap with Entra SSO — evaluate |

### 3.4 Do Not Deploy

| Service | Reason |
|---------|--------|
| AKS | ACA is sufficient for current workload |
| Service Bus | No async messaging requirement beyond Odoo queues |
| Redis | No caching layer needed (Odoo has built-in caching) |
| Azure Functions | ACA containers cover all compute needs |
| Cosmos DB | PostgreSQL is sufficient |
| App Service | ACA is the canonical compute platform |
| Multiple storage accounts per micro-use-case | Consolidate to `stipaiodoodev` + `stipaidevlake` |
| Fabric as primary data platform | Databricks is primary; Fabric is consumption complement only |
| Anything recreating Supabase/n8n/Plane/Shelf | Retired |

---

## 4. Target Resource Group Structure

### Production Target (5 RGs)

```
rg-ipai-edge-prod
  └── Front Door + WAF policy

rg-ipai-odoo-prod
  ├── ACA environment
  ├── ipai-odoo-web (container app)
  ├── ipai-odoo-worker (container app)
  ├── ipai-odoo-cron (container app)
  ├── ipai-copilot-gateway (container app)
  ├── ipai-ocr (container app)
  ├── ipai-api-facade (container app)
  ├── ACR (cripaidev)
  ├── PostgreSQL Flexible Server (pg-ipai-odoo)
  ├── Azure Files (Odoo filestore)
  ├── Key Vault (kv-ipai-odoo-prod)
  └── App Insights + Log Analytics

rg-ipai-ai-prod
  ├── Foundry workspace + project
  ├── Azure OpenAI
  ├── Document Intelligence
  ├── AI Search (optional)
  └── AI-related monitoring

rg-ipai-data-prod
  ├── Databricks workspace
  ├── ADLS Gen2 (lake storage)
  └── Databricks-managed RG (auto, do not touch)

rg-ipai-shared-prod
  ├── Managed identities (Odoo, Lakehouse, Platform, Agents)
  └── Shared Key Vault (kv-ipai-prod)
```

### Dev Environment (Current — Consolidate)

The current 8+ RGs should consolidate toward the production pattern:

| Current RG | Target Mapping |
|-----------|---------------|
| `rg-ipai-dev-odoo-runtime` | → `rg-ipai-odoo-dev` |
| `rg-ipai-shared-dev` | → `rg-ipai-shared-dev` (keep) |
| `rg-ipai-ai-dev` | → `rg-ipai-ai-dev` (keep) |
| `rg-ipai-dev-odoo-data` | → merge into `rg-ipai-odoo-dev` |
| `rg-ipai-data-dev` | → evaluate: merge into `rg-ipai-data-dev` or remove |
| `rg-ipai-agents-dev` | → **delete after VM cleanup** |
| `rg-ipai-devops` | → keep (DevOps tooling) |
| `rg-data-intel-ph` | → merge into `rg-ipai-ai-dev` |
| `rg-dbw-managed-ipai-dev` | → keep (Databricks auto-managed, do not touch) |

---

## 5. Front Door Route Cleanup

### Keep (Must-Have Backends)

| Origin Group | Backend | Health Probe | Keep |
|-------------|---------|-------------|------|
| `odoo-web` | `ipai-odoo-dev-web:80` | `/web/health` | **Yes** |
| `ocr` | `ipai-ocr-dev:8001` | `/health` | **Yes** |
| `mcp-gateway` | `ipai-mcp-dev:8766` | `/healthz` | **Yes** |
| `redirect` | 301 → odoo-web | — | **Yes** |

### Add (New Backends)

| Origin Group | Backend | Health Probe | Purpose |
|-------------|---------|-------------|---------|
| `copilot-gateway` | `ipai-copilot-gateway:8088` | `/health` | Ask Pulser + authenticated Pulser |
| `api-facade` | `ipai-api-facade:3000` | `/health` | Lead capture, demo booking |
| `website` | `ipai-website-dev:80` | `/` | Landing page (if kept separate) |

### Remove (Retired Backends)

| Origin Group | Backend | Reason |
|-------------|---------|--------|
| `n8n` | `:5678` | n8n retired |
| `plane` | `:3002` | Plane retired |
| `shelf` | `:3003` | Shelf retired |
| `crm` | `:3004` | Standalone CRM retired |
| `auth` | `:8080` | Keycloak retired |
| `superset` | `:8088` | Supplemental only — remove public route |

---

## 6. Cost Optimization Notes

| Resource | Current Tier | Recommendation |
|----------|-------------|----------------|
| Front Door | **Missing** | **Must provision** — P0 gap |
| PostgreSQL | General Purpose D2ds_v5 | Right-sized for Odoo; keep |
| Databricks SQL Warehouse | PRO Serverless | 10min auto-stop is good; keep |
| ACA | Consumption | Scale-to-zero for non-Odoo apps |
| OpenAI | Pay-as-you-go | Monitor token usage; set spending caps |
| Doc Intelligence | Pay-as-you-go | Low volume expected initially |

### Cleanup Completed (2026-03-25)

| Action | Status |
|--------|--------|
| Delete Supabase VM + disk + IP | **Done** — saves ~$140/mo |
| Delete 4 retired ACA apps (Keycloak, Plane, Shelf, CRM) | **Done** |
| Delete n8n (on VM) | **Done** with VM deletion |
| Remove deprecated PG `ipai-odoo-dev-pg` | **Previously done** |

---

## 7. Reconciliation Summary

| Category | Live Count | Target Count | Status |
|----------|-----------|-------------|--------|
| Resource Groups | 16 | 5 (prod) | Consolidate — many empty |
| Container Apps | 9 | 7-9 | Retired apps deleted; evaluate Superset/Login/Website |
| PostgreSQL Servers | 1 (`pg-ipai-odoo`) | 1 | **Aligned** |
| Key Vaults | 4 | 3-4 | **Aligned** (dev/staging/prod + Foundry auto) |
| Storage Accounts | 5 | 2-3 + Azure Files | Evaluate consolidation |
| VMs | 0 | 0 | **Aligned** — Supabase deleted |
| AI Services | 5 | 3 must-have + 2 optional | **Aligned** — evaluate Language + Vision |
| Managed Identities | 9 | 8-9 | **Aligned** |
| Front Door | 0 | 1 | **P0 gap** — must provision |
| Azure DNS Zone | 1 (provisioned) | 1 | **Provisioned** — needs NS delegation |
| Databricks | 1 workspace | 1 workspace | **Aligned** |
| AI Foundry | 1 workspace + 1 project | 1 + 1 | **Aligned** |

### Reconciliation Method

```bash
# Live query (requires az login)
python3 scripts/ci/azure_resource_reconcile.py

# Against snapshot
az graph query -q "Resources | project name, type, resourceGroup, location" --first 200 -o json > snapshot.json
python3 scripts/ci/azure_resource_reconcile.py --snapshot snapshot.json
```

---

*Reconciled against Azure Resource Graph (69 live resources, 2026-03-25).*
*Validation: `scripts/ci/azure_resource_reconcile.py` — run before any architecture doc update.*
*See `INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE.md` for the full architecture context.*
