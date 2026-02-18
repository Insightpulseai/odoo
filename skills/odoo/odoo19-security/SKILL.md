---
name: odoo19-security
description: Odoo 19 Security - Access Rights, Record Rules, Field Access, Groups, Security Pitfalls, SQL injection prevention
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/security.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Security

Comprehensive reference for Odoo 19 security mechanisms: Access Rights (ir.model.access),
Record Rules (ir.rule), Field Access, Security Groups (res.groups), and security pitfalls
including SQL injection, unsafe methods, and XSS prevention.

---

## 1. Overview

Odoo provides two main data-driven mechanisms to manage access to data:

1. **Access Rights** (ir.model.access) -- Grant CRUD access to entire models per group
2. **Record Rules** (ir.rule) -- Conditional per-record access filtering

Both are linked to users through **groups** (`res.groups`). A user belongs to any
number of groups, and security mechanisms are associated to groups.

---

## 2. Security Groups (res.groups)

### 2.1 Group Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `Char` | User-readable group name (role/purpose) |
| `category_id` | `Many2one(ir.module.category)` | Module category; converts groups to exclusive selection in user form |
| `implied_ids` | `Many2many(res.groups)` | Other groups auto-set alongside this one (pseudo-inheritance) |
| `comment` | `Text` | Additional notes |

### 2.2 Defining Groups in XML

```xml
<record id="group_project_user" model="res.groups">
    <field name="name">User</field>
    <field name="category_id" ref="base.module_category_project"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    <field name="comment">Access to project tasks and basic features.</field>
</record>

<record id="group_project_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="category_id" ref="base.module_category_project"/>
    <field name="implied_ids" eval="[(4, ref('group_project_user'))]"/>
</record>
```

### 2.3 Common Built-in Groups

| External ID | Description |
|-------------|-------------|
| `base.group_user` | Internal User (Employee) |
| `base.group_system` | Settings (Administrator) |
| `base.group_erp_manager` | Access Rights (Technical) |
| `base.group_no_one` | Technical Features (debug mode) |
| `base.group_public` | Public User |
| `base.group_portal` | Portal User |
| `base.group_multi_company` | Multi-company |

### 2.4 Checking Group Membership in Python

```python
# Check if current user has a specific group
if self.env.user.has_group('project.group_project_manager'):
    # manager-level logic
    pass

# Alternative via env
if self.env.is_admin():
    pass
if self.env.is_system():
    pass
```

---

## 3. Access Rights (ir.model.access)

### 3.1 Concept

Access rights **grant** access to an entire model for a given set of CRUD operations.
If no access rights matches an operation for a user's groups, the user has **no access**.

Access rights are **additive**: a user's accesses are the union of all accesses through
all their groups. Example: Group A grants read+create, Group B grants update.
The user in both groups gets read+create+update.

### 3.2 ir.model.access Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `Char` | Description of the access rule |
| `model_id` | `Many2one(ir.model)` | Model whose access is controlled |
| `group_id` | `Many2one(res.groups)` | Group receiving access. **Empty = granted to ALL users** (including portal/public) |
| `perm_create` | `Boolean` | Grant create access |
| `perm_read` | `Boolean` | Grant read access |
| `perm_write` | `Boolean` | Grant write access |
| `perm_unlink` | `Boolean` | Grant delete access |

### 3.3 CSV Format (Standard Practice)

Access rights are typically defined in `security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_project_task_user,project.task user,model_project_task,project.group_project_user,1,1,1,0
access_project_task_manager,project.task manager,model_project_task,project.group_project_manager,1,1,1,1
access_project_task_portal,project.task portal,model_project_task,base.group_portal,1,0,0,0
```

**Column Reference:**

| Column | Description |
|--------|-------------|
| `id` | External identifier for the access rule |
| `name` | Descriptive name |
| `model_id:id` | External ID of the model (`model_` + model name with `.` replaced by `_`) |
| `group_id:id` | External ID of the group (empty = all users) |
| `perm_read` | `1` or `0` |
| `perm_write` | `1` or `0` |
| `perm_create` | `1` or `0` |
| `perm_unlink` | `1` or `0` |

### 3.4 Registering in __manifest__.py

```python
{
    'name': 'My Module',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}
```

### 3.5 Public Access (No Group)

An empty `group_id` grants access to **every** user, including non-employees
(portal, public). Use this sparingly:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_public_info,public.info public,model_public_info,,1,0,0,0
```

### 3.6 Complete Access Rights Example

For a module `ipai_project` with model `ipai.project.task`:

**File: `security/ir.model.access.csv`**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ipai_project_task_user,ipai.project.task user,model_ipai_project_task,project.group_project_user,1,1,1,0
access_ipai_project_task_manager,ipai.project.task manager,model_ipai_project_task,project.group_project_manager,1,1,1,1
```

---

## 4. Record Rules (ir.rule)

### 4.1 Concept

Record rules are **conditions** that must be satisfied for an operation to be
allowed on individual records. They are evaluated **after** access rights.

Record rules are **default-allow**: if access rights grant access and no rule applies
to the operation/model for the user, access is granted.

### 4.2 ir.rule Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `Char` | Description of the rule |
| `model_id` | `Many2one(ir.model)` | Model the rule applies to |
| `groups` | `Many2many(res.groups)` | Groups the rule applies to. **Empty = global rule** |
| `domain_force` | `Text` | Domain expression (Python) that filters records |
| `perm_create` | `Boolean` | Apply rule to create operations (default: True) |
| `perm_read` | `Boolean` | Apply rule to read operations (default: True) |
| `perm_write` | `Boolean` | Apply rule to write operations (default: True) |
| `perm_unlink` | `Boolean` | Apply rule to unlink operations (default: True) |

### 4.3 Domain Variables

The `domain_force` is a Python expression with these variables available:

| Variable | Description |
|----------|-------------|
| `time` | Python's `time` module |
| `user` | Current user as a singleton recordset |
| `company_id` | Current user's selected company ID (integer) |
| `company_ids` | All company IDs the user has access to (list) |

### 4.4 Global vs Group Rules

| Rule Type | Condition | Composition |
|-----------|-----------|-------------|
| **Global** | No groups specified | Rules **intersect** (AND). Adding global rules always restricts further. |
| **Group** | One or more groups specified | Rules **unify** (OR). Adding group rules can expand access. |

Global and group rulesets intersect with each other. The first group rule added
to a global ruleset **restricts** access.

**Danger:** Creating multiple global rules risks creating non-overlapping rulesets
that remove all access.

### 4.5 Record Rule XML Examples

**File: `security/security.xml`**

```xml
<odoo>
    <data noupdate="1">
        <!-- Global rule: users can only see records from their companies -->
        <record id="rule_task_company" model="ir.rule">
            <field name="name">Task: multi-company</field>
            <field name="model_id" ref="model_project_task"/>
            <field name="domain_force">[
                '|',
                ('company_id', '=', False),
                ('company_id', 'in', company_ids)
            ]</field>
        </record>

        <!-- Group rule: users see only their own tasks -->
        <record id="rule_task_user_own" model="ir.rule">
            <field name="name">Task: own tasks only</field>
            <field name="model_id" ref="model_project_task"/>
            <field name="groups" eval="[(4, ref('project.group_project_user'))]"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
        </record>

        <!-- Group rule: managers see all tasks -->
        <record id="rule_task_manager_all" model="ir.rule">
            <field name="name">Task: manager sees all</field>
            <field name="model_id" ref="model_project_task"/>
            <field name="groups" eval="[(4, ref('project.group_project_manager'))]"/>
            <field name="domain_force">[(1, '=', 1)]</field>
        </record>

        <!-- Rule only for read and write (not create/unlink) -->
        <record id="rule_task_portal_read" model="ir.rule">
            <field name="name">Task: portal read own</field>
            <field name="model_id" ref="model_project_task"/>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="domain_force">[('partner_id', '=', user.partner_id.id)]</field>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="False"/>
            <field name="perm_create" eval="False"/>
            <field name="perm_unlink" eval="False"/>
        </record>
    </data>
</odoo>
```

### 4.6 Common Record Rule Patterns

```xml
<!-- Only own records -->
<field name="domain_force">[('user_id', '=', user.id)]</field>

<!-- Own company or no company (shared) -->
<field name="domain_force">[
    '|',
    ('company_id', '=', False),
    ('company_id', 'in', company_ids)
]</field>

<!-- All records (manager/admin bypass) -->
<field name="domain_force">[(1, '=', 1)]</field>

<!-- Based on partner (portal) -->
<field name="domain_force">[('partner_id', '=', user.partner_id.id)]</field>

<!-- Time-based rule -->
<field name="domain_force">[('create_date', '>=', (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'))]</field>
```

---

## 5. Field Access

### 5.1 groups Attribute on Fields

Fields can restrict access via the `groups` attribute, a comma-separated string
of external identifiers:

```python
class SensitiveModel(models.Model):
    _name = 'sensitive.model'

    public_name = fields.Char()
    # Only managers can see/edit this field
    secret_data = fields.Char(groups='base.group_system')
    # Multiple groups (any of these grants access)
    financial_data = fields.Float(groups='account.group_account_manager,base.group_system')
```

### 5.2 Effect of Field Groups

If the current user is NOT in one of the listed groups:

- Restricted fields are **removed from views** automatically
- Restricted fields are **removed from `fields_get()` responses**
- Attempts to explicitly read/write restricted fields raise `AccessError`

### 5.3 Field Groups in XML Views

You can also restrict field visibility in views (but the model-level `groups`
is the security-enforced mechanism):

```xml
<field name="secret_data" groups="base.group_system"/>
```

---

## 6. Security Pitfalls

### 6.1 Unsafe Public Methods

Any public method (not starting with `_`) can be executed via RPC with
arbitrary parameters. ACL is only verified during CRUD operations.

```python
# UNSAFE: public method, arguments cannot be trusted
def action_done(self):
    if self.state == "draft" and self.env.user.has_group('base.manager'):
        self._set_state("done")

# SAFE: private method, only callable from Python
def _set_state(self, new_state):
    self.sudo().write({"state": new_state})
```

**Rules:**
- Methods starting with `_` are NOT callable from RPC
- On public methods, neither `self` (the records) nor parameters can be trusted
- Use `@api.private` to make a method non-RPC-callable without `_` prefix

### 6.2 Bypassing the ORM

Never use the database cursor directly when the ORM can do the same thing.
Bypassing the ORM skips:
- Access rights and record rules
- Translations
- Field invalidation
- Active record filtering
- Automated behaviors

```python
# WRONG: SQL injection vulnerability, bypasses ORM
self.env.cr.execute(
    'SELECT id FROM auction_lots WHERE auction_id in ('
    + ','.join(map(str, ids)) + ') AND state=%s', ('draft',)
)

# WRONG: No injection, but still bypasses ORM
self.env.cr.execute(
    'SELECT id FROM auction_lots WHERE auction_id in %s '
    'AND state=%s', (tuple(ids), 'draft')
)

# BETTER: Using SQL wrapper
from odoo.tools import SQL
self.env.cr.execute(SQL("""
    SELECT id FROM auction_lots
    WHERE auction_id IN %s AND state = %s
""", tuple(ids), 'draft'))

# BEST: Use the ORM
auction_lots = self.env['auction.lots'].search([
    ('auction_id', 'in', ids),
    ('state', '=', 'draft'),
    ('obj_price', '>', 0),
])
```

### 6.3 SQL Injection Prevention

**Never** use Python string concatenation (`+`) or string interpolation (`%`)
to build SQL queries with user input.

```python
# VERY BAD: SQL injection vulnerability
self.env.cr.execute(
    'SELECT distinct child_id FROM account_account_consol_rel '
    'WHERE parent_id IN (' + ','.join(map(str, ids)) + ')'
)

# BETTER: psycopg2 parameterization
self.env.cr.execute(
    'SELECT DISTINCT child_id '
    'FROM account_account_consol_rel '
    'WHERE parent_id IN %s',
    (tuple(ids),)
)

# BEST: SQL wrapper
from odoo.tools import SQL
self.env.cr.execute(SQL("""
    SELECT DISTINCT child_id
    FROM account_account_consol_rel
    WHERE parent_id IN %s
""", tuple(ids)))
```

### 6.4 Safe Domain Building

Never manipulate domain lists directly with user input. Use the `Domain` class:

```python
from odoo.fields import Domain

# BAD: user can inject domain like ['|', ('id', '>', 0)]
domain = ...  # passed by the user
security_domain = [('user_id', '=', self.env.uid)]
domain += security_domain  # side-effect if function argument
self.search(domain)

# GOOD: Domain class handles safe composition
domain = Domain(...)
domain &= Domain('user_id', '=', self.env.uid)
self.search(domain)
```

### 6.5 XSS Prevention (Unescaped Content)

Never use `t-raw` in QWeb templates with untrusted data:

```xml
<!-- BAD: XSS vulnerability -->
<div t-name="insecure_template">
    <div id="information-bar"><t t-raw="info_message"/></div>
</div>

<!-- GOOD: Use t-esc for text content -->
<div t-name="secure_template">
    <div id="information-bar">
        <div class="info"><t t-esc="message"/></div>
        <div class="subject"><t t-esc="subject"/></div>
    </div>
</div>
```

### 6.6 markupsafe.Markup for Safe HTML

`Markup` is a string subclass that auto-escapes parameters when combined:

```python
from markupsafe import Markup, escape

# Markup auto-escapes concatenated strings
>>> Markup('<em>Hello</em> ') + '<foo>'
Markup('<em>Hello</em> &lt;foo&gt;')

# Markup auto-escapes format parameters
>>> Markup('<em>Hello</em> %s') % '<foo>'
Markup('<em>Hello</em> &lt;foo&gt;')

# Safe HTML generation
>>> Markup("<strong>%s</strong>") % user_input
# user_input is automatically escaped

# Create safe content from record field
def get_name(self, to_html=False):
    if to_html:
        return Markup("<strong>%s</strong>") % self.name
    else:
        return self.name
```

**Important patterns:**

```python
# GOOD: Structure in Markup, data via %s
>>> Markup("<p>Foo %s</p>") % bar

# BAD: bar is not escaped (inserted before Markup wrapping)
>>> Markup("<p>Foo %s</p>" % bar)

# BAD: fstring inserts before escaping
>>> Markup(f"<p>Foo {self.bar}</p>")

# GOOD: use .format() for Markup
>>> Markup("<p>Foo {bar}</p>").format(bar=self.bar)

# Combining Markup objects
>>> link = Markup("<a>%s</a>") % self.name
>>> message = escape("Click %s") % link  # GOOD
>>> message = "Click %s" % link           # BAD (result is plain str)

# Separating structure from content
>>> Markup("<p>") + "Hello <R&D>" + Markup("</p>")
Markup('<p>Hello &lt;R&amp;D&gt;</p>')
```

### 6.7 Markup with Translations

```python
from markupsafe import Markup

# Translation with Markup parameters auto-escapes the translation
>>> Markup("<p>%s</p>") % _("Hello <R&D>")
Markup('<p>Bonjour &lt;R&amp;D&gt;</p>')

>>> _("Order %s has been confirmed", Markup("<a>%s</a>") % order.name)
Markup('Order <a>SO42</a> has been confirmed')
```

### 6.8 Escaping vs Sanitizing

**Escaping** converts TEXT to CODE. Mandatory every time you mix data with code.

```python
from odoo.tools import html_escape, html_sanitize

data = "<R&D>"  # TEXT from external source

# Escaping: TEXT -> CODE (always safe)
code = html_escape(data)  # => Markup('&lt;R&amp;D&gt;')

# Mix with other code safely
self.website_description = Markup("<strong>%s</strong>") % code
```

**Sanitizing** converts CODE to SAFER CODE. Only needed when code is untrusted.

```python
# Sanitizing without escaping is BROKEN
>>> html_sanitize(data)
Markup('')  # data is corrupted!

# Sanitizing AFTER escaping is OK
>>> html_sanitize(code)
Markup('<p>&lt;R&amp;D&gt;</p>')

# Sanitizing with options
>>> html_sanitize(code, strip_classes=True)  # removes CSS classes
```

### 6.9 Avoiding eval()

```python
# VERY BAD: arbitrary code execution
domain = eval(self.filter_domain)

# BAD: still powerful, only for trusted users
from odoo.tools import safe_eval
domain = safe_eval(self.filter_domain)

# GOOD: safe literal parsing
from ast import literal_eval
domain = literal_eval(self.filter_domain)
```

**Parsing alternatives:**

| Language | Data type | Safe Parser |
|----------|-----------|-------------|
| Python | int, float | `int()`, `float()` |
| Python | dict/list | `json.loads()`, `ast.literal_eval()` |
| JavaScript | int, float | `parseInt()`, `parseFloat()` |
| JavaScript | object, list | `JSON.parse()` |

### 6.10 Safe Dynamic Field Access

```python
# UNSAFE: getattr can access private attributes and methods
def _get_state_value(self, res_id, state_field):
    record = self.sudo().browse(res_id)
    return getattr(record, state_field, False)

# SAFE: __getitem__ only accesses fields
def _get_state_value(self, res_id, state_field):
    record = self.sudo().browse(res_id)
    return record[state_field]
```

---

## 7. Complete Security Setup Example

### 7.1 Module Structure

```
ipai_project_ext/
├── __manifest__.py
├── models/
│   └── project_task.py
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
└── views/
    └── project_task_views.xml
```

### 7.2 __manifest__.py

```python
{
    'name': 'IPAI Project Extension',
    'version': '19.0.1.0.0',
    'depends': ['project'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
    ],
}
```

### 7.3 security/security.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- Custom groups -->
    <record id="group_task_auditor" model="res.groups">
        <field name="name">Task Auditor</field>
        <field name="category_id" ref="base.module_category_project"/>
        <field name="implied_ids" eval="[(4, ref('project.group_project_user'))]"/>
    </record>

    <data noupdate="1">
        <!-- Global rule: multi-company -->
        <record id="rule_ipai_task_company" model="ir.rule">
            <field name="name">IPAI Task: multi-company</field>
            <field name="model_id" ref="model_ipai_project_task"/>
            <field name="domain_force">[
                '|',
                ('company_id', '=', False),
                ('company_id', 'in', company_ids)
            ]</field>
        </record>

        <!-- Group rule: regular users see own tasks -->
        <record id="rule_ipai_task_user" model="ir.rule">
            <field name="name">IPAI Task: user own</field>
            <field name="model_id" ref="model_ipai_project_task"/>
            <field name="groups" eval="[(4, ref('project.group_project_user'))]"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
        </record>

        <!-- Group rule: managers see all -->
        <record id="rule_ipai_task_manager" model="ir.rule">
            <field name="name">IPAI Task: manager all</field>
            <field name="model_id" ref="model_ipai_project_task"/>
            <field name="groups" eval="[(4, ref('project.group_project_manager'))]"/>
            <field name="domain_force">[(1, '=', 1)]</field>
        </record>

        <!-- Group rule: auditors can read all, write none -->
        <record id="rule_ipai_task_auditor" model="ir.rule">
            <field name="name">IPAI Task: auditor read all</field>
            <field name="model_id" ref="model_ipai_project_task"/>
            <field name="groups" eval="[(4, ref('group_task_auditor'))]"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="False"/>
            <field name="perm_create" eval="False"/>
            <field name="perm_unlink" eval="False"/>
        </record>
    </data>
</odoo>
```

### 7.4 security/ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ipai_project_task_user,ipai.project.task user,model_ipai_project_task,project.group_project_user,1,1,1,0
access_ipai_project_task_manager,ipai.project.task manager,model_ipai_project_task,project.group_project_manager,1,1,1,1
access_ipai_project_task_auditor,ipai.project.task auditor,model_ipai_project_task,group_task_auditor,1,0,0,0
```

### 7.5 Model with Security Considerations

```python
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

class IpaiProjectTask(models.Model):
    _name = 'ipai.project.task'
    _description = 'IPAI Project Task'

    name = fields.Char(required=True)
    description = fields.Html(sanitize=True)  # sanitize untrusted HTML
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # Field-level security: only managers see this
    internal_notes = fields.Text(groups='project.group_project_manager')
    cost = fields.Monetary(
        currency_field='currency_id',
        groups='account.group_account_manager,base.group_system',
    )
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # Public method: must validate carefully
    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("Only draft tasks can be confirmed.")
            record.write({'state': 'confirmed'})

    # Private method: safe from RPC
    def _force_state(self, new_state):
        self.sudo().write({'state': new_state})
```

---

## 8. sudo() and Security Context

### 8.1 When to Use sudo()

```python
# Bypass access rights (run as superuser)
all_records = self.env['model'].sudo().search([])

# Common pattern: read data from another model the user can't access
company_setting = self.env['ir.config_parameter'].sudo().get_param('my.setting')

# Write as superuser
record.sudo().write({'internal_field': value})
```

### 8.2 sudo() Pitfalls

```python
# WRONG: sudo() doesn't protect against SQL injection
self.sudo().env.cr.execute("SELECT * FROM users WHERE id = " + user_input)

# WRONG: sudo() on user-provided record IDs without validation
record = self.env['sensitive.model'].sudo().browse(user_provided_id)
record.write({'admin_field': 'hacked'})  # no access check!

# CORRECT: validate first, then sudo for specific operations
record = self.env['sensitive.model'].browse(user_provided_id)  # access check happens
record.sudo().write({'system_field': computed_value})
```

### 8.3 Reverting sudo()

```python
# Get back to normal user context
normal_records = sudo_records.sudo(False)
```

---

## 9. Security Checklist

### 9.1 For Every New Model

1. Define access rights in `security/ir.model.access.csv`
2. Consider record rules in `security/security.xml` for multi-company and ownership
3. Use `groups` attribute on sensitive fields
4. Mark internal methods as private (`_` prefix or `@api.private`)
5. Sanitize HTML fields (`sanitize=True`)

### 9.2 For Every Public Method

1. Validate `self` records (don't trust the recordset)
2. Validate all parameters
3. Use `sudo()` sparingly and only for specific operations
4. Never expose internal state through return values

### 9.3 For Every SQL Query

1. Use `SQL()` wrapper or psycopg2 parameterization
2. Never concatenate user input into queries
3. Flush relevant fields before querying
4. Invalidate cache after modifications
5. Prefer ORM methods over raw SQL

### 9.4 For Every Template/View

1. Use `t-esc` not `t-raw` for user-provided content
2. Use `Markup` for safe HTML construction
3. Escape before combining text with HTML
4. Sanitize when displaying untrusted HTML content
