# ipai_workos_affine

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Installs the full WorkOS AFFiNE-style suite

## Dependencies

- `ipai_workos_core`
- `ipai_workos_blocks`
- `ipai_workos_db`
- `ipai_workos_views`
- `ipai_workos_collab`
- `ipai_workos_search`
- `ipai_workos_templates`
- `ipai_workos_canvas`
- `ipai_platform_permissions`
- `ipai_platform_audit`

## Module Contents

| Type | Count |
|------|-------|
| Models | 0 |
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
| Init Imports | ✅ |

## Warnings

- ⚠️ No security/ir.model.access.csv

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_workos_affine --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_workos_affine --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.817655_
