# Monorepo End-State — Implementation Plan

**Status**: Active
**Depends on**: constitution.md, prd.md

---

## EE Neutralization Operating Model

The following model ensures InsightPulse AI achieves EE feature parity without
using Odoo Enterprise Edition licenses.

```
EE Feature
    |
    v
Is there an OCA module?
    |-- YES -> Configure OCA module -> ipai_* override (if needed) -> DONE
    +-- NO -> Can it be bridged via external service?
                |-- YES -> Create IPAI bridge -> Register in ssot/bridges/catalog.yaml
                |           -> Create docs/contracts/ entry -> DONE
                +-- NO -> Document as gap in ee_to_oca_matrix.yaml (gap_type: no_alternative)
```

---

## Phase 1: Audit (Weeks 1-2)

**Goal**: Populate `ssot/parity/ee_to_oca_matrix.yaml` with all EE features relevant to InsightPulse AI.

### Tasks
- [ ] 1.1 List all EE-only features used or desired (source: Odoo docs + internal requirements)
- [ ] 1.2 For each feature, identify OCA alternatives (source: OCA GitHub org, v19 branch)
- [ ] 1.3 Populate matrix with at least 10 highest-priority features
- [ ] 1.4 Mark each with `gap_type`: `oca_available | ipai_bridge | no_alternative`

**Output**: `ssot/parity/ee_to_oca_matrix.yaml` with >=10 entries

---

## Phase 2: Bridge Registry (Weeks 2-3)

**Goal**: Formally register all active IPAI bridges.

### Tasks
- [ ] 2.1 Audit all `addons/ipai/` modules for external service integrations
- [ ] 2.2 Populate `ssot/bridges/catalog.yaml` with active bridges
- [ ] 2.3 Create `docs/contracts/MAIL_BRIDGE_CONTRACT.md` (Zoho Mail)
- [ ] 2.4 Create `docs/contracts/AI_BRIDGE_CONTRACT.md` (AI tools / Gemini)
- [ ] 2.5 Create `docs/contracts/OCR_BRIDGE_CONTRACT.md` (PaddleOCR)
- [ ] 2.6 Verify each active bridge has: catalog entry + contract doc + secrets registry entry

**Output**: Complete bridge catalog + 3 contract docs

---

## Phase 3: CI Gate (Week 3)

**Goal**: Automate enforcement of EE neutralization policy.

### Tasks
- [ ] 3.1 Create `.github/workflows/ee-parity-gate.yml`
- [ ] 3.2 Gate scans `addons/ipai/**/*.py` for `odoo.enterprise` imports
- [ ] 3.3 Gate scans `addons/ipai/**/__manifest__.py` for enterprise module names
- [ ] 3.4 Gate runs on all PRs targeting `main`
- [ ] 3.5 Document false-positive exemption mechanism (inline comment `# ee-parity-exempt`)

**Output**: Working CI gate that passes on current codebase

---

## Phase 4: Documentation Completion (Week 4)

**Goal**: Ensure all reference documents exist and are current.

### Tasks
- [ ] 4.1 Verify `docs/architecture/MONOREPO_END_STATE_OKR.md` is complete (Workstream A)
- [ ] 4.2 Verify `docs/architecture/AI_PROVIDER_BRIDGE.md` is complete (Workstream C)
- [ ] 4.3 Verify `docs/runbooks/SECRETS_SSOT.md` is complete (Workstream D)
- [ ] 4.4 Verify `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` is complete (Workstream D)
- [ ] 4.5 Update `docs/ai/SSOT.md` to reference new SSOT registries

**Output**: All 4 reference docs present and linked from SSOT

---

## Rollback Plan

This plan is additive-only (new files, new CI checks). Rollback = revert PRs.

No destructive changes to existing modules, workflows, or infrastructure.
