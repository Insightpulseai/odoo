# IPAI Skill Development Pattern

> **Locked:** 2026-04-15
> **Authority:** this file (how IPAI authors skills, modeled on `microsoft/azure-skills`)
> **Doctrine source:** `microsoft/azure-skills` — registered `consume_directly`
> **Compose with:** [`anthropics/skills`](../architecture/capability-source-map.md) spec + patterns

---

## The canonical pattern (adopted from `microsoft/azure-skills`)

Microsoft built `azure-skills` as a **packaged agent capability layer**, not a prompt library. Three layers in one install:

```
  Skills (the brain)       → decision logic, workflows, guardrails
  MCP servers (the hands)  → live tool execution
  Host adapters (thin)     → Claude Code / Copilot CLI / VS Code / Gemini
```

Core insight: **skill = authoritative workflow contract**, not a prompt.

## 5 patterns to copy (exact)

### 1. Skill = one bounded scenario

```
One scenario → one skill → one SKILL.md → one references/ → one tool allowlist → one guarded workflow
```

Don't build mega-skills. `azure-deploy` is only for *already-prepared* apps. For creating apps, use `azure-prepare`. That's discipline.

### 2. Force workflow sequencing via hard prerequisites

`azure-deploy` refuses to run unless:
- `azure-prepare` already ran
- `azure-validate` already ran
- `.azure/deployment-plan.md` exists
- plan status = `Validated`
- validation proof present

**Not best-effort guidance — hard stops.** Runbook system, not prompt library.

### 3. Separate guidance from execution

```
Skills       = what SHOULD happen
MCP/tools    = DO the actions
Runtime      = separate from policy
```

The `.claude-plugin/`, `.cursor-plugin/` folders are host packaging — **not the intellectual asset**. The value is in skill boundaries + workflow sequencing + recipes + tool bindings.

### 4. Skill structure

```
skills/<skill-name>/
├── SKILL.md                  # orchestration contract + front matter
│   ├── name
│   ├── description
│   ├── triggers              # when this skill activates
│   ├── do-not-use-when       # anti-triggers
│   ├── prerequisites         # hard stops
│   ├── step table            # ordered workflow
│   ├── rules                 # rules the agent must obey
│   └── mcp bindings          # which tools this skill can call
└── references/               # detailed operational knowledge
    ├── recipe.md             # the concrete how-to
    ├── checklist.md          # pre/post checklists
    ├── troubleshooting.md    # known failures + fixes
    └── sdk-notes.md          # implementation guidance
```

### 5. Multi-host packaging — thin adapter only

The skill corpus is portable. Host wrappers (Claude / Copilot / VS Code / Gemini) are thin. Same skill bodies, different discovery mechanisms. **Don't let host packaging become the product.**

---

## Apply to IPAI — first 10 skills to build

Tight scope. Bounded scenarios. Our planes only.

| # | Skill | Purpose | Tools allowed | Prerequisites |
|---|---|---|---|---|
| 1 | `ipai-azure-bom` | Validate a resource against BOM v2 before deploy | `mcp__azure__*` (read-only) | None |
| 2 | `ipai-azure-tags` | Apply + verify 17 mandatory tags | `mcp__azure__*` tag ops | `ipai-azure-bom` green |
| 3 | `ipai-foundry-runtime` | Inspect + wire Foundry models + project | Foundry MCP | `ipai-azure-bom` green |
| 4 | `ipai-odoo-runtime` | Inspect Odoo container + trigger module install | ACA exec + Odoo MCP (future) | Container reachable |
| 5 | `ipai-prismalab-tools` | Author / test PrismaLab tool skills | Foundry + AI Search | Search index live |
| 6 | `ipai-bir-close` | Run month-end close cadence + BIR filings | Odoo MCP + compliance register | Close period open |
| 7 | `ipai-databricks-semantic` | Author + promote Databricks Asset Bundles | `databricks/cli` | Workspace reachable |
| 8 | `ipai-boards-operating-model` | Manage Azure Boards portfolio + dashboards | ADO MCP | Project exists |
| 9 | `ipai-pulser-artifact-emitter` | Emit artifacts in canonical envelope | None (output-only) | — |
| 10 | `ipai-pipeline-compose` | Compose Azure Pipeline from templates | Local yaml | Templates exist |

All 10 are **composition** over already-registered upstreams. No new modules, no forks.

---

## Repo folder structure (per `microsoft/azure-skills` pattern)

```
.claude/skills/
├── ipai-azure-bom/
│   ├── SKILL.md
│   └── references/
│       ├── bom-validation-recipe.md
│       ├── pre-deploy-checklist.md
│       └── troubleshooting.md
├── ipai-azure-tags/
│   └── ...same shape...
├── ipai-foundry-runtime/
│   └── ...
... etc
```

## `SKILL.md` template (canonical for IPAI)

```markdown
---
name: ipai-<scope>
description: <one-line, used by agent for discovery>
triggers:
  - <when this skill should activate>
do-not-use-when:
  - <explicit anti-triggers>
prerequisites:
  - <hard stops — skill refuses if missing>
tools:
  allowed:
    - mcp__azure__*
    - mcp__azure-devops__*
  forbidden:
    - anything not in `allowed`
references:
  - ./references/<recipe>.md
---

# <Skill Name>

## When to use
<brief>

## Hard prerequisites (skill stops if any fail)
1. <check 1>
2. <check 2>

## Workflow

| Step | Action | Tool | Evidence |
|------|--------|------|----------|
| 1 | ... | mcp__... | saved to ... |
| 2 | ... | ... | ... |

## Rules
- <hard rule 1>
- <hard rule 2>

## Anti-patterns
- <what NOT to do>

## References
- [Recipe](./references/recipe.md)
- [Checklist](./references/checklist.md)
```

---

## Pattern guardrails (what NOT to copy)

### Don't

- Let host packaging become the product — it's thin adapters only
- Build too many skills too early — 10 bounded beats 40 soft
- Make every skill generic — **opinionated is good**
- Skip the `references/` folder — recipes + checklists are where the real value lives
- Use skills as prompt libraries — they're workflow contracts with tool allowlists

### Do

- One bounded scenario per skill
- Hard prerequisites over best-effort guidance
- Allowlist MCP tools per skill (default: deny)
- Put recipes/checklists next to the skill body
- Package once → run on Claude / Copilot / VS Code / Gemini

---

## The repo doctrine in one line

```
Skills ARE authoritative runbooks.
Not prompt libraries.
Not documentation.
Not tool wrappers.
RUNBOOKS — with prerequisites, allowlists, and hard stops.
```

---

## References

- `microsoft/azure-skills` — source pattern (registered `consume_directly`)
- [`../architecture/capability-source-map.md`](../architecture/capability-source-map.md)
- [`../architecture/pulser-assistant-surface-design.md`](../architecture/pulser-assistant-surface-design.md) — 5 surfaces this pattern serves
- [`anthropics/skills`](https://github.com/anthropics/skills) — Agent Skills spec

---

*Last updated: 2026-04-15*
