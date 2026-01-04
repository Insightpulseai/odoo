# ipai_assets

**Status**: ✅ PASS
**Version**: 18.0.1.1.0
**Author**: InsightPulseAI

## Summary

Equipment and asset checkout tracking (Cheqroom-style parity)

## Dependencies

- `base`
- `mail`
- `hr`
- `stock`

## Module Contents

| Type | Count |
|------|-------|
| Models | 4 |
| Views | 12 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_assets --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_assets --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.168452_
