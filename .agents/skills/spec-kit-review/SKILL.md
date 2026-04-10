---
name: Spec Kit Review
description: Validate spec bundle completeness — constitution, PRD, plan, tasks — and check alignment with SSOT, architecture docs, and target state
---

# Spec Kit Review Skill

## When to use
When creating, updating, or reviewing any spec bundle under `spec/<slug>/`.

## Required files per bundle

```
spec/<slug>/
├── constitution.md   # Non-negotiable rules and constraints
├── prd.md            # Product requirements
├── plan.md           # Implementation plan
└── tasks.md          # Task checklist with status
```

## Validation checks

1. All 4 files exist
2. Constitution defines clear boundaries and prohibited patterns
3. PRD references architecture docs where relevant
4. Plan references SSOT files and has phased delivery
5. Tasks have status markers (not started / in progress / done / blocked)
6. No contradictions with `AGENTS.md` or `.Codex/rules/`
7. No references to deprecated systems (see AGENTS.md deprecated table)
8. Architecture decisions reference `docs/architecture/` ADRs

## Naming convention

- Slug: kebab-case
- Example: `spec/odoo-copilot-azure-runtime/`
