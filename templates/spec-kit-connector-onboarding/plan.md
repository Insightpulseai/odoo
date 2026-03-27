# Plan — <Connector Name>

## 1. Deployment boundary
- Workload item: `<workload-item-slug>`
- Environment(s): `<dev/staging/prod>`
- Region: `<region>`
- Data residency assumption: `<assumption>`
- Connector mode: `<platform_managed.runtime_bound | platform_managed.cloud_connection | partner_managed>`

## 2. Connector mode
- Mode: `<platform_managed.runtime_bound | platform_managed.cloud_connection | partner_managed>`

### If `platform_managed.runtime_bound`
Fill sections 3–6 fully.

### If `platform_managed.cloud_connection`
Fill section 2b instead of sections 4–6. Sections 4–6 may be marked N/A with justification.

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

## 2b. Cloud-connection contract (if `platform_managed.cloud_connection`)
- Source connection type: `<salesforce | dynamics365 | other>`
- Source connection ID: `<connection-id>`
- Orchestration connection type: `<fabric-sql | other>`
- Orchestration connection ID: `<connection-id>`
- Authentication method: `<oauth | api-key | managed-identity | other>`
- SaaS login / server endpoint: `<endpoint if applicable>`
- Managed connection trust boundary: `<what the connection object can access>`
- Post-create handoff:
  - Dataset activation: `<manual | automatic>`
  - Relationship setup: `<required tables/objects>`
  - Discovery validation: `<how to verify source is visible>`

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

### 4.1 Runtime-bound identity plan
- Azure/provider prerequisites: `<provider/service>`
- Role requirements: `<role>`
- Secret bootstrap path: `<path>`

### 4.2 Cloud-connection identity plan
- Source connection type: `<salesforce | other>`
- Source connection ID: `<connection-id>`
- Orchestration connection type: `<fabric-sql | other>`
- Orchestration connection ID: `<connection-id>`
- Auth method: `<oauth | other>`
- Managed connection owner: `<owner>`

### 4.3 Partner-managed identity plan
- Partner name: `<partner>`
- Connection ID: `<connection-id>`
- Partner-owned identity boundary: `<boundary>`
- Workload-owned trust binding: `<binding>`

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

### 6.1 Runtime-bound topology expectations
- Direct source connectivity requirements
- Connector runtime location
- Dependency installation requirements

### 6.2 Cloud-connection topology expectations
- Managed cloud connection boundary
- Workload-item binding boundary
- Expected landed object/schema contract
- Post-create dataset/relationship configuration dependency

### 6.3 Partner-managed topology expectations
- External ingestion runtime owner
- Handoff/landing boundary into workload item
- Expected delivered schema/object contract
- Freshness/update contract

## 7. Onboarding sequence

### If `platform_managed.runtime_bound`
1. verify source prerequisites
2. verify providers/services
3. provision/verify identity
4. provision/verify secret references
5. provision/verify runtime
6. bind connector to workload item
7. run source handshake validation
8. run first extraction/discovery validation
9. record post-create evidence

### If `platform_managed.cloud_connection`
1. verify source prerequisites
2. verify source connection object exists
3. verify orchestration/metadata connection exists
4. bind both connection IDs to workload item
5. validate source visibility/discovery
6. hand off to dataset/relationship setup
7. validate dataset activation
8. record post-create evidence

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
