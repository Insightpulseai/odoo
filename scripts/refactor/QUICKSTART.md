# Refactor Pipeline Quick Start

Complete workflow from analysis to automated fixes to PR.

## 🚀 Full Workflow (5 Minutes)

```bash
# 1. Run analysis (2-5 min depending on codebase size)
./scripts/refactor/run_refactor_subagents.sh

# 2. Review findings
cat out/refactor/ACTION_PLAN.md

# 3. Apply automated fixes (security priority)
./scripts/refactor/apply_fixes.sh security

# 4. Verify changes
git diff
npm test
npm run typecheck

# 5. Create PR
git checkout -b refactor/security-deps
git commit -am "fix(deps): patch security vulnerabilities

Applies automated security fixes from refactor analysis:
- Critical/high vulnerability patches
- Safe dependency updates (patch/minor only)

Evidence: out/refactor/npm-audit.json
Verification: CI security gate passes

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push -u origin refactor/security-deps
```

## 📊 Understanding the Output

### ACTION_PLAN.md Structure

```markdown
# Codebase Refactoring Analysis — Prioritized Action Plan

## Top Priorities (sorted by severity)

- **[CRITICAL] security: npm audit: 2 critical vulnerabilities**
  - Evidence: `out/refactor/npm-audit.json`
  - Suggested fix: Patch/upgrade deps; consider overrides/resolutions...

- **[HIGH] security: Semgrep findings: 5**
  - Evidence: `out/refactor/semgrep.json`
  - Suggested fix: Triage by ruleId; fix injections, unsafe eval...

- **[MEDIUM] dead-code: Unused deps: 3 deps, 2 devDeps**
  - Evidence: `out/refactor/depcheck.json`
  - Suggested fix: Remove unused deps; replace transitive-only imports...
```

**Severity Levels**:
- `CRITICAL` → Immediate action, blocks CI
- `HIGH` → Fix in current sprint
- `MEDIUM` → Plan for next sprint
- `LOW` → Backlog/tech debt

## 🎯 Fix Strategies by Theme

### 1. Security (Automated)

```bash
# Safe mode (recommended)
./scripts/refactor/apply_fixes.sh security

# Force mode (caution: breaking changes)
FORCE=1 ./scripts/refactor/fixers/fix_deps_safe.sh
```

**When to Use Force Mode**:
- Safe mode didn't resolve all critical/high vulnerabilities
- You have comprehensive test coverage
- Ready to handle potential breaking changes

**Validation**:
```bash
node scripts/refactor/ci_security_gate.js  # Must pass
npm test                                    # Must pass
npm run typecheck                           # Must pass
```

### 2. Unused Exports (Manual for Now)

```bash
# Review findings
cat out/refactor/ts-prune.txt

# Manual process:
# 1. Verify exports are truly unused (not public API)
# 2. Delete/inline exports
# 3. Run typecheck to ensure no breakage
# 4. Commit: "refactor: remove unused exports"
```

### 3. Duplicates (Manual)

```bash
# Review findings
cat out/refactor/dupes/jscpd-report.md

# Manual process:
# 1. Identify duplicate blocks
# 2. Extract to shared helper/utility
# 3. Replace duplicates with helper calls
# 4. Commit: "refactor: extract shared utilities"
```

### 4. Error Handling (Manual)

```bash
# Review findings
cat out/refactor/eslint.json
cat out/refactor/error-handling.grep.txt

# Manual process:
# 1. Standardize error classes
# 2. Unify error envelopes (API responses)
# 3. Consistent logging patterns
# 4. Commit: "refactor: standardize error handling"
```

## 🔒 CI Security Gate

**Automatic Enforcement**: CI fails PRs with critical/high vulnerabilities

**Gate Logic** (`ci_security_gate.js`):
```javascript
if (critical > 0 || high > 0) {
  exit("Failing CI: critical/high vulnerabilities present");
}
```

**Bypass** (emergency only, requires approval):
```yaml
# Add to workflow step:
continue-on-error: true  # DO NOT use in production
```

## 📈 ROI Priority (Recommended Order)

Based on security + impact:

1. **Security** → Immediate (automated)
   - Fix critical/high vulnerabilities
   - Run: `./scripts/refactor/apply_fixes.sh security`

2. **Unused Exports** → High impact (manual)
   - Reduces bundle size
   - Improves tree-shaking
   - Lower maintenance burden

3. **Duplicates** → Medium impact (manual)
   - DRY principle
   - Single source of truth
   - Easier bug fixes

4. **Error Handling** → Low impact (manual)
   - Consistency
   - Better debugging
   - User experience

## 🔄 Continuous Refactoring

### Weekly Cadence

```bash
# Monday: Run analysis
./scripts/refactor/run_refactor_subagents.sh

# Tuesday: Triage + apply security fixes
./scripts/refactor/apply_fixes.sh security

# Wednesday-Friday: Manual refactoring (unused/dupes/errors)
# based on ACTION_PLAN.md priorities
```

### PR Batch Strategy

**Good**: Small, focused PRs
```
✅ refactor/security-deps       (10-20 deps)
✅ refactor/unused-exports-auth (5-10 files)
✅ refactor/duplicates-utils    (2-3 helpers)
```

**Bad**: Large, mixed PRs
```
❌ refactor/everything          (100+ files, mixed themes)
❌ refactor/cleanup             (unclear scope)
```

## 🛠️ Customization

### Adjust Analysis Thresholds

Edit `scripts/refactor/run_refactor_subagents.sh`:

```bash
# More aggressive duplicate detection
--min-lines 5 --min-tokens 50

# Less aggressive (reduce noise)
--min-lines 10 --min-tokens 100
```

### Add Custom Fixer

```bash
# Create fixer
cat > scripts/refactor/fixers/fix_custom.sh <<'BASH'
#!/usr/bin/env bash
set -euo pipefail
# Your custom fix logic here
BASH
chmod +x scripts/refactor/fixers/fix_custom.sh

# Wire into apply_fixes.sh
# Add case statement entry
```

## 📚 Additional Resources

- **Analysis Details**: `scripts/refactor/README.md`
- **Fixer Details**: `scripts/refactor/fixers/README.md`
- **CI Workflow**: `.github/workflows/refactor-subagents.yml`
- **Evidence**: `docs/evidence/*/refactor-subagents/`
