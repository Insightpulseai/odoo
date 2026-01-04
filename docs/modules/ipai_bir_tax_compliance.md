# ipai_bir_tax_compliance

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: IPAI

## Summary

Philippine BIR tax compliance - 36 eBIRForms support

## Dependencies

- `base`
- `mail`
- `account`

## Module Contents

| Type | Count |
|------|-------|
| Models | 10 |
| Views | 15 |
| Menus | 11 |
| Actions | 6 |
| Data Files | 10 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_bir_tax_compliance --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_bir_tax_compliance --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.194951_
