# Agentic Rules (Continue)

## Overview

This repository uses the **Continue+** spec-kit system. All agent behavior must follow these rules.

## Before Any Action

1. Read `CLAUDE.md` for project-level instructions
2. Read `spec/<slug>/constitution.md` for invariant rules
3. Check `spec/<slug>/plan.md` for approved implementation plan
4. Check `spec/<slug>/tasks.md` for current task status

## Role Boundaries

### Planner Role (`/plan`)
- MAY read any file
- MAY NOT edit any file
- MUST output structured plan to `spec/<slug>/plan.md`
- MUST list all files that will change
- MUST identify risks and rollback strategy

### Implementer Role (`/implement`)
- MAY read any file
- MAY edit only files listed in approved plan
- MUST prefer minimal diffs
- MUST document any deviations from plan
- MUST NOT introduce scope creep

### Verifier Role (`/verify`)
- MAY read any file
- MAY run verification commands from allowlist
- MAY make minimal fixes to pass checks
- MUST NOT introduce new features
- MUST document all commands executed

## CI Awareness

### Path Classification

| Category | Triggers Odoo CI |
|----------|------------------|
| `addons/**`, `odoo/**` | YES |
| `docs/**`, `*.md` | NO |
| `spec/**` | NO |
| `.claude/**`, `.continue/**` | NO |
| `.github/**`, `scripts/**` | NO |

### Rules

1. Changes outside `addons/` or `odoo/` MUST NOT trigger Odoo CI
2. Infra-only changes MUST NOT touch business logic in `addons/`
3. When CI is Odoo-related and no addons changed:
   - Propose CI path-ignore fix
   - Do NOT touch business logic

## Safety

### Allowed Commands

```yaml
allowed_commands:
  - git status
  - git diff
  - git log
  - git add
  - git commit
  - python -m pytest
  - python -m flake8
  - pre-commit run
  - odoo-bin --test-enable
```

### Forbidden

- Run commands not in allowlist without explicit approval
- Echo or log secrets/credentials
- Modify `.git/` directly
- Force push to protected branches
- Delete files outside plan scope

## Output Standards

All outputs must follow the formats defined in `spec/continue-plus/constitution.md`.
