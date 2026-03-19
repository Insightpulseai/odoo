# TaxPulse Migration Plan

> Phased plan for consolidating all Philippine tax/BIR compliance assets
> into canonical repo locations.
> Generated: 2026-03-18

---

## Phase 0: Inventory + Freeze (This document)

**Duration**: Complete
**Status**: Done

### Deliverables

- [x] `docs/architecture/TAX_BIR_CONSOLIDATION_REPORT.md` -- full inventory
- [x] `docs/architecture/TAX_BIR_KNOWLEDGE_MAP.md` -- domain knowledge map
- [x] `ssot/domain/tax_bir_inventory.yaml` -- machine-readable inventory
- [x] `ssot/domain/tax_bir_gap_analysis.yaml` -- gap analysis
- [x] `docs/architecture/TAXPULSE_MIGRATION_PLAN.md` -- this plan
- [x] `docs/evidence/tax-bir-scan/README.md` -- scan evidence

### Freeze Rules

- No new tax/BIR assets created outside canonical locations until Phase 1 completes
- No deletion of any discovered assets without explicit approval
- All new work references this inventory

---

## Phase 1: Docs/Spec Consolidation

**Duration**: 1-2 sessions
**Priority**: P0
**Risk**: Low (documentation only, no code changes)

### 1.1 Remove Duplicate Spec Bundles

| Action | Source | Target |
|--------|--------|--------|
| Delete | `odoo/spec/tax-pulse-sub-agent/` | Keep `spec/tax-pulse-sub-agent/` (root) only |
| Delete | `odoo/odoo/docs/portfolio/specs/bir-tax-compliance/` | Keep one canonical location |
| Delete | `archive/root/docs/portfolio/specs/bir-tax-compliance/` | Remove archive copy |
| Delete | `odoo/odoo/archive/root/docs/portfolio/specs/bir-tax-compliance/` | Remove nested archive |
| Delete | `odoo/odoo/odoo/docs/portfolio/specs/bir-tax-compliance/` | Remove triple-nested |

### 1.2 Canonicalize Spec Locations

| Spec | Canonical Location | Notes |
|------|-------------------|-------|
| Tax Pulse Sub-Agent | `spec/tax-pulse-sub-agent/` | Primary Tax Pulse spec |
| TaxPulse-PH Port | `odoo/spec/taxpulse-ph-port/` | Port plan from legacy |
| IPAI Tax Engine | `odoo/spec/ipai-tax-engine/` | Supabase tax engine |
| Finance Unified | `odoo/spec/finance-unified/` | Unified finance system |
| AFC Parity | `odoo/spec/afc-parity/` | SAP parity |
| BIR Tax Compliance | `odoo/docs/portfolio/specs/bir-tax-compliance/` | Keep one copy only |

### 1.3 Fix Feature Registry

- Update `odoo/platform/registry/features/bir-compliance.json`: change `ipai_finance_bir_compliance` to `ipai_bir_tax_compliance`

### 1.4 Update SSOT References

- Verify all cross-references in SSOT YAML files point to canonical paths
- Update `docs/architecture/TAXPULSE_SALVAGE_MAP.md` with absorption status

---

## Phase 2: Odoo Domain Salvage

**Duration**: 2-3 sessions
**Priority**: P0
**Risk**: Medium (code changes to active module)

### 2.1 ATC Code Namespace Reconciliation

**Critical**: The highest-priority task.

| Action | Details |
|--------|---------|
| Adopt WI/WC namespace | Match BIR RR 11-2018 and Supabase schema |
| Update `ewt.rules.yaml` | Rename W010 -> WI010, W020 -> WC010, etc. with individual/corporate distinction |
| Update `ph_rates_2025.json` | Rename to WI/WC codes |
| Update test fixtures | Align expected values with new codes |
| Run all tests | Verify no regression |

### 2.2 Add Missing Rules Packs

| Pack | Priority | Action |
|------|----------|--------|
| `fwt.rules.yaml` | P1 | Create from F001-F005 in ph_rates_2025.json |
| `compensation.rules.yaml` | P2 | Create from TRAIN brackets (optional -- may stay as Python) |
| Expand EWT rules | P1 | Add missing ATC codes from Supabase matrix |

### 2.3 Audit Odoo Models

- Verify existence of: `bir.filing.deadline`, `bir.vat.return`, `bir.withholding.return`, `bir.tax.return`, `bir.alphalist`
- Create any missing models referenced by tool contracts
- Add security groups: `group_ipai_bir_approver`, `group_ipai_finance_manager`

### 2.4 Create QWeb Report Templates

| Form | Priority | Template Path |
|------|----------|--------------|
| 1601-C | P1 | `reports/report_bir_1601c.xml` |
| 2550Q | P1 | `reports/report_bir_2550q.xml` |
| 1702-RT | P2 | `reports/report_bir_1702rt.xml` |
| 2307 | P1 | `reports/report_bir_2307.xml` |

### 2.5 Install Companion Modules

- Test install `ipai_bir_notifications` in `test_ipai_bir_notifications`
- Test install `ipai_bir_plane_sync` in `test_ipai_bir_plane_sync`
- Install in `odoo_dev` if tests pass

---

## Phase 3: Agent/Platform Salvage

**Duration**: 2-3 sessions
**Priority**: P1
**Risk**: Medium

### 3.1 Absorb TaxPulse AI Review Engine

| Component | Source | Target | Action |
|-----------|--------|--------|--------|
| 5-dimension scoring rubric | `jgtolentino/TaxPulse-PH-Pack` | `agents/` | Port scoring logic |
| Review protocol | Same | `agents/foundry/` | Adapt for Azure Foundry |
| finance-tax-pulse Edge Function | Same | `odoo/supabase/functions/` | Review and port |

### 3.2 Create Bridge OpenAPI Spec

- Create `agents/contracts/openapi/ipai_odoo_bridge.openapi.yaml` from tool contracts SSOT
- Validate against tool contract definitions

### 3.3 Build n8n BIR Form Generation Workflow

- Implement the workflow documented in `odoo/platform/bridges/bir-form-generation/README.md`
- Generate .dat files per eBIRForms specification
- Test with demo data

### 3.4 Create Demo Account Moves

- Create demo XML in `ipai_bir_tax_compliance/demo/` with:
  - Vendor bills with EWT tax lines
  - Customer invoices with Output VAT
  - Purchase invoices with Input VAT
  - Bills with multiple ATC codes

---

## Phase 4: Benchmark Harness

**Duration**: 2-3 sessions
**Priority**: P1
**Risk**: Low

### 4.1 End-to-End Test Harness

Build `tests/integration/test_bir_e2e.py`:
1. Create test account.move records in Odoo test DB
2. Trigger tax-compute webhook (mock or real)
3. Verify ops.tax_findings in Supabase
4. Verify risk scoring matches expected values
5. Verify BIR form generation pipeline

### 4.2 BIR-Specific Eval Datasets

| Dataset | Cases | Priority |
|---------|-------|----------|
| `bir_advisory.yaml` | 50 informational | P1 |
| `bir_ops.yaml` | 30 navigational | P1 |
| `bir_actions.yaml` | 40 transactional | P1 |

### 4.3 Golden Dataset

- Obtain accountant-verified BIR form computations for representative periods
- Create golden fixture files per form type
- Add to test suite as regression tests

### 4.4 SFT Training Assets

| Asset | Priority |
|-------|----------|
| `bir_sft_catalog.yaml` | P2 |
| `bir_sft_train.jsonl` | P2 |
| `bir_sft_valid.jsonl` | P2 |

---

## Phase 5: Production Hardening

**Duration**: 2-4 sessions
**Priority**: P2
**Risk**: Medium-High

### 5.1 eBIRForms XML Export

- Implement XML generation matching eBIRForms v7.9.5 format
- Add schema validation (obtain or reverse-engineer XSD)
- Test with eBIRForms offline software import

### 5.2 Approval Workflow

- Implement PLM-style approval gates in Odoo
- Wire approval flow: Router pauses -> Activity created -> Approver acts -> Router resumes
- Test all approval paths for transactional tools

### 5.3 eFPS Integration PoC

- Build Playwright-based browser automation PoC
- Document eFPS XML submission path
- Evaluate reliability and maintenance cost

### 5.4 CI Gates

- Add BIR computation tests to CI pipeline
- Add ATC namespace consistency check
- Add spec validation for tax-related bundles

---

## Phase Dependencies

```
Phase 0 (Inventory) ──┐
                       ├── Phase 1 (Docs) ──── Phase 2 (Odoo) ──┐
                       │                                          ├── Phase 4 (Benchmark)
                       └── Phase 3 (Agent/Platform) ──────────────┘
                                                                   │
                                                               Phase 5 (Hardening)
```

---

## Success Criteria

| Phase | Criterion |
|-------|-----------|
| 0 | All 6 output files created, inventory complete |
| 1 | Zero duplicate spec bundles, all references canonical |
| 2 | ATC namespaces reconciled, rules engine green, models verified |
| 3 | AI review engine absorbed, bridge API spec created |
| 4 | E2E test harness passing, 120 eval cases created |
| 5 | eBIRForms XML export functional, approval gates enforced |

---

*Generated: 2026-03-18*
