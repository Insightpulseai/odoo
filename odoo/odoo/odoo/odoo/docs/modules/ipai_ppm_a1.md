# ipai_ppm_a1

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

A1 Control Center - Workstreams, Templates, Tasks, Checks + Seed Import/Export

## Dependencies

- `base`
- `mail`
- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 11 |
| Views | 18 |
| Menus | 9 |
| Actions | 6 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ppm_a1 --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ppm_a1 --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.188990_
