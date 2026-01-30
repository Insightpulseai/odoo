# -*- coding: utf-8 -*-
{
    "name": "IPAI Web Icons - Fluent",
    "version": "19.0.1.0.0",
    "category": "Themes/Icons",
    "summary": "Microsoft Fluent System Icons for consistent Odoo + React UI",
    "description": """
IPAI Web Icons - Fluent
=======================

Provides Microsoft Fluent System Icons for use throughout Odoo CE backend,
ensuring visual consistency with React Fluent UI applications.

Icon Library
------------
Uses a curated subset of Microsoft Fluent System Icons optimized for:
- Menu icons
- Action buttons
- Status indicators
- Form field icons

Icon Variants
-------------
- Regular (outlined)
- Filled (solid)
- Sizes: 16px, 20px, 24px

Usage in Views
--------------
Use icon classes in Odoo views:
    <button icon="fluent-home-24"/>
    <field name="icon" widget="char" placeholder="fluent-document-20"/>

Or reference SVG directly:
    /ipai_web_icons_fluent/static/src/icons/fluent/home-24-regular.svg

Icon Mapping
------------
Common Odoo icons are mapped to Fluent equivalents:
- fa-home → fluent-home
- fa-user → fluent-person
- fa-cog → fluent-settings
- fa-file → fluent-document
- etc.

Source
------
Icons from: https://github.com/microsoft/fluentui-system-icons
License: MIT
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "web",
    ],
    "data": [
        "views/assets.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_web_icons_fluent/static/src/scss/icons.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
