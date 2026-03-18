---
status: comprehensive-reference
consolidates:
  - odoo-qweb-reports skill
  - odoo-testing-patterns skill
  - odoo-performance-optimization skill
  - odoo-website-themes skill
  - odoo-translations skill
  - odoo-version-migration skill
  - ODOO_MIXINS_REFERENCE.md
  - ODOO_TESTING_GUIDE.md
  - ODOO_QWEB_REFERENCE.md
  - ODOO_PERFORMANCE_GUIDE.md
last_updated: 2026-02-09
---

# Odoo Developer Complete Reference

Consolidated reference covering QWeb reports, testing patterns, performance optimization, mixins, website themes, translations, and version migrations for Odoo 19.

---

## Table of Contents

1. [QWeb Reports & Templates](#qweb-reports--templates)
2. [Testing Patterns](#testing-patterns)
3. [Performance Optimization](#performance-optimization)
4. [Common Mixins](#common-mixins)
5. [Website Themes](#website-themes)
6. [Translations (i18n/l10n)](#translations-i18nl10n)
7. [Version Migration](#version-migration)

---

## QWeb Reports & Templates

### Report Definition

```xml
<!-- ir.actions.report -->
<record id="action_report_invoice" model="ir.actions.report">
    <field name="name">Invoice</field>
    <field name="model">account.move</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_addon.report_invoice</field>
    <field name="report_file">my_addon.report_invoice</field>
    <field name="binding_model_id" ref="model_account_move"/>
    <field name="binding_type">report</field>
</record>
```

### QWeb Template

```xml
<template id="report_invoice">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Header -->
                    <h2>Invoice <span t-field="o.name"/></h2>

                    <!-- Customer Info -->
                    <div class="row">
                        <div class="col-6">
                            <strong>Customer:</strong><br/>
                            <div t-field="o.partner_id"
                                 t-options='{"widget": "contact", "fields": ["address", "name", "phone"]}'/>
                        </div>
                        <div class="col-6">
                            <strong>Invoice Date:</strong>
                            <span t-field="o.invoice_date"/><br/>
                            <strong>Due Date:</strong>
                            <span t-field="o.invoice_date_due"/>
                        </div>
                    </div>

                    <!-- Invoice Lines -->
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Description</th>
                                <th class="text-right">Quantity</th>
                                <th class="text-right">Unit Price</th>
                                <th class="text-right">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="o.invoice_line_ids" t-as="line">
                                <tr>
                                    <td><span t-field="line.name"/></td>
                                    <td class="text-right"><span t-field="line.quantity"/></td>
                                    <td class="text-right"><span t-field="line.price_unit"/></td>
                                    <td class="text-right"><span t-field="line.price_subtotal"/></td>
                                </tr>
                            </t>
                        </tbody>
                    </table>

                    <!-- Totals -->
                    <div class="row">
                        <div class="col-6 offset-6">
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Subtotal</strong></td>
                                    <td class="text-right"><span t-field="o.amount_untaxed"/></td>
                                </tr>
                                <tr>
                                    <td><strong>Tax</strong></td>
                                    <td class="text-right"><span t-field="o.amount_tax"/></td>
                                </tr>
                                <tr>
                                    <td><strong>Total</strong></td>
                                    <td class="text-right"><span t-field="o.amount_total"/></td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
            </t>
        </t>
    </t>
</template>
```

### QWeb Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `t-field` | Field value with formatting | `<span t-field="o.date"/>` |
| `t-esc` | Escaped text | `<span t-esc="o.name"/>` |
| `t-raw` | Raw HTML | `<div t-raw="o.description"/>` |
| `t-if` | Conditional | `<div t-if="o.state == 'draft'">Draft</div>` |
| `t-foreach` | Loop | `<t t-foreach="o.lines" t-as="line">` |
| `t-set` | Variable | `<t t-set="total" t-value="o.amount"/>` |
| `t-call` | Template inheritance | `<t t-call="web.external_layout">` |

### Custom Report Methods

```python
from odoo import models

class ReportInvoice(models.AbstractModel):
    _name = 'report.my_addon.report_invoice'
    _description = 'Invoice Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)

        # Custom computations
        for doc in docs:
            doc.custom_total = sum(line.price_subtotal for line in doc.invoice_line_ids)

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'data': data,
            # Custom values
            'company': self.env.company,
            'report_date': fields.Date.today(),
        }
```

---

## Testing Patterns

### Backend Unit Tests

```python
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestPartner(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env['res.partner']
        cls.test_partner = cls.Partner.create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })

    def test_partner_creation(self):
        """Test partner is created correctly"""
        self.assertEqual(self.test_partner.name, 'Test Partner')
        self.assertTrue(self.test_partner.id)

    def test_partner_email_validation(self):
        """Test email validation"""
        with self.assertRaises(ValidationError):
            self.Partner.create({'name': 'Bad Email', 'email': 'invalid'})

    def test_partner_search(self):
        """Test partner search"""
        partners = self.Partner.search([('name', '=', 'Test Partner')])
        self.assertEqual(len(partners), 1)
        self.assertEqual(partners[0].id, self.test_partner.id)
```

### Testing with Form

```python
from odoo.tests import Form

def test_partner_form(self):
    """Test partner via form"""
    partner_form = Form(self.env['res.partner'])
    partner_form.name = 'Form Partner'
    partner_form.email = 'form@example.com'
    partner = partner_form.save()

    self.assertEqual(partner.name, 'Form Partner')
```

### Testing Access Rights

```python
from odoo.exceptions import AccessError

def test_partner_access_rights(self):
    """Test user access rights"""
    user = self.env['res.users'].create({
        'name': 'Test User',
        'login': 'test_user',
        'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
    })

    # Test as different user
    Partner = self.Partner.with_user(user)

    # Should have read access
    partner = Partner.browse(self.test_partner.id)
    self.assertEqual(partner.name, 'Test Partner')

    # Should not have delete access
    with self.assertRaises(AccessError):
        partner.unlink()
```

### Frontend Tests (HOOT)

See `odoo-hoot-testing` skill for complete frontend testing patterns.

---

## Performance Optimization

### Query Optimization

**Bad:**
```python
# N+1 query problem
for partner in partners:
    print(partner.country_id.name)  # Extra query per partner
```

**Good:**
```python
# Eager loading
partners = partners.with_context(prefetch_fields=True)
# Or use read() with specific fields
partner_data = partners.read(['name', 'country_id'])
```

### Batch Operations

**Bad:**
```python
for line in lines:
    line.write({'state': 'done'})  # One query per line
```

**Good:**
```python
lines.write({'state': 'done'})  # Single query
```

### Caching

```python
from odoo import tools

class MyModel(models.Model):
    _name = 'my.model'

    @tools.ormcache('partner_id')
    def _get_partner_data(self, partner_id):
        """Cached method"""
        return self.env['res.partner'].browse(partner_id).read(['name', 'email'])[0]

    def clear_cache(self):
        """Clear cache when needed"""
        self._get_partner_data.clear_cache(self)
```

### Database Indexes

```python
_sql_constraints = [
    ('unique_ref', 'UNIQUE(ref)', 'Reference must be unique'),
]

def init(self):
    """Create indexes"""
    self._cr.execute("""
        CREATE INDEX IF NOT EXISTS my_model_partner_date_idx
        ON my_model (partner_id, date)
    """)
```

### Computed Fields Optimization

```python
# Store computed field
amount_total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.price_subtotal')
def _compute_total(self):
    for record in self:
        record.amount_total = sum(record.line_ids.mapped('price_subtotal'))
```

---

## Common Mixins

### mail.thread (Chatter)

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'My Model'

    name = fields.Char(required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], tracking=True)

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        self.message_post(body='Document confirmed')
```

### mail.activity.mixin (Activities)

```python
# Schedule activity
self.activity_schedule(
    'mail.mail_activity_data_todo',
    user_id=self.user_id.id,
    summary='Review document',
    note='Please review this document',
    date_deadline=fields.Date.today() + timedelta(days=7)
)

# Mark activity done
activity.action_done()
```

### portal.mixin (Portal Access)

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['portal.mixin']

    def _compute_access_url(self):
        for record in self:
            record.access_url = f'/my/model/{record.id}'
```

### rating.mixin (Ratings)

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['rating.mixin']

    # Automatically adds rating_ids and rating methods
```

---

## Website Themes

### Theme Structure

```
my_theme/
├── __manifest__.py
├── data/
│   └── presets.xml
├── static/
│   ├── src/
│   │   ├── scss/
│   │   │   ├── primary_variables.scss
│   │   │   └── custom.scss
│   │   └── js/
│   │       └── custom.js
│   └── images/
│       └── logo.png
└── views/
    ├── layout.xml
    └── snippets.xml
```

### Theme Manifest

```python
{
    'name': 'My Theme',
    'category': 'Theme/Creative',
    'version': '19.0.1.0.0',
    'depends': ['website', 'website_theme_install'],
    'data': [
        'views/layout.xml',
        'views/snippets.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'my_theme/static/src/scss/primary_variables.scss',
        ],
        'web.assets_frontend': [
            'my_theme/static/src/scss/custom.scss',
            'my_theme/static/src/js/custom.js',
        ],
    },
    'images': ['static/images/theme_preview.jpg'],
}
```

### Custom Snippet

```xml
<template id="s_custom_snippet" name="Custom Snippet">
    <section class="s_custom_snippet">
        <div class="container">
            <h2 class="text-center">Custom Section</h2>
            <p class="text-center">Custom content here</p>
        </div>
    </section>
</template>

<record id="s_custom_snippet" model="ir.ui.view">
    <field name="key">my_theme.s_custom_snippet</field>
    <field name="name">Custom Snippet</field>
    <field name="type">qweb</field>
    <field name="inherit_id" ref="website.snippets"/>
    <field name="mode">extension</field>
    <field name="arch" type="xml">
        <xpath expr="//div[@id='snippet_structure']" position="inside">
            <t t-snippet="my_theme.s_custom_snippet" t-thumbnail="/my_theme/static/images/snippet_thumb.jpg"/>
        </xpath>
    </field>
</record>
```

---

## Translations (i18n/l10n)

### Mark Strings for Translation

**Python:**
```python
from odoo import _, _lt

# Lazy translation (for class attributes)
_name = _lt('My Model')

# Runtime translation
def my_method(self):
    msg = _('This is translatable')
    return msg
```

**JavaScript:**
```javascript
import { _t } from "@web/core/l10n/translation";

const message = _t("This is translatable");
```

**XML:**
```xml
<button string="Save" type="object"/>  <!-- Automatically translatable -->
```

### Generate POT File

```bash
# Generate translation template
python3 odoo-bin --i18n-export=my_addon.pot -d database --modules=my_addon
```

### Import Translations

```bash
# Import PO file
python3 odoo-bin --i18n-import=fr_FR.po -l fr_FR -d database --modules=my_addon
```

### Translation File Structure

```
my_addon/
└── i18n/
    ├── my_addon.pot      # Template
    ├── fr_FR.po          # French
    ├── es_ES.po          # Spanish
    └── de_DE.po          # German
```

---

## Version Migration

### Migration Script Structure

```
my_addon/
└── migrations/
    └── 19.0.1.0.0/
        ├── pre-migrate.py
        └── post-migrate.py
```

### Pre-Migration Script

```python
# migrations/19.0.1.0.0/pre-migrate.py
def migrate(cr, version):
    """Pre-migration operations"""
    # Backup data
    cr.execute("""
        CREATE TABLE my_model_backup AS
        SELECT * FROM my_model
    """)

    # Drop conflicting constraints
    cr.execute("""
        ALTER TABLE my_model
        DROP CONSTRAINT IF EXISTS my_constraint
    """)
```

### Post-Migration Script

```python
# migrations/19.0.1.0.0/post-migrate.py
from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """Post-migration operations"""
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Update records
    records = env['my.model'].search([])
    for record in records:
        record.new_field = record.old_field * 2

    # Clean up
    cr.execute("DROP TABLE IF EXISTS my_model_backup")
```

### Version Compatibility

```python
from odoo import api, fields, models, release

class MyModel(models.Model):
    _name = 'my.model'

    def my_method(self):
        # Check Odoo version
        version = release.version_info[0]
        if version >= 19:
            # Odoo 19+ code
            pass
        else:
            # Older version code
            pass
```

---

## Quick Reference

### Performance Checklist
- ✅ Use `read()` instead of browsing when possible
- ✅ Batch writes/creates
- ✅ Add database indexes on frequently searched fields
- ✅ Cache expensive computations
- ✅ Use `prefetch_fields=True` for related fields
- ✅ Store computed fields when appropriate

### Testing Checklist
- ✅ Test CRUD operations
- ✅ Test access rights
- ✅ Test computed fields
- ✅ Test constraints
- ✅ Test workflows/state changes
- ✅ Test UI components (HOOT)
- ✅ Aim for >80% coverage

### Report Checklist
- ✅ Use `web.external_layout` for header/footer
- ✅ Test with different paper sizes
- ✅ Test with long/short data
- ✅ Optimize for PDF generation
- ✅ Handle missing data gracefully

### Migration Checklist
- ✅ Backup database before migration
- ✅ Test migration on copy first
- ✅ Use pre-migrate for schema changes
- ✅ Use post-migrate for data updates
- ✅ Test all functionality after migration
- ✅ Update module version in manifest

---

## Related Skills

Frontend:
- `odoo-owl-components` - Owl framework development
- `odoo-js-modules` - JavaScript module system
- `odoo-hoot-testing` - Frontend testing

Backend:
- `odoo19-oca-devops` - OCA compliance
- `odoo-module-scaffold` - Module generation
- `odoo-agile-scrum-devops` - Development workflow

Domain:
- `odoo-finance-automation` - Finance automation
- `bir-tax-filing` - BIR compliance
- `odoo-github-integration` - GitHub workflows

## Resources

- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [OCA Guidelines](https://github.com/OCA/maintainer-tools)
- [QWeb Reference](https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html)
- [Testing Guide](https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html)
- [Performance Tips](https://www.odoo.com/documentation/19.0/developer/reference/backend/performance.html)
