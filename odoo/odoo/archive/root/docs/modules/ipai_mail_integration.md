# ipai_mail_integration

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Mailgun/SMTP/OAuth mail integration without IAP dependencies

## Dependencies

- `base`
- `mail`
- `ipai_enterprise_bridge`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 4 |
| Menus | 3 |
| Actions | 2 |
| Data Files | 4 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_mail_integration --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_mail_integration --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.823865_
