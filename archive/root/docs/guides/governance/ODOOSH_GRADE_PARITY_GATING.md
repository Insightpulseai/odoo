# Odoo.sh-Grade Parity Gating Framework

**Status**: Active | **Last Updated**: 2026-02-12
**Owner**: Engineering Platform Team
**Authority**: This document defines canonical gating policy for `Insightpulseai/odoo`

---

## Executive Summary

This framework establishes **Odoo.sh-grade** quality gates for the InsightPulse Odoo CE+OCA platform, ensuring every PR meets production-ready standards before merge. Gates are organized into **3 tiers** based on failure impact and execution cost.

**Definition of "Odoo.sh-grade"**: Production-ready changes that maintain:
1. **Install determinism**: Clean DB installs succeed with exact seed counts
2. **Documentation accuracy**: All docs build cleanly and reference current architecture
3. **Parity integrity**: CE+OCA coverage remains ≥80% of EE feature catalog

---

## Gate Tiers

### Tier-0: Blocking Gates (MUST PASS on every PR)

**Execution Time**: <5 minutes total
**Failure Impact**: Production deployment risk
**Policy**: Zero exceptions; automated enforcement

| Gate | Workflow | Purpose | Artifact |
|------|----------|---------|----------|
| **Seed Determinism** | `finance-ppm-health.yml` | Verify Finance PPM seeds install with exact counts (8/12/144/36/36) | `artifacts/seed_audit.json` |
| **Clean Install Smoke** | `build-seeded-image.yml` | Prove fresh DB installs all canonical modules without error | `artifacts/install_proof.txt` |
| **Docs Build** | `docs-build.yml` | MkDocs strict build with zero warnings | `artifacts/docs_site/` |
| **Forbidden Patterns** | `forbidden-patterns-gate.yml` | Block outdated references (Mailgun, .net domains, Odoo 18, Plane) | `artifacts/forbidden_scan.txt` |

### Tier-1: Quality Gates (SHOULD PASS, may defer with justification)

**Execution Time**: 5-15 minutes
**Failure Impact**: User experience degradation
**Policy**: Merge with documented tech debt ticket if failing

| Gate | Workflow | Purpose |
|------|----------|---------|
| **EE Parity Coverage** | `ee-parity-gate.yml` | Maintain ≥80% feature parity via CE+OCA mapping |
| **OCA Module Health** | `auto-install-parity-modules.yml` | Verify OCA dependencies install cleanly |
| **Security Scan** | `security-audit.yml` | Bandit + safety checks on Python code |
| **Type Coverage** | `typing-gate.yml` | Mypy validation on typed modules |

### Tier-2: Enhancement Gates (optional, informational)

**Execution Time**: 15+ minutes
**Failure Impact**: Code quality signals
**Policy**: Informational only; no merge blocking

| Gate | Workflow | Purpose |
|------|----------|---------|
| **Performance Regression** | `performance-benchmark.yml` | Detect module load time increases >10% |
| **Accessibility** | `a11y-audit.yml` | Pa11y scan on frontend views |
| **Link Rot** | `link-checker.yml` | Detect broken documentation links |

---

## Tier-0 Gate Specifications

### 1. Seed Determinism Gate

**Workflow**: `.github/workflows/finance-ppm-health.yml`
**Local Reproduction**: `bash scripts/gates/run_parity_gates.sh seed-audit`

**Success Criteria**:
```bash
# Must produce exact counts from XML seed sources
projects:      8  # from addons/ipai/ipai_finance_workflow/data/finance_projects.xml
teams:        12  # from addons/ipai/ipai_finance_workflow/data/finance_team.xml
month-end:   144  # from addons/ipai/ipai_finance_workflow/data/finance_ppm_tasks.xml (BIR excluded)
bir:          36  # from addons/ipai/ipai_finance_workflow/data/finance_ppm_tasks.xml (BIR only)
stages:       36  # from addons/ipai/ipai_finance_workflow/data/finance_task_stages.xml
```

**Evidence Required**: `artifacts/seed_audit.json` with SHA256 hashes of source XML files

**Definition of Green**:
- JSON artifact generated deterministically (no variances across runs)
- All 5 counts match expected values
- Zero XML parsing errors
- Zero duplicate record IDs

**Failure Remediation**:
1. Run `python scripts/validate_finance_ppm_data.py --strict`
2. If XML changed: Update expected counts in `scripts/gates/seed_audit_config.json`
3. If generator changed: Regenerate XML via `python scripts/generate_seed_xml.py`
4. Never hard-code counts in workflow YAML; derive from source files

### 2. Clean Install Smoke Gate

**Workflow**: `.github/workflows/build-seeded-image.yml`
**Local Reproduction**: `bash scripts/gates/run_parity_gates.sh install-smoke`

**Success Criteria**:
```bash
# Fresh PostgreSQL 16 database, no prior state
docker compose exec -T odoo odoo -d odoo_fresh_test \
  -i ipai_enterprise_bridge,ipai_scout_bundle,ipai_ces_bundle \
  --stop-after-init --log-level=error --without-demo=all

# Exit code 0, zero ERROR lines in output
```

**Evidence Required**: `artifacts/install_proof.txt` with:
- Database name
- Modules installed
- Installation duration
- Log excerpt (last 50 lines)

**Definition of Green**:
- Exit code 0
- Zero `ERROR` or `CRITICAL` log lines
- Installation completes in <120 seconds
- Database teardown succeeds

**Failure Remediation**:
1. Check module `__manifest__.py` dependencies are installable
2. Verify no hard-coded database references (use `self.env.cr.dbname`)
3. Run `python -m py_compile` on all `.py` files in changed modules
4. Check for missing `__init__.py` files in module subdirectories

### 3. Docs Build Gate

**Workflow**: `.github/workflows/docs-build.yml`
**Local Reproduction**: `bash scripts/gates/run_parity_gates.sh docs-build`

**Success Criteria**:
```bash
pip install -r requirements-docs.txt
mkdocs build --strict --site-dir artifacts/docs_site

# Exit code 0, zero warnings
```

**Evidence Required**: `artifacts/docs_site/` directory with built HTML

**Definition of Green**:
- MkDocs build completes with `--strict` flag
- Zero `WARNING` or `ERROR` messages
- All nav links resolve (no 404s in internal links)
- Build time <60 seconds

**Failure Remediation**:
1. Fix broken markdown references: `[text](path)` must point to existing files
2. Update `mkdocs.yml` nav structure if pages moved/deleted
3. Run `mkdocs serve` locally to preview before pushing
4. Use `<!-- markdownlint-disable -->` for intentional violations only

### 4. Forbidden Patterns Gate

**Workflow**: `.github/workflows/forbidden-patterns-gate.yml`
**Local Reproduction**: `bash scripts/gates/run_parity_gates.sh forbidden-scan`

**Success Criteria**:
```bash
# Scan for deprecated/forbidden patterns
rg -n "mailgun|mg\.insightpulseai" README.md docs/ || EXIT_CODE=$?
rg -n "insightpulseai\.net" README.md docs/ mkdocs.yml || EXIT_CODE=$?
rg -n "Odoo 18|odoo.*18" README.md docs/ mkdocs.yml || EXIT_CODE=$?
rg -n "Plane" README.md docs/ || EXIT_CODE=$?

# Exit code 1 (no matches) is success; exit code 0 (matches found) is failure
```

**Evidence Required**: `artifacts/forbidden_scan.txt` with:
- List of matched files and line numbers (or "No forbidden patterns found")
- Pattern scan timestamp
- Scan duration

**Definition of Green**:
- Zero matches for all forbidden patterns
- Scan completes in <10 seconds

**Failure Remediation**:
1. **Mailgun**: Replace with "Zoho Mail SMTP" and `smtp.zoho.com:587`
2. **insightpulseai.net**: Replace with `insightpulseai.com`
3. **Odoo 18**: Replace with "Odoo 19 CE"
4. **Plane**: Remove or move to `docs/deprecated/PLANE_ARCHIVE.md` with clear deprecation notice

**Allowed Exceptions** (must be in `docs/deprecated/` or `docs/archive/`):
- Historical deployment proofs referencing old systems
- Migration guides explicitly documenting the change

---

## Local Gate Runner

**Script**: `scripts/gates/run_parity_gates.sh`
**Usage**: `bash scripts/gates/run_parity_gates.sh [gate-name|all]`

**Supported Commands**:
```bash
# Run individual gates
bash scripts/gates/run_parity_gates.sh seed-audit
bash scripts/gates/run_parity_gates.sh install-smoke
bash scripts/gates/run_parity_gates.sh docs-build
bash scripts/gates/run_parity_gates.sh forbidden-scan

# Run all Tier-0 gates
bash scripts/gates/run_parity_gates.sh all

# Output artifacts to artifacts/ directory
# Exit code 0 = all gates passed, non-zero = failure
```

**Artifacts Output**:
```
artifacts/
├── seed_audit.json          # Deterministic seed count + hashes
├── install_proof.txt         # Clean DB install evidence
├── docs_site/                # Built MkDocs site
├── forbidden_scan.txt        # Pattern scan results
└── gate_run_summary.json    # Overall pass/fail status
```

---

## CI Workflow Integration

**GitHub Actions Setup**:

```yaml
# .github/workflows/tier0-parity-gate.yml (NEW - consolidates Tier-0 gates)
name: Tier-0 Parity Gate

on:
  pull_request:
  push:
    branches: [main]

jobs:
  tier0-gates:
    name: Run Tier-0 Gates
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Tier-0 Gate Runner
        run: bash scripts/gates/run_parity_gates.sh all

      - name: Upload Gate Artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: tier0-gate-artifacts
          path: artifacts/
          retention-days: 7

      - name: Fail if gates failed
        if: failure()
        run: |
          echo "::error::Tier-0 gates failed. See artifacts for details."
          exit 1
```

**Existing Workflows to Deprecate**:
- Individual gate workflows can remain but should be marked "informational only"
- New canonical gate runner is `tier0-parity-gate.yml`

---

## Break-Glass Procedures

**Emergency Merge (Tier-0 Gate Override)**:

**Policy**: Requires VP Engineering approval + post-merge fix commitment

**Procedure**:
1. Create override label: `bypass-tier0-gates` (repo admin only)
2. Add label to PR with justification comment
3. Workflow checks for label: `if: contains(github.event.pull_request.labels.*.name, 'bypass-tier0-gates')`
4. Post-merge: Create P0 issue to fix failing gate within 24 hours
5. Remove label after gate fixed

**Example Justification**:
```
Override Reason: Production incident requires immediate config change
Failing Gate: docs-build (broken link to deprecated page)
Fix Commitment: Issue #1234 to remove deprecated page reference (ETA: 4 hours)
Approved By: @vp-engineering
```

---

## Rollback Strategy

**Scenario 1: New gate breaks main branch**

```bash
# Identify breaking commit
git log --oneline -n 20

# Revert specific gate workflow addition
git revert <commit-sha-of-gate-workflow>
git push origin main

# Alternative: Temporarily disable gate in workflow
# Edit .github/workflows/tier0-parity-gate.yml
# Change: if: github.ref == 'refs/heads/main' && false  # Disable temporarily
```

**Scenario 2: Seed count expectations out of sync**

```bash
# Emergency: Update expected counts in config
# Edit scripts/gates/seed_audit_config.json
# Commit with message: "fix(gates): update seed expectations after <reason>"

# Proper fix: Regenerate seeds or fix drift
python scripts/generate_seed_xml.py
python scripts/validate_finance_ppm_data.py --strict
```

**Scenario 3: False positive in forbidden patterns**

```bash
# Temporary: Add pattern to exclusion list
# Edit scripts/gates/forbidden_scan_exclusions.txt
# Add file path that should be excluded

# Proper fix: Move offending content to docs/deprecated/
mkdir -p docs/deprecated
git mv docs/MAILGUN_INTEGRATION.md docs/deprecated/MAILGUN_INTEGRATION_DEPRECATED.md
```

---

## Metrics & Monitoring

**Gate Health Dashboard** (GitHub Actions):
- Tier-0 pass rate: Target ≥99% on main branch
- Average gate execution time: Target <3 minutes for all Tier-0 gates
- False positive rate: Target <1% (gates failing due to flakiness, not real issues)

**Quarterly Review**:
- Review gate effectiveness: Are gates catching real issues?
- Review gate performance: Can execution time be reduced?
- Review false positive incidents: Do exclusions need refinement?

---

## Appendix: Evidence-Based Claims

**Source of Truth for Tier-0 Gates**:

| Claim | Evidence File | Line Numbers |
|-------|---------------|--------------|
| Finance PPM counts: 8/12/144/36/36 | `.github/workflows/finance-ppm-health.yml` | 33-34, 40 |
| Mailgun deprecated, Zoho canonical | `CLAUDE.md` | Line referencing Zoho Mail SMTP |
| Odoo 19 (not 18) | `CLAUDE.md` | "Stack: Odoo CE 19.0" |
| .net domains deprecated | `CLAUDE.md` | "Domain: insightpulseai.com (.net is deprecated)" |
| Plane deprecated | `CLAUDE.md` | "Deprecated: Plane (all)" |

**TODO Items** (where evidence is missing):
- [ ] Document authoritative Finance PPM seed source (Excel → generator → XML flow)
- [ ] Create canonical parity report location (currently scattered across `config/ee_parity/` and `docs/parity/`)
- [ ] Consolidate deployment documentation (38 files need mapping to canonical sources)

---

**Changelog**:
- **2026-02-12**: Initial framework definition based on existing CI infrastructure analysis
