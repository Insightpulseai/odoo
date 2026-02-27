# Governance: Schema Appreciation

## 1. No Blind Queries

Agents are strictly forbidden from writing production `INSERT`/`UPDATE`/`DELETE` queries without first probing the schema and understanding the grain.

## 2. Introspection via `meta` Schema

Agents must use the `meta.*` views to discover schema layout, never relying solely on raw `pg_catalog` or assumptions.

## 3. Semantic Grounding

Agents must consult `meta.dictionary` to differentiate between `event_time` and `processed_time`, to identify PII, and to confirm the true grain of the table.

## 4. Evidence of Verification

All generated SQL must be preceded by lightweight probes (e.g., `COUNT(*)`, non-PII row sampling) to prove the agent's schema assumptions are correct before proceeding.

## 5. Contract Stability

`meta.*` is a stable API. Breaking changes require explicit version bump and migration notes.

## 6. Probe Budget

No blind queries; no unlimited scanning. Probe budgets are mandatory.

## 7. PII Safety

Agents MUST not select raw PII fields; schema-level metadata and masked sampling only.
