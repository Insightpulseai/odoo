# Refactor Fixers

Automated fixers that convert `out/refactor/*` findings into mechanical PRs.

## Principles

- **Idempotent**: Re-run safe, can be applied multiple times
- **Small Blast Radius**: One theme per PR (deps, unused exports, dupes)
- **Always Validate**: Run tests/typecheck after applying
- **Evidence-Based**: Only fix issues identified by analysis

## Available Fixers

### 1. Security (Dependencies)

**Script**: `fix_deps_safe.sh`

Applies safe dependency patches for security vulnerabilities.

```bash
# Safe mode (patch/minor only)
./scripts/refactor/fixers/fix_deps_safe.sh

# Force mode (allow breaking upgrades - validate carefully)
FORCE=1 ./scripts/refactor/fixers/fix_deps_safe.sh
```

**Verification**:
```bash
npm test
npm run typecheck
node scripts/refactor/ci_security_gate.js
```

### 2. Dead Code (Coming Soon)

**Target**: Unused exports identified by ts-prune

**Strategy**:
- Generate deletion patch for exports marked as unused
- Exclude public API entry points
- Validate with typecheck

### 3. Duplicates (Coming Soon)

**Target**: Duplicate code blocks identified by jscpd

**Strategy**:
- Extract common helpers
- Centralize constants
- Create utility modules

### 4. Error Handling (Coming Soon)

**Target**: Inconsistent error patterns identified by ESLint/grep

**Strategy**:
- Standardize error types
- Unify error envelopes
- Consistent logging

## Workflow

```
1. Run analysis
   └→ ./scripts/refactor/run_refactor_subagents.sh

2. Review findings
   └→ cat out/refactor/ACTION_PLAN.md

3. Apply fixers (by priority)
   └→ ./scripts/refactor/fixers/fix_deps_safe.sh
   └→ (future: fix_unused_exports.sh)
   └→ (future: fix_duplicates.sh)

4. Verify changes
   └→ npm test && npm run typecheck

5. Create PR
   └→ git checkout -b refactor/security-deps
   └→ git commit -m "fix(deps): patch security vulnerabilities"
   └→ git push
```

## CI Integration

Security gate automatically fails PRs with critical/high vulnerabilities:

```bash
# Runs in CI after analysis
node scripts/refactor/ci_security_gate.js
```

## Adding New Fixers

1. Create fixer script: `scripts/refactor/fixers/fix_<theme>.sh`
2. Make idempotent (check before applying)
3. Add verification steps
4. Document in this README
5. Add to workflow section above

## Safety Guardrails

- **Dry Run Mode**: Preview changes before applying (use `DRY_RUN=1`)
- **Selective Application**: Target specific files/patterns only
- **Validation Gates**: Always run tests/typecheck
- **Evidence Trail**: Document findings → fixes mapping
- **Rollback Ready**: Keep changes reversible

## ROI Priority (Recommended Order)

Based on impact vs. effort:

1. **Critical/High Deps** (fix_deps_safe.sh) - Immediate security value
2. **Unused Exports** - Reduces bundle size, improves maintainability
3. **Duplicate Code** - DRY principle, reduces maintenance burden
4. **Error Handling** - Consistency, debugging experience
