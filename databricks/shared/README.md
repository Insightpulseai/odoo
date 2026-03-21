# Shared Configuration

> Common variables and configuration consumed by all Databricks bundles.

## Allowed Contents

- `variables.yml` — common variable definitions (catalog, schemas, workspace host, compute defaults)
- Shared Python utility libraries (future, if needed)

## Disallowed Contents

- Job definitions
- Pipeline definitions
- Resource YAML files
- Anything that would be deployed as a standalone unit

## Consumption Rule

Each bundle's `databricks.yml` includes shared files via relative path:

```yaml
include:
  - ../../shared/*.yml
```

Variables defined here can be overridden in each bundle's target-specific configuration.
