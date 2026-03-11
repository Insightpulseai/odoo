# ipai_ai_sources_odoo

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Export Odoo data (tasks, KB articles) to Supabase KB for RAG retrieval

## Dependencies

- `base`
- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 3 |
| Menus | 1 |
| Actions | 1 |
| Data Files | 4 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ Subpackages not imported in __init__.py: ['tests']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ai_sources_odoo --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ai_sources_odoo --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.570030_
