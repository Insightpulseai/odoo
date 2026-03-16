# Constitution: Odoo Copilot – Process Mining (Local-First)

## Principles

1. **Local-first capture and analysis**: raw event logs can be collected and processed on-prem.
2. **Minimal invasive instrumentation**: prefer existing Odoo models/logs, avoid UI scripts.
3. **Deterministic pipelines**: idempotent extraction and transformation.
4. **Explainable insights**: every recommendation links to evidence (case ids, timestamps, events).
5. **Privacy and compliance**: configurable redaction and retention; PII-aware schemas.
6. **Extensible connectors**: Odoo DB + logs + optional external systems.

## Non-goals

- Full "screen recording" RPA unless explicitly enabled later.
- Replacing Odoo workflows; this is analytics + recommendations.

## Data Sovereignty

- All raw event data stays within the Odoo infrastructure boundary.
- Only aggregated, anonymized metrics may optionally sync to external systems.
- Sensitive fields (partner names, amounts, user IDs) must be redactable via configuration.

## Conformance Rules

- Rules engine must be declarative and auditable.
- Every deviation must reference the specific rule and evidence that triggered it.
- False positive rates should be tracked and rules tuned accordingly.
