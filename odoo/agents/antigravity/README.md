# Antigravity Professional Pack

**Purpose**: Codify repeatable "professional developer" workflows for end-to-end task delegation with artifact-based verification.

---

## Philosophy

**Ship faster with less context switching** by:

- Delegating end-to-end tasks to agents
- Running long maintenance work asynchronously
- Verifying via **Artifacts** (plans/diffs/screenshots/recordings) instead of reading raw logs

---

## Contents

### Workflows (`.agent/antigravity/workflows/`)

Command-like task recipes for common professional tasks:

1. **`draft-pr.md`** - Generate professional PR descriptions from git diffs
2. **`generate-project-docs.md`** - Create/refresh README.md from repo structure
3. **`optimize-code.md`** - Refactor & optimize with benchmarks
4. **`dockerize-app.md`** - Containerize application with multi-stage builds
5. **`seed-database.md`** - Create deterministic seed scripts

### Skills (`.agent/antigravity/skills/`)

Specialized capabilities with safety rails:

1. **`incident-triage/`** - Production issues → root cause → fix → evidence
2. **`safe-migration/`** - DB schema changes with idempotence & rollback

---

## Usage

### Workflows

Workflows are invoked naturally:

- "Draft a PR description for my changes"
- "Generate project documentation"
- "Optimize this code with benchmarks"
- "Dockerize this application"
- "Create a database seed script"

### Skills

Skills activate automatically based on context:

- "This endpoint is failing in production" → `incident-triage`
- "Add a new column to users table" → `safe-migration`

---

## Verification Principle

All workflows and skills produce **artifacts** for verification:

- ✅ Plans (before making changes)
- ✅ Diffs (what changed)
- ✅ Test results (proof it works)
- ✅ Screenshots/recordings (for UI changes)
- ✅ Benchmarks (for performance work)

**Never trust claims without artifacts.**

---

## Integration with Existing Skills

This pack complements your existing skills:

- `code-review` - Pre-merge verification
- `oca-development-standards` - Odoo best practices
- `odoo-ci-optimization` - CI/CD patterns

Use together for complete development lifecycle coverage.

---

## Extending the Pack

To add new workflows:

```bash
cat > .agent/antigravity/workflows/my-workflow.md <<'MD'
Workflow Name

Goal: What this workflow accomplishes

Steps:
1) First step
2) Second step
3) Output artifacts

Output: What gets produced
MD
```

To add new skills:

```bash
mkdir -p .agent/antigravity/skills/my-skill
cat > .agent/antigravity/skills/my-skill/SKILL.md <<'MD'
---
name: my-skill
description: When to activate this skill
---

# Skill Name

## Goal
What this skill does

## Process
How it works

## Output format
What it produces
MD
```

---

## References

- [Antigravity Developer Blog](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)
- [Antigravity Tutorial](https://medium.com/google-cloud/tutorial-getting-started-with-google-antigravity-b5cc74c103c2)
