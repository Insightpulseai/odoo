# Knowledge Base Crosswalk: Upstream Bundle Examples to Our Bundles

> Maps each upstream `databricks/bundle-examples` template to our bundle implementation,
> documenting what was adopted, adapted, and intentionally skipped.

---

## 1. default_python -> foundation_python

### Source: `databricks/bundle-examples/default_python/`

| Upstream Element | Our Adaptation | Status |
|-----------------|---------------|--------|
| `databricks.yml` with single target | Multi-target (dev/staging/prod) with catalog variables | Adapted |
| `pyproject.toml` with setuptools | Switched to hatchling (consistent with existing `infra/databricks/`) | Adapted |
| `src/<package>/` layout | `src/ipai_data_intelligence/` with domain-specific subpackages | Adapted |
| `tests/` with pytest | Identical pattern, added fixtures directory | Adopted |
| `resources/` for jobs | Identical pattern, split into `jobs/` and `pipelines/` subdirs | Adopted |
| Wheel artifact | Identical, used for cross-bundle library sharing | Adopted |
| Single `main.py` notebook | Not used; we use Python package imports in DLT notebooks | Skipped |
| GitHub Copilot integration | Not applicable to our CI setup | Skipped |

### Key Variables Added (not in upstream)

```yaml
variables:
  catalog:        # Unity Catalog name per environment
  schema_bronze:  # Medallion layer schema names
  schema_silver:
  schema_gold:
  schema_platinum:
```

### Key Target Additions (not in upstream)

```yaml
targets:
  prod:
    run_as:
      service_principal_name: finance-ppm-service-principal
    permissions:
      - level: CAN_VIEW
        group_name: data-engineers
      - level: CAN_MANAGE
        group_name: platform-admins
```

---

## 2. lakeflow_pipelines_python -> lakeflow_ingestion

### Source: `databricks/bundle-examples/lakeflow_pipelines_python/`

| Upstream Element | Our Adaptation | Status |
|-----------------|---------------|--------|
| DLT pipeline resource definition | Adapted for Bronze-only scope (ingestion, not full medallion) | Adapted |
| Python DLT notebook pattern | Will use for JDBC and REST extractors | Planned |
| `pyproject.toml` with DLT deps | Added `httpx` for REST API extraction | Adapted |
| Pipeline `catalog` and `target` config | Uses our `${var.catalog}.${var.schema_bronze}` pattern | Adapted |
| Photon acceleration | Enabled for prod target | Adopted |
| Auto-scaling cluster config | Adopted for DLT pipeline clusters | Adopted |
| Streaming tables | Deferred (batch-first per constitution Principle 3) | Deferred |
| LakeFlow Connect sources | Will use for JDBC extraction from Odoo PostgreSQL | Planned |

### Ingestion Sources (our additions)

| Source | Protocol | Target Schema |
|--------|---------|--------------|
| Odoo PostgreSQL | JDBC via LakeFlow Connect | `${catalog}.bronze` |
| External REST APIs | HTTP via Python extractors | `${catalog}.bronze` |
| File uploads (CSV/JSON) | Auto Loader (cloud files) | `${catalog}.bronze` |

---

## 3. default_sql -> sql_warehouse

### Source: `databricks/bundle-examples/default_sql/`

| Upstream Element | Our Adaptation | Status |
|-----------------|---------------|--------|
| SQL file tasks in jobs | Adopted for mart refresh and schema creation | Adopted |
| `warehouse_id` variable | Identical usage | Adopted |
| SQL file organization | Extended with `schemas/`, `marts/`, `serving/` subdirectories | Adapted |
| Dashboard resources | Will use for supplemental Lakeview dashboards | Planned |
| Single SQL file pattern | Extended to multi-file task chains with dependencies | Adapted |
| Query parameters | Will use `${var.catalog}` for catalog substitution | Planned |

### SQL Layer Mapping (our addition)

| Directory | Medallion Layer | Purpose |
|-----------|---------------|---------|
| `src/sql/schemas/` | All | DDL: CREATE SCHEMA IF NOT EXISTS |
| `src/sql/marts/` | Gold | Business aggregates, KPI rollups |
| `src/sql/serving/` | Platinum | Read-only views for Power BI and APIs |

---

## 4. Patterns Evaluated and Not Adopted

### default_dbt

**Reason**: dbt is not in the InsightPulse AI stack. We use native Databricks SQL tasks for Gold/Platinum transformations and DLT for Bronze/Silver. Adding dbt would introduce a redundant transformation layer.

### mlops_stacks

**Reason**: ML model serving is not yet in scope for the Finance PPM workload. When AI/ML model deployment is needed, this pattern will be evaluated as a new bundle (e.g., `mlops_serving`).

### lakehouse_monitoring

**Reason**: Data quality monitoring is handled by:
- Custom quality check framework in `ipai_data_intelligence.quality`
- Databricks system tables for job/pipeline health
- Azure Monitor for infrastructure alerting

A dedicated monitoring bundle may be added later if the custom framework proves insufficient.

### rag_application

**Reason**: RAG workloads are served via Azure AI Foundry (`aifoundry-ipai-dev`), not Databricks. The agent-platform runtime handles embedding generation and retrieval. Databricks provides the governed data layer but not the inference endpoint.

---

## 5. Versioning and Drift

This crosswalk was authored against:
- `databricks/bundle-examples` commit: latest as of 2026-03-22
- Databricks CLI version: >= 0.230.0 (bundle v2 schema)
- Databricks Runtime: 15.x LTS

When upstream patterns change, update this document in the same PR that adapts our bundles.

---

*Last updated: 2026-03-22*
