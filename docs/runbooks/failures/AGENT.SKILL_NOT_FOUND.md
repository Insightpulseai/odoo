# Runbook: AGENT.SKILL_NOT_FOUND

**Severity**: Critical
**HTTP Status**: 422
**Retryable**: No

## Symptoms

An Edge Function (or agent runtime) received a `skill_id` that does not
exist in `ops.skills`.  The run is rejected immediately.

```
{
  "error": "AGENT.SKILL_NOT_FOUND",
  "skill_id": "<value>",
  "message": "No skill with id '<value>' in ops.skills"
}
```

## Root Causes

1. `ssot/agents/skills.yaml` was not synced to `ops.skills` after a new skill was added.
2. A typo in the `skill_id` field of the agent caller.
3. The `skills-sync` GitHub Action failed silently on the last merge.

## Remediation

```bash
# 1. Verify the skill exists in YAML
grep "id:" ssot/agents/skills.yaml

# 2. Check if it's in the database
# (via Supabase dashboard or psql)
SELECT id FROM ops.skills WHERE id = '<skill_id>';

# 3. If missing from DB, trigger the sync action manually
gh workflow run skills-sync.yml --repo Insightpulseai/odoo

# 4. If missing from YAML, add the skill entry and open a PR
# spec/deerflow-patterns-adoption/prd.md describes the YAML schema

# 5. If typo in caller, fix the skill_id reference and redeploy
```

## Prevention

CI gate `scripts/ci/validate_skills_registry.py` blocks PRs that reference
undeclared skill IDs.  Ensure all agent code uses constants from the YAML.
