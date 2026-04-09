# Constitution — IPAI Tax Engine

## Non-negotiable rules

1. PH-native by design — BIR ATC matrix, SLSP/QAP/SAWT .dat format, BIR form templates
2. Odoo 18 CE is the transactional SoR — all posted moves originate here
3. Odoo 18 PH localization (v19) ships 2550Q, SLSP/QAP/SAWT .dat natively — IPAI extends, not rebuilds
4. 2307 generation is the primary gap Odoo CE does not cover — this is the core deliverable
5. Zero marginal cost per transaction — no AvaTax-style per-call pricing
6. SAP Tax Compliance is the benchmark for capability design — not the implementation target
7. AvaTax is the benchmark for API performance and automation patterns — PH is explicitly unsupported
8. Supabase Edge Functions handle compute; Supabase Storage holds output artifacts
9. Databricks Gold layer handles audit analytics and ML risk scoring
10. All tax computations are idempotent (keyed on odoo_db + move_id + atc_code + period)

## Source-of-truth boundaries

- **Odoo PostgreSQL** = canonical posted transactions (account.move, account.move.line)
- **mdm.tax_rules / mdm.atc_matrix** = tax master data (Supabase)
- **ops.bir_forms** = generated form metadata + Storage URL
- **audit.tax_events** = immutable computation log (append-only)
- **Databricks Gold** = tax_risk_scores (ML-derived, not authoritative)

## What Odoo 18 already provides natively (do not rebuild)

- 2550Q (Quarterly VAT Return) — revamped for latest BIR regs
- SLSP, QAP, SAWT reports — official BIR format
- .dat file export for SLSP/QAP/SAWT — compatible with BIR Alphalist/ReLiEf
- Payment withholding tax — native option to apply on payment
- Disbursement vouchers with signature and check number

## Competitive positioning

| vs SAP Tax Compliance | vs AvaTax |
|---|---|
| No S/4HANA license required | PH market supported (AvaTax has no PH plans) |
| Same rule-engine capability pattern | Same API-first pattern |
| ML risk scoring via Databricks | Zero marginal cost per transaction |
| Azure Marketplace packageable | Works on Odoo CE (open source) |
