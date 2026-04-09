# Odoo Module Scaffold Ops Skill

## Purpose

Scaffold new Odoo modules via CLI. Covers odoo-bin scaffold, module structure generation, and naming conventions (ipai_<domain>_<feature>).

## Owner

odoo-cli-operator

## Preconditions

- Odoo CE 18.0 installed
- Target addons directory exists (addons/ipai/)
- Module naming follows ipai_<domain>_<feature> convention

## Covered Operations

### Scaffold Command

- `odoo-bin scaffold <module_name> <destination>` — generate module skeleton
- Generates: `__init__.py`, `__manifest__.py`, `controllers/`, `models/`, `views/`, `security/`, `demo/`, `static/`

### Naming Convention

- Pattern: `ipai_<domain>_<feature>`
- Examples: `ipai_finance_ppm`, `ipai_ai_tools`, `ipai_auth_oidc`, `ipai_bir_tax_compliance`
- Domain: business domain (finance, ai, auth, bir, hr, etc.)
- Feature: specific feature within the domain

### Post-Scaffold Customization

- Update `__manifest__.py` with correct version (18.0.x.y.z), license (LGPL-3), dependencies
- Add `ir.model.access.csv` to security/
- Follow model class attribute order per odoo18-coding.md
- Add to addons path if not already present

## Generated Structure

```
ipai_<domain>_<feature>/
  __init__.py
  __manifest__.py
  controllers/
    __init__.py
    controllers.py
  models/
    __init__.py
    models.py
  views/
    views.xml
    templates.xml
  security/
    ir.model.access.csv
  demo/
    demo.xml
  static/
    description/
      icon.png
```

## Disallowed Operations

- Creating modules outside addons/ipai/ (except addons/oca/ which is vendor)
- Creating modules without ipai_ prefix
- Creating modules that duplicate OCA module functionality (OCA-first rule)
- Creating modules with Enterprise dependencies

## Verification

- After scaffold: directory structure exists with all expected files
- __manifest__.py has version 18.0.x.y.z and license LGPL-3
- Module installs cleanly: `odoo-bin -d test_<module> -i <module> --stop-after-init`
