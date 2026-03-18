# ipai_bi_superset

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Thin-layer Superset integration via guest token embedding

## Dependencies

- `base`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 7 |
| Menus | 5 |
| Actions | 3 |
| Data Files | 6 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_bi_superset --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_bi_superset --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.792024_
