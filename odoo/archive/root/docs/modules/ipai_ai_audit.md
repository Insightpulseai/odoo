# ipai_ai_audit

**Status**: ✅ PASS
**Version**: 18.0.1.0.1
**Author**: InsightPulse AI

## Summary

AI usage logging, redaction, and governance controls

## Dependencies

- `base`
- `mail`
- `ipai_ai_provider_pulser`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 7 |
| Menus | 5 |
| Actions | 2 |
| Data Files | 7 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ai_audit --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ai_audit --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.431304_
