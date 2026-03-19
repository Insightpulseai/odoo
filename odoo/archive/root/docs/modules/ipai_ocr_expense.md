# ipai_ocr_expense

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

AI-powered receipt scanning and expense digitization

## Dependencies

- `hr_expense`
- `ipai_expense`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 3 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ocr_expense --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ocr_expense --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.030677_
