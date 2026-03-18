# Constitution — Target Platform Architecture

## Purpose

Define the non-negotiable architectural rules for the target platform.

## Principles

1. Use explicit truth planes.
2. Separate platform landing zone concerns from workload/application landing zone concerns.
3. Keep control plane and data plane distinct.
4. Treat Odoo as transactional core, not analytics or agent core.
5. Treat Databricks as data/ML engineering core, not ERP.
6. Treat Foundry as agent runtime/model/tool/eval core, not business SoR.
7. Keep tenant context explicit across all workload planes.
8. Prefer shared platform controls with selective workload isolation.
9. Benchmark against external architectures without forcing literal vendor dependencies.
10. Prefer deterministic diagram sources and exported artifacts.

## Non-goals

- all-in-one monolith
- implicit tenancy
- shadow control planes
- undocumented cross-plane ownership
