# Tasks: Schema Appreciation Skill

- [ ] Create `db/migrations/XXXXXX_create_meta_schema.sql`.
- [ ] Define `meta.tables`, `meta.columns` views reflecting `information_schema`.
- [ ] Define `meta.dictionary` table.
- [ ] Implement CI step to generate `docs/schema/schema.json` and `docs/schema/schema.md`.
- [ ] Update `agents/skills/schema-appreciation/SKILL.md` with progressive disclosure workflow rules.
- [ ] Update `spec/agent/constitution.md` to reference the Schema Appreciation skill as mandatory for database operations.
- [ ] Implement meta schema contract: create required views with stable columns.
- [ ] Implement probe-budget enforcement in the skill runtime (max queries/rows/time).
- [ ] Add snapshot generator producing `docs/schema/schema.json`, `docs/schema/schema.md`, `docs/schema/semantic_dictionary.json`.
- [ ] Add CI checks: snapshot drift, dictionary coverage threshold, contract-breaking change detection.
- [ ] Deprecate `docs/supabase/context` (mark legacy; stop refresh).
