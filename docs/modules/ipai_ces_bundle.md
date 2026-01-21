# ipai_ces_bundle

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

One-click meta-installer for CES creative effectiveness vertical

## Dependencies

- `project`
- `hr`
- `hr_timesheet`
- `mail`
- `portal`
- `base_tier_validation`
- `base_exception`
- `date_range`
- `ipai_enterprise_bridge`

## Module Contents

| Type | Count |
|------|-------|
| Models | 0 |
| Views | 0 |
| Menus | 0 |
| Actions | 0 |
| Data Files | 0 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ces_bundle --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ces_bundle --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.907584_
