# ipai_agent_core

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Skill/tool/knowledge registry + run logs for IPAI agents

## Dependencies

- `base`
- `web`

## Module Contents

| Type | Count |
|------|-------|
| Models | 4 |
| Views | 9 |
| Menus | 6 |
| Actions | 4 |
| Data Files | 8 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_agent_core --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_agent_core --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.124676_
