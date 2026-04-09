---
name: oca_module_porting
description: Port OCA modules between Odoo versions using oca-port
category: devops
priority: medium
version: "1.0"
---

# OCA Module Porting

## oca-port Tool
```bash
pip install oca-port
# Check if module can be migrated
oca-port origin/18.0 origin/19.0 <module_path> --verbose --dry-run
```

## Two Modes
1. Module doesn't exist on target → assists full migration
2. Module exists → retrieves unported commits grouped by PR

## Odoo 18 Migration Specifics
- Replace 'tree' view type with 'list' everywhere (Python, JS, XML)
- Run: odoo-bin upgrade_code --addons-path <path>
- groups_id → group_ids on res.users
- Provide migration scripts for breaking changes

## Quality Gates Before Adoption
1. Verify 19.0 branch exists and CI is green
2. Check development_status >= Stable in __manifest__.py
3. Test install in disposable DB (test_<module>)
4. Verify no conflicts with existing ipai_* modules
5. Document in addons.manifest.yaml with provenance
6. Track exceptions in docs/architecture/OCA19_COMPATIBILITY_EXCEPTIONS.md

## Never Rules
- Never modify OCA module source code — create ipai_* override
- Never copy OCA files into addons/ipai/ — use _inherit overrides
- OCA submodule pins in .gitmodules — update via git submodule update --remote
