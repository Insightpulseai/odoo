# Deployment Spec — Finance Domain Intelligence

> **Status**: Ready
> **Benchmark**: Microsoft Business Process Solutions deployment pattern
> **Spec bundle**: `spec/finance-domain-intelligence/`

---

## 1. Workload Item

| Field | Value |
|-------|-------|
| **Solution name** | `finance-domain-intelligence` |
| **Solution type** | `composite` (semantic models + dashboards + agent data products) |
| **Owning repo** | `data-intelligence` |
| **Owning plane** | `data-intelligence` (Databricks + Power BI) |
| **Spec bundle** | `spec/finance-domain-intelligence/` |

## 2. Deployment Boundary

| Field | Value |
|-------|-------|
| **Workspace / project** | Databricks workspace `dbw-ipai-dev` (Unity Catalog) |
| **Resource group** | `rg-ipai-ai-dev` |
| **Capacity / SKU** | Databricks Standard tier, SQL Warehouse `e7d89eabce4c330c` |
| **Power BI workspace** | `ipai-finance` (to be created) |
| **Fabric capacity** | Shared with Databricks mirroring (if Fabric enabled) |

## 3. Required Roles

| Action | Required role | Identity |
|--------|--------------|----------|
| Enable Databricks workspace | RG Owner / Contributor on `rg-ipai-ai-dev` | Platform admin |
| Create Unity Catalog schemas | Catalog admin (`ipai`) | Pipeline service principal |
| Deploy DLT pipelines | Workspace Contributor | Pipeline service principal |
| Create Power BI workspace | Power BI Pro license + Fabric admin | Platform admin |
| Publish Power BI reports | Workspace Contributor (Power BI) | Pipeline service principal |
| Create orchestration connection | Contributor + PG data reader | Pipeline service principal |
| Onboard Odoo PG source | PG connection credentials (Key Vault) | Managed identity |
| Wire agent tools | Agent-platform Contributor | Pipeline service principal |

## 4. Target Region & Data Residency

| Field | Value |
|-------|-------|
| **Primary region** | `southeastasia` |
| **Business data location** | Databricks `dbw-ipai-dev` (Southeast Asia) |
| **Metadata / control plane** | Unity Catalog metastore (Southeast Asia) |
| **Power BI tenant** | Geography-level (metadata only) |
| **Data residency constraint** | Philippine financial data stays in SEA region |

## 5. Orchestration / Metadata Connection

> **Rule**: This connection MUST be provisioned and verified before any source onboarding.

| Field | Value |
|-------|-------|
| **Connection type** | Azure Database for PostgreSQL (Fabric Mirroring) + Unity Catalog |
| **Connection target** | `pg-ipai-odoo.postgres.database.azure.com` / database: `odoo` |
| **Connection identity** | Managed identity (server-level) |
| **Connection ID** | To be captured after Fabric Mirroring enablement |
| **Purpose** | Bronze-layer ingestion from Odoo PG, extraction state tracking |

### Pre-onboarding checklist

- [ ] `pg-ipai-odoo` Fabric Mirroring enabled (server restart completed)
- [ ] Managed identity has `azure_pg_admin` role on target database
- [ ] Connection ID captured from Fabric mirroring configuration
- [ ] Connection health verified (`SELECT 1` from mirrored endpoint)
- [ ] Unity Catalog schema `ipai.finance` created

## 6. Source Onboarding Sequence

> **Rule**: Sources are onboarded in order. Each source depends on the orchestration connection being live.

| Order | Source | Method | Landing | Prerequisites |
|-------|--------|--------|---------|---------------|
| 1 | Odoo CE 19 (Azure PG) | Fabric Mirroring from `pg-ipai-odoo` | Bronze (`ipai.finance_bronze`) | Orchestration connection live, mirroring active |
| 2 | BSP exchange rates | Scheduled API import (n8n → Bronze) | Bronze (`ipai.finance_bronze.exchange_rates`) | Source 1 complete |
| 3 | ECB exchange rates | Scheduled API import (n8n → Bronze) | Bronze (`ipai.finance_bronze.ecb_rates`) | Fallback for BSP |

### Odoo tables mirrored (minimum viable)

| Odoo table | Domain | Used by |
|------------|--------|---------|
| `account_move` | GL, AP, AR | Journal entries |
| `account_move_line` | GL, AP, AR | Posting line items |
| `account_account` | GL | Chart of accounts |
| `account_journal` | GL | Journal definitions |
| `account_fiscal_year` | GL | Fiscal periods |
| `res_currency` | GL, AP, AR | Currency master |
| `res_currency_rate` | GL, AP, AR | Historical rates |
| `res_partner` | AP, AR | Customer/supplier |
| `res_company` | GL, AP, AR | Company master |
| `account_payment` | AP, AR | Payment documents |

## 7. Deployment Sequence

```text
1.  Verify required roles (Databricks admin, PG admin, Power BI Pro)
2.  Verify pg-ipai-odoo Fabric Mirroring enabled
3.  Create Unity Catalog schema: ipai.finance_bronze, ipai.finance_silver, ipai.finance_gold
4.  Create orchestration connection (verify Fabric Mirroring → Bronze landing)
5.  Verify orchestration connection health (SELECT 1 on mirrored tables)
6.  Deploy DLT pipeline: Bronze → Silver (normalize, deduplicate, type)
7.  Deploy DLT pipeline: Silver → Gold (star schema, surrogate keys, hierarchies)
8.  Verify Gold-layer reconciliation against Odoo GL totals
9.  Onboard BSP/ECB exchange rate sources
10. Create Power BI workspace ipai-finance
11. Publish Power BI reports (Trial Balance, AP Aging, AR Aging, etc.)
12. Wire Pulser agent tools to Gold-layer semantic model endpoints
13. Run post-deploy verification suite
14. Publish deployment attestation
```

## 8. Post-Deploy Verification

| Check | Method | Pass criteria |
|-------|--------|--------------|
| Orchestration connection health | `SELECT count(*) FROM ipai.finance_bronze.account_move` | Row count > 0 |
| Bronze freshness | `MAX(mirrored_at) FROM bronze metadata` | Within 24h of Odoo source |
| Silver deduplication | `COUNT(*) silver = COUNT(DISTINCT key) bronze` | No duplicates |
| Gold GL reconciliation | `SUM(debit) - SUM(credit)` Gold vs Odoo | Delta < 0.01 |
| Gold hierarchy completeness | Every account reachable via drill-up | 100% coverage |
| Currency conversion accuracy | Spot-check against BSP published rate | Match to 4 decimal places |
| Power BI report render | Power BI REST API `GetReports` | All reports return `200` |
| Agent grounding test | Ask Pulser "Trial balance as of today" | Response cites GL semantic model |

## 9. Rollback

| Field | Value |
|-------|-------|
| **Rollback target** | Previous DLT pipeline version + previous Power BI report version |
| **Rollback method** | Redeploy previous DLT pipeline; republish previous Power BI .pbix |
| **Data rollback** | Append-only — no data rollback needed. Gold layer rebuilds from Silver. |
| **Agent rollback** | Revert tool endpoint to previous semantic model version |

## 10. Post-Deploy Next Steps

- [ ] Validate freshness SLA after first full 24h refresh cycle
- [ ] Enable Databricks SQL alert for GL reconciliation drift > 0.01
- [ ] Enable Power BI scheduled refresh (daily, aligned to Odoo close)
- [ ] Wire Pulser finance tools: `get_trial_balance`, `get_ap_aging`, `get_ar_aging`
- [ ] Update domain solution registry in `ssot/platform/domain_solutions.yaml`
- [ ] Schedule quarterly semantic model version review (`YYYY.Q`)
