---
name: Odoo Module Architecture
description: Create, scaffold, slim, or restructure Odoo 18 CE modules, manifests, and addon layout. Use when building new ipai_* modules or auditing module structure.
---

# Odoo Module Architecture

## Purpose

Guide module creation, manifest correctness, and addon path layout for Odoo 18 CE.

## When to use

- Creating a new `ipai_*` module
- Fixing or auditing `__manifest__.py`
- Deciding whether something should be a module vs configuration
- Scaffolding module directory structure
- Reviewing addon inclusion/exclusion for the Docker image

## Inputs or assumptions

- Odoo 18 CE only (no Enterprise)
- Custom modules live in `addons/ipai/`
- OCA modules live in `addons/oca/`
- Vendor Odoo lives in `vendor/odoo/`

## Source priority

1. Local project structure (`addons/`, `__manifest__.py` files)
2. Odoo 18 CE official documentation
3. OCA guidelines

## Workflow

1. Check if CE configuration solves the need → stop
2. Check if an OCA 18.0 module exists → install it
3. Check if an existing `ipai_*` handles this → extend it
4. Only then create `ipai_<domain>_<feature>`
5. If heavy logic (AI/OCR/agent) → keep outside Odoo entirely

## Module structure

```
addons/ipai/ipai_<domain>_<feature>/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── <model>.py
├── views/
│   └── <model>_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── <model>_security.xml
├── data/
│   └── <data>.xml
├── static/
│   └── description/
│       └── icon.png          # 128x128 PNG for app grid
├── tests/
│   ├── __init__.py
│   └── test_<feature>.py
└── README.rst                # OCA-style, optional
```

## Manifest required fields

```python
{
    "name": "Human-readable name",
    "version": "18.0.1.0.0",        # Odoo version prefix
    "category": "Category",
    "summary": "One-line summary",
    "author": "InsightPulse AI",
    "license": "LGPL-3",
    "depends": ["base"],             # Explicit, minimal
    "data": [
        "security/ir.model.access.csv",
        "views/model_views.xml",
    ],
    "installable": True,
    "application": False,            # True only for top-level apps
}
```

## Manifest rules

- `version` must start with `18.0.`
- `depends` must list only modules available in CE + OCA, never EE
- `license` must be `LGPL-3` or `AGPL-3`
- `installable: False` for deprecated modules (removes from Apps list)
- `auto_install` only for glue modules that should activate when all deps are present
- `post_load` only for WSGI-level hooks (rare)

## Addon path rules

- Odoo does NOT recurse into subdirectories for addon discovery
- Each OCA repo root is a separate `addons_path` entry
- `addons_path` is generated at Docker build time from repos on disk
- Never flatten OCA repos into a single directory

## Output format

Module scaffold with all required files, manifest, and security stubs.

## Verification

- `__manifest__.py` parses without error
- All files listed in `data` key exist on disk
- `security/ir.model.access.csv` has entries for every model
- Module installs: `odoo-bin -d test_<module> -i <module> --stop-after-init --no-http`

## Anti-patterns

- Creating a module when CE configuration suffices
- Duplicating OCA functionality in `ipai_*`
- Missing `security/ir.model.access.csv` (causes silent access denial)
- Using `application: True` for utility/glue modules
- Hardcoding `addons_path` instead of generating from disk layout
