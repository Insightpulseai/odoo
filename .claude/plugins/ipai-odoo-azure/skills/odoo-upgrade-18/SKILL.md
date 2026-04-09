---
name: odoo-upgrade-18
description: Apply Odoo 18 CE upgrade rules and migration patterns
triggers:
  - keywords: ["upgrade", "migrate", "18.0", "tree to list", "groups_id to group_ids"]
layer: A-domain
---

# Odoo 18 Upgrade Skill

Breaking changes from 17.0:
1. `res.users.groups_id` renamed to `group_ids`
2. `tree` view type renamed to `list` globally
3. Portal and Internal User groups are mutually exclusive
4. Use `Command` tuples for x2many: `Command.create()`, `Command.link()`, `Command.set()`
5. Version strings must be `18.0.x.y.z` — never 19.0

OCA porting workflow:
1. `oca-port origin/17.0 origin/18.0 <module> --verbose --dry-run`
2. `odoo-bin upgrade_code --addons-path <path>`
3. Test install: `odoo-bin -d test_<module> -i <module> --stop-after-init --test-enable`
4. Classify result per failure matrix
