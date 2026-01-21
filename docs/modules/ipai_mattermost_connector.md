# ipai_mattermost_connector

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

API client and sync for Mattermost chat platform

## Dependencies

- `base`
- `mail`
- `ipai_integrations`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 3 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_mattermost_connector --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_mattermost_connector --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.897464_
