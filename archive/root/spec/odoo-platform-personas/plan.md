# Implementation Plan — Odoo Platform Personas & Expertise Registry

**Spec Bundle**: `spec/odoo-platform-personas/`
**Status**: Draft v1.0
**Date**: 2026-02-24

---

## Overview

This plan organizes the work to move from spec definition to operating model in production. The plan is structured in six phases, each with a clear input/output contract. Phases 0–2 are internal spec work. Phases 3–5 require coordination with CI and Supabase implementation.

---

## Phase 0 — Spec Kit Baseline Finalization

**Goal**: Lock the canonical vocabulary before any implementation work.

**Inputs**:
- `constitution.md` ✅
- `prd.md` ✅
- `plan.md` ✅ (this file)
- `tasks.md` ✅

**Outputs**:
- All four spec kit files internally consistent
- No open contradictions in persona names, expertise taxonomy, or gate definitions
- `spec/odoo-platform-personas/` marked as SSOT for persona/gate model

**Tasks**: T0 (see tasks.md)

**Acceptance**: Spec bundle passes `/speckit.analyze` consistency check with zero contradictions.

---

## Phase 1 — Persona Contract Authoring

**Goal**: Create a reusable persona template and instantiate all four canonical persona contracts.

**Inputs**:
- Phase 0 complete (spec locked)
- Expertise taxonomy domains finalized (FR-2)

**Outputs**:
- `docs/personas/template.md` — reusable template for any persona
- `docs/personas/developer.md` — Odoo Platform Developer contract
- `docs/personas/qa_tester.md` — Odoo QA / Release Tester contract
- `docs/personas/release_manager.md` — Odoo Release Manager contract
- `docs/personas/sre.md` — Odoo Platform SRE contract
- `docs/personas/expertise_registry.yaml` — persona-to-domain mapping table

**Tasks**: T1, T2, T3 (see tasks.md)

**Acceptance**:
- All four persona contracts pass template completeness check (all sections present)
- Expertise registry covers all 10 domains with persona assignments
- No capability gap: every G1–G4 gate check maps to at least one persona + expertise domain

---

## Phase 2 — Gate and Evidence Schema Design

**Goal**: Define the data shape for gates and evidence so CI and Supabase implementations can be built without reinterpreting this spec.

**Inputs**:
- Phase 1 complete (persona contracts authored)
- G1–G4 gate definitions from PRD (FR-3)

**Outputs**:
- `docs/gates/gate_schema.yaml` — structured gate definitions (gate code, name, required evidence, blocked promotions)
- `docs/gates/evidence_schema.yaml` — evidence record shape per gate
- `docs/gates/exception_schema.yaml` — exception record shape (FR-6 fields)
- `docs/gates/environment_controls.yaml` — environment safety control policies

**Tasks**: T4, T7 (see tasks.md)

**Acceptance**:
- Gate schema validates all 4 gates with no ambiguous fields
- Evidence schema covers all activities in FR-5
- Exception schema covers all fields in FR-6
- Environment controls cover all FR-4 requirements

---

## Phase 3 — CI Gate Alignment Design

**Goal**: Map G1–G4 gates to CI workflow implementation requirements. This phase produces a CI design spec, not CI YAML (that is a follow-on implementation task).

**Inputs**:
- Phase 2 complete (gate/evidence schemas)
- Existing CI workflow inventory (`.github/workflows/`)

**Outputs**:
- `docs/gates/ci_gate_mapping.md` — per-gate CI check requirements and workflow anchors
- `docs/gates/promotion_block_spec.md` — conditions that must block promotion at each gate
- `docs/gates/override_path_spec.md` — exception override path and required audit logging

**Dependencies**:
- Requires CI audit of existing `.github/workflows/` for current gate-equivalent checks
- Requires decision on CI gate enforcement point (PR merge gate, deployment trigger, or both)

**Tasks**: T5 (see tasks.md)

**Acceptance**:
- Every G1–G4 gate has at least one identified CI check that maps to it
- Promotion block conditions are deterministic (not "if someone remembers")
- Exception override path documents the audit trail required

---

## Phase 4 — Supabase Control-Plane Integration Design

**Goal**: Define conceptual tables and event ingestion contract so the Supabase spec (`spec/odoo-release-gates-control-plane/`) can be implemented directly from this output.

**Inputs**:
- Phase 2 complete (gate/evidence schemas)
- `spec/odoo-release-gates-control-plane/constitution.md`

**Outputs**:
- `docs/gates/supabase_domain_map.md` — mapping from persona/gate model to `ops.*` domains
- `docs/gates/event_ingest_contract.md` — CI/agent → Supabase event payload spec
- `docs/gates/rls_boundary_assumptions.md` — conceptual RLS boundaries per persona role

**Dependencies**:
- Supabase project active (`spdtwktxdalcfigzeqrz`)
- `spec/odoo-release-gates-control-plane/` spec bundle complete

**Tasks**: T6 (see tasks.md)

**Acceptance**:
- All G1–G4 gate outcomes have a corresponding `ops.*` table mapping
- Event ingestion contract includes idempotency key and schema version fields
- RLS boundaries align with persona decision rights (no cross-persona privilege leakage)

---

## Phase 5 — Dry Run, Validation, and Adoption

**Goal**: Run one real or simulated release through G1–G4, identify ambiguities, and promote this spec to production SSOT.

**Inputs**:
- Phases 1–4 complete
- At least one active release cycle in progress

**Outputs**:
- Dry run report (evidence artifacts, gate outcomes, ambiguities found)
- Updated spec bundle (v1.1) resolving ambiguities
- Persona/gate model referenced in engineering and release runbooks
- Governance review cadence established (monthly/quarterly)

**Tasks**: T8, T9 (see tasks.md)

**Acceptance**:
- At least one end-to-end release cycle is traced using this model
- No gate step is ambiguous about role ownership or evidence requirement
- Spec bundle versioning policy is documented
- Release runbook references `spec/odoo-platform-personas/` as authoritative

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Supabase control-plane not ready when Phase 4 starts | Medium | Medium | Phase 4 is design-only; implementation deferred to separate spec |
| CI workflows don't map cleanly to G1–G4 | Medium | High | Phase 3 audit identifies gaps; CI refactor scoped separately |
| Agent capability registry not yet canonical | Low | Medium | Phase 1 persona contracts can proceed without registry; registry is follow-on |
| Dry run reveals fundamental gate ambiguity | Low | High | Spec v1.1 update absorbs fixes; dry run is required before adoption |
| Competing release governance practices in team | Medium | Medium | Spec bundle must be referenced in PR templates and release runbooks |

---

## Milestone Summary

| Milestone | Phase | Deliverable |
|-----------|-------|------------|
| M0 | 0 | Spec bundle locked and consistent |
| M1 | 1 | All four persona contracts published |
| M2 | 2 | Gate and evidence schemas designed |
| M3 | 3 | CI gate alignment design complete |
| M4 | 4 | Supabase integration design complete |
| M5 | 5 | Dry run complete; spec promoted to production SSOT |
