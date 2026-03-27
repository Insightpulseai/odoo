# Constitution — <Connector Name>

## 1. Purpose
Define the invariant operating contract for `<connector-slug>`, the governed onboarding path for connecting `<source-system>` into `<workload-item>`.

## 2. Connector boundaries
### In scope
- source-system onboarding
- connector runtime type
- connector execution identity
- secret authority
- network placement
- runtime dependencies
- validation checks
- failure handling / rollback

### Out of scope
- downstream semantic model design
- business-template design
- assistant behavior design
- ad hoc manual source access outside the connector contract

## 3. Workload-item binding
- Workload item: `<workload-item-slug>`
- Domain: `<finance | sales | procurement | tax | other>`
- Source system: `<source-system>`
- Source type: `<erp | crm | db | api | file | other>`
- Ingestion ownership model: `<platform_managed | partner_managed>`

## 3a. Ingestion ownership model (required)
Every connector must declare one of two ingestion ownership modes.
The mode determines which contract sections are mandatory.

### `platform_managed`
The platform owns the extraction runtime. Required:
- providers/services
- execution identity
- secrets authority
- runtime topology
- network placement
- local/runtime dependencies

Benchmark: Azure Data Factory connector pattern (self-hosted IR, service principal, Key Vault, provider registration).

### `partner_managed`
A third-party platform owns extraction. The workload item owns processing only. Required:
- partner name
- connection ID (precreated by partner)
- partner trust boundary
- ingestion SLA / freshness contract
- handoff schema / landing contract
- failure escalation path back to the partner

Benchmark: Open Mirroring connector pattern (partner selection, connection ID binding, external extraction).

Platform-managed sections (identity, secrets, runtime topology, network) are optional for partner-managed connectors
but must be explicitly marked N/A with justification if omitted.

## 4. Prerequisite invariants
The connector must define:
- source-system prerequisites
- required cloud providers/services
- required roles/permissions
- required local/runtime dependencies
- required network path and placement

No connector may be treated as deployable unless all prerequisites are explicit.

## 5. Identity and secret invariants
- Execution identity type: `<managed identity | service principal | other>`
- Identity owner: `<team/role>`
- Secret authority: `<key vault / secret manager>`
- Rotation authority: `<team/role>`

Connector credentials must never be treated as repo state.

## 6. Runtime topology invariants
The connector must declare:
- where it runs
- what network adjacency it requires
- what target endpoints it needs
- what runtime dependencies it needs
- what isolation boundary it assumes

## 7. Validation invariants
Minimum validations:
- identity/auth validation
- secret access validation
- network reachability validation
- source handshake validation
- first extraction / discovery validation
- post-create health/status validation

## 8. Failure-class invariants
Every connector spec must classify failure modes under:
- identity
- rbac
- state
- network
- artifact
- toolchain
- pipeline_config
- runtime_health
- source_system

## 9. Partner-managed invariants (if `partner_managed`)
When ingestion is partner-managed:
- partner name and version must be documented
- connection ID must be captured before workload-item binding
- partner trust boundary must be explicit (what data the partner sees, what it does not)
- ingestion SLA must be documented (freshness, availability, retry behavior)
- handoff schema must be explicit (what lands, in what format, where)
- failure escalation path must name who to contact for partner-side failures
- platform cannot assume control over partner extraction behavior

## 10. Change control
Spec updates are required for:
- source endpoint changes
- identity or role changes
- secret authority changes
- runtime topology changes
- network placement changes
- connector dependency changes
- validation workflow changes
- ingestion ownership model changes (platform_managed ↔ partner_managed)
- partner name or connection ID changes (if partner_managed)
