# Odoo 19 Backend Actions

## Window Actions (`ir.actions.act_window`)

**Purpose:** Opens views (Form, List, Kanban) for a model. The standard way to navigate menus.
**Structure:**

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Records</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form</field>
    <field name="domain">[('user_id', '=', uid)]</field>
    <field name="context">{'search_default_my_filter': 1, 'default_user_id': uid}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first record!
        </p>
    </field>
</record>
```

## Server Actions (`ir.actions.server`)

**Purpose:** Execute Python code, create/write records, or trigger other actions.
**Structure:**

```xml
<record id="action_server_sync" model="ir.actions.server">
    <field name="name">Sync with External API</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">
        # Available variables: env, model, record, records
        records.action_sync()
    </field>
    <!-- Add to "Action" menu -->
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">list,form</field>
</record>
```

## Scheduled Actions (`ir.cron`)

**Purpose:** Periodic background tasks.
**Structure:**

```xml
<record id="cron_sync_daily" model="ir.cron">
    <field name="name">Daily Sync</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">model.cron_sync()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field> <!-- Infinite -->
    <field name="doall" eval="False"/> <!-- Catch up missed? -->
</record>
```

## URL Actions (`ir.actions.act_url`)

**Purpose:** Redirect to external URL or download file.

```xml
<record id="action_open_google" model="ir.actions.act_url">
    <field name="name">Open Google</field>
    <field name="url">https://google.com</field>
    <field name="target">new</field>
</record>
```

## Common Mistakes

- **Context Pitfall:** `context` in window actions is STATIC. Use `search_default_` keys for default filters.
- **Looping in Server Actions:** Avoid `for record in records:` if you can use vector operations. If not, ensure it's performant.
- **Cron Timeouts:** Standard limit is 900s. For long jobs, use `_commit_progress(processed, remaining)` to checkin and avoid kill-signals.

## Source Links

- [Actions](https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html)
