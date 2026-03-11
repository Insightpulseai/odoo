# ipai_settings_dashboard

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI / TBWA

## Summary

Unified AI provider settings with Kapa RAG, OpenAI, and Gemini support

## Dependencies

- `base`
- `mail`
- `ipai_ai_core`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 1 |
| Menus | 2 |
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

## Warnings

- ⚠️ No security/ir.model.access.csv

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_settings_dashboard --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_settings_dashboard --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.424053_
