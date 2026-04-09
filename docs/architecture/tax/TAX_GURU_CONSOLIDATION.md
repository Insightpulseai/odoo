# Tax Guru Copilot — Consolidation Report

> Canonical consolidation of all tax/BIR compliance skills, tools, agents, modules,
> workflows, prompts, docs, specs, automations, and data contracts into one coherent system.
> Date: 2026-04-01
> Predecessor: `docs/architecture/tax/BIR_CONSOLIDATION.md` (2026-03-18 scan)
> Spec path: `spec/pulser-{platform,agents,web,odoo}/` (Tax Guru phases in each)

---

## 1. Executive Summary

**68 tax/BIR assets** were inventoried in the 2026-03-18 scan. This consolidation report updates that inventory against the new Pulser layered architecture (decided 2026-04-01) and resolves the scattered ownership into one canonical model.

**Key changes since the 2026-03-18 scan:**
- Tax Guru Copilot formally defined as a Pulser sub-agent (not a standalone product)
- TaxPulse-PH-Pack confirmed as a bounded PH execution pack, not the whole Tax Guru
- Joule capability taxonomy applied: transactional / navigational / informational
- 4-repo Pulser spec bundles created with Tax Guru phases (P5/R5/W5/O5)
- Supabase fully deprecated (2026-03-26) — all Supabase tax assets require migration to Azure-native

**Critical blockers (unchanged):**
- ATC code namespace divergence (W-series vs WI/WC-series) — must reconcile before any production tax workflow
- Supabase tax engine schema must migrate to Azure-native (PG on `pg-ipai-odoo` or Databricks)
- No end-to-end test harness connecting Odoo → tax compute → agent → evidence

---

## 2. Canonical Inventory

### A. Odoo Modules (keep — canonical execution layer)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| OM-1 | `ipai_bir_tax_compliance` | `addons/ipai/ipai_bir_tax_compliance/` | **Canonical** | Keep — primary BIR module |
| OM-2 | `ipai_bir_compliance` | `addons/ipai/ipai_bir_compliance/` | Partial | Merge into OM-1 or deprecate |
| OM-3 | `ipai_finance_ppm` (BIR demo data) | `addons/ipai/ipai_finance_ppm/demo/` | Active | Keep — month-end BIR seeds |
| OM-4 | `ipai_finance_close_seed` (BIR tasks) | `addons/ipai/ipai_finance_close_seed/data/` | Active | Keep — close task seeds |

### B. Rules Engine (keep — inside OM-1)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| RE-1 | JSONLogic evaluator | `addons/ipai/ipai_bir_tax_compliance/engine/evaluator.py` | Canonical | Keep |
| RE-2 | Formula engine | `addons/ipai/ipai_bir_tax_compliance/engine/formula.py` | Canonical | Keep |
| RE-3 | Rules loader | `addons/ipai/ipai_bir_tax_compliance/engine/loader.py` | Canonical | Keep |
| RE-4 | EWT rules pack | `addons/ipai/ipai_bir_tax_compliance/data/rules/ewt.rules.yaml` | Active | Keep — reconcile ATC codes |
| RE-5 | VAT rules pack | `addons/ipai/ipai_bir_tax_compliance/data/rules/vat.rules.yaml` | Active | Keep |
| RE-6 | PH rates 2025 | `addons/ipai/ipai_bir_tax_compliance/data/rates/ph_rates_2025.json` | Active | Keep — reconcile ATC codes |

### C. Agent Skills (keep — in `agents`)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| SK-1 | `taxpulse-ph-pack` skill | `agents/skills/odoo/taxpulse-ph-pack/SKILL.md` | Canonical | Keep — reference skill for PH pack |
| SK-2 | `bir-tax-filing` skill | `agents/skills/bir-tax-filing/SKILL.md` | Active | Keep — filing workflow skill |
| SK-3 | `bir-eservices` skill | `agents/skills/odoo/bir-eservices/SKILL.md` | Active | Keep — eFPS/eBIRForms roadmap |
| SK-4 | `ph-close-tax-pack` prompt | `agents/library/prompts/finance/ph-close-tax-pack.md` | Active | Keep — close-cycle tax prompt |
| SK-5 | Finance close specialist | `agents/library-pack/prompts/agents/finance_close_specialist.md` | Tangential | Keep — references tax in close context |
| SK-6 | Diva copilot tax-guru persona | `agents/personas/diva-copilot-tax-guru.md` | Active | Rename to `pulser-tax-guru.md` |

### D. Knowledge Base (keep — in `agents`)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| KB-1 | BIR forms reference | `agents/knowledge-base/bir-compliance/bir-forms-reference.md` | Canonical | Keep |
| KB-2 | BIR filing calendar | `agents/knowledge-base/bir-compliance/bir-filing-calendar.md` | Canonical | Keep |
| KB-3 | VAT compliance guide | `agents/knowledge-base/bir-compliance/vat-compliance-guide.md` | Canonical | Keep |
| KB-4 | Withholding tax guide | `agents/knowledge-base/bir-compliance/withholding-tax-guide.md` | Canonical | Keep |
| KB-5 | BIR eServices benchmark | `agents/knowledge/benchmarks/bir-eservices-ebirforms.md` | Active | Keep |
| KB-6 | SAP tax compliance agent | `agents/knowledge-base/finance-close-kb/sap-tax-compliance-agent.md` | Reference | Keep — benchmark reference |
| KB-7 | PH tax taxonomy | `agents/library-pack/schemas/taxonomy/philippines_tax.yaml` | Active | Keep — canonical PH taxonomy |
| KB-8 | Odoo tax runtime KB | `agents/knowledge/kb_odoo_tax_runtime.yaml` | Active | Keep |

### E. Spec Bundles (consolidate)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| SP-1 | `tax-pulse-sub-agent` | `spec/tax-pulse-sub-agent/` | **Canonical** | Keep — original Tax Pulse spec |
| SP-2 | `pulser-platform` (Tax Guru P5) | `spec/pulser-platform/` | **Canonical** | Keep — control plane objects |
| SP-3 | `pulser-agents` (Tax Guru R5) | `spec/pulser-agents/` | **Canonical** | Keep — agent runtime objects |
| SP-4 | `pulser-web` (Tax Guru W5) | `spec/pulser-web/` | **Canonical** | Keep — web surfaces |
| SP-5 | `pulser-odoo` (Tax Guru O5) | `spec/pulser-odoo/` | **Canonical** | Keep — Odoo adapter objects |
| SP-6 | `tax-pulse-sub-agent` (nested dupe) | `odoo/spec/tax-pulse-sub-agent/` | **Duplicate** | Delete — dupe of SP-1 |
| SP-7 | `taxpulse-ph-port` | `odoo/spec/taxpulse-ph-port/` | Partial | Archive — port plan from legacy |
| SP-8 | `ipai-tax-engine` | `odoo/spec/ipai-tax-engine/` | Stale | Archive — Supabase tax engine (deprecated) |
| SP-9 | `bir-tax-compliance` (portfolio, 3+ copies) | `odoo/docs/portfolio/specs/bir-tax-compliance/` + archives | **Duplicate** | Delete all except one canonical |

### F. SSOT / Domain Data (keep — reconcile)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| SS-1 | Tax BIR inventory | `ssot/domain/tax_bir_inventory.yaml` | Canonical | Keep — update with this consolidation |
| SS-2 | Tax BIR gap analysis | `ssot/domain/tax_bir_gap_analysis.yaml` | Active | Keep — update status |
| SS-3 | ATC code mapping | `ssot/domain/atc_code_mapping.yaml` | Active | Keep — **P0: reconcile W vs WI/WC** |
| SS-4 | Tax Pulse tool contracts | `infra/ssot/agents/tax_pulse_tool_contracts.yaml` | Active | Keep |
| SS-5 | Agent capability matrix | `infra/ssot/agents/agent_capability_matrix.yaml` | Tangential | Keep — references tax capabilities |
| SS-6 | Benchmark gap analysis | `infra/ssot/evals/tax_bir_benchmark_gap_analysis.yaml` | Active | Keep |
| SS-7 | Benchmark test inventory | `infra/ssot/evals/tax_bir_benchmark_test_inventory.yaml` | Active | Keep |
| SS-8 | Finance scenario library | `ssot/finance/scenario-library.yaml` | Canonical | Keep — Tax compliance scenarios |

### G. Architecture Docs (keep — reference)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| AD-1 | BIR Consolidation Report | `docs/architecture/tax/BIR_CONSOLIDATION.md` | Canonical | Keep — predecessor to this doc |
| AD-2 | BIR Knowledge Map | `docs/architecture/tax/BIR_KNOWLEDGE_MAP.md` | Active | Keep |
| AD-3 | BIR Migration Plan | `docs/architecture/tax/BIR_MIGRATION_PLAN.md` | Active | Keep — update phase status |
| AD-4 | BIR Test Consolidation | `docs/architecture/tax/BIR_TEST_CONSOLIDATION.md` | Active | Keep |
| AD-5 | TaxPulse Migration | `docs/architecture/tax/TAXPULSE_MIGRATION.md` | Active | Keep — update with Pulser alignment |
| AD-6 | TaxPulse Salvage | `docs/architecture/tax/TAXPULSE_SALVAGE.md` | Reference | Keep |
| AD-7 | Tax Guru Consolidation | `docs/architecture/tax/TAX_GURU_CONSOLIDATION.md` | **This doc** | Canonical |
| AD-8 | Benchmark Avalara | `docs/architecture/agents/BENCHMARK_AVALARA.md` | Reference | Keep |
| AD-9 | SAP Tax Compliance taxonomy | `docs/research/tax-compliance-ph-odoo/tax-compliance-capability-taxonomy.md` | Reference | Keep |
| AD-10 | SAP Tax Compliance object model | `docs/research/tax-compliance-ph-odoo/tax-compliance-object-model.md` | Reference | Keep |

### H. Supabase Assets (migrate or archive)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| SB-1 | BIR Tax Engine schema | `odoo/supabase/migrations/20260317_bir_tax_engine.sql` | **Stale** | Archive — Supabase deprecated; migrate schema to PG |
| SB-2 | BIR Forms registry migration | `odoo/supabase/migrations/20260212000001_registry_bir_forms.sql` | **Stale** | Archive |
| SB-3 | Tax compute Edge Function | `odoo/supabase/functions/tax-compute/index.ts` | **Stale** | Archive — replace with Azure Function or Odoo engine |
| SB-4 | BIR urgent alert function | `odoo/supabase/functions/bir-urgent-alert/index.ts` | **Stale** | Archive |
| SB-5 | Tax compliance workstream seeds | `odoo/supabase/seeds/workstreams/stc_tax_compliance/` | **Stale** | Archive — migrate to Odoo seed data |
| SB-6 | BIR data seeds (CSV/XML/JSON) | `odoo/supabase/data/` (multiple) | **Stale** | Archive — migrate to Odoo demo data |

### I. Platform / Bridges (review)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| PB-1 | BIR form generation bridge | `platform/bridges/bir-form-generation/README.md` | Active | Keep — document integration pattern |
| PB-2 | E-filing automation bridge | `platform/bridges/efiling-automation/README.md` | Active | Keep |

### J. Workflows / Automations (keep)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| WF-1 | Odoo tax assist workflow | `agents/workflows/odoo-tax-assist.yaml` | Active | Keep — canonical tax workflow |
| WF-2 | Finance actions (tax) | `agents/actions/finance.py` | Active | Keep |

### K. CI / Evals (keep)

| ID | Asset | Path | Status | Disposition |
|----|-------|------|--------|-------------|
| EV-1 | Copilot eval dataset v2 (tax cases) | `agents/evals/odoo-copilot/datasets/` | Active | Keep — expand BIR cases |
| EV-2 | AP tax eval summary | `docs/evidence/ap-invoice-eval/ap-tax-eval-summary.md` | Active | Keep |
| EV-3 | Tax BIR benchmark scan evidence | `docs/evidence/tax-bir-benchmark-scan/` | Evidence | Keep |
| EV-4 | Tax BIR scan evidence | `docs/evidence/tax-bir-scan/` | Evidence | Keep |

---

## 3. Canonical Taxonomy

```yaml
capability_types:
  - transactional    # create/update/approve/file tax actions
  - navigational     # guide to tax config/forms/queues/reports
  - informational    # explain rules, answer policy, summarize status

capability_domains:
  - ph_bir_compliance      # BIR form generation, filing, deadline tracking
  - tax_determination      # withholding/VAT/income tax computation
  - filing_prep            # pre-filing validation, readiness checks
  - collections            # AR tax treatment, overdue tax items
  - ap_ar_tax_treatment    # AP/AR invoice tax classification
  - tax_policy_guidance    # BIR regulation explanation, policy Q&A
  - tax_grounding          # document/knowledge grounding for tax answers
  - tax_analytics          # curated tax marts, compliance KPIs
  - tax_exception_review   # exception triage, variance investigation

runtime_layers:
  - control_plane          # platform: registry, capability packages, promotion
  - reasoning_agent        # agents: Tax Guru reasoning, workflows, evals
  - workflow               # agents: graph-based deterministic tax processes
  - execution_adapter      # odoo: safe actions, context assembly, BIR execution
  - ui_surface             # web: workbench, exception queue, evidence viewer
  - analytical_model       # data-intelligence: curated tax compliance marts
  - grounding_source       # agents: BIR regulations, policy documents
  - evidence_export        # platform + odoo: audit trail, evidence artifacts
```

---

## 4. Ownership Map

### `platform` — Tax Control Plane

| Object | Description |
|--------|-------------|
| PulserTaxRuleSource | Tax rule authority registry (BIR, company policy, external engine) |
| PulserTaxJurisdictionProfile | Jurisdiction metadata (PH, company, agency) |
| PulserTaxCapabilityProfile | Per-capability config (type, jurisdictions, action modes, roles) |
| PulserTaxEvidenceBundle | Transaction-level evidence (rule sources, docs, confidence) |
| PulserTaxExceptionCase | Exception tracking (type, severity, assignment) |
| Tax capability packages | 7 packages: `pulser_tax_{info,navigation,actions,grounding,exception_review,policy_guidance,filing_prep}` |

### `agents` — Tax Guru Reasoning

| Object | Description |
|--------|-------------|
| PulserTaxDeterminationRequest/Result | Tax computation workflow (jurisdiction → type → taxability → evidence) |
| PulserTaxPolicyAnswer | Policy Q&A with rule source refs and evidence |
| PulserTaxActionProposal | Proposed tax action with risk level and approval mode |
| Tax reasoning workflows | `agents/workflows/odoo-tax-assist.yaml` + Tax Guru determination graphs |
| Tax skills | `taxpulse-ph-pack`, `bir-tax-filing`, `bir-eservices` |
| Tax knowledge base | `agents/knowledge-base/bir-compliance/` (4 articles) |
| Tax evals | BIR-specific eval datasets (expand from current copilot evals) |

### `web` — Tax Experience

| Surface | Description |
|---------|-------------|
| PulserTaxDecisionCard | Tax treatment summary with confidence and evidence |
| PulserTaxExceptionQueueView | Exception list with filters and bulk actions |
| PulserTaxEvidenceView | Audit-ready evidence bundle display |
| Tax preview/admin shell | DevUI-like testing for tax capabilities |

### `odoo` — Tax Execution Adapter

| Object | Description |
|--------|-------------|
| `ipai_bir_tax_compliance` module | Canonical BIR module (rules engine, rates, forms) |
| `ipai.pulser.tax_context` | Record-aware tax context assembly |
| `ipai.pulser.tax_action_request` | Safe tax action proposals (suggest_only default) |
| `ipai.pulser.tax_exception_event` | Exception emission to platform |
| TaxPulse-PH-Pack integration | Bounded PH domain pack (BIR forms, computations, agencies) |
| FastAPI tax endpoints | `GET /api/v1/pulser/tax/context/{model}/{id}`, `POST /api/v1/pulser/tax/action`, `POST /api/v1/pulser/tax/exception` |

### `data-intelligence` — Tax Analytics (future)

| Object | Description |
|--------|-------------|
| Tax compliance mart | Gold-layer mart: filing status, exception rates, compliance KPIs |
| BIR deadline tracking | Filing readiness by form/period/agency |

### `.github` — Tax CI Enforcement

| Check | Description |
|-------|-------------|
| ATC code consistency | Validate ATC codes match `ssot/domain/atc_code_mapping.yaml` |
| Tax capability registration | All tax capability packages must be registered |
| Duplicate detection | No duplicate tax capability names across repos |

---

## 5. Consolidated Target Architecture

```
Tax Guru Copilot (Pulser sub-agent)
├── Domain Packs
│   ├── TaxPulse-PH-Pack (PH BIR compliance, active)
│   │   └── ipai_bir_tax_compliance module
│   │       ├── engine/ (JSONLogic evaluator, formula, loader)
│   │       ├── data/rules/ (EWT, VAT rules packs)
│   │       ├── data/rates/ (PH rates 2025)
│   │       └── tests/ (EWT, VAT, engine tests)
│   ├── future VAT/GST global pack
│   ├── future withholding pack
│   └── future filing-prep pack
│
├── Control Plane (platform)
│   ├── Tax capability packages (7)
│   ├── Tax rule source registry
│   ├── Tax jurisdiction profiles
│   ├── Tax evidence bundles
│   └── Tax exception cases
│
├── Reasoning Layer (agents)
│   ├── Tax determination workflows
│   ├── Tax policy Q&A (grounded)
│   ├── Tax action proposals
│   ├── Tax skills (3) + KB (4 articles)
│   ├── Tax evals (BIR-specific datasets)
│   └── Tax persona (pulser-tax-guru)
│
├── Experience Layer (web)
│   ├── Tax decision card
│   ├── Tax exception queue
│   ├── Tax evidence viewer
│   └── Tax preview/admin shell
│
└── Execution Adapter (odoo)
    ├── Tax context assembly
    ├── Safe tax actions (suggest_only default)
    ├── Tax exception emission
    └── FastAPI tax endpoints
```

---

## 6. Minimal Spec Kit Deltas

Spec bundles already exist with Tax Guru phases. No new spec bundle is needed.

### Existing canonical spec paths

| Repo Scope | Spec Path | Tax Guru Phase |
|------------|-----------|----------------|
| Control plane | `spec/pulser-platform/` | Phase P5 (7 tasks) |
| Agent runtime | `spec/pulser-agents/` | Phase R5 (7 tasks) |
| Web surfaces | `spec/pulser-web/` | Phase W5 (5 tasks) |
| Odoo adapter | `spec/pulser-odoo/` | Phase O5 (8 tasks) |
| Original Tax Pulse | `spec/tax-pulse-sub-agent/` | Keep as reference — subsumed by Pulser phases |

### Required updates to `spec/tax-pulse-sub-agent/prd.md`

Add at the top of the PRD:

```markdown
> **Supersession notice**: Tax Pulse Sub-Agent is now part of the Pulser Assistant layered
> architecture. Implementation tasks have been distributed across:
> - `spec/pulser-platform/` Phase P5 (control plane objects)
> - `spec/pulser-agents/` Phase R5 (reasoning workflows)
> - `spec/pulser-web/` Phase W5 (web surfaces)
> - `spec/pulser-odoo/` Phase O5 (Odoo adapter)
>
> This PRD remains the canonical domain requirements reference for PH BIR tax compliance.
> The Pulser spec phases implement it.
```

---

## 7. Consolidation Roadmap

### Phase 0: Cleanup (P0, no code risk)

| # | Action | Status |
|---|--------|--------|
| 0.1 | Delete duplicate `odoo/spec/tax-pulse-sub-agent/` | Pending |
| 0.2 | Delete duplicate `bir-tax-compliance` portfolio specs (3+ copies) | Pending |
| 0.3 | Add supersession notice to `spec/tax-pulse-sub-agent/prd.md` | Pending |
| 0.4 | Rename `agents/personas/diva-copilot-tax-guru.md` → `pulser-tax-guru.md` | Pending |
| 0.5 | Update `ssot/domain/tax_bir_inventory.yaml` to reference Pulser phases | Pending |

### Phase 1: ATC Code Reconciliation (P0, critical blocker)

| # | Action | Status |
|---|--------|--------|
| 1.1 | Finalize canonical ATC namespace in `ssot/domain/atc_code_mapping.yaml` | Pending |
| 1.2 | Update `data/rules/ewt.rules.yaml` to use canonical codes | Pending |
| 1.3 | Update `data/rates/ph_rates_2025.json` to use canonical codes | Pending |
| 1.4 | Add CI check for ATC code consistency | Pending |

### Phase 2: Supabase Migration (P1, deprecation-driven)

| # | Action | Status |
|---|--------|--------|
| 2.1 | Archive `odoo/supabase/migrations/20260317_bir_tax_engine.sql` | Pending |
| 2.2 | Archive `odoo/supabase/functions/tax-compute/` | Pending |
| 2.3 | Archive `odoo/supabase/seeds/workstreams/stc_tax_compliance/` | Pending |
| 2.4 | Migrate essential schema objects to `pg-ipai-odoo` or Odoo models | Pending |
| 2.5 | Replace tax-compute Edge Function with Odoo engine + agent workflow | Pending |

### Phase 3: Pulser Tax Guru Implementation (P1-P2, per Pulser phases)

| # | Action | Spec Phase |
|---|--------|-----------|
| 3.1 | Implement platform Tax Guru objects | `pulser-platform` P5 |
| 3.2 | Implement agent Tax Guru workflows | `pulser-agents` R5 |
| 3.3 | Implement web Tax Guru surfaces | `pulser-web` W5 |
| 3.4 | Implement Odoo Tax Guru adapter | `pulser-odoo` O5 |
| 3.5 | Create BIR-specific eval datasets (120 cases) | `pulser-agents` R5.5 |

### Phase 4: TaxPulse-PH-Pack Absorption (P2)

| # | Action | Status |
|---|--------|--------|
| 4.1 | Absorb BIR form models from TaxPulse-PH-Pack into `ipai_bir_tax_compliance` | Pending |
| 4.2 | Absorb multi-agency framework (8 entities) | Pending |
| 4.3 | Absorb AI review engine into `agents/` as Tax Guru eval/scoring | Pending |
| 4.4 | Absorb validation rules (18 rules) into canonical module | Pending |
| 4.5 | Absorb authority sources config into agents grounding registry | Pending |

### Phase 5: Production Hardening (P2-P3)

| # | Action | Status |
|---|--------|--------|
| 5.1 | End-to-end test harness (Odoo → agent → evidence) | Pending |
| 5.2 | eBIRForms XML export implementation | Pending |
| 5.3 | BIR form PDF report templates | Pending |
| 5.4 | eFPS integration PoC | Pending |

---

## 8. Risks / Drift / Open Assumptions

### Critical Risks

1. **ATC code divergence** (unchanged from 2026-03-18): W-series vs WI/WC-series. Must resolve before any production tax workflow. See `ssot/domain/atc_code_mapping.yaml`.

2. **Supabase tax engine migration**: The tax-compute Edge Function and BIR schema in Supabase are stale but contain logic not yet replicated in Odoo or agents. Risk of losing computation capability during migration.

3. **TaxPulse-PH-Pack not absorbed**: 38 assets catalogued (TXP-001 through TXP-038), only the rules engine partially ported. AI review engine, multi-agency framework, authority sources, and protocol system remain unported.

### Drift Risks

4. **Spec proliferation**: 5+ spec locations reference tax (tax-pulse-sub-agent, pulser-*, finance-unified, ipai-tax-engine, taxpulse-ph-port, bir-tax-compliance portfolio). Risk of specs drifting apart.

5. **Odoo becoming the entire tax control plane**: The `ipai_bir_tax_compliance` module is rich but must remain an execution pack, not the policy/reasoning authority.

### Assumptions

6. **Odoo 18 CE is canonical** — all tax module development targets Odoo 18.
7. **Azure-native only** — no Supabase, no Cloudflare, no DigitalOcean in tax flows.
8. **PH-first** — Tax Guru starts with Philippine BIR compliance; global expansion is future.
9. **Informational + navigational first** — transactional tax actions deferred to later phases.
10. **TaxPulse-PH-Pack repo** (`jgtolentino/TaxPulse-PH-Pack`) is external reference, not vendored.

---

## 9. CI / Enforcement Recommendations

| Check | Scope | Description |
|-------|-------|-------------|
| `tax-atc-consistency` | `.github` | Validate all ATC codes in rules/rates match `ssot/domain/atc_code_mapping.yaml` |
| `tax-capability-registration` | `.github` | Every `pulser_tax_*` capability package must be registered in platform registry |
| `tax-no-duplicates` | `.github` | No duplicate tax capability names across repos |
| `tax-evidence-required` | `.github` | Promoted tax capabilities must have evidence artifacts |
| `tax-taxonomy-drift` | `.github` | Validate capability types match canonical taxonomy |
| `tax-deprecated-detection` | `.github` | Flag Supabase references in tax code paths |
| `tax-ownership-boundary` | `.github` | Tax reasoning in `agents` only, tax execution in `odoo` only, no cross-boundary leakage |

---

## Decision Record

**Date**: 2026-04-01
**Decision**: Consolidate all tax/BIR assets under the Pulser Tax Guru sub-agent architecture.
**Supersedes**: Ad-hoc scatter across 68 assets in 4+ locations.
**Canonical spec path**: Tax Guru phases inside `spec/pulser-{platform,agents,web,odoo}/`.
**Reference spec**: `spec/tax-pulse-sub-agent/` (domain requirements, subsumed by Pulser phases).
**Status**: Approved — consolidation roadmap active.
