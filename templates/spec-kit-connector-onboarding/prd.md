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

## 5. Core use cases
1. onboard `<source-system>` into `<workload-item>`
2. validate connector prerequisites before deploy
3. provision connector identity and secret references
4. deploy or register connector runtime
5. validate first successful source handshake/extraction
6. diagnose onboarding failures using standard failure classes

## 6. Functional requirements
### FR-1 Source prerequisites
The connector shall document all source prerequisites, including system settings, required access, and required dependencies.

### FR-2 Identity
The connector shall define a single execution identity contract and required role assignments.

### FR-3 Secrets
The connector shall define where secrets live, how they are referenced, and who rotates them.

### FR-4 Runtime topology
The connector shall define runtime location, network placement, required endpoints, and local/runtime dependencies.

### FR-5 Validation
The connector shall define preflight, deployment, and post-create validation steps.

### FR-6 Failure handling
The connector shall map failures into the approved failure taxonomy.

## 7. Success metrics
- 100% of production connectors have explicit identity and secret authority
- 100% of production connectors define runtime topology and network placement
- 100% of production connectors define post-create validation
- 0 connector launches without a failure classification model
- reduced mean time to diagnose onboarding failures

## 8. Acceptance criteria
- [ ] source prerequisites are explicit
- [ ] required roles and providers are explicit
- [ ] connector execution identity is explicit
- [ ] secret authority is explicit
- [ ] runtime topology is explicit
- [ ] onboarding sequence is explicit
- [ ] validation sequence is explicit
- [ ] rollback/decommission path is explicit
