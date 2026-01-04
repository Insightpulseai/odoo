# ipai_bir_compliance

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

BIR 2307 Generator & Alphalist/RELIEF DAT File Engine

## Dependencies

- `account`

## Module Contents

| Type | Count |
|------|-------|
| Models | 1 |
| Views | 2 |
| Menus | 2 |
| Actions | 2 |
| Data Files | 3 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ Subpackages not imported in __init__.py: ['reports']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_bir_compliance --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_bir_compliance --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.184311_
