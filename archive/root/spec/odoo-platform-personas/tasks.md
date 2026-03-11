# Tasks — Odoo Platform Personas & Expertise Registry

## T0 — Finalize Spec Kit Baseline
- [ ] Review and approve canonical persona names
- [ ] Review and approve expertise taxonomy naming convention
- [ ] Review and approve G1–G4 gate sequence
- [ ] Review and approve minimum evidence requirements
- [ ] Mark `spec/odoo-platform-personas/*` as SSOT for persona/gate model

**Done when**
- Constitution + PRD + Plan + Tasks are internally consistent
- No unresolved contradictions in scope, roles, or gates

---

## T1 — Create Persona Contract Templates (Agent/Human Shared Format)
- [ ] Define persona template sections:
  - Mission
  - Scope / Non-scope
  - Inputs
  - Outputs
  - Decision rights
  - Prohibited actions
  - Escalation rules
  - Required evidence
  - KPIs
  - Failure modes
- [ ] Create template artifact in agent/persona docs location
- [ ] Validate template supports all four canonical personas without custom fields

**Done when**
- One template can instantiate Developer, QA, Release Manager, and SRE personas

---

## T2 — Instantiate Canonical Persona Contracts
- [ ] Create Odoo Platform Developer contract
- [ ] Create Odoo QA / Release Tester contract
- [ ] Create Odoo Release Manager contract
- [ ] Create Odoo Platform SRE / System Administrator contract
- [ ] Add shared governance overlay / skill-pack reference to all four

**Done when**
- Each persona contract is complete and references shared governance expectations

---

## T3 — Build Expertise Registry Mapping
- [ ] Create expertise registry entries for:
  - `odoo.devx.ci_cd`
  - `odoo.devx.debugging`
  - `odoo.qa.automation`
  - `odoo.qa.staging_validation`
  - `odoo.release.orchestration`
  - `odoo.release.governance`
  - `odoo.sre.backup_recovery`
  - `odoo.sre.monitoring_performance`
  - `odoo.sre.network_dns_mail`
  - `odoo.platform.environment_governance`
- [ ] Map personas ↔ expertise domains
- [ ] Identify shared vs persona-specific expertise

**Done when**
- Persona-to-expertise mapping is explicit and no critical capability is unmapped

---

## T4 — Define Gate/Evidence Schema (Spec-Level)
- [ ] Define structured gate definitions for G1–G4
- [ ] Define required evidence payload per gate (spec-level schema)
- [ ] Define exception record shape (risk, approver, TTL, review)
- [ ] Define post-deploy confirmation evidence expectations

**Done when**
- Gate/evidence rules are implementation-ready for CI and Supabase wiring

---

## T5 — CI Gate Enforcement Design (Implementation Spec Follow-on)
- [ ] Draft CI mapping for G1–G4 checks
- [ ] Draft promotion block conditions for failed/missing gates
- [ ] Draft exception override path and audit logging requirements
- [ ] Draft artifact retention requirements for gate evidence

**Done when**
- CI implementation can be built without reinterpreting persona/gate intent

---

## T6 — Supabase Control-Plane Integration Design (Implementation Spec Follow-on)
- [ ] Draft conceptual tables for releases, gates, approvals, evidence, exceptions, incidents
- [ ] Define event ingestion contract from CI/agents
- [ ] Define RLS boundary assumptions by persona/role
- [ ] Define reporting views/queries for release and ops KPIs

**Done when**
- A separate Supabase spec can be authored directly from this output

---

## T7 — Environment Governance Controls Design
- [ ] Define non-prod email suppression/catcher policy
- [ ] Define staging data refresh + masking policy expectations
- [ ] Define environment TTL lifecycle policy
- [ ] Define access control expectations for logs/shell/runtime actions
- [ ] Define exception handling and expiry process

**Done when**
- Environment safety controls are clear enough for automation implementation

---

## T8 — Validation & Dry Run
- [ ] Run one simulated release through G1–G4 using current process
- [ ] Identify ambiguities in role ownership, evidence, or approvals
- [ ] Update spec bundle to remove ambiguity
- [ ] Record initial lessons learned for v1.1 improvements

**Done when**
- At least one end-to-end dry run validates that the model is understandable and usable

---

## T9 — Publish & Governance Adoption
- [ ] Reference this spec in engineering/release runbooks
- [ ] Require persona/gate terminology in release documentation
- [ ] Add governance review cadence (monthly/quarterly)
- [ ] Create versioning policy for future amendments to this spec bundle

**Done when**
- Persona + gate model is used in active release/ops workflows and versioned as SSOT
