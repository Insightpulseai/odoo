# Claude Code Extension Layer (Repo Map)

This repo uses Claude Code's extension primitives as deterministic governance over agent behavior.

## CLAUDE.md (persistent instructions)

| Path | Status | Purpose |
|------|--------|---------|
| `/CLAUDE.md` | PRESENT | Repo SSOT pointer + minimal invariants + verify loop |

## Rules (scoped instructions)

| Path | Status | Purpose |
|------|--------|---------|
| `/.claude/rules/ssot-platform.md` | PRESENT | SSOT platform rules (10 rules, CI enforcement) |

## Skills (reusable workflows)

| Path | Status | Purpose |
|------|--------|---------|
| `/.claude/skills/ui-ux-pro-max/SKILL.md` | PRESENT | UI/UX design system skill (colors, typography, components) |
| `/.claude/skills/oca-module-porter/SKILL.md` | PRESENT | OCA module 18.0->19.0 porting skill (migration checklist) |

## Subagents (isolated contexts)

| Path | Status | Purpose |
|------|--------|---------|
| `/.claude/agents/` | RESERVED | Directory does not exist yet; will host read-only investigator and other isolated-context agents |

## Hooks (deterministic enforcement)

| Path | Status | Purpose |
|------|--------|---------|
| `/.claude/hooks.json` | RESERVED | File does not exist yet; will enforce before_commit gates (tool spec contract, SSOT validation) |

## MCP (tool bus)

| Path | Status | Purpose |
|------|--------|---------|
| `.mcp.json` | RESERVED | Project MCP server descriptors (kept out of repo per policy) |

## CI gates

| Path | Status | Purpose |
|------|--------|---------|
| `.github/workflows/` | PRESENT | 153 existing workflows |
| Tool-spec contract gate | PLANNED | Will enforce tool spec + ledger + eval consistency |

## Reference docs

| Path | Status | Purpose |
|------|--------|---------|
| `docs/agents/output_contract.md` | PRESENT | Agent output contract (structured envelope format) |
| `docs/agents/CLAUDE_CODE_PLUGINS_POLICY.md` | PRESENT | When to use plugins vs project-local extensions |
| `docs/agents/SKILLS_SOURCES.md` | PRESENT | Skills and sources documentation |
| `docs/agents/REGISTRY_SCHEMA.md` | PRESENT | Agent registry schema |
| `docs/agents/REGISTRY_ASSESSMENT.md` | PRESENT | Registry assessment |
| `docs/agents/LOCAL_LLM_ROUTING.md` | PRESENT | Local LLM routing |

---

*This document indexes all Claude Code extension primitives in this repo.*
*PRESENT = verified via filesystem. RESERVED = planned, not yet created. PLANNED = to be implemented.*
