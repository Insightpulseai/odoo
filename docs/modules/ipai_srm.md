# ipai_srm

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

Supplier lifecycle and performance management (SAP SRM/Ariba-style parity)

## Dependencies

- `base`
- `mail`
- `purchase`
- `contacts`

## Module Contents

| Type | Count |
|------|-------|
| Models | 7 |
| Views | 10 |
| Menus | 6 |
| Actions | 4 |
| Data Files | 8 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_srm --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_srm --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.777909_
