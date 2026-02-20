# OCA Migration Checklists by Version

Sources:
- https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-18.0
- https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-17.0
- https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-16.0
- https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-15.0

---

## Universal Steps (All Version Migrations)

```bash
# 1. Create migration branch from TARGET version
git checkout -b ${TO_VERSION}-mig-${MODULE} origin/${TO_VERSION}

# 2. Apply patches from source version
git format-patch --keep-subject --stdout origin/${TO_VERSION}..origin/${FROM_VERSION} -- ${MODULE} \
  | git am -3 --keep

# If whitespace conflicts:
git format-patch --keep-subject --stdout origin/${TO_VERSION}..origin/${FROM_VERSION} -- ${MODULE} \
  | git am -3 --keep --ignore-whitespace
# Then: git am --continue after resolving conflicts

# 3. Bump version in __manifest__.py
# Change: 'version': 'OLD.1.0.0'  ->  'version': 'NEW.1.0.0'

# 4. Remove migration scripts from previous version
rm -rf ${MODULE}/migrations/

# 5. Remove financing credits from previous version in CREDITS.rst

# 6. Run pre-commit formatting (ignore pylint at this stage)
pre-commit run -a --hook-stage=manual black isort prettier
git add .
git commit -m "[IMP] ${MODULE}: black, isort, prettier"
```

---

## Migration to 18.0

Wiki: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-18.0

### XML Changes

```bash
# Replace 'tree' view type with 'list' in ALL contexts:
# - Python code
# - JavaScript code
# - XML files
# EXCEPTION: Keep XML IDs that contain 'tree' (e.g., action_tree_view) to avoid breakage

# Use Odoo's automated upgrade script (requires local Odoo installation):
<path_to_odoo>/odoo-bin upgrade_code --addons-path <path_to_module>
```

### Python Changes

```python
# BEFORE (17.0):
if self.user_has_groups('base.group_user'):
    pass
self.check_access_rights('read')
self.check_access_rule('read')

# AFTER (18.0):
if self.env.user.has_group('base.group_user'):
    pass
self.check_access('read')  # unified single method replaces both
```

### JavaScript / Tour Tests

```javascript
// BEFORE (17.0) - extra_trigger on same step
{ trigger: '.o_field_widget', extra_trigger: '.some_class' }

// AFTER (18.0) - split into two independent steps
{ trigger: '.some_class' },
{ trigger: '.o_field_widget' },
```

### 18.0 Checklist

- [ ] Bump version to `18.0.1.0.0`
- [ ] Remove `migrations/` folder
- [ ] Replace `tree` view type with `list` (preserve XML IDs)
- [ ] Replace `user_has_groups()` with `env.user.has_group()`
- [ ] Replace `check_access_rights()` + `check_access_rule()` with `check_access()`
- [ ] Fix JS tour `extra_trigger` usage
- [ ] Run `pre-commit run -a`
- [ ] Generate README with `oca-gen-addon-readme`

---

## Migration to 17.0

Wiki: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-17.0

### Python Changes

```python
# 1. name_get -> _compute_display_name
# BEFORE (16.0):
def name_get(self):
    return [(rec.id, f"{rec.code} - {rec.name}") for rec in self]

# AFTER (17.0):
def _compute_display_name(self):
    for rec in self:
        rec.display_name = f"{rec.code} - {rec.name}"
# Remember to add new fields to @api.depends if needed

# 2. Module hooks: cr argument -> env argument
# BEFORE (16.0):
def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ...

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ...

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ...

# AFTER (17.0):
def pre_init_hook(env):
    ...

def post_init_hook(env):
    ...

def uninstall_hook(env):
    ...

# 3. get_resource_path -> file_path
# BEFORE (16.0):
from odoo.tools import get_resource_path
path = get_resource_path('module_name', 'path', 'to', 'file')

# AFTER (17.0):
from odoo.tools import file_path
path = file_path('module_name:path/to/file')
```

### XML / View Changes

```xml
<!-- attrs attribute is replaced by direct boolean attributes -->

<!-- BEFORE (16.0): -->
<field name="field_name" attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- AFTER (17.0): -->
<field name="field_name" invisible="state == 'draft'"/>

<!-- BEFORE: states attribute -->
<button states="draft,confirmed"/>

<!-- AFTER: invisible attribute -->
<button invisible="state not in ('draft', 'confirmed')"/>

<!-- tree view: column_invisible -> optional -->
<!-- BEFORE: -->
<field name="field" column_invisible="..."/>

<!-- AFTER: -->
<field name="field" optional="hide"/>
```

### Settings Views

- Settings view was simplified in 17.0 — check if `res_config_settings` views need updating

### 17.0 Checklist

- [ ] Bump version to `17.0.1.0.0`
- [ ] Remove `migrations/` folder
- [ ] Replace `name_get()` with `_compute_display_name()`
- [ ] Update module hook signatures (`cr` -> `env`)
- [ ] Replace `get_resource_path` with `file_path`
- [ ] Replace `attrs=` with inline boolean expressions
- [ ] Replace `states=` with `invisible=`
- [ ] Fix `column_invisible` in tree views
- [ ] Check settings views
- [ ] Run `pre-commit run -a`
- [ ] Generate README

---

## Migration to 16.0

Wiki: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-16.0

### Python Changes

```python
# 1. group_ids -> groups in field definitions
# BEFORE (15.0):
state = fields.Selection(group_ids=[(4, ref('base.group_user'))])

# AFTER (16.0):
state = fields.Selection(groups='base.group_user')

# 2. ir.config_parameter: remove group_ids from records
# In data XML files, remove group_ids from ir.config_parameter records
```

### XML / View Changes

```xml
<!-- colors attribute replaced by decoration-* in tree/list views -->

<!-- BEFORE (15.0): -->
<tree colors="red:state=='cancel';blue:state=='draft'">

<!-- AFTER (16.0): -->
<tree decoration-danger="state=='cancel'" decoration-info="state=='draft'">

<!-- widget changes -->
<!-- BEFORE: kanban_state_selection -->
<field name="kanban_state" widget="kanban_state_selection"/>

<!-- AFTER: -->
<field name="kanban_state" widget="state_selection"/>
```

### 16.0 Checklist

- [ ] Bump version to `16.0.1.0.0`
- [ ] Remove `migrations/` folder
- [ ] Run pre-commit black/isort/prettier pass
- [ ] Remove `group_ids` from ir.config_parameter records
- [ ] Replace `group_ids=` with `groups=` in field definitions
- [ ] Replace `colors=` with `decoration-*=` in tree views
- [ ] Replace `widget="kanban_state_selection"` with `widget="state_selection"`
- [ ] Check maturity level — can it be improved?

---

## Migration to 15.0

Wiki: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-15.0

### JavaScript / Assets

```python
# BEFORE (14.0) - qweb in manifest:
'qweb': ['static/src/xml/template.xml']

# AFTER (15.0) - assets declaration in manifest:
'assets': {
    'web.assets_backend': [
        'module/static/src/js/widget.js',
        'module/static/src/scss/style.scss',
    ],
    'web.assets_qweb': [
        'module/static/src/xml/template.xml',
    ],
    'web.assets_frontend': [
        'module/static/src/js/portal.js',
    ],
}
```

### Python Changes (15.0)

```python
# OWL components replace old Widget system
# AbstractModel.browse() behavior changes
# mail.thread inheritance changes
```

### 15.0 Checklist

- [ ] Bump version to `15.0.1.0.0`
- [ ] Remove `migrations/` folder
- [ ] Move assets from `qweb` key to `assets` dict in manifest
- [ ] Update any OWL/widget code
- [ ] Check mail.thread inheritance
- [ ] Run pre-commit
- [ ] Generate README

---

## Using Odoo's Built-in Upgrade Code Tool (18.0+)

```bash
# Requires a local Odoo installation
<path_to_odoo>/odoo-bin upgrade_code --addons-path <path_to_module>

# This script handles the most common 17.0->18.0 transformations automatically:
# - tree -> list view type replacement
# - Various attribute migrations
```

## Checking OpenUpgrade for Data Model Changes

For database field/model changes (not covered above):

```
https://github.com/OCA/OpenUpgrade/blob/{VERSION}/docsource/api_changes.rst
https://github.com/OCA/OpenUpgrade/tree/{VERSION}/openupgrade_scripts/scripts/
```
