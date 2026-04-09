# Data Intelligence

> **Benchmark**: Databricks + Fabric data intelligence
> **Canonical source**: `data-intelligence/docs/`

## Purpose

Cross-repo entry point for the data intelligence documentation family. Full content lives in the `data-intelligence/` directory that owns the executable truth.

## Doc Ownership

| Topic | Canonical Location | Owner |
|---|---|---|
| Data intelligence model (full) | [data-intelligence/docs/index.md](../../../data-intelligence/docs/index.md) | `data-intelligence` |
| Databricks + Fabric reference | `data-intelligence/docs/data-intelligence/databricks-fabric-reference.md` | `data-intelligence` |
| Lakehouse and governance | `data-intelligence/docs/data-intelligence/lakehouse-and-governance.md` | `data-intelligence` |
| Ingestion patterns | `data-intelligence/docs/data-intelligence/realtime-and-batch-ingestion.md` | `data-intelligence` |
| Semantic consumption and BI | `data-intelligence/docs/data-intelligence/semantic-consumption-and-bi.md` | `data-intelligence` |
| Data-AI integration | `data-intelligence/docs/data-intelligence/data-ai-integration.md` | `data-intelligence` |

## Benchmark Position

| Databricks/Fabric Capability | IPAI Equivalent | Status |
|---|---|---|
| Databricks workspace | `dbw-ipai-dev` | Operational |
| Unity Catalog | `ipai_dev` catalog | Scaffold |
| DLT pipelines | Pipeline definitions | Scaffold |
| Medallion architecture | Bronze → Silver → Gold → Platinum | Design |
| Fabric mirroring | `pg-ipai-odoo` → OneLake | Design |
| Power BI consumption | Power BI (primary BI) | Scaffold |
| Superset (supplemental) | `ipai-superset-dev` | Operational |

## Key Rules

- **Power BI** is the primary mandatory BI surface. Superset is supplemental only.
- **Databricks** is the mandatory governed transformation plane. Fabric complements but never replaces Databricks engineering.
- **Supabase ETL is deprecated.** Use Databricks JDBC extract instead.

## Related Documents

- `docs/architecture/ODOO_ON_AZURE_REFERENCE_ARCHITECTURE.md` — Layer 3
- `docs/odoo-on-azure/reference/doc-authority.md` — ownership model
- `lakehouse/` — legacy code (migration target: `data-intelligence/`)

---

*Created: 2026-04-05 | Version: 1.0*
