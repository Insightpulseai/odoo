# Repository Taxonomy

## Purpose

Human-readable guide to the InsightPulse AI repository organization.

## Machine-Readable SSOT

The canonical repository inventory is:

```
docs/governance/repository_taxonomy.yaml
```

Validated by: `docs/governance/repository_taxonomy.schema.json`
CI check: `.github/workflows/control-room-governance.yml`

## Repository Types

| Type | Description | Examples |
|------|-------------|---------|
| `monorepo` | Multi-project repository | `odoo` |
| `spec-planning` | Specification and planning | `ipai-odoo-refactor` |
| `service` | Deployable service | — |
| `library` | Shared library/package | — |
| `infra` | Infrastructure configuration | — |
| `app` | Application | — |
