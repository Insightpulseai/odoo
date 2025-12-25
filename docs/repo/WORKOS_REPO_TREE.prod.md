# WorkOS Production Repository Tree

**Generated**: 2025-12-25 16:52 UTC
**Production SHA**: 74219604437336cd68131d79c232eb1578b5a7d1
**Server**: root@159.223.75.148
**Repository**: /opt/odoo-ce

## Module Structure

```
addons/ipai_workos_affine
├── __init__.py
└── __manifest__.py

addons/ipai_workos_blocks
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   └── block.py
├── security
│   └── ir.model.access.csv
├── static
│   └── src
│       ├── js
│       └── scss
└── views
    └── block_views.xml

addons/ipai_workos_canvas
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   └── canvas.py
├── security
│   └── ir.model.access.csv
├── static
│   └── src
│       └── js
└── views
    └── canvas_views.xml

addons/ipai_workos_collab
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   └── comment.py
├── security
│   └── ir.model.access.csv
└── views
    └── comment_views.xml

addons/ipai_workos_core
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   ├── page.py
│   ├── space.py
│   └── workspace.py
├── security
│   └── ir.model.access.csv
├── static
│   └── src
│       ├── js
│       └── scss
└── views
    ├── menu_views.xml
    ├── page_views.xml
    ├── space_views.xml
    └── workspace_views.xml

addons/ipai_workos_db
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   ├── database.py
│   ├── property.py
│   └── row.py
├── security
│   └── ir.model.access.csv
├── static
│   └── src
│       ├── js
│       └── scss
└── views
    └── database_views.xml

addons/ipai_workos_search
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   └── search.py
├── security
│   └── ir.model.access.csv
└── views
    └── search_views.xml

addons/ipai_workos_templates
├── __init__.py
├── __manifest__.py
├── data
│   └── default_templates.xml
├── models
│   ├── __init__.py
│   └── template.py
├── security
│   └── ir.model.access.csv
└── views
    └── template_views.xml

addons/ipai_workos_views
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   └── view.py
├── security
│   └── ir.model.access.csv
├── static
│   └── src
│       ├── js
│       └── scss
└── views
    └── view_views.xml

addons/ipai_platform_approvals
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   └── approval_mixin.py
├── security
│   └── ir.model.access.csv
└── views
    └── approval_views.xml

addons/ipai_platform_audit
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   └── audit_mixin.py
├── security
│   └── ir.model.access.csv
└── views
    └── audit_views.xml

addons/ipai_platform_permissions
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   └── permission.py
├── security
│   └── ir.model.access.csv
└── views
    └── permission_views.xml

addons/ipai_platform_theme
├── __init__.py
├── __manifest__.py
├── static
│   └── src
│       └── scss
└── views
    └── assets.xml

addons/ipai_platform_workflow
├── __init__.py
├── __manifest__.py
├── models
│   ├── __init__.py
│   └── workflow_mixin.py
├── security
│   └── ir.model.access.csv
└── views
    └── workflow_views.xml
```

## Statistics

- **Total Modules**: 14 (9 WorkOS + 5 Platform)
- **Installed Modules**: 11
- **Uninstalled Modules**: 3 (ipai_platform_approvals, ipai_platform_theme, ipai_platform_workflow)
- **Total Python Files**: 24 models
- **Total XML Views**: 17 view files
- **Total Security Files**: 14 access control files
