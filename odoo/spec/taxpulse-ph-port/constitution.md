# TaxPulse-PH-Pack Port -- Constitution

> Governing rules for the selective transplant of `jgtolentino/TaxPulse-PH-Pack` (Odoo 18.0, Beta)
> into the canonical `addons/ipai/ipai_bir_tax_compliance` module (Odoo 19.0 CE).

---

## Rules

### 1. Single Canonical Module

`ipai_bir_tax_compliance` is the one and only BIR compliance module in this repo.
No parallel module tree, no `taxpulse_*` namespace, no second BIR module.
All ported assets land inside or alongside `ipai_bir_tax_compliance`.

### 2. No Enterprise Dependencies

TaxPulse-PH-Pack references `account_reports` (Odoo EE).
Every such dependency must be either:
- Replaced with OCA `account_financial_report` / `mis_builder`, or
- Removed entirely if the feature is not needed.

No `odoo.com` IAP calls. No EE module imports.

### 3. No Deprecated Supabase References

Supabase project `xkxyvboeubffxxbebsll` is deprecated.
Any TaxPulse code referencing it must be stripped or redirected to
the canonical project `spdtwktxdalcfigzeqrz` (if external integration is needed)
or removed if the functionality is handled by Odoo/PostgreSQL.

### 4. Externalized Rates and Rules

Tax rates, TRAIN brackets, EWT codes, final WHT rates, VAT thresholds,
and compliance rules must live in JSON or YAML data files, never hardcoded
in Python source.

Pattern: `data/rates/*.json`, `data/rules/*.yaml`.
The rules engine loads these at runtime. Updates ship as data file changes,
not code changes.

### 5. Single-Entity Baseline

TaxPulse supports multi-agency filing (BIR, SEC, PhilHealth, SSS, Pag-IBIG).
The port targets BIR only. Multi-agency support is an optional future extension
behind a feature flag or separate module (`ipai_ph_multi_agency`), not the default.

### 6. Tests Required

Every ported component must have corresponding tests:
- Rules engine: unit tests with CSV fixtures
- Computation: tax computation tests (VAT, EWT, WHT, income tax)
- Reports: render tests (PDF output, XML export structure)
- Copilot tools: registration and basic invocation tests

No code lands without a test. Classify failures per `~/.claude/rules/testing.md`.

### 7. Copilot Integration via Existing Architecture

BIR copilot tools integrate through the existing 3-agent + 1-workflow architecture.
No new agent type. Tools register as BIR action tools in the existing tool registry.
The BIR Compliance Pack is an addition to the agent matrix, not a replacement.

---

*Spec created: 2026-03-15*
