# Reverse PRD — Better Fivetran (Fluxrail)

## Product Name: Fluxrail

## Summary

Governed data movement and activation platform. Fivetran-grade reliability without black-box connector behavior, weak semantic understanding, or limited workflow closure. Combines managed replication, schema-aware transformations, activation, and evidence-backed operational controls.

## Benchmark

Fivetran: 700+ connectors, automated data movement, hybrid deployment, transformations, governance, activations, managed data lake support.

## Problem

Data movement products behave like pipeline utilities, not operational systems:
- Connector state is opaque
- Schema drift explained poorly
- Activation is bolted on
- Lineage is not decision-grade
- Business users depend on data engineers for edge cases
- Pipeline changes not treated as governed product changes

## Target Users

Data platform teams, analytics engineering, RevOps/FinOps/Marketing ops, embedded analytics vendors, enterprise IT (ERP + SaaS + warehouse sync)

## Goals

1. Connector reliability comparable to Fivetran
2. Every sync explainable, inspectable, reversible at contract level
3. Unify ingest, transform, semantic mapping, activation in one governed model
4. Reduce time from new source connection to trusted downstream use
5. Operations first-class: drift, replay, approval, rollout, rollback, evidence

## Non-Goals

- Generic notebook platform
- Full BI replacement
- Ungoverned low-code playground
- Arbitrary code execution inside production connector workers

## Product Principles

1. **Pipelines are products** — versioned, reviewable, auditable
2. **Explainability beats magic** — auto-mapping visible, not hidden
3. **Governance built-in** — part of daily workflow, not side menu
4. **Activation equals ingestion** — reverse ETL is core, not premium
5. **Hybrid is normal** — private network, BYO compute, regional control standard

## Functional Requirements

- FR-1: Connector contract model (source metadata, table/field map, type inference, drift history)
- FR-2: Controlled schema evolution (auto-accept, approval-required, staged rollout, replay)
- FR-3: Unified activation (warehouse ingestion, reverse sync, event/webhook/API, scheduled/triggered)
- FR-4: Semantic sync layer (business objects: account, customer, invoice, order)
- FR-5: Evidence-backed operations (run summary, schema changes, policy violations)
- FR-6: Hybrid and residency control (cloud, hybrid worker, customer VNet)
- FR-7: Embedded mode (customer-facing sync setup and health)
- FR-8: AI-assisted remediation (field mappings, type corrections, drift fixes — reviewable)

## Key Differentiators vs Fivetran

- Explicit sync contracts (not opaque)
- Schema approval workflows
- First-class semantic object mapping
- Evidence-native run operations
- Stronger reverse/activation parity
- Embedded customer-facing pipeline UX
- AI-guided but reviewable remediation

## IPAI Mapping

| Fluxrail Concept | IPAI Implementation |
|-----------------|---------------------|
| Connector contracts | `ops_platform__contracts__connection_registry__v1.registry.yaml` |
| Schema evolution | Supabase migrations + dbt models |
| Activation (reverse ETL) | n8n workflows → Odoo/Supabase |
| Semantic layer | Databricks Unity Catalog + Lakebase |
| Evidence operations | `ops.run_events` in Supabase |
| Hybrid compute | ACA + Databricks + n8n |
| Embedded mode | Databricks Apps + web/ |
| AI remediation | Foundry copilot tools |

## Release Thesis

If Fivetran is "automated data movement," Fluxrail is **governed operational data movement with explainable activation**.
