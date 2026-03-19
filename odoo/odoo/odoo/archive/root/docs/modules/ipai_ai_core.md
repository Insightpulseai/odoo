# ipai_ai_core

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.1
**Author**: InsightPulse AI

## Summary

Provider-based AI threads/messages/citations for Odoo CE 18 (works with OCA AI UI).

## Dependencies

- `base`
- `mail`
- `web`

## Module Contents

| Type | Count |
|------|-------|
| Models | 5 |
| Views | 8 |
| Menus | 3 |
| Actions | 2 |
| Data Files | 4 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ Subpackages not imported in __init__.py: ['tests']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ai_core --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ai_core --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.495505_
