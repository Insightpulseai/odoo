# Tax/BIR Consolidation Scan Evidence

## Scan Metadata

| Field | Value |
|-------|-------|
| **Timestamp** | 2026-03-18 |
| **Timezone** | Asia/Manila (UTC+08:00) |
| **Scanner** | Claude Code (manual agent-driven scan) |
| **Model** | Opus 4.6 (1M context) |

## Repos Scanned

| Repo | Path | Method |
|------|------|--------|
| `Insightpulseai/odoo` | `/Users/tbwa/Documents/GitHub/Insightpulseai/odoo` | Grep + Glob (all depths) |
| `Insightpulseai/odoo/odoo/` | Nested subtree within above | Grep + Glob + Read |
| `Insightpulseai/agents` | `/Users/tbwa/Documents/GitHub/Insightpulseai/agents` | Grep + Glob |
| `Insightpulseai/agents/knowledge-base` | `/Users/tbwa/Documents/GitHub/Insightpulseai/agents/knowledge-base` | Grep |
| `jgtolentino/TaxPulse-PH-Pack` | External (documented via salvage map) | Not cloned; referenced from `docs/architecture/TAXPULSE_SALVAGE_MAP.md` |

## Search Terms Used

### Primary Terms (Grep)
- `BIR|TaxPulse|tax_pulse|taxpulse`
- `withholding|EWT|FWT|SAWT|SLSP|alphalist`
- `1601|2550|1702|eBIR|eFPS|ATC|RDO`
- `Philippine tax|PH tax|bir_compliance|tax.compliance`
- `VAT|Avalara|AvaTax|tax.engine|tax_engine`
- `ipai_tax|ipai_bir|ipai_finance.*tax|l10n_ph`

### Secondary Terms (Glob patterns)
- `**/*tax*` (in addons/, spec/, ssot/)
- `**/*bir*` (in addons/)
- `**/ipai_bir_tax_compliance/**`
- `**/tax-pulse-sub-agent/**`
- `**/taxpulse-ph-port/**`
- `**/ipai-tax-engine/**`
- `**/bir-tax-compliance/**`
- `**/stc_tax_compliance/**`
- `**/bir-compliance/**`

## Files Read (Key Files Inspected in Full)

| File | Purpose |
|------|---------|
| `docs/architecture/TAXPULSE_SALVAGE_MAP.md` | Legacy precursor documentation |
| `addons/ipai/ipai_bir_tax_compliance/engine/evaluator.py` | Rules engine implementation |
| `addons/ipai/ipai_bir_tax_compliance/data/rules/ewt.rules.yaml` | EWT rules pack |
| `addons/ipai/ipai_bir_tax_compliance/data/rates/ph_rates_2025.json` | Rate tables |
| `spec/tax-pulse-sub-agent/prd.md` | Tax Pulse PRD |
| `odoo/spec/taxpulse-ph-port/prd.md` | Port plan PRD |
| `odoo/supabase/functions/tax-compute/index.ts` | Tax compute Edge Function |
| `odoo/supabase/migrations/20260317_bir_tax_engine.sql` | Tax engine schema |
| `odoo/ssot/tax/compliance_check_catalog.yaml` | Compliance checks SSOT |
| `odoo/ssot/agents/tax_pulse_tool_contracts.yaml` | Tool contracts SSOT |
| `odoo/platform/bridges/bir-form-generation/README.md` | Bridge contract |
| `odoo/platform/registry/features/bir-compliance.json` | Feature registry |
| `agents/skills/odoo/taxpulse-ph-pack/SKILL.md` | TaxPulse skill |
| `agents/skills/bir-tax-filing/SKILL.md` | BIR filing skill |
| `agents/skills/odoo/bir-eservices/SKILL.md` | BIR eServices skill |
| `agents/knowledge/benchmarks/bir-eservices-ebirforms.md` | Benchmark doc |
| `odoo/supabase/seeds/workstreams/stc_tax_compliance/00_workstream.yaml` | STC workstream |

## Assumptions

1. **The nested `odoo/odoo/` directory** is treated as a subtree or historical snapshot. Assets there that duplicate root-level assets are flagged as duplicates.
2. **`jgtolentino/TaxPulse-PH-Pack`** was not cloned or directly inspected. Information about it comes from the salvage map and agent skill docs.
3. **Module installation status** (installed vs not installed) is inferred from documentation, not from a live database query.
4. **Odoo model existence** (bir.filing.deadline, bir.vat.return, etc.) is documented as "uncertain" where not directly verified from `__manifest__.py` or `models/` inspection.
5. **The `addons/oca/` directory** contains OCA modules with generic tax-related files (e.g., `account_tax_balance`). These are standard OCA modules, not PH-specific, and are inventoried but not classified as BIR assets.

## Evidence Limitations

1. **No database access**: The scan is file-system only. No queries were run against any Odoo or Supabase database to verify installed modules, schema state, or data.
2. **External repo not cloned**: The `TaxPulse-PH-Pack` precursor was not directly inspected.
3. **No runtime verification**: Edge Functions and n8n workflows were inspected as source code only, not tested against live services.
4. **Agent eval results not parsed**: The eval JSON files were identified but not parsed for BIR-specific test case counts.
5. **node_modules excluded**: All `node_modules/` directories were excluded from search (glob default behavior).
6. **Binary files not inspected**: Images, compiled assets, and lock files were noted in search results but not classified.

## Output Files

| File | Path |
|------|------|
| Consolidation Report | `docs/architecture/TAX_BIR_CONSOLIDATION_REPORT.md` |
| Knowledge Map | `docs/architecture/TAX_BIR_KNOWLEDGE_MAP.md` |
| Asset Inventory (YAML) | `ssot/domain/tax_bir_inventory.yaml` |
| Gap Analysis (YAML) | `ssot/domain/tax_bir_gap_analysis.yaml` |
| Migration Plan | `docs/architecture/TAXPULSE_MIGRATION_PLAN.md` |
| Scan Evidence (this file) | `docs/evidence/tax-bir-scan/README.md` |

---

## Legacy Repo Scan (TaxPulse-PH-Pack)

| Field | Value |
|-------|-------|
| **Legacy repo URL** | https://github.com/jgtolentino/TaxPulse-PH-Pack.git |
| **Clone path** | /tmp/TaxPulse-PH-Pack-salvage |
| **Commit SHA** | `72ce864958099748c60cf11ed3b3536ddf82064c` |
| **Scan date** | 2026-03-18 |
| **Clone command** | `git clone https://github.com/jgtolentino/TaxPulse-PH-Pack.git /tmp/TaxPulse-PH-Pack-salvage` |
| **Clone status** | SUCCESS |
| **Total files (non-.git)** | ~85 files |
| **Assets catalogued** | 38 entries (TXP-001 through TXP-038) |

### Files Inspected (TaxPulse-PH-Pack)

| File | Purpose |
|------|---------|
| `__manifest__.py` | Root Odoo module manifest (v18.0.1.0.0) |
| `models/bir_1601c.py` | BIR 1601-C Monthly Withholding model |
| `models/bir_2550q.py` | BIR 2550Q Quarterly VAT model |
| `models/bir_1702rt.py` | BIR 1702-RT Annual Income Tax model |
| `models/taxpulse_agency.py` | Multi-agency model (8 entities) |
| `models/supabase_sync.py` | Supabase sync handler |
| `security/ir.model.access.csv` | 18 ACL rules |
| `engine/rules_engine/evaluator.py` | JSONLogic evaluator (14 operators) |
| `engine/rules_engine/formula.py` | Formula engine (SUM/MAX/MIN/ABS/ROUND) |
| `engine/rules_engine/loader.py` | YAML rules loader with caching |
| `engine/config/finance_tax_pulse_model.yaml` | LLM orchestrator config |
| `packs/ph/rules/ewt.rules.yaml` | 10 EWT rules (W-series ATC) |
| `packs/ph/rules/vat.rules.yaml` | 8 VAT rules |
| `packs/ph/rates/ph_rates_2025.json` | PH tax rates (TRAIN, EWT, FWT, VAT, CIT) |
| `packs/ph/pack.meta.yaml` | Pack metadata |
| `packs/ph/forms/bir_2550Q_2025.form.yaml` | BIR 2550Q form definition |
| `packs/ph/mappings/vat_2550Q.mapping.yaml` | VAT bucket-to-form-line mapping |
| `packs/ph/validations/core_validations.yaml` | 18 validation rules |
| `packs/ph/tests/fixtures/ewt_expected_withholding.csv` | EWT golden dataset |
| `supabase/001_create_bir_tables.sql` | BIR schema (4 tables + RLS) |
| `supabase/002_rpc_functions.sql` | Upsert RPCs + dashboard stats |
| `supabase/003_tax_pulse_schema.sql` | Tax Pulse schema (authority + run log) |
| `supabase/004_tax_pulse_protocol_seed.sql` | Protocol v1 High Compliance Mode |
| `supabase/functions/finance-tax-pulse/index.ts` | AI review Edge Function |
| `config/tax_pulse_sources.yaml` | 13 authority sources (4 tiers) |
| `specs/001-taxpulse-engine.prd.md` | SpectraTax Engine PRD |
| `skills/taxpulse-repo-audit/SKILL.md` | Repo audit skill |
| `.github/workflows/ci.yml` | CI workflow (Odoo 18 + lint + test) |

### Key Finding: ATC Code Reconciliation

TaxPulse-PH-Pack uses the W-series ATC namespace (W010-W170) identical to the canonical `ipai_bir_tax_compliance` module, confirming shared lineage. Additionally contains F-series final withholding codes (F001-F005) and WC/WF prefix-based classification logic in `bir_1601c.py`. Full ATC detail recorded in `ssot/domain/atc_code_mapping.yaml` under the `taxpulse_legacy` system entry.

---

*Scan completed: 2026-03-18 (updated with TaxPulse-PH-Pack salvage)*
