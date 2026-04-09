---
name: Odoo Upgrades
description: Use when porting modules between versions, cleaning manifests, fixing migrations, or checking upgrade compatibility.
---

# Odoo Upgrades

## When to use

- Porting an OCA module from one version to another (e.g., 17.0 → 18.0)
- Cleaning deprecated API usage in existing modules
- Writing or fixing migration scripts
- Checking whether a custom module survives a version upgrade
- Reviewing manifest version compatibility

## Version changes in Odoo 18

### Python API changes

- `attrs` dict syntax removed → use direct XML attributes (`invisible`, `readonly`, `required`)
- `states` attribute removed → use `invisible` with domain
- `tree` view type → renamed to `list` (both work, prefer `list`)
- `@api.multi` removed (already gone since 13.0, but verify)
- `fields.Selection` → `selection_add` uses `(value, label)` tuples with optional `before=`/`after=`

### XML changes

- `<tree>` → `<list>` (preferred)
- `attrs="{'invisible': [...]}"` → `invisible="field_name"` or `invisible="expression"`
- `states="draft,confirmed"` → `invisible="state not in ('draft', 'confirmed')"`
- Bootstrap 5 (no jQuery dependency for layout)

### Manifest changes

- `version` must use `18.0.x.y.z` format
- `python` key in `external_dependencies` must list exact package names
- `assets` key replaces `qweb` key for template registration

## Migration scripts

```
<module>/migrations/<version>/
├── pre-migrate.py    # Before module update
├── post-migrate.py   # After module update
└── end-migrate.py    # After all modules updated
```

```python
# migrations/18.0.1.1.0/post-migrate.py
from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, [
        ("ipai.my.model", "ipai_my_model", "old_field", "new_field"),
    ])
```

## OCA porting checklist

1. Update `__manifest__.py` version to `18.0.x.y.z`
2. Replace `attrs` dict syntax with direct attributes
3. Replace `states` with `invisible` domains
4. Replace `<tree>` with `<list>`
5. Update `assets` key (remove `qweb` key)
6. Check all `depends` modules exist at 18.0
7. Run `pre-commit` (OCA hooks: pylint, flake8, isort, black)
8. Test install on fresh database
9. Run module tests

## Checking OCA 18.0 availability

```bash
# Check if module exists at 18.0
git ls-remote --heads https://github.com/OCA/<repo>.git refs/heads/18.0

# Check specific module in repo
curl -sf https://raw.githubusercontent.com/OCA/<repo>/18.0/<module>/__manifest__.py | head -5
```

## Do not

- Port modules without checking if an 18.0 version already exists
- Remove migration scripts from prior versions (they may still be needed)
- Change `_name` of existing models during migration (breaks FK references)
- Skip testing on a fresh database after porting
- Assume OCA modules are available at 18.0 without verifying the branch
