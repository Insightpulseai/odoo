# ipai_superset_connector

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Embed Superset dashboards in Odoo with guest token authentication

## Dependencies

- `base`
- `web`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 6 |
| Menus | 5 |
| Actions | 3 |
| Data Files | 6 |

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
_Audited: 2026-01-21T22:42:54.569771_
