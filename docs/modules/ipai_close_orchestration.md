# ipai_close_orchestration

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: IPAI

## Summary

Close Cycle Orchestration - Cycles, Tasks, Templates, Checklists, Exceptions, Gates

## Dependencies

- `base`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 9 |
| Views | 20 |
| Menus | 10 |
| Actions | 7 |
| Data Files | 9 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_close_orchestration --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_close_orchestration --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.246091_
