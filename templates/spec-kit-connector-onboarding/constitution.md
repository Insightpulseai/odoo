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

## 9. Change control
Spec updates are required for:
- source endpoint changes
- identity or role changes
- secret authority changes
- runtime topology changes
- network placement changes
- connector dependency changes
- validation workflow changes
