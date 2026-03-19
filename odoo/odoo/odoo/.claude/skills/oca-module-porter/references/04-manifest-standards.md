# OCA Manifest Standards

Source: https://github.com/OCA/maintainer-tools/blob/master/template/module/__manifest__.py

---

## Complete OCA Manifest Template

```python
# License: LGPL-3 or any later version (https://www.gnu.org/licenses/lgpl)
{
    # ==========================================
    # REQUIRED fields
    # ==========================================
    "name": "Module Human-Readable Name",
    "version": "19.0.1.0.0",          # {odoo_ver}.{major}.{minor}.{patch}.{fix}
    "author": "Author Name, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/{repo-name}",
    "license": "LGPL-3",              # OCA default; AGPL-3 for web-facing modules
    "category": "Specific/Category",
    "depends": ["base"],              # List module technical names

    # ==========================================
    # STRONGLY RECOMMENDED fields
    # ==========================================
    "summary": """
        One-line module description. Used in README.rst and App Store.
        Keep it under 80 characters.
    """,
    "development_status": "Beta",     # Alpha | Beta | Production/Stable | Mature
    "maintainers": ["github_username"],  # GitHub usernames

    # ==========================================
    # Data / Assets
    # ==========================================
    "data": [
        # Load order matters! Security first, then data, then views
        "security/ir.model.access.csv",
        "security/module_name_security.xml",
        "data/module_name_data.xml",
        "views/module_name_views.xml",
        "views/module_name_menus.xml",
        "report/module_name_report.xml",
    ],
    "demo": [
        "data/module_name_demo.xml",
    ],

    # Assets (15.0+)
    "assets": {
        "web.assets_backend": [
            "module_name/static/src/js/widget.js",
            "module_name/static/src/scss/style.scss",
        ],
        "web.assets_qweb": [
            "module_name/static/src/xml/template.xml",
        ],
    },

    # ==========================================
    # Optional installation flags
    # ==========================================
    "installable": True,
    "auto_install": False,
    "application": False,             # True only for full applications (top-level menu)

    # ==========================================
    # External dependencies (optional)
    # ==========================================
    "external_dependencies": {
        "python": ["requests", "PyPDF2"],   # pip package names
        "bin": ["wkhtmltopdf"],             # system binary names
    },
}
```

---

## Version Numbering

Format: `{odoo_version}.{major}.{minor}.{patch}.{fix}`

| Segment | Meaning | Example |
|---------|---------|---------|
| `odoo_version` | Odoo major version | `19.0` |
| `major` | Breaking changes | `1` |
| `minor` | New features | `0` |
| `patch` | Bug fixes | `0` |
| `fix` | Hotfixes | `0` |

**Rules**:
- Reset to `{TO_VERSION}.1.0.0` on every new Odoo version migration
- First release of a new port: `{TO_VERSION}.1.0.0`
- Bug fix: increment last segment: `19.0.1.0.1`
- New feature: `19.0.1.1.0`
- Breaking change: `19.0.2.0.0`

---

## Author Field Format

```python
# CORRECT: Always append OCA
"author": "First Author, Second Author, Odoo Community Association (OCA)",

# WRONG: Missing OCA
"author": "First Author",
```

---

## License Values

| License | Use Case |
|---------|----------|
| `LGPL-3` | Default for most OCA modules |
| `AGPL-3` | Modules with web-facing/SaaS components |
| `OEEL-1` | Odoo Enterprise (never used in OCA) |

---

## development_status Values

| Value | Meaning | Default? |
|-------|---------|----------|
| `Alpha` | Under development, not for production | No |
| `Beta` | Pre-production, possible instability | YES (default if missing) |
| `Production/Stable` | Production-ready | No |
| `Mature` | Multi-version, multi-maintainer, actively maintained | No |

**Upgrade requirements**:
- Beta -> Stable: 2 peer reviews + 5-day review period; module must only depend on Stable/Mature modules
- Stable -> Mature: Module must have survived at least one major version port; maintained by multiple parties

---

## website Field

```python
# Format: always point to OCA GitHub repo for OCA modules
"website": "https://github.com/OCA/{repo-name}",

# Examples:
"website": "https://github.com/OCA/server-tools",
"website": "https://github.com/OCA/account-financial-tools",
```

The `oca-fix-manifest-website` pre-commit hook validates and fixes this field automatically.

---

## category Field

Common OCA categories:

```
Accounting/Accounting
Accounting/Expenses
Accounting/Payment
Base Setup
CRM
Discuss
eCommerce
Email Marketing
Human Resources/Attendances
Human Resources/Employees
Human Resources/Leaves
Human Resources/Payroll
Inventory/Delivery
Manufacturing
Point of Sale
Project
Purchase
Sales/Sales
Warehouse
Website
```

---

## depends Field Rules

- Only list DIRECT dependencies (not transitive)
- Use technical module names (not display names)
- Always include `base` if inheriting from `BaseModel`
- Do NOT depend on Enterprise modules (`sale_subscription`, `account_accountant`, etc.)
- For OCA modules: depend on the module's technical name as found in its `__manifest__.py`

---

## data Load Order

Critical: files load in the order listed. Follow this order:
1. Security groups (`security/module_groups.xml`)
2. Security access rights (`security/ir.model.access.csv`)
3. Security record rules (`security/module_security.xml`)
4. Data files (`data/module_data.xml`)
5. Views (`views/model_views.xml`)
6. Menu items (`views/module_menus.xml`)
7. Reports (`report/model_report.xml`)

---

## assets Field (15.0+)

Common asset bundles:

```python
"assets": {
    # Backend (web client)
    "web.assets_backend": [...],

    # Frontend (website/portal)
    "web.assets_frontend": [...],

    # QWeb templates for backend
    "web.assets_qweb": [...],

    # Tests
    "web.assets_tests": [...],
    "web.qunit_suite_tests": [...],
}
```
