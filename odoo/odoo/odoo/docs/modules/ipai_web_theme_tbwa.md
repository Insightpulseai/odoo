# ipai_web_theme_tbwa

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

TBWA brand styling for Odoo CE 18 backend (consumes brand tokens)

## Dependencies

- `web`
- `mail`
- `ipai_ui_brand_tokens`

## Module Contents

| Type | Count |
|------|-------|
| Models | 0 |
| Views | 0 |
| Menus | 0 |
| Actions | 0 |
| Data Files | 1 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ✅ |

## Warnings

- ⚠️ No security/ir.model.access.csv

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_web_theme_tbwa --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_web_theme_tbwa --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.806514_
