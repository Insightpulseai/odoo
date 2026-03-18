# Bugbot Mandatory Pre-Merge AI Review

**Status**: Phase 1 (Opt-In) - Week 1
**Version**: 1.0.0
**Last Updated**: 2026-02-12

---

## Overview

Bugbot is a mandatory AI-powered code review gate that analyzes all pull requests for logic errors, security vulnerabilities, and performance issues before merge. It provides high-signal, low-noise feedback focused on catching critical bugs early.

**Key Features**:
- **Automated invocation**: Runs on every PR with Python/JavaScript/XML changes
- **Odoo-specific patterns**: Detects N+1 queries, SQL injection, improper ORM usage
- **Severity-based blocking**: P0 issues block merge (Phase 3), P1/P2 are warnings
- **Emergency override**: `skip-bugbot` label for time-sensitive fixes
- **Configurable prompts**: Customized per language/framework in `.ai/bugbot-rules.yml`

---

## How It Works

### Workflow Trigger

Bugbot runs automatically on:
- PR creation (`opened`)
- New commits (`synchronize`)
- PR reopening (`reopened`)

**File types reviewed**:
- Python: `addons/**/*.py`
- JavaScript/TypeScript: `templates/**/*.{js,ts,tsx}`
- XML: `addons/**/*.xml` (Odoo views, data, security)

### Review Process

1. **Detect changes**: Git diff between base branch and PR head
2. **Post comment**: `@cursor run bugbot` with review checklist
3. **Set status**: GitHub status check "Bugbot Required" → Pending
4. **Wait for review**: Cursor Bugbot analyzes code and responds
5. **Status update**: Manual update required (for now) → Success/Failure

### Review Focus Areas

**P0 (Critical - Blocks Merge)**:
- Logic errors and edge cases
- SQL injection via `cr.execute()`
- Authentication/authorization bypass
- Hardcoded secrets
- Security rule gaps (Odoo ir.rule)

**P1 (Important - Warning)**:
- N+1 queries (`.search()` in loops)
- Missing database indexes
- Improper transaction boundaries (`cr.commit`)
- Heavy operations in compute methods
- Blocking calls in async contexts

**P2 (Advisory - Info)**:
- Missing test coverage
- Code duplication (DRY violations)
- Complex functions (>50 lines, cyclomatic complexity >10)
- UI/UX issues in Odoo views

---

## Configuration

### Bugbot Rules (`.ai/bugbot-rules.yml`)

```yaml
bugbot:
  version: "1.0"

  review_focus:
    correctness:
      enabled: true
      severity_threshold: P0
    security:
      enabled: true
      severity_threshold: P0
    performance:
      enabled: true
      severity_threshold: P1

  blocking:
    p0_blocks_merge: false  # Phase 1: Opt-in
    p1_blocks_merge: false
    p2_blocks_merge: false

  override:
    allow_maintainer_override: true
    skip_label: "skip-bugbot"
```

### Workflow (`.github/workflows/bugbot-required.yml`)

- **Concurrency control**: Cancels previous runs on new commits
- **Override check**: Skips if `skip-bugbot` label present
- **Artifact generation**: Saves review summary to `artifacts/bugbot/`
- **Status management**: Sets GitHub status check

---

## Migration Phases

### Phase 1: Opt-In (Week 1-2) - **Current**

**Status**: ✅ Active
**Configuration**: `p0_blocks_merge: false`
**Behavior**:
- Bugbot posts comments on all PRs
- Reviews are informational only
- No merge blocking
- Manual trigger optional via `bugbot-review` label

**Success Criteria**:
- ✅ Bugbot responds < 5 minutes
- ✅ False positive rate < 30% (tuning phase)
- ✅ Developer feedback: "helpful" > 70%

### Phase 2: Soft-Mandatory (Week 3-4)

**Status**: 📋 Planned
**Configuration**: `p0_blocks_merge: true`
**Behavior**:
- Status check shows ❌ on P0 findings
- Merge not blocked (GitHub branch protection not configured)
- Monitor false positives, tune prompts

**Success Criteria**:
- ✅ P0 precision > 80%
- ✅ Zero critical bugs escape to production
- ✅ Mean review time < 3 minutes

### Phase 3: Hard-Mandatory (Week 5+)

**Status**: 📋 Planned
**Configuration**: `p0_blocks_merge: true` + GitHub branch protection
**Behavior**:
- P0 findings block merge
- Emergency override via `skip-bugbot` label
- Full enforcement

**Success Criteria**:
- ✅ False positive rate < 20%
- ✅ Override usage < 5% (emergency only)
- ✅ Team satisfaction > 80%

---

## Usage Guide

### For Developers

#### Normal PR Workflow

1. **Create PR**: Bugbot comment appears automatically
2. **Review findings**: Read Bugbot response in PR comments
3. **Fix issues**: Apply suggested patches or implement fixes
4. **Verify**: Check that status changes to ✅ (manual for now)
5. **Merge**: Proceed with merge after all gates pass

#### Example Bugbot Response

```markdown
## Bugbot AI Review Results

**P0 (Critical)**:
- `addons/ipai_finance_ppm/models/budget.py:45` - SQL injection risk
  ```python
  # BAD
  cr.execute('SELECT * FROM budget WHERE name = %s' % name)

  # GOOD
  cr.execute('SELECT * FROM budget WHERE name = %s', (name,))
  ```

**P1 (Warning)**:
- `addons/ipai_finance_ppm/models/task.py:120` - N+1 query detected
  ```python
  # BAD
  for task in tasks:
      employees = self.env['hr.employee'].search([('task_id', '=', task.id)])

  # GOOD
  employee_data = self.env['hr.employee'].read_group(
      [('task_id', 'in', tasks.ids)],
      ['task_id'],
      ['task_id']
  )
  ```

**Summary**: 1 P0, 1 P1, 0 P2
```

### Emergency Override (Maintainers Only)

**When to use**:
- Critical production hotfix
- False positive confirmed
- Time-sensitive security patch

**How to override**:
```bash
# Add skip-bugbot label
gh pr edit <PR_NUMBER> --add-label skip-bugbot

# Verify workflow skipped
gh run list --workflow bugbot-required.yml --limit 1
```

**Responsibility**: Maintainer assumes risk for bypassing review

---

## Common Patterns Detected

### Odoo-Specific

**SQL Injection**:
```python
# ❌ WRONG - SQL injection risk
cr.execute("SELECT * FROM res_users WHERE login = '%s'" % login)

# ✅ CORRECT - Parameterized query
cr.execute("SELECT * FROM res_users WHERE login = %s", (login,))
```

**N+1 Queries**:
```python
# ❌ WRONG - N+1 query
for partner in partners:
    invoices = self.env['account.move'].search([('partner_id', '=', partner.id)])

# ✅ CORRECT - Single query
invoices = self.env['account.move'].search([('partner_id', 'in', partners.ids)])
```

**Transaction Boundaries**:
```python
# ❌ WRONG - cr.commit() in model method
def process_payment(self):
    self.state = 'paid'
    self.env.cr.commit()  # NEVER do this

# ✅ CORRECT - Let framework handle transactions
def process_payment(self):
    self.state = 'paid'
    # Transaction committed automatically
```

**Recordset Empty Checks**:
```python
# ❌ WRONG - Unnecessary .exists()
if record.exists():
    record.name = 'Updated'

# ✅ CORRECT - Recordsets are falsy when empty
if record:
    record.name = 'Updated'
```

### Next.js/TypeScript

**XSS Prevention**:
```tsx
// ❌ WRONG - Unescaped user input
<div dangerouslySetInnerHTML={{__html: userInput}} />

// ✅ CORRECT - Escaped by default
<div>{userInput}</div>
```

**Race Conditions**:
```typescript
// ❌ WRONG - Race condition
async function updateUser() {
  const user = await getUser()
  user.count++
  await saveUser(user)
}

// ✅ CORRECT - Atomic update
async function updateUser() {
  await db.user.update({
    where: { id },
    data: { count: { increment: 1 } }
  })
}
```

---

## Troubleshooting

### Workflow Not Triggering

**Symptom**: No Bugbot comment on PR

**Possible causes**:
1. No Python/JS/XML files changed → Check `git diff`
2. Skip label present → Remove `skip-bugbot` label
3. Workflow disabled → Check `.github/workflows/bugbot-required.yml`

**Verification**:
```bash
# Check workflow status
gh workflow view bugbot-required.yml

# Check PR files
gh pr diff <PR_NUMBER> --name-only | grep -E '\.(py|js|ts|tsx|xml)$'
```

### False Positives

**Symptom**: Bugbot reports issue that isn't actually a problem

**Action**:
1. Verify finding is incorrect
2. Add comment explaining why (for training data)
3. Use `skip-bugbot` label if blocking
4. Report to maintainer for prompt tuning

**Example**:
```markdown
@cursor This is a false positive. The `.search()` is intentional here because
we need to preserve recordset ordering. Marked as skip-bugbot.
```

### High False Positive Rate

**Symptom**: >30% of findings are incorrect

**Action**:
1. Collect examples in GitHub issue
2. Update `.ai/bugbot-rules.yml` prompts
3. Add exclusion patterns if needed
4. Retrain with better examples

---

## Metrics & Monitoring

### Success Metrics

**Phase 1 (Opt-In)**:
- Response time: < 5 minutes
- False positive rate: < 30%
- Developer satisfaction: > 70%

**Phase 2 (Soft-Mandatory)**:
- P0 precision: > 80%
- Critical bugs prevented: > 0
- Mean review time: < 3 minutes

**Phase 3 (Hard-Mandatory)**:
- False positive rate: < 20%
- Override usage: < 5%
- Team satisfaction: > 80%

### Tracking

**GitHub Insights**:
- Workflow run success rate
- Average run duration
- Override label usage frequency

**PR Comments**:
- Bugbot response time
- Finding distribution (P0/P1/P2)
- Developer feedback

---

## Rollback Plan

### Emergency Rollback (< 5 minutes)

**Option 1: Disable workflow**
```bash
gh workflow disable bugbot-required.yml
```

**Option 2: Skip all PRs**
```bash
# Add skip-bugbot label to all open PRs
gh pr list --json number -q '.[].number' | xargs -I {} gh pr edit {} --add-label skip-bugbot
```

### Gradual Rollback (1-2 hours)

**Fix prompts**:
1. Update `.ai/bugbot-rules.yml`
2. Test on closed PRs
3. Re-enable workflow

### Complete Revert (15-30 minutes)

```bash
# Revert Bugbot files
git revert <commit_sha>
git push origin main
```

---

## FAQ

**Q: Can I bypass Bugbot for urgent hotfixes?**
A: Yes, add the `skip-bugbot` label. Maintainers only.

**Q: What if Bugbot doesn't respond?**
A: Manual status update required (for now). Check GitHub Actions logs.

**Q: How do I report false positives?**
A: Add comment on PR explaining why, then use `skip-bugbot` if blocking.

**Q: Will this slow down my PRs?**
A: No. Bugbot runs in < 5 minutes and doesn't block merge in Phase 1.

**Q: What happens if I ignore P2 findings?**
A: P2 is advisory only. No merge blocking.

---

## See Also

- Configuration: [.ai/bugbot-rules.yml](/.ai/bugbot-rules.yml)
- Workflow: [.github/workflows/bugbot-required.yml](/.github/workflows/bugbot-required.yml)
- Parity Gates: [docs/governance/ODOOSH_GRADE_PARITY_GATING.md](ODOOSH_GRADE_PARITY_GATING.md)
- All Gates: [.github/workflows/all-green-gates.yml](/.github/workflows/all-green-gates.yml)
