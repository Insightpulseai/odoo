---
name: odoo19-module
description: Odoo 19 module manifest structure, all manifest fields, hooks, directory conventions, and module lifecycle
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/module.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Module Manifests

## Overview

The manifest file declares a Python package as an Odoo module and specifies
module metadata. It is a file called `__manifest__.py` containing a single
Python dictionary where each key specifies module metadata.

---

## Complete Manifest Example

```python
# __manifest__.py
{
    'name': 'My Custom Module',
    'version': '19.0.1.0.0',
    'summary': 'Short one-line description of the module',
    'description': """
        Extended description of the module.
        Can be multi-line reStructuredText.

        Features
        --------
        * Feature 1
        * Feature 2
    """,
    'author': 'My Company',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'category': 'Sales/Sales',
    'depends': [
        'base',
        'sale',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'views/my_model_views.xml',
        'views/my_model_menus.xml',
        'data/my_model_data.xml',
        'report/my_report.xml',
        'report/my_report_templates.xml',
        'wizards/my_wizard_views.xml',
    ],
    'demo': [
        'demo/my_model_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/**/*',
            'my_module/static/src/css/**/*',
            'my_module/static/src/xml/**/*',
        ],
        'web.report_assets_common': [
            'my_module/static/src/less/report_fonts.less',
        ],
    },
    'external_dependencies': {
        'python': ['requests', 'phonenumbers'],
        'bin': ['wkhtmltopdf'],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
```

---

## All Manifest Fields

### `name` (str, required)

The human-readable name of the module, displayed in the Apps menu:

```python
'name': 'Sales Commission Management',
```

### `version` (str)

Module version following semantic versioning rules. For Odoo modules, the
convention is to prefix with the Odoo major version:

```python
'version': '19.0.1.0.0',
```

Version format: `<odoo_version>.<major>.<minor>.<patch>`

### `description` (str)

Extended description in reStructuredText format:

```python
'description': """
    Sales Commission Management
    ===========================

    This module adds commission management to the sales workflow.

    Features
    --------
    * Automatic commission calculation
    * Commission reports
    * Multi-tier commission structures
""",
```

### `author` (str)

Name of the module author:

```python
'author': 'My Company, OCA',
```

### `website` (str)

Website URL for the module author:

```python
'website': 'https://github.com/OCA/sale-workflow',
```

### `license` (str, default: `LGPL-3`)

Distribution license for the module. Valid values:

| License | Description |
|---------|-------------|
| `GPL-2` | GNU General Public License v2 |
| `GPL-2 or any later version` | GPL v2+ |
| `GPL-3` | GNU General Public License v3 |
| `GPL-3 or any later version` | GPL v3+ |
| `AGPL-3` | GNU Affero General Public License v3 |
| `LGPL-3` | GNU Lesser General Public License v3 (default) |
| `Other OSI approved licence` | Other OSI-approved license |
| `OEEL-1` | Odoo Enterprise Edition License v1.0 |
| `OPL-1` | Odoo Proprietary License v1.0 |
| `Other proprietary` | Other proprietary license |

```python
'license': 'AGPL-3',
```

### `category` (str, default: `Uncategorized`)

Classification category within Odoo. Use existing categories when possible.
Hierarchies use `/` separator:

```python
'category': 'Sales/Sales',
```

Common categories:
- `Accounting/Accounting`
- `Sales/Sales`
- `Inventory/Inventory`
- `Human Resources/Employees`
- `Project/Project`
- `Website/Website`
- `Marketing/Marketing`
- `Hidden` (for technical modules)

Unknown categories are created on-the-fly. `Foo / Bar` creates category `Foo`
with child `Bar`, and sets `Bar` as the module's category.

### `depends` (list(str))

Odoo modules that must be loaded before this one. Dependencies are installed
and loaded in order before the module.

```python
'depends': ['base', 'sale', 'mail'],
```

**Important**: Module `base` is always installed in any Odoo instance, but you
must still specify it as a dependency to ensure your module is updated when
`base` is updated.

### `data` (list(str))

List of data files always installed or updated with the module. Paths are
relative to the module root directory:

```python
'data': [
    'security/ir.model.access.csv',
    'security/my_security.xml',
    'data/my_data.xml',
    'views/my_views.xml',
    'views/my_menus.xml',
    'report/my_reports.xml',
    'wizards/my_wizard.xml',
],
```

**File loading order matters**. Files are loaded in the order listed. Security
files should come first, then data, then views.

### `demo` (list(str))

List of data files only installed or updated in demonstration mode:

```python
'demo': [
    'demo/my_demo_data.xml',
    'demo/my_demo_partners.xml',
],
```

### `auto_install` (bool or list(str), default: `False`)

Controls automatic installation behavior:

**Boolean `True`**: Module is automatically installed when ALL dependencies
are installed. Used for "link modules" (synergetic integration between
independent modules):

```python
# sale_crm depends on sale + crm
# Auto-installs when both sale and crm are present
'depends': ['sale', 'crm'],
'auto_install': True,
```

**List of dependency names**: Module auto-installs when all listed dependencies
(a subset of `depends`) are installed. Remaining dependencies are auto-installed too:

```python
# Auto-install when 'sale' is installed; 'crm' will be auto-installed too
'depends': ['sale', 'crm'],
'auto_install': ['sale'],
```

**Empty list `[]`**: Module always auto-installs regardless of dependencies
(dependencies are auto-installed too):

```python
'auto_install': [],  # Always installed
```

### `external_dependencies` (dict)

Python and/or binary dependencies required for the module to be installed:

```python
'external_dependencies': {
    'python': ['requests', 'phonenumbers', 'xlsxwriter'],
    'bin': ['wkhtmltopdf', 'lessc'],
},
```

- **`python`**: List of Python module names to import. Module won't install if
  any import fails.
- **`bin`**: List of binary executable names. Module won't install if any
  binary is not found in the system PATH.

### `application` (bool, default: `False`)

Whether the module is a fully-fledged application (`True`) or a technical
module (`False`):

```python
'application': True,
```

Applications appear prominently in the Apps menu. Technical modules provide
extra functionality to existing applications.

### `assets` (dict)

Defines how static files are loaded in various asset bundles:

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/**/*',
        'my_module/static/src/css/backend.css',
        'my_module/static/src/xml/templates.xml',
    ],
    'web.assets_frontend': [
        'my_module/static/src/js/frontend/**/*',
        'my_module/static/src/css/frontend.css',
    ],
    'web.report_assets_common': [
        'my_module/static/src/less/report.less',
    ],
},
```

Common asset bundles:
- `web.assets_backend` - Backend (internal) assets
- `web.assets_frontend` - Frontend (website) assets
- `web.report_assets_common` - Report-specific assets
- `web.assets_common` - Shared assets (backend + frontend)

### `installable` (bool, default: `True`)

Whether users can install the module from the Web UI:

```python
'installable': True,
```

Set to `False` to hide the module from the Apps list (useful for deprecated
modules or modules not yet ready).

### `maintainer` (str)

Person or entity maintaining the module. Defaults to author if not specified:

```python
'maintainer': 'OCA',
```

### `active` (bool) -- DEPRECATED

Replaced by `auto_install`. Do not use.

---

## Module Hooks

Hooks are functions defined in the module's `__init__.py` that are called
at specific points in the module lifecycle.

### Hook Declaration in Manifest

```python
{
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
```

### Hook Implementations

```python
# __init__.py
from . import models
from . import wizards


def pre_init_hook(env):
    """Executed BEFORE the module's installation.

    Use for:
    - Checking prerequisites
    - Preparing the database for installation
    - Creating database structures that ORM cannot handle

    Args:
        env: Odoo environment
    """
    # Example: create a required database extension
    env.cr.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def post_init_hook(env):
    """Executed RIGHT AFTER the module's installation.

    Use for:
    - Setting initial data that depends on the module's models
    - Running one-time data migrations
    - Configuring system parameters

    Args:
        env: Odoo environment
    """
    # Example: set a default configuration
    env['ir.config_parameter'].set_param(
        'my_module.default_setting', 'value'
    )

    # Example: create initial records
    env['my.model'].create([
        {'name': 'Default Record 1', 'active': True},
        {'name': 'Default Record 2', 'active': True},
    ])


def uninstall_hook(env):
    """Executed AFTER the module's uninstallation.

    Use for:
    - Cleaning up data that won't be automatically removed
    - Removing system parameters
    - Reverting database changes made by hooks

    Args:
        env: Odoo environment
    """
    # Example: clean up system parameters
    env['ir.config_parameter'].search([
        ('key', 'like', 'my_module.%')
    ]).unlink()
```

**Important**: Only use hooks when setup/cleanup is extremely difficult or
impossible through the standard API.

---

## Directory Structure Conventions

### Standard Module Layout

```
my_module/
├── __init__.py              # Python package init
├── __manifest__.py          # Module manifest
├── controllers/             # HTTP controllers
│   ├── __init__.py
│   └── main.py
├── data/                    # Data files (loaded on install)
│   ├── my_data.xml
│   └── mail_templates.xml
├── demo/                    # Demo data files
│   └── my_demo.xml
├── i18n/                    # Translations
│   ├── my_module.pot        # Template for translations
│   ├── fr.po                # French translation
│   └── es.po                # Spanish translation
├── models/                  # Python model definitions
│   ├── __init__.py
│   ├── my_model.py
│   └── inherited_model.py
├── report/                  # Report definitions
│   ├── my_report.xml        # Report action + paper format
│   └── my_report_templates.xml  # QWeb templates
├── security/                # Access rights and rules
│   ├── ir.model.access.csv  # Access control list
│   └── security_rules.xml   # Record rules, groups
├── static/                  # Static web assets
│   ├── description/         # Module description assets
│   │   ├── icon.png         # Module icon (128x128)
│   │   └── index.html       # HTML description
│   └── src/                 # Source files
│       ├── css/
│       ├── js/
│       ├── img/
│       └── xml/             # OWL templates
├── tests/                   # Test files
│   ├── __init__.py
│   ├── test_my_model.py
│   └── common.py            # Test fixtures/helpers
├── views/                   # View definitions
│   ├── my_model_views.xml   # Form, list, search views
│   └── my_model_menus.xml   # Menu items and actions
└── wizards/                 # Transient models (wizards)
    ├── __init__.py
    ├── my_wizard.py
    └── my_wizard_views.xml
```

### `__init__.py` Files

Root `__init__.py`:
```python
from . import models
from . import controllers
from . import wizards
```

Sub-package `__init__.py` (e.g., `models/__init__.py`):
```python
from . import my_model
from . import inherited_model
```

---

## Module Naming Conventions

### For This Project (ipai_* modules)

Follow the pattern: `ipai_<domain>_<feature>`

```
ipai_finance_ppm       # Finance domain, PPM feature
ipai_ai_tools          # AI domain, tools feature
ipai_auth_oidc         # Auth domain, OIDC feature
ipai_slack_connector   # Slack integration connector
```

### OCA Naming Convention

```
<app>_<feature>        # e.g., sale_commission, hr_expense_advance
```

### Version Convention

For Odoo modules, prefix the version with the Odoo major version:

```python
'version': '19.0.1.0.0',  # Odoo 19, module version 1.0.0
```

---

## Data File Loading Order

The order of files in the `data` list matters. Follow this convention:

```python
'data': [
    # 1. Security (must come first -- models need access rights)
    'security/security_groups.xml',
    'security/ir.model.access.csv',
    'security/security_rules.xml',

    # 2. Data (reference data, sequences, parameters)
    'data/ir_sequence_data.xml',
    'data/mail_template_data.xml',
    'data/ir_cron_data.xml',

    # 3. Wizards (transient model views)
    'wizards/my_wizard_views.xml',

    # 4. Views (model views and menus)
    'views/my_model_views.xml',
    'views/inherited_views.xml',
    'views/my_menus.xml',

    # 5. Reports
    'report/my_report.xml',
    'report/my_report_templates.xml',
],
```

---

## Security Files

### Access Control List (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,my_module.group_manager,1,1,1,1
```

### Security Groups (XML)

```xml
<record id="group_manager" model="res.groups">
    <field name="name">My Module Manager</field>
    <field name="category_id" ref="base.module_category_sales_sales"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Record Rules (XML)

```xml
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: user sees own records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

---

## Module Philosophy (Project-Specific)

Follow the hierarchy: **Config > OCA > Delta (ipai_*)**

1. **Config**: Use built-in Odoo configuration first
2. **OCA**: Use vetted OCA community modules second
3. **Delta**: Create custom `ipai_*` modules only for truly custom needs

Only CE (Community Edition) modules are allowed. No Enterprise modules, no
odoo.com IAP.

---

## Common Patterns

### Minimal Module (Boilerplate)

```python
# __manifest__.py
{
    'name': 'My Module',
    'version': '19.0.1.0.0',
    'depends': ['base'],
    'author': 'My Company',
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
    'installable': True,
}
```

```python
# __init__.py
from . import models
```

```python
# models/__init__.py
from . import my_model
```

```python
# models/my_model.py
from odoo import fields, models

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
```

### Link Module (auto_install)

```python
# sale_project_link/__manifest__.py
{
    'name': 'Sale Project Link',
    'version': '19.0.1.0.0',
    'depends': ['sale', 'project'],
    'author': 'My Company',
    'license': 'LGPL-3',
    'auto_install': True,
    'data': [
        'views/sale_order_views.xml',
    ],
}
```

### Module with External Dependencies

```python
{
    'name': 'PDF Report Generator',
    'version': '19.0.1.0.0',
    'depends': ['base', 'web'],
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['weasyprint', 'cairocffi'],
        'bin': ['wkhtmltopdf'],
    },
    'data': [
        'views/report_views.xml',
    ],
}
```
