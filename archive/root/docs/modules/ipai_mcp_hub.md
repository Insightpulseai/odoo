# ipai_mcp_hub

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Model Context Protocol (MCP) server and tool registry

## Dependencies

- `base`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 8 |
| Menus | 4 |
| Actions | 3 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_mcp_hub --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_mcp_hub --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.918802_
