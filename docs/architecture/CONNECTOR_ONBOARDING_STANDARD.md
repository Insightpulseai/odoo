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

## Ingestion ownership model (required)

Every connector must declare one of two ingestion modes:

### `platform_managed`
The platform owns the extraction runtime.
Benchmark: Azure Data Factory connector pattern (self-hosted IR, service principal, Key Vault, provider registration).

Required contract areas:
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

### `partner_managed`
A third-party owns extraction. The workload item owns processing only.
Benchmark: Open Mirroring connector pattern (partner selection, connection ID binding, external extraction).

Required contract areas:
- source-system prerequisites
- partner name and version
- connection ID (precreated by partner)
- partner trust boundary
- ingestion SLA / freshness contract
- handoff schema / landing contract
- failure escalation path back to the partner
- onboarding sequence (partner binding flow)
- validation sequence
- rollback/decommission path

Platform-managed sections (identity, secrets, runtime topology, network) are optional for partner-managed connectors
but must be explicitly marked N/A with justification if omitted.

## Relationship to workload items
A workload item is the deployable domain solution.
A connector is the governed onboarding path for a source feeding that workload item.

## Recommended naming
- workload item: `<domain-solution-slug>`
- platform-managed connector: `<workload-item-slug>-<source-system>-connector`
- partner-managed connector: `<workload-item-slug>-<partner>-<source-system>-connector`

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
- partner_escalation (partner-managed addition)
