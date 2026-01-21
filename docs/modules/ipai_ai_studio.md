# ipai_ai_studio

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

AI-driven Studio-like module generator for Odoo CE (spec -> addon scaffold -> validate -> apply)

## Dependencies

- `base`
- `web`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 2 |
| Menus | 2 |
| Actions | 1 |
| Data Files | 4 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ai_studio --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ai_studio --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.589005_
