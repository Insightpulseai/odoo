# Odoo CE Deployment & CI/CD Documentation

This directory contains documentation for deploying and maintaining the Odoo 18 CE instance with OCA modules.

## 📚 Documentation

### Testing
- **[../TESTING_ODOO_18.md](../TESTING_ODOO_18.md)** - Odoo 18 Testing Guide ⭐
  - Official Odoo 18 testing patterns
  - `TransactionCase` examples
  - Test tags and filtering
  - JavaScript testing (HOOT)
  - `bin/odoo-tests.sh` usage
  - Best practices

### CI/CD
- **[OCA_CI_GUARDIAN.md](./OCA_CI_GUARDIAN.md)** - OCA CI Guardian agent documentation
  - Enterprise contamination prevention
  - OCA compliance enforcement
  - Automated workflow fixes
  - Troubleshooting guide

## 🚀 Quick Start

### Running CI Checks Locally

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Check for Enterprise dependencies
grep -R "enterprise\|web_studio\|documents\|iap" addons/ || echo "✅ Clean"

# Run module tests (CI script)
./scripts/ci/run_odoo_tests.sh

# Run Odoo 18 tests (recommended)
./bin/odoo-tests.sh

# Run specific module
./bin/odoo-tests.sh ipai_expense

# Run with tags
./bin/odoo-tests.sh ipai_expense /ipai_expense
```

### CI Workflows

#### ci-odoo-ce.yml (Guardrails)
- Enterprise module blocking
- odoo.com URL detection
- Repository structure validation

#### ci-odoo-oca.yml (OCA Guardian)
- **Test Matrix:** Unit Tests, Integration Tests, All Tests
- **Coverage Reporting:** Code coverage with HTML reports
- **Performance Testing:** Module installation timing and DB size
- **OCA Compliance:** Full compliance checking
- **OpenUpgrade Compatibility:** Migration script validation
- **Static Analysis:** Enterprise detection and linting

## 🛡️ Guardrails

### 1. No Enterprise Modules
**Rule:** Community Edition only - no Enterprise dependencies

**Blocked:**
- `web_studio`, `documents`, `iap`
- Enterprise imports: `from odoo.addons.*_enterprise`
- Manifest dependencies on Enterprise modules

**Allowed:**
- All CE modules
- OCA community modules
- Custom modules based on CE

### 2. No odoo.com Links
**Rule:** Replace odoo.com with InsightPulse or OCA links

**Why:** Branding and independence from Odoo proprietary platforms (self-hosted Odoo CE 19)

### 3. OCA Conventions
**Rule:** Follow OCA repository structure and best practices

**Enforced:**
- Standard directory layout
- Valid `__manifest__.py` files
- Pre-commit hooks
- Migration scripts (if applicable)

## 📦 Repository Structure

```
odoo-ce/
├── addons/                    # Custom InsightPulse modules
├── oca/                       # OCA community modules
├── .github/
│   └── workflows/
│       ├── ci-odoo-ce.yml    # Core guardrails
│       └── ci-odoo-oca.yml   # OCA CI Guardian
├── agents/
│   ├── odoo_oca_ci_fixer.yaml        # Agent spec
│   └── prompts/
│       └── odoo_oca_ci_fixer_system.txt
├── scripts/
│   └── ci/
│       └── run_odoo_tests.sh
├── docs/
│   └── deployment/
│       ├── README.md          # This file
│       └── OCA_CI_GUARDIAN.md
└── openupgrade_scripts/       # Optional migration scripts
```

## 🔧 Tools & Scripts

### scripts/ci/run_odoo_tests.sh
```bash
# Run all tests
./scripts/ci/run_odoo_tests.sh

# Run unit tests only
TEST_TAGS="/unit" ./scripts/ci/run_odoo_tests.sh

# Run integration tests only
TEST_TAGS="/integration" ./scripts/ci/run_odoo_tests.sh

# Run specific modules
ODOO_MODULES=ipai_docs,ipai_expense ./scripts/ci/run_odoo_tests.sh

# Run with coverage reporting
WITH_COVERAGE=true COVERAGE_HTML=true ./scripts/ci/run_odoo_tests.sh

# Debug mode with specific tags
LOG_LEVEL=debug TEST_TAGS="/unit" ./scripts/ci/run_odoo_tests.sh

# Full example with all options
DB_NAME=test_db \
ODOO_MODULES=ipai_docs,ipai_expense \
TEST_TAGS="/unit" \
WITH_COVERAGE=true \
COVERAGE_HTML=true \
LOG_LEVEL=test \
./scripts/ci/run_odoo_tests.sh
```

### scripts/gen_repo_tree.sh
```bash
# Regenerate repository tree in spec.md
./scripts/gen_repo_tree.sh
```

## 🤖 Agents

### odoo-oca-ci-fixer
**Purpose:** Automatically fix CI/CD issues and enforce OCA compliance

**Triggers:**
- CI workflow failure
- Enterprise dependency detected
- OCA compliance violation

**Capabilities:**
- Diagnose workflow failures
- Generate corrected workflows
- Fix manifest dependencies
- Create PRs with fixes

**Usage:**
See [OCA_CI_GUARDIAN.md](./OCA_CI_GUARDIAN.md) for details

## 📋 Checklists

### Before Committing New Module
- [ ] No Enterprise dependencies in `__manifest__.py`
- [ ] No Enterprise imports in Python files
- [ ] No odoo.com URLs in code
- [ ] Pre-commit hooks pass
- [ ] Module installs successfully
- [ ] Tests pass (if present)

### Before Merging PR
- [ ] All CI checks green
- [ ] No Enterprise contamination detected
- [ ] Repository structure validated
- [ ] Code reviewed
- [ ] Documentation updated (if needed)

### Before Deploying
- [ ] CI/CD pipeline successful
- [ ] Staging environment tested
- [ ] Database backup created
- [ ] Rollback plan prepared
- [ ] Deployment window scheduled

## 🆘 Troubleshooting

### CI Fails: "Enterprise dependency detected"
1. Check the error output for specific file/line
2. Review `__manifest__.py` dependencies
3. Search for Enterprise imports: `grep -R "enterprise" addons/`
4. Replace with CE alternative or remove

### CI Fails: "Repo tree out of date"
```bash
./scripts/gen_repo_tree.sh
git add spec.md
git commit -m "chore: update repo tree"
```

### Tests Fail Locally but Pass in CI
- Check Python version (should be 3.10)
- Check PostgreSQL version (should be 15)
- Verify addons path includes `oca/`
- Check for missing system dependencies

### Module Won't Install
- Verify manifest syntax: `python -c "import ast; ast.parse(open('__manifest__.py').read())"`
- Check dependencies are installed
- Review Odoo logs for detailed error

## 📞 Support

**Issues:** Open issue in GitHub
**Mattermost:** #odoo-dev, #ci-alerts
**Documentation:** `/docs/deployment/`

---

**Last Updated:** 2025-11-23
**Maintained by:** InsightPulse AI DevOps
