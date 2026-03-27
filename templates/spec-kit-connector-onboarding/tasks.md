# Tasks — <Connector Name>

## Phase 0 — Ingestion ownership model
- [ ] declare ingestion ownership model: `platform_managed` or `partner_managed`

## Phase 1 — Source and prerequisites
- [ ] identify source owner
- [ ] document source prerequisites
- [ ] document required providers/services
- [ ] document required roles/permissions

## Phase 2a — Identity and secrets (platform_managed)
- [ ] define execution identity
- [ ] define role assignments
- [ ] define secret authority
- [ ] define secret references
- [ ] define rotation owner

## Phase 2b — Partner contract (partner_managed)
- [ ] document partner name and version
- [ ] obtain precreated connection ID
- [ ] document partner trust boundary
- [ ] document ingestion SLA (freshness, availability, retry)
- [ ] document handoff schema (landing location, format, schema contract)
- [ ] document failure escalation path (partner contact, escalation path, platform fallback)

## Phase 3 — Runtime and network (platform_managed only; N/A for partner_managed)
- [ ] define runtime type
- [ ] define network placement
- [ ] define required endpoints
- [ ] define runtime dependencies

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
