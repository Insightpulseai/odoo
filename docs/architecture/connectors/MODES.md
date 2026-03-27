# Connector Onboarding Modes

## Purpose
Define the three supported source-ingestion modes for workload-item connectors.

## Mode A — `platform_managed.runtime_bound`
The platform owns the extraction runtime.

Typical characteristics:
- explicit provider/service prerequisites
- explicit role requirements
- explicit execution identity
- explicit secret authority
- explicit runtime topology
- explicit network adjacency where needed
- explicit runtime dependencies

Use this mode when the platform is responsible for deploying and operating the connector runtime.

Benchmark: Azure Data Factory connector pattern — requires Azure resource-provider registration,
specific subscription/resource-group permissions, a service principal whose secret is stored in
Key Vault, and a self-hosted integration runtime VM with direct connectivity to the source system.

## Mode B — `platform_managed.cloud_connection`
A managed cloud connection object owns the source auth/binding, while the workload item binds both the source connection and an orchestration/metadata connection.

Typical characteristics:
- managed SaaS/cloud connection object
- connection ID captured as a first-class contract value
- orchestration connection ID captured separately
- authentication via OAuth or managed credential
- no self-hosted/source-adjacent runtime required
- dataset/relationship setup follows source creation

Use this mode when the workload item owns the connector contract but not a runtime-heavy extractor footprint.

Benchmark: Salesforce / managed SaaS connector pattern — create a managed cloud connection,
capture the source connection ID, bind it together with a separate orchestration connection ID,
then hand off to dataset/relationship activation.

## Mode C — `partner_managed`
A third-party ingestion or mirroring platform owns extraction, while the workload item binds to the resulting connection/landing contract.

Typical characteristics:
- explicit partner selection
- explicit connection ID
- explicit trust boundary
- explicit handoff/landing contract
- explicit freshness/SLA
- explicit escalation path back to the partner

Use this mode when the workload item owns downstream processing but not the extraction runtime.

Benchmark: Open Mirroring connector pattern — the workload item still processes the extracted data,
but ingestion is handled by a third-party tool, and onboarding binds the source through partner
selection and a precreated connection ID.

## Decision rule
Choose `platform_managed.runtime_bound` when you need first-party control over:
- secrets
- runtime placement
- dependency stack
- network adjacency
- extraction behavior

Choose `platform_managed.cloud_connection` when you want:
- managed SaaS/cloud binding
- explicit source + orchestration connection IDs
- lighter connector runtime footprint
- post-create handoff into dataset activation

Choose `partner_managed` when you want:
- delegated ingestion runtime ownership
- lighter onboarding inside the workload item
- explicit partner-bound connection contracts

## Invariant
Every production connector must declare exactly one connector mode.
The mode cannot be left unset or deferred — it determines which contract sections are mandatory.

## Companion documents
- Standard: `STANDARD.md`
- Template: `templates/spec-kit-connector-onboarding/`
