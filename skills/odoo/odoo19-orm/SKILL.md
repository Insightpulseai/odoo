---
name: odoo19-orm
description: Odoo 19 ORM API - Models, Fields, Recordsets, CRUD, Domains, Environment, Inheritance, Decorators
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/orm.rst"
  extracted: "2026-02-17"
---

# Odoo 19 ORM API

Comprehensive reference for the Odoo 19 Object-Relational Mapping layer, covering Models,
Fields, Recordsets, CRUD operations, Domains, Environment, SQL execution, Inheritance
mechanisms, and API decorators.

---

## 1. Models

### 1.1 Model Types

Odoo provides three model base classes in `odoo.models`:

| Class | `_auto` | `_abstract` | `_transient` | Purpose |
|-------|---------|-------------|--------------|---------|
| `Model` | `True` | `False` | `False` | Regular persistent models with database tables |
| `TransientModel` | `True` | `False` | `True` | Temporary data (wizards); auto-vacuumed |
| `AbstractModel` | `False` | `True` | `False` | Shared base; no database table |

### 1.2 Model Definition

```python
from odoo import models, fields

class AModel(models.Model):
    _name = 'a.model.name'
    _description = 'A Model'

    field1 = fields.Char()
    field2 = fields.Integer(string="Field Label")
```

**Warning:** You cannot define a field and a method with the same name -- the last
one silently overwrites the former.

### 1.3 Key Model Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_name` | `str` | Model technical name (dot-notation, e.g. `'sale.order'`) |
| `_description` | `str` | User-visible model label |
| `_inherit` | `str` or `list[str]` | Parent model(s) for inheritance |
| `_inherits` | `dict` | Delegation inheritance mapping `{parent_model: fk_field}` |
| `_table` | `str` | SQL table name (auto-derived from `_name` replacing `.` with `_`) |
| `_rec_name` | `str` | Field used as display name (default: `'name'`) |
| `_order` | `str` | Default sort order (default: `'id'`) |
| `_auto` | `bool` | Whether to create a database table |
| `_log_access` | `bool` | Whether to generate `create_date`, `write_date`, etc. |
| `_parent_name` | `str` | Field name for parent (default: `'parent_id'`) |
| `_parent_store` | `bool` | Enable materialized parent path for `child_of`/`parent_of` |
| `_check_company_auto` | `bool` | Auto-check multi-company consistency |
| `_fold_name` | `str` | Field to determine folded groups in kanban |

### 1.4 TransientModel Specifics

```python
class MyWizard(models.TransientModel):
    _name = 'my.wizard'
    _description = 'My Wizard'
    _transient_max_count = 0       # max records (0 = no limit)
    _transient_max_hours = 1.0     # max age in hours
```

TransientModel records are automatically vacuumed. `_log_access` must be enabled
(always True for TransientModel).

---

## 2. Fields

### 2.1 Basic Fields

```python
from odoo import fields

active = fields.Boolean(default=True)
name = fields.Char(string="Name", required=True, translate=True)
sequence = fields.Integer(default=10)
amount = fields.Float(digits=(16, 2))
```

| Field Type | Python Type | Notes |
|------------|-------------|-------|
| `Boolean` | `bool` | |
| `Char` | `str` | `size`, `trim`, `translate` |
| `Integer` | `int` | |
| `Float` | `float` | `digits` for precision |

### 2.2 Advanced Fields

```python
description = fields.Text()
notes = fields.Html(sanitize=True)
data = fields.Binary(attachment=True)
image = fields.Image(max_width=1024, max_height=1024)
price = fields.Monetary(currency_field='currency_id')
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
], default='draft')
```

| Field Type | Python Type | Notes |
|------------|-------------|-------|
| `Text` | `str` | Multi-line, no size limit |
| `Html` | `str` (markup) | `sanitize`, `sanitize_tags`, `sanitize_attributes` |
| `Binary` | `bytes` / `str` | `attachment=True` stores in `ir.attachment` |
| `Image` | `bytes` / `str` | Extends Binary with resize |
| `Monetary` | `float` | Requires `currency_field` |
| `Selection` | `str` | List of `(value, label)` tuples or callable |

### 2.3 Date/Datetime Fields

```python
date_start = fields.Date(default=fields.Date.today)
deadline = fields.Date()
timestamp = fields.Datetime(default=fields.Datetime.now)
```

**Datetime storage:** Stored as `timestamp without timezone` in UTC. Timezone
conversion is handled client-side.

**Helpers:**

```python
# Conversion
fields.Date.to_date(string_or_date)
fields.Datetime.to_datetime(string_or_datetime)

# Arithmetic
fields.Date.add(date_value, days=0, weeks=0, months=0, years=0)
fields.Date.subtract(date_value, days=0, weeks=0, months=0, years=0)
fields.Date.start_of(date_value, 'month')  # 'year', 'quarter', 'month', 'week', 'day'
fields.Date.end_of(date_value, 'month')

# Context-aware
fields.Date.today()            # date in UTC
fields.Date.context_today(record)  # date in user's timezone
fields.Datetime.now()          # datetime in UTC
fields.Datetime.context_timestamp(record, timestamp)  # convert to user tz
```

**Comparison rules:**
- Date fields can ONLY be compared to `date` objects.
- Datetime fields can ONLY be compared to `datetime` objects.
- Never compare date strings with datetime strings.

### 2.4 Relational Fields

```python
# Many2one: FK to another model
partner_id = fields.Many2one('res.partner', string="Partner", ondelete='cascade')

# One2many: Virtual reverse of Many2one
order_line_ids = fields.One2many('sale.order.line', 'order_id', string="Order Lines")

# Many2many: Cross-reference table
tag_ids = fields.Many2many('project.tags', string="Tags")
# With explicit relation table:
tag_ids = fields.Many2many(
    'project.tags',
    'project_task_tag_rel',  # relation table
    'task_id',               # column for this model
    'tag_id',                # column for comodel
    string="Tags",
)
```

### 2.5 Command Class (for relational write operations)

Use `Command` to manipulate relational fields in `create()` and `write()`:

```python
from odoo.fields import Command

# One2many / Many2many commands:
Command.create(values)         # (0, 0, values)  -- create new record and link
Command.update(id, values)     # (1, id, values)  -- update linked record
Command.delete(id)             # (2, id, 0)       -- delete record and unlink
Command.unlink(id)             # (3, id, 0)       -- unlink (M2M only)
Command.link(id)               # (4, id, 0)       -- link existing record
Command.clear()                # (5, 0, 0)        -- unlink all
Command.set(ids)               # (6, 0, ids)      -- replace with ids list

# Example usage:
record.write({
    'line_ids': [
        Command.create({'name': 'New Line', 'qty': 5}),
        Command.update(line_id, {'qty': 10}),
        Command.delete(old_line_id),
    ],
    'tag_ids': [
        Command.link(tag1_id),
        Command.unlink(tag2_id),
        Command.set([tag1_id, tag3_id]),
    ],
})
```

### 2.6 Pseudo-relational Fields

```python
# Reference: polymorphic Many2one (selection of model + id)
ref = fields.Reference(
    selection=[('res.partner', 'Partner'), ('res.users', 'User')],
    string="Reference",
)

# Many2oneReference: like Many2one but model stored in another field
res_id = fields.Many2oneReference(model_field='res_model')
res_model = fields.Char()
```

### 2.7 Computed Fields

```python
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total = fields.Float(compute='_compute_total', store=True)

    @api.depends('line_ids.price_subtotal')
    def _compute_total(self):
        for record in self:
            record.total = sum(record.line_ids.mapped('price_subtotal'))
```

**Key parameters:**

| Parameter | Description |
|-----------|-------------|
| `compute` | Method name for computing the value |
| `store` | `True` to persist in DB (enables search/group) |
| `compute_sudo` | Default `True` for stored fields; run compute as superuser |
| `inverse` | Method name for reverse computation (makes field writable) |
| `search` | Method name returning a domain (enables search on non-stored) |
| `readonly` | Default `True` for computed; set `False` with `inverse` |

**Inverse example:**

```python
document = fields.Char(compute='_get_document', inverse='_set_document')

def _get_document(self):
    for record in self:
        with open(record.get_document_path) as f:
            record.document = f.read()

def _set_document(self):
    for record in self:
        if not record.document:
            continue
        with open(record.get_document_path()) as f:
            f.write(record.document)
```

**Search on computed field:**

```python
upper_name = fields.Char(compute='_compute_upper', search='_search_upper')

def _search_upper(self, operator, value):
    if operator == 'like':
        operator = 'ilike'
    return Domain('name', operator, value)
```

**Multi-field compute:**

```python
discount_value = fields.Float(compute='_apply_discount')
total = fields.Float(compute='_apply_discount')

@api.depends('value', 'discount')
def _apply_discount(self):
    for record in self:
        discount = record.value * record.discount
        record.discount_value = discount
        record.total = record.value - discount
```

### 2.8 Related Fields

A special case of computed fields that proxy a sub-field value:

```python
partner_name = fields.Char(related='partner_id.name', store=True, readonly=True)

# With explicit dependency (only recompute when partner_id changes, not partner name):
nickname = fields.Char(
    related='partner_id.name', store=True,
    depends=['partner_id'],
)
```

**Defaults:** not stored, not copied, readonly, computed in superuser mode.

**Limitation:** Cannot chain Many2many or One2many in related field paths.
Supported: `m2o_id.m2m_ids`, `m2o_id.o2m_ids`. Not supported: `m2m_ids.m2m_ids`.

### 2.9 Default Values

```python
# Static default
name = fields.Char(default="a value")

# Dynamic default (callable)
def _default_name(self):
    return self.get_value()

name = fields.Char(default=lambda self: self._default_name())
```

### 2.10 Automatic Fields

Every model automatically has:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `Integer` | Database identifier |
| `display_name` | `Char` | Computed from `_rec_name` or `_compute_display_name` |
| `create_date` | `Datetime` | When record was created (if `_log_access`) |
| `create_uid` | `Many2one(res.users)` | Who created the record |
| `write_date` | `Datetime` | Last update timestamp |
| `write_uid` | `Many2one(res.users)` | Who last updated |

### 2.11 Reserved Field Names

| Field | Type | Purpose |
|-------|------|---------|
| `name` | `Char` | Default `_rec_name`, display in listings |
| `active` | `Boolean` | Toggle visibility; `False` hides from searches |
| `state` | `Selection` | Lifecycle stages |
| `parent_id` | `Many2one` | Tree structure, enables `child_of`/`parent_of` |
| `parent_path` | `Char` | Materialized path when `_parent_store=True` |
| `company_id` | `Many2one(res.company)` | Multi-company field |

**Archive/unarchive methods:**

```python
records.action_archive()    # set active=False
records.action_unarchive()  # set active=True
```

---

## 3. Constraints and Indexes

```python
class AModel(models.Model):
    _name = 'a.model'

    # SQL CHECK constraint
    _my_check = models.Constraint("CHECK (x > y)", "x must be greater than y")

    # Database index
    _name_idx = models.Index("(last_name, first_name)")

    # Unique index
    _code_uniq = models.UniqueIndex("(code)")
```

Constraint names must start with `_`. Error messages can be strings (auto-translated)
or functions `(env, diag) -> str`.

---

## 4. Recordsets

### 4.1 Basics

Recordsets are ordered collections of records of the same model. `self` in model
methods is always a recordset.

```python
class AModel(models.Model):
    _name = 'a.model'

    def a_method(self):
        # self can be 0 to all records
        self.do_operation()

    def do_operation(self):
        print(self)       # => a.model(1, 2, 3, 4, 5)
        for record in self:
            print(record)  # => a.model(1), a.model(2), ...
```

### 4.2 Field Access (Active Record Pattern)

```python
>>> record.name
'Example Name'
>>> record.company_id.name
'Company Name'
>>> record.name = "Bob"      # triggers DB update

# Dynamic field access (safe):
>>> field = "name"
>>> record[field]
'Bob'
```

**Warning:** Reading a non-relational field on multi-record recordset raises an error.
Relational fields always return a recordset (empty if not set).

### 4.3 Multi-record Field Access

```python
# Use mapped() for non-relational fields on multi-record sets:
total_qty = sum(self.mapped('qty'))

# Multi-relational field access (since V13):
records.partner_id            # == records.mapped('partner_id')
records.partner_id.bank_ids   # == records.mapped('partner_id.bank_ids')
records.partner_id.mapped('name')  # == records.mapped('partner_id.name')
```

### 4.4 Record Cache and Prefetching

The ORM caches field values and prefetches to minimize queries:

```python
record.name    # first access: reads from DB (prefetches all simple fields)
record.name    # second access: from cache

# Prefetching across iteration:
for partner in partners:       # 1000 records
    print(partner.name)        # 1 query total (prefetches all partners)
    print(partner.lang)        # 0 extra queries (prefetched with name)

# Secondary record prefetching:
countries = set()
for partner in partners:
    country = partner.country_id    # prefetches all partners' country_id
    countries.add(country.name)     # prefetches all countries' name
# Total: only 2 queries
```

Use `search_fetch()` and `fetch()` to manually populate the cache.

### 4.5 Recordset Operations

```python
# Membership
record in recordset
record not in recordset

# Comparison
set1 <= set2   # subset
set1 < set2    # strict subset
set1 >= set2   # superset
set1 > set2    # strict superset

# Set operations
set1 | set2    # union
set1 & set2    # intersection
set1 - set2    # difference
```

### 4.6 Filter, Map, Sort, Group

```python
# Filter by callable
adults = partners.filtered(lambda p: p.age >= 18)

# Filter by field (truthy)
active_partners = partners.filtered('active')

# Filter by domain
ready = records.filtered_domain([('state', '=', 'ready')])

# Map to field values
names = partners.mapped('name')                 # list of strings
partner_records = orders.mapped('partner_id')   # recordset

# Sort
sorted_partners = partners.sorted(key=lambda p: p.name)
sorted_partners = partners.sorted('name', reverse=True)

# Group by field
grouped = partners.grouped('country_id')
# Returns dict: {country_record: partner_recordset, ...}
```

### 4.7 Recordset Information

```python
recordset.ids        # list of record IDs
recordset.env        # Environment
recordset.exists()   # filter to existing records only
recordset.ensure_one()  # assert exactly 1 record, return it
record.get_metadata()   # creation info, xmlid, etc.
```

---

## 5. Common ORM Methods (CRUD)

### 5.1 Create

```python
# Single record
record = self.env['res.partner'].create({
    'name': 'New Partner',
    'email': 'new@example.com',
})

# Batch create (list of dicts)
records = self.env['res.partner'].create([
    {'name': 'Partner A'},
    {'name': 'Partner B'},
])
```

### 5.2 Read

```python
# Browse by ID(s) -- returns recordset
record = self.env['res.partner'].browse(42)
records = self.env['res.partner'].browse([1, 2, 3])

# Read field values as dicts (rarely needed, prefer attribute access)
data = records.read(['name', 'email'])
# Returns: [{'id': 1, 'name': '...', 'email': '...'}, ...]

# Read group (aggregation)
results = self.env['sale.order']._read_group(
    domain=[('state', '=', 'sale')],
    groupby=['partner_id'],
    aggregates=['amount_total:sum'],
)
# Returns list of tuples: [(partner_record, sum_value), ...]
```

### 5.3 Search

```python
# Search returns recordset
partners = self.env['res.partner'].search([
    ('is_company', '=', True),
    ('country_id.code', '=', 'US'),
], limit=10, order='name asc')

# Search count
count = self.env['res.partner'].search_count([('is_company', '=', True)])

# Search + fetch (populates cache for specified fields)
partners = self.env['res.partner'].search_fetch(
    [('is_company', '=', True)],
    ['name', 'email', 'phone'],
    limit=100,
)

# Name search (search by name with operator)
results = self.env['res.partner'].name_search('Acme', operator='ilike', limit=10)
# Returns: [(id, display_name), ...]

# Fetch specific fields into cache for known recordset
partners.fetch(['street', 'city'])
```

### 5.4 Write

```python
record.write({
    'name': 'Updated Name',
    'email': 'updated@example.com',
})

# Direct attribute assignment also works:
record.name = 'Updated Name'

# Relational field updates use Command:
record.write({
    'child_ids': [
        Command.create({'name': 'Child 1'}),
        Command.link(existing_child_id),
    ],
})
```

### 5.5 Copy

```python
new_record = record.copy()
new_record = record.copy(default={'name': 'Copy of ' + record.name})
```

### 5.6 Unlink (Delete)

```python
records.unlink()
```

### 5.7 Default Values

```python
defaults = self.env['res.partner'].default_get(['name', 'country_id'])
# Returns: {'name': ..., 'country_id': ...}
```

### 5.8 Name Create

```python
# Quick create from name only
partner_id, name = self.env['res.partner'].name_create("New Partner")
```

### 5.9 Fields Introspection

```python
fields_info = self.env['res.partner'].fields_get(['name', 'email'])
# Returns dict of field metadata
```

---

## 6. Search Domains

### 6.1 Domain Class (Odoo 19)

```python
from odoo.fields import Domain

# Simple conditions
d1 = Domain('name', '=', 'abc')
d2 = Domain('phone', 'like', '7620')

# Combine
d3 = d1 & d2       # AND
d4 = d1 | d2       # OR
d5 = ~d1            # NOT

# Combine many
Domain.AND([d1, d2, d3])
Domain.OR([d4, d5])

# Constants
Domain.TRUE    # always true
Domain.FALSE   # always false
```

### 6.2 Domain Operators

| Operator | Description |
|----------|-------------|
| `=` | equals |
| `!=` | not equals |
| `>`, `>=`, `<`, `<=` | comparisons |
| `=?` | unset or equals (True if value is None/False) |
| `like` / `not like` | pattern match `%value%` |
| `ilike` / `not ilike` | case-insensitive like |
| `=like` / `not =like` | exact pattern (`_` = any char, `%` = any string) |
| `=ilike` / `not =ilike` | case-insensitive =like |
| `in` / `not in` | membership in collection |
| `child_of` | descendant of value |
| `parent_of` | ascendant of value |
| `any` / `not any` | matches if any related record satisfies domain |
| `any!` / `not any!` | like `any` but bypasses access checks |

### 6.3 Domain Examples

```python
# Partners named 'ABC' with phone or mobile containing '7620'
Domain('name', '=', 'ABC') & (
    Domain('phone', 'ilike', '7620') | Domain('mobile', 'ilike', '7620')
)

# Sales orders to invoice with out-of-stock products
Domain('invoice_status', '=', 'to invoice') \
    & Domain('order_line', 'any', Domain('product_id.qty_available', '<=', 0))

# Partners born in February (date granularity)
Domain('birthday.month_number', '=', 2)
```

### 6.4 Date Granularity in Domains

Supported granularities: `year_number`, `quarter_number`, `month_number`,
`iso_week_number`, `day_of_week`, `day_of_month`, `day_of_year`,
`hour_number`, `minute_number`, `second_number`.

### 6.5 Dynamic Time Values

```python
Domain('some_date', '<', 'now')          # current datetime
Domain('some_date', '<', 'today')        # today at midnight
Domain('some_date', '<', '-3d +1H')      # now - 3 days + 1 hour
Domain('some_date', '<', '=3H')          # today at 03:00:00
Domain('some_date', '<', '=5d')          # 5th of current month at midnight
Domain('some_date', '<', '=1m')          # January, same day of month
Domain('some_date', '>=', '=monday -1w') # Monday of previous week
```

**Syntax:** Space-separated terms. First optional term: `today` or `now`.
Then `+`/`-`/`=` + integer + unit (`d`, `w`, `m`, `y`, `H`, `M`, `S`)
or lowercase weekday.

### 6.6 Serialization

```python
# From list to Domain
domain = Domain([('name', '=', 'abc'), ('phone', 'like', '7620')])

# From Domain to list
domain_list = list(domain)
# ['&', ('name', '=', 'abc'), ('phone', 'like', '7620')]
```

### 6.7 Domain Utilities

```python
domain.iter_conditions()   # iterate over leaf conditions
domain.map_conditions(fn)  # transform conditions
domain.optimize()          # simplify domain
domain.validate(model)     # validate against model
```

---

## 7. Environment

### 7.1 Accessing the Environment

```python
>>> records.env
<Environment object ...>
>>> records.env.uid
3
>>> records.env.user
res.users(3)
>>> records.env.cr
<Cursor object ...>
>>> records.env.company
res.company(1)
>>> records.env.companies
res.company(1, 2)
>>> records.env.lang
'en_US'
```

### 7.2 Getting Recordsets from Environment

```python
# Empty recordset of another model
partners = self.env['res.partner']

# Search from env
partners = self.env['res.partner'].search([('is_company', '=', True)])
```

### 7.3 Environment Utilities

```python
# Resolve external ID
record = self.env.ref('module.external_id')

# Check user privileges
self.env.is_superuser()
self.env.is_admin()
self.env.is_system()

# Execute raw SQL (returns rows)
rows = self.env.execute_query(SQL("SELECT id, name FROM res_partner WHERE active = %s", True))
```

### 7.4 Altering the Environment

```python
# Change context
records_with_ctx = records.with_context(key='value')
records_with_ctx = records.with_context(**{'lang': 'fr_FR'})

# Change user (also changes context)
records_as_user = records.with_user(user_record_or_id)

# Change company
records_for_company = records.with_company(company_record_or_id)

# Sudo (superuser bypass)
records_sudo = records.sudo()          # run as superuser
records_sudo = records.sudo(False)     # run as current user (undo sudo)

# Full environment replacement
records_new_env = records.with_env(new_env)
```

---

## 8. SQL Execution

### 8.1 Direct SQL with odoo.tools.SQL

```python
from odoo.tools import SQL

# Safe parameterized query using SQL wrapper
self.env.cr.execute(SQL(
    "SELECT id FROM res_partner WHERE name = %s AND active = %s",
    'Acme Corp', True
))
rows = self.env.cr.fetchall()

# Using environment helper
rows = self.env.execute_query(SQL(
    "SELECT id, name FROM res_partner WHERE active = %s", True
))
```

### 8.2 SQL Utilities

```python
# Join SQL fragments
query = SQL(" AND ").join([
    SQL("name = %s", name),
    SQL("active = %s", True),
])

# Safe identifiers
table = SQL.identifier('res_partner')
column = SQL.identifier('res_partner', 'name')
```

### 8.3 Flushing Before SQL

The ORM delays writes. Always flush relevant data before raw SQL:

```python
# Flush everything
self.env.flush_all()

# Flush specific model fields
self.env['res.partner'].flush_model(['name', 'email'])

# Flush specific recordset fields
records.flush_recordset(['state'])
```

### 8.4 Invalidating Cache After SQL Writes

```python
# After UPDATE/INSERT/DELETE, invalidate cache:
self.env['model'].flush_model(['state'])
self.env.cr.execute("UPDATE model SET state=%s WHERE state=%s", ['new', 'old'])
self.env['model'].invalidate_model(['state'])

# Targeted invalidation
records.invalidate_recordset(['state'])

# Full invalidation
self.env.invalidate_all()
```

### 8.5 Notifying Modified Fields

After raw SQL updates, inform the framework for recomputation:

```python
self.env['model'].flush_model(['state'])
self.env.cr.execute(
    "UPDATE model SET state=%s WHERE state=%s RETURNING id",
    ['new', 'old']
)
ids = [row[0] for row in self.env.cr.fetchall()]

records = self.env['model'].browse(ids)
records.invalidate_recordset(['state'])
records.modified(['state'])  # triggers recomputation of dependents
```

---

## 9. Method Decorators

### 9.1 @api.depends

Specifies field dependencies for computed fields. Triggers recomputation when
dependencies change.

```python
@api.depends('partner_id.name', 'date_order')
def _compute_display(self):
    for record in self:
        record.display = f"{record.partner_id.name} - {record.date_order}"
```

Supports dotted paths: `'line_ids.product_id.name'`.

### 9.2 @api.depends_context

Specifies context keys that affect computed field values:

```python
@api.depends_context('company')
def _compute_tax(self):
    company = self.env.company
    ...
```

### 9.3 @api.constrains

Python-level validation. Raised as `ValidationError`:

```python
from odoo.exceptions import ValidationError

@api.constrains('age')
def _check_age(self):
    for record in self:
        if record.age < 0:
            raise ValidationError("Age cannot be negative.")
```

**Note:** Only triggered when constrained fields are in `create`/`write` values.
Dotted field names (relational) are not supported.

### 9.4 @api.onchange

Triggered by UI field changes (form view). Can modify other field values and
return warnings:

```python
@api.onchange('partner_id')
def _onchange_partner(self):
    if self.partner_id:
        self.delivery_address = self.partner_id.street
        return {
            'warning': {
                'title': 'Warning',
                'message': 'Check the delivery address',
            }
        }
```

**Note:** `self` in onchange is a virtual record (not saved to DB). Assignments
to `self` fields update the form in the UI.

### 9.5 @api.model

Marks a method as operating on the model level (not on records):

```python
@api.model
def _get_default_company(self):
    return self.env.company
```

### 9.6 @api.model_create_multi

Decorator for `create` override to handle both single dict and list of dicts:

```python
@api.model_create_multi
def create(self, vals_list):
    # vals_list is always a list of dicts
    for vals in vals_list:
        vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)
```

### 9.7 @api.ondelete

Specifies behavior when records are deleted based on conditions:

```python
@api.ondelete(at_uninstall=False)
def _unlink_check(self):
    for record in self:
        if record.state == 'posted':
            raise UserError("Cannot delete posted records.")
```

`at_uninstall=True` means the check also runs during module uninstallation.

### 9.8 @api.autovacuum

Marks a method to be called by the daily autovacuum cron:

```python
@api.autovacuum
def _gc_old_records(self):
    limit = fields.Datetime.subtract(fields.Datetime.now(), days=90)
    self.search([('create_date', '<', limit)]).unlink()
```

### 9.9 @api.private

Marks a method as private (not callable via RPC even without `_` prefix):

```python
@api.private
def sensitive_operation(self):
    ...
```

---

## 10. Inheritance and Extension

### 10.1 Classical Inheritance (new model from existing)

Creates a new model with a new table, copying fields and methods from parent:

```python
class Animal(models.Model):
    _name = 'animal'
    _description = 'Animal'
    name = fields.Char()

    def speak(self):
        return "..."

class Dog(models.Model):
    _name = 'dog'
    _inherit = ['animal']
    _description = 'Dog'

    def speak(self):
        return "Woof!"

# Two separate tables: animal and dog
```

### 10.2 Extension (in-place modification)

Extends an existing model without creating a new table. The most common
inheritance pattern:

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Add new fields
    loyalty_points = fields.Integer(default=0)

    # Override methods
    def write(self, vals):
        if 'email' in vals:
            # custom logic
            pass
        return super().write(vals)
```

**Note:** When `_inherit` is a string and `_name` is not set, `_name` defaults
to the same value as `_inherit`.

### 10.3 Delegation (composition via _inherits)

Delegates field lookup to child models. "Has one" relationship:

```python
class Screen(models.Model):
    _name = 'delegation.screen'
    _description = 'Screen'
    size = fields.Float(string='Screen Size in inches')

class Keyboard(models.Model):
    _name = 'delegation.keyboard'
    _description = 'Keyboard'
    layout = fields.Char(string='Layout')

class Laptop(models.Model):
    _name = 'delegation.laptop'
    _description = 'Laptop'
    _inherits = {
        'delegation.screen': 'screen_id',
        'delegation.keyboard': 'keyboard_id',
    }
    name = fields.Char(string='Name')
    maker = fields.Char(string='Maker')
    screen_id = fields.Many2one('delegation.screen', required=True, ondelete="cascade")
    keyboard_id = fields.Many2one('delegation.keyboard', required=True, ondelete="cascade")

# Usage:
record = env['delegation.laptop'].create({
    'screen_id': env['delegation.screen'].create({'size': 13.0}).id,
    'keyboard_id': env['delegation.keyboard'].create({'layout': 'QWERTY'}).id,
})
record.size     # => 13.0  (delegated to screen)
record.layout   # => 'QWERTY' (delegated to keyboard)
record.write({'size': 14.0})  # writes directly to delegated field
```

**Warning:** Methods are NOT inherited via delegation, only fields.
Chained `_inherits` is not well supported.

### 10.4 Fields Incremental Definition

When extending a model, redefine a field with the same name and type to
modify its attributes:

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    # Only add help text, keep all other attributes from parent
    state = fields.Selection(help="Current status of the order")
```

---

## 11. Error Management

```python
from odoo.exceptions import (
    AccessDenied,      # authentication failure
    AccessError,       # unauthorized operation
    CacheMiss,         # field value not in cache
    MissingError,      # record doesn't exist
    RedirectWarning,   # error with redirect action
    UserError,         # user-facing business error
    ValidationError,   # constraint violation
)

# Common usage:
from odoo.exceptions import UserError, ValidationError

if not record.partner_id:
    raise UserError("A partner is required.")

@api.constrains('amount')
def _check_amount(self):
    if any(r.amount < 0 for r in self):
        raise ValidationError("Amount must be positive.")
```

---

## 12. Common Patterns

### 12.1 Complete Model Definition

```python
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command, Domain

class ProjectTask(models.Model):
    _name = 'project.task'
    _description = 'Project Task'
    _order = 'sequence, id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Title", required=True, tracking=True)
    description = fields.Html()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)

    project_id = fields.Many2one('project.project', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string="Assignee", default=lambda self: self.env.user)
    tag_ids = fields.Many2many('project.tags')
    subtask_ids = fields.One2many('project.task', 'parent_id')
    parent_id = fields.Many2one('project.task', string="Parent Task")

    date_deadline = fields.Date()
    hours_planned = fields.Float()
    hours_spent = fields.Float()
    progress = fields.Float(compute='_compute_progress', store=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_uniq', 'unique(name, project_id)', 'Task name must be unique per project!'),
    ]

    @api.depends('hours_planned', 'hours_spent')
    def _compute_progress(self):
        for task in self:
            if task.hours_planned:
                task.progress = min(100, (task.hours_spent / task.hours_planned) * 100)
            else:
                task.progress = 0.0

    @api.constrains('date_deadline')
    def _check_deadline(self):
        for task in self:
            if task.date_deadline and task.date_deadline < fields.Date.today():
                raise ValidationError("Deadline cannot be in the past.")

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            self.user_id = self.project_id.user_id

    def action_start(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError("Only draft tasks can be started.")
        self.write({'state': 'in_progress'})

    def action_done(self):
        for task in self:
            task.state = 'done'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = 'New Task'
        return super().create(vals_list)
```

### 12.2 Wizard Pattern

```python
class TaskAssignWizard(models.TransientModel):
    _name = 'task.assign.wizard'
    _description = 'Assign Tasks Wizard'

    user_id = fields.Many2one('res.users', string="Assignee", required=True)
    task_ids = fields.Many2many('project.task', string="Tasks")

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        defaults['task_ids'] = [Command.set(active_ids)]
        return defaults

    def action_assign(self):
        self.ensure_one()
        self.task_ids.write({'user_id': self.user_id.id})
        return {'type': 'ir.actions.act_window_close'}
```

### 12.3 Search with Context and Sudo

```python
# Search as superuser (bypass access rules)
all_partners = self.env['res.partner'].sudo().search([])

# Search with specific context
partners = self.env['res.partner'].with_context(
    active_test=False  # include archived records
).search([])

# Search with company context
partners = self.env['res.partner'].with_company(company).search([])
```
