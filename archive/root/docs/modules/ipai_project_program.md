# ipai_project_program

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Program (parent project) + Implementation Modules (IM1/IM2) as child projects + Directory + seed loader

## Dependencies

- `project`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 6 |
| Menus | 7 |
| Actions | 4 |
| Data Files | 7 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ Subpackages not imported in __init__.py: ['tests', 'seed']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_project_program --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_project_program --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.303694_
