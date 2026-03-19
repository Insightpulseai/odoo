# Branch Protection Governance (SSOT)

> Single source of truth for default branch protection requirements.
> This document defines the required protection rules that MUST be enforced on `main`.
> CI validates compliance via `.github/workflows/branch-protection-audit.yml`.

**Status**: ✅ Active | **Last Updated**: 2026-03-05
**Enforcement**: Automated via CI | **Override**: Requires architecture approval

---

## Required Protection Rules

### 1. Pull Request Requirements

```yaml
require_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: false  # Not enforcing CODEOWNERS yet
  require_last_push_approval: true
```

**Rationale**: No direct pushes to `main`. All changes must go through PR review.

**Exception Process**: None. Architecture changes requiring emergency hotfixes must use a dedicated `hotfix/*` branch with post-facto PR.

---

### 2. Required Status Checks

All PRs targeting `main` must pass these checks before merge:

```yaml
required_status_checks:
  strict: true  # Require branches to be up to date
  contexts:
    # Core governance
    - "GitHub App SSOT Guard"
    - "DNS SSOT Guard"
    - "Spec-Kit Drift Check"

    # Security gates
    - "Secret Pattern Scan"
    - "Dependency Audit (Critical/High)"
    - "SAST (Semgrep)"

    # Quality gates
    - "Comprehensive Testing"
    - "TypeScript Build"
    - "Python Lint (Black + isort)"

    # Documentation gates
    - "Spec Bundle Validation"
    - "Evidence Path Check"
```

**Rationale**: Multi-layered defense ensuring SSOT compliance, security, and quality before merge.

**Adding New Required Checks**:
1. Update this document's `contexts` list
2. Ensure the workflow exists and is reliable
3. Commit both changes together
4. CI will enforce new requirement immediately

---

### 3. Restrictions

```yaml
restrictions:
  users: []
  teams: []
  apps: []
```

**Rationale**: No bypass permissions. All contributors (including admins) must follow PR workflow.

**Admin Override**: GitHub's "Include administrators" setting is **disabled**. Even repo admins cannot bypass PR requirements.

---

### 4. Linear History

```yaml
require_linear_history: true
```

**Rationale**: No merge commits. All PRs must be squashed or rebased.

**Branch Strategy**: Feature branches are ephemeral. History on `main` must be clean and bisectable.

---

### 5. Force Push Protection

```yaml
allow_force_pushes: false
allow_deletions: false
```

**Rationale**: Prevent history rewriting on `main`. Force pushes can bypass commit signatures and break audit trails.

---

### 6. Conversation Resolution

```yaml
require_conversation_resolution: true
```

**Rationale**: All review comments must be resolved before merge. Prevents accidental merge of unaddressed feedback.

---

## Validation Strategy

### CI Enforcement

`.github/workflows/branch-protection-audit.yml` runs on:
- Every push to `main` (validates current state)
- PR open/sync (validates target branch)
- Daily scheduled check (drift detection)

**Failure Modes**:
- Missing required check → Fail with list of missing contexts
- Disabled PR requirement → Fail with remediation steps
- Force push enabled → Fail with security alert

### Manual Verification

```bash
# Check current branch protection status
gh api repos/Insightpulseai/odoo/branches/main/protection \
  --jq '{
    required_pull_request_reviews,
    required_status_checks,
    restrictions,
    enforce_admins,
    required_linear_history,
    allow_force_pushes,
    allow_deletions,
    required_conversation_resolution
  }'

# Compare against SSOT
diff <(echo "$EXPECTED_CONFIG") <(gh api repos/.../protection)
```

---

## Drift Remediation

If CI detects drift (settings don't match SSOT):

1. **Automated Fix** (preferred):
   ```bash
   # Run infrastructure sync (requires GitHub PAT with admin:repo)
   ./scripts/governance/sync-branch-protection.sh
   ```

2. **Manual Fix** (via GitHub API):
   ```bash
   gh api --method PUT repos/Insightpulseai/odoo/branches/main/protection \
     -F required_pull_request_reviews[required_approving_review_count]=1 \
     -F required_pull_request_reviews[dismiss_stale_reviews]=true \
     -F required_status_checks[strict]=true \
     -F required_status_checks[contexts][]=@required-checks.json \
     -F enforce_admins=true \
     -F required_linear_history=true \
     -F allow_force_pushes=false \
     -F allow_deletions=false \
     -F required_conversation_resolution=true
   ```

3. **Emergency Override** (requires architecture team approval):
   - Document reason in `docs/architecture/ADR/YYYY-MM-DD-branch-protection-override.md`
   - Create tracking issue with `governance` label
   - Restore protection within 24 hours

---

## Exception Handling

### Dependabot PRs

Dependabot PRs automatically trigger required checks. If a check is flaky or irrelevant for dependency updates:

1. Add conditional logic to workflow (skip for `dependabot/**` branches)
2. Document exemption in workflow file
3. Add compensating control (e.g., require manual review from security team)

### CI Outages

If a required check is experiencing an outage:

1. Create incident issue with `ci-outage` label
2. Temporarily mark check as non-required (document in issue)
3. Review all merged PRs post-incident
4. Restore requirement once service is stable

**DO NOT** bypass PR requirement due to CI issues. Use merge queue or wait for resolution.

---

## Security Considerations

### Bypass via Settings UI

GitHub's branch protection UI allows admins to modify settings without PR review. This creates a governance gap.

**Mitigation**:
- Daily CI audit detects drift within 24 hours
- Alert via GitHub issue + Slack notification
- Revert unauthorized changes automatically
- Escalate repeated violations to security team

### Bypass via GitHub CLI/API

GitHub CLI with `admin:repo` scope can modify branch protection programmatically.

**Mitigation**:
- Limit `admin:repo` PAT distribution (architecture team only)
- All protection changes must reference this SSOT document
- Audit trail via GitHub audit log + Supabase ops.platform_events

---

## References

| Resource | URL |
|----------|-----|
| GitHub Branch Protection API | https://docs.github.com/rest/branches/branch-protection |
| Required Status Checks | https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging |
| Linear History | https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-linear-history |

---

**Changelog**:
- 2026-03-05: Initial SSOT document for branch protection governance
- Next: Add automated sync script + CI enforcement workflow
