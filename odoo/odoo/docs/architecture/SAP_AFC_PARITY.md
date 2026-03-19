# SAP AFC Parity — Architecture Reference

**Date:** 2026-03-15 | **Spec:** `spec/afc-parity/`

## Benchmark Sources

### 1. Public/open benchmark

- **Repo:** [`SAP-docs/s4hana-cloud-advanced-financial-closing`](https://github.com/SAP-docs/s4hana-cloud-advanced-financial-closing)
- **Content:** 148 markdown pages — close orchestration, templates, phases, archiving, user/admin patterns, security, integration capabilities
- **Sections:** Overview (3), Connectivity (32), User-Management (28), Business-Configuration (22), Integration-Capabilities (14), Data-Management (11), System-Monitoring (10), Security (7), Monitoring-and-Troubleshooting (4), Archiving (2), others (15)
- **Use for:** Close orchestration patterns, template design, approval workflows, archiving, user/admin patterns, dual status model

### 2. Proprietary benchmark

- **Source:** SAP Help Portal — SAP Tax Compliance for S/4HANA
- **Content:** Compliance checks, scenarios, worklists, remediation semantics, VAT checks
- **Access:** PDF/HTML only at `help.sap.com` — no public GitHub repo exists
- **Use for:** Behavioral reference only — compliance check design, finding/remediation semantics, worklist patterns
- **Do NOT:** Treat as importable code, quote as SSOT, or assume repo availability

### 3. Out-of-scope (architectural mismatch)

SAP AFC is a satellite system that connects to S/4HANA, ERP 6.0, etc. for remote job execution. Our Odoo is the primary ERP. The following SAP patterns do not apply:

- Communication system connectivity (32 pages)
- Remote job execution and scheduling queues
- Connection status monitoring (adaptive reconnection logic)
- SAP BTP integration (Fiori, Build Process Automation, Task Center, Work Zone)
- Cloud Connector setup

## Current Parity: ~60%

| Category | Count |
|---|---|
| Full parity | 18 features |
| Partial parity | 10 features |
| Gaps (P1) | 4 features |
| Gaps (P2) | 5 features |
| Gaps (P3) | 2 features |
| Not applicable | ~30 pages of SAP docs |

## Gap Closure Priority

First engineering target: **Successor invalidation cascade (G-01)**

This is the highest-value gap — it enables automated dependency chain resolution, which is foundational for all subsequent close orchestration improvements.

See `spec/afc-parity/plan.md` for the full phased implementation plan.

## Key SAP AFC Concepts Mapped to Odoo

| SAP AFC Concept | Odoo Equivalent |
|---|---|
| Task List Template | `close.template` (to be added to `ipai_finance_ppm`) |
| Task List (runtime) | `close.run` (to be added) |
| Task Group Template | Reusable task set within template |
| Task Status (11 states) | Odoo task `state` selection (extend) |
| Approval Status (5 states) | Separate approval field on task |
| Closing Key Date | Period end date on `close.run` |
| Communication System | N/A (Odoo is primary) |
| Factory Calendar | `resource.calendar` with PH holidays |
| Company Code Group | `res.company` hierarchy |

## Related Specs

- `spec/afc-parity/` — This gap closure spec bundle
- `spec/tax-pulse-sub-agent/` — Tax Pulse agent (SAP Tax Compliance is behavioral benchmark only, not code dependency)
- `spec/tax-compliance-ph-odoo/` — PH tax compliance TCMS design
