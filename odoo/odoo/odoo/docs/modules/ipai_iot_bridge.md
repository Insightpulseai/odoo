# ipai_iot_bridge

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

IoT device bridge for CE+OCA without EE IoT dependencies

## Dependencies

- `base`
- `mail`
- `ipai_enterprise_bridge`

## Module Contents

| Type | Count |
|------|-------|
| Models | 4 |
| Views | 5 |
| Menus | 4 |
| Actions | 3 |
| Data Files | 3 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_iot_bridge --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_iot_bridge --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.803167_
