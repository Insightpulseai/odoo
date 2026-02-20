# Risky Operations - Plan Approval Required

> **Contract**: For operations in this list, teammates MUST produce a plan and request lead approval BEFORE making ANY changes.
> **Rationale**: These operations can cause data loss, security breaches, or break production systems.
> **Last Updated**: 2026-02-20

---

## Critical Risk Categories

### 🔴 ALWAYS Require Plan Approval

#### 1. Schema & Migration Changes
**Scope**: `supabase/migrations/*.sql`, database schema modifications
**Risk**: Data loss, breaking changes, irreversible migrations

**Plan Must Include**:
- Full SQL diff (before/after schema)
- Rollback migration SQL
- Data migration strategy (if applicable)
- Verification query to confirm schema state

**Examples**:
```sql
-- ❌ NEVER without approval
ALTER TABLE users DROP COLUMN email;
ALTER TABLE orders ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ✅ Requires explicit plan
-- Migration: 20260220_add_audit_columns.sql
ALTER TABLE orders ADD COLUMN created_by uuid REFERENCES auth.users(id);
ALTER TABLE orders ADD COLUMN updated_at timestamptz DEFAULT now();

-- Rollback: 20260220_add_audit_columns_rollback.sql
ALTER TABLE orders DROP COLUMN created_by;
ALTER TABLE orders DROP COLUMN updated_at;
```

#### 2. RLS Policy Changes
**Scope**: Row-Level Security policies in Supabase
**Risk**: Security breaches, data leaks, unauthorized access

**Plan Must Include**:
- Policy name and table
- Full policy SQL (before/after)
- Security test cases (who should/shouldn't have access)
- Verification queries

**Examples**:
```sql
-- ❌ NEVER without approval
DROP POLICY "users_select_policy" ON users;
ALTER POLICY "orders_select" ON orders USING (true); -- Public access!

-- ✅ Requires explicit plan
CREATE POLICY "users_own_data" ON users
  FOR SELECT USING (auth.uid() = id);

-- Test cases:
-- 1. User A can see only their own data
-- 2. User B cannot see User A's data
-- 3. Service role can see all data
```

#### 3. CI Gate Logic Changes
**Scope**: `.github/workflows/**` that run on `push` or `pull_request`
**Risk**: Break CI/CD, block deployments, bypass quality gates

**Plan Must Include**:
- Workflow file path
- Exact YAML diff
- Reason for gate change
- Local test showing gate works

**Examples**:
```yaml
# ❌ NEVER without approval (weakens gate)
- name: Run tests
  run: npm test || true  # Ignores failures!

# ✅ Requires explicit plan
- name: Run tests
  run: npm test
  continue-on-error: false
```

#### 4. Production Config Changes
**Scope**: `config/prod/**`, production environment variables
**Risk**: Break production, expose secrets, downtime

**Plan Must Include**:
- Config file path
- Full diff (redact secrets)
- Deployment plan (blue/green, canary, etc.)
- Rollback procedure

**Examples**:
```bash
# ❌ NEVER without approval
DATABASE_URL=postgresql://localhost/test  # Wrong environment!

# ✅ Requires explicit plan
# Change: config/prod/odoo.conf
# Before: workers = 4
# After: workers = 8
# Reason: Handle increased load after marketing campaign
# Rollback: Set workers = 4, restart service
```

#### 5. Multi-Module OCA Ports
**Scope**: `addons/oca/**` when porting >5 modules at once
**Risk**: Break dependencies, version conflicts, mass regression

**Plan Must Include**:
- List of modules to port (with dependencies)
- Porting order (resolve deps first)
- Verification plan (install all, check deps)
- Rollback strategy (git revert hash)

**Examples**:
```bash
# ❌ NEVER without approval (breaks deps)
oca-port 18.0 19.0 purchase_tier_validation  # Depends on base_tier_validation!

# ✅ Requires explicit plan
# Port order:
# 1. base_tier_validation (no deps)
# 2. purchase_tier_validation (depends on #1)
# 3. sale_tier_validation (depends on #1)
# Verification: Install all 3, check odoo -i purchase_tier_validation
```

---

## 🟡 Moderate Risk - Approval Recommended

#### 6. Edge Function Deployment
**Scope**: `supabase/functions/**`
**Risk**: Runtime errors, API breakage, performance issues

**Plan Should Include**:
- Function name and trigger
- Code diff
- Test invocation (curl command)
- Performance expectations

#### 7. Pre-commit Hook Changes
**Scope**: `.pre-commit-config.yaml`
**Risk**: Block all commits, slow down development

**Plan Should Include**:
- Hook diff
- Local test (run on sample file)
- Escape hatch (if hook fails)

#### 8. Docker/DevContainer Changes
**Scope**: `.devcontainer/**`, `docker-compose*.yml`
**Risk**: Break local dev, dependency conflicts

**Plan Should Include**:
- Dockerfile/compose diff
- Local rebuild test
- Dependency version justification

---

## 🟢 Low Risk - Approval Optional

#### 9. Documentation Updates
**Scope**: `*.md`, `docs/**` (non-runbook)
**Risk**: Minimal (typos, outdated info)

**Approval Optional**: Lead can approve inline or delegate.

#### 10. Single-Module Manifest Bumps
**Scope**: `addons/oca/*/__manifest__.py` (single module)
**Risk**: Low (version mismatch worst case)

**Approval Optional**: If only changing version number and no deps.

#### 11. Test-Only Changes
**Scope**: `**/tests/**`, test fixtures
**Risk**: Low (tests don't affect production)

**Approval Optional**: If no production code touched.

---

## Plan Approval Template

When requesting approval, teammates MUST use this format:

```markdown
## Plan Approval Request

**Teammate**: [OCA Porter | CI Gatekeeper | Platform SSOT | Runtime Engineer]
**Risk Category**: [Critical | Moderate | Low]
**Operation**: [Brief description]

### Files to Change
- path/to/file1.py
- path/to/file2.sql

### Exact Diffs
\`\`\`diff
--- a/path/to/file1.py
+++ b/path/to/file1.py
@@ -10,3 +10,3 @@
-    version = "18.0.1.0.0"
+    version = "19.0.1.0.0"
\`\`\`

### Verification Checklist
- [ ] Python syntax: `python3 -m py_compile path/to/file1.py`
- [ ] Manifest version: `grep version path/to/__manifest__.py`
- [ ] No unrelated files: `git diff --name-only`

### Rollback Strategy
- Revert commit: `git revert <hash>`
- Or manual: Change version back to 18.0.1.0.0

**Approval Requested**: YES | NO
```

---

## Lead Approval Checklist

Before approving ANY risky operation, verify:

- [ ] **Scope is minimal** (only necessary changes)
- [ ] **Diffs are precise** (no formatting noise)
- [ ] **Verification is deterministic** (commands, not "should work")
- [ ] **Rollback is documented** (for critical risk)
- [ ] **Dependencies are resolved** (correct order)
- [ ] **Tests exist** (or test plan documented)

**If ANY checkbox fails**: Request plan revision before approval.

---

## Escalation Path

If teammate disagrees with approval requirement:
1. Teammate explains why operation is low-risk
2. Lead evaluates with fresh perspective
3. If still risky: Require plan (lead has final say)
4. If genuinely low-risk: Update this document

**This document is living** - add/remove operations as patterns emerge.

---

## Emergency Override

In TRUE emergencies (production down, data loss imminent):
- Lead can bypass plan approval
- MUST document in commit message: `EMERGENCY: [reason]`
- MUST create post-mortem in `docs/postmortem/YYYYMMDD-incident.md`

**Emergency criteria**:
- Production system down
- Active data loss
- Security breach in progress

NOT emergencies:
- "Need this feature by EOD"
- "Client is waiting"
- "I already started coding"

---

## References

- `.claude/AGENT_TEAMS.md` - Team topology and execution model
- `.claude/settings.json` - Team configuration
- [OCA Porting Runbook](../docs/oca/PORTING_19_RUNBOOK.md)
- [Spec Kit Playbook](../spec/README.md)
