# Contributing to Odoo CE

Thank you for your interest in contributing! This document provides guidelines
for contributing to this Odoo CE/OCA-aligned repository.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Module Development](#module-development)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
  - [Command Line Checkout](#checkout-and-manual-merge-via-command-line)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).
By participating, you are expected to uphold this code.

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose
- Git with submodule support
- Node.js 20+ (for frontend/tooling)

### Quick Setup

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce

# Install pre-commit hooks
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg

# Start development stack
docker compose up -d

# Verify setup
./scripts/validate-spec-kit.sh
./scripts/validate-continue-config.sh
```

---

## Development Setup

### 1. Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Pre-commit Hooks

We use pre-commit for code quality. **This is mandatory.**

```bash
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit run --all-files  # Verify setup
```

### 3. IDE Configuration

**VS Code** (recommended):
- Install Python, Pylance, and Continue extensions
- Use workspace settings from `.vscode/settings.json`

**PyCharm**:
- Configure interpreter from `.venv`
- Enable OCA-style inspections

---

## Contribution Workflow

We follow a **spec-driven development** workflow:

### 1. Create a Spec Bundle

Before any significant work, create a spec bundle:

```bash
mkdir -p spec/my-feature
touch spec/my-feature/{constitution,prd,plan,tasks}.md
```

Fill in:
- `constitution.md` - Non-negotiable rules for this feature
- `prd.md` - Product requirements and user stories
- `plan.md` - Implementation plan with files to change
- `tasks.md` - Checkbox task list

### 2. Branch Naming

Use conventional branch names:

```
feat/short-description
fix/issue-number-description
docs/what-changed
refactor/area-changed
```

### 3. Development Cycle

```bash
# 1. Create feature branch
git checkout -b feat/my-feature

# 2. Make changes following the plan
# 3. Run pre-commit hooks
pre-commit run --all-files

# 4. Commit with conventional message
git commit -m "feat(scope): add feature description"

# 5. Push and create PR
git push -u origin feat/my-feature
```

---

## Coding Standards

### CE/OCA-Only Policy

**This repository is strictly CE/OCA-only.** We do not use:

- ❌ Odoo Enterprise modules
- ❌ IAP (In-App Purchase) features
- ❌ Proprietary odoo.com services
- ❌ odoo.com marketing links in code

Our CI will **fail your build** if Enterprise dependencies are detected.

### Python Style

We follow PEP 8 with OCA conventions:

```python
# Good: OCA-style imports
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# Good: Model definition
class MyModel(models.Model):
    _name = 'my.module.model'
    _description = 'My Model Description'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

    @api.depends('field1', 'field2')
    def _compute_result(self):
        for record in self:
            record.result = record.field1 + record.field2
```

### Line Length

- Python: 88 characters (Black default)
- XML: 120 characters
- JavaScript: 80 characters

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Module | `lowercase_snake` | `ipai_expense` |
| Model | `lowercase.dot` | `ipai.expense.report` |
| Field | `lowercase_snake` | `total_amount` |
| Method | `lowercase_snake` | `_compute_total` |
| Class | `PascalCase` | `ExpenseReport` |

---

## Module Development

### Module Structure (OCA Standard)

```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── data.xml
├── demo/
│   └── demo.xml
├── static/
│   └── description/
│       ├── icon.png
│       └── index.html
├── readme/
│   ├── DESCRIPTION.rst
│   ├── USAGE.rst
│   ├── CONFIGURE.rst
│   └── CONTRIBUTORS.rst
├── tests/
│   ├── __init__.py
│   └── test_my_model.py
└── README.rst (auto-generated)
```

### Manifest Requirements

```python
{
    'name': 'My Module',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Brief description',
    'description': '',  # Use readme/ folder instead
    'author': 'InsightPulseAI, Odoo Community Association (OCA)',
    'website': 'https://github.com/jgtolentino/odoo-ce',
    'license': 'AGPL-3',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
```

### README Generation

We use OCA's auto-generated README. Create fragments in `readme/`:

```
readme/
├── DESCRIPTION.rst    # What does this module do?
├── USAGE.rst          # How to use it?
├── CONFIGURE.rst      # Configuration steps
├── CONTRIBUTORS.rst   # Who contributed?
└── CREDITS.rst        # Acknowledgements
```

Run `pre-commit run oca-gen-addon-readme --all-files` to generate `README.rst`.

---

## Testing

### Unit Tests

```python
# tests/test_my_model.py
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMyModel(TransactionCase):

    def setUp(self):
        super().setUp()
        self.MyModel = self.env['my.module.model']

    def test_create_record(self):
        record = self.MyModel.create({'name': 'Test'})
        self.assertEqual(record.name, 'Test')

    def test_validation_error(self):
        with self.assertRaises(ValidationError):
            self.MyModel.create({'name': ''})
```

### Running Tests

```bash
# Run all tests for a module
odoo-bin -d test_db -i my_module --test-enable --stop-after-init

# Run specific test
odoo-bin -d test_db -i my_module --test-tags my_module.test_my_model
```

### CI Testing

Tests run automatically on PR via GitHub Actions. Ensure all tests pass before requesting review.

---

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def calculate_total(self, lines, tax_rate=0.12):
    """Calculate total amount with tax.

    Args:
        lines: List of line items with 'amount' field
        tax_rate: Tax rate as decimal (default: 0.12)

    Returns:
        float: Total amount including tax

    Raises:
        ValidationError: If lines is empty
    """
    pass
```

### Spec Documentation

For significant features, maintain the spec bundle:

- Update `tasks.md` as you complete work
- Document deviations from `plan.md`
- Keep `constitution.md` rules current

---

## Pull Request Process

### PR Checklist

Before submitting:

- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] Tests pass locally
- [ ] Spec bundle is complete (if applicable)
- [ ] No Enterprise/IAP dependencies
- [ ] Conventional commit messages used
- [ ] Documentation updated

### PR Template

```markdown
## Summary
Brief description of changes

## Spec Reference
`spec/<slug>/` (if applicable)

## Changes
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed

## Screenshots
(if UI changes)
```

### Review Process

1. Create PR against `main` branch
2. Ensure CI checks pass (all-green-gates)
3. Request review from maintainers
4. Address feedback
5. Squash and merge when approved

### Checkout and Manual Merge via Command Line

If you cannot use the merge button or an automatic merge cannot be performed, you can
perform a manual merge on the command line.

> **Note:** These steps are not applicable if the base branch is protected.

**Step 1:** Clone the repository or update your local repository with the latest changes.

```bash
git pull origin main
```

**Step 2:** Switch to the head branch of the pull request.

```bash
git checkout <pr-branch-name>
```

**Step 3:** Merge the base branch into the head branch.

```bash
git merge main
```

**Step 4:** Fix any conflicts and commit the result.

```bash
# After resolving conflicts in your editor:
git add <resolved-files>
git commit -m "fix: resolve merge conflicts with main"
```

See [Resolving a merge conflict using the command line](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line) for detailed conflict resolution instructions.

**Step 5:** Push the changes.

```bash
git push -u origin <pr-branch-name>
```

**Example:** For a PR from branch `feat/add-expense-ocr`:

```bash
git pull origin main
git checkout feat/add-expense-ocr
git merge main
# Resolve any conflicts...
git add .
git commit -m "fix: resolve merge conflicts with main"
git push -u origin feat/add-expense-ocr
```

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no logic change
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Adding tests
- `ci`: CI/CD changes
- `chore`: Maintenance tasks (see below for scope conventions)

#### Chore Scope Conventions (OCA-style)

| Scope | When to Use |
|-------|-------------|
| `chore(oca):` | OCA layer: submodules, `oca.lock.json`, `oca-aggregate.yml`, pins |
| `chore(repo):` | Repo-wide maintenance (docs regen, formatting, housekeeping) |
| `chore(ci):` | Workflows, gating, pre-commit, drift checks |
| `chore(deps):` | Python/Node deps, devcontainer, toolchain pins |
| `chore(deploy):` | Docker compose, nginx, env templates, infra docs |

See [docs/OCA_CHORE_SCOPE.md](docs/OCA_CHORE_SCOPE.md) for full conventions including PR templates and verification gates.

Example:
```
feat(expense): add OCR receipt scanning

- Integrate PaddleOCR for receipt text extraction
- Add vendor normalization for PH merchants
- Include confidence scoring

Closes #123
Spec: expense-automation
```

---

## Questions?

- Open a [GitHub Issue](https://github.com/jgtolentino/odoo-ce/issues)
- Check existing [Discussions](https://github.com/jgtolentino/odoo-ce/discussions)
- Review [OCA Guidelines](https://odoo-community.org/page/contributing)

---

*Thank you for contributing to Odoo CE!*
