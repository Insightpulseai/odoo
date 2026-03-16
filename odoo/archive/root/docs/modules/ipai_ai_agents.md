# ipai_ai_agents

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

Odoo 19-style Ask AI / AI agents UX for Odoo CE 18 (OCA-friendly custom addon)

## Dependencies

- `base`
- `web`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 4 |
| Views | 8 |
| Menus | 7 |
| Actions | 5 |
| Data Files | 7 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ Subpackages not imported in __init__.py: ['services']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ai_agents --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ai_agents --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.371673_
