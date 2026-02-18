# anthropics/skills mirror

This directory is a vendored snapshot of Anthropic's public Agent Skills repository.

- **Upstream**: https://github.com/anthropics/skills
- **Sync script**: `scripts/vendor/sync_anthropic_skills.sh`
- **Index**: `reports/anthropic_skills_index.json` + `docs/agents/ANTHROPIC_SKILLS_INDEX.md`

## Policy

- Treat as **READ-ONLY** mirror. Do not edit upstream files in-place.
- Any skill we adopt gets ported into `agents/skills/<skill-id>/` with our metadata + tests.
- Skills are NOT Odoo modules. They are agent instruction packages and/or workflow wrappers.
- Upstream skills are organized as folders containing `SKILL.md`.

## Governance

- Adopted skills must pass through `spec/skill-intake-anthropic/constitution.md`.
- Skills that require external services must be classified as **Bridge** or **Connector**, never "parity addons".
- No secrets in repo. Environment placeholders only.
