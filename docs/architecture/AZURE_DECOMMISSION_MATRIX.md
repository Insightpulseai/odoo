# Azure Decommission Matrix — Post-Normalization

> **Date**: 2026-03-22
> **Status**: EXECUTED — `rg-ipai-dev` deleted 2026-03-22 (was empty, deletion confirmed via `az group show`)
> **Source**: `infra/ssot/azure/resources.yaml`, `odoo/odoo/infra/ssot/azure/rg-normalization-matrix.yaml`

---

## DELETE — Legacy `rg-ipai-dev` (16 resources)

Entire resource group can be deleted after stabilization hold expires.
All runtime resources are duplicated in canonical `rg-ipai-dev-odoo-runtime`.

| # | Resource | Type | Action | Notes |
|---|----------|------|--------|-------|
| 1 | `ipai-odoo-dev-web` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 2 | `ipai-odoo-dev-worker` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 3 | `ipai-odoo-dev-cron` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 4 | `ipai-auth-dev` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 5 | `ipai-copilot-gateway` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 6 | `ipai-crm-dev` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 7 | `ipai-mcp-dev` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 8 | `ipai-ocr-dev` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 9 | `ipai-plane-dev` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 10 | `ipai-shelf-dev` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 11 | `ipai-superset-dev` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 12 | `ipai-website-dev` | Container App | **DELETE** | Replaced in rg-ipai-dev-odoo-runtime |
| 13 | `ipai-odoo-dev-env` | ACA Environment | **DELETE** | Replaced by new env in rg-ipai-dev-odoo-runtime |
| 14 | `ipai-branding-install` | Container App Job | **DELETE** | Legacy one-shot job |
| 15 | `ipai-odoo-dev-wave1` | Container App Job | **DELETE** | Legacy migration job |
| 16 | `ipai-odoo-install` | Container App Job | **DELETE** | Legacy install job |

**Pre-delete checklist:**

- [ ] Confirm all 13 canonical apps in `rg-ipai-dev-odoo-runtime` are healthy
- [ ] Confirm `erp.insightpulseai.com` resolves to new ACA env (salmontree domain)
- [ ] Confirm Front Door origin groups point to `rg-ipai-dev-odoo-runtime` apps
- [ ] Confirm no active DNS or Front Door routes target the old `ipai-odoo-dev-env`
- [ ] Confirm `ipai-odoo-dev-pg` (PostgreSQL) has been moved to `rg-ipai-dev-odoo-data` or is not in `rg-ipai-dev`

**Execution:**

```bash
# Safest: delete individual resources first, then the RG
az group delete --name rg-ipai-dev --yes --no-wait
```

---

## KEEP — Canonical Runtime (`rg-ipai-dev-odoo-runtime`)

All 13 normalized ACA resources. This is the live production lane.

| # | Resource | Type | Status |
|---|----------|------|--------|
| 1 | `ipai-odoo-dev-web` | Container App | **KEEP** — Odoo HTTP frontend |
| 2 | `ipai-odoo-dev-worker` | Container App | **KEEP** — Odoo background worker |
| 3 | `ipai-odoo-dev-cron` | Container App | **KEEP** — Odoo scheduled jobs |
| 4 | `ipai-auth-dev` | Container App | **KEEP** — Keycloak SSO (transitional to Entra) |
| 5 | `ipai-copilot-gateway` | Container App | **KEEP** — Copilot gateway |
| 6 | `ipai-crm-dev` | Container App | **KEEP** — CRM service |
| 7 | `ipai-mcp-dev` | Container App | **KEEP** — MCP coordinator |
| 8 | `ipai-ocr-dev` | Container App | **KEEP** — OCR service |
| 9 | `ipai-plane-dev` | Container App | **KEEP** — Plane PM |
| 10 | `ipai-shelf-dev` | Container App | **KEEP** — Shelf service |
| 11 | `ipai-superset-dev` | Container App | **KEEP** — Superset BI |
| 12 | `ipai-website-dev` | Container App | **KEEP** — Website |
| 13 | `ipai-odoo-dev-env` | ACA Environment | **KEEP** — salmontree domain |

---

## KEEP — Canonical Platform (`rg-ipai-dev-platform`)

| Resource | Type | Status |
|----------|------|--------|
| `kv-ipai-dev` | Key Vault | **KEEP** — shared secrets |
| `ipai-odoo-dev-kv` | Key Vault | **KEEP** — Odoo-specific secrets |
| `cripaidev` | Container Registry | **KEEP** — shared ACR |
| `ipaiodoodevacr` | Container Registry | **KEEP** — Odoo ACR |
| `ipaiwebacr` | Container Registry | **REVIEW** — consolidation candidate |

---

## KEEP — Canonical Data (`rg-ipai-dev-odoo-data`)

| Resource | Type | Status |
|----------|------|--------|
| `ipai-odoo-dev-pg` | PostgreSQL Flexible Server | **KEEP** — Odoo database |
| Storage accounts | Azure Storage | **KEEP** — filestore |

---

## KEEP — Shared Infrastructure (`rg-ipai-shared-dev`)

| Resource | Type | Status |
|----------|------|--------|
| `ipai-fd-dev` | Front Door | **KEEP** — global edge/TLS |
| `ipaiDevWafPolicy` | WAF Policy | **KEEP** — security |
| `cripaidev` | Container Registry | **KEEP** (if not moved to platform RG yet) |
| `id-ipai-agents-dev` | Managed Identity | **KEEP** — agent workloads |

---

## KEEP — Shared Observability (`rg-ipai-shared-observability` / `rg-ipai-shared-dev`)

| Resource | Type | Status |
|----------|------|--------|
| `law-ipai-dev` | Log Analytics | **KEEP** — centralized logging |
| `appi-ipai-dev` | App Insights | **KEEP** — APM |
| Smart Detection action group | Action Group | **KEEP** — managed |

---

## KEEP — AI Plane (`rg-ipai-ai-dev`)

| Resource | Type | Status |
|----------|------|--------|
| `oai-ipai-dev` | Azure OpenAI | **KEEP** |
| `docai-ipai-dev` | Document Intelligence | **KEEP** |
| `vision-ipai-dev` | Computer Vision | **KEEP** |
| `lang-ipai-dev` | Language | **KEEP** |
| `srch-ipai-dev` | AI Search | **KEEP** |
| `dbw-ipai-dev` | Databricks | **KEEP** — cannot move |
| `vnet-ipai-databricks` | VNet | **KEEP** |
| NSGs (3) | Network Security Groups | **KEEP** |
| Private DNS zone | Private DNS | **KEEP** |
| `stipaidevlake` | ADLS Gen2 | **KEEP** — medallion lake |

---

## KEEP — Foundry (`rg-data-intel-ph`)

| Resource | Type | Status |
|----------|------|--------|
| `data-intel-ph-resource` | AI Hub | **KEEP** — cannot move |
| `data-intel-ph` | Foundry Project | **KEEP** |

---

## KEEP — Databricks Managed (`rg-dbw-managed-ipai-dev`)

| Resource | Type | Status |
|----------|------|--------|
| `dbmanagedidentity` | Managed Identity | **KEEP** — Databricks-controlled |
| `unity-catalog-access-connector` | Access Connector | **KEEP** |
| `dbstoragew6tn3uhg4bluy` | Storage Account | **KEEP** — DBFS root |

---

## KEEP — DevOps (`rg-ipai-devops`)

| Resource | Type | Status |
|----------|------|--------|
| `ipai-build-pool` | Managed DevOps Pool | **KEEP** |
| `ipai-devcenter` | Dev Center | **KEEP** |
| `ipai-devcenter-project` | Dev Center Project | **KEEP** |

---

## KEEP — Agents / Supabase VM (`rg-ipai-agents-dev`)

| Resource | Type | Status |
|----------|------|--------|
| `vm-ipai-supabase-dev` | Virtual Machine | **KEEP** — self-hosted Supabase |
| `vm-ipai-supabase-dev_OsDisk_*` | OS Disk | **KEEP** — VM-managed |
| `vm-ipai-supabase-devNSG` | NSG | **KEEP** — VM networking |
| `vm-ipai-supabase-devPublicIP` | Public IP | **KEEP** — 4.193.100.31 |
| `vm-ipai-supabase-devVMNic` | NIC | **KEEP** — VM networking |
| `vm-ipai-supabase-devVNET` | VNet | **KEEP** — VM networking |

### Follow-up validation candidate

| Resource | Type | Status |
|----------|------|--------|
| `id-ipai-aca-dev` | Managed Identity | **REVIEW** — verify no new ACA references it |

**Validation query:**

```bash
# Check if any ACA in the new runtime RG still references this identity
az containerapp list -g rg-ipai-dev-odoo-runtime \
  --query "[].{name:name, identities:identity.userAssignedIdentities}" -o table
```

If no ACA references `id-ipai-aca-dev`, it can be deleted in a follow-up pass.

---

## Already Deleted (Phase 4 early, 2026-03-20)

| Resource | RG | Type | Deleted |
|----------|----|------|---------|
| `debug-odoo-ep` | `rg-ipai-agents-dev` | Container Instance | 2026-03-20 |
| `odoo-init` | `rg-ipai-agents-dev` | Container App Job | 2026-03-20 |
| `cae-ipai-dev` | `rg-ipai-agents-dev` | ACA Environment | 2026-03-20 |

---

## Also review post-hold (`rg-ipai-data-dev`)

| Resource | Type | Status |
|----------|------|--------|
| `pg-ipai-dev` | PostgreSQL Flexible Server | **REVIEW** — assess if still needed after `ipai-odoo-dev-pg` is canonical |

Per normalization matrix, `rg-ipai-data-dev` is a Phase 4 deletion candidate after `pg-ipai-dev` assessment.

---

## Summary

| Action | Resource Group | Count | When |
|--------|---------------|-------|------|
| **DELETE** | `rg-ipai-dev` | 16 | After 2026-03-23 hold + pre-delete checklist |
| **REVIEW** | `rg-ipai-data-dev` | 1 (pg-ipai-dev) | After pg assessment |
| **REVIEW** | `rg-ipai-agents-dev` | 1 (id-ipai-aca-dev) | After ACA identity audit |
| **REVIEW** | `rg-ipai-dev-platform` | 1 (ipaiwebacr) | ACR consolidation pass |
| **KEEP** | All other RGs | ~50+ | Canonical target layout |
