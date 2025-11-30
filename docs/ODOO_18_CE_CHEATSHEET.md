# Odoo 18 CE / OCA Cheat Sheet (Smart Delta Edition)

This cheat sheet captures core Odoo 18 CE conventions + Smart Delta / OCA-first rules for autonomous module development.

---

## 1. Odoo Model Base Classes

All Odoo ORM models ultimately derive from `BaseModel` internally, but you always inherit from one of three public base classes:

1. **`models.Model`**
   - Persistent, database-backed model.
   - Normal business objects (e.g. `res.partner`, `account.move`).
   - Creates/extends a real PostgreSQL table.

2. **`models.TransientModel`**
   - Temporary / wizard models.
   - Records stored in DB but automatically vacuumed.
   - Use for assistants, wizards, temporary configuration, one-shot actions.

3. **`models.AbstractModel`**
   - Abstract super-class / mixin.
   - No database table created directly.
   - Used to share reusable logic, methods, and fields across concrete models.

> **Rule for agents:** Pick the _minimal_ base class that fits the use case:
> - Persisted business object → `Model`
> - Short-lived wizard / dialog → `TransientModel`
> - Reusable behavior with no standalone data → `AbstractModel`

---

## 2. Python Naming Conventions

### 2.1 Class Names (Python)

- Use **PascalCase (UpperCamelCase)** for Python classes:

```python
from odoo import models, fields


class AccountMove(models.Model):
    _name = "account.move"
    _description = "Journal Entry"
```

> Old API (`osv.osv`, snake_case classes) is **deprecated** and must not be used in new code.

### 2.2 Model Technical Name (`_name`)

* Use **dot notation + singular** for the `_name` string:

  * ✅ `res.partner`, `sale.order`, `account.move`
  * ❌ `res.partners`, `sale.orders`, `saleS.orderS`

Rules:

* Singular noun.
* All lowercase.
* Namespaced by app/module where appropriate (`module.model`).

### 2.3 Variable Naming

Inside Odoo Python modules:

* **Recordset variables:** PascalCase (so they stand out):

```python
Partner = self.env["res.partner"]
Moves = self.env["account.move"].search(domain)
```

* **Local/common variables:** snake_case:

```python
partner_ids = Partner.ids
move_count = len(Moves)
```

* **Constants / global vars:** UPPER_SNAKE_CASE:

```python
DEFAULT_LIMIT = 100
```

---

## 3. `__manifest__.py` – Module Descriptor

Every module **must** have a `__manifest__.py` file at its root. Without this, Odoo will not detect or load the module.

### 3.1 Core Responsibilities

1. **Identity & Metadata**

   * `name`: Human-readable title.
   * `version`: Often prefixed with target Odoo version, e.g. `18.0.1.0.0`.
   * `summary`: One-line subtitle.
   * `description`: Longer explanation.
   * `category`, `author`, `company`, `maintainer`, `website`, `license`.

2. **Dependencies & Load Order**

   * `depends`: **Required** list of module technical names this module extends.
   * Ensures models/views from dependencies are loaded before this module.
   * Missing dependencies cause installation/update errors (`KeyError`, missing views, etc.).

   ```python
   "depends": [
       "base",
       "web",
       "portal",
   ],
   ```

3. **Content to Load**

   * `data`: XML/CSV/YAML files loaded on install and on update (`-i`/`-u`).

     * Views, menus, security (`ir.model.access.csv`), actions, configuration.
     * Load security early in the list.

   * `demo`: Demo data, only loaded when DB is created with demo enabled.

   * `assets`: JS/CSS/assets to be added to web bundles.

4. **Behavior Flags & Extra Requirements**

   * `application`: If `True`, shows up as an app in Odoo UI.
   * `installable`: If `False`, hidden from install screen.
   * `auto_install`: Automatically installs when all listed dependencies are present.
   * `external_dependencies`: Python packages or system binaries required.

Example skeleton:

```python
{
    "name": "InsightPulse Finance PPM",
    "version": "18.0.1.0.0",
    "summary": "Finance PPM – BIR compliance & month-end automation",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": [
        "base",
        "account",
        "project",
        "portal",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/project_task_views.xml",
        "data/ppm_cron_jobs.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "ipai_finance_ppm/static/src/**/*",
        ],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": ["pycountry"],
        "bin": [],
    },
}
```

---

## 4. Standard Odoo Module Structure

At minimum:

```text
my_module/
  __init__.py
  __manifest__.py
  models/
    __init__.py
    *.py
  views/
    *.xml
  data/
    *.xml
    *.csv
```

### 4.1 Key Directories

1. **`models/`**

   * Python ORM classes:

     * `models.Model`
     * `models.TransientModel`
     * `models.AbstractModel`
   * Must contain `__init__.py`.

2. **`views/`**

   * XML views and actions:

     * Form views, tree views, kanban, search, etc.
     * Menus, window actions.
   * Usually named `*_views.xml`, `menu.xml`, etc.

3. **`data/`**

   * Initialization/configuration:

     * Security (groups, ir.model.access).
     * Cron jobs.
     * Default configuration records.

Other common directories:

* `controllers/` – HTTP routes and controllers.
* `static/` – web assets (JS/CSS/images).
* `report/` – QWeb reports, templates.
* `security/` – access rules and `ir.model.access.csv`.

---

## 5. Smart Delta – OCA-First Intelligent Customization

> **Goal:** Build custom "delta" modules for Odoo 18 CE that are:
>
> * OCA-compliant
> * Version-aware (Odoo 18 specific)
> * Generated and maintained by AI agents with a self-healing feedback loop.

### 5.1 Delta Modules (Examples)

* **`ipai_ce_cleaner`**

  * Hides Odoo Enterprise upsell elements.
  * Depends on `base_setup`, `web`.
  * Must not introduce Enterprise code contamination.

* **`ipai_portal_fix`**

  * Fixes `KeyError: website` in portal routes by correctly depending on `portal`/`website`, or guarding accesses.
  * Ensures manifest dependencies match actual usage.

### 5.2 Agent Roles

1. **Planning Agent**

   * Takes NL requirements → technical plan:

     * Models, fields, security, views, dependencies.
   * Checks if requirement can be solved via:

     * Native config or automations
     * OCA module reuse
     * Only then: new custom module.

2. **Coding Agent**

   * Generates Python (ORM) + XML using Odoo 18 rules.
   * Uses **RAG over Odoo 18 docs/changelog** to stay version-aware:

     * Prefers `check_access`, `has_access` over manual ACL logic.
     * Uses correct base class (`Model` / `TransientModel` / `AbstractModel`).
     * Follows naming/layout best practices.

3. **Quality Agent**

   * Runs **OCA tooling**:

     * `oca-odoo-pre-commit-hooks`
     * `pylint-odoo`
   * Enforces style, manifest integrity, ORM best practices.
   * Parses tool output and returns structured feedback for self-correction.

4. **Orchestrator Agent**

   * Coordinates Planning, Coding, and Quality.
   * Manages state: DRAFT → OCA_PASSED → CI_PASSED → READY.
   * Only opens PR / triggers external CI once **local OCA checks are green**.

---

## 6. OCA Compliance in the Loop

### 6.1 Tools

* **`oca-odoo-pre-commit-hooks`**

  * Enforces OCA code style conventions.
  * Checks manifests, imports, headers, etc.

* **`pylint-odoo`**

  * Static analysis specialized for Odoo modules:

    * Ensures ORM API usage is correct.
    * Flags anti-patterns and common mistakes.

### 6.2 Autonomous Self-Healing

1. Coding Agent generates code for the new or updated module.
2. Quality Agent runs OCA tools.
3. If any check fails:

   * Parse error logs into a structured object (per file, per rule).
   * Return this to the Coding Agent.
4. Coding Agent:

   * Adjusts code to fix each violation.
   * Re-runs local OCA checks.
5. Loop until:

   * All OCA checks pass with **no violations**.

> **Rule:** External CI (GitHub Actions, GitLab CI) only runs after the **local OCA gate is clean**.

---

## 7. CI/CD and Custom Image Deployment

### 7.1 Immutable Custom Image

* Build a Docker image that includes:

  * Odoo 18 CE core.
  * OCA modules (e.g. via git submodules).
  * Custom InsightPulse delta modules.
* Tag with semver and Odoo version, e.g. `ghcr.io/.../odoo-ce:18.0.0-ipai1`.

### 7.2 CI Steps (Typical)

1. **Build image**

   * Dockerfile using official Odoo 18 image as base or custom base.
2. **Spin up test container**

   * `docker run` with a test DB.
3. **Install/Update modules**

   * `odoo-bin -i <modules> --test-enable -d test_db --stop-after-init`
   * or `-u <modules>` for upgrades.
4. **Run tests**

   * Unit/integration tests as needed.
5. **Promotion**

   * Only push/tag image as `:prod` (or deploy) when tests pass.

### 7.3 Smart Delta Rule

* A delta is "deployment-ready" only when:

  1. OCA tools pass (local self-healing complete).
  2. Unit/integration tests pass in CI.
  3. Image builds successfully and can install/upgrade modules in a clean DB.

---

Use this cheat sheet as the **canonical reference** for agents and humans when designing or reviewing Odoo 18 CE / OCA customizations, especially in your Smart Delta autonomous workflows.
