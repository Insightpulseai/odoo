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

## Ingestion ownership model

Every connector must declare one of two modes:

### `platform_managed` (ADF benchmark)
Platform owns the extraction runtime. Full identity, secret, runtime, network contract required.

### `partner_managed` (Open Mirroring benchmark)
Third-party owns extraction. Partner name, connection ID, trust boundary, SLA, handoff schema required.

## Scope
This template is for connector onboarding only:
- source prerequisites
- required roles and providers
- ingestion ownership model
- connector execution identity (platform_managed) or partner contract (partner_managed)
- secret storage authority
- runtime topology / network placement
- runtime dependencies
- onboarding sequence
- validation and rollback

It is not the semantic-model spec and not the agent UX spec.

## Canonical relationship
- workload item spec = deployable domain solution
- connector onboarding spec = deployable source-ingestion contract for that workload item
- platform_managed = platform owns extraction runtime
- partner_managed = partner owns extraction, platform owns processing
