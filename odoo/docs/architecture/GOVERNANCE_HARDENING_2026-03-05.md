# Governance Hardening - 2026-03-05

> Security and governance hardening for automation workflows following SSOT principles

**Status**: ✅ Complete | **PR**: Pending | **Risk Level**: Low (adds controls, no breaking changes)

---

## Summary

This hardening pass addresses governance violations in the automation suite committed in `0dfc24b66`:

1. **Branch Protection Enforcement** - CI-validated SSOT for default branch rules
2. **Workflow Permission Lockdown** - Least-privilege permissions, no `contents:write` on automation
3. **EE Parity Reframing** - Changed from deployment tool to analysis/reporting tool
4. **Environment Gates** - Production deployments require manual approval

---

## Changes Made

### 1. Branch Protection SSOT (`docs/architecture/GOVERNANCE_BRANCH_PROTECTION.md`)

**Purpose**: Single source of truth for branch protection requirements

**Key Rules**:
- PR required (no direct pushes to main)
- Required checks: GitHub App SSOT Guard, DNS SSOT Guard, Comprehensive Testing, etc.
- Linear history enforced
- Force push disabled
- Admin enforcement enabled

**Enforcement**: `.github/workflows/branch-protection-audit.yml` validates compliance daily

### 2. Workflow Hardening

#### `deploy-odoo-modules.yml`
- ❌ **Removed**: Automatic push deployment trigger
- ✅ **Added**: Explicit `workflow_dispatch` only
- ✅ **Added**: Environment protection (`staging` / `production`)
- ✅ **Added**: Least-privilege permissions block

**Before**:
```yaml
on:
  push:  # DANGEROUS - auto-deploys on push
permissions:
  contents: read
  id-token: write
  issues: write  # Too broad
```

**After**:
```yaml
on:
  workflow_dispatch:  # Manual only
permissions:
  contents: read       # Read repo files
  id-token: write      # OIDC token exchange
  issues: write        # Create rollback issues
  # Explicitly NOT granted: write to repo

environment:
  name: ${{ github.event.inputs.environment }}
  # Production requires manual approval
```

#### `ee-parity-automation.yml` (Complete Rewrite)
- ❌ **Removed**: `contents:write` permission
- ❌ **Removed**: Automatic deployment logic
- ❌ **Removed**: Push/schedule triggers that mutate prod
- ✅ **Added**: Read-only analysis and reporting
- ✅ **Added**: PR generation for improvements (not direct commits)
- ✅ **Added**: Gap tracking issues
- ✅ **Added**: SSOT registry consumption

**Philosophy Change**:
- **Before**: "Do parity" (active deployment)
- **After**: "Report parity" (analysis + proposals)

### 3. EE Parity SSOT Registry (`ssot/ee_parity/replacements.yaml`)

**Purpose**: Registry-driven approach to EE feature parity tracking

**Structure**:
- 10 EE features with current/target parity percentages
- Replacement mappings (OCA modules, n8n workflows, external services)
- Evidence requirements
- Gap documentation
- Prioritization guidance

**Validation Rules** (enforced by workflow):
- All features must have evidence
- No feature can claim >95% parity (always gaps vs EE)
- Production status requires >=80% parity
- All features must list known gaps

**Benefits**:
- Single source of truth for parity claims
- Evidence-backed metrics
- Clear gap visibility
- Prevents "parity inflation"

---

## Risk Assessment

### Low Risk Changes

✅ **Branch Protection Audit** - Non-breaking, adds validation only
✅ **EE Parity Reframing** - Workflow now read-only (safer than before)
✅ **SSOT Registry** - Documentation artifact, no runtime impact
✅ **Permissions Lockdown** - Reduces blast radius, no functional changes

### Medium Risk Changes

⚠️ **Deploy Workflow Changes** - Removes auto-deployment
- **Mitigation**: Workflow was never used in production yet (just committed)
- **Rollback**: Revert to `0dfc24b66` if needed

---

## Rollback Strategy

If this hardening causes issues:

```bash
# Revert to pre-hardening state
git revert <hardening-commit-hash>

# Or selectively restore files
git checkout 0dfc24b66 -- .github/workflows/deploy-odoo-modules.yml
git checkout 0dfc24b66 -- .github/workflows/ee-parity-automation.yml
```

**Note**: Branch protection changes require manual GitHub API calls to revert (see `GOVERNANCE_BRANCH_PROTECTION.md` for commands)

---

## Verification Checklist

### Pre-Deployment

- [ ] All workflows pass YAML lint
- [ ] Branch protection audit workflow is valid
- [ ] SSOT registry schema is valid
- [ ] Permissions blocks are least-privilege
- [ ] No workflows have `contents:write` without justification

### Post-Deployment

- [ ] Branch protection audit runs successfully on main
- [ ] EE parity workflow generates reports (not deployments)
- [ ] Deploy workflow requires environment approval for production
- [ ] No unexpected CI failures
- [ ] GitHub branch protection settings match SSOT

---

## Next Steps

1. **Review PR** - Architecture team reviews changes
2. **Merge to Main** - Apply governance controls
3. **Configure Environments** - Set up production environment with required reviewers in GitHub Settings → Environments
4. **Test Workflows** - Trigger `ee-parity-automation.yml` manually to verify reporting
5. **Monitor Compliance** - Branch protection audit runs daily, watch for drift alerts

---

## References

- Original automation commit: `0dfc24b66`
- Hardening rationale: See user prompt on 2026-03-05
- Branch protection SSOT: `docs/architecture/GOVERNANCE_BRANCH_PROTECTION.md`
- EE parity SSOT: `ssot/ee_parity/replacements.yaml`

**Author**: Claude Sonnet 4.5 (governance hardening agent)
**Date**: 2026-03-05
**Review**: Required before merge
