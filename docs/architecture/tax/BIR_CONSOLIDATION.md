# Tax/BIR Consolidation Report

> Comprehensive inventory and migration plan for all Philippine tax/BIR-related
> assets across the InsightPulse AI org repos.
> Generated: 2026-03-18 | Scan scope: `Insightpulseai/odoo`, `Insightpulseai/agents`

---

## Executive Summary

Philippine tax/BIR compliance work is distributed across **3 repos** and **1 external precursor**:

1. **`Insightpulseai/odoo`** (primary working repo) -- contains Odoo modules, specs, SSOT, seeds, scripts
2. **`Insightpulseai/odoo/odoo/`** (nested submodule/subtree) -- contains duplicated specs, Supabase schema, platform bridges, deep nested portfolio specs
3. **`Insightpulseai/agents`** -- contains agent skills, knowledge-base articles, foundry agent manifests, evaluation datasets, benchmark docs
4. **`jgtolentino/TaxPulse-PH-Pack`** (external precursor, not yet absorbed) -- the upstream source for rules engine, multi-agency framework, AI review

**Key findings:**
- **68 distinct tax/BIR assets** identified across all repos
- **12 duplicate groups** where the same content exists in 2+ locations (spec bundles, portfolio specs, seeds)
- **The `ipai_bir_tax_compliance` Odoo module** is the canonical BIR compliance module with a working JSONLogic rules engine, rate tables, and test fixtures
- **Supabase has a full tax engine schema** (`20260317_bir_tax_engine.sql`) with ATC master data, risk scoring, and BIR form generation tables
- **The `tax-compute` Edge Function** is a working Deno function that processes Odoo move lines, resolves ATC codes, computes EWT, and scores risk
- **Agent knowledge is well-structured** with 4 KB articles, 3 skills, and evaluation datasets
- **The legacy TaxPulse-PH-Pack** has not been absorbed -- it contains the upstream computation engine that `ipai_bir_tax_compliance` was ported from

**Critical gaps:**
- No end-to-end test harness connecting Odoo -> Supabase -> Agent
- No eBIRForms XML generation implemented (stubbed only)
- No eFPS integration
- No BIR form PDF report templates in Odoo
- `ipai_bir_notifications` and `ipai_bir_plane_sync` modules exist but are not installed
- No seed/demo data for the Supabase tax engine schema (ATC matrix is in migration SQL only)

---

## Repos Scanned

| Repo | Path | Status |
|------|------|--------|
| `Insightpulseai/odoo` | `/Users/tbwa/Documents/GitHub/Insightpulseai/odoo` | Primary -- active |
| `Insightpulseai/odoo` (nested) | `.../odoo/odoo/` | Nested subtree -- contains duplicated content |
| `Insightpulseai/agents` | `/Users/tbwa/Documents/GitHub/Insightpulseai/agents` | Active -- agent skills, KB, evals |
| `jgtolentino/TaxPulse-PH-Pack` | External (not cloned locally) | Precursor -- documented via salvage map |

---

## Findings by Repo

### 1. `Insightpulseai/odoo` (root)

#### Odoo Modules

| Asset | Path | Type | Status |
|-------|------|------|--------|
| `ipai_bir_tax_compliance` | `addons/ipai/ipai_bir_tax_compliance/` | Odoo module | Active -- rules engine, rates, tests |
| `ipai_finance_ppm` | `addons/ipai/ipai_finance_ppm/` | Odoo module | Active -- month-end close orchestration, BIR demo data |
| `ipai_finance_close_seed` | `addons/ipai/ipai_finance_close_seed/` | Odoo module | Active -- BIR task seeds (`07_tasks_bir_tax.xml`, `tasks_bir.csv`, `tasks_bir.xml`) |

#### Rules Engine (inside `ipai_bir_tax_compliance`)

| Asset | Path | Description |
|-------|------|-------------|
| JSONLogic evaluator | `addons/ipai/ipai_bir_tax_compliance/engine/evaluator.py` | Full JSONLogic evaluator with 14 operators |
| Formula engine | `addons/ipai/ipai_bir_tax_compliance/engine/formula.py` | Aggregation formulas (SUM, etc.) |
| Rules loader | `addons/ipai/ipai_bir_tax_compliance/engine/loader.py` | YAML rules file loader |
| EWT rules | `addons/ipai/ipai_bir_tax_compliance/data/rules/ewt.rules.yaml` | 10 EWT rules + aggregation (W010-W170) |
| VAT rules | `addons/ipai/ipai_bir_tax_compliance/data/rules/vat.rules.yaml` | 8 VAT computation rules |
| PH rates 2025 | `addons/ipai/ipai_bir_tax_compliance/data/rates/ph_rates_2025.json` | TRAIN brackets, EWT, FWT, corporate, VAT |
| EWT test fixtures | `addons/ipai/ipai_bir_tax_compliance/tests/fixtures/ewt_expected_withholding.csv` | Expected withholding amounts |
| VAT test fixtures | `addons/ipai/ipai_bir_tax_compliance/tests/fixtures/vat_basic_*.csv` | VAT transactions + expected lines |
| Rules engine tests | `addons/ipai/ipai_bir_tax_compliance/tests/test_rules_engine.py` | JSONLogic engine tests |
| EWT compute tests | `addons/ipai/ipai_bir_tax_compliance/tests/test_bir_ewt_compute.py` | EWT computation tests |
| VAT compute tests | `addons/ipai/ipai_bir_tax_compliance/tests/test_bir_vat_compute.py` | VAT computation tests |

#### Spec Bundles (root `spec/`)

| Spec | Path | Content |
|------|------|---------|
| `tax-pulse-sub-agent` | `spec/tax-pulse-sub-agent/` | PRD, plan, tasks, constitution for the Tax Pulse capability pack |

#### SSOT / Governance

| Asset | Path | Type |
|-------|------|------|
| Compliance check catalog | (referenced at `ssot/tax/` -- exists in nested repo) | SSOT YAML |
| Production seed plan | `ssot/migration/production_seed_plan.yaml` | Migration SSOT |
| Platform capabilities | `ssot/governance/platform-capabilities-unified.yaml` | Governance |

#### Architecture Docs

| Asset | Path |
|-------|------|
| TaxPulse Salvage Map | `docs/architecture/TAXPULSE_SALVAGE_MAP.md` |
| Agent Production Reality | `docs/architecture/AGENT_PRODUCTION_REALITY.md` |
| Unified Target Architecture | `../target-state/UNIFIED.md` |
| Platform Target State | `../target-state/PLATFORM.md` |

#### Scripts

| Asset | Path |
|-------|------|
| Production DB init (references BIR) | `scripts/odoo/init_production_db.sh` |
| Seed state validator | `scripts/odoo/validate_seed_state.py` |
| AI Search index validator | `scripts/ai-search/validate-index.py` |

---

### 2. `Insightpulseai/odoo/odoo/` (nested)

#### Supabase Tax Engine

| Asset | Path | Type |
|-------|------|------|
| BIR Tax Engine migration | `odoo/supabase/migrations/20260317_bir_tax_engine.sql` | SQL -- full schema (mdm, ops, audit) with 18 ATC codes, rates, matrix |
| BIR Forms registry migration | `odoo/supabase/migrations/20260212000001_registry_bir_forms.sql` | SQL -- BIR forms registry |
| Tax compute Edge Function | `odoo/supabase/functions/tax-compute/index.ts` | Deno -- HMAC-signed webhook, ATC resolution, EWT compute, risk scoring |
| BIR urgent alert function | `odoo/supabase/functions/bir-urgent-alert/index.ts` | Deno -- deadline alert function |
| BIR form generation seed | `odoo/supabase/seed/9001_erp/9001_erp_finance_bir_templates.sql` | SQL seed |

#### Supabase Seeds (Tax Compliance Workstream)

| Asset | Path |
|-------|------|
| Workstream definition | `odoo/supabase/seeds/workstreams/stc_tax_compliance/00_workstream.yaml` |
| Worklist types | `odoo/supabase/seeds/workstreams/stc_tax_compliance/10_worklist_types.yaml` |
| Compliance checks | `odoo/supabase/seeds/workstreams/stc_tax_compliance/20_compliance_checks.yaml` |
| Scenarios | `odoo/supabase/seeds/workstreams/stc_tax_compliance/30_scenarios.yaml` |
| PH localization | `odoo/supabase/seeds/workstreams/stc_tax_compliance/60_localization_ph.yaml` |
| Odoo mapping | `odoo/supabase/seeds/workstreams/stc_tax_compliance/90_odoo_mapping.yaml` |

#### Supabase Data Seeds

| Asset | Path |
|-------|------|
| BIR tax tasks | `odoo/supabase/data/seed/finance_ppm/tbwa_smp/tasks_bir_tax.csv` |
| BIR December 2025 seed | `odoo/supabase/data/bir_december_2025_seed.xml` |
| BIR calendar 2026 | `odoo/supabase/data/bir_calendar_2026.json` |
| Archive BIR tax tasks | `odoo/supabase/data/archive/finance_ppm/tbwa_smp/20260216/data_finance_seed/04_project.task.bir_tax.csv` |

#### SSOT

| Asset | Path |
|-------|------|
| Compliance check catalog | `odoo/ssot/tax/compliance_check_catalog.yaml` |
| Tax Pulse tool contracts | `odoo/ssot/agents/tax_pulse_tool_contracts.yaml` |
| Agent capability matrix | `odoo/ssot/agents/agent_capability_matrix.yaml` |
| Finance unified system | `odoo/ssot/finance/unified-system.yaml` |

#### Spec Bundles (nested)

| Spec | Path | Content |
|------|------|---------|
| `taxpulse-ph-port` | `odoo/spec/taxpulse-ph-port/` | Port plan from TaxPulse-PH-Pack into canonical module |
| `tax-pulse-sub-agent` | `odoo/spec/tax-pulse-sub-agent/` | Duplicate of root spec |
| `ipai-tax-engine` | `odoo/spec/ipai-tax-engine/` | Supabase tax engine spec (PRD, constitution, tasks) |
| `finance-unified` | `odoo/spec/finance-unified/` | Unified finance system spec |
| `afc-parity` | `odoo/spec/afc-parity/` | AFC (SAP) parity spec |

#### Portfolio Specs (nested, 3 layers deep)

| Spec | Path | Notes |
|------|------|-------|
| `bir-tax-compliance` | `odoo/docs/portfolio/specs/bir-tax-compliance/` | Duplicated in archive and nested-nested |
| `bir-tax-compliance` (archive) | `archive/root/docs/portfolio/specs/bir-tax-compliance/` | Archive copy |
| `bir-tax-compliance` (triple-nested) | `odoo/odoo/docs/portfolio/specs/bir-tax-compliance/` | Deep nested |
| PH tax taxonomy | `odoo/docs/portfolio/specs/taxonomy/philippines_tax.yaml` | Taxonomy definition |

#### Platform

| Asset | Path |
|-------|------|
| BIR form generation bridge | `odoo/platform/bridges/bir-form-generation/README.md` |
| BIR compliance feature registry | `odoo/platform/registry/features/bir-compliance.json` |
| EE parity test (references BIR) | `odoo/platform/tools/parity/test_ee_parity.py` |

---

### 3. `Insightpulseai/agents`

#### Agent Skills

| Skill | Path | Description |
|-------|------|-------------|
| `taxpulse-ph-pack` | `agents/skills/odoo/taxpulse-ph-pack/SKILL.md` | Full skill doc with architecture, benchmark vs AvaTax, SSOT refs |
| `bir-tax-filing` | `agents/skills/bir-tax-filing/SKILL.md` | Filing workflow skill with form reference, SQL queries, compliance calendar |
| `bir-eservices` | `agents/skills/odoo/bir-eservices/SKILL.md` | eFPS/eBIRForms integration architecture and roadmap |

#### Knowledge Base

| KB Article | Path |
|------------|------|
| BIR forms reference | `agents/knowledge-base/bir-compliance/bir-forms-reference.md` |
| BIR filing calendar | `agents/knowledge-base/bir-compliance/bir-filing-calendar.md` |
| VAT compliance guide | `agents/knowledge-base/bir-compliance/vat-compliance-guide.md` |
| Withholding tax guide | `agents/knowledge-base/bir-compliance/withholding-tax-guide.md` |

#### Benchmarks

| Asset | Path |
|-------|------|
| BIR eServices/eBIRForms benchmark | `agents/knowledge/benchmarks/bir-eservices-ebirforms.md` |

#### Foundry / Agent Manifests (reference BIR)

| Asset | Path |
|-------|------|
| Retrieval grounding contract | `agents/foundry/ipai-odoo-copilot-azure/retrieval-grounding-contract.md` |
| System prompt | `agents/foundry/ipai-odoo-copilot-azure/system-prompt.md` |
| Guardrails | `agents/foundry/ipai-odoo-copilot-azure/guardrails.md` |
| Finance assistant manifest | `agents/foundry/agents/agents__runtime__odoo_finance_assistant__v1.manifest.yaml` |
| Close assistant manifest | `agents/foundry/agents/agents__runtime__odoo_close_assistant__v1.manifest.yaml` |
| Copilot manifest | `agents/foundry/agents/agents__runtime__odoo_copilot__v1.manifest.yaml` |

#### Evaluations

| Asset | Path |
|-------|------|
| Eval dataset v2 | `agents/evals/odoo-copilot/datasets/eval-dataset-v2.json` |
| Eval run 20260314 | `agents/evals/odoo-copilot/results/eval-run-20260314.json` |
| Eval run 20260315 (final) | `agents/evals/odoo-copilot/results/eval-20260315-full-final.json` |

---

### 4. `jgtolentino/TaxPulse-PH-Pack` (external, not absorbed)

Per the salvage map (`docs/architecture/TAXPULSE_SALVAGE_MAP.md`):

| Component | Description | Status |
|-----------|-------------|--------|
| Odoo module surface | BIR forms, tax computation, agency mappings | Not absorbed |
| PH rules pack | JSONLogic, rate tables, thresholds | Partially ported into `ipai_bir_tax_compliance` |
| AI review engine | Scoring, rubric, protocol-driven evaluation | Not absorbed |
| Supabase layer | Run logs, protocol tables, Edge Function | Not absorbed |
| Multi-agency framework | 8 PH entities | Not ported |

---

## Duplicate / Conflict Analysis

| Group | Locations | Recommendation |
|-------|-----------|----------------|
| `spec/tax-pulse-sub-agent` | Root `spec/` + nested `odoo/spec/` | Keep root only; delete nested copy |
| `bir-tax-compliance` portfolio spec | `odoo/docs/portfolio/specs/` + `archive/` + `odoo/odoo/docs/portfolio/specs/` + `odoo/odoo/archive/` | Keep one canonical location; remove all others |
| `spec/odoo-copilot-agent-framework` | Root `spec/` + nested `odoo/spec/` | Keep root only |
| BIR task CSV seeds | `odoo/supabase/data/seed/` + `odoo/supabase/data/archive/` | Archive is correct as-is |
| Compliance check catalog | Referenced in multiple specs; lives in `odoo/ssot/tax/` | Single SSOT -- correct |
| Finance-BIR demo XML | `addons/ipai/ipai_finance_ppm/demo/` + `addons/ipai/ipai_finance_close_seed/data/` | Different modules with different purposes -- acceptable |
| AFC migrations | `odoo/supabase/supabase/migrations/` + `odoo/supabase/migrations/` | Two migration directories -- needs consolidation |
| Tax rates JSON vs SQL seed | `addons/ipai/.../data/rates/ph_rates_2025.json` (W-series codes) vs `migrations/20260317_bir_tax_engine.sql` (WI/WC codes) | **Conflict**: Different ATC code namespaces. Need reconciliation. |

---

## Recommended Canonical Ownership

| Domain | Owner Repo | Canonical Path |
|--------|-----------|----------------|
| Odoo BIR module (models, views, security, reports) | `odoo` | `addons/ipai/ipai_bir_tax_compliance/` |
| Rules engine (JSONLogic evaluator, rules packs) | `odoo` | `addons/ipai/ipai_bir_tax_compliance/engine/` + `data/rules/` |
| Tax rates (versioned JSON) | `odoo` | `addons/ipai/ipai_bir_tax_compliance/data/rates/` |
| Supabase tax engine schema | `odoo` (nested) | `odoo/supabase/migrations/20260317_bir_tax_engine.sql` |
| Tax compute Edge Function | `odoo` (nested) | `odoo/supabase/functions/tax-compute/` |
| Compliance check catalog (SSOT) | `odoo` (nested) | `odoo/ssot/tax/compliance_check_catalog.yaml` |
| Tool contracts (SSOT) | `odoo` (nested) | `odoo/ssot/agents/tax_pulse_tool_contracts.yaml` |
| Agent skills | `agents` | `agents/skills/odoo/taxpulse-ph-pack/` + `agents/skills/bir-tax-filing/` |
| Knowledge base articles | `agents` | `agents/knowledge-base/bir-compliance/` |
| Benchmark docs | `agents` | `agents/knowledge/benchmarks/bir-eservices-ebirforms.md` |
| Eval datasets | `agents` | `agents/evals/odoo-copilot/datasets/` |
| Spec bundles (Tax Pulse) | `odoo` | `spec/tax-pulse-sub-agent/` (single canonical) |

---

## Migration Priorities

| Priority | Action | Risk |
|----------|--------|------|
| P0 | Reconcile ATC code namespaces (W-series in JSON vs WI/WC in SQL) | **High** -- computation inconsistency |
| P0 | Remove duplicate spec bundles from nested paths | Low |
| P1 | Absorb TaxPulse-PH-Pack AI review engine into `agents/` | Medium |
| P1 | Build end-to-end test harness (Odoo -> Supabase -> verify) | High |
| P2 | Implement eBIRForms XML export in Odoo module | Medium |
| P2 | Install `ipai_bir_notifications` and `ipai_bir_plane_sync` | Low |
| P3 | Implement BIR form PDF report templates | Medium |
| P3 | Build eFPS browser automation PoC | Low |

---

## Risks / Unresolved Gaps

1. **ATC code namespace divergence**: The Odoo module uses W010/W020 codes while the Supabase schema uses WI010/WC010 (individual/corporate split). These must be reconciled.
2. **TaxPulse-PH-Pack not absorbed**: The upstream precursor contains multi-agency support (8 entities), AI review scoring, and Supabase protocol tables that have not been migrated.
3. **No end-to-end tests**: The rules engine has unit tests, but there is no integration test that verifies the full pipeline from Odoo posted moves through Supabase computation.
4. **eBIRForms/eFPS integration**: Both are listed as "next" in roadmaps but neither is implemented.
5. **Deep nesting duplication**: The nested `odoo/odoo/` subtree contains 4 layers of duplicated BIR specs that create confusion about which is canonical.

---

---

## TaxPulse-PH-Pack Salvage Findings

> Scan date: 2026-03-18
> Source: `git clone https://github.com/jgtolentino/TaxPulse-PH-Pack.git /tmp/TaxPulse-PH-Pack-salvage`
> Commit SHA: `72ce864958099748c60cf11ed3b3536ddf82064c`

### What Was Found

The TaxPulse-PH-Pack legacy repo is a standalone Odoo 18.0 module with an integrated rules engine, Supabase data warehouse, and AI-powered compliance review system. It is the **direct upstream precursor** to the `ipai_bir_tax_compliance` module in the canonical repo.

### Asset Categories and Counts

| Category | Count | Salvage Priority |
|----------|-------|-----------------|
| Odoo models (BIR forms + agency + sync) | 5 models | High -- BIR form models not yet in canonical module |
| Odoo security ACLs | 18 ACL rules | High -- well-structured 3-tier access |
| Rules engine (evaluator, formula, loader) | 3 Python files | Low -- already ported to ipai_bir_tax_compliance |
| Rules packs (EWT, VAT) | 2 YAML files | Low -- already ported |
| Rate tables (PH rates 2025) | 1 JSON file | Low -- already ported |
| Form definitions (BIR 2550Q) | 1 YAML file | Medium -- detailed form line mapping not in canonical |
| Form-to-bucket mappings | 1 YAML file | Medium -- bucket-to-BIR-line mapping |
| Validation rules (transaction + aggregate) | 1 YAML file (18 rules) | Medium -- richer than canonical module |
| Test fixtures (EWT, VAT) | 3 CSV files | Medium -- golden dataset fixtures |
| Supabase schema (BIR tables) | 1 SQL file (4 tables + RLS) | Medium -- `bir` schema with agency-scoped RLS |
| Supabase RPC functions | 1 SQL file (4 RPCs) | Medium -- upsert + dashboard stats |
| Tax Pulse schema (authority + run log) | 1 SQL file (6 tables + views + RPCs) | High -- not yet in canonical platform |
| Protocol v1 seed (High Compliance Mode) | 1 SQL file | High -- detailed scoring rubric |
| Edge Function (finance-tax-pulse) | 1 TypeScript file | High -- AI review orchestrator |
| Authority sources config | 1 YAML file (13 sources) | High -- RAG authority registry |
| LLM orchestrator config | 1 YAML file | Medium -- model params + cost controls |
| PRD / Specs | 2 markdown files | Medium -- SpectraTax Engine PRD is comprehensive |
| Agent skills | 3 SKILL.md files | Low-Medium -- taxpulse-repo-audit is useful |
| CI workflow | 1 YAML file | Low -- targets Odoo 18 |
| Roadmap tickets | 6 markdown files | Low -- feature ideas |
| Sub-module (ipai_project_brief) | 1 module | Drop -- unrelated to tax |

**Total: 38 distinct assets catalogued as TXP-001 through TXP-038 in `ssot/domain/tax_bir_inventory.yaml`**

### ATC Code Namespace Findings (Critical)

TaxPulse-PH-Pack uses the **W-series ATC namespace** (W010, W020, W030, W040, W050, W157, W158, W161, W169, W170), which is **identical to** the namespace used by `ipai_bir_tax_compliance` in the canonical repo. This confirms both originate from the same codebase lineage.

Additionally, TaxPulse-PH-Pack has:
- **F-series codes** for Final Withholding Tax: F001 (interest 20%), F002 (cash dividends 10%), F003 (stock dividends 10%), F004 (royalties 20%), F005 (prizes 20%)
- **WC/WF prefix detection** in `bir_1601c.py` for classifying account.move tax lines as compensation (WC) vs final (WF/F) withholding
- **TRAIN Law graduated brackets**: 6 tiers from 0% (below PHP 250K) to 35% (above PHP 8M)

The W-series codes are **simplified aliases** and NOT the BIR-canonical ATC codes (which use format like WI010, WC010 for individual/corporate split). The Supabase `20260317_bir_tax_engine.sql` migration in the canonical repo uses WI/WC namespace. The reconciliation gap remains unresolved.

### Salvageable vs Stale

**High-Priority Salvage (not yet in canonical):**
1. **AI review engine** (Edge Function + protocol + authority sources) -- the 5-dimension compliance scoring system is fully implemented with structured JSON output, run logging, and composite score calculation
2. **BIR form Odoo models** (bir.1601c, bir.2550q, bir.1702rt) -- complete Odoo ORM models with state workflow, compute methods, and Supabase sync
3. **Multi-agency framework** (taxpulse.agency model, 8 entities) -- analytic account integration, TIN/RDO management
4. **Tax Pulse Supabase schema** (authority registry, run log, protocol versioning) -- structured review audit trail
5. **Form definitions and mappings** (BIR 2550Q with all line items) -- detailed form-level validation rules

**Already Ported (low priority):**
1. Rules engine (evaluator.py, formula.py, loader.py) -- already in ipai_bir_tax_compliance
2. EWT/VAT rules packs -- already ported
3. Rate tables -- already ported

**Stale / Drop:**
1. Odoo 18 cert/prompt specs -- we are on Odoo 18
2. `ipai_project_brief` sub-module -- unrelated
3. CI workflow -- targets Odoo 18.0 + Python 3.11

### Recommended Salvage Priorities

1. **P0**: Absorb the AI review engine (TXP-024 + TXP-022 + TXP-023 + TXP-025 + TXP-026) into `agents/` and platform Supabase migrations. This is the most valuable unported component.
2. **P0**: Absorb BIR form Odoo models (TXP-002, TXP-003, TXP-004) and agency model (TXP-005) into `ipai_bir_tax_compliance`, with Odoo 18 migration (`tree` to `list`, etc.)
3. **P1**: Absorb form definitions (TXP-015), mappings (TXP-016), and validation rules (TXP-017) into the canonical rules pack
4. **P1**: Port the detailed PRD (TXP-027) as reference documentation for the SpectraTax Engine vision
5. **P2**: Absorb security ACLs (TXP-007) and test fixtures (TXP-018, TXP-019) into canonical module
6. **P2**: Absorb taxpulse-repo-audit skill (TXP-031) into agents/skills/

### Blockers / Warnings

- **Enterprise dependency**: The root `__manifest__.py` depends on `account_reports` which is an **Enterprise-only module**. This must be removed or replaced with OCA equivalents when porting to CE.
- **Deprecated Supabase instance**: The `supabase_sync.py` model hardcodes `xkxyvboeubffxxbebsll.supabase.co` which is deprecated. Must be updated to the canonical self-hosted instance `spdtwktxdalcfigzeqrz` on Azure VM `vm-ipai-supabase-dev` (`rg-ipai-agents-dev`). Never use `xkxyvboeubffxxbebsll` or `ublqmilcjtpnflofprkr`.
- **Odoo 18 to 19 migration**: All models need `tree` to `list` view type migration and `groups_id` to `group_ids` field rename check.

---

*Generated by tax-bir-scan, 2026-03-18 (updated with TaxPulse-PH-Pack salvage)*
