# Runbook: CI.SKILLS_REGISTRY_INVALID

**Severity**: Critical
**HTTP Status**: n/a (CI failure)
**Retryable**: No (fix YAML, then re-push)

## Symptoms

`scripts/ci/validate_skills_registry.py` fails on PR CI.

```
ERROR: ssot/agents/skills.yaml schema validation failed
  skill[1].max_duration_s: must be integer
  skill[2].state_machine[0]: 'PLANN' is not one of ['PLAN', 'PATCH', 'VERIFY', 'PR']
```

## Root Causes

1. A new skill was added with a typo or missing required field.
2. The `status` field uses a value not in the allowed enum.
3. The `executor` field has an invalid value.
4. The `state_machine` contains an invalid state name.

## Remediation

```bash
# 1. Run the validator locally
python3 scripts/ci/validate_skills_registry.py

# 2. Fix the reported errors in ssot/agents/skills.yaml
# Required fields: id, name, description, executor, max_duration_s, tags,
#                  state_machine, owner, status
# executor must be: vercel_sandbox | do_runner
# status must be: active | deprecated | experimental
# state_machine values must be: PLAN | PATCH | VERIFY | PR

# 3. Re-run the validator until clean
python3 scripts/ci/validate_skills_registry.py && echo "PASS"

# 4. Push the fix
git add ssot/agents/skills.yaml
git commit -m "fix(ssot): correct skills registry schema errors"
git push
```

## Prevention

Run `python3 scripts/ci/validate_skills_registry.py` as a pre-commit hook:
```bash
echo "python3 scripts/ci/validate_skills_registry.py" >> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
