# ipai_ce_branding

**Status**: ⚠️ WARN
**Version**: 18.0.1.2.0
**Author**: InsightPulse AI

## Summary

Custom branding for Odoo CE login and backend

## Dependencies

- `web`
- `base`
- `remove_odoo_enterprise`
- `disable_odoo_online`

## Module Contents

| Type | Count |
|------|-------|
| Models | 0 |
| Views | 0 |
| Menus | 0 |
| Actions | 0 |
| Data Files | 2 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ce_branding --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ce_branding --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.882915_
