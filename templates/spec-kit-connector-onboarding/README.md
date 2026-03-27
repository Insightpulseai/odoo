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

## Supported connector modes

Every connector must declare exactly one mode:

### `platform_managed.runtime_bound` (ADF benchmark)
Platform owns the extraction runtime. Full identity, secret, runtime, network contract required.

### `platform_managed.cloud_connection` (Salesforce/SaaS benchmark)
Platform owns the connector contract through managed cloud connection objects. Source connection ID + orchestration connection ID required. No self-hosted runtime.

### `partner_managed` (Open Mirroring benchmark)
Third-party owns extraction. Partner name, connection ID, trust boundary, SLA, handoff schema required.

## Scope
This template is for connector onboarding only:
- source prerequisites
- required roles and providers
- connector mode
- connector execution identity (runtime_bound), managed connection contract (cloud_connection), or partner contract (partner_managed)
- secret storage authority
- runtime topology / network placement
- runtime dependencies
- onboarding sequence
- validation and rollback

It is not the semantic-model spec and not the agent UX spec.

## Canonical relationship
- workload item spec = deployable domain solution
- connector onboarding spec = deployable source-ingestion contract for that workload item

## Supported connector modes
- `platform_managed.runtime_bound`
- `platform_managed.cloud_connection`
- `partner_managed`
