---
name: incident-triage
description: Use for production issues, failing deploys, CI red builds, error spikes, or "why is this broken" requests. Produce root cause + minimal fix + verification evidence.
---

# Incident Triage Skill

## Goal

Reduce Mean Time To Recovery (MTTR) by producing:

- A repro or clear failure signature
- The likely root cause
- A minimal fix
- Validation evidence (tests + logs)

## When to activate

Activate for:

- "This endpoint is failing in production"
- "CI build is broken"
- "Deploy failed"
- "Error spike in logs"
- "Why is this broken?"
- "Users reporting 500 errors"
- "Performance degradation"

Do NOT activate for:

- Feature requests
- General questions
- Code reviews (use `code-review` skill)

## Process

### 1. Capture Failure Signal

Gather evidence:

- **Stack trace**: Full error with line numbers
- **Log pattern**: Repeated error messages
- **Failing test name**: Exact test that's red
- **Endpoint**: URL + HTTP method + status code
- **Metrics**: Error rate, latency, throughput
- **Timeline**: When did it start? What changed?

### 2. Create Minimal Repro

Provide commands to reproduce:

```bash
# Example: API endpoint failure
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User"}'
# Expected: 201 Created
# Actual: 500 Internal Server Error
```

### 3. Identify Root Cause Candidates

Analyze potential causes:

**Common categories**:

- **Config**: Environment variables, feature flags, secrets
- **Migration**: Database schema out of sync
- **Auth**: Token expiration, permission changes
- **Performance**: Resource exhaustion, timeouts
- **Dependencies**: External API down, library version mismatch
- **Data**: Unexpected null values, constraint violations
- **Code**: Recent changes, edge cases

**For Odoo**:

- Module not installed/upgraded
- Record rules blocking access
- Computed field dependency cycle
- Missing `sudo()` for cross-company access
- Workflow state mismatch

### 4. Implement Smallest Safe Fix

Make minimal change to restore service:

- Fix the immediate bug
- Add guard clauses
- Update config
- Rollback problematic change

**Do NOT**:

- Refactor unrelated code
- Add new features
- Make "while we're here" changes

### 5. Verify Fix

Provide evidence:

**Tests**:

```bash
# Run affected tests
pytest tests/test_api.py::test_create_user -v
# PASSED

# Run full suite
pytest
# 47 passed, 0 failed
```

**Logs**:

```bash
# Before fix
grep "ERROR" logs/app.log | tail -5
# 2024-02-11 10:15:23 ERROR: KeyError: 'email'
# 2024-02-11 10:15:24 ERROR: KeyError: 'email'

# After fix
grep "ERROR" logs/app.log | tail -5
# (no errors)
```

**Smoke test**:

```bash
# Test endpoint
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'
# HTTP/1.1 201 Created
```

### 6. Output Artifacts

- **Plan**: Root cause analysis
- **Diffs**: What changed
- **Test results**: Proof it works
- **Screenshots/recordings**: For UI issues

## Output Format

### Summary

- What broke
- Blast radius (how many users affected)
- When it started
- Current status

### Root Cause Analysis

```markdown
## Root Cause

**Symptom**: POST /api/users returns 500 error

**Evidence**:

- Stack trace shows `KeyError: 'email'` at line 45
- Started after deploy at 2024-02-11 10:00
- Affects 100% of user creation requests

**Root Cause**:
Recent change made `email` field required but didn't update validation.
Request body without `email` crashes instead of returning 400 Bad Request.

**Fix**:
Add validation to check for required fields before processing.
```

### Findings

**[BLOCKER] Missing email validation**

- Evidence: `api/users.py:45`
  ```python
  user = User(
      name=data['name'],
      email=data['email']  # KeyError if missing
  )
  ```
- Impact: All user creation requests fail with 500
- Fix:

  ```python
  if 'email' not in data:
      return {'error': 'email is required'}, 400

  user = User(
      name=data['name'],
      email=data['email']
  )
  ```

- Verify: `pytest tests/test_api.py::test_create_user_missing_email`

### Patch

```diff
diff --git a/api/users.py b/api/users.py
index 1234567..abcdefg 100644
--- a/api/users.py
+++ b/api/users.py
@@ -42,6 +42,9 @@ def create_user():
     data = request.get_json()

+    if 'email' not in data:
+        return {'error': 'email is required'}, 400
+
     user = User(
         name=data['name'],
         email=data['email']
```

### Verification Commands

```bash
# Apply patch
git apply fix.patch

# Run tests
pytest tests/test_api.py -v

# Test missing email case
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User"}'
# Expected: 400 Bad Request with error message

# Test valid case
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'
# Expected: 201 Created

# Check logs
tail -f logs/app.log
# Should show no errors
```

### Rollback Strategy

```bash
# If fix causes issues, rollback:
git revert <commit-hash>
git push

# Or deploy previous version:
kubectl rollout undo deployment/api
```

## Verification

- [ ] Failure reproduced with exact commands
- [ ] Root cause identified with evidence
- [ ] Minimal fix applied
- [ ] Tests prove fix works
- [ ] Rollback strategy documented
- [ ] No "while we're here" changes
