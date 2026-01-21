# ipai_sms_gateway

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

SMS gateway for sending messages via HTTP providers

## Dependencies

- `base`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 5 |
| Menus | 3 |
| Actions | 2 |
| Data Files | 3 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_sms_gateway --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_sms_gateway --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.459313_
