# ipai_n8n_connector

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Workflow automation integration with n8n

## Dependencies

- `base`
- `mail`
- `ipai_integrations`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 4 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_n8n_connector --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_n8n_connector --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.002588_
