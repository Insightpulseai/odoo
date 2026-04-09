# TaxPulse-PH-Pack Port -- Product Requirements Document

> Goal: Close the BIR adequacy gap (currently 2.5/5) by merging TaxPulse-PH-Pack
> strengths into the canonical `ipai_bir_tax_compliance` module.

---

## Problem Statement

The current BIR compliance implementation scores 2.5/5 on adequacy:
- Tax rates are partially hardcoded or missing
- TRAIN law brackets incomplete
- Final WHT computation is stubbed
- No rules engine for compliance logic
- No PDF report templates for key BIR forms
- No eFPS XML export capability
- Copilot has no BIR-specific action tools

TaxPulse-PH-Pack (Odoo 18.0, Beta) solved many of these problems but lives in a
separate repo with EE dependencies and a different module structure.

## Solution

Selective transplant of proven TaxPulse assets into the canonical module,
adapted for Odoo 18.0 CE, with externalized rates and a JSONLogic rules engine.

---

## Port Scope

### Port IN

| Asset | Source | Target |
|-------|--------|--------|
| Tax rates | `ph_rates_2025.json` (TRAIN brackets, EWT codes, final WHT, corporate tax, VAT) | `data/rates/ph_rates_2025.json` |
| VAT rules | `vat.rules.yaml` (JSONLogic DSL) | `data/rules/vat.rules.yaml` |
| EWT rules | `ewt.rules.yaml` (JSONLogic DSL) | `data/rules/ewt.rules.yaml` |
| Rules engine | `rules_engine/evaluator.py`, `formula.py`, `loader.py` | `models/rules_engine/` |
| Report templates | XML templates for BIR forms 1601-C, 2550Q, 1702-RT | `report/` |
| Test fixtures | CSV fixtures, engine tests, computation tests | `tests/` |
| Knowledge schema | Authority registry schema concept (for `bir_compliance_search`) | `data/knowledge/` |

### Do NOT Port

| Asset | Reason |
|-------|--------|
| Multi-agency model (SEC, PhilHealth, SSS, Pag-IBIG) | Out of scope -- BIR only baseline (Constitution rule 5) |
| Deprecated Supabase references (`xkxyvboeubffxxbebsll`) | Deprecated (Constitution rule 3) |
| `account_reports` EE dependency | CE only (Constitution rule 2) |
| Competing module tree (`taxpulse_*` namespace) | Single canonical module (Constitution rule 1) |
| TaxPulse UI chrome and branding | Not applicable to IPAI stack |

---

## Success Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | Rules engine passes all fixture tests | `test_rules_engine.py` green in `test_ipai_bir_tax_compliance` DB |
| 2 | VAT computation uses externalized rates from `ph_rates_2025.json` | Unit test computes VAT from JSON rates, not hardcoded values |
| 3 | EWT computation uses externalized rates and JSONLogic rules | Unit test evaluates EWT rules from YAML, returns correct withholding |
| 4 | TRAIN bracket logic complete (all 2025 brackets) | Fixture test covers all income brackets with expected tax amounts |
| 5 | Final WHT computation functional (not stubbed) | Unit test for dividend, interest, royalty WHT rates |
| 6 | PDF reports render for 1601-C, 2550Q, 1702-RT | Report render test produces non-empty PDF output |
| 7 | eFPS XML export stub present and structurally valid | XML output validates against expected schema structure |
| 8 | Copilot BIR tools registered | `compute_bir_vat_return`, `compute_bir_withholding_return`, `validate_bir_return`, `check_overdue_filings`, `generate_alphalist`, `generate_efps_xml`, `generate_bir_pdf` present in tool registry |
| 9 | No EE imports in module | `grep -r "account_reports\|odoo.addons.account_reports" addons/ipai/ipai_bir_tax_compliance/` returns empty |
| 10 | No hardcoded tax rates in Python | All rate references load from JSON/YAML data files |

---

## Non-Goals (This Spec)

- Full BIR e-filing integration (requires BIR API access)
- Multi-company tax consolidation
- Historical rate versioning (future spec)
- PhilHealth/SSS/Pag-IBIG compliance (future spec, separate module)

---

*Spec created: 2026-03-15*
