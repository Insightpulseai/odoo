# ipai_crm_pipeline

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: IPAI

## Summary

Salesforce-like CRM pipeline experience

## Dependencies

- `crm`
- `mail`
- `ipai_platform_workflow`
- `ipai_platform_theme`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 3 |
| Menus | 2 |
| Actions | 2 |
| Data Files | 4 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_crm_pipeline --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_crm_pipeline --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.267088_
