# Runbook: AGENT.VERIFY_CI_FAIL

**Severity**: High
**HTTP Status**: 200 (run recorded, not errored)
**Retryable**: Yes (up to 2 times)

## Symptoms

The VERIFY phase completed but the CI check suite did not pass within the
configured wait window (default 10 minutes per attempt).

```json
{
  "run_id": "<uuid>",
  "status": "failed",
  "output": {
    "failure_mode": "AGENT.VERIFY_CI_FAIL",
    "pr_url": "https://github.com/Insightpulseai/odoo/pull/XXX",
    "checks_failed": ["typecheck", "lint"]
  }
}
```

## Remediation

```bash
# 1. Check PR CI results
gh pr checks <pr_number> --repo Insightpulseai/odoo

# 2. Get the failing job logs
gh run view <run_id> --log-failed --repo Insightpulseai/odoo

# 3a. If typecheck/lint: the agent made a syntax error — close the PR,
#     re-invoke pulser-patch with additional context about the error
# 3b. If flaky test: re-run the workflow once
gh run rerun <run_id> --failed --repo Insightpulseai/odoo

# 4. If CI passes on re-run, update ops.runs status
UPDATE ops.runs SET status = 'completed', output = output || '{"ci_retry": true}'
WHERE id = '<run_id>';
```

## Prevention

- Agent PATCH phase should run `pnpm typecheck` locally (in sandbox) before
  creating the PR.
- The benchmark `ci_pass_rate` metric penalises runs requiring CI re-runs.
