# Parity Agent Constitution (non-negotiables)

- Parity is defined as: (1) feature availability, (2) user-visible behavior, (3) data model + API contracts, (4) operational characteristics (SLOs, auditability).
- Every parity claim MUST be backed by: reproducible tests, versioned evidence, and a traceable mapping to upstream docs/code.
- OCA-first, external-service-second, minimal custom glue last.
- No manual UI steps in pipelines. Everything is CLI/CI reproducible.
- Every integration has a contract test (schema + API + auth + event semantics).
