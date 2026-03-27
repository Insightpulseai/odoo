# Connector Onboarding Standard

## Purpose
Standardize how workload-item source connectors are specified and onboarded.

## Canonical structure
Every production connector must have a four-file Spec Kit bundle:

```
spec/<connector-slug>/
├── constitution.md
├── prd.md
├── plan.md
└── tasks.md
```

## Required contract areas
- source-system prerequisites
- required providers/services
- required roles/permissions
- connector execution identity
- secret authority
- runtime topology and network placement
- runtime dependencies
- onboarding sequence
- validation sequence
- rollback/decommission path

## Relationship to workload items
A workload item is the deployable domain solution.
A connector is the governed onboarding path for a source feeding that workload item.

## Recommended naming
- workload item: `<domain-solution-slug>`
- connector: `<workload-item-slug>-<source-system>-connector`

## Template location
`templates/spec-kit-connector-onboarding/`

## Failure taxonomy alignment
Connector failure modes must map to the platform failure taxonomy:
- identity
- rbac
- state
- network
- artifact
- toolchain
- pipeline_config
- runtime_health
- source_system (connector-specific addition)
