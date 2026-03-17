# ipai_integrations

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Central integration hub for Mattermost, Focalboard, and n8n

## Dependencies

- `base`
- `web`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 6 |
| Views | 11 |
| Menus | 8 |
| Actions | 5 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_integrations --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_integrations --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.771725_
