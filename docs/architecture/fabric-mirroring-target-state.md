# Fabric Mirroring — Target State (IPAI)

> **Locked:** 2026-04-15
> **Authority:** this file (canonical Fabric mirroring posture for IPAI)
> **Fabric capacity:** `fcipaidev` (trial — expires ~2026-05-20 per memory)
> **Companions:**
> - [`docs/architecture/databricks-one-and-workspace-operating-model.md`](./databricks-one-and-workspace-operating-model.md) — workspace operating model
> - [`docs/skills/databricks-ipai-grounded.md`](../skills/databricks-ipai-grounded.md) — Databricks grounded setup
> - [`docs/skills/azure-postgresql-ipai-grounded.md`](../skills/azure-postgresql-ipai-grounded.md) — PG grounded setup
>
> **Microsoft refs:**
> - [Mirroring overview](https://learn.microsoft.com/fabric/mirroring/overview)
> - [Mirroring from Azure Postgres Flex (GA)](https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql)
> - [Mirroring from Azure Databricks Unity Catalog](https://learn.microsoft.com/fabric/mirroring/azure-databricks)

---

## 0. Canonical contract

```
Fabric capacity (current)         = fcipaidev (TRIAL — expires ~2026-05-20)
Fabric workspace                  = (per capacity, managed by capacity admin)

Mirror path #1 — transactional    : Azure Postgres Flex  → Fabric (Database mirroring)
                                    Replicates full data + schema into OneLake as Delta
                                    Continuous, near-real-time (~15s publish cadence)

Mirror path #2 — analytics        : Azure Databricks UC  → Fabric (Metadata mirroring)
                                    Shortcuts only — no data movement
                                    Metadata sync (schemas + tables, not data)

Anti-pattern                      : Double-mirror the same data via both paths
                                    (Use PG→Fabric for transaction truth; UC→Fabric for governed analytics;
                                     if both needed, route PG→Databricks UC→Fabric, not PG→Fabric AND UC→Fabric)
```

---

## 1. Two mirroring paths — different semantics

| Aspect | PG Flex → Fabric (Database mirroring) | Databricks UC → Fabric (Metadata mirroring) |
|---|---|---|
| **What moves** | Full data + schema, continuously | Only catalog structure (metadata); data stays in UC |
| **Storage in Fabric** | Delta tables in OneLake (actual copy) | Shortcut references (no copy) |
| **Latency** | ~15s publish cadence, near-real-time | Propagation "a few seconds to several minutes" per MS Learn |
| **Fabric analytics experiences** | SQL analytics endpoint (read-only T-SQL), Power BI Direct Lake, Spark notebooks | Same: SQL analytics endpoint + Power BI + Spark |
| **Source load** | Higher during initial snapshot (CPU + IOPS); WAL growth from long transactions | Minimal — just catalog queries |
| **Source DDL handling** | Most DDL auto-propagates; some exceptions (see MS limitations page) | Schema/table additions + deletions auto-sync (if enabled); materialized views + streaming tables NOT displayed; external non-Delta tables NOT displayed |
| **Source GA status** | ✅ GA for PG Flex | ✅ GA for Databricks UC |
| **Cost (data)** | Compute free; OneLake storage free up to 1 TB per CU | No data storage cost — shortcuts only |
| **Cost (queries)** | Paid (OneLake compute, Power BI, Spark rates) | Paid (SQL endpoint, Power BI via Direct Lake) |

**Decision rule for IPAI:**

- **Operational/transactional data** (invoices, payments, GL, CRM, PPM) → **PG → Fabric** (database mirroring). Keeps raw transaction truth queryable in Fabric without ETL.
- **Curated/governed analytics data** (gold-layer metrics, semantic tables, cross-source joins) → **UC → Fabric** (metadata mirroring). Single version of truth in UC, consumed by Fabric via shortcuts.
- **Never both for the same table.** If gold-layer UC tables derive from PG data, the chain is:
  ```
  PG → Databricks (Lakeflow SDP ingests) → UC gold tables → Fabric shortcut
  ```
  not
  ```
  PG → Fabric (mirror) AND UC → Fabric (mirror)    ← DOUBLE SOURCE; diverges
  ```

---

## 2. PG Flex source requirements — applied to IPAI

Per the MS Learn PG mirroring page:

| Requirement | MS doc | IPAI status |
|---|---|---|
| **Compute tier**: General Purpose OR Memory Optimized. **Burstable NOT supported.** | ✅ confirmed | `ipai-odoo-dev-pg` (old Burstable) was deprecated for exactly this reason |
| **PG version**: supports current PG Flex versions (v13+) | — | Both candidate servers on PG 16 ✅ |
| **Network**: publicly accessible OR network-isolated (private endpoint / VNet). If private + doesn't allow Azure services, need VNet data gateway. | ✅ both modes supported | Public works (sponsored server); private-firewalled works (old server) |
| **High availability**: supported — replication continues across failover | ✅ | HA is optional, not required |
| **Logical replication**: required (implicit — mirroring uses logical decoding) | source DB parameter | Must verify `wal_level=logical` + `max_replication_slots` on chosen source |
| **User/grants**: replication-capable role required on source | tutorial page | Must be set on whichever server is canonical |
| **WAL monitoring**: long transactions can fill WAL — monitor storage | ⚠️ ops concern | Add alert rule post-mirror setup |

**Cross-subscription:** not explicitly prohibited in the docs. Fabric capacity and source PG can be in different subs — the connection is made via server endpoint + credentials, not via ARM-scoped RBAC on the source. But for operational clarity, **consolidate on one sub** (the sponsored sub).

---

## 3. IPAI's two PG servers — mirror qualification

Ground truth as of 2026-04-15 (`az postgres flexible-server show` + `az network private-endpoint list`):

| Attribute | `pg-ipai-odoo` (OLD SUB) | `pg-ipai-odoo-dev` (SPONSORED) |
|---|---|---|
| Sub | Azure subscription 1 (`536d8cf6…`) | Microsoft Azure Sponsorship (`eba824fb…`) |
| RG | `rg-ipai-dev-odoo-data` | `rg-ipai-dev-data-sea` |
| Tier / SKU | GP / `Standard_D2ds_v5` | GP / `Standard_D4s_v3` |
| Storage | 32 GB | 128 GB |
| HA | ZoneRedundant | Disabled |
| Public access | **Disabled** | **Enabled** |
| Private endpoints | **2× Approved on `vnet-ipai-dev/snet-pe`** (`pe-pg-ipai-odoo…`) | None |
| Admin user | `odoo_admin` | (same convention) |
| PG version / TLS | 16 / TLS ≥ 1.2 enforced | 16 / TLS ≥ 1.2 enforced |
| DBs | `odoo`, `odoo_staging`, `odoo_dev` | same three |
| **Shape** | **Production-shape** — HA + PE isolation | **Dev-shape** — public, no HA |
| **Mirror-qualified?** | ✅ Yes (GP, PG 16, PE-connected — mirroring supports both modes) | ✅ Yes (GP, PG 16, public) |

Both qualify per MS reqs. The two servers are **intentionally different shapes**, not drift.

---

## 4. Canonical PG decision — OPEN QUESTION

I've over-driven this decision twice. Leaving it as a direct question for the owner.

**Facts (both verified from portal + CLI):**

| Fact | `pg-ipai-odoo` | `pg-ipai-odoo-dev` |
|---|---|---|
| Subscription | Azure subscription 1 (old) | Microsoft Azure Sponsorship ✅ |
| Created | (pre-dating this audit) | **2026-04-13 01:33:37 UTC** (very recent — 2 days before this doc) |
| Shape | HA ZoneRedundant + 2 Approved PEs on `vnet-ipai-dev/snet-pe` | No HA, no PE, public access enabled |
| Admin login | `odoo_admin` | **`ipaiadmin`** |
| PG version | 16 (patch unknown) | 16.13 |
| SKU / storage | GP `Standard_D2ds_v5`, 32 GB | GP `Standard_D4s_v3`, 16 GiB RAM, 128 GB |
| Fabric mirror | Per memory "ACTIVE" (needs verification — Fabric capacity not visible via ARM) | Not enabled; "Fabric mirroring" menu present on resource |
| Virtual endpoint | — | Not enabled |

**Two plausible interpretations:**

**(a) `pg-ipai-odoo-dev` is the ADR-002 migration target in-progress.** The 2026-04-13 provisioning date + sponsored sub + fresh admin login + bigger SKU fits a cross-sub redeploy. Next steps would be: cutover data, enable HA, add PE, wire Fabric mirror, decom old server, rename drops `-dev`. Under this reading, both servers are transient states of one canonical production-shape PG.

**(b) `pg-ipai-odoo-dev` is a genuine dev environment.** Separate admin user, public access, no HA by design; `pg-ipai-odoo` stays as the canonical production-shape server and gets its own cross-sub path. Under this reading, we maintain two distinct servers in target state (dev + prod-shape), named accordingly.

**Question for owner:** (a) or (b)?

The answer drives:
- Whether `pg-ipai-odoo-dev` ever gets HA/PE/mirror enabled
- Whether `pg-ipai-odoo` is decommissioned after data migration or kept
- Whether memory carries one PG entry or two
- Which server is the Fabric mirror source (current memory claim is `pg-ipai-odoo`; needs to stay valid through the move)
- Final naming (`pg-ipai-odoo` post-rename? `pg-ipai-odoo-prod` alongside `pg-ipai-odoo-dev`?)

Until this is answered, I'm not updating `ssot/agents/runtime_registry.yaml` or memory, and not issuing firewall/PE changes.

**Dev access path (independent of the decision above):**

- **Direct-from-local:** `pg-ipai-odoo-dev` (public + firewall allowlist) with VS Code `ms-ossdata.vscode-pgsql` + Entra auth. Admin user `ipaiadmin`.
- **VNet-side (for `pg-ipai-odoo`):** requires Bastion host, dev container on `vnet-ipai-dev`, or ACA exec from an app in that VNet. Not reachable from a local laptop without a tunnel. Admin user `odoo_admin`.
- The earlier "private-endpoint-only blocker" claim was misdiagnosed — there was never a blocker for dev-from-local; we were pointing at the wrong server.

---

## 5. Fabric capacity — time-sensitive

Per memory: Fabric trial (`fcipaidev`) expires ~2026-05-20.

**Paths forward:**

| Option | Action | Decision window |
|---|---|---|
| **(a) Procure F-SKU capacity** | Azure → Fabric → Create capacity (F2+ minimum for mirroring) on sponsored sub | Decide by 2026-05-01 to avoid trial-expiry churn |
| **(b) Let trial expire + re-procure later** | Mirror config lost; redo after procurement | Only if mirroring isn't on the critical path |
| **(c) Switch primary analytics surface to Databricks-only** | UC is the governed layer; skip Fabric mirror entirely; Power BI consumes UC directly via Databricks connector | Only if the Fabric mirror latency/cost comparison favors native UC path |

**Recommendation: (a)** — F2 is cheap (~USD 260/mo) and keeps both mirror paths alive. Option (c) is tempting but loses the cross-database T-SQL queries across PG + UC that mirroring enables in one pane.

---

## 6. Mirroring rollout sequence

Ordered by dependency:

```
Step 1. Consolidate PG on sponsored sub (this doc §4 decision)
        - Confirm pg-ipai-odoo-dev is canonical
        - Decom pg-ipai-odoo (old sub) per ADR-002 revised plan
        - Update ssot/agents/runtime_registry.yaml + memory

Step 2. Enable logical replication on pg-ipai-odoo-dev
        - az postgres flexible-server parameter set --name wal_level --value LOGICAL
        - Restart server (wal_level change requires restart)
        - Verify max_replication_slots >= 10

Step 3. Procure Fabric F-SKU capacity before trial expiry (2026-05-20)
        - F2 on sponsored sub, Southeast Asia region (co-locate with PG)

Step 4. Create Fabric workspace on new capacity
        - Workspace name: ws-ipai-dev (or similar)
        - Assign to F-SKU capacity

Step 5. Configure mirror path #1 — PG → Fabric
        - Fabric workspace → + New → Mirrored database → Azure Database for PostgreSQL
        - Source: pg-ipai-odoo-dev.postgres.database.azure.com
        - DB: odoo (canonical) first; odoo_staging + odoo_dev later if useful
        - Tables: start narrow (account_move, account_payment, res_partner, crm_lead)
        - Validate snapshot completes; validate ~15s incremental lag

Step 6. Configure mirror path #2 — Databricks UC → Fabric
        - Fabric workspace → + New → Mirrored Azure Databricks Catalog
        - Source: dbw-ipai-dev workspace, catalog ppm
        - Auto-sync: enabled for ppm.gold (consumer schema)
        - Exclude bronze + silver (non-consumer)

Step 7. Build a cross-source Power BI report
        - Uses both mirrors in a single Direct Lake model
        - Validates the "both paths live" target state

Step 8. Lock monitoring
        - WAL size alert on pg-ipai-odoo-dev
        - Mirror lag alert in Fabric
        - Capacity unit (CU) utilization alert on F-SKU
```

---

## 7. What this doc does NOT cover

- **Fabric mirroring CI/CD** — see [Mirroring REST API docs](https://learn.microsoft.com/fabric/mirroring/mirrored-database-rest-api) when automating
- **DDL limitations** — see the per-source limitations pages (PG: `azure-database-postgresql-limitations`, UC: `azure-databricks-limitations`)
- **Cross-tenant sharing** — OneLake external data sharing is a separate doctrine if IPAI ever publishes data to customer tenants
- **Backup / DR posture for mirrored data** — mirrored data is derived; source PG + UC are the authoritative backup targets

---

## 8. Bottom line

```
Two mirror paths serve two needs:
  PG → Fabric     = transaction data into OneLake (operational truth, analytics-ready)
  UC → Fabric     = governed analytics tables as shortcuts (single source, no copy)

IPAI action this sprint:
  1. Pick pg-ipai-odoo-dev (sponsored) as canonical  ← decision gate
  2. Procure Fabric F2 before trial expires 2026-05-20
  3. Enable logical replication + wire mirror #1
  4. Wire mirror #2 after ppm.gold has real tables
```

---

## 9. References

Internal:
- [`docs/architecture/databricks-one-and-workspace-operating-model.md`](./databricks-one-and-workspace-operating-model.md)
- [`docs/skills/databricks-ipai-grounded.md`](../skills/databricks-ipai-grounded.md)
- [`docs/skills/azure-postgresql-ipai-grounded.md`](../skills/azure-postgresql-ipai-grounded.md)
- [`ssot/agents/runtime_registry.yaml`](../../ssot/agents/runtime_registry.yaml) — needs refresh
- Memory: `project_fabric_finance_ppm`, `reference_fabric_mirroring_docs`, `reference_databricks_fabric_repos`

External (Microsoft Learn):
- [Mirroring overview](https://learn.microsoft.com/fabric/mirroring/overview)
- [PG Flex mirroring (GA)](https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql)
- [PG Flex mirroring tutorial](https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql-tutorial)
- [PG Flex mirroring limitations](https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql-limitations)
- [Databricks UC mirroring](https://learn.microsoft.com/fabric/mirroring/azure-databricks)
- [Databricks UC mirroring tutorial](https://learn.microsoft.com/fabric/mirroring/azure-databricks-tutorial)
- [Fabric pricing](https://azure.microsoft.com/pricing/details/microsoft-fabric/)

---

*Last updated: 2026-04-15*
