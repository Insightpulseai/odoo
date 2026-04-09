---
name: odoo-models
description: Create or modify Odoo 18 CE model classes following OCA coding standards
triggers:
  - file_pattern: "addons/ipai/**/models/*.py"
  - keywords: ["model", "_name", "_inherit", "fields."]
layer: A-domain
---

# Odoo 18 Model Skill

When creating or modifying Odoo models:

1. Follow strict class attribute order: private attrs → defaults → fields → constraints → compute → CRUD → actions → business
2. Naming: `ipai_<domain>_<feature>` for module, `ipai.<domain>.<model>` for model name
3. Version: `18.0.x.y.z` — never 19.0
4. Use `Command` tuples for x2many writes
5. Never `cr.commit()`, never mutate context directly
6. Lazy translation only: `_('text %s', var)` — never f-strings or .format()
7. Import order: stdlib → odoo core → odoo.addons
8. CE only — no Enterprise module dependencies
9. OCA first — check if OCA module exists before creating ipai_*

Reference: `~/.claude/rules/odoo19-coding.md` (file name is legacy, content is Odoo 18)
