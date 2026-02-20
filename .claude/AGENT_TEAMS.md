# Agent Teams - Deterministic Execution Model

> **Status**: Enabled via `.claude/settings.json` (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
> **Mode**: `in-process` (all teammates in same session, shared context)
> **Last Updated**: 2026-02-20

---

## Core Principle

**"Lead agent + specialist teammates + shared task list"** - parallelize by independent lenses, synthesize at checkpoints.

Agent teams are **workflow automation**, not code generation. Use when:
- Work naturally splits by **domain** (not by file count)
- Tasks have **clear boundaries** (porting, CI, schema, runtime)
- **Plan approval required** for risky operations (see `RISKY_OPERATIONS.md`)

Do NOT use for:
- Single-domain work (just execute directly)
- Exploratory/discovery work (too much context switching)
- Rapid iteration (overhead > benefit)

---

## Team Topology

### Release Captain (Lead Agent)
**Role**: Only agent allowed to merge, finalize diffs, create PRs
**Permissions**: Full write access, git push, gh pr create
**Responsibilities**:
- Review teammate plans before approval
- Synthesize changes across domains
- Final verification and merge

### Specialist Teammates

#### 1. OCA Porter
**Domain**: `addons/oca/**` porting hygiene, manifest correctness
**Triggers**:
- OCA module porting (18.0→19.0, etc.)
- Manifest version bumps
- `__manifest__.py` changes
- Pre-commit hook compliance

**Guardrails**:
- Must request plan approval for multi-module ports
- Cannot modify non-OCA addons
- Must verify Python syntax before commit

**Allowed Tools**:
- Read, Edit, Grep, Glob
- `Bash(git *)` (status, diff, add, commit)
- `Bash(python3 -m py_compile*)`
- `Bash(black *)`, `Bash(isort *)`, `Bash(flake8*)`

**Blocked Tools**:
- `Bash(git push*)` (only Release Captain)
- Write (prefer Edit for manifest bumps)

#### 2. CI Gatekeeper
**Domain**: `.github/workflows/**`, spec kit hygiene, drift checks
**Triggers**:
- Workflow YAML changes
- Spec bundle updates (`spec/**/`)
- Gate/validation script changes (`scripts/ci/*`)
- Pre-commit config changes

**Guardrails**:
- Must request plan approval for gate logic changes
- Cannot modify workflows that run on `push` to main without approval
- Must validate YAML syntax before commit

**Allowed Tools**:
- Read, Edit, Grep, Glob
- `Bash(git *)` (status, diff, add, commit)
- `Bash(./scripts/spec_validate.sh)`
- `Bash(./scripts/ci_local.sh*)`

**Blocked Tools**:
- `Bash(git push*)` (only Release Captain)

#### 3. Platform SSOT (Supabase)
**Domain**: `supabase/**`, ops tables, RLS policies, edge functions
**Triggers**:
- Migration files (`supabase/migrations/*.sql`)
- RLS policy changes
- Edge function changes (`supabase/functions/`)
- Ops/monitoring tables (`ops.*`)

**Guardrails**:
- **CRITICAL**: Must request plan approval for ALL schema/RLS changes
- Cannot modify migration files that already ran (only add new)
- Must include rollback SQL in plan

**Allowed Tools**:
- Read, Edit, Grep, Glob
- `Bash(git *)` (status, diff, add, commit)
- `Bash(./scripts/verify.sh)` (schema validation)

**Blocked Tools**:
- `Bash(git push*)` (only Release Captain)
- Direct DB execution (migrations only)

#### 4. Runtime Engineer
**Domain**: Dev/stage/prod runtime contracts, scripts, Docker, DevContainer
**Triggers**:
- `.devcontainer/**` changes
- `docker-compose*.yml` changes
- `config/**` environment configs
- Runtime scripts (`scripts/odoo_*.sh`)

**Guardrails**:
- Must request plan approval for Docker/compose changes
- Cannot modify prod configs without explicit permission
- Must verify local dev environment still works

**Allowed Tools**:
- Read, Edit, Grep, Glob
- `Bash(git *)` (status, diff, add, commit)
- `Bash(docker exec *)` (local verification)
- `Bash(./scripts/repo_health.sh)`

**Blocked Tools**:
- `Bash(git push*)` (only Release Captain)
- Direct prod deployment commands

---

## Execution Pattern

### 1. Team Spawn
```text
You are the TEAM LEAD. Create an agent team and run in parallel.

Team to spawn:
1) "OCA Porter" — addons/oca porting hygiene
2) "CI Gatekeeper" — workflows and gates
3) "Platform SSOT" — Supabase patterns
4) "Runtime Engineer" — runtime contracts

Task: [specific goal]

Rules:
- Each teammate produces PLAN first (no edits)
- Lead approves only complete plans (file list, diffs, checklist)
- After approval, implement and report
- Lead synthesizes and creates PR
```

### 2. Plan Phase (Read-Only)
Each teammate:
1. Read assigned domain files
2. Produce plan with:
   - **Files to change** (specific paths)
   - **Exact diffs** (before/after snippets)
   - **Verification checklist** (how to test)
   - **Rollback strategy** (if risky)
3. Request approval from lead

### 3. Approval Gate
Lead reviews ALL plans before ANY edits:
- ✅ Scope is minimal (only necessary changes)
- ✅ No unrelated files included
- ✅ Diffs are precise (no reformatting noise)
- ✅ Verification is deterministic (no "should work")
- ✅ Rollback is documented (if risky)

**Risky operations** (see `RISKY_OPERATIONS.md`):
- Schema/migration changes
- RLS policy modifications
- CI gate logic changes
- Production config changes
- Multi-module OCA ports

### 4. Implementation Phase
After lead approval:
1. Teammates execute approved plans
2. Run verification checklists
3. Report completion with evidence

### 5. Synthesis & Cleanup
Lead:
1. Review all teammate outputs
2. Check `git diff` scope (no accidental files)
3. Finalize commit messages
4. Create PR
5. Shut down team

---

## Team Lifecycle

### When to Enable Team
- Clear domain boundaries (4+ specialists needed)
- Work parallelizes naturally (no blocking dependencies)
- Risky operations requiring plan approval

### When to Disable Team
- Single-domain work (just execute)
- Rapid iteration needed (overhead too high)
- Exploratory work (too much context switching)

### Cleanup Checklist
- [ ] All teammates completed their tasks
- [ ] `git diff` scope matches expected changes
- [ ] No accidental files staged
- [ ] Team shut down (no orphaned processes)

---

## Token Budget

**Per teammate**: ~4-8K tokens (plan + implementation)
**Lead overhead**: ~2-4K tokens (coordination + synthesis)
**Total for 4-teammate team**: ~20-40K tokens

Use teams when **parallelism benefit > token overhead**.

---

## Examples

### ✅ Good Team Use Cases
- Systematic OCA porting (15 modules, 4 repos)
- Multi-domain release prep (OCA + CI + Supabase + Docker)
- Large refactor (schema + RLS + edge functions + CI)

### ❌ Bad Team Use Cases
- Single manifest version bump (just edit directly)
- Bug fix in one file (no parallelism)
- Documentation updates (no risky operations)

---

## References

- [Claude Code Agent Teams Docs](https://code.claude.com/docs/en/agent-teams)
- `.claude/settings.json` - Team configuration
- `.claude/RISKY_OPERATIONS.md` - Plan approval requirements
