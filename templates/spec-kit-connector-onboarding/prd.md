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

## 5. Ingestion ownership model
- `platform_managed`: platform owns the extraction runtime (ADF benchmark)
- `partner_managed`: third-party owns extraction, workload item owns processing (Open Mirroring benchmark)

The model must be declared. It determines which functional requirements are mandatory vs N/A.

## 6. Core use cases

### Platform-managed
1. onboard `<source-system>` into `<workload-item>`
2. validate connector prerequisites before deploy
3. provision connector identity and secret references
4. deploy or register connector runtime
5. validate first successful source handshake/extraction
6. diagnose onboarding failures using standard failure classes

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

### FR-2 Identity (platform_managed: required | partner_managed: N/A or limited)
The connector shall define a single execution identity contract and required role assignments.
For partner-managed connectors, document the partner's identity boundary instead.

### FR-3 Secrets (platform_managed: required | partner_managed: N/A or limited)
The connector shall define where secrets live, how they are referenced, and who rotates them.
For partner-managed connectors, document whether the platform holds any secrets for the partner relationship.

### FR-4 Runtime topology (platform_managed: required | partner_managed: N/A)
The connector shall define runtime location, network placement, required endpoints, and local/runtime dependencies.
For partner-managed connectors, mark N/A — the partner owns the runtime.

### FR-5 Partner contract (partner_managed: required | platform_managed: N/A)
The connector shall define the partner name, connection ID, trust boundary, ingestion SLA, handoff schema, and failure escalation path.

### FR-6 Validation
The connector shall define preflight, deployment, and post-create validation steps.

### FR-7 Failure handling
The connector shall map failures into the approved failure taxonomy.
Partner-managed connectors must additionally define a partner escalation path.

## 8. Success metrics
- 100% of production connectors declare ingestion ownership model
- 100% of platform-managed connectors have explicit identity and secret authority
- 100% of partner-managed connectors have explicit partner contract and SLA
- 100% of production connectors define post-create validation
- 0 connector launches without a failure classification model
- reduced mean time to diagnose onboarding failures

## 9. Acceptance criteria

### All connectors
- [ ] ingestion ownership model declared (`platform_managed` or `partner_managed`)
- [ ] source prerequisites are explicit
- [ ] onboarding sequence is explicit
- [ ] validation sequence is explicit
- [ ] failure taxonomy mapping is explicit
- [ ] rollback/decommission path is explicit

### Platform-managed (additional)
- [ ] required roles and providers are explicit
- [ ] connector execution identity is explicit
- [ ] secret authority is explicit
- [ ] runtime topology is explicit

### Partner-managed (additional)
- [ ] partner name and version documented
- [ ] connection ID captured
- [ ] partner trust boundary documented
- [ ] ingestion SLA documented
- [ ] handoff schema documented
- [ ] failure escalation path documented
