# Agent Operating Contract (SSOT)

> Canonical rules for all AI agents operating in this repository.

## Core Principles

1. **Follow repo skills** under `/skills/*` - these are enforced capabilities
2. **No UI steps** - all operations must be CLI/API driven
3. **Commands must be copy-pasteable** - no placeholders or prose instructions
4. **Execute, don't explain** - act first, report results
5. **Evidence-based** - all claims must have verifiable proof

## Canonical Workflow

1. Read Spec Kit (`spec/<slug>/*`) + `spec/platforms/*`
2. Implement scripts + config deterministically
3. Add tests + drift checks
4. Update runbooks in `docs/runbooks/`
5. CI must reproduce locally with `./scripts/ci/run_all.sh`

## Enabled Skills

| Skill | Contract | Purpose |
|-------|----------|---------|
| Web Session Command Bridge | [skills/web-session-command-bridge/skill.md](skills/web-session-command-bridge/skill.md) | CLI-ready commands for all environments |

## Output Requirements

Every significant change must include:

```
### APPLY
<commands to apply the change>

### TEST / VERIFY
<commands to verify the change works>

### DEPLOY / MIGRATE
<commands to deploy if applicable>

### VALIDATE
<commands to validate deployment>

### ROLLBACK
<commands to undo if needed>
```

## Required Outputs for Platform Changes

- Apply commands
- Test/verify commands
- Deploy/rollback commands
- Production validation commands

## Where to Write Things

- Specs: `spec/`
- Runbooks: `docs/runbooks/`
- Scripts: `scripts/`
- Workflows: `.github/workflows/`

## Environment Awareness

Agents must detect and adapt to the execution environment:

| Variable | Environment | Behavior |
|----------|-------------|----------|
| `CLAUDE_PROJECT_DIR` | Claude Code Web | Web-safe commands, no Docker assumed |
| `CI` | GitHub Actions | CI-optimized paths |
| Neither | Local CLI | Full access, Docker optional |

## Canonical Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/ci/run_all.sh` | Unified CI reproduction |
| `./scripts/docs_refresh.sh` | Regenerate documentation |
| `./scripts/repo_health.sh` | Repository structure validation |
| `./scripts/spec_validate.sh` | Spec bundle validation |
| `./scripts/skill_web_session_bridge.sh` | Print environment-aware commands |

## Banned Behaviors

- No "here's a guide" prose
- No UI click instructions
- No time estimates
- No questions before proceeding
- No placeholder values in commands
- No claiming completion without evidence

## Verification

All changes must pass:
```bash
./scripts/ci/run_all.sh
git diff --exit-code
```

---

*See individual skill contracts in `/skills/` for detailed requirements.*
