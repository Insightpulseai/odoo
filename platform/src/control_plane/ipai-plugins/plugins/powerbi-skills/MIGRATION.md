# Power BI Skills Migration Guide

This plugin migrates the legacy `.claude/commands/` based Power BI logic to the new **Claude Code Skills** format.

## Before

Legacy commands were stored in `.claude/commands/`:
- `dax-fix.md`
- `pbip-init.md`

## After

Skills are now namespaced and modularized:
- `/powerbi-skills:dax-authoring`
- `/powerbi-skills:pbip-scaffolding`

## Porting Instructions

To port a legacy command to a skill:
1. Create a directory in `skills/<name>/`.
2. Move the `.md` content to `SKILL.md`.
3. Add YAML frontmatter with `name` and `description`.
4. Register the skill in `.claude-plugin/plugin.json`.

---

*Last updated: 2026-04-12*
