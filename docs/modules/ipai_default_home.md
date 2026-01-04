# ipai_default_home

**Status**: ⚠️ WARN
**Version**: 18.0.3.0.0
**Author**: InsightPulse AI

## Summary

Custom app grid home page with modern styling

## Dependencies

- `base`
- `web`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 0 |
| Views | 0 |
| Menus | 1 |
| Actions | 1 |
| Data Files | 2 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_default_home --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_default_home --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.283494_
