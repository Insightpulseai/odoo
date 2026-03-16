# ipai_ai_connectors

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Inbound integration hub for AI platform (n8n, GitHub, Slack webhooks)

## Dependencies

- `base`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 1 |
| Views | 3 |
| Menus | 1 |
| Actions | 1 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ai_connectors --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ai_connectors --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.453290_
