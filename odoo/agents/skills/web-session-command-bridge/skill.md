# Skill: Web Session Command Bridge

> Repo-enforced capability ensuring every change request produces execution-ready commands.

## Purpose

Ensure every change request produces execution-ready commands that work in:
- Claude Code Web session VM
- CI runner (GitHub Actions)
- Local CLI (optional parity)

## Hard Rules

1. **Always output copy-pasteable commands** for apply / test / deploy / validate
2. **Prefer repo-local scripts** in `./scripts/` over raw ad-hoc commands
3. **Never require UI clicks** - all operations must be CLI/API driven
4. **If Docker is available**, provide `docker compose` equivalents
5. **If Docker is NOT available**, provide "no-docker" fallbacks using node/python CLIs
6. **Commands must be idempotent** where possible

## Required Outputs (for non-trivial tasks)

Every significant change must include these sections:

```
### 1) APPLY COMMANDS
<git add/commit commands or script invocations>

### 2) TEST / VERIFY COMMANDS
<test commands that prove the change works>

### 3) DEPLOY / MIGRATE COMMANDS
<deployment or migration commands if applicable>

### 4) VALIDATION COMMANDS
<commands that verify the deployment succeeded>

### 5) ROLLBACK COMMANDS
<commands to undo the change if needed>
```

## Environment Detection

The skill should detect and adapt to the execution environment:

| Environment | Detection | Behavior |
|-------------|-----------|----------|
| Claude Code Web | `$CLAUDE_PROJECT_DIR` set | Use web-safe commands, no Docker assumed |
| CI Runner | `$CI` set | Use CI-optimized paths, full tooling available |
| Local CLI | Neither set | Full access, Docker optional |

## Command Macros (Repo Standard)

These are the canonical scripts that should be referenced:

| Script | Purpose |
|--------|---------|
| `./scripts/ci/run_all.sh` | Unified CI reproduction (all gates) |
| `./scripts/docs_refresh.sh` | Regenerate documentation artifacts |
| `./scripts/repo_health.sh` | Repository structure validation |
| `./scripts/spec_validate.sh` | Spec bundle validation |
| `./scripts/skill_web_session_bridge.sh` | Print environment-aware command template |

## Output Format Template

```text
## Outcome
<1-3 lines describing what was done>

## Evidence
<bullet list of files + paths>

## Verification Results
<bullet list of pass/fail checks>

## Changes Shipped
<bullet list or table of changes>

---

### APPLY
```bash
<commands>
```

### TEST / VERIFY
```bash
<commands>
```

### DEPLOY / MIGRATE
```bash
<commands>
```

### VALIDATE
```bash
<commands>
```

### ROLLBACK
```bash
<commands>
```
```

## Docker Parity Rules

When Docker is available:

```bash
# Prefer compose commands
docker compose up -d
docker compose exec <service> <command>
docker compose logs -f <service>

# For Odoo specifically
docker compose exec odoo-core odoo -d odoo_core -u <module> --stop-after-init
```

When Docker is NOT available:

```bash
# Use direct CLI tools
pnpm install && pnpm run build
python3 -m pip install -r requirements.txt
./scripts/ci/run_all.sh
```

## Banned Behaviors

- No "here's a guide" or "follow these steps" prose
- No UI click instructions
- No time estimates
- No questions before proceeding (act, then report)
- No placeholder values in commands

## Integration with CLAUDE.md

This skill is referenced from `CLAUDE.md` and enforced via CI workflow `skill-enforce.yml`.

---

*Skill Version: 1.0.0*
*Last Updated: 2026-01-24*
