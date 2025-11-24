# Odoo CE/OCA CI Guardian

**Agent ID:** `odoo-oca-ci-fixer`
**Version:** 1.0.0
**Status:** Active

---

## Overview

The Odoo CE/OCA CI Guardian is an autonomous agent that ensures all Odoo 18 CE code complies with OCA (Odoo Community Association) best practices and prevents Enterprise module contamination.

## Purpose

This agent automatically:
- ✅ Enforces OCA repository conventions
- ✅ Detects and blocks Enterprise module dependencies
- ✅ Ensures OpenUpgrade compatibility
- ✅ Maintains CI/CD pipeline health
- ✅ Auto-generates fixes for failing workflows

## CI Checks

### 1. Enterprise Contamination Detection

**What it checks:**
- Python imports from `odoo.addons.*_enterprise`
- Manifest dependencies on Enterprise modules
- Keywords: `web_studio`, `documents`, `iap`
- URLs pointing to odoo.com (warning only)

**Example violations:**
```python
# ❌ BLOCKED
from odoo.addons.web_studio import ...
from odoo.addons.documents import ...

# ❌ BLOCKED in __manifest__.py
'depends': ['web_studio', 'base']

# ✅ ALLOWED
from odoo import models, fields
'depends': ['base', 'account']
```

### 2. OCA Compliance

**What it checks:**
- Repository structure follows oca-addons-repo-template
- Manifest files are valid
- Pre-commit hooks configured
- Python syntax validation

**Enforced structure:**
```
odoo-ce/
├── addons/           # Custom modules
├── oca/              # OCA modules
├── .github/
│   └── workflows/
│       ├── ci-odoo-ce.yml       # Existing checks
│       └── ci-odoo-oca.yml      # OCA CI Guardian
├── scripts/
│   └── ci/
│       └── run_odoo_tests.sh
└── openupgrade_scripts/  # Optional migration scripts
```

### 3. Module Testing

**What it tests:**
- Python syntax validation
- Module installation on Odoo 18 CE
- Unit tests (if present)
- PostgreSQL integration

**Test matrix:**
- Python: 3.10
- Odoo: 18.0 CE
- PostgreSQL: 15

### 4. OpenUpgrade Compatibility (Optional)

For repositories with migration scripts:
- Validates `openupgrade_scripts/` structure
- Checks import compatibility with OpenUpgradeLib

---

## Workflows

### ci-odoo-oca.yml

**Triggers:**
- Push to: `main`, `18.0`, `18.0-*`, `claude/*`
- Pull requests to: `main`, `18.0`, `18.0-*`

**Jobs:**

1. **Lint & Static Checks**
   - Pre-commit hooks
   - Enterprise contamination detection
   - odoo.com URL warnings
   - Python syntax validation

2. **Unit & Odoo Tests**
   - PostgreSQL service
   - Odoo 18 CE installation
   - Module installation tests
   - Test execution with coverage

3. **OpenUpgrade Smoke**
   - Migration script validation (18.0 branch only)

4. **Repository Structure**
   - Validate repo tree is up-to-date

---

## How to Use

### Manual Invocation

When CI fails or you need OCA compliance check:

```bash
# 1. Generate repository snapshot
./scripts/ci/run_odoo_tests.sh

# 2. Review agent recommendations
# The agent will analyze:
# - Failing CI logs
# - Repository structure
# - Module manifests
# - Workflow configurations

# 3. Apply fixes
# The agent will provide ready-to-commit patches
```

### Automatic Invocation

The agent auto-activates on:
- ❌ CI workflow failures
- ⚠️ Enterprise dependency detected
- ⚠️ OCA compliance violations
- ⚠️ Test failures

### GitHub Integration

On CI failure, the agent can:
1. Comment on PR with diagnosis
2. Create fix branch with patches
3. Open PR with corrected workflows
4. Notify in Mattermost/Slack

---

## Agent Configuration

### Permissions

The agent can:
- **Read:**
  - `addons/**`
  - `oca/**`
  - `.github/workflows/**`
  - `requirements.txt`
  - `openupgrade_scripts/**`

- **Edit:**
  - `.github/workflows/**`
  - `scripts/ci/**`
  - `**/__manifest__.py` (fix dependencies)

### Skills

- Workflow generation and repair
- OCA convention enforcement
- Enterprise detection algorithms
- OpenUpgrade compatibility validation
- GitHub API integration

### Primary Sources

The agent consults:
- [Odoo 18.0 Documentation](https://www.odoo.com/documentation/18.0/)
- [OCA Maintainer Tools](https://github.com/OCA/maintainer-tools)
- [OCA GitHub Bot](https://github.com/OCA/oca-github-bot)
- [OCB (Odoo Community Backports)](https://github.com/OCA/OCB)
- [OpenUpgrade](https://github.com/OCA/OpenUpgrade)
- [OCA Addons Repo Template](https://github.com/OCA/oca-addons-repo-template)

---

## Common Fixes

### Fix 1: Enterprise Dependency in Module

**Problem:**
```python
# addons/my_module/__init__.py
from odoo.addons.web_studio import api
```

**Agent fix:**
```python
# Remove or replace with CE alternative
from odoo import api
```

### Fix 2: Workflow Missing Enterprise Check

**Problem:**
```yaml
# .github/workflows/ci.yml missing enterprise check
```

**Agent fix:**
```yaml
- name: Enterprise contamination check
  run: |
    if grep -R "enterprise\|web_studio\|documents\|iap" addons/; then
      echo "::error::Enterprise dependency detected"
      exit 1
    fi
```

### Fix 3: Incorrect Test Configuration

**Problem:**
```bash
# Missing addons-path
odoo -i my_module --test-enable
```

**Agent fix:**
```bash
odoo -i my_module --test-enable --addons-path=addons,oca
```

---

## Troubleshooting

### Q: Agent says "Enterprise found" but I don't see it

**A:** Check for:
- Commented code with enterprise imports
- Test fixtures importing enterprise
- Dependencies in `__manifest__.py`
- Inherited code from enterprise modules

### Q: Tests pass locally but fail in CI

**A:** Common causes:
- Missing system dependencies
- PostgreSQL version mismatch
- Missing OCA modules in CI
- Different Odoo versions

**Solution:**
```yaml
# Add to workflow
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y wkhtmltopdf
```

### Q: How do I exclude a file from enterprise check?

**A:** Add to `.github/workflows/ci-odoo-oca.yml`:
```yaml
enterprise_imports=$(grep -Rn "enterprise" addons --exclude="legacy_migration.py" || true)
```

---

## Maintenance

### Updating Agent

The agent auto-updates via:
```bash
git pull origin main
# Agent spec in: agents/odoo_oca_ci_fixer.yaml
# System prompt in: agents/prompts/odoo_oca_ci_fixer_system.txt
```

### Disabling Agent

Temporarily disable:
```yaml
# .github/workflows/ci-odoo-oca.yml
# Comment out or delete file
```

Permanently disable:
```bash
git rm .github/workflows/ci-odoo-oca.yml
git commit -m "chore: disable OCA CI Guardian"
```

---

## Contributing

To improve the agent:

1. **Report issues:** If agent blocks valid code
2. **Suggest enhancements:** Additional OCA checks
3. **Submit PRs:** Workflow improvements

---

## References

- Agent Spec: `agents/odoo_oca_ci_fixer.yaml`
- System Prompt: `agents/prompts/odoo_oca_ci_fixer_system.txt`
- Workflow: `.github/workflows/ci-odoo-oca.yml`
- Test Script: `scripts/ci/run_odoo_tests.sh`

**Maintainer:** InsightPulse AI DevOps
**Last Updated:** 2025-11-23
