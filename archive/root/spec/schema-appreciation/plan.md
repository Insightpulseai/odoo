# Implementation Plan: Schema Appreciation Skill

## Phase 1: Meta Schema Introspection

- Write SQL migrations to create the `meta` schema in Supabase.
- Create views: `meta.tables`, `meta.columns`, `meta.relationships`, `meta.indexes`, `meta.policies` over `pg_catalog` and `information_schema`.

## Phase 2: Semantic Dictionary Setup

- Create `meta.dictionary` to hold entity name, IDs, time semantics, grain, common filters, and PII markers.
- Populate initial semantic values for core tables.

## Phase 3: Agent Skill Definition

- Define the Agent Skill (trigger, prompt rules) that enforces the progressive disclosure workflow:
  1. Determine relevant entities.
  2. Query `meta` schemas for selected tables.
  3. Verify grain and time fields.
  4. Probe data.
- Add "Schema Appreciation Checklist" to agent standards.

## Phase 4: CI Governance

- Add schema snapshot checks to the CI pipeline.
- Enforce that dictionary entries stay synchronized with schema changes.

## Phase 5: Governance Hardening

- Formalize meta schema contract versioning and backward-compat rules.
- Add dictionary coverage thresholds for Tier-1 entities.
- Add CI gate for contract-breaking changes and missing snapshots.
