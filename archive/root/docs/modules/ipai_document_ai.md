# ipai_document_ai

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Self-hosted OCR and document intelligence for Odoo

## Dependencies

- `base`
- `mail`
- `account`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 4 |
| Menus | 3 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_document_ai --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_document_ai --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.174169_
