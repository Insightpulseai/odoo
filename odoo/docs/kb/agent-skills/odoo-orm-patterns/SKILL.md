---
name: odoo_orm_patterns
description: Odoo 19 ORM operations, recordsets, domains, and compute patterns
category: backend
priority: critical
version: "1.0"
---

# ORM Patterns

## Recordset Operations

### Read Operations

```python
# Browse by ID (returns recordset, no DB query until field access)
record = self.env['res.partner'].browse(42)
records = self.env['res.partner'].browse([1, 2, 3])

# Search (returns recordset)
partners = self.env['res.partner'].search([
    ('is_company', '=', True),
    ('country_id.code', '=', 'PH'),
], limit=10, order='name ASC')

# Search and read (returns list of dicts — use for reporting/export only)
data = self.env['res.partner'].search_read(
    domain=[('is_company', '=', True)],
    fields=['name', 'email', 'phone'],
    limit=10,
)

# Count
count = self.env['res.partner'].search_count([
    ('is_company', '=', True),
])
```

### Write Operations

```python
# Create single record
partner = self.env['res.partner'].create({
    'name': 'Test Partner',
    'email': 'test@example.com',
})

# Create multiple records (batch — preferred)
partners = self.env['res.partner'].create([
    {'name': 'Partner A'},
    {'name': 'Partner B'},
])

# Update
partner.write({'phone': '+63 2 1234 5678'})

# Delete
partner.unlink()

# Copy (duplicate with defaults)
new_partner = partner.copy(default={'name': 'Copy of Partner'})
```

### Recordset Methods

```python
# Filter (returns subset matching predicate)
active_partners = partners.filtered(lambda p: p.active and p.email)

# Also accepts string for simple field truthy check
active_partners = partners.filtered('active')

# Map (returns recordset for relational fields, list for others)
emails = partners.mapped('email')            # ['a@b.com', 'c@d.com']
countries = partners.mapped('country_id')    # recordset of res.country
child_emails = partners.mapped('child_ids.email')  # dotted path traversal

# Sort
sorted_partners = partners.sorted(key=lambda p: p.name)
sorted_partners = partners.sorted('name', reverse=True)

# Exists (filter out deleted records)
if record.exists():
    record.do_something()

# Set operations
combined = records_a | records_b     # union
common = records_a & records_b       # intersection
diff = records_a - records_b         # difference

# Iteration
for partner in partners:
    partner.do_something()  # each iteration: single-record recordset

# Length and membership
len(partners)           # number of records
partner in partners     # membership test
```

**NEVER** use list comprehensions on recordsets when `filtered` or `mapped` can do the job:

```python
# WRONG
emails = [p.email for p in partners if p.email]

# CORRECT
emails = partners.filtered('email').mapped('email')
```

## Domain Syntax

Domains are lists of criteria, using Polish (prefix) notation for operators.

### Basic Criteria

```python
# Simple comparisons
[('field', '=', value)]
[('field', '!=', value)]
[('field', '<', value)]
[('field', '>', value)]
[('field', '<=', value)]
[('field', '>=', value)]

# String matching
[('name', 'like', 'test')]       # case-sensitive, %test%
[('name', 'ilike', 'test')]      # case-insensitive, %test%
[('name', '=like', 'test%')]     # case-sensitive, exact pattern
[('name', '=ilike', 'Test%')]    # case-insensitive, exact pattern

# List membership
[('state', 'in', ['draft', 'confirmed'])]
[('state', 'not in', ['cancelled'])]

# Hierarchy
[('category_id', 'child_of', parent_id)]
[('category_id', 'parent_of', child_id)]
```

### Boolean Operators

Default operator between criteria is `&` (AND). Use prefix notation:

```python
# AND (default — implicit between all criteria)
[('state', '=', 'draft'), ('active', '=', True)]
# Equivalent to:
['&', ('state', '=', 'draft'), ('active', '=', True)]

# OR
['|', ('state', '=', 'draft'), ('state', '=', 'confirmed')]

# NOT
['!', ('active', '=', True)]

# Complex: (state = draft OR state = confirmed) AND active = True
['|', ('state', '=', 'draft'), ('state', '=', 'confirmed'),
 ('active', '=', True)]

# Complex: state = draft AND (type = sale OR type = purchase)
[('state', '=', 'draft'),
 '|', ('type', '=', 'sale'), ('type', '=', 'purchase')]
```

### Dotted Paths (Related Fields)

```python
# Traverse relational fields with dots
[('partner_id.country_id.code', '=', 'PH')]
[('order_line.product_id.categ_id', 'child_of', category_id)]
```

## Compute Fields

### Basic Compute

```python
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=True,          # persist to DB (required for search/group_by)
    readonly=True,       # default for compute, explicit for clarity
)

@api.depends('line_ids.price', 'line_ids.qty')
def _compute_total(self):
    for record in self:
        record.total = sum(
            line.price * line.qty for line in record.line_ids
        )
```

### Compute with Inverse

```python
display_name = fields.Char(
    compute='_compute_display_name',
    inverse='_inverse_display_name',
    store=True,
)

@api.depends('first_name', 'last_name')
def _compute_display_name(self):
    for record in self:
        record.display_name = f'{record.first_name} {record.last_name}'

def _inverse_display_name(self):
    for record in self:
        parts = (record.display_name or '').split(' ', 1)
        record.first_name = parts[0]
        record.last_name = parts[1] if len(parts) > 1 else ''
```

### Compute Rules

```python
# CORRECT: Always loop over self
@api.depends('amount', 'tax_rate')
def _compute_tax(self):
    for record in self:
        record.tax_amount = record.amount * record.tax_rate

# WRONG: Assigning without loop (breaks on multi-record recordsets)
@api.depends('amount', 'tax_rate')
def _compute_tax(self):
    self.tax_amount = self.amount * self.tax_rate  # CRASHES on multi-record
```

- `@api.depends()` is mandatory for stored compute fields
- `@api.depends()` triggers recomputation when listed fields change
- For non-stored compute fields, `@api.depends()` is optional but recommended
- `@api.depends_context('key')` for context-dependent computes (e.g., language, company)

## Context

Context is an immutable dictionary carried through the ORM call chain.

### Reading Context

```python
# Current context
ctx = self.env.context

# Specific key
lang = self.env.context.get('lang', 'en_US')
active_id = self.env.context.get('active_id')
active_ids = self.env.context.get('active_ids', [])
active_model = self.env.context.get('active_model')
```

### Modifying Context

```python
# CORRECT: with_context returns a NEW recordset with modified context
records = self.with_context(tracking_disable=True)
records.write({'name': 'Updated'})

# Add to existing context
records = self.with_context(**self.env.context, custom_key='value')

# WRONG: Never modify context dict directly
self.env.context['key'] = 'value'  # FAILS — context is frozen
```

### Common Context Keys

| Key | Purpose |
|-----|---------|
| `no_reset_password` | Skip password reset email on user create |
| `mail_create_nosubscribe` | Don't subscribe creator to record |
| `mail_notrack` | Disable field tracking (chatter) |
| `tracking_disable` | Disable all tracking and mail |
| `active_test` | `False` to include archived records in search |
| `default_<field>` | Set default value for field |
| `search_default_<filter>` | Activate a search filter |
| `allowed_company_ids` | List of companies user can access |
| `force_company` | Force specific company context |

## Command Tuples (One2many / Many2many Writes)

When writing to `One2many` or `Many2many` fields, use command tuples:

```python
# (0, 0, vals) — Create a new record and link it
record.write({'line_ids': [(0, 0, {'name': 'New Line', 'amount': 100})]})

# (1, id, vals) — Update an existing linked record
record.write({'line_ids': [(1, line_id, {'amount': 200})]})

# (2, id, 0) — Delete the linked record from DB
record.write({'line_ids': [(2, line_id, 0)]})

# (3, id, 0) — Unlink (M2M only: remove relation, keep record)
record.write({'tag_ids': [(3, tag_id, 0)]})

# (4, id, 0) — Link existing record (M2M: add relation)
record.write({'tag_ids': [(4, tag_id, 0)]})

# (5, 0, 0) — Clear all links (M2M: unlink all, O2M: delete all)
record.write({'tag_ids': [(5, 0, 0)]})

# (6, 0, [ids]) — Replace: clear all, then link these IDs
record.write({'tag_ids': [(6, 0, [tag1_id, tag2_id])]})
```

### Quick Reference Table

| Command | Args | Effect | O2M | M2M |
|---------|------|--------|-----|-----|
| `(0, 0, vals)` | dict | Create + link | Yes | Yes |
| `(1, id, vals)` | id, dict | Update linked | Yes | Yes |
| `(2, id, 0)` | id | Delete from DB | Yes | Yes |
| `(3, id, 0)` | id | Remove link only | No | Yes |
| `(4, id, 0)` | id | Add link | No | Yes |
| `(5, 0, 0)` | — | Clear all | Yes | Yes |
| `(6, 0, ids)` | id list | Replace all | No | Yes |

### Combining Commands

```python
record.write({'line_ids': [
    (0, 0, {'name': 'New Line'}),           # create new
    (1, existing_id, {'amount': 500}),       # update existing
    (2, obsolete_id, 0),                     # delete obsolete
]})
```

## Environment

### Accessing the Environment

```python
self.env                  # current environment
self.env.cr               # database cursor (NEVER commit/rollback)
self.env.uid              # current user ID (int)
self.env.user             # current user (res.users recordset)
self.env.company          # current company (res.company recordset)
self.env.companies        # accessible companies (recordset)
self.env.context          # context dict (frozen)
self.env.lang             # current language code
self.env.ref('xml_id')    # resolve XML ID to record
self.env['model.name']    # access another model's recordset
```

### Switching Environment

```python
# Sudo: bypass access rights (use sparingly)
record.sudo().write({'field': 'value'})

# Switch user
record.with_user(user_id).check_access('write')

# Switch company
record.with_company(company_id).create({...})

# Combined
record.sudo().with_company(company).with_context(lang='en_US')
```

### Sudo Rules

- Use `sudo()` only when the current user legitimately lacks rights but the operation is authorized
- Always `sudo()` at the narrowest scope possible
- Never `sudo()` on user input without validation
- Prefer `check_access_rights()` / `check_access_rule()` over blanket `sudo()`

## Hard Rules

### Never Use `cr.commit()` or `cr.rollback()`

```python
# WRONG — breaks Odoo's transaction management
self.env.cr.commit()
self.env.cr.rollback()

# CORRECT — use savepoint for error recovery
try:
    with self.env.cr.savepoint():
        risky_operation()
except Exception:
    # savepoint automatically rolled back
    handle_error()
```

Savepoint limit: max 64 nested savepoints per transaction.

### Action Methods Must Call `ensure_one()`

```python
# CORRECT
def action_confirm(self):
    self.ensure_one()
    self.state = 'confirmed'

# WRONG — will fail silently or crash on multi-record
def action_confirm(self):
    self.state = 'confirmed'
```

### Translation Strings

```python
# CORRECT — positional args via comma
raise UserError(_('Cannot delete %s in state %s.', record.name, record.state))

# WRONG — string formatting inside _()
raise UserError(_('Cannot delete %s in state %s.' % (record.name, record.state)))
raise UserError(_('Cannot delete {} in state {}.'.format(record.name, record.state)))
raise UserError(_(f'Cannot delete {record.name} in state {record.state}.'))
```

The `_()` function must receive a static string as its first argument for the translation system to extract it. Variable parts go as additional positional arguments.

### SQL Safety

```python
# CORRECT — parameterized query
self.env.cr.execute(
    "SELECT id FROM res_partner WHERE email = %s",
    (email,)
)

# WRONG — SQL injection risk
self.env.cr.execute(
    f"SELECT id FROM res_partner WHERE email = '{email}'"
)

# For table/column names (cannot be parameterized), use psycopg2.sql
from psycopg2 import sql
self.env.cr.execute(
    sql.SQL("SELECT {} FROM {}").format(
        sql.Identifier('name'),
        sql.Identifier('res_partner'),
    )
)
```

### Recordset Falsy Checks

```python
# CORRECT — check for empty recordset
if not record:
    ...
if record:
    ...

# Also CORRECT — explicit exists() after browse
record = self.env['res.partner'].browse(partner_id)
if record.exists():
    ...

# WRONG — comparing to None
if record is None:  # recordsets are never None
    ...
```
