# ipai_portal_fix

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.1
**Author**: InsightPulseAI

## Summary

Fixes KeyError: website in portal.frontend_layout template

## Dependencies

- `portal`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 0 |
| Menus | 0 |
| Actions | 0 |
| Data Files | 1 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ✅ |

## Warnings

- ⚠️ No security/ir.model.access.csv

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_portal_fix --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_portal_fix --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.675063_
