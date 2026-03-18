# ipai_ask_ai_chatter

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Integrate Ask AI into Odoo Chatter for contextual AI assistance

## Dependencies

- `mail`
- `ipai_ask_ai`

## Module Contents

| Type | Count |
|------|-------|
| Models | 1 |
| Views | 3 |
| Menus | 1 |
| Actions | 1 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ask_ai_chatter --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ask_ai_chatter --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.745554_
