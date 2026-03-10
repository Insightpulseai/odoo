# Runbook: AGENT.PATCH_DIFF_TOO_LARGE

**Severity**: High
**HTTP Status**: 422
**Retryable**: No

## Symptoms

The PATCH phase generated a diff exceeding the 500-line limit.

```json
{
  "error": "AGENT.PATCH_DIFF_TOO_LARGE",
  "changed_lines": 847,
  "limit": 500
}
```

## Root Causes

1. The issue scope is too broad (e.g., "refactor entire auth module").
2. Auto-generated code (migrations, lock files) was included in the diff.
3. The agent is fixing multiple unrelated issues in one run.

## Remediation

```bash
# 1. Inspect what the agent tried to change
SELECT output FROM ops.runs WHERE id = '<run_id>';

# 2. Break the task into smaller issues
# Each pulser-patch run should touch ≤ 3 files ideally

# 3. Add .gitignore-style exclusions to the skill config if lock files
#    are the culprit (pnpm-lock.yaml, etc.)
# Edit ssot/agents/skills.yaml — add diff_exclude_patterns field

# 4. Re-open the original issue with scope-limited sub-tasks
```

## Prevention

- Split large refactoring issues into ≤ 50-line focused tasks.
- The benchmark `diff_minimality` metric penalises large diffs.
- CI gate blocks diffs > 500 lines (configurable per skill).
