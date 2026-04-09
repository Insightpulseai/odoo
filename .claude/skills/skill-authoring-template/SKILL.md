---
name: Skill Authoring Template
description: Create or revise Claude Code project skills. Use when building new skills under .claude/skills, adding knowledge-backed templates, or standardizing skill best practices.
---

# Skill Authoring Template

## Goal

Produce focused, discoverable, knowledge-backed skills that Claude can invoke reliably.

## Required principles

- One skill = one capability.
- Keep the skill focused and composable.
- The description must include:
  - what the skill does
  - when Claude should use it
- Prefer progressive disclosure:
  - concise `SKILL.md`
  - optional `reference.md`
  - optional `examples.md`
  - optional `templates/`
  - optional `scripts/`

## Required sections for new skills

1. `Purpose`
2. `When to use`
3. `Inputs or assumptions`
4. `Workflow`
5. `Output format`
6. `Source priority`
7. `Verification`
8. `Anti-patterns`

## Knowledge-backed skill rule

Every knowledge-based skill must define source priority explicitly:
1. local indexed project knowledge
2. official external source (for Microsoft topics: Microsoft Learn MCP)
3. other official upstream docs only if needed

## Template skeleton

Use this skeleton for new skills:

```md
---
name: <Skill Name>
description: <What it does>. Use when <clear triggers>.
---

# <Skill Name>

## Purpose

## When to use

## Inputs or assumptions

## Source priority

## Workflow

## Output format

## Verification

## Anti-patterns
```

## Best practices

- Prefer a narrow trigger description over a broad one.
- Add examples for edge cases.
- Do not hide critical behavior in external files without referencing them from `SKILL.md`.
- If a skill depends on official docs, state that dependency clearly.
