# ipai_control_room

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Control Room for pipelines, data quality, and operational insights

## Dependencies

- `base`
- `mail`
- `project`
- `web`
- `ipai_theme_fluent2`

## Module Contents

| Type | Count |
|------|-------|
| Models | 18 |
| Views | 41 |
| Menus | 21 |
| Actions | 16 |
| Data Files | 9 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ✅ |

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_control_room --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_control_room --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.004724_
