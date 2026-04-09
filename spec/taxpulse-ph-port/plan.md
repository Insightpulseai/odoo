# TaxPulse-PH-Pack Port -- Implementation Plan

> 5-phase plan for selective transplant into `ipai_bir_tax_compliance` (Odoo 18.0 CE).

---

## Phase 1: Foundation

**Goal**: Port the data layer and rules engine. Remove EE assumptions. Adapt to 19.0.

### Deliverables

1. Copy `ph_rates_2025.json` into `data/rates/ph_rates_2025.json`
   - Validate JSON structure: TRAIN brackets, EWT codes, final WHT, corporate tax, VAT
   - Ensure no hardcoded Python rate references remain

2. Copy `vat.rules.yaml` and `ewt.rules.yaml` into `data/rules/`
   - Validate JSONLogic DSL syntax
   - Strip any multi-agency references (BIR only)

3. Port rules engine (`evaluator.py`, `formula.py`, `loader.py`) into `models/rules_engine/`
   - Adapt imports from TaxPulse namespace to `ipai_bir_tax_compliance`
   - Remove any `account_reports` (EE) imports
   - Replace deprecated Supabase calls with local data loading
   - Adapt to Odoo 18.0 ORM conventions (see `odoo18-coding.md`)

4. Port CSV test fixtures into `tests/fixtures/`
5. Port and adapt engine unit tests into `tests/test_rules_engine.py`
6. Update `__manifest__.py`: add data files, bump version, verify deps are CE-only

### Exit Gate

Rules engine loads rates from JSON, evaluates rules from YAML, passes all fixture tests
in disposable `test_ipai_bir_tax_compliance` database.

---

## Phase 2: Computation

**Goal**: Refactor VAT/EWT/WHT compute paths to use the rules engine and externalized rates.

### Deliverables

1. Refactor VAT computation model to call `rules_engine.evaluator` with `vat.rules.yaml`
   - Input: transaction data (amount, partner VAT status, transaction type)
   - Output: VAT amount, VAT-exempt flag, zero-rated flag

2. Refactor EWT computation model to call `rules_engine.evaluator` with `ewt.rules.yaml`
   - Map ATC codes to EWT rates from `ph_rates_2025.json`
   - Handle expanded withholding tax categories

3. Fix TRAIN bracket logic
   - Port complete 2025 TRAIN law income tax brackets from `ph_rates_2025.json`
   - Ensure progressive rate computation is correct for all brackets
   - Add bracket boundary edge-case tests

4. Complete final WHT stub
   - Port final withholding tax rates (dividends, interest, royalties, prizes)
   - Wire to rules engine evaluation path

5. Add computation tests
   - VAT: standard, zero-rated, exempt, mixed transactions
   - EWT: each major ATC code category
   - Income tax: each TRAIN bracket boundary
   - Final WHT: each final tax category

### Exit Gate

All computation tests pass. No tax rate is hardcoded in Python source.
`grep -rn "0.12\|0.05\|0.10\|0.15\|0.20\|0.25\|0.30\|0.35" models/` returns
only references to the rates loader, not literal tax rates.

---

## Phase 3: Reports

**Goal**: Port BIR form PDF/report templates. Add eFPS XML export stub.

### Deliverables

1. Port XML report templates for:
   - **1601-C** (Monthly Remittance Return of Income Taxes Withheld on Compensation)
   - **2550Q** (Quarterly Value-Added Tax Return)
   - **1702-RT** (Annual Income Tax Return for Corporation/Partnership)

2. Convert templates to Odoo 18.0 report conventions
   - Use `ir.actions.report` with QWeb templates
   - Replace any EE report engine references with standard CE QWeb
   - Ensure `tree` -> `list` migration (Odoo 18 breaking change)

3. Add eFPS XML export stub
   - Define XML schema structure for BIR electronic filing
   - Implement `generate_efps_xml` method that produces structurally valid XML
   - Mark as stub -- full eFPS integration is a future spec

4. Add report render tests
   - Each report template renders to non-empty PDF
   - eFPS XML output validates against expected structure

### Exit Gate

PDF reports render for all 3 forms. eFPS XML stub produces valid XML structure.
Report tests pass in disposable database.

---

## Phase 4: Copilot

**Goal**: Register BIR action tools in the copilot agent matrix.

### Deliverables

1. Register the following BIR action tools:
   - `compute_bir_vat_return` -- Compute VAT return for a period
   - `compute_bir_withholding_return` -- Compute withholding tax return for a period
   - `validate_bir_return` -- Validate a return against rules before filing
   - `check_overdue_filings` -- List overdue BIR filing deadlines
   - `generate_alphalist` -- Generate alphalist of payees for withholding
   - `generate_efps_xml` -- Generate eFPS XML for electronic filing
   - `generate_bir_pdf` -- Generate PDF for a specific BIR form

2. Add BIR Compliance Pack to the agent matrix
   - Pack groups the 7 tools above
   - Integrates through existing 3-agent + 1-workflow architecture
   - No new agent type created

3. Add `bir_compliance_search` knowledge integration
   - Port authority registry schema concept from TaxPulse
   - Enable copilot to answer BIR compliance questions from structured knowledge

4. Add tool registration and invocation tests

### Exit Gate

All 7 tools appear in the copilot tool registry. Basic invocation tests pass
(tools accept valid input and return structured output). BIR Compliance Pack
is listed in agent matrix.

---

## Phase 5: Notifications

**Goal**: Enable `ipai_bir_notifications` module with deadline tracking and alerts.

### Deliverables

1. Flip `ipai_bir_notifications` to `installable: True` in `__manifest__.py`
2. Wire notification triggers to BIR deadline states:
   - Upcoming deadline (configurable days-before threshold)
   - Overdue filing
   - Submission confirmation
3. Add notification channel support (Odoo mail, Slack via `ipai_slack_connector`)
4. Add tests:
   - Deadline state transitions trigger correct notifications
   - Notification content includes form type, period, and deadline date
   - Overdue detection works for past-due deadlines

### Exit Gate

`ipai_bir_notifications` installs cleanly. Deadline notifications fire on state
transitions. Tests pass in disposable database.

---

## Dependency Chain

```
Phase 1 (Foundation) --> Phase 2 (Computation) --> Phase 3 (Reports)
                                                       |
                                                       v
                                                Phase 4 (Copilot)
                                                       |
                                                       v
                                                Phase 5 (Notifications)
```

Phases 1-3 are sequential. Phase 4 depends on Phase 3 (reports must exist for
`generate_bir_pdf`). Phase 5 depends on Phase 4 (copilot tools must exist for
`check_overdue_filings` integration).

---

*Spec created: 2026-03-15*
