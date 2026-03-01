# CI Automation: Project Board Add Failed

**Failure code**: `CI.AUTOMATION.PROJECT_BOARD_FAILED`
**Severity**: low
**CI behavior**: non-blocking (must not block merges)
**SSOT**: `ssot/errors/failure_modes.yaml`

---

## What it means

The `add-to-project` or `project-automation` workflow failed to add an issue or PR
to the GitHub project board (jgtolentino/projects/4). The issue or PR is still
open and mergeable. This failure only affects project tracking visibility.

---

## Likely causes

1. **Wrong project board ID**: `PROJECT_URL` in the workflow references an old or
   incorrect project number (currently `projects/4`). If the project was recreated,
   this ID is stale.

2. **TOKEN scope missing**: `secrets.PROJECT_TOKEN` does not have the `project` scope.
   Classic PATs need `project` checked. Fine-grained PATs need project read/write.

3. **Org permission change**: The token owner lost access to the project after an
   org permission change or team change.

---

## Deterministic fix

### Step 1 — Identify which workflow failed

```bash
# Check which workflow triggered the failure
gh run list --repo Insightpulseai/odoo --workflow="Add to Project" --limit 5
gh run list --repo Insightpulseai/odoo --workflow="Project Automation" --limit 5
```

### Step 2 — Verify the project still exists and get its current ID

```bash
# List projects for the user — confirm project number 4 still exists
gh api graphql -f query='
  query {
    user(login: "jgtolentino") {
      projectsV2(first: 10) {
        nodes { number title id }
      }
    }
  }' --jq '.data.user.projectsV2.nodes[] | "\(.number): \(.title)"'
```

If project number 4 no longer exists, update `PROJECT_URL` in:
- `.github/workflows/add-to-project.yml`
- `.github/workflows/project-automation.yml`

### Step 3 — Verify token scope

```bash
# Check token permissions (requires the token itself — do not paste here)
# Ask the token owner to verify 'project' scope is checked in GitHub Settings
# → Settings → Developer settings → Personal access tokens → [token] → Edit
```

If the scope is missing: rotate a new PAT with `project` scope and update
`secrets.PROJECT_TOKEN` in GitHub repo settings (Settings → Secrets → Actions).

### Step 4 — Confirm the fix works

Re-run the failed workflow:
```bash
gh run rerun <run-id> --repo Insightpulseai/odoo
```

---

## Prevention

Both workflow files already have `continue-on-error: true` on the project board
step (added in feat/failure-modes-convergence-observability). This ensures the
failure does not propagate to PR merge gates.

If project board automation is irreparably broken, disable it:
```yaml
# In the workflow job step:
if: false   # disable until PROJECT_TOKEN is rotated
```

---

## Related files

- `.github/workflows/add-to-project.yml`
- `.github/workflows/project-automation.yml`
- `ssot/errors/failure_modes.yaml` (entry: `CI.AUTOMATION.PROJECT_BOARD_FAILED`)
