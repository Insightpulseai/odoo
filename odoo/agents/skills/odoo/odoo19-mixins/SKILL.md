---
name: odoo19-mixins
description: Odoo 19 mixins including mail.thread, mail.alias.mixin, mail.activity.mixin, utm.mixin, website.published.mixin, website.seo.metadata, and rating.mixin
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/mixins.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Mixins and Useful Classes

## Overview

Odoo provides reusable mixins that add common behaviors to models. This reference
covers messaging (mail.thread), email aliases, activities, UTM tracking, website
publication, SEO metadata, and customer rating mixins.

---

## mail.thread -- Messaging Integration

The most commonly used mixin. Adds chatter (messaging), followers, field tracking,
notifications, and email gateway support to any model.

### Basic Integration

```python
from odoo import fields, models

class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']
    _description = 'Business Trip'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Responsible')
    guest_ids = fields.Many2many('res.partner', 'Participants')
```

### Form View with Chatter

```xml
<record id="business_trip_form" model="ir.ui.view">
    <field name="name">business.trip.form</field>
    <field name="model">business.trip</field>
    <field name="arch" type="xml">
        <form string="Business Trip">
            <!-- Your usual form view goes here -->
            <sheet>
                <group>
                    <field name="name"/>
                    <field name="partner_id"/>
                    <field name="guest_ids" widget="many2many_tags"/>
                </group>
            </sheet>
            <!-- Chatter integration -->
            <chatter open_attachments="True"/>
        </form>
    </field>
</record>
```

### Chatter Element Options

| Option | Description |
|--------|-------------|
| `open_attachments` | Show attachment section expanded by default |
| `reload_on_attachment` | Reload form view when attachments are added/removed |
| `reload_on_follower` | Reload form view when followers are updated |
| `reload_on_post` | Reload form view when new messages are posted |

Once chatter is enabled:
- Users can add messages or internal notes on any record
- Messages send notifications to all followers
- Internal notes notify employee users (`base.group_user`) only
- Notifications can be replied to via email (if mail gateway is configured)

---

### Posting Messages

#### `message_post()`

Post a new message in an existing thread:

```python
record.message_post(
    body='The trip has been approved!',
    subject='Trip Approved',
    message_type='notification',
    subtype_xmlid='mail.mt_note',
    partner_ids=[partner.id],
    attachments=[('report.pdf', pdf_content)],
)
```

Parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `body` | `str` or `Markup` | Message body. Escaped if `str`. Use `Markup` for HTML |
| `subject` | `str` | Message subject |
| `message_type` | `str` | See `mail.message.message_type` field |
| `subtype_xmlid` | `str` | XML ID of the message subtype |
| `parent_id` | `int` | ID of parent message (for replies) |
| `attachments` | `list(tuple)` | List of `(name, content)` tuples (NOT base64) |
| `partner_ids` | `list(int)` | Additional partner IDs to notify |
| `body_is_html` | `bool` | Treat body as HTML even if `str` |

Returns: ID of newly created `mail.message` record.

#### `message_post_with_view()`

Post a message using a QWeb view template:

```python
record.message_post_with_view(
    'my_module.my_message_template',
    values={'record': record, 'data': extra_data},
    subtype_id=self.env.ref('mail.mt_comment').id,
)
```

#### `message_post_with_template()`

Post a message using a mail template:

```python
template = self.env.ref('my_module.email_template_approved')
record.message_post_with_template(template.id)
```

---

### Receiving Messages (Email Gateway)

Override these methods to process incoming emails:

#### `message_new()`

Called when a new email arrives for a given model (via alias) and does not
belong to an existing thread:

```python
def message_new(self, msg_dict, custom_values=None):
    """Create a new record from an incoming email.

    Args:
        msg_dict: dict with email details and attachments
        custom_values: optional dict of additional field values for create()
    Returns:
        int: ID of the newly created record
    """
    name = msg_dict.get('subject', 'New Record')
    # Extract data from email
    partner = self.env['res.partner'].search(
        [('email', 'ilike', msg_dict.get('email_from'))],
        limit=1
    )
    defaults = {
        'name': name,
        'partner_id': partner.id,
    }
    defaults.update(custom_values or {})
    return super().message_new(msg_dict, custom_values=defaults)
```

#### `message_update()`

Called when a new email arrives for an existing thread:

```python
def message_update(self, msg_dict, update_vals=None):
    """Update a record from an incoming email reply.

    Args:
        msg_dict: dict with email details and attachments
        update_vals: dict of values to update on the record
    Returns:
        True
    """
    if msg_dict.get('subject') and 'urgent' in msg_dict['subject'].lower():
        update_vals = update_vals or {}
        update_vals['priority'] = '1'
    return super().message_update(msg_dict, update_vals=update_vals)
```

---

### Followers Management

#### `message_subscribe()`

Add partners as followers:

```python
record.message_subscribe(
    partner_ids=[partner1.id, partner2.id],
    subtype_ids=[subtype1.id, subtype2.id],
)
```

Parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `partner_ids` | `list(int)` | Partner IDs to subscribe |
| `channel_ids` | `list(int)` | Channel IDs to subscribe |
| `subtype_ids` | `list(int)` | Subtype IDs for subscription (defaults to default subtypes) |
| `force` | `bool` | If True, delete existing followers before creating new ones |

#### `message_unsubscribe()`

Remove partners from followers:

```python
record.message_unsubscribe(partner_ids=[partner1.id])
```

#### `message_unsubscribe_users()`

Unsubscribe users (wrapper on `message_unsubscribe`):

```python
record.message_unsubscribe_users(user_ids=[user1.id])
# If user_ids is None, unsubscribes the current user
record.message_unsubscribe_users()
```

---

### Field Tracking

Add `tracking=True` to fields to automatically log changes in chatter:

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']
    _description = 'Business Trip'

    name = fields.Char(tracking=True)
    partner_id = fields.Many2one('res.partner', 'Responsible', tracking=True)
    guest_ids = fields.Many2many('res.partner', 'Participants')
    state = fields.Selection([
        ('draft', 'New'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], tracking=True)
```

Every change to a tracked field logs a note in the chatter. The `name` field
(if tracked) is displayed in notifications for context, even if unchanged.

---

### Subtypes

Subtypes classify notifications, allowing subscribers to customize which
notifications they receive.

#### Define a Subtype

```xml
<record id="mt_state_change" model="mail.message.subtype">
    <field name="name">Trip confirmed</field>
    <field name="res_model">business.trip</field>
    <field name="default" eval="True"/>
    <field name="description">Business Trip confirmed!</field>
</record>
```

#### Subtype Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Name displayed in notification customization popup (mandatory) |
| `description` | Char | Description added to posted message |
| `internal` | Boolean | Visible only to employees (`base.group_user`) |
| `parent_id` | Many2one | Link subtypes for automatic subscription (e.g., project -> task) |
| `relation_field` | Char | Field linking parent/child models (e.g., `project_id`) |
| `res_model` | Char | Model this subtype applies to (False = all models) |
| `default` | Boolean | Activated by default when subscribing |
| `sequence` | Integer | Order in notification popup |
| `hidden` | Boolean | Hidden from notification popup |

#### Override `_track_subtype()`

Map field changes to specific subtypes:

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']
    _description = 'Business Trip'

    name = fields.Char(tracking=True)
    partner_id = fields.Many2one('res.partner', 'Responsible', tracking=True)
    guest_ids = fields.Many2many('res.partner', 'Participants')
    state = fields.Selection([
        ('draft', 'New'),
        ('confirmed', 'Confirmed'),
    ], tracking=True)

    def _track_subtype(self, init_values):
        """Return subtype triggered by field changes.

        Args:
            init_values: dict of original field values before changes.
                         Only modified fields are present.
        Returns:
            mail.message.subtype record or False
        """
        self.ensure_one()
        if 'state' in init_values and self.state == 'confirmed':
            return self.env.ref('my_module.mt_state_change')
        return super(BusinessTrip, self)._track_subtype(init_values)
```

---

### Customizing Notifications

Override `_notify_get_groups()` to add custom action buttons and control
notification behavior per recipient group:

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread', 'mail.alias.mixin']
    _description = 'Business Trip'

    def action_cancel(self):
        self.write({'state': 'draft'})

    def _notify_get_groups(self, message, groups):
        """Customize notification buttons per recipient group."""
        groups = super(BusinessTrip, self)._notify_get_groups(message, groups)

        self.ensure_one()
        if self.state == 'confirmed':
            app_action = self._notify_get_action_link(
                'method', method='action_cancel'
            )
            trip_actions = [{'url': app_action, 'title': _('Cancel')}]

        new_group = (
            'group_trip_manager',
            lambda partner: any(
                user.sudo().has_group('business.group_trip_manager')
                for user in partner.user_ids
            ),
            {'actions': trip_actions},
        )

        return [new_group] + groups
```

#### Group Data Keys

| Key | Description | Default |
|-----|-------------|---------|
| `has_button_access` | Show "Access Document" button | True (new groups), False (portal/customer) |
| `button_access` | Dict with `url` and `title` | — |
| `has_button_follow` | Show "Follow" button | True (new groups), False (portal/customer) |
| `button_follow` | Dict with `url` and `title` | — |
| `has_button_unfollow` | Show "Unfollow" button | True (new groups), False (portal/customer) |
| `button_unfollow` | Dict with `url` and `title` | — |
| `actions` | List of action button dicts (`url`, `title`) | — |

Default groups: `user` (employee), `portal` (portal user), `customer` (no user).

#### `_notify_get_action_link()`

Generate action URLs for notification buttons:

```python
# Link to form view
url = self._notify_get_action_link('view')

# Assign current user to user_id field
url = self._notify_get_action_link('assign')

# Follow/unfollow
url = self._notify_get_action_link('follow')
url = self._notify_get_action_link('unfollow')

# Call a method on the record
url = self._notify_get_action_link('method', method='action_approve')

# Open a new record form
url = self._notify_get_action_link('new', action_id='my_module.my_action')
```

---

### mail.thread Context Keys

Control `mail.thread` behavior during `create()` and `write()`:

| Context Key | Effect |
|-------------|--------|
| `mail_create_nosubscribe` | Don't subscribe current user at create/message_post |
| `mail_create_nolog` | Don't log "Document created" message at create |
| `mail_notrack` | Don't perform value tracking at create/write |
| `tracking_disable` | Disable ALL MailThread features (subscriptions, tracking, posts) |
| `mail_auto_delete` | Auto-delete mail notifications (default: True) |
| `mail_notify_force_send` | Send notifications directly if < 50 emails (default: True) |
| `mail_notify_user_signature` | Add current user signature in emails (default: True) |

Usage example:

```python
# Create record without triggering mail features (better performance)
record = self.env['my.model'].with_context(tracking_disable=True).create(vals)

# Import data without creating "created" log messages
records = self.env['my.model'].with_context(
    mail_create_nolog=True,
    mail_create_nosubscribe=True,
).create(vals_list)
```

### `_mail_post_access` Attribute

Controls required access rights to post messages on the model:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'  # Default is 'write'
```

---

## mail.alias.mixin -- Email Aliases

Configurable email addresses linked to records that create new records when
emailed. Preferred over raw Incoming Mail Gateway for most use cases.

### Advantages Over Mail Gateway

- Easier to configure (single catchall domain, all routing inside Odoo)
- No System access rights needed
- Configured directly on the related record
- Built to be extended from the start

### Integration

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread', 'mail.alias.mixin']
    _description = 'Business Trip'

    name = fields.Char(tracking=True)
    partner_id = fields.Many2one('res.partner', 'Responsible', tracking=True)
    guest_ids = fields.Many2many('res.partner', 'Participants')
    state = fields.Selection([
        ('draft', 'New'),
        ('confirmed', 'Confirmed'),
    ], tracking=True)
    expense_ids = fields.One2many('business.expense', 'trip_id', 'Expenses')
    alias_id = fields.Many2one(
        'mail.alias', string='Alias',
        ondelete="restrict", required=True,
    )

    def _get_alias_model_name(self, vals):
        """Return the model name for records created by the alias.

        Args:
            vals: dict of values passed to create()
        Returns:
            str: model name
        """
        return 'business.expense'

    def _get_alias_values(self):
        """Return values for alias creation/update.

        Returns:
            dict: values written to the alias
        """
        values = super(BusinessTrip, self)._get_alias_values()
        values['alias_defaults'] = {'trip_id': self.id}
        values['alias_contact'] = 'followers'
        return values
```

**Important**: The model created by the alias **must** inherit `mail.thread`.

### Required Overrides

#### `_get_alias_model_name(vals)`

Specifies what model is created when the alias receives an email:

```python
def _get_alias_model_name(self, vals):
    return 'business.expense'
```

#### `_get_alias_values()`

Returns values for the alias configuration:

```python
def _get_alias_values(self):
    values = super()._get_alias_values()
    values['alias_defaults'] = {'trip_id': self.id}
    values['alias_contact'] = 'followers'
    return values
```

### Key Alias Fields

| Field | Type | Description |
|-------|------|-------------|
| `alias_name` | Char | Email alias name (e.g., `jobs` for `jobs@example.odoo.com`) |
| `alias_user_id` | Many2one (res.users) | Owner of created records (falls back to sender match or Admin) |
| `alias_defaults` | Text | Python dict evaluated for default values on new records |
| `alias_force_thread_id` | Integer | Force all messages to a specific thread (disables creation) |
| `alias_contact` | Selection | Who can post: `everyone`, `partners`, `followers` |

### Form View for Alias Configuration

```xml
<page string="Emails">
    <group name="group_alias">
        <label for="alias_name" string="Email Alias"/>
        <div name="alias_def">
            <field name="alias_id" class="oe_read_only oe_inline"
                   string="Email Alias" required="0"/>
            <div class="oe_edit_only oe_inline" name="edit_alias"
                 style="display: inline;">
                <field name="alias_name" class="oe_inline"/>
                @
                <field name="alias_domain" class="oe_inline" readonly="1"/>
            </div>
        </div>
        <field name="alias_contact" class="oe_inline"
               string="Accept Emails From"/>
    </group>
</page>
```

### Processing Incoming Emails

Override `message_new()` on the target model to extract values from emails:

```python
class BusinessExpense(models.Model):
    _name = 'business.expense'
    _inherit = ['mail.thread']
    _description = 'Business Expense'

    name = fields.Char()
    amount = fields.Float('Amount')
    trip_id = fields.Many2one('business.trip', 'Business Trip')
    partner_id = fields.Many2one('res.partner', 'Created by')

    def message_new(self, msg_dict, custom_values=None):
        """Create expense from incoming email."""
        name = msg_dict.get('subject', 'New Expense')

        # Extract amount from email subject
        import re
        amount_pattern = r'(\d+(\.\d*)?|\.\d+)'
        expense_price = re.findall(amount_pattern, name)
        price = float(expense_price[-1][0]) if expense_price else 1.0

        # Find partner by email
        email_from = msg_dict.get('email_from', '')
        partner = self.env['res.partner'].search(
            [('email', 'ilike', email_from)], limit=1
        )

        defaults = {
            'name': name,
            'amount': price,
            'partner_id': partner.id,
        }
        defaults.update(custom_values or {})
        return super(BusinessExpense, self).message_new(
            msg_dict, custom_values=defaults
        )
```

---

## mail.activity.mixin -- Activities Tracking

Adds scheduled activity support (phone calls, meetings, to-dos) to records.
Activities are displayed above the message history in the chatter.

### Integration

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Business Trip'

    name = fields.Char()
    # activity_ids is provided by the mixin
```

### Form View with Activities

```xml
<record id="business_trip_form" model="ir.ui.view">
    <field name="name">business.trip.form</field>
    <field name="model">business.trip</field>
    <field name="arch" type="xml">
        <form string="Business Trip">
            <sheet>
                <group>
                    <field name="name"/>
                </group>
            </sheet>
            <chatter>
                <field name="message_follower_ids" widget="mail_followers"/>
                <field name="activity_ids" widget="mail_activity"/>
                <field name="message_ids" widget="mail_thread"/>
            </chatter>
        </form>
    </field>
</record>
```

### Scheduling Activities Programmatically

```python
# Schedule an activity
record.activity_schedule(
    'mail.mail_activity_data_todo',
    user_id=user.id,
    summary='Review trip expenses',
    note='Please review and approve all submitted expenses',
    date_deadline=fields.Date.today() + timedelta(days=7),
)

# Schedule activity with a template
record.activity_schedule(
    'my_module.mail_activity_type_approve',
    user_id=manager.id,
)

# Mark activity as done
activity = record.activity_ids.filtered(
    lambda a: a.activity_type_id.xml_id == 'mail.mail_activity_data_todo'
)
activity.action_done()
```

### Kanban View with Activity Widget

```xml
<kanban>
    <field name="activity_ids"/>
    <templates>
        <t t-name="card">
            <field name="name"/>
            <field name="activity_ids" widget="kanban_activity"/>
        </t>
    </templates>
</kanban>
```

### Concrete Examples in Odoo

- `crm.lead` in CRM
- `sale.order` in Sales
- `project.task` in Project

---

## utm.mixin -- Visitor/Campaign Tracking

Tracks online marketing campaigns through URL parameters. Adds campaign, source,
and medium fields to your model.

### Fields Added

| Field | Type | Description |
|-------|------|-------------|
| `campaign_id` | Many2one (utm.campaign) | Campaign (e.g., Christmas Special) |
| `source_id` | Many2one (utm.source) | Source (e.g., Search Engine, mailing list) |
| `medium_id` | Many2one (utm.medium) | Medium (e.g., Email, social network) |

### Integration

```python
class MyModel(models.Model):
    _name = 'my_module.my_model'
    _inherit = ['utm.mixin']
    _description = 'My Tracked Object'
```

### How It Works

1. User visits URL with UTM parameters:
   `https://www.example.com/?campaign_id=summer_sale&source_id=google&medium_id=cpc`
2. Three cookies are set in the visitor's browser
3. When a record inheriting `utm.mixin` is created from the website, the mixin
   reads the cookies and sets the field values on the new record
4. These fields can then be used for reporting (group by campaign/source/medium)

### Extending with Custom Tracking Fields

```python
class UtmMyTrack(models.Model):
    _name = 'my_module.my_track'
    _description = 'My Tracking Object'

    name = fields.Char(string='Name', required=True)


class MyModel(models.Model):
    _name = 'my_module.my_model'
    _inherit = ['utm.mixin']
    _description = 'My Tracked Object'

    my_field = fields.Many2one('my_module.my_track', 'My Field')

    @api.model
    def tracking_fields(self):
        result = super(MyModel, self).tracking_fields()
        result.append([
            # ("URL_PARAMETER", "FIELD_NAME_MIXIN", "NAME_IN_COOKIES")
            ('my_field', 'my_field', 'odoo_utm_my_field')
        ])
        return result
```

This creates a cookie `odoo_utm_my_field` from the URL parameter `my_field`.
When a record is created from a website form, the generic `create()` override
fetches default values from the cookie (creating `my_module.my_track` records
on the fly if needed).

### Concrete Examples

- `crm.lead` in CRM
- `hr.applicant` in Recruitment (hr_recruitment)

---

## website.published.mixin -- Website Visibility

Adds a publication toggle for records that have frontend pages. Controls whether
the page is visible to website visitors.

### Fields Added

| Field | Type | Description |
|-------|------|-------------|
| `website_published` | Boolean | Publication status |
| `website_url` | Char (computed) | URL through which the object is accessed |

### Integration

```python
class BlogPost(models.Model):
    _name = "blog.post"
    _description = "Blog Post"
    _inherit = ['website.published.mixin']

    def _compute_website_url(self):
        for blog_post in self:
            blog_post.website_url = "/blog/%s" % blog_post.blog_id.id
```

**Important**: You must implement `_compute_website_url()` for your class.

### Backend Button (Button Box)

```xml
<button class="oe_stat_button" name="website_publish_button"
        type="object" icon="fa-globe">
    <field name="website_published" widget="website_button"/>
</button>
```

### Frontend Publish Widget

```xml
<div id="website_published_button" class="float-right"
     groups="base.group_website_publisher">
    <t t-call="website.publish_management">
        <t t-set="object" t-value="blog_post"/>
        <t t-set="publish_edit" t-value="True"/>
        <t t-set="action" t-value="'blog.blog_post_action'"/>
    </t>
</div>
```

Parameters:
- `object`: The record to publish/unpublish
- `publish_edit`: If True, frontend button links to backend
- `action`: Full external ID of the backend action (requires Form View)

### Behavior

The `website_publish_button` action:
- If `website_url` has a valid compute function: redirects to frontend for
  direct publication (prevents accidental publication)
- If no compute function: toggles `website_published` boolean directly

---

## website.seo.metadata -- SEO Metadata

Adds SEO metadata fields for frontend pages.

### Fields Added

| Field | Type | Description |
|-------|------|-------------|
| `website_meta_title` | Char | Additional page title |
| `website_meta_description` | Char | Short page description (used by search engines) |
| `website_meta_keywords` | Char | Keywords for search engine classification |

### Integration

```python
class BlogPost(models.Model):
    _name = "blog.post"
    _description = "Blog Post"
    _inherit = ['website.seo.metadata', 'website.published.mixin']
```

These fields are editable in the frontend via the "Promote" tool in the Editor
toolbar. The tool helps select lexically-related keywords.

---

## rating.mixin -- Customer Rating

Adds customer rating support with email requests, kanban integration, and
statistics aggregation.

### Integration

```python
class MyModel(models.Model):
    _name = 'my_module.my_model'
    _inherit = ['rating.mixin', 'mail.thread']

    user_id = fields.Many2one('res.users', 'Responsible')
    partner_id = fields.Many2one('res.partner', 'Customer')
```

### Automatic Behavior

- `rating.rating` records link to the `partner_id` field (the customer being asked)
  - Override with `rating_get_partner_id()` to use a different field
- `rating.rating` records link to the partner of the `user_id` field (the person rated)
  - Override with `rating_get_rated_partner_id()` for a different field
- Chatter displays rating events if the model inherits `mail.thread`

### Rating Email Template

```xml
<record id="rating_my_model_email_template" model="mail.template">
    <field name="name">My Model: Rating Request</field>
    <field name="email_from">
        ${object.rating_get_rated_partner_id().email or '' | safe}
    </field>
    <field name="subject">Service Rating Request</field>
    <field name="model_id" ref="my_module.model_my_model"/>
    <field name="partner_to">
        ${object.rating_get_partner_id().id}
    </field>
    <field name="auto_delete" eval="True"/>
    <field name="body_html"><![CDATA[
% set access_token = object.rating_get_access_token()
<p>Hi,</p>
<p>How satisfied are you?</p>
<ul>
    <li><a href="/rate/${access_token}/5">Satisfied</a></li>
    <li><a href="/rate/${access_token}/3">Okay</a></li>
    <li><a href="/rate/${access_token}/1">Dissatisfied</a></li>
</ul>
]]></field>
</record>
```

### Rating Action and Button

```xml
<!-- Action to view ratings -->
<record id="rating_rating_action_my_model" model="ir.actions.act_window">
    <field name="name">Customer Ratings</field>
    <field name="res_model">rating.rating</field>
    <field name="view_mode">kanban,pivot,graph</field>
    <field name="domain">[
        ('res_model', '=', 'my_module.my_model'),
        ('res_id', '=', active_id),
        ('consumed', '=', True)
    ]</field>
</record>

<!-- Add rating button to form view -->
<record id="my_module_my_model_view_form_inherit_rating" model="ir.ui.view">
    <field name="name">my_module.my_model.view.form.inherit.rating</field>
    <field name="model">my_module.my_model</field>
    <field name="inherit_id" ref="my_module.my_model_view_form"/>
    <field name="arch" type="xml">
        <xpath expr="//div[@name='button_box']" position="inside">
            <button name="%(rating_rating_action_my_model)d" type="action"
                    class="oe_stat_button" icon="fa-smile-o">
                <field name="rating_count" string="Rating" widget="statinfo"/>
            </button>
        </xpath>
    </field>
</record>
```

Default views (kanban, pivot, graph) are available for ratings.

### Concrete Examples

- `project.task` in Project (rating_project)
- `helpdesk.ticket` in Helpdesk (Enterprise only)

---

## Complete Multi-Mixin Example

A comprehensive model using multiple mixins:

```python
from odoo import api, fields, models

class ServiceRequest(models.Model):
    _name = 'service.request'
    _description = 'Service Request'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'rating.mixin',
        'utm.mixin',
    ]

    name = fields.Char(string='Reference', required=True, tracking=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        required=True, tracking=True,
    )
    user_id = fields.Many2one(
        'res.users', string='Assigned To',
        tracking=True,
    )
    description = fields.Html('Description')
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], default='new', tracking=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
        ('2', 'Very Urgent'),
    ], default='0', tracking=True)

    def action_start(self):
        self.write({'state': 'in_progress'})
        # Schedule a follow-up activity
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=self.user_id.id,
            summary='Follow up on service request',
            date_deadline=fields.Date.today() + timedelta(days=3),
        )

    def action_resolve(self):
        self.write({'state': 'resolved'})
        # Send rating request
        template = self.env.ref('my_module.rating_request_template')
        self.message_post_with_template(template.id)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'resolved':
            return self.env.ref('my_module.mt_request_resolved')
        return super()._track_subtype(init_values)
```

```xml
<record id="service_request_form" model="ir.ui.view">
    <field name="name">service.request.form</field>
    <field name="model">service.request</field>
    <field name="arch" type="xml">
        <form string="Service Request">
            <header>
                <button name="action_start" string="Start"
                        type="object" class="btn-primary"
                        invisible="state != 'new'"/>
                <button name="action_resolve" string="Resolve"
                        type="object" class="btn-primary"
                        invisible="state != 'in_progress'"/>
                <field name="state" widget="statusbar"
                       statusbar_visible="new,in_progress,resolved,closed"/>
            </header>
            <sheet>
                <div class="oe_button_box" name="button_box">
                    <button name="%(rating_rating_action_request)d"
                            type="action" class="oe_stat_button"
                            icon="fa-smile-o">
                        <field name="rating_count" string="Rating"
                               widget="statinfo"/>
                    </button>
                </div>
                <group>
                    <group>
                        <field name="name"/>
                        <field name="partner_id"/>
                        <field name="user_id"/>
                    </group>
                    <group>
                        <field name="state"/>
                        <field name="priority"/>
                        <field name="campaign_id" groups="base.group_no_one"/>
                        <field name="source_id" groups="base.group_no_one"/>
                        <field name="medium_id" groups="base.group_no_one"/>
                    </group>
                </group>
                <notebook>
                    <page string="Description">
                        <field name="description"/>
                    </page>
                </notebook>
            </sheet>
            <chatter>
                <field name="message_follower_ids" widget="mail_followers"/>
                <field name="activity_ids" widget="mail_activity"/>
                <field name="message_ids" widget="mail_thread"/>
            </chatter>
        </form>
    </field>
</record>
```

---

## Mixin Selection Guide

| Need | Mixin | Key Benefit |
|------|-------|-------------|
| Chatter, messaging, followers | `mail.thread` | Full messaging system |
| Field change logging | `mail.thread` + `tracking=True` | Automatic change logs |
| Email-based record creation | `mail.alias.mixin` | Records from emails |
| Scheduled activities/tasks | `mail.activity.mixin` | Activity management |
| Campaign tracking | `utm.mixin` | Marketing analytics |
| Website publish toggle | `website.published.mixin` | Content visibility |
| SEO metadata | `website.seo.metadata` | Search engine optimization |
| Customer satisfaction | `rating.mixin` | Rating collection |
