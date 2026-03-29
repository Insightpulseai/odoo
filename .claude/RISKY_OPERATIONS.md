# Risky Operations - Plan Approval Required

> **Contract**: For operations in this list, teammates MUST produce a plan and request lead approval BEFORE making ANY changes.
> **Rationale**: These operations can cause data loss, security breaches, or break production systems.
> **Last Updated**: 2026-03-30

---

## Critical Risk Categories

### 🔴 ALWAYS Require Plan Approval

#### 1. Schema & Migration Changes
**Scope**: Odoo model changes, PostgreSQL migrations, database schema modifications
**Risk**: Data loss, breaking changes, irreversible migrations

**Plan Must Include**:
- Full SQL diff (before/after schema)
- Rollback migration SQL
- Data migration strategy (if applicable)
- Verification query to confirm schema state

**Examples**:
```sql
-- ❌ NEVER without approval
ALTER TABLE res_partner DROP COLUMN email;
ALTER TABLE sale_order ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES res_users(id) ON DELETE CASCADE;

-- ✅ Requires explicit plan
-- Odoo module migration: pre-migrate or post-migrate script
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS approved_by integer REFERENCES res_users(id);
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now();

-- Rollback: revert module version and run downgrade
ALTER TABLE sale_order DROP COLUMN IF EXISTS approved_by;
ALTER TABLE sale_order DROP COLUMN IF EXISTS updated_at;
```

#### 2. Access Control & Security Policy Changes
**Scope**: `ir.model.access.csv`, `ir.rule` record rules, Entra ID / OAuth config
**Risk**: Security breaches, data leaks, unauthorized access

**Plan Must Include**:
- ACL or record rule name and model
- Full before/after diff
- Security test cases (who should/shouldn't have access)
- Verification steps

**Examples**:
```xml
<!-- ❌ NEVER without approval -->
<record id="sale_order_rule_all" model="ir.rule">
  <field name="domain_force">[(1, '=', 1)]</field> <!-- Public access! -->
</record>

<!-- ✅ Requires explicit plan -->
<record id="sale_order_rule_company" model="ir.rule">
  <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
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

#### 6. Azure Infrastructure Changes
**Scope**: `infra/azure/**`, Bicep/ARM templates, Container App config
**Risk**: Runtime errors, service disruption, cost impact

**Plan Should Include**:
- Resource name and type
- Template diff
- Validation (`az deployment group what-if`)
- Rollback procedure

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

**Teammate**: [OCA Porter | CI Gatekeeper | Azure Platform | Runtime Engineer]
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
