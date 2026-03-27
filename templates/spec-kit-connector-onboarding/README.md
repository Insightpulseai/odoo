# Connector Onboarding Spec Kit Template

Use this template for every workload-item source connector.

Create:

```
spec/<connector-slug>/
├── constitution.md
├── prd.md
├── plan.md
└── tasks.md
```

## Scope
This template is for connector onboarding only:
- source prerequisites
- required roles and providers
- connector execution identity
- secret storage authority
- runtime topology / network placement
- runtime dependencies
- onboarding sequence
- validation and rollback

It is not the semantic-model spec and not the agent UX spec.

## Canonical relationship
- workload item spec = deployable domain solution
- connector onboarding spec = deployable source-ingestion contract for that workload item
