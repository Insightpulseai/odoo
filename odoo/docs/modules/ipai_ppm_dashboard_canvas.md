# ipai_ppm_dashboard_canvas

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Clarity Canvas-style Project Dashboard with phases, milestones, tasks, to-dos, and OKR views

## Dependencies

- `project`
- `mail`
- `web`
- `hr_timesheet`

## Module Contents

| Type | Count |
|------|-------|
| Models | 0 |
| Views | 0 |
| Menus | 6 |
| Actions | 0 |
| Data Files | 9 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ppm_dashboard_canvas --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ppm_dashboard_canvas --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.222983_
