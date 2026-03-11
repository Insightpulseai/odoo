# ipai_ai_provider_pulser

**Status**: ✅ PASS
**Version**: 18.0.1.0.1
**Author**: InsightPulse AI

## Summary

AI provider adapter for Pulser/self-hosted AI gateway

## Dependencies

- `base`
- `mail`
- `ipai_agent_core`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 2 |
| Menus | 1 |
| Actions | 1 |
| Data Files | 3 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ai_provider_pulser --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ai_provider_pulser --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.553813_
