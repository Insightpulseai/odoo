# ipai_ask_ai

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

ERP-aware RAG Engine for Finance and Month-End Close workflows

## Dependencies

- `base`
- `mail`
- `project`
- `ipai_finance_ppm`

## Module Contents

| Type | Count |
|------|-------|
| Models | 4 |
| Views | 4 |
| Menus | 3 |
| Actions | 2 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ask_ai --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ask_ai --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.686449_
