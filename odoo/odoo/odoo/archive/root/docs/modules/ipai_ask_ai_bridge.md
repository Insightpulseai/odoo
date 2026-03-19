# ipai_ask_ai_bridge

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Minimal launcher for external Ask AI / Copilot service.

## Dependencies

- `base`
- `web`

## Module Contents

| Type | Count |
|------|-------|
| Models | 1 |
| Views | 1 |
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

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ask_ai_bridge --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ask_ai_bridge --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.717494_
