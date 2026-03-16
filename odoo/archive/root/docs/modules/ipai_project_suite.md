# ipai_project_suite

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Toggleable enterprise-like project management features for Odoo CE

## Dependencies

- `project`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 12 |
| Views | 10 |
| Menus | 3 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_project_suite --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_project_suite --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.340041_
