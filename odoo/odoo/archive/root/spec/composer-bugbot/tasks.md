# Composer Bugbot Implementation Tasks

**Status**: Week 1 (Foundation - Opt-In)

---

## Week 1: Foundation (Opt-In)

### Task 1.1: Create Composer Bugbot Configuration
**Status**: Pending
**Assignee**: TBD
**Priority**: P0

**Description**: Create `.ai/composer-bugbot-rules.yml` with review focus, severity levels, and PHP-specific prompts

**Acceptance Criteria**:
- ✅ YAML validates with `yamllint`
- ✅ Contains all review focus areas: security, psr-compliance, composer-deps, code-quality
- ✅ Severity mapping defined: P0 (block), P1 (warn), P2 (info)
- ✅ File exclusions configured: vendor/**, *.blade.php
- ✅ Custom prompts for PHP security patterns (SQL injection, XSS, deserialization)

**Files Created**:
- `.ai/composer-bugbot-rules.yml`

---

### Task 1.2: Create GitHub Actions Workflow
**Status**: Pending
**Assignee**: TBD
**Priority**: P0

**Description**: Create `.github/workflows/composer-bugbot-required.yml` with parallel jobs for all validation steps

**Acceptance Criteria**:
- ✅ Workflow triggers on pull_request events (opened, synchronize, reopened)
- ✅ Contains 5 jobs: override-check, composer-audit, phpstan-security, phpcs-psr, ai-review
- ✅ All jobs use `continue-on-error: true` (reporting phase only)
- ✅ Artifacts uploaded with 7-day retention
- ✅ Status check created (informational, non-blocking)

**Files Created**:
- `.github/workflows/composer-bugbot-required.yml`

---

### Task 1.3: Create Composer Audit Script
**Status**: Pending
**Assignee**: TBD
**Priority**: P0

**Description**: Create `scripts/composer-bugbot/run-composer-audit.sh` wrapper for composer audit with JSON output

**Acceptance Criteria**:
- ✅ Script runs `composer audit --format=json`
- ✅ Parses output to extract CVSS scores
- ✅ Saves results to `artifacts/composer-audit.json`
- ✅ Exit code 0 if no CVEs, 1 if CVSS ≥ 7.0
- ✅ Executable permissions set (`chmod +x`)

**Files Created**:
- `scripts/composer-bugbot/run-composer-audit.sh`

**Execution**:
```bash
mkdir -p scripts/composer-bugbot
chmod +x scripts/composer-bugbot/run-composer-audit.sh
bash scripts/composer-bugbot/run-composer-audit.sh
```

---

### Task 1.4: Create PHPStan Security Script
**Status**: Pending
**Assignee**: TBD
**Priority**: P0

**Description**: Create `scripts/composer-bugbot/run-phpstan-security.sh` for static security analysis

**Acceptance Criteria**:
- ✅ Script runs `vendor/bin/phpstan analyse` with security ruleset
- ✅ Detects SQL injection, XSS, deserialization, weak crypto patterns
- ✅ Saves results to `artifacts/phpstan-security.txt`
- ✅ Exit code 0 if clean, 1 if P0 findings
- ✅ Works with or without phpstan.neon (defaults to inline config)

**Files Created**:
- `scripts/composer-bugbot/run-phpstan-security.sh`

**Execution**:
```bash
chmod +x scripts/composer-bugbot/run-phpstan-security.sh
bash scripts/composer-bugbot/run-phpstan-security.sh src/
```

---

### Task 1.5: Create PHP_CodeSniffer PSR Script
**Status**: Pending
**Assignee**: TBD
**Priority**: P0

**Description**: Create `scripts/composer-bugbot/run-phpcs-psr.sh` for PSR-12 compliance validation

**Acceptance Criteria**:
- ✅ Script runs `vendor/bin/phpcs --standard=PSR12`
- ✅ Counts total violations per file
- ✅ Saves results to `artifacts/psr-violations.txt`
- ✅ Exit code 0 if <50 violations, 1 if ≥50
- ✅ Provides human-readable summary

**Files Created**:
- `scripts/composer-bugbot/run-phpcs-psr.sh`

**Execution**:
```bash
chmod +x scripts/composer-bugbot/run-phpcs-psr.sh
bash scripts/composer-bugbot/run-phpcs-psr.sh src/
```

---

### Task 1.6: Create Findings Parser
**Status**: Pending
**Assignee**: TBD
**Priority**: P1

**Description**: Create `scripts/composer-bugbot/parse-findings.py` to aggregate all findings into GitHub status format

**Acceptance Criteria**:
- ✅ Parses JSON from composer audit, PHPStan, phpcs
- ✅ Aggregates findings by severity (P0/P1/P2)
- ✅ Generates GitHub status check output
- ✅ Includes summary statistics (total findings, breakdown by tool)
- ✅ Python 3.12+ compatible

**Files Created**:
- `scripts/composer-bugbot/parse-findings.py`

**Execution**:
```bash
python scripts/composer-bugbot/parse-findings.py \
  --composer artifacts/composer-audit.json \
  --phpstan artifacts/phpstan-security.txt \
  --phpcs artifacts/psr-violations.txt \
  --output artifacts/findings-summary.json
```

---

### Task 1.7: Local Testing & Documentation
**Status**: Pending
**Assignee**: TBD
**Priority**: P1

**Description**: Test all scripts locally and create README.md with usage instructions

**Acceptance Criteria**:
- ✅ All scripts execute successfully on sample PHP project
- ✅ README.md created in `spec/composer-bugbot/`
- ✅ Documentation includes setup, usage, troubleshooting
- ✅ Example outputs provided for each script
- ✅ Local test passes without errors

**Files Created**:
- `spec/composer-bugbot/README.md`

**Verification**:
```bash
# Run all scripts in sequence
bash scripts/composer-bugbot/run-composer-audit.sh
bash scripts/composer-bugbot/run-phpstan-security.sh src/
bash scripts/composer-bugbot/run-phpcs-psr.sh src/
python scripts/composer-bugbot/parse-findings.py \
  --composer artifacts/composer-audit.json \
  --phpstan artifacts/phpstan-security.txt \
  --phpcs artifacts/psr-violations.txt
```

---

## Week 2: Dependency Hardening

### Task 2.1: Add Composer Dev Dependencies
**Status**: Pending
**Priority**: P0

**Dependencies**: Tasks 1.1-1.7

**Files Modified**:
- `composer.json` (add phpstan/*, squizlabs/php_codesniffer)

---

### Task 2.2: Create PHPStan Configuration
**Status**: Pending
**Priority**: P0

**Files Created**:
- `phpstan.neon`

---

### Task 2.3: Generate Security Baseline
**Status**: Pending
**Priority**: P1

**Files Created**:
- `security-baseline.json`
- `scripts/composer-bugbot/generate-security-baseline.py`

---

## Week 3: PSR Compliance Automation

### Task 3.1: Create PHP_CodeSniffer Configuration
**Status**: Pending
**Priority**: P0

**Files Created**:
- `phpcs.xml`

---

### Task 3.2: Add Auto-Fix Script
**Status**: Pending
**Priority**: P1

**Files Created**:
- `scripts/composer-bugbot/auto-fix-psr.sh`

---

## Week 4: AI Review Integration

### Task 4.1: Update Configuration for Merge Blocking
**Status**: Pending
**Priority**: P0

**Files Modified**:
- `.ai/composer-bugbot-rules.yml` (set `p0_blocks_merge: true`)

---

### Task 4.2: Create Cursor API Integration
**Status**: Pending
**Priority**: P0

**Files Created**:
- `scripts/composer-bugbot/call-cursor-api.py`

---

### Task 4.3: Create PR Comment Poster
**Status**: Pending
**Priority**: P0

**Files Created**:
- `scripts/composer-bugbot/post-pr-comments.py`

---

## Week 5: Documentation & Cleanup

### Task 5.1: Create Governance Documentation
**Status**: Pending
**Priority**: P1

**Files Created**:
- `docs/governance/COMPOSER_BUGBOT_REVIEW.md`

---

### Task 5.2: Create Development Guides
**Status**: Pending
**Priority**: P1

**Files Created**:
- `docs/development/PHP_SECURITY_PATTERNS.md`
- `docs/development/PSR_COMPLIANCE_GUIDE.md`

---

### Task 5.3: Create Evidence Automation
**Status**: Pending
**Priority**: P2

**Files Created**:
- `scripts/deployment/capture-composer-evidence.sh`

---

## Week 6: Hard-Mandatory Enforcement

### Task 6.1: Configure Branch Protection
**Status**: Pending
**Priority**: P0

**Manual Steps**:
- GitHub Settings → Branches → main → Add `composer-bugbot-required` to required status checks

---

### Task 6.2: Document Override Process
**Status**: Pending
**Priority**: P1

**Files Modified**:
- `docs/governance/COMPOSER_BUGBOT_REVIEW.md`

---

### Task 6.3: Monitor & Tune
**Status**: Pending
**Priority**: P1

**Activities**:
- Track override frequency (target <5%)
- Collect developer feedback
- Adjust prompts for false positives

---

## Legend

**Status**:
- ✅ Completed
- 🔄 In Progress
- ⏳ Blocked
- ❌ Failed
- 📋 Pending

**Priority**:
- P0: Blocker (must complete this week)
- P1: High (should complete this week)
- P2: Medium (nice to have)
- P3: Low (backlog)
