# Verification — Codex Doctrine Prompt Update

## Deterministic Checks

1. `rg` section and policy-token checks passed against [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md).
2. `nl -ba` confirmed exact line placement for both appended doctrine blocks.
3. `git diff --stat` confirmed a single-file prompt change with append-only insertions.

## Command Results

### Section presence

- `46:## Codex runtime/config doctrine`
- `68:- Do not weaken \`approval_policy\` or \`sandbox_mode\` for the sake of deployment speed.`
- `75:- Respect \`shell_environment_policy\`.`
- `96:- Treat \`smart_approvals\` as experimental if present and do not rely on it as the sole safety mechanism for prod deployment.`
- `119:## Codex automations and worktree doctrine`
- `170:- Even if \`approval_policy = "never"\` is allowed, preserve human approval for destructive or high-risk production actions.`
- `199:- record whether it ran in local project mode or worktree mode`
- `207:The live production release must remain human-accountable.`

### Line-range inspection

- Runtime/config doctrine spans [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L46) through [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L117)
- Automations/worktree doctrine spans [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L119) through [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L208)

### Diff summary

- `agents/skills/odoo-staging-to-production-promotion/prompt.md | 164 insertions`
- No other prompt files were modified for this change.

## Verification Verdict

PASS
