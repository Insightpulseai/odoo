# Databricks + Fabric Role Split

## Architecture Decision

**Databricks is the canonical data-intelligence plane. Fabric/Power BI is the downstream consumption layer. PostgreSQL mirroring to Fabric is a tactical complement, not the primary analytics path.**

This aligns with the Microsoft/Databricks reference architecture documented at:
https://techcommunity.microsoft.com/blog/azurearchitectureblog/data-intelligence-end-to-end-with-azure-databricks-and-microsoft-fabric/4232621

---

## Canonical data flow

```text
Odoo PG (operational SoR)
  │
  ├──→ Databricks Lakehouse Federation (live read)
  │       │
  │       ├──→ Bronze (raw ingest / Delta tables)
  │       ├──→ Silver (cleaned, typed, joined)
  │       └──→ Gold (business-ready aggregates)
  │               │
  │               ├──→ Power BI / Copilot (via Databricks SQL endpoint)
  │               └──→ Fabric SQL analytics (via shortcut or Direct Lake)
  │
  └──→ Fabric Mirroring (tactical complement)
          │
          └──→ OneLake Delta tables → SQL analytics endpoint
                  (useful for quick operational dashboards,
                   not the governed transformation path)
```

---

## System roles

| System | Role | Authority |
|--------|------|-----------|
| **Odoo PostgreSQL** | Operational SoR (System of Record) | Canonical transactional truth |
| **Azure Databricks** | Data-intelligence plane | Governed lakehouse, medallion transformation, Unity Catalog |
| **Unity Catalog** | Governance layer | Schema, ACL, lineage, data products |
| **Databricks SQL Warehouse** | Serving layer | SQL access to gold tables for BI/AI consumers |
| **Fabric / Power BI** | Consumption layer | Analyst-facing reports, dashboards, Copilot |
| **Fabric Mirroring** | Tactical complement | Quick operational mirrors, not primary analytics path |
| **Azure Purview** | Metadata visibility (optional) | Broader enterprise catalog across Azure estate |

---

## What Fabric Mirroring is good for

- Quick operational dashboards over raw Odoo tables
- Exploring data before investing in a full Databricks pipeline
- Low-latency ad-hoc queries on recent transactional data
- Scenarios where the consumer is pure Fabric/Power BI without Databricks access

## What Fabric Mirroring is NOT

- Not a replacement for the Databricks medallion pipeline
- Not a governed transformation layer
- Not the canonical path for data products or curated analytics
- Not a substitute for Unity Catalog governance

---

## PostgreSQL mirroring decision

### Current state

| Database | Mirroring allowed | Purpose | Recommendation |
|----------|------------------|---------|----------------|
| `odoo` | Yes (selected) | Dev/active operational | Keep for tactical/pilot use |
| `odoo_staging` | No | Staging mirror | Enable only if staging analytics needed |
| `odoo_prod` | No | Production | Enable if Fabric-first BI is needed for ops dashboards |
| `postgres` | Visible | System database | Never mirror |

### Collation note

| Database | Collation | Risk |
|----------|-----------|------|
| `odoo` | `en_US.utf8` | Standard |
| `odoo_staging` | `en_US.utf8` | Standard |
| `odoo_prod` | `C` | Different — sorting/comparison behavior differs from dev/staging |

Normalize `odoo_prod` collation to `en_US.utf8` before treating cross-environment behavior as equivalent.

---

## Preferred target state

### Primary analytics path (Databricks-first)

```text
Odoo PG → Lakehouse Federation → Bronze → Silver → Gold → Databricks SQL → Power BI
```

- **Status**: OPERATIONAL (verified — all layers have data)
- **Governance**: Unity Catalog
- **Catalogs**: `dbw_ipai_dev` (managed), `odoo_erp` (federated)

### Secondary tactical path (Fabric mirroring)

```text
Odoo PG → Fabric Mirroring → OneLake → SQL analytics endpoint → Power BI
```

- **Status**: Fabric capacity active (F2), mirrored DB created, PG connection pending portal setup
- **Use case**: Quick operational dashboards, Copilot integration

### Not recommended

```text
Odoo PG → Fabric Mirroring → [skip Databricks] → Gold analytics
```

This bypasses governance, medallion quality, and Unity Catalog lineage.

---

## Replication vs Mirroring

| Concern | Solution | Current state |
|---------|----------|---------------|
| Analytics / BI | Fabric Mirroring or Databricks Federation | Both available |
| Read scaling (app traffic) | PG Read Replicas | Not configured |
| Failover / DR | PG HA / Virtual Endpoints | Not configured |
| Operational resilience | PG Replication topology | Single primary only |

Fabric mirroring does NOT provide operational resilience.

---

## Reference

- Microsoft/Databricks reference architecture: [Data Intelligence End-to-End](https://techcommunity.microsoft.com/blog/azurearchitectureblog/data-intelligence-end-to-end-with-azure-databricks-and-microsoft-fabric/4232621)
- Data platform audit: `docs/audits/data-platform/20260328/`
- E2E verification: Bronze (33 tables) → Silver (18) → Gold (26) — all verified with live data
