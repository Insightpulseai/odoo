# AFC Parity — Constitution

**Version:** 1.0 | **Status:** Approved | **Date:** 2026-03-15

## Non-Negotiable Rules

### P1 — SAP AFC is a behavioral benchmark, not a code dependency

The `SAP-docs/s4hana-cloud-advanced-financial-closing` GitHub repo (148 pages) is the public open benchmark for close orchestration patterns. SAP Tax Compliance is documented only on the proprietary SAP Help Portal — no public repo exists. Never treat SAP docs as importable code or SSOT.

### P2 — Odoo is the primary ERP, not a satellite

SAP AFC is a satellite coordination platform that connects to S/4HANA. Our architecture is fundamentally different — Odoo IS the ERP. Approximately 30 pages of SAP connectivity/communication system docs do not apply. Do not replicate satellite patterns.

### P3 — Template-first close orchestration

All financial close runs must be generated from templates. No ad-hoc close runs without a template definition. This mirrors SAP AFC's Task List Template pattern.

### P4 — Dependency-driven task sequencing

Task completion must enforce predecessor dependencies. Successors must not start until predecessors reach their required state. This is the highest-priority gap to close (successor invalidation cascade).

### P5 — Evidence-mandatory completion

Tasks marked as requiring evidence must have attachments before they can transition to completed state. No exceptions.

### P6 — Approval-gated state transitions

Material financial tasks require explicit digital sign-off before successors unlock. Approval status is tracked separately from task status (dual state machine, following SAP AFC pattern).

### P7 — PH statutory compliance is a hard constraint

BIR deadlines are non-negotiable. Compliance check failures within 7 days of a deadline must trigger escalation. Filing tasks cannot be bypassed.

### P8 — Audit trail immutability

All state transitions on close tasks, findings, and approvals must be logged to `mail.thread` chatter. Audit records are append-only — no deletions.

### P9 — No SAP Tax Compliance code reuse

SAP Tax Compliance is a proprietary add-on. Our Tax Pulse / BIR Compliance Pack is built independently using Odoo ORM, OCA modules, and custom `ipai_*` modules. Behavioral patterns may be benchmarked; code is never ported.

### P10 — Gap closure is sequenced, not simultaneous

Implementation follows the priority order defined in plan.md. Do not start P2 gaps before P1 gaps are resolved.
