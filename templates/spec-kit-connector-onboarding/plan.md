# Plan — <Connector Name>

## 1. Deployment boundary
- Workload item: `<workload-item-slug>`
- Environment(s): `<dev/staging/prod>`
- Region: `<region>`
- Data residency assumption: `<assumption>`

## 2. Source contract
- Source system: `<source-system>`
- Source owner: `<team/owner>`
- Source connectivity method: `<runtime/protocol>`
- Source prerequisites:
  - `<prerequisite>`
  - `<prerequisite>`

## 3. Provider / platform prerequisites
- Required providers/services:
  - `<provider/service>`
- Required permissions:
  - `<role>`
  - `<role>`

## 4. Identity plan
- Execution identity type: `<type>`
- Identity object name: `<name>`
- Required role assignments:
  - `<scope>` -> `<role>`
- Approval owner: `<owner>`

## 5. Secret plan
- Secret authority: `<vault/store>`
- Secret names/refs:
  - `<secret-ref>`
- Rotation owner: `<owner>`
- Secret injection method: `<env/ref/runtime binding>`

## 6. Runtime topology plan
- Connector runtime type: `<self-hosted runner | managed runtime | app | function | vm | container>`
- Network placement: `<subnet/vnet/segment>`
- Required endpoints:
  - `<endpoint>`
- Runtime dependencies:
  - `<dependency>`
  - `<dependency>`

## 7. Onboarding sequence
1. verify source prerequisites
2. verify providers/services
3. provision/verify identity
4. provision/verify secret references
5. provision/verify runtime
6. bind connector to workload item
7. run source handshake validation
8. run first extraction/discovery validation
9. record post-create evidence

## 8. Validation plan
### Preflight
- identity check
- secret access check
- network reachability check
- dependency check

### Post-create
- connector registration check
- source handshake check
- extraction/discovery check
- health/status check

## 9. Rollback / decommission
- disable connector
- revoke runtime access
- revoke or rotate secrets
- remove workload-item binding
- preserve onboarding evidence
