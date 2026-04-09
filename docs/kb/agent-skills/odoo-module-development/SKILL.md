---
name: odoo_module_development
description: Create and maintain Odoo 18 CE modules following OCA conventions
category: backend
priority: critical
version: "1.0"
---

# Odoo Module Development

## Module Structure

Every Odoo 18 module follows this canonical directory layout:

```
ipai_<domain>_<feature>/
  __init__.py
  __manifest__.py
  models/
    __init__.py
    <model_name>.py
  views/
    <model_name>_views.xml
    menus.xml
  security/
    ir.model.access.csv
    security.xml
  data/
    <data_file>.xml
  static/
    description/
      icon.png
    src/
      js/
      scss/
      xml/
  tests/
    __init__.py
    test_<model_name>.py
  wizard/
    __init__.py
    <wizard_name>.py
  controllers/
    __init__.py
    main.py
  report/
    <report_name>.xml
    <report_template>.xml
```

Only include directories that contain files. Do not create empty directories.

## __manifest__.py Template

```python
{
    'name': 'IPAI Feature Name',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'One-line description of the module purpose',
    'description': """
Long description if needed.
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

### Version Convention

Format: `19.0.<series>.<migration>.<fix>`

- `19.0` = Odoo major version (always match target)
- `<series>` = module feature series (start at 1)
- `<migration>` = data migration bump
- `<fix>` = bugfix increment

### Required Keys

| Key | Required | Notes |
|-----|----------|-------|
| `name` | Yes | Human-readable module name |
| `version` | Yes | Must start with `19.0.` |
| `category` | Yes | Odoo category string |
| `summary` | Yes | One line, max 80 chars |
| `depends` | Yes | At minimum `['base']` |
| `data` | Yes | List of data/view XML files loaded on install |
| `license` | Yes | `LGPL-3` for CE modules |
| `installable` | Yes | `True` unless explicitly archived |
| `application` | No | `True` only for top-level app modules |
| `auto_install` | No | `True` only for glue modules bridging two deps |

## Model Definition Pattern

Follow this 10-section class order for all model files:

```python
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class IpaiExampleModel(models.Model):
    _name = 'ipai.example.model'
    _description = 'IPAI Example Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _rec_name = 'name'

    # --- Section 1: Default methods ---
    def _default_company_id(self):
        return self.env.company

    # --- Section 2: Fields ---
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=_default_company_id,
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )
    line_ids = fields.One2many(
        'ipai.example.line',
        'example_id',
        string='Lines',
    )
    tag_ids = fields.Many2many(
        'ipai.example.tag',
        string='Tags',
    )
    total_amount = fields.Monetary(
        string='Total',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
    )

    # --- Section 3: Compute methods ---
    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    # --- Section 4: Constrains ---
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name and len(record.name) < 3:
                raise ValidationError(
                    _('Name must be at least 3 characters.')
                )

    # --- Section 5: Onchange methods ---
    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.currency_id = self.company_id.currency_id

    # --- Section 6: CRUD overrides ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'ipai.example.model'
                )
        return super().create(vals_list)

    def write(self, vals):
        return super().write(vals)

    def unlink(self):
        if any(rec.state == 'done' for rec in self):
            raise UserError(_('Cannot delete confirmed records.'))
        return super().unlink()

    # --- Section 7: Action methods ---
    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'

    def action_done(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Only confirmed records can be set to done.'))
        self.state = 'done'

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def action_draft(self):
        self.ensure_one()
        self.state = 'draft'

    # --- Section 8: Business methods ---
    def _prepare_report_data(self):
        self.ensure_one()
        return {
            'name': self.name,
            'total': self.total_amount,
        }

    # --- Section 9: Cron methods ---
    @api.model
    def _cron_process_pending(self):
        records = self.search([('state', '=', 'confirmed')])
        records.action_done()

    # --- Section 10: Private methods ---
    def _get_display_name(self):
        return f'{self.name} ({self.state})'
```

## Security (ir.model.access.csv)

Format: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ipai_example_model_user,ipai.example.model.user,model_ipai_example_model,base.group_user,1,1,1,0
access_ipai_example_model_manager,ipai.example.model.manager,model_ipai_example_model,base.group_system,1,1,1,1
```

### Rules

- `model_id:id` = `model_<dotted_name_with_underscores>` (dots become underscores)
- One row per group per model
- Users get CRUD minus unlink; managers get full CRUD
- Always include at least `base.group_user` access
- For record rules (row-level security), use `security/security.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="ipai_example_model_company_rule" model="ir.rule">
        <field name="name">IPAI Example: multi-company</field>
        <field name="model_id" ref="model_ipai_example_model"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids),
        ]</field>
    </record>
</odoo>
```

## Data Files

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">

    <!-- Sequence -->
    <record id="seq_ipai_example" model="ir.sequence">
        <field name="name">IPAI Example Sequence</field>
        <field name="code">ipai.example.model</field>
        <field name="prefix">EX/%(year)s/</field>
        <field name="padding">5</field>
    </record>

    <!-- Default record -->
    <record id="ipai_example_default_tag" model="ipai.example.tag">
        <field name="name">Default</field>
    </record>

    <!-- Reference another record -->
    <record id="ipai_example_record_1" model="ipai.example.model">
        <field name="name">Example Record</field>
        <field name="tag_ids" eval="[(4, ref('ipai_example_default_tag'))]"/>
        <field name="company_id" ref="base.main_company"/>
    </record>

</odoo>
```

### noupdate Rules

- `noupdate="1"`: Data loaded only on install, not on update (sequences, default config, demo data)
- `noupdate="0"` (or omit): Data reloaded on every update (views, actions, menus, access rights)

## __init__.py Pattern

Root `__init__.py`:

```python
from . import models
from . import controllers
from . import wizard
```

Subdirectory `models/__init__.py`:

```python
from . import ipai_example_model
from . import ipai_example_line
```

## Checklist

Before committing a new or modified module:

- [ ] `__manifest__.py` version starts with `19.0.`
- [ ] `__manifest__.py` license is `LGPL-3`
- [ ] All model files imported in `__init__.py` chain
- [ ] All data/view XML files listed in `__manifest__.py` `data` key
- [ ] `ir.model.access.csv` covers every new model
- [ ] No `cr.commit()` or `cr.rollback()` calls
- [ ] All translatable strings use `_('...')`
- [ ] Compute methods loop over `self` (not `self.field = ...` without loop)
- [ ] `ensure_one()` called in action methods
- [ ] Test file exists in `tests/` with at least one test case
- [ ] Module installs cleanly: `odoo -d test_<module> -i <module> --stop-after-init`
