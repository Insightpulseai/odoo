# Bundle Patterns Reference

> This directory contains reference documentation mapping upstream Databricks bundle-examples to our bundle layout.
> These files are NOT deployable. They exist to document design decisions and provide onboarding context.

---

## Upstream Patterns Used

| Upstream Pattern | Our Bundle | Key Adaptations |
|-----------------|-----------|-----------------|
| `default_python` | `foundation_python` | Multi-catalog variables, service principal prod target, wheel cross-bundle consumption |
| `lakeflow_pipelines_python` | `lakeflow_ingestion` | JDBC extraction focus, Odoo PostgreSQL as primary source, Bronze-only scope |
| `default_sql` | `sql_warehouse` | Gold/Platinum layer focus, Power BI serving views, SQL warehouse compute |

## Patterns Not Used (and Why)

| Upstream Pattern | Reason Not Used |
|-----------------|-----------------|
| `default_dbt` | dbt is not in our stack; we use native SQL tasks and DLT |
| `mlops_stacks` | ML model serving is not yet in scope; deferred to future spec |
| `lakehouse_monitoring` | Monitoring is handled by Azure Monitor + Databricks system tables |
| `rag_application` | RAG is served via Azure AI Foundry, not Databricks |

## How to Add a New Bundle

1. Identify the closest upstream pattern from `databricks/bundle-examples`
2. Create a new directory under `databricks/bundles/<name>/`
3. Copy the `databricks.yml` skeleton from the matched pattern
4. Adapt variables to include `catalog`, `schema_*` per our convention
5. Add dev/staging/prod targets with our catalog names
6. Add `run_as` and `permissions` to the prod target
7. Update `databricks/README.md` bundle inventory
8. Update `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md`
9. Update this crosswalk document
10. Add the new bundle path to `.github/workflows/databricks-bundles-ci.yml`

## References

- Upstream bundle-examples: `https://github.com/databricks/bundle-examples`
- Databricks Asset Bundles docs: `https://docs.databricks.com/en/dev-tools/bundles/index.html`
- DAB configuration reference: `https://docs.databricks.com/en/dev-tools/bundles/settings.html`
