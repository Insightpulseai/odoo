# Skill Intake Constitution (Anthropic → IPAI)

> **Version**: 1.0.0
> **Date**: 2026-02-17

---

## Non-Negotiables

1. Upstream skills are **examples**, not production artifacts.
2. Any adopted skill must be re-authored into our internal format under `agents/skills/`.
3. Skills must declare taxonomy: `{tool-only | connector | bridge}`.
4. Secrets are never embedded; env placeholders only.
5. Deterministic IO: inputs/outputs must be JSON schema'd; no hidden side effects.

---

## Taxonomy Mapping

| Upstream Skill Type | Our Classification | Lives In |
|--------------------|--------------------|----------|
| Pure tool/prompt workflow | `tool-only` | `agents/skills/<id>/` |
| Requires external API | `connector` | `agents/skills/<id>/` + bridge config |
| Runs as separate service | `bridge` | `bridges/<service>/` |

---

## Intake Workflow

```
Mirror (read-only) → Index → Evaluate → Port → Test → Register
```

1. **Mirror**: `third_party/anthropic_skills/` (automated weekly sync)
2. **Index**: `reports/anthropic_skills_index.json` (automated)
3. **Evaluate**: Manual review of upstream SKILL.md for applicability
4. **Port**: Copy into `agents/skills/<id>/` using template, add metadata + schemas
5. **Test**: Run deterministic test harness with golden fixtures
6. **Register**: Add to `agents/skills/registry.json` (or similar manifest)

---

## Constraints

- Skills are NOT Odoo modules. No `__manifest__.py`, no `addons/` placement.
- No secrets in repo. Use env placeholders (`$SKILL_API_KEY`, etc.).
- Upstream files in `third_party/` are read-only. All modifications go in `agents/skills/`.
- Skills must not introduce new runtime dependencies without review.
