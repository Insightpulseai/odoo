# ipai_superset_connector

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Apache Superset integration with managed dataset sync

## Dependencies

- `base`
- `mail`
- `sale`
- `account`
- `stock`
- `hr`
- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 5 |
| Views | 9 |
| Menus | 6 |
| Actions | 5 |
| Data Files | 8 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_superset_connector --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_superset_connector --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.822685_
