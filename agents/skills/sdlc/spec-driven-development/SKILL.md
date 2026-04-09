# Skill: Spec-Driven Development

## Metadata

| Field | Value |
|-------|-------|
| **id** | `spec-driven-development` |
| **domain** | `sdlc` |
| **source** | Microsoft Agentic SDLC pattern (Phase 1) |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, odoo |
| **tags** | spec-kit, requirements, constitution, task-decomposition |

---

## Pattern

Every code change starts from a structured specification, never from an ad-hoc prompt. The spec constrains the agent's scope, tech stack, and output format through a constitution file.

---

## Workflow

```
1. User provides natural-language intent
2. Spec agent generates structured spec (PRD + plan + tasks)
3. Constitution validates constraints (tech stack, banned patterns, org rules)
4. Tasks decompose into scoped GitHub issues
5. Each issue triggers a coding agent (one issue = one PR)
```

---

## Constitution File

The constitution is the governance document that constrains agent behavior. It defines:

- **Tech stack**: What frameworks, languages, and tools are allowed
- **Banned patterns**: What the agent must never do (e.g., no Enterprise modules, no IAP)
- **Org standards**: Commit convention, naming rules, testing requirements
- **SSOT boundaries**: Which repo owns which domain

### IPAI Constitution Sources

| Source | Path |
|--------|------|
| Global agent rules | `CLAUDE.md` (repo root) |
| OCA governance | `~/.claude/rules/oca-governance.md` |
| Odoo 18 coding | `~/.claude/rules/odoo18-coding.md` |
| SSOT platform | `.claude/rules/ssot-platform.md` |
| Infrastructure | `~/.claude/rules/infrastructure.md` |
| Secrets policy | `~/.claude/rules/secrets-policy.md` |
| Agentic SDLC constitution | `agents/foundry/agentic-sdlc-constitution.md` |

---

## Spec Bundle Structure

```
spec/<feature-name>/
├── constitution.md    # Governance constraints for this feature
├── prd.md             # Product requirements document
├── plan.md            # Technical implementation plan
├── tasks.md           # Decomposed, scoped tasks
└── evidence/          # Verification artifacts
```

---

## Task Decomposition Rules

1. **One task = one PR** — never combine unrelated changes
2. **Scope narrowly** — "Add field X to model Y" not "Implement feature Z"
3. **Include acceptance criteria** — each task has a testable definition of done
4. **Reference SSOT** — each task names the file(s) it will modify
5. **Estimate blast radius** — flag tasks that cross SSOT boundaries

---

## IPAI Slash Commands

| Command | Purpose |
|---------|---------|
| `/speckit.specify` | Create spec from intent |
| `/speckit.plan` | Generate implementation plan |
| `/speckit.tasks` | Decompose plan into tasks |
| `/speckit.clarify` | Resolve ambiguities before planning |
| `/speckit.constitution` | Create/update governance constraints |
| `/speckit.implement` | Execute tasks from plan |

---

## Supabase Schema (ops.specs)

```sql
CREATE TABLE IF NOT EXISTS ops.specs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES ops.tenants(id),
    title TEXT NOT NULL,
    intent TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'active', 'completed', 'cancelled')),
    spec_bundle JSONB NOT NULL DEFAULT '{}',
    constitution_hash TEXT,
    github_repo TEXT,
    created_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ops.spec_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spec_id UUID REFERENCES ops.specs(id) ON DELETE CASCADE,
    task_index INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked', 'cancelled')),
    github_issue_number INTEGER,
    github_pr_number INTEGER,
    assignee TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_specs_status ON ops.specs(status);
CREATE INDEX idx_spec_tasks_spec_id ON ops.spec_tasks(spec_id);
CREATE INDEX idx_spec_tasks_status ON ops.spec_tasks(status);
```

---

## Related Skills

- [agentic-sdlc-msft-pattern](../agentic-sdlc-msft-pattern/SKILL.md) — Full pattern overview
- [sre-feedback-loop](../sre-feedback-loop/SKILL.md) — Day-2 ops loop that feeds back into specs
