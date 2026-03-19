# Odoo Copilot Benchmark — PRD

> Product requirements for the copilot benchmark framework.

---

## 1. Benchmark Targets

The benchmark framework evaluates the IPAI Odoo Copilot against two reference surfaces:

### General Copilot Benchmark (SAP Joule)

SAP Joule is the benchmark reference for general copilot capability across transactional, navigational, and informational classes. This evaluates whether the copilot can perform ERP operations, navigate to records, and answer business questions at enterprise-grade quality.

### Tax/Compliance Benchmark (AvaTax)

For tax and compliance workflows, the benchmark reference is the capability surface represented by AvaTax.

This benchmark is limited to:

- tax calculation and mapping quality
- jurisdiction/rule selection quality
- AP use-tax and exception handling
- batch and real-time workflow support
- compliance-grade explainability and audit support

The product may only be described as "surpassing the benchmark" if it demonstrates superior weighted benchmark performance on the approved tax/compliance task suite with no critical compliance failures.

#### Benchmark win conditions

1. Higher weighted composite score on approved tax/compliance workflows
2. Equal or better tax accuracy on priority workflows
3. Equal or better compliance-control behavior
4. Equal or better auditability/explainability
5. No critical compliance or unsafe-action failures

#### Claim discipline

Safe claims (if benchmark passes):

- "better fit for our target Odoo tax/compliance workflows"
- "outperforms the AvaTax benchmark surface on approved internal tasks"

Unsafe claims (never make without global parity evidence):

- "better than AvaTax overall"
- "global tax engine replacement"
- "equivalent tax content coverage"
- "same compliance footprint"

---

## 2. Evaluation Framework

See `ssot/evals/copilot_marketplace_benchmark.yaml` for the machine-readable benchmark definition including dimensions, weights, task sets, judges, and scoring thresholds.

See `constitution.md` in this spec bundle for the general copilot benchmark framework (transactional/navigational/informational classes, governance gates, evidence requirements).

---

## 3. Evidence Requirements

All benchmark claims require:

- Captured prompts and outputs
- Deterministic check results
- LLM judge scores (different model from candidate)
- Human expert review (Philippine finance/tax expert)
- Failure log with root cause analysis
- Audit examples demonstrating explainability

Evidence is stored at: `docs/evals/evidence/{YYYYMMDD-HHMM}/copilot_marketplace/`
