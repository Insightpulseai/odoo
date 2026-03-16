# Composer Bugbot Implementation Plan

**Timeline**: 6 weeks (phased rollout)

**Status**: Planning phase

---

## Week 1: Foundation (Opt-In)

### Deliverables
1. **`.ai/composer-bugbot-rules.yml`** (Configuration SSOT)
   - Review focus areas: security, psr-compliance, composer-deps, code-quality
   - Severity levels: P0 (block), P1 (warn), P2 (info)
   - File exclusions: `vendor/**`, `*.blade.php` (handled by frontend gates)
   - Custom prompts for PHP patterns

2. **`.github/workflows/composer-bugbot-required.yml`** (GitHub Actions workflow)
   - Trigger: `pull_request: [opened, synchronize, reopened]`
   - Jobs: override-check, composer-audit, phpstan-security, phpcs-psr, ai-review
   - Artifact upload: security-report.json, psr-violations.txt, composer-audit.json
   - Status: Reporting only (no merge blocking)

3. **`scripts/composer-bugbot/`** (Automation scripts)
   - `run-composer-audit.sh` - Wrapper for composer audit with JSON output
   - `run-phpstan-security.sh` - PHPStan with security ruleset
   - `run-phpcs-psr.sh` - PHP_CodeSniffer PSR-12 validation
   - `parse-findings.py` - Aggregate findings into GitHub status format

### Verification
```bash
# Test workflow locally
act pull_request -W .github/workflows/composer-bugbot-required.yml

# Validate configuration
yamllint .ai/composer-bugbot-rules.yml

# Test scripts
bash scripts/composer-bugbot/run-composer-audit.sh
bash scripts/composer-bugbot/run-phpstan-security.sh
```

### Success Criteria
- ✅ Workflow triggers on PHP file changes
- ✅ All 4 jobs complete successfully
- ✅ Artifacts uploaded with findings
- ✅ Status check shows in PR (informational)

---

## Week 2: Dependency Hardening

### Tasks
1. **Add `composer audit` CVE blocking**
   - Parse `composer audit --format=json` output
   - Extract CVSS scores from advisories
   - Block if any dependency has CVSS ≥ 7.0

2. **Create security baseline**
   - Generate initial security-baseline.json
   - Document known vulnerabilities (with justification)
   - Future runs compare against baseline

3. **Integrate PHPStan security rules**
   - Add `phpstan/extension-installer` to composer.json
   - Install `phpstan/phpstan-symfony` for framework-specific rules
   - Configure phpstan.neon with security focus

### Critical Files
- `composer.json` (add dev dependencies)
- `phpstan.neon` (security ruleset configuration)
- `.github/workflows/composer-bugbot-required.yml` (update composer-audit job)
- `security-baseline.json` (NEW - known vulnerability baseline)

### Verification
```bash
# Run composer audit
composer audit --format=json | jq '.advisories | length'

# Run PHPStan with security rules
vendor/bin/phpstan analyse --configuration=phpstan.neon

# Check baseline generation
python scripts/composer-bugbot/generate-security-baseline.py
```

### Success Criteria
- ✅ Composer audit blocks on CVSS ≥ 7.0
- ✅ Security baseline captures all current advisories
- ✅ PHPStan detects SQL injection, XSS, deserialization patterns

---

## Week 3: PSR Compliance Automation

### Tasks
1. **Add PHP_CodeSniffer PSR-12 validation**
   - Install `squizlabs/php_codesniffer` via Composer
   - Configure phpcs.xml with PSR-12 standard
   - Add phpcs job to workflow

2. **Implement violation threshold**
   - Count PSR violations per file
   - Block if total violations >50 (code quality gate)
   - Generate human-readable report

3. **Add auto-fix capability**
   - Use `phpcbf` (PHP Code Beautifier and Fixer)
   - Provide auto-fix suggestions in PR comments
   - Document how developers can run locally

### Critical Files
- `phpcs.xml` (NEW - PSR-12 ruleset)
- `.github/workflows/composer-bugbot-required.yml` (add phpcs job)
- `scripts/composer-bugbot/run-phpcs-psr.sh` (NEW)
- `scripts/composer-bugbot/auto-fix-psr.sh` (NEW - phpcbf wrapper)

### Verification
```bash
# Run PHP_CodeSniffer
vendor/bin/phpcs --standard=PSR12 src/

# Test auto-fix
vendor/bin/phpcbf --standard=PSR12 src/

# Validate threshold logic
python scripts/composer-bugbot/check-psr-threshold.py
```

### Success Criteria
- ✅ PSR-12 violations detected accurately
- ✅ Auto-fix suggestions provided in PR comments
- ✅ Threshold blocking works (>50 violations = fail)

---

## Week 4: AI Review Integration (Soft-Mandatory)

### Tasks
1. **Set `p0_blocks_merge: true` in configuration**
   - Modify `.ai/composer-bugbot-rules.yml`
   - P0 findings now fail status check (GitHub shows ❌)
   - Still no branch protection (warning only)

2. **Add Cursor AI review integration**
   - Call Cursor Bugbot API with PHP file diffs
   - Parse response for P0/P1/P2 findings
   - Post inline GitHub comments with severity tags

3. **Monitor false positives**
   - Track false positive rate by severity
   - Adjust prompts in `.ai/composer-bugbot-rules.yml`
   - Target: <20% false positive rate for P0

### Critical Files
- `.ai/composer-bugbot-rules.yml` (MODIFY: `p0_blocks_merge: true`)
- `.github/workflows/composer-bugbot-required.yml` (add ai-review job)
- `scripts/composer-bugbot/call-cursor-api.py` (NEW - API integration)
- `scripts/composer-bugbot/post-pr-comments.py` (NEW - GitHub comments)

### Verification
```bash
# Test AI review API
python scripts/composer-bugbot/call-cursor-api.py --pr 123

# Test PR comment posting
python scripts/composer-bugbot/post-pr-comments.py --pr 123 --findings findings.json

# Monitor status checks
gh pr checks 123 | grep composer-bugbot
```

### Success Criteria
- ✅ AI review runs on every PR with PHP changes
- ✅ P0 findings fail status check (❌)
- ✅ Inline comments posted with line numbers and severity
- ✅ False positive rate <20% for P0

---

## Week 5: Refactor & Documentation

### Tasks
1. **Create comprehensive documentation**
   - `docs/governance/COMPOSER_BUGBOT_REVIEW.md` (usage guide)
   - `docs/development/PHP_SECURITY_PATTERNS.md` (common vulnerabilities)
   - `docs/development/PSR_COMPLIANCE_GUIDE.md` (standards reference)

2. **Add evidence capture automation**
   - `scripts/deployment/capture-composer-evidence.sh`
   - Phases: before, after, verification
   - Output: `docs/evidence/<YYYYMMDD-HHMM>/composer-bugbot/`

3. **Cleanup deprecated references**
   - `scripts/cleanup/remove-deprecated-php-refs.sh`
   - Scan for insecure patterns (MD5 passwords, unserialize, etc.)
   - Report findings with line numbers

### Critical Files
- `docs/governance/COMPOSER_BUGBOT_REVIEW.md` (NEW)
- `docs/development/PHP_SECURITY_PATTERNS.md` (NEW)
- `docs/development/PSR_COMPLIANCE_GUIDE.md` (NEW)
- `scripts/deployment/capture-composer-evidence.sh` (NEW)
- `scripts/cleanup/remove-deprecated-php-refs.sh` (NEW)

### Verification
```bash
# Test evidence capture
bash scripts/deployment/capture-composer-evidence.sh "composer-rollout" "before"

# Test deprecated pattern scanner
bash scripts/cleanup/remove-deprecated-php-refs.sh

# Verify documentation accuracy
markdownlint docs/governance/COMPOSER_BUGBOT_REVIEW.md
```

### Success Criteria
- ✅ Documentation complete and accurate
- ✅ Evidence automation working
- ✅ Deprecated pattern scanner functional

---

## Week 6: Hard-Mandatory Enforcement

### Tasks
1. **Add "Composer Bugbot Required" to branch protection**
   - GitHub Settings → Branches → main → Required status checks
   - Add `composer-bugbot-required` to required list
   - Merge blocked on P0 findings (hard enforcement)

2. **Document override process**
   - Emergency bypass: `skip-composer-bugbot` label
   - Requires maintainer approval + incident report
   - Post-merge audit of all overrides

3. **Monitor first week of enforcement**
   - Track override frequency (target <5%)
   - Collect developer feedback
   - Tune prompts for false positives

### Critical Files
- `docs/governance/COMPOSER_BUGBOT_REVIEW.md` (MODIFY: add override process)
- `.github/CODEOWNERS` (ensure maintainers can approve overrides)

### Verification
```bash
# Test branch protection enforcement
git push origin feature/test-composer-gate
gh pr create --title "Test: Composer gate enforcement"

# Verify override workflow
gh pr edit 123 --add-label skip-composer-bugbot
gh run list --workflow composer-bugbot-required.yml --limit 1
```

### Success Criteria
- ✅ Branch protection enforced (merge blocked on P0)
- ✅ Override process documented and working
- ✅ Override usage <5% of all PRs
- ✅ Developer satisfaction >80%

---

## Rollback Plan

### Emergency (< 5 minutes)
```bash
gh workflow disable composer-bugbot-required.yml
# OR
gh pr edit <PR> --add-label skip-composer-bugbot
```

### Gradual (1-2 hours)
- Set `p0_blocks_merge: false` in `.ai/composer-bugbot-rules.yml`
- Fix prompts based on false positives
- Re-enable with improved configuration

### Complete Revert (15-30 minutes)
```bash
git revert <commit_sha>  # Revert Composer Bugbot workflow additions
git push origin main
```

---

## Integration Points

**With Bugbot (Python)**:
- Complementary: Composer Bugbot for PHP, Bugbot for Python
- Shared artifact format: security-report.json schema
- Unified PR comment style

**With Parity Gating**:
- Extends quality gates beyond Odoo Python modules
- Adds PHP code quality dimension
- Supports OCA PHP components (if any)

**With Existing CI**:
- Leverages existing GitHub Actions setup
- Follows artifact upload pattern
- Uses same retention policy (7 days)

---

**Status**: ✅ Week 1 Ready to Execute
**Next**: Create `.ai/composer-bugbot-rules.yml` and workflow file
**Estimated Time to Week 2**: 2-3 hours per week
