# ipai_sample_metrics

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

Minimal OCA-style example app: metrics with list/form views and API helpers

## Dependencies

- `base`

## Module Contents

| Type | Count |
|------|-------|
| Models | 1 |
| Views | 3 |
| Menus | 2 |
| Actions | 1 |
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

- ⚠️ Subpackages not imported in __init__.py: ['tests']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_sample_metrics --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_sample_metrics --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.396838_
