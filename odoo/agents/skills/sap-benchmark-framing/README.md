# sap-benchmark-framing

Identifies and classifies SAP on Azure patterns as benchmarks vs mandatory integrations.

## When to use
- Architecture review references SAP patterns
- Need to determine if SAP is benchmark or dependency
- New benchmark source needs classification

## Key rule
SAP on Azure = benchmark for architecture quality. Odoo on Azure = implementation target.
A benchmark becomes an integration only when an explicit contract exists in `docs/contracts/`.
