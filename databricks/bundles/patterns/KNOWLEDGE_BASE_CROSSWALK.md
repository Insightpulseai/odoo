# Knowledge Base Crosswalk: Upstream Bundle Examples to Our Bundles

> Maps each upstream `databricks/bundle-examples` template to our bundle implementation,
> documenting what was adopted, adapted, and intentionally skipped.

## Adopted Baseline Patterns

| Upstream Pattern | Our Bundle | Adaptation |
|-----------------|------------|------------|
| `default_python` | `foundation_python` | Adapted for ipai_data_intelligence package, setuptools instead of hatch, added jobs/transforms/quality subpackages |
| `lakeflow_pipelines_python` | `lakeflow_ingestion` | Adapted for lakeflow_ingestion_etl package, placeholder pipeline entrypoint |
| `default_sql` | `sql_warehouse` | Adapted for SQL-first marts pattern, added warehouse_id variable |

## Deferred / Future Patterns

| Upstream Pattern | Status | Reason |
|-----------------|--------|--------|
| `mlops_stacks` | Deferred | Add when ML ownership is clear |
| `dbt_sql` | Deferred | Evaluate if dbt adoption is approved |
| `model_serving` | Deferred | Add when serving endpoints are needed |

## Rules

1. Every adopted pattern must have a row in the table above
2. Every deferred pattern must have a reason
3. This file is updated when a new bundle is added or a pattern decision changes
4. This file is reference-only and never deployed
