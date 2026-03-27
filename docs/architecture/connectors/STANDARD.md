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

## Connector mode (required)

Every connector must declare exactly one of three connector modes:

### `platform_managed.runtime_bound`
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

### `platform_managed.cloud_connection`
The platform owns the connector contract through managed cloud connection objects.
Benchmark: Salesforce / managed SaaS connector pattern (cloud connection object, connection ID binding, no source-adjacent runtime).

Required contract areas:
- source-system prerequisites
- source connection type
- source connection ID
- orchestration/metadata connection type
- orchestration/metadata connection ID
- authentication method
- managed connection trust boundary
- post-create dataset/relationship handoff
- onboarding sequence (connection binding + dataset activation flow)
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

Runtime-bound sections (identity, secrets, runtime topology, network) are optional for cloud-connection and partner-managed connectors
but must be explicitly marked N/A with justification if omitted.

## Relationship to workload items
A workload item is the deployable domain solution.
A connector is the governed onboarding path for a source feeding that workload item.

## Recommended naming
- workload item: `<domain-solution-slug>`
- runtime-bound connector: `<workload-item-slug>-<source-system>-connector`
- cloud-connection connector: `<workload-item-slug>-<source-system>-cloud-connector`
- partner-managed connector: `<workload-item-slug>-<partner>-<source-system>-connector`

## Supported modes (detailed)

See `MODES.md` for full mode definitions and decision rules.

### 1. `platform_managed.runtime_bound`
Use when the workload/platform owns the extraction runtime.
Required emphasis:
- provider/service prerequisites
- role assignments
- execution identity
- secret authority
- runtime topology
- network placement
- dependency installation

### 2. `platform_managed.cloud_connection`
Use when the workload/platform owns the connector contract through managed cloud connection objects rather than a runtime-heavy extractor.
Required emphasis:
- source connection type
- source connection ID
- orchestration connection type
- orchestration connection ID
- authentication method
- managed connection trust boundary
- dataset/relationship handoff after source creation

### 3. `partner_managed`
Use when ingestion is delegated to an external mirroring/partner tool and the workload item binds to that ingestion through a partner contract.
Required emphasis:
- partner name
- connection ID
- trust boundary
- landing/handoff contract
- freshness/SLA
- escalation path

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
- connection_object (cloud-connection addition)
- partner_escalation (partner-managed addition)
