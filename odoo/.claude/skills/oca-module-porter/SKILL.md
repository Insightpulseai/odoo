---
name: oca-module-porter
description: "OCA module porting specialist. Port OCA Odoo modules between versions using oca-port CLI, apply OCA quality standards (pre-commit, manifest, README), run acceptance tests, and generate OCA-compliant commits and PRs. Actions: port, migrate, check, validate, test, commit, pr. Triggers: 'port module', 'migrate OCA', 'oca-port', 'port addon', 'migrate 16.0 to 17.0', 'port to 19.0', 'OCA migration', 'module migration checklist'. Supports: 14.0, 15.0, 16.0, 17.0, 18.0, 19.0."
version: "1.0.0"
tags: [odoo, oca, migration, porting, pre-commit, maintainer-tools]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# OCA Module Porter

Specialist skill for porting OCA Odoo modules from one version to another using official OCA tooling.
Covers the complete workflow: selection → automated porting → quality checks → testing → commit → PR.

## When to Use This Skill

- Porting an OCA module from version X to version Y (e.g., 18.0 → 19.0)
- Applying OCA quality standards to a migrated module
- Validating a ported module against OCA pre-commit requirements
- Generating OCA-compliant manifest, README, and commit messages
- Running acceptance tests after a port
- Submitting upstream PRs to OCA repositories

## How to Use (Prompt Patterns)

- "Port the `server_environment` module from OCA/server-tools 18.0 to 19.0"
- "Run oca-port on `account_statement_import_base`, check quality, generate commit"
- "Apply OCA pre-commit hooks to the ported `base_tier_validation` module"
- "Generate the README for `mail_tracking` using oca-gen-addon-readme"
- "Create an OCA-compliant PR description for the 19.0 migration of `queue_job`"
- "Validate the manifest of `web_environment_ribbon` against OCA standards"

---

## Deterministic Porting Workflow

### Phase 1: Setup and Validation

```bash
# Install oca-port (one-time)
pip3 install oca-port

# Verify installation
oca-port --version

# Set environment variables
export GITHUB_TOKEN="<your-github-token>"  # Required for GitHub API
export MODULE="server_environment"
export REPO="server-tools"
export FROM_VERSION="18.0"
export TO_VERSION="19.0"
```

### Phase 2: Automated Port (oca-port CLI)

```bash
# Dry-run first — shows what would happen without making changes
oca-port origin/${FROM_VERSION} origin/${TO_VERSION} ${MODULE} --verbose --dry-run

# Effective port — creates working branch automatically
oca-port origin/${FROM_VERSION} origin/${TO_VERSION} ${MODULE} --verbose

# Non-OCA organization or non-standard branches:
oca-port origin/main origin/18.0-mig \
  --source-version=${FROM_VERSION} \
  --target-version=${TO_VERSION} \
  --upstream-org=OCA \
  ./${MODULE} --verbose

# Fetch remote branches automatically:
oca-port origin/${FROM_VERSION} origin/${TO_VERSION} ${MODULE} --fetch
```

**oca-port creates a branch named**: `{TO_VERSION}-mig-{MODULE}` (or destination branch if specified)

**oca-port automatically**:
1. Compares git histories between source and target branches
2. Identifies commits not yet ported, grouped by Pull Request
3. Creates the working branch from the target branch
4. Proposes interactive porting of each missing PR/commit
5. Calls odoo-module-migrator for automated code transformations (v0.18+)

### Phase 3: Code Migration (odoo-module-migrator)

When oca-port cannot fully automate, or for manual migration paths:

```bash
# Install
pip3 install odoo-module-migrator

# Migrate code automatically
odoo-module-migrate \
  --directory /path/to/repo \
  --modules ${MODULE} \
  --init-version-name ${FROM_VERSION} \
  --target-version-name ${TO_VERSION}

# With git format-patch (single module only)
odoo-module-migrate \
  --directory /path/to/repo \
  --modules ${MODULE} \
  --init-version-name ${FROM_VERSION} \
  --target-version-name ${TO_VERSION} \
  --format-patch \
  --remote origin
```

**Output message types**:
- `INFO`: Automatically changed — no action required
- `WARNING`: Check this — may need manual fix
- `ERROR`: Must fix manually — module will not work otherwise

### Phase 4: Manual Migration Checklist

Apply the version-specific checklist below. Universal steps (all versions):

```bash
# 1. Bump version in __manifest__.py
# Change: 'version': '18.0.1.0.0'  ->  'version': '19.0.1.0.0'

# 2. Remove old migration scripts
rm -rf ${MODULE}/migrations/

# 3. Run pre-commit to fix formatting
pre-commit run --all-files
# Expected: black, isort, prettier pass; ignore pylint at this stage

# 4. Commit formatting changes separately
git add .
git commit -m "[IMP] ${MODULE}: pre-commit formatting (black, isort, prettier)"
```

### Phase 5: Quality Validation

```bash
# Install pre-commit
pip3 install pre-commit
pre-commit install

# Run all hooks
pre-commit run --all-files

# Generate README from fragments
oca-gen-addon-readme \
  --repo-name=${REPO} \
  --branch=${TO_VERSION} \
  --addon-dir=${MODULE}

# Fix manifest website field
oca-fix-manifest-website ${MODULE}/__manifest__.py
```

### Phase 6: Acceptance Testing

```bash
# 1. Python syntax check (all .py files)
python3 -m py_compile ${MODULE}/**/*.py && echo "PASS: No syntax errors"

# 2. Module loads in Odoo shell
./scripts/odoo_shell.sh -c "env['ir.module.module'].search([('name', '=', '${MODULE}')])"

# 3. Module installs without errors
./scripts/odoo_module_install.sh ${MODULE}

# 4. Run module tests (if test suite exists)
pytest --odoo-database=odoo_test --addons-path=. -p no:warnings ${MODULE}/tests/

# 5. Check manifest version
grep "'version'" ${MODULE}/__manifest__.py
# Expected: 'version': '19.0.1.0.0'
```

### Phase 7: Evidence Capture

```bash
TIMESTAMP=$(date +"%Y%m%d-%H%M%z")
EVIDENCE_DIR="web/docs/evidence/${TIMESTAMP}/oca-port-${MODULE}"
mkdir -p "${EVIDENCE_DIR}/logs"

oca-port origin/${FROM_VERSION} origin/${TO_VERSION} ${MODULE} 2>&1 \
  | tee "${EVIDENCE_DIR}/logs/port.log"

python3 -m py_compile ${MODULE}/**/*.py 2>&1 \
  | tee "${EVIDENCE_DIR}/logs/syntax.log" && echo "PASS" >> "${EVIDENCE_DIR}/logs/syntax.log"

pre-commit run --all-files 2>&1 | tee "${EVIDENCE_DIR}/logs/precommit.log"
```

### Phase 8: OCA-Compliant Commit

```bash
git add addons/oca/${REPO}/${MODULE}/

git commit -m "[MIG] ${MODULE}: Migration to ${TO_VERSION}

- Tool: oca-port CLI
- From: ${FROM_VERSION} -> ${TO_VERSION}
- Pre-commit: passed
- Tests: smoke tests passed (load + install)
- Evidence: ${EVIDENCE_DIR}"
```

### Phase 9: Upstream PR to OCA

```bash
git push origin ${TO_VERSION}-mig-${MODULE}

gh pr create \
  --repo OCA/${REPO} \
  --base ${TO_VERSION} \
  --title "[${TO_VERSION}][MIG] ${MODULE}: Migration to ${TO_VERSION}" \
  --body "$(cat <<'EOF'
## Migration Summary

Port of MODULE from FROM to TO.

## Changes

- Bumped version to TO.1.0.0
- Applied automated migration via oca-port
- Applied odoo-module-migrator transformations
- Fixed pre-commit hooks (black, isort, prettier)
- Updated README via oca-gen-addon-readme

## Testing

- [x] Python syntax check passed
- [x] Module loads in Odoo shell
- [x] Module installs without errors
- [ ] Full test suite (if applicable)

Closes #ISSUE_NUMBER
EOF
)"
```

---

## OCA Module Structure (Required)

```
MODULE_NAME/
|-- __init__.py
|-- __manifest__.py         # Required: name, version, author, license, depends, data
|-- readme/
|   |-- DESCRIPTION.rst     # Required for oca-gen-addon-readme
|   |-- USAGE.rst           # Highly recommended
|   |-- CONTRIBUTORS.rst    # Highly recommended
|   |-- INSTALL.rst         # Optional
|   |-- CONFIGURE.rst       # Optional
|   |-- HISTORY.rst         # Optional (changelog)
|   |-- newsfragments/      # Optional (towncrier fragments)
|-- models/
|   |-- __init__.py
|   |-- model_name.py
|-- views/
|   |-- model_name_views.xml
|   |-- model_name_menus.xml
|-- security/
|   |-- ir.model.access.csv
|   |-- model_name_security.xml
|-- data/
|   |-- model_name_data.xml
|-- tests/
|   |-- __init__.py
|   |-- test_model_name.py
|-- static/
|   |-- description/
|   |   |-- icon.png        # Module icon (128x128)
```

---

## OCA Manifest Standards

```python
{
    'name': 'Module Human-Readable Name',
    'version': '19.0.1.0.0',          # MANDATORY: {odoo_version}.{major}.{minor}.{patch}.{fix}
    'author': 'Author Name, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/{repo-name}',
    'license': 'LGPL-3',              # LGPL-3 is OCA default
    'category': 'Specific/Category',
    'summary': 'One-line module description (used in README)',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/model_name_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'development_status': 'Beta',     # Alpha | Beta | Production/Stable | Mature
    'maintainers': ['github_username'],
}
```

**Version format rules**:
- `{odoo_version}.{major}.{minor}.{patch}.{fix}`
- Reset to `{TO_VERSION}.1.0.0` on each migration
- `development_status` defaults to `Beta` if not set

---

## OCA Pre-Commit Configuration

Standard `.pre-commit-config.yaml` for OCA repos (17.0+):

```yaml
repos:
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-bugbear]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        name: prettier (yaml, json, md)
        types_or: [yaml, json, markdown]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/OCA/maintainer-tools
    rev: 0.1.39
    hooks:
      - id: oca-gen-addon-readme
        args: ['--addons-dir', '.', '--if-source-missing', 'ignore']
      - id: oca-update-pre-commit-excluded-addons
      - id: oca-fix-manifest-website

  - repo: https://github.com/OCA/odoo-pre-commit-hooks
    rev: v0.2.20
    hooks:
      - id: oca-checks-odoo-module
      - id: oca-checks-po
        args: ["--fix"]

  - repo: https://github.com/OCA/pylint-odoo
    rev: v8.0.0
    hooks:
      - id: pylint_odoo
        args: [--rcfile=.pylintrc, --exit-zero]
```

**Hook groups summary**:
- `black` — Python code formatting
- `isort` — Python import sorting
- `flake8` — PEP8 linting
- `prettier` — YAML/JSON/Markdown formatting
- `oca-gen-addon-readme` — Generates README.rst from fragments
- `oca-checks-odoo-module` — OCA-specific XML/manifest checks
- `oca-checks-po` — Translation file validation
- `pylint_odoo` — Odoo-specific Python linting

**Disabling checks**:
```python
# pylint: disable=missing-docstring
some_code  # noqa: E501
some_code  # isort: skip
# fmt: off
unformatted_block()
# fmt: on
```

---

## Version-Specific Migration Checklists

### Migrating to 18.0

**XML changes**:
```bash
# Replace 'tree' view type with 'list' everywhere in Python/JS/XML
# KEEP XML IDs containing 'tree' in their name to avoid downstream breakage
# Use Odoo's upgrade script:
<path_to_odoo>/odoo-bin upgrade_code --addons-path <path_to_module>
```

**Python changes**:
```python
# BEFORE (17.0)
self.user_has_groups('base.group_user')
self.check_access_rights('read')
self.check_access_rule('read')

# AFTER (18.0)
self.env.user.has_group('base.group_user')
self.check_access('read')     # single unified method
```

**JS test changes**:
```javascript
// BEFORE (17.0)
{ trigger: '.o_field_widget', extra_trigger: '.some_class' }

// AFTER (18.0) - split into two steps
{ trigger: '.some_class' },
{ trigger: '.o_field_widget' },
```

### Migrating to 17.0

**Python changes**:
```python
# BEFORE (16.0) - name_get override
def name_get(self):
    return [(rec.id, f"{rec.code} - {rec.name}") for rec in self]

# AFTER (17.0) - _compute_display_name
def _compute_display_name(self):
    for rec in self:
        rec.display_name = f"{rec.code} - {rec.name}"

# BEFORE (16.0) - module hooks use cr
def pre_init_hook(cr):
    ...

# AFTER (17.0) - hooks use env
def pre_init_hook(env):
    ...

# BEFORE (16.0)
from odoo.tools import get_resource_path
path = get_resource_path('module', 'path/to/file')

# AFTER (17.0)
from odoo.tools import file_path
path = file_path('module:path/to/file')
```

**View/XML changes**:
- `attrs` attribute: now use `invisible`, `readonly`, `required` directly
- `states` attribute: replaced by `invisible`
- `column_invisible` in tree: now uses `optional` attribute on columns

### Migrating to 16.0

**Initial steps**:
```bash
git checkout -b ${TO_VERSION}-mig-${MODULE} origin/${FROM_VERSION}
git format-patch --keep-subject --stdout origin/16.0..origin/15.0 -- ${MODULE} \
  | git am -3 --keep [--ignore-whitespace]
pre-commit run -a
git add .
git commit -m "[IMP] ${MODULE}: black, isort, prettier"
```

**Python/API changes**:
- Remove `groups_id` from `ir.config_parameter` records
- Replace `group_ids` with `groups` in field definitions
- Replace `colors` attribute with `decoration-*` in tree views

### Migrating to 15.0

**JavaScript/Assets changes**:
```python
# BEFORE (14.0) - assets in __manifest__.py qweb key
'qweb': ['static/src/xml/template.xml']

# AFTER (15.0) - assets declared under 'assets' key
'assets': {
    'web.assets_backend': [
        'module/static/src/js/widget.js',
        'module/static/src/scss/style.scss',
    ],
    'web.assets_qweb': [
        'module/static/src/xml/template.xml',
    ],
}
```

---

## README Fragment Files

Directory structure inside each module:

```
MODULE/readme/
|-- DESCRIPTION.rst     # REQUIRED: What the module does (no section title)
|-- USAGE.rst           # Recommended: How to use it
|-- CONTRIBUTORS.rst    # Recommended: List of contributors
|-- INSTALL.rst         # Optional: Installation requirements
|-- CONFIGURE.rst       # Optional: Configuration steps
|-- ROADMAP.rst         # Optional: Future plans
|-- HISTORY.rst         # Optional: Changelog
|-- CREDITS.rst         # Optional: Financing acknowledgments
|-- newsfragments/      # Optional: Towncrier changelog fragments
```

**Fragment rules**:
- Each file is plain RST without section titles (body text only)
- Use paragraphs, lists, tables, images
- `HISTORY.rst` is auto-generated by towncrier if using `newsfragments/`

**Generate README**:
```bash
oca-gen-addon-readme \
  --repo-name=server-tools \
  --branch=19.0 \
  --addon-dir=server_environment \
  [--org-name=OCA]
```

Produces `README.rst` in module root — PyPI compliant.

---

## OCA Testing Requirements

**Test file location**: `MODULE/tests/`

**Standard test structure**:
```python
# tests/__init__.py
from . import test_module_name

# tests/test_module_name.py
from odoo.tests.common import TransactionCase

class TestModuleName(TransactionCase):
    """Test cases for module_name"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Setup fixtures

    def test_basic_functionality(self):
        """Test basic module functionality"""
        # Test implementation
        self.assertTrue(True)
```

**Test case classes**:
- `TransactionCase` — Rolls back after each test (most common)
- `HttpCase` — For website/portal/controller tests
- `SavepointCase` — Faster, no rollback between tests

**Running tests**:
```bash
# Via Odoo CLI
./odoo-bin -d odoo_test --test-enable -i MODULE --stop-after-init

# Via pytest-odoo
pytest --odoo-database=odoo_test --addons-path=. ${MODULE}/tests/

# With coverage
pytest --odoo-database=odoo_test \
  --cov=${MODULE} \
  --cov-report=html \
  ${MODULE}/tests/
```

**Coverage expectations**:
- OCA expects >75% coverage for Production/Stable modules
- Coverage is checked automatically in CI via Codecov/Coveralls
- Modules marked Alpha/Beta have lower coverage requirements

---

## OCA Commit Message Format

```
[TAG] module_name: Short description (max 72 chars)

Optional longer body explaining motivation and context.
```

**Tags**:
| Tag | Meaning |
|-----|---------|
| `[MIG]` | Migration to new Odoo version |
| `[ADD]` | New feature or module |
| `[IMP]` | Improvement to existing feature |
| `[FIX]` | Bug fix |
| `[REM]` | Removal of feature/file |
| `[REF]` | Refactoring (no behavior change) |
| `[MOV]` | File/code moved |
| `[REL]` | Release commit |
| `[UPD]` | Update to non-code files (README, translations) |

**Migration commit sequence example**:
```
[IMP] server_environment: black, isort, prettier
[UPD] server_environment: bump version to 19.0.1.0.0
[FIX] server_environment: fix deprecated API calls
[MIG] server_environment: Migration to 19.0
```

---

## OCA PR Description Template

```markdown
## Summary

Port of `MODULE_NAME` from VERSION_FROM to VERSION_TO.

## Changes Made

- Bumped version to VERSION_TO.1.0.0
- Applied automated migration via `oca-port`
- Applied `odoo-module-migrator` code transformations
- Fixed pre-commit quality checks (black, isort, prettier)
- Updated README.rst via `oca-gen-addon-readme`
- [Any manual changes and why]

## Testing

- [x] Python syntax check (`python3 -m py_compile`) passed
- [x] Module loads in Odoo shell
- [x] Module installs without errors
- [ ] Full test suite run (if applicable)

## Notes

<!-- Describe any breaking changes, manual steps required, or known issues -->

Closes #ISSUE_NUMBER (if exists)
```

---

## OCA Module Maturity Levels

| Level | `development_status` | Requirements |
|-------|---------------------|--------------|
| Alpha | `Alpha` | Development/testing; not for production |
| Beta | `Beta` | Pre-production; potential instability. Default if unset |
| Stable | `Production/Stable` | Requires 2 peer reviews + 5-day review period; only depends on Stable/Mature |
| Mature | `Mature` | Survives multiple major versions; actively maintained by multiple parties |

---

## PR Review Process

- Merge requires: **2 positive reviews** within 5 days (or 2 after 5 days)
- At least **1 review from PSC member** or OCA Core Maintainer with write access
- When 2 approvals: `approved` label is set
- When PR is >= 5 days old with approvals: `ready to merge` label is set
- oca-github-bot handles label automation

---

## PR Blacklist (oca-port-pr)

When a PR/commit should not be ported:

```bash
# Blacklist specific PRs for a branch/module
oca-port-pr blacklist OCA/REPO#250,OCA/REPO#251 TARGET_VERSION MODULE_NAME

# With reason
oca-port-pr blacklist OCA/REPO#250 TARGET_VERSION MODULE_NAME \
  --reason "Refactored in TARGET_VERSION, not needed anymore"
```

---

## Tools Summary

| Tool | Install | Purpose |
|------|---------|---------|
| `oca-port` | `pip3 install oca-port` | Primary migration tool — git history analysis and porting |
| `oca-port-pr` | (included in oca-port) | Manage PR blacklists for oca-port |
| `odoo-module-migrate` | `pip3 install odoo-module-migrator` | Automated Python/XML code transformations |
| `pre-commit` | `pip3 install pre-commit` | Run all quality hooks |
| `oca-gen-addon-readme` | (via maintainer-tools pre-commit hook) | Generate README.rst from fragments |
| `oca-fix-manifest-website` | (via maintainer-tools pre-commit hook) | Fix manifest website key |
| `pylint-odoo` | `pip3 install pylint-odoo` | Odoo-specific Python linting |
| `pytest-odoo` | `pip3 install pytest-odoo` | Run Odoo tests via pytest |
