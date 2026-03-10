# ipai_command_center

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Platform cockpit for runs, KPIs, alerts, and AI

## Dependencies

- `base`
- `mail`
- `ipai_design_system_apps_sdk`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 7 |
| Menus | 5 |
| Actions | 3 |
| Data Files | 4 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_command_center --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_command_center --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.981708_
