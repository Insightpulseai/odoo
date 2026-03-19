# Claude Code Plugins Policy

## Purpose

Define when we package extensions as plugins vs keeping them project-local (rules/skills/hooks).

## Default

Prefer project-local: `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, `.claude/hooks.json`.

## Plugin threshold

Promote to a plugin only if:
- used across 2+ repos, AND
- contains stable contracts (schemas/tools), AND
- has CI validation and versioning, AND
- does not embed secrets.

## Governance

- Plugins must not expand tool surface without corresponding tool specs + action eval coverage.
- Plugin tool specs must follow `contracts/tools/TOOL_SPEC_TEMPLATE.md`.
- Plugin eval cases must be registered in `eval/action_eval.yaml`.
