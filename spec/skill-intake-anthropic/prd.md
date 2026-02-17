# PRD: Intake Pipeline for Upstream Skills

> **Version**: 1.0.0
> **Date**: 2026-02-17

---

## Goal

Enable controlled adoption of upstream skills from https://github.com/anthropics/skills.

## Requirements

- Mirror upstream repo into `third_party/anthropic_skills/` (snapshot)
- Provide a converter template: upstream skill → `agents/skills/<name>/`
- Enforce gates:
  - Taxonomy + metadata classification
  - Deterministic IO schema (JSON Schema for inputs/outputs)
  - No embedded secrets
  - Sandbox-executable test harness

## Success Criteria

| Milestone | Criteria |
|-----------|----------|
| Mirror operational | Weekly sync produces updated index |
| First skill ported | At least one upstream skill ported into `agents/skills/` with tests |
| CI gates enforced | PR adding a skill without metadata/schema is blocked |
