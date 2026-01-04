# ipai_ask_ai

**Status**: ✅ PASS
**Version**: 18.0.1.1.0
**Author**: InsightPulse AI

## Summary

AI-powered conversational assistant for Odoo

## Dependencies

- `base`
- `web`
- `mail`
- `ipai_platform_theme`

## Module Contents

| Type | Count |
|------|-------|
| Models | 4 |
| Views | 1 |
| Menus | 0 |
| Actions | 0 |
| Data Files | 6 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ask_ai --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ask_ai --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.141335_
