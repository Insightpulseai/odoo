# Runbook: AGENT.PR_OPEN_FAILED

**Severity**: High
**HTTP Status**: 502
**Retryable**: Yes (after token / permission fix)

## Symptoms

The PR phase could not open a GitHub PR.

```json
{
  "error": "AGENT.PR_OPEN_FAILED",
  "github_status": 403,
  "message": "Resource not accessible by integration"
}
```

## Root Causes

1. `GH_TOKEN` / `GITHUB_TOKEN` has insufficient scopes (`repo:write` required).
2. Branch protection requires manual PR creation (can't push directly).
3. GitHub API rate limit exceeded.
4. The branch already has an open PR (duplicate prevention should catch this).

## Remediation

```bash
# 1. Check token scopes
gh auth status

# 2. If rate limited, wait and retry (limit resets every hour)
gh api rate_limit | jq '.resources.core'

# 3. Verify branch protection allows agent PRs
gh api repos/Insightpulseai/odoo/branches/main/protection

# 4. If duplicate PR: close the old one or merge it first
gh pr list --repo Insightpulseai/odoo --state open | grep <branch>

# 5. Manual fallback: push the branch and open the PR manually
git push origin <agent-branch>
gh pr create --title "..." --body "..." --base main
```

## Prevention

- Store `GH_TOKEN` in Vercel env with `repo:write, pull_requests:write` scopes.
- Run duplicate-PR check before PR phase (query open PRs for the branch).
