# Agent Skill Sources

## Anthropic Skills (upstream reference)

- **Repo**: https://github.com/anthropics/skills
- **Purpose**: Examples/patterns for packaging tool-using workflows as reusable "skills".
- **Policy**: Treat as **reference + optional mirrored library**. Do not directly execute
  upstream skills in production without passing through our governance gates (taxonomy,
  secrets, deterministic IO, sandboxing).

## Governance

- Any adopted skill must be wrapped into our internal skill format and registered
  under `agents/skills/`.
- Skills that require external services must be classified as **Bridge** or **Connector**,
  never "parity addons".
- Skills are NOT Odoo modules. They do not have `__manifest__.py` and are never
  placed under `addons/`.

## Intake Pipeline

1. **Mirror**: `scripts/vendor/sync_anthropic_skills.sh` syncs upstream into
   `third_party/anthropic_skills/` (read-only).
2. **Index**: `scripts/skills/index_anthropic_skills.py` generates
   `reports/anthropic_skills_index.json` + `docs/agents/ANTHROPIC_SKILLS_INDEX.md`.
3. **Port**: Adopted skills are ported into `agents/skills/<skill-id>/` using the
   template at `agents/skills/_templates/anthropic_port/`.
4. **CI**: `.github/workflows/sync-anthropic-skills.yml` runs weekly + on-demand.
