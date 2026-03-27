# Plan — <Connector Name>

## 1. Deployment boundary
- Workload item: `<workload-item-slug>`
- Environment(s): `<dev/staging/prod>`
- Region: `<region>`
- Data residency assumption: `<assumption>`

## 2. Ingestion ownership model
- Model: `<platform_managed | partner_managed>`

### If `platform_managed`
Fill sections 3–6 fully.

### If `partner_managed`
Fill section 2a instead of sections 4–6. Sections 4–6 may be marked N/A with justification.

## 2a. Partner-managed ingestion contract (if `partner_managed`)
- Partner name: `<partner>`
- Partner version: `<version>`
- Connection ID: `<precreated connection ID>`
- Partner trust boundary: `<what data the partner sees / does not see>`
- Ingestion SLA:
  - Freshness: `<target>`
  - Availability: `<target>`
  - Retry behavior: `<description>`
- Handoff schema:
  - Landing location: `<where data lands>`
  - Format: `<parquet | delta | json | mirrored tables>`
  - Schema contract: `<explicit columns / tables or discovery-based>`
- Failure escalation:
  - Partner contact: `<contact>`
  - Escalation path: `<path>`
  - Platform fallback: `<what happens if partner ingestion fails>`

## 3. Source contract
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

### If `platform_managed`
1. verify source prerequisites
2. verify providers/services
3. provision/verify identity
4. provision/verify secret references
5. provision/verify runtime
6. bind connector to workload item
7. run source handshake validation
8. run first extraction/discovery validation
9. record post-create evidence

### If `partner_managed`
1. verify source prerequisites
2. verify partner availability and version
3. obtain precreated connection ID from partner
4. bind connection ID to workload item
5. verify partner handshake / landing schema
6. run first extraction/discovery validation
7. verify ingestion SLA baseline
8. record post-create evidence

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
