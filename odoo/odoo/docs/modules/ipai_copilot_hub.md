# ipai_copilot_hub

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Ops Control Room / AI Runbook Hub with Fluent UI shell

## Dependencies

- `base`
- `web`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 1 |
| Menus | 5 |
| Actions | 3 |
| Data Files | 5 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_copilot_hub --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_copilot_hub --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.051438_
