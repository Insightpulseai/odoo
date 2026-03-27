# Tasks — <Connector Name>

## Phase 0 — Connector mode
- [ ] declare connector mode: `platform_managed.runtime_bound`, `platform_managed.cloud_connection`, or `partner_managed`

## Phase 1 — Source and prerequisites
- [ ] identify source owner
- [ ] document source prerequisites
- [ ] document required providers/services
- [ ] document required roles/permissions

## Phase 2a — Identity and secrets (runtime_bound)
- [ ] define execution identity
- [ ] define role assignments
- [ ] define secret authority
- [ ] define secret references
- [ ] define rotation owner
- [ ] define first-party connector execution identity
- [ ] define secret bootstrap and runtime injection

## Phase 2b — Cloud-connection contract (cloud_connection)
- [ ] define source connection type
- [ ] define source connection ID
- [ ] define orchestration connection type
- [ ] define orchestration connection ID
- [ ] define authentication method
- [ ] define managed connection ownership boundary

## Phase 2c — Partner contract (partner_managed)
- [ ] document partner name and version
- [ ] obtain precreated connection ID
- [ ] document partner trust boundary
- [ ] document partner-owned identity boundary
- [ ] document workload-owned trust binding
- [ ] define escalation/ownership split
- [ ] document ingestion SLA (freshness, availability, retry)
- [ ] document handoff schema (landing location, format, schema contract)
- [ ] document failure escalation path (partner contact, escalation path, platform fallback)

## Phase 3 — Runtime and network

### Runtime-bound
- [ ] define runtime type
- [ ] define network placement
- [ ] define required endpoints
- [ ] define runtime dependencies
- [ ] define direct source connectivity requirements
- [ ] define dependency installation requirements

### Cloud-connection
- [ ] define managed cloud connection boundary
- [ ] define workload-item binding boundary
- [ ] define expected landed object/schema contract
- [ ] define post-create dataset/relationship handoff
- [ ] define discovery/visibility validation

### Partner-managed
- [ ] define external ingestion runtime owner
- [ ] define landing/handoff boundary into workload item
- [ ] define expected delivered schema/object contract
- [ ] define freshness/update contract

## Phase 4 — Onboarding flow
- [ ] define preflight checks
- [ ] define deployment steps (or partner binding steps)
- [ ] define post-create validation
- [ ] define first extraction/discovery validation

## Phase 5 — Governance and operations
- [ ] define failure taxonomy mapping
- [ ] define evidence outputs
- [ ] define rollback/decommission path
- [ ] define owner/signoff requirements
