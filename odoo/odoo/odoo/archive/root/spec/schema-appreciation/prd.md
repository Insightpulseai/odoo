# Product Requirements Document: Schema Appreciation Skill

## Overview

A production-grade schema validation skill for agentic workflows to ensure agents query, understand, and verify the database schema using a progressive disclosure approach rather than blind, full-DDL ingestion.

## Requirements

- **Progressive Retrieval**: Agents must query entities progressively (name search -> columns -> relationships -> fast probes).
- **Meta Schema Layer**: A dedicated Supabase `meta` schema containing read-only introspection views (`tables`, `columns`, `relationships`, `indexes`, `policies`) and a manually curated `dictionary`.
- **Semantic Dictionary**: A table mapping physical entities to business logic (grain, event vs processing time, canonical IDs, PII classification).
- **Probing Rules**: Agents must run small, non-destructive probes (e.g., `COUNT(*)`, distinct keys, 10-row masked samples) before writing production SQL.
- **CI Enforcement**: Schema migrations must be accompanied by semantic dictionary updates and ERD exports.

## Meta Schema Contract

The meta layer is a stable, queryable API for schema introspection. Agents MUST use it before touching domain tables.
Required views (minimum): `meta.tables`, `meta.columns`, `meta.relationships`, `meta.indexes`, `meta.constraints`, `meta.policies`, `meta.functions`, `meta.triggers`, `meta.extensions`.
Views MUST be backward-compatible (additive changes only) unless a contract version bump is declared.

## Probe Budget and Probe Protocol

Agents MUST follow a probe budget (max queries, max rows returned, max runtime) and a deterministic probe order:

1. rowcount/cardinality (metadata-first)
2. key integrity checks (PK/FK presence, null rates)
3. time semantics (event vs processed time)
4. join sanity checks for intended join paths

Agents MUST avoid row-level PII reads.

## Semantic Dictionary Schema

`meta.dictionary` MUST include: entity, grain, canonical_id, `join_keys[]`, event_time_column, processed_time_column, pii_classification, and notes.
