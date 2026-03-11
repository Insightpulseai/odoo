# ipai_enterprise_bridge

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Thin glue layer for CE+OCA parity: config, approvals, AI/infra integration

## Dependencies

- `base`
- `web`
- `mail`
- `contacts`
- `account`
- `sale_management`
- `purchase`
- `stock`
- `project`
- `hr`
- `hr_timesheet`
- `base_tier_validation`
- `base_exception`
- `date_range`
- `ipai_workspace_core`

## Module Contents

| Type | Count |
|------|-------|
| Models | 13 |
| Views | 10 |
| Menus | 9 |
| Actions | 4 |
| Data Files | 11 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ Subpackages not imported in __init__.py: ['tests']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_enterprise_bridge --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_enterprise_bridge --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.202586_
