# ipai_project_profitability_bridge

**Status**: ✅ PASS
**Version**: 18.0.1.0.1
**Author**: InsightPulse AI

## Summary

Lightweight profitability KPIs per project using analytic lines (CE-safe).

## Dependencies

- `project`
- `analytic`
- `web`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 7 |
| Menus | 1 |
| Actions | 2 |
| Data Files | 5 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_project_profitability_bridge --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_project_profitability_bridge --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.284949_
