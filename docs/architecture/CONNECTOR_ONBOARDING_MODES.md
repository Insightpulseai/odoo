# Connector Onboarding Modes

## Purpose
Define the two supported source-ingestion ownership models for workload-item connectors.

## Mode A — `platform_managed`
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

## Mode B — `partner_managed`
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
Choose `platform_managed` when you need first-party control over:
- secrets
- runtime placement
- dependency stack
- network adjacency
- extraction behavior

Choose `partner_managed` when you want:
- delegated ingestion runtime ownership
- lighter onboarding inside the workload item
- explicit partner-bound connection contracts

## Invariant
Every production connector must declare exactly one ingestion ownership model.
The mode cannot be left unset or deferred — it determines which contract sections are mandatory.

## Companion documents
- Standard: `docs/architecture/CONNECTOR_ONBOARDING_STANDARD.md`
- Template: `templates/spec-kit-connector-onboarding/`
