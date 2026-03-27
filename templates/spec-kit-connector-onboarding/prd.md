# PRD — <Connector Name>

## 1. Summary
`<Connector Name>` onboards `<source-system>` into `<workload-item>` using a governed connector runtime with explicit identity, secret, network, and validation contracts.

## 2. Problem
Current source onboarding fails when:
- connector setup is treated as ad hoc configuration
- identity and secret boundaries are implicit
- network/runtime requirements are undocumented
- post-create validation is weak or absent
- failures cannot be classified quickly

## 3. Goals
### Primary goals
- make source onboarding repeatable
- make execution identity and secret authority explicit
- make runtime topology and dependencies explicit
- make post-create validation deterministic
- support runtime-bound, cloud-connection, and partner-managed connector patterns

### Secondary goals
- reduce onboarding drift across environments
- improve diagnosability
- support workload-item packaging discipline

### Non-goals
- replacing semantic model design
- defining BI/business templates
- defining assistant/user-facing workflows

## 4. Personas
- platform engineer
- data/platform operator
- workload-item owner
- security/governance owner
- source-system owner

## 5. Connector mode
- `platform_managed.runtime_bound`: platform owns the extraction runtime (ADF benchmark)
- `platform_managed.cloud_connection`: platform owns connector contract through managed cloud connection objects (Salesforce/SaaS benchmark)
- `partner_managed`: third-party owns extraction, workload item owns processing (Open Mirroring benchmark)

The mode must be declared. It determines which functional requirements are mandatory vs N/A.

## 6. Core use cases

### Runtime-bound
1. onboard `<source-system>` into `<workload-item>`
2. validate connector prerequisites before deploy
3. provision connector identity and secret references
4. deploy or register connector runtime
5. validate first successful source handshake/extraction
6. diagnose onboarding failures using standard failure classes

### Cloud-connection
1. onboard `<source-system>` into `<workload-item>` via managed cloud connection
2. validate source connection object exists
3. validate orchestration/metadata connection exists
4. bind both connection IDs to workload item
5. validate source visibility/discovery
6. hand off to dataset/relationship setup
7. diagnose onboarding failures using standard failure classes

### Partner-managed
1. onboard `<source-system>` into `<workload-item>` via partner
2. validate partner availability and connection ID
3. bind connection ID to workload item
4. validate partner handshake and landing schema
5. verify ingestion SLA baseline
6. diagnose onboarding failures using standard failure classes + partner escalation

## 7. Functional requirements
### FR-1 Source prerequisites
The connector shall document all source prerequisites, including system settings, required access, and required dependencies.

### FR-2 Identity (runtime_bound: required | cloud_connection: connection auth | partner_managed: N/A or limited)
The connector shall define a single execution identity contract and required role assignments.
For cloud-connection connectors, document the managed connection auth method and connection-owner boundary.
For partner-managed connectors, document the partner's identity boundary instead.

### FR-3 Secrets (runtime_bound: required | cloud_connection: limited | partner_managed: N/A or limited)
The connector shall define where secrets live, how they are referenced, and who rotates them.
For cloud-connection connectors, document whether secrets are managed by the connection object or externally.
For partner-managed connectors, document whether the platform holds any secrets for the partner relationship.

### FR-4 Runtime topology (runtime_bound: required | cloud_connection: connection boundary | partner_managed: N/A)
The connector shall define runtime location, network placement, required endpoints, and local/runtime dependencies.
For cloud-connection connectors, define managed connection ownership and workload-item handoff boundary.
For partner-managed connectors, mark N/A — the partner owns the runtime.

### FR-5 Connection contract (cloud_connection: required | partner_managed: required | runtime_bound: N/A)
For cloud-connection connectors: source connection type/ID, orchestration connection type/ID, auth method, trust boundary, post-create handoff.
For partner-managed connectors: partner name, connection ID, trust boundary, ingestion SLA, handoff schema, failure escalation path.

### FR-6 Validation
The connector shall define preflight, deployment, and post-create validation steps.

### FR-7 Failure handling
The connector shall map failures into the approved failure taxonomy.
Partner-managed connectors must additionally define a partner escalation path.

### FR-8 Connector mode
The connector shall explicitly declare one of:
- `platform_managed.runtime_bound`
- `platform_managed.cloud_connection`
- `partner_managed`

### FR-9 Runtime-bound connector contract (runtime_bound: required | others: N/A)
If `platform_managed.runtime_bound`, the connector shall define:
- required providers/services
- execution identity
- secret authority
- runtime dependencies
- network placement
- source connectivity validation

### FR-10 Cloud-connection connector contract (cloud_connection: required | others: N/A)
If `platform_managed.cloud_connection`, the connector shall define:
- source connection type
- source connection ID
- orchestration connection type
- orchestration connection ID
- authentication method
- managed connection trust boundary
- post-create dataset/relationship activation handoff

### FR-11 Partner-managed connector contract (partner_managed: required | others: N/A)
If `partner_managed`, the connector shall define:
- partner name
- connection ID
- trust boundary
- landing/handoff contract
- freshness/SLA expectations
- partner escalation path

## 8. Success metrics
- 100% of production connectors declare connector mode
- 100% of runtime-bound connectors have explicit identity and secret authority
- 100% of cloud-connection connectors have explicit source + orchestration connection IDs
- 100% of partner-managed connectors have explicit partner contract and SLA
- 100% of production connectors define post-create validation
- 0 connector launches without a failure classification model
- reduced mean time to diagnose onboarding failures

## 9. Acceptance criteria

### All connectors
- [ ] connector mode declared (`platform_managed.runtime_bound`, `platform_managed.cloud_connection`, or `partner_managed`)
- [ ] source prerequisites are explicit
- [ ] onboarding sequence is explicit
- [ ] validation sequence is explicit
- [ ] failure taxonomy mapping is explicit
- [ ] rollback/decommission path is explicit

### Runtime-bound (additional)
- [ ] required roles and providers are explicit
- [ ] connector execution identity is explicit
- [ ] secret authority is explicit
- [ ] runtime topology is explicit

### Cloud-connection (additional)
- [ ] source connection type and ID documented
- [ ] orchestration connection type and ID documented
- [ ] authentication method documented
- [ ] managed connection trust boundary documented
- [ ] post-create dataset/relationship handoff documented

### Partner-managed (additional)
- [ ] partner name and version documented
- [ ] connection ID captured
- [ ] partner trust boundary documented
- [ ] ingestion SLA documented
- [ ] handoff schema documented
- [ ] failure escalation path documented
