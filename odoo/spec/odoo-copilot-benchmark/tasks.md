# Odoo Copilot Benchmark — Tasks

> Task checklist for the benchmark framework.

---

## General Copilot Benchmark (SAP Joule Reference)

- [ ] Define scenario registry (9 domains × 3 capability classes)
- [ ] Build scenario runner with evidence capture
- [ ] Implement deterministic scoring model
- [ ] Implement governance hard gates
- [ ] Build reporting pipeline
- [ ] Execute first full benchmark run

## Tax/Compliance Benchmark (AvaTax Reference)

- [ ] Replace benchmark target with AvaTax in SSOT
- [ ] Define 25-40 canonical tax/compliance tasks
- [ ] Add policy-threshold test cases for undercharge / overcharge detection
- [ ] Add gold outcomes for tax mapping and exception handling
- [ ] Add human tax-review rubric
- [ ] Add auditability scoring rubric
- [ ] Capture repeated-run outputs and failure logs
- [ ] Gate any "better than AvaTax benchmark" claim on evidence completion

## TaxPulse Salvage (Precursor Integration)

- [ ] Create salvage map doc (`docs/architecture/taxpulse_salvage_map.md`)
- [ ] Create salvage inventory (`docs/architecture/taxpulse_salvage_inventory.md`)
- [ ] Migrate Odoo tax models to `odoo/addons/local/taxpulse_ph_pack/`
- [ ] Migrate specialist agent logic to `agents/packages/taxpulse_ph/`
- [ ] Migrate Supabase schema to `platform/supabase/taxpulse/`
- [ ] Consolidate spec/specs into canonical spec bundle
- [ ] Use TaxPulse specialist agent as AvaTax benchmark candidate (not generic copilot)
