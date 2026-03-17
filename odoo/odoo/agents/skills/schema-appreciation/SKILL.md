---
description: Ensure database schema context is queried progressively, safely, and accurately without blind large-scale dumps.
---

# Schema Appreciation Skill

You are running the Schema Appreciation Skill.

## Objective

- Understand the minimal necessary schema context for the requested task using progressive disclosure.
- Use the meta introspection layer as ground truth; never dump raw DDL as a first step.

## Rules (hard)

- No blind queries. Start with `meta.*` only.
- Follow probe budget (max queries/rows/time). Avoid row-level PII.
- You must explicitly identify: grain, canonical join keys, event_time vs processed_time.

## Procedure

1. Identify likely entities/tables/views by searching `meta.tables` + `meta.dictionary`.
2. Expand only the relevant objects:
   - `meta.columns` for column types/nullability/defaults
   - `meta.relationships` for join paths
   - `meta.constraints` / `meta.indexes` for correctness/perf constraints
   - `meta.policies` for RLS constraints
3. Validate assumptions with probes:
   - cardinality/rowcounts (metadata-first)
   - null rates for keys
   - distinct key checks (sampled or stats-based)
   - min/max timestamps for event_time and processed_time
4. Produce outputs:
   - A concise schema map (entities, join paths, keys)
   - Time semantics: which column is event time, which is processed time
   - Any risks (missing FK, nullable key, RLS restrictions, unindexed joins)

Stop once context is sufficient to proceed with the actual task.
