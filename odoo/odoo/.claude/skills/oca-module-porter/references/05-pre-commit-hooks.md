# OCA Pre-Commit Hooks Reference

Sources:
- https://github.com/OCA/maintainer-tools/blob/master/.pre-commit-hooks.yaml
- https://github.com/OCA/odoo-pre-commit-hooks
- https://pypi.org/project/oca-odoo-pre-commit-hooks/

---

## Standard OCA .pre-commit-config.yaml (17.0+)

```yaml
# .pre-commit-config.yaml — Standard OCA template for 17.0+
repos:
  # Python formatting
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        # Excludes __init__.py by default

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3

  # Python linting
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        additional_dependencies:
          - flake8-bugbear
          - flake8-coding
          - flake8-debugger
          - pep8-naming

  # Web asset formatting
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        name: prettier (yaml, json, markdown, xml)
        types_or: [yaml, json, markdown, xml]
        # Note: XML formatting applies to view files too

  # General file quality
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: mixed-line-ending
        args: ['--fix=lf']

  # OCA maintainer-tools hooks
  - repo: https://github.com/OCA/maintainer-tools
    rev: 0.1.39
    hooks:
      - id: oca-gen-addon-readme
        args:
          - '--addons-dir'
          - '.'
          - '--if-source-missing'
          - 'ignore'
      - id: oca-update-pre-commit-excluded-addons
      - id: oca-fix-manifest-website

  # OCA Odoo-specific hooks
  - repo: https://github.com/OCA/odoo-pre-commit-hooks
    rev: v0.2.20
    hooks:
      - id: oca-checks-odoo-module
      - id: oca-checks-po
        args: ["--fix"]

  # setuptools-odoo (or whool for newer versions)
  - repo: https://github.com/acsone/setuptools-odoo
    rev: 3.1.9
    hooks:
      - id: setuptools-odoo-make-default
        args: ['--addons-dir', '.']

  # Pylint for Odoo
  - repo: https://github.com/OCA/pylint-odoo
    rev: v8.0.0
    hooks:
      - id: pylint_odoo
        args:
          - --rcfile=.pylintrc
          - --exit-zero
        additional_dependencies:
          - pylint-odoo
```

---

## OCA Maintainer-Tools Hooks Detail

| Hook ID | Purpose |
|---------|---------|
| `oca-gen-addon-readme` | Generates `README.rst` from `readme/` fragments |
| `oca-update-pre-commit-excluded-addons` | Updates excluded addons list |
| `oca-fix-manifest-website` | Fixes/validates the `website` key in manifest |
| `oca-gen-addons-table` | Generates addons table for repo README |
| `oca-towncrier` | Runs towncrier to generate changelog |

---

## OCA Odoo Pre-Commit Hooks Detail

Repository: https://github.com/OCA/odoo-pre-commit-hooks

| Hook ID | Checks |
|---------|--------|
| `oca-checks-odoo-module` | Module-level checks (accepts `__manifest__.py` paths or module paths) |
| `oca-checks-po` | Translation file (`.po`) validation and fixing |

**oca-checks-odoo-module checks**:
- `file-not-used` — Files created but not referenced in `__manifest__.py`
- `manifest-syntax-error` — Python syntax errors in manifest
- `prefer-readme-rst` — Warns if README is not RST format
- `csv-duplicate-record-id` — Duplicate IDs in CSV files
- `use-header-comments` — Missing copyright header comments
- `weblate-component-too-long` — Translation component names too long
- `prefer-env-translation` — For 18.0+: replace `_('text')` with `self.env._('text')`

**Configuring checks**:
```bash
# Environment variables
OCA_HOOKS_ENABLE=file-not-used,manifest-syntax-error
OCA_HOOKS_DISABLE=prefer-readme-rst

# Or via config file: .oca_hooks.cfg
[oca-hooks]
disable = prefer-readme-rst
enable = file-not-used,manifest-syntax-error
```

**Manual invocation**:
```bash
oca-checks-odoo-module --disable=prefer-readme-rst ./MODULE/__manifest__.py
oca-checks-odoo-module --enable=file-not-used ./MODULE/
```

---

## Pylint Odoo (.pylintrc)

Standard `.pylintrc` for OCA modules:

```ini
[MASTER]
load-plugins=pylint_odoo

[ODOO]
# Odoo version
odoo_version=19.0

[MESSAGES CONTROL]
# Disable checks that generate too many false positives
disable=
    # Common disables in OCA:
    C0114,  # missing-module-docstring
    C0115,  # missing-class-docstring
    C0116,  # missing-function-docstring
    W0212,  # protected-access (common in Odoo)
    E0401,  # import-error (Odoo framework imports)

[FORMAT]
max-line-length = 88  # Match black
```

---

## Black Configuration (pyproject.toml)

```toml
[tool.black]
line-length = 88
target-version = ['py310', 'py311', 'py312']
```

---

## isort Configuration (pyproject.toml)

```toml
[tool.isort]
profile = "black"
multi_line_output = 3
force_sort_within_sections = true
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "ODOO", "ADDONS", "FIRSTPARTY", "LOCALFOLDER"]
known_odoo = ["odoo"]
known_addons = []
default_section = "THIRDPARTY"
skip_glob = ["**/__init__.py"]
```

---

## Suppressing Individual Checks

```python
# pylint
some_code  # pylint: disable=missing-docstring
some_code  # noqa: pylint(missing-docstring)

# flake8
some_long_line  # noqa: E501
from module import *  # noqa: F401,F403

# isort
import something  # isort: skip
# isort: skip_file

# black
# fmt: off
unformatted = {
  'not':   'formatted'
}
# fmt: on
```

---

## Running Pre-Commit

```bash
# Install pre-commit
pip3 install pre-commit

# Install hooks in repo
pre-commit install
pre-commit install --hook-type commit-msg

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run oca-gen-addon-readme --all-files

# Run on specific files
pre-commit run --files module_name/models/model.py

# Update hook versions
pre-commit autoupdate

# Skip hooks (use sparingly)
SKIP=pylint_odoo git commit -m "message"
git commit -m "message" --no-verify  # Skip ALL hooks — not recommended
```

---

## Expected Pre-Commit Output (Healthy State)

```
isort....................................................................Passed
black....................................................................Passed
flake8...................................................................Passed
prettier.................................................................Passed
trailing whitespace......................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
check json...............................................................Passed
oca-gen-addon-readme.....................................................Passed
oca-checks-odoo-module...................................................Passed
pylint_odoo..............................................................Passed
```
