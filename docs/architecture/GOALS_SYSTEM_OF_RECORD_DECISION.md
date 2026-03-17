# Goals System of Record Decision

> ADR-GSR-001 | Status: Accepted | Date: 2026-03-17

---

## 1. Executive Summary

InsightPulse AI maintains strategic goals, OKRs, KPIs, and roadmap entities across six distinct storage locations: in-repo SSOT YAML files with CI validators, spec bundles, strategy Markdown documents, Azure DevOps Boards (declared but not yet operationalized), Plane (self-hosted project management), and a sparse GitHub Issues/Projects surface. This analysis finds that the **in-repo SSOT YAML layer** (`ssot/governance/`) is the only goal store that is both structured and CI-validated today, making it the de facto canonical system of record for strategic goals. Azure DevOps Boards is the declared target for portfolio-level system of record but has not yet been operationalized. The recommended path forward is to formalize the in-repo YAML layer as the current canonical SoR, complete Azure DevOps Boards operationalization as the target portfolio SoR (OBJ-002 in the strategy), and define explicit graduation criteria for when portfolio authority transfers from YAML to Azure Boards. Until those criteria are met, the YAML layer is authoritative and Azure Boards is a projection surface.

---

## 2. Current Goal-Location Inventory

| # | Location | Content Type | Format | Grain | Last Updated | CI Validated |
|---|----------|-------------|--------|-------|--------------|--------------|
| 1 | `ssot/governance/platform-strategy-2026.yaml` | Vision, mission, 7 SMART objectives, 22 KRs, 13 KPIs, 4 programs, 16 tasks, risks | YAML (VMOKRAPI-SPATRES) | Strategic objective / KR / KPI | 2026-03-14 | Yes (schema + validator) |
| 2 | `ssot/governance/enterprise_okrs.yaml` | 5 thematic objectives (A-E), 3 canonical OKRs (O1-O3), 17 KPI cross-refs | YAML | Thematic OKR / KPI | 2026-03-08 | Yes (validator) |
| 3 | `ssot/governance/planning_system_index.yaml` | 6-layer planning hierarchy, canonical file pointers, join keys | YAML | Meta-index | 2026-03-14 | Planned |
| 4 | `ssot/governance/platform-capabilities-unified.yaml` | ERP parity %, OCA adoption, BIR compliance, AI consolidation | YAML | Capability / parity % | 2026-03 | No |
| 5 | `infra/ssot/ppm/portfolio.yaml` | 5 tracked initiatives (INIT-001..005) | YAML | Initiative | 2026-03 | No |
| 6 | `infra/ssot/roadmap/roadmap_crosswalk.yaml` | ~30 capabilities across 4 roadmap tracks | YAML | Capability / epic | Active (incomplete) | No |
| 7 | `spec/` (76 bundles) | Feature-level goals via constitution/prd/plan/tasks | Markdown | Feature / task | Varies | Yes (spec_validate.sh) |
| 8 | `docs/strategy/UNIFIED_STRATEGY_MODEL.md` | Strategy mapping doc (objectives to OKRs to programs) | Markdown | Narrative | 2026-03 | No |
| 9 | `docs/governance/ENTERPRISE_OPERATING_MODEL.md` | 5-layer org model, SoR matrix, roadmap linking model | Markdown | Narrative | 2026-03 | No |
| 10 | `docs/architecture/ROADMAP_TARGET_STATE.md` | Odoo as sole roadmap write authority, projection surfaces | Markdown | Architecture decision | 2026-03-17 | No |
| 11 | `docs/architecture/ROADMAP_FIELD_AUTHORITY.md` | Field-level ownership rules (Odoo-owned vs Plane-managed) | Markdown | Field authority | 2026-03 | No |
| 12 | Azure DevOps Boards | Portfolio epics, features, stories, tasks (Agile template) | AzDO Work Items | Epic / feature / story / task | Not operationalized | N/A |
| 13 | Plane (self-hosted) | Work items, cycles, sprints, comments | Plane entities | Epic / issue / cycle | Active (SoW only) | N/A |
| 14 | GitHub Issues | Sparse (2 issues found) | GitHub Issues | Issue | Minimal | N/A |
| 15 | GitHub Projects v2 | Intended boards (Roadmap + Execution) | GitHub Projects | Board / field | Unverified (token scope) | N/A |

---

## 3. Classification Table

| # | Location | Classification | Rationale |
|---|----------|---------------|-----------|
| 1 | `platform-strategy-2026.yaml` | **Canonical** | CI-validated, schema-backed, most complete goal store that exists. Contains vision through tasks. |
| 2 | `enterprise_okrs.yaml` | **Canonical** | CI-validated, complementary thematic OKR layer. Cross-references #1 via KPI IDs. |
| 3 | `planning_system_index.yaml` | **Canonical** | Master index that defines layer hierarchy and join keys. Required for coherence. |
| 4 | `platform-capabilities-unified.yaml` | **Candidate** | Useful capability-level parity tracking but no CI validator yet. Should be promoted. |
| 5 | `infra/ssot/ppm/portfolio.yaml` | **Canonical** | Active initiative register consumed by ops-ppm-rollup. Complements strategy layer at execution grain. |
| 6 | `roadmap_crosswalk.yaml` | **Candidate (incomplete)** | Many `[NEEDS_CLARIFICATION]` placeholders. Not yet reliable enough for canonical status. |
| 7 | `spec/` bundles | **Canonical** | Feature-level implementation truth. Already declared canonical in CLAUDE.md. |
| 8 | `UNIFIED_STRATEGY_MODEL.md` | **Narrative companion** | Human-readable mapping document. Derives from #1 and #2. Not a data store. |
| 9 | `ENTERPRISE_OPERATING_MODEL.md` | **Narrative companion** | Governance framework doc. Declares SoR matrix but is not itself a data store. |
| 10 | `ROADMAP_TARGET_STATE.md` | **Architecture decision** | Declares Odoo as roadmap write authority. Policy doc, not goal data. |
| 11 | `ROADMAP_FIELD_AUTHORITY.md` | **Architecture decision** | Field-level ownership rules. Policy doc, not goal data. |
| 12 | Azure DevOps Boards | **Target state (not yet operational)** | Declared as portfolio SoR in target-state.yaml and UNIFIED_STRATEGY_MODEL.md. OBJ-002 addresses operationalization. Currently bounded role, not seeded. |
| 13 | Plane | **Execution-only (SoW)** | Explicitly and repeatedly declared as "SoW, not SoR" across 4+ governance documents. Command source and projection target only. |
| 14 | GitHub Issues | **Legacy / unused** | Only 2 issues. Not a planning surface. |
| 15 | GitHub Projects v2 | **Unclear** | Token lacks read:project scope. Intended boards documented but not verified as active. |

---

## 4. Recommended Canonical Goal Location

**Current SoR (effective today):** The in-repo SSOT YAML layer under `ssot/governance/`.

Specifically:

| Layer | Canonical File | Authority |
|-------|---------------|-----------|
| Strategy + Objectives + KRs + KPIs | `ssot/governance/platform-strategy-2026.yaml` | Primary |
| Thematic OKRs + KPI cross-refs | `ssot/governance/enterprise_okrs.yaml` | Complementary |
| Layer index + join keys | `ssot/governance/planning_system_index.yaml` | Meta |
| Initiative execution | `infra/ssot/ppm/portfolio.yaml` | Execution register |
| Feature-level goals | `spec/*/constitution.md` + `prd.md` | Feature truth |

**Target SoR (when operationalized):** Azure DevOps Boards inherits portfolio-level authority (epics, features, initiative status) once OBJ-002 gates pass.

**Transition rule:** The YAML layer remains canonical until Azure DevOps Boards meets the graduation criteria defined in Section 7.

---

## 5. Rationale

### Why in-repo YAML wins today

1. **It exists and is populated.** The `platform-strategy-2026.yaml` file contains 7 objectives, 22 key results, 13 KPIs, 4 programs, and 16 tasks. No other surface has this density of structured goal data.

2. **It is CI-validated.** Both `platform-strategy-2026.yaml` and `enterprise_okrs.yaml` have dedicated CI validators and JSON schemas. Changes to strategic goals are gated by CI, which is the strongest governance primitive this organization has.

3. **It is repo-native.** The entire operating model treats the repo as SSOT (Rule 1 in ssot-platform.md). Goals stored in YAML follow the same governance path as code: PR, review, merge, CI gate. This is consistent with the platform doctrine.

4. **It has explicit cross-references.** The `planning_system_index.yaml` defines join keys between layers (objective IDs link to OKR refs, KPI refs link across files). This is a structured relational model, not scattered prose.

### Why Azure DevOps Boards is not canonical yet

1. **OBJ-002 ("AzDo operationalization") is "not yet started."** The strategy itself acknowledges this as a Q1 2026 deliverable that has not been completed.

2. **Bounded role documented.** `ssot/azure/target-state.yaml` explicitly states AzDo has `role: bounded` with constraint "Portfolio SoR (Boards) + infra-scoped pipelines only." The "bounded" qualifier indicates intentional scoping, not full operational authority.

3. **No seeded content verified.** Two AzDo projects are defined in YAML (`ipai-platform`, `lakehouse`) but there is no evidence of work items, epics, or features having been created in AzDo Boards.

4. **Repos/artifacts/test_plans/wiki are PROHIBITED** in the AzDo alignment YAML. AzDo is intentionally limited to Boards + Pipelines, which further reinforces that it is an execution projection surface, not a goal authoring surface.

### What was rejected

| Alternative | Rejection Reason |
|-------------|-----------------|
| Plane as SoR | Explicitly prohibited by 4+ governance documents. SoW only. |
| GitHub Issues/Projects | Only 2 issues. Not populated. Iteration API limitation makes it unsuitable for quarterly planning. |
| Odoo as goal SoR | Odoo is declared SoR for transactional/finance data and roadmap entities (initiatives, milestones). But strategic goals (vision, OKRs, KPIs) are governance artifacts, not transactional records. The YAML layer is the correct home for governance-grade goal definitions. Odoo may be the write authority for roadmap initiative *execution state*, but the goal *definitions* live in repo YAML. |
| Notion | Deprecated. Legacy data exists in Supabase. Being replaced. |
| Consolidated single file | The planning_system_index.yaml already provides the index. Merging all layers into one file would create a 1000+ line YAML that violates separation of concerns. The current layered model with explicit join keys is architecturally sound. |

---

## 6. Mapping Model

| Artifact Type | Where It Lives | Who Writes | Who Reads | Format |
|--------------|---------------|------------|-----------|--------|
| Vision / Mission | `ssot/governance/platform-strategy-2026.yaml` | Platform lead (via PR) | All systems, docs, dashboards | YAML |
| Strategic Objectives (OBJ-001..007) | `ssot/governance/platform-strategy-2026.yaml` | Platform lead (via PR) | AzDo Boards (projection), Plane (linking), docs | YAML |
| Thematic OKRs (obj_A..E) | `ssot/governance/enterprise_okrs.yaml` | Platform lead (via PR) | Strategy docs, KPI dashboards | YAML |
| Rollup OKRs (O1..O3) | `ssot/governance/enterprise_okrs.yaml` | Platform lead (via PR) | Operating model docs, Plane epic linking | YAML |
| KPIs (kpi_001..017) | `ssot/governance/platform-strategy-2026.yaml` + `enterprise_okrs.yaml` | Platform lead (via PR) | Superset dashboards, Databricks Apps, docs | YAML |
| Quarterly Programs | `ssot/governance/platform-strategy-2026.yaml` | Platform lead (via PR) | AzDo Boards (iteration mapping), docs | YAML |
| Initiatives (INIT-xxx) | `infra/ssot/ppm/portfolio.yaml` | Platform lead (via PR) | Ops-ppm-rollup, ops.ppm_initiatives table | YAML |
| Roadmap Initiatives (lifecycle) | Odoo (`ipai_product_roadmap`) | Odoo (API/UI) | Plane (projection), Supabase (mirror), Fabric/OneLake | Odoo ORM |
| Epics / Features | AzDo Boards (target) / Plane (current SoW) | AzDo: portfolio lead / Plane: team | GitHub (PR linking), Odoo (initiative linking) | Work items |
| Spec Bundles (feature goals) | `spec/<slug>/constitution.md` + `prd.md` | Feature owner (via PR) | Agents, CI validators, implementation | Markdown |
| Tasks (implementation) | `spec/<slug>/tasks.md` + GitHub Issues + Plane | Feature owner / team | CI, agents, dashboards | Markdown / platform |
| PR / Code linkage | GitHub | Engineers | CI, AzDo (linking), Plane (linking) | Git + GitHub API |

### Key distinction: Goal definitions vs. goal execution state

| Concern | SoR | Rationale |
|---------|-----|-----------|
| "What are our objectives and how do we measure them?" | In-repo YAML (`ssot/governance/`) | Governance artifact. Changes require PR + CI gate. |
| "What is the current status of initiative X?" | Odoo (`ipai_product_roadmap`) | Transactional state. Changes via Odoo API. |
| "What work items exist for this sprint?" | Plane (SoW) / AzDo Boards (target) | Execution tracking. Not goal definition. |
| "What features does spec X require?" | `spec/<slug>/prd.md` | Feature-level requirements. PR-governed. |

---

## 7. Consolidation Plan

### Phase 1: Formalize current state (immediate)

| Action | Owner | Deliverable |
|--------|-------|-------------|
| Add this decision document to the planning system index | Platform lead | Row in `planning_system_index.yaml` pointing to this ADR |
| Add CI validator for `platform-capabilities-unified.yaml` | Platform lead | Promote from candidate to canonical |
| Clean up `roadmap_crosswalk.yaml` placeholders | Platform lead | Resolve all `[NEEDS_CLARIFICATION]` entries or remove them |
| Confirm GitHub Projects v2 board state | Platform lead | Verify with `read:project` scoped token; document finding |

### Phase 2: Azure DevOps Boards operationalization (OBJ-002)

| Action | Owner | Deliverable |
|--------|-------|-------------|
| Seed AzDo Boards with 7 objectives as Epics | Platform lead | 7 epics in `ipai-platform` project, each tagged with OBJ-xxx ID |
| Map quarterly programs to AzDo iterations | Platform lead | 4 iteration paths (Q1-Q4 2026) |
| Create Features under each Epic for KR-level tracking | Platform lead | Features linked to KR IDs from `enterprise_okrs.yaml` |
| Build sync script: YAML objectives to AzDo Epics | Platform lead | `scripts/ci/sync_objectives_to_azdo.py` |
| Define graduation criteria (below) | Platform lead | Documented in this ADR |

### Phase 3: Authority transfer (conditional)

Azure DevOps Boards inherits portfolio SoR authority ONLY when ALL of the following gates pass:

| Gate | Criteria | Verification |
|------|----------|-------------|
| G1 | All 7 objectives exist as AzDo Epics with correct metadata | Script audit |
| G2 | All 22 KRs exist as AzDo Features linked to parent Epics | Script audit |
| G3 | AzDo Boards has been actively used for 2+ sprint cycles | Activity log |
| G4 | Sync script (YAML to AzDo) runs in CI on every merge to main | CI workflow exists and green |
| G5 | Rollback path documented (AzDo to YAML export) | Export script tested |

Until all 5 gates pass, the YAML layer remains authoritative and AzDo Boards is a projection.

### Deprecation schedule

| Artifact | Action | When |
|----------|--------|------|
| GitHub Issues (2 existing) | Close or migrate to Plane | Phase 1 |
| GitHub Projects v2 boards | If unused, archive. If active, document role and reconcile with AzDo. | Phase 1 |
| `roadmap_crosswalk.yaml` (if unfixable) | Deprecate and redirect to `platform-capabilities-unified.yaml` | Phase 1 |
| Notion task data in Supabase | Already deprecated. No action needed. | Done |
| YAML layer (post-graduation) | Retain as audit trail and CI-validated snapshot. AzDo becomes write surface. YAML is regenerated from AzDo. | Phase 3 (conditional) |

### What to keep permanently

| Artifact | Reason |
|----------|--------|
| `ssot/governance/platform-strategy-2026.yaml` | Vision, mission, doctrine, risks, evidence policy are governance constants. Even after AzDo graduation, these remain in-repo. |
| `ssot/governance/enterprise_okrs.yaml` | Thematic OKRs and KPI definitions are reference data, not execution data. They belong in version control. |
| `ssot/governance/planning_system_index.yaml` | Master index. Always in-repo. |
| `spec/` bundles | Feature-level truth. Always in-repo. |
| `infra/ssot/ppm/portfolio.yaml` | Initiative register. Stays until Odoo `ipai_product_roadmap` is fully operational and consuming it. |

---

## 8. Risks and Ambiguities

### R1: Dual-authority drift between YAML and AzDo

**Risk:** Once AzDo is seeded, two surfaces contain objective data. If updates happen in one but not the other, they diverge.

**Mitigation:** The sync script (Phase 2) must be bidirectional-aware. Define YAML as write-master until graduation. After graduation, define AzDo as write-master and YAML as generated output.

### R2: OBJ-002 never completes

**Risk:** AzDo operationalization remains "not yet started" indefinitely. The YAML layer becomes the permanent SoR by default.

**Mitigation:** This is acceptable. The YAML layer is a valid long-term SoR. The architecture does not require AzDo to function. AzDo is an enhancement for portfolio visibility, not a prerequisite for execution.

### R3: Odoo roadmap module vs. YAML goal definitions

**Risk:** `ROADMAP_TARGET_STATE.md` declares Odoo as the "sole write authority for roadmap entities." This could be interpreted as Odoo owning goal definitions, not just execution state.

**Mitigation:** Clarified in Section 6. Odoo owns roadmap initiative lifecycle (status, milestones, dependencies, KPI linkage). The YAML layer owns goal *definitions* (what the objectives are, what the KRs are, what the KPIs measure). These are different concerns. The `ipai_product_roadmap` module should consume objective IDs from YAML, not redefine them.

### R4: Plane scope creep

**Risk:** Teams start treating Plane as the de facto goal tracker because it has a UI and the YAML files do not.

**Mitigation:** Already mitigated by 4+ governance documents declaring Plane as SoW-only. Reinforce with: every Plane Epic must reference an `OBJ-xxx` ID from the YAML layer. Plane never defines new objectives.

### R5: GitHub Projects v2 state unknown

**Risk:** Active boards may exist with goal-like content that contradicts the YAML layer.

**Mitigation:** Phase 1 action: verify state with properly scoped token. If active, reconcile or archive.

### R6: KPI definitions split across two files

**Ambiguity:** KPIs appear in both `platform-strategy-2026.yaml` (13 KPIs) and `enterprise_okrs.yaml` (17 KPI references). The join is via `kpi_ref` fields.

**Resolution:** `platform-strategy-2026.yaml` is the KPI definition authority (it contains the full KPI objects). `enterprise_okrs.yaml` contains KPI *references* (pointers). This is correct relational design, not duplication. Document this explicitly in the planning index.

### R7: No dashboard or UI for YAML-based goals

**Ambiguity:** The YAML layer has CI validation but no human-friendly dashboard.

**Resolution:** This is intentional for now. The strategy explicitly routes dashboards through Superset and Databricks Apps. A CI-generated strategy status page (Markdown or HTML) could be added as a low-cost Phase 1 enhancement, but it is not a blocker.

---

## 9. Final Recommendation

| Surface | Recommendation | Timing |
|---------|---------------|--------|
| `ssot/governance/` YAML files | **Build now.** Formalize as canonical SoR. Add missing validators. This is the system that works today. | Immediate |
| `infra/ssot/ppm/portfolio.yaml` | **Build now.** Continue as initiative register. Add CI validator. | Immediate |
| `spec/` bundles | **Build now.** Already canonical. No changes needed. | Ongoing |
| Azure DevOps Boards | **Migrate later.** Seed and operationalize per OBJ-002. Do not grant authority until 5 graduation gates pass. | Q1-Q2 2026 |
| Odoo `ipai_product_roadmap` | **Build now.** Owns initiative execution state (status, milestones). Consumes objective IDs from YAML. Does not redefine goals. | Per roadmap |
| Plane | **Keep as SoW.** Never promote to SoR. Link every Epic to an `OBJ-xxx` ID. | Ongoing |
| Superset / Databricks Apps | **Build now.** Consume KPI data for dashboards. Read-only analytical surfaces. | Per roadmap |
| GitHub Issues | **Deprecate.** Close or migrate the 2 existing issues. Not a planning surface. | Immediate |
| GitHub Projects v2 | **Audit first.** Verify state. If unused, archive. If active, define bounded role and reconcile. | Phase 1 |
| Notion | **Avoid.** Already deprecated. Do not reintroduce. | Permanent |

### Summary decision

The in-repo YAML SSOT layer is the canonical system of record for strategic goals, effective immediately. Azure DevOps Boards is the declared target for portfolio-level SoR but authority transfer is gated by 5 explicit criteria. Odoo is the write authority for roadmap initiative execution state. Plane is the system of work. These four roles are complementary, not competing, and the boundaries between them are now explicit.

---

*Last updated: 2026-03-17*
*Decision author: Architecture review (agent-assisted)*
*Governance index: Register this ADR in `ssot/governance/planning_system_index.yaml` as a new `decisions` layer entry.*
