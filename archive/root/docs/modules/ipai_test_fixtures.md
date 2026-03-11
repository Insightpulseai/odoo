# ipai_test_fixtures

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Shared test fixtures and factory methods for IPAI modules

## Dependencies

- `base`
- `hr`
- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 0 |
| Menus | 0 |
| Actions | 0 |
| Data Files | 0 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ No security/ir.model.access.csv
- ⚠️ Subpackages not imported in __init__.py: ['tests']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_test_fixtures --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_test_fixtures --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.654506_
