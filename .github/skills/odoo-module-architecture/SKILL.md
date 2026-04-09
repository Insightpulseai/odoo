---
name: Odoo Module Architecture
description: Use when creating, scaffolding, slimming, or restructuring Odoo 18 CE modules, manifests, and addon layout.
---

# Odoo Module Architecture

## When to use

- Creating a new `ipai_*` module
- Fixing or auditing `__manifest__.py`
- Deciding whether something should be a module vs configuration
- Scaffolding module directory structure
- Reviewing addon inclusion/exclusion for the Docker image

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

## Decision checklist

1. Does CE configuration solve this? → Do not create a module
2. Does an OCA 18.0 module exist? → Install it instead
3. Does an existing `ipai_*` handle this? → Extend it
4. Is this truly custom? → Create `ipai_<domain>_<feature>`
5. Is this heavy logic (AI/OCR/agent)? → Keep outside Odoo entirely

## Manifest rules

- `version` must start with `18.0.`
- `depends` must list only modules available in CE + OCA, never EE
- `license` must be `LGPL-3` or `AGPL-3`
- `installable: False` for deprecated modules (removes from Apps list)
- `auto_install` only for glue modules that should activate when all deps are present
- `post_load` only for WSGI-level hooks (rare, e.g., `ipai_aca_proxy`)

## Addon path rules

- Odoo does NOT recurse into subdirectories for addon discovery
- Each OCA repo root is a separate `addons_path` entry
- `addons_path` is generated at Docker build time from repos on disk
- Never flatten OCA repos into a single directory
