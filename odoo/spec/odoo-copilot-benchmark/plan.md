# Odoo Copilot Benchmark — Plan

> Implementation plan for the benchmark framework.

---

## General Copilot Benchmark (SAP Joule Reference)

See `constitution.md` for the full framework. Implementation phases:

1. Define scenario registry (9 domains × 3 capability classes)
2. Build scenario runner with evidence capture
3. Implement deterministic scoring model
4. Implement governance hard gates
5. Build reporting pipeline (per-domain, per-class summaries)
6. Execute first full benchmark run

---

## Tax/Compliance Benchmark (AvaTax Reference)

### Benchmark phases

1. Define tax/compliance task suite (25-40 canonical tasks)
2. Define gold outcomes and policy thresholds
3. Run repeated blind evaluations
4. Score with deterministic checks + LLM judge + human tax reviewer
5. Produce audit evidence pack
6. Approve or reject "surpasses benchmark" claim

### Scope

In scope:

- AP tax review
- use-tax / VAT / withholding classification support
- tax exception detection
- compliance note generation
- audit-ready explanation quality

Out of scope:

- generic ERP chat quality (covered by general benchmark)
- unsupported global tax-content parity claims
- vendor-specific product breadth not implemented in runtime
