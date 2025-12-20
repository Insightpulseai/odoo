# CLAUDE.md — Odoo CE Project

## Quick Reference

**Stack**: Odoo CE 18.0 (OCA) + n8n + Mattermost + PostgreSQL 15

**Supabase Project**: `spdtwktxdalcfigzeqrz` (external integrations only)

**Common Commands**:
```bash
docker compose up -d              # Start stack
./scripts/deploy-odoo-modules.sh  # Deploy module
./scripts/ci/run_odoo_tests.sh    # Run tests
```

## Agent Workflow (Mandatory)

All changes must follow this pattern:

```
explore → plan → implement → verify → commit
```

### Role Commands
- `/project:plan` — Create a detailed plan before implementation
- `/project:implement` — Execute the plan with minimal changes
- `/project:verify` — Run all verification checks
- `/project:ship` — Orchestrate full workflow end-to-end
- `/project:fix-github-issue` — Fix a specific GitHub issue

### Verification Sequence
Always run before committing:
```bash
./scripts/repo_health.sh       # Check repo structure
./scripts/spec_validate.sh     # Validate spec bundles
./scripts/ci_local.sh          # Run local CI checks
```

### Rules
1. Never guess: read files first, then change them
2. Prefer the simplest implementation that solves the task
3. Always include verification after any mutation
4. Keep diffs minimal and reviewable
5. Update docs and tests with code changes

## External Memory (Just-in-Time Retrieval)

Detailed config stored in SQLite for reduced context usage:

```bash
python .claude/query_memory.py config       # Supabase/DB config
python .claude/query_memory.py arch         # Architecture components
python .claude/query_memory.py commands     # All commands
python .claude/query_memory.py rules        # Project rules
python .claude/query_memory.py deprecated   # Deprecated items
python .claude/query_memory.py all          # Everything
```

## Critical Rules

1. **Secrets**: Use `.env` files, never hardcode (see `.env.example`)
2. **Database**: Odoo uses local PostgreSQL (`db`), NOT Supabase
3. **Supabase**: Only for n8n workflows, task bus, external integrations
4. **Deprecated**: Never use `xkxyvboeubffxxbebsll` or `ublqmilcjtpnflofprkr`
5. **Specs**: All significant changes must reference a spec bundle
6. **Safety**: Only use allow-listed tools (see `.claude/settings.json`)

## Architecture

```
Mattermost <-> n8n <-> Odoo <-> PostgreSQL (local)
                |
                v
            Supabase (external integrations)
```

## Spec Kit Structure

All significant features must have a spec bundle:

```
spec/
└─ <feature-slug>/
   ├─ constitution.md   # Non-negotiable rules
   ├─ prd.md            # Product requirements
   ├─ plan.md           # Implementation plan
   └─ tasks.md          # Task checklist
```

See `spec/pulser-master-control/` for reference.

## Monorepo Structure

```
apps/               # Applications (pulser-runner, web)
packages/           # Shared packages (github-app, agent-core)
addons/             # Odoo modules
spec/               # Spec bundles
scripts/            # Automation scripts
supabase/           # Database migrations
```

## PR Discipline

- Small commits, descriptive messages
- Follow conventional commits: `feat|fix|refactor|docs|test|chore(scope): description`
- If relevant: add/update docs + tests with code changes
- Never push directly to main without verification

---
*Query `.claude/project_memory.db` for detailed configuration*
