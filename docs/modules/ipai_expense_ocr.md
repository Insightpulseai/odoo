# ipai_expense_ocr

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

OCR-powered receipt scanning for expense management

## Dependencies

- `hr_expense`
- `ipai_document_ai`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 6 |
| Menus | 1 |
| Actions | 1 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_expense_ocr --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_expense_ocr --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.273178_
