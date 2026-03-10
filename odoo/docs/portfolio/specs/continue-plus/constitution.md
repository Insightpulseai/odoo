# Continue+ Constitution

## Purpose

This document defines the invariant rules that govern all agent behavior in this repository. Agents MUST read and obey this constitution before any action.

---

## 1. Spec-Kit Enforcement

### 1.1 Required Files

Every shippable feature MUST have a complete spec bundle:

```
spec/<slug>/
├── constitution.md   # Invariant rules (this pattern)
├── prd.md            # Product requirements
├── plan.md           # Implementation plan
└── tasks.md          # Checklist of work items
```

### 1.2 Quality Gates

- **No placeholders**: Files MUST NOT contain `TODO`, `TBD`, `LOREM`, `PLACEHOLDER`, or `[FILL IN]`
- **Minimum content**: Each file MUST have ≥100 words of substantive content
- **No empty sections**: All required headings MUST have content

### 1.3 Blocking Behavior

- `/ship` command MUST fail if spec-kit is incomplete
- PRs MUST reference spec slug in description
- Tasks checklist MUST be included in PR body

---

## 2. Role Separation

### 2.1 Planner Role

- MAY read any file
- MAY NOT edit any file
- MUST output structured plan to `spec/<slug>/plan.md`
- MUST list all files that will change

### 2.2 Implementer Role

- MAY read any file
- MAY edit only files listed in approved plan
- MUST prefer minimal diffs
- MUST document deviations from plan

### 2.3 Verifier Role

- MAY read any file
- MAY run verification commands from allowlist
- MAY make minimal fixes to pass checks
- MUST NOT introduce new features

---

## 3. CI Scope Rule

### 3.1 Diff Classification

Changes are classified into categories:

| Category | Paths | Triggers Odoo CI |
|----------|-------|------------------|
| Code | `addons/**`, `odoo/**` | YES |
| Docs | `docs/**`, `*.md` | NO |
| Spec | `spec/**` | NO |
| Agent Config | `.claude/**`, `.continue/**`, `CLAUDE.md` | NO |
| Infra | `.github/**`, `scripts/**`, `deploy/**` | NO (unless code also changed) |
| Tests | `tests/**` | YES |

### 3.2 Short-Circuit Rule

**Changes outside `addons/` or `odoo/` MUST NOT trigger Odoo CI.**

CI workflows MUST short-circuit based on diff classification.

### 3.3 Implementation

All Odoo CI workflows MUST include:

```yaml
on:
  pull_request:
    paths-ignore:
      - 'spec/**'
      - '.claude/**'
      - '.continue/**'
      - 'CLAUDE.md'
      - 'docs/**'
      - 'scripts/**'
      - '.github/workflows/spec-kit-*.yml'
      - '.github/workflows/agent-*.yml'
```

---

## 4. Safety Rules

### 4.1 Tool Allowlist

Agents MAY only execute commands from this allowlist:

```yaml
allowed_commands:
  - git status
  - git diff
  - git log
  - git add
  - git commit
  - python -m pytest
  - python -m flake8
  - python -m pylint
  - pre-commit run
  - odoo-bin --test-enable
  - npm test
  - npm run lint
  - make test
  - make lint
```

### 4.2 Forbidden Actions

Agents MUST NOT:

- Run commands not in allowlist without explicit user approval
- Echo or log secrets/credentials
- Modify `.git/` directly
- Force push to protected branches
- Delete files outside their plan scope

### 4.3 Credential Handling

- NEVER hardcode secrets
- NEVER commit `.env` files with real credentials
- ALWAYS use environment variable references

---

## 5. Output Standards

### 5.1 Plan Output Format

```markdown
## Scope
[What this change accomplishes]

## Assumptions
[What we assume to be true]

## Files to Change
- `path/to/file1.py` - [reason]
- `path/to/file2.md` - [reason]

## Risks / Rollback
[What could go wrong, how to undo]

## Verification Commands
- `command 1`
- `command 2`

## Tasks
- [ ] Task 1
- [ ] Task 2
```

### 5.2 Implementation Output Format

```markdown
## Files Changed
- `path/to/file1.py` - [summary of changes]

## Deviations from Plan
[Any changes not in original plan, with justification]
```

### 5.3 Verification Output Format

```markdown
## Commands Executed
- `command 1` - PASS
- `command 2` - FAIL → fixed → PASS

## Final Status
[PASS/FAIL] - [summary]
```

### 5.4 Ship Output Format

```markdown
## Summary
[1-3 sentences]

## Spec Reference
`spec/<slug>/`

## Changes
- [file-level summary]

## Verification Evidence
- [x] Lint: PASS
- [x] Tests: PASS
- [x] Type check: PASS

## Tasks Completed
- [x] Task 1
- [x] Task 2
```

---

## 6. Enforcement

### 6.1 Pre-Commit Hooks

The following checks run on every commit:

- Spec-kit presence validation
- Placeholder detection
- Minimum content check

### 6.2 CI Enforcement

The following checks run on every PR:

- `spec-kit-enforce.yml` - Validates spec bundle
- `agent-preflight.yml` - Classifies diff and gates CI

### 6.3 Blocking vs Warning

| Check | Default | Override |
|-------|---------|----------|
| Spec presence | BLOCK | `--allow-missing-spec` |
| Placeholder detection | WARN | `--strict-placeholders` |
| Minimum content | WARN | `--strict-content` |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-20 | Initial constitution |
