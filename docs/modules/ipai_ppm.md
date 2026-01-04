# ipai_ppm

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Portfolio/Program governance layer with risk register, KPI snapshots, and resource allocation

## Dependencies

- `project`
- `hr`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 6 |
| Views | 16 |
| Menus | 8 |
| Actions | 5 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ppm --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ppm --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.683596_
