# ipai_dev_studio_base

**Status**: ⚠️ WARN
**Version**: 18.0.1.1.0
**Author**: InsightPulseAI

## Summary

Base OCA/CE module bundle and dev tools for InsightPulse

## Dependencies

- `base`
- `web`
- `mail`
- `contacts`
- `project`

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_dev_studio_base --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_dev_studio_base --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.296810_
