# TaxPulse-PH-Pack Port -- Task Checklist

> Checkbox task list for each phase. Verification items at end.

---

## Phase 1: Foundation

- [ ] Clone/fetch `jgtolentino/TaxPulse-PH-Pack` for reference (do not import)
- [ ] Copy `ph_rates_2025.json` to `addons/ipai/ipai_bir_tax_compliance/data/rates/ph_rates_2025.json`
- [ ] Validate JSON: TRAIN brackets, EWT codes, final WHT rates, corporate tax, VAT rates
- [ ] Copy `vat.rules.yaml` to `addons/ipai/ipai_bir_tax_compliance/data/rules/vat.rules.yaml`
- [ ] Copy `ewt.rules.yaml` to `addons/ipai/ipai_bir_tax_compliance/data/rules/ewt.rules.yaml`
- [ ] Strip multi-agency references from rules YAML (BIR only)
- [ ] Create `addons/ipai/ipai_bir_tax_compliance/models/rules_engine/__init__.py`
- [ ] Port `evaluator.py` to `models/rules_engine/evaluator.py` -- adapt namespace, remove EE imports
- [ ] Port `formula.py` to `models/rules_engine/formula.py` -- adapt namespace
- [ ] Port `loader.py` to `models/rules_engine/loader.py` -- replace Supabase calls with local file loading
- [ ] Remove any `account_reports` imports from ported code
- [ ] Adapt all ported code to Odoo 19.0 ORM conventions
- [ ] Copy CSV test fixtures to `tests/fixtures/`
- [ ] Port engine tests to `tests/test_rules_engine.py`
- [ ] Update `__manifest__.py`: add data files to `data` key, bump version
- [ ] Verify `__manifest__.py` deps contain no EE modules
- [ ] Run: `odoo-bin -d test_ipai_bir_tax_compliance -i ipai_bir_tax_compliance --stop-after-init --test-enable`
- [ ] Classify test results per testing policy
- [ ] Commit: `feat(bir): port rules engine and externalized rates from TaxPulse-PH-Pack`

## Phase 2: Computation

- [ ] Refactor VAT computation model to call `rules_engine.evaluator` with `vat.rules.yaml`
- [ ] Refactor EWT computation model to call `rules_engine.evaluator` with `ewt.rules.yaml`
- [ ] Map ATC codes to EWT rates from `ph_rates_2025.json`
- [ ] Port complete 2025 TRAIN law income tax brackets
- [ ] Implement progressive rate computation for all TRAIN brackets
- [ ] Add bracket boundary edge-case handling
- [ ] Complete final WHT computation (dividends, interest, royalties, prizes)
- [ ] Wire final WHT to rules engine evaluation path
- [ ] Remove all hardcoded tax rate literals from Python models
- [ ] Add test: VAT standard rate computation
- [ ] Add test: VAT zero-rated transaction
- [ ] Add test: VAT exempt transaction
- [ ] Add test: VAT mixed transaction
- [ ] Add test: EWT for each major ATC code category
- [ ] Add test: Income tax for each TRAIN bracket boundary
- [ ] Add test: Final WHT for each final tax category (dividend, interest, royalty, prize)
- [ ] Verify: `grep -rn` for hardcoded rate literals returns only loader references
- [ ] Run full test suite on disposable DB
- [ ] Classify test results
- [ ] Commit: `feat(bir): refactor tax computation to use rules engine and externalized rates`

## Phase 3: Reports

- [ ] Port 1601-C report template (Monthly Remittance -- Compensation WHT)
- [ ] Port 2550Q report template (Quarterly VAT Return)
- [ ] Port 1702-RT report template (Annual Income Tax -- Corp/Partnership)
- [ ] Convert all templates to Odoo 19.0 QWeb report conventions
- [ ] Replace any EE `account_reports` references with CE QWeb
- [ ] Apply `tree` -> `list` migration where applicable
- [ ] Register reports as `ir.actions.report` records
- [ ] Implement `generate_efps_xml` method with valid XML structure
- [ ] Define eFPS XML schema structure for BIR electronic filing
- [ ] Add test: 1601-C renders to non-empty PDF
- [ ] Add test: 2550Q renders to non-empty PDF
- [ ] Add test: 1702-RT renders to non-empty PDF
- [ ] Add test: eFPS XML output validates against expected structure
- [ ] Run report tests on disposable DB
- [ ] Classify test results
- [ ] Commit: `feat(bir): add BIR form report templates and eFPS XML export stub`

## Phase 4: Copilot

- [ ] Implement `compute_bir_vat_return` tool
- [ ] Implement `compute_bir_withholding_return` tool
- [ ] Implement `validate_bir_return` tool
- [ ] Implement `check_overdue_filings` tool
- [ ] Implement `generate_alphalist` tool
- [ ] Implement `generate_efps_xml` tool (copilot wrapper)
- [ ] Implement `generate_bir_pdf` tool (copilot wrapper)
- [ ] Register all 7 tools in the copilot tool registry
- [ ] Define BIR Compliance Pack in agent matrix
- [ ] Port authority registry schema to `data/knowledge/`
- [ ] Wire `bir_compliance_search` to knowledge data
- [ ] Add test: all 7 tools appear in tool registry
- [ ] Add test: `compute_bir_vat_return` accepts valid input, returns structured output
- [ ] Add test: `compute_bir_withholding_return` accepts valid input, returns structured output
- [ ] Add test: `validate_bir_return` detects invalid return data
- [ ] Add test: `check_overdue_filings` returns overdue items for past deadlines
- [ ] Add test: BIR Compliance Pack listed in agent matrix
- [ ] Run copilot tests on disposable DB
- [ ] Classify test results
- [ ] Commit: `feat(bir): register BIR copilot action tools and compliance pack`

## Phase 5: Notifications

- [ ] Set `installable: True` in `ipai_bir_notifications/__manifest__.py`
- [ ] Verify dependency chain (`ipai_bir_tax_compliance` as dep)
- [ ] Implement upcoming-deadline notification trigger (configurable days-before)
- [ ] Implement overdue-filing notification trigger
- [ ] Implement submission-confirmation notification
- [ ] Add Odoo mail channel support
- [ ] Add Slack channel support via `ipai_slack_connector`
- [ ] Add test: upcoming deadline state triggers notification
- [ ] Add test: overdue state triggers notification
- [ ] Add test: notification content includes form type, period, deadline date
- [ ] Add test: overdue detection for past-due deadlines
- [ ] Run notification tests on disposable DB
- [ ] Classify test results
- [ ] Commit: `feat(bir): enable ipai_bir_notifications with deadline tracking`

---

## Final Verification

- [ ] Full module install test: `odoo-bin -d test_ipai_bir_tax_compliance -i ipai_bir_tax_compliance,ipai_bir_notifications --stop-after-init --test-enable`
- [ ] No EE imports: `grep -r "account_reports\|odoo.addons.account_reports" addons/ipai/ipai_bir_tax_compliance/` returns empty
- [ ] No deprecated Supabase: `grep -r "xkxyvboeubffxxbebsll" addons/ipai/ipai_bir_tax_compliance/` returns empty
- [ ] No hardcoded rates in Python: spot-check models for literal tax rate values
- [ ] All tests classified per testing policy
- [ ] Evidence saved to `docs/evidence/<stamp>/taxpulse-ph-port/`
- [ ] BIR adequacy score re-evaluated (target: >= 4.0/5)

---

*Spec created: 2026-03-15*
