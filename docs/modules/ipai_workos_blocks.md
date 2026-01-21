# ipai_workos_blocks

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Notion-style block editor for pages

## Dependencies

- `base`
- `web`
- `ipai_workos_core`

## Module Contents

| Type | Count |
|------|-------|
| Models | 1 |
| Views | 2 |
| Menus | 1 |
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

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_workos_blocks --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_workos_blocks --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.822321_
