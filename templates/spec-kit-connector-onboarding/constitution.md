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
- Connector mode: `<platform_managed.runtime_bound | platform_managed.cloud_connection | partner_managed>`

## 3a. Connector mode (required)
Every connector must declare exactly one of three connector modes.
The mode determines which contract sections are mandatory.

### `platform_managed.runtime_bound`
The platform owns the extraction runtime. Required:
- providers/services
- execution identity
- secrets authority
- runtime topology
- network placement
- local/runtime dependencies

Benchmark: Azure Data Factory connector pattern (self-hosted IR, service principal, Key Vault, provider registration).

### `platform_managed.cloud_connection`
The platform owns the connector contract through managed cloud connection objects. Required:
- source connection type
- source connection ID
- orchestration/metadata connection type
- orchestration/metadata connection ID
- authentication method
- managed connection trust boundary
- post-create handoff into dataset/relationship setup

Benchmark: Salesforce / managed SaaS connector pattern (cloud connection object, connection ID binding, no source-adjacent runtime).

### `partner_managed`
A third-party platform owns extraction. The workload item owns processing only. Required:
- partner name
- connection ID (precreated by partner)
- partner trust boundary
- ingestion SLA / freshness contract
- handoff schema / landing contract
- failure escalation path back to the partner

Benchmark: Open Mirroring connector pattern (partner selection, connection ID binding, external extraction).

Runtime-bound sections (identity, secrets, runtime topology, network) are optional for cloud-connection and partner-managed connectors
but must be explicitly marked N/A with justification if omitted.

## 4. Prerequisite invariants
The connector must define:
- source-system prerequisites
- required cloud providers/services
- required roles/permissions
- required local/runtime dependencies
- required network path and placement

No connector may be treated as deployable unless all prerequisites are explicit.

### 4.1 Runtime-bound minimums
If `connector_mode = platform_managed.runtime_bound`, the spec must explicitly define:
- required providers/services
- required roles/permissions
- execution identity
- secret authority
- runtime topology
- network placement
- runtime dependencies

### 4.2 Cloud-connection minimums
If `connector_mode = platform_managed.cloud_connection`, the spec must explicitly define:
- source connection type
- source connection ID
- orchestration/metadata connection type
- orchestration/metadata connection ID
- authentication method
- SaaS login/server endpoint if applicable
- trust boundary for the managed connection object
- post-create handoff into dataset/relationship setup

### 4.3 Partner-managed minimums
If `connector_mode = partner_managed`, the spec must explicitly define:
- mirroring/ingestion partner name
- connection ID / partner binding identifier
- partner trust boundary
- ingestion SLA / freshness contract
- handoff schema / landing contract
- partner escalation path
- ownership of extraction runtime outside the workload item

## 5. Identity and secret invariants
- Execution identity type: `<managed identity | service principal | other>`
- Identity owner: `<team/role>`
- Secret authority: `<key vault / secret manager>`
- Rotation authority: `<team/role>`

Connector credentials must never be treated as repo state.

### 5.1 Conditional identity rule
- `platform_managed.runtime_bound`: execution identity is mandatory
- `platform_managed.cloud_connection`: managed connection auth method and connection-owner boundary are mandatory
- `partner_managed`: connector-bound execution identity may be external to the workload item, but the trust boundary and partner connection contract are mandatory

## 6. Runtime topology invariants
The connector must declare:
- where it runs
- what network adjacency it requires
- what target endpoints it needs
- what runtime dependencies it needs
- what isolation boundary it assumes

### 6.1 Conditional runtime rule
- `platform_managed.runtime_bound`: runtime topology must include connector runtime placement and source reachability assumptions
- `platform_managed.cloud_connection`: runtime topology must define managed connection ownership plus workload-item handoff boundary
- `partner_managed`: runtime topology must define the external ingestion boundary and landing/handoff boundary into the workload item

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
- connector mode changes (runtime_bound ↔ cloud_connection ↔ partner_managed)
- connection ID changes (if cloud_connection or partner_managed)
- partner name changes (if partner_managed)
