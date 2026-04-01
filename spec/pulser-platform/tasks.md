# Tasks — Pulser Assistant: Control Plane

## Phase 1 — Formation and Capability Registry

- [ ] Define PulserFormation schema (systems, capabilities, grounding, environment bindings)
- [ ] Define PulserCapabilityPackage schema (name, version, agent/workflow refs, enablement state)
- [ ] Define PulserIntegrationTarget schema (system type, connection config, health status)
- [ ] Create formation CRUD operations
- [ ] Create capability package CRUD operations
- [ ] Create integration target registration operations
- [ ] Register initial formation: "IPAI Finance Assistant" (Odoo + data-intelligence + finance agents)

## Phase 2 — Identity and Trust

- [ ] Define PulserIdentityBinding schema (entra_id, pulser_role, permissions, trust_level)
- [ ] Implement Entra ID-backed identity resolution
- [ ] Enforce one-identity-per-human constraint
- [ ] Define trust levels (viewer, operator, admin, compliance)
- [ ] Wire identity bindings to capability package access control

## Phase 3 — Grounding Registry

- [ ] Define PulserGroundingSource schema (type, location, owner, refresh_cadence, quality_score)
- [ ] Define PulserGroundingPipeline schema (source_ref, pipeline_type, status, last_refresh, metrics)
- [ ] Create grounding source registration operations
- [ ] Create grounding pipeline status tracking
- [ ] Register initial grounding sources: finance knowledge base, BIR compliance docs, Odoo schema reference

## Phase 4 — Preview/Production Release Model

- [ ] Define promotion state machine (draft → preview → validated → promoted → retired)
- [ ] Define PulserPromotionRecord schema (formation/package ref, channel, evidence refs, promoter, timestamp)
- [ ] Define PulserValidationRun schema (type, target, results, evidence refs)
- [ ] Define PulserEvidenceArtifact schema (type, checksum, source, timestamp)
- [ ] Implement evidence-gated promotion (block production without validation)
- [ ] Implement preview → production promotion workflow
- [ ] Wire promotion gate into AzDO pipeline

## Phase 5 — Cross-Repo Adapters

- [ ] Add registration adapter for `agents` (capability package ↔ agent/workflow template)
- [ ] Add registration adapter for `web` (surface ↔ hosted UI component)
- [ ] Add registration adapter for `odoo` (integration target ↔ adapter module)
- [ ] Add registration adapter for `data-intelligence` (grounding source ↔ Gold mart)
- [ ] Add drift reconciliation: compare registry state against deployed runtime state

## Phase 6 — Policy and Governance

- [ ] Define capability enablement policy (who can enable/disable packages)
- [ ] Define grounding change policy (require review for production grounding changes)
- [ ] Define promotion policy (minimum validation coverage, mandatory evidence types)
- [ ] Add policy enforcement to promotion workflow
- [ ] Add audit trail for all formation/capability/grounding changes

## Verification Gates

- [ ] At least one formation registered and operational
- [ ] At least one capability package promoted preview → production with evidence
- [ ] All grounding sources registered with refresh status
- [ ] Identity bindings enforced for active users
- [ ] Zero direct-to-production promotions
- [ ] Cross-repo adapters operational for agents, web, odoo

### Phase P5 — Tax Guru Control Plane Objects

- [ ] P5.1 — Define PulserTaxRuleSource schema (jurisdiction, authority_type enum: bir/company_policy/external_tax_engine/accounting_guidance, version, effective dates)
- [ ] P5.2 — Define PulserTaxJurisdictionProfile schema (country/region/city/company, default tax regime)
- [ ] P5.3 — Define PulserTaxCapabilityProfile schema (capability_type enum, supported tax types/jurisdictions, action modes, role bindings)
- [ ] P5.4 — Define PulserTaxEvidenceBundle schema (rule source refs, document refs, explanation, confidence score)
- [ ] P5.5 — Define PulserTaxExceptionCase schema (exception_type enum, severity, assignment, evidence binding)
- [ ] P5.6 — Register 7 tax capability packages in PulserCapabilityPackage registry
- [ ] P5.7 — Add tax KPI definitions to evidence/metrics model
