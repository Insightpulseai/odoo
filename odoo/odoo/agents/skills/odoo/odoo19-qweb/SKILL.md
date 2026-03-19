---
name: odoo19-qweb
description: Odoo 19 QWeb templating engine — directives, inheritance, data output, loops, conditionals, attributes, sub-templates, JS and Python specifics
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/frontend/qweb.rst"
  extracted: "2026-02-17"
---

# Odoo 19 QWeb Templates

## Overview

QWeb is the **primary templating engine** in Odoo. It is an XML-based engine that generates HTML fragments and pages. Template directives are XML attributes prefixed with `t-` (e.g., `t-if`, `t-foreach`).

QWeb is used in two environments:
- **Python** (server-side): rendering website pages, reports, emails
- **JavaScript** (client-side): OWL component templates in the web client

The placeholder element `<t>` executes directives without producing output itself:

```xml
<!-- <t> produces no output -->
<t t-if="condition">
    <p>Test</p>
</t>
<!-- result when condition=true: <p>Test</p> -->

<!-- Regular elements produce output -->
<div t-if="condition">
    <p>Test</p>
</div>
<!-- result when condition=true: <div><p>Test</p></div> -->
```

---

## Data Output

### t-out (Primary Directive)

`t-out` evaluates an expression and injects the result into the document. **Automatically HTML-escapes** its input to prevent XSS:

```xml
<p><t t-out="value"/></p>
```

With `value = 42`:

```html
<p>42</p>
```

### Safe Content (No Double-Escaping)

Content that is already marked as "safe" (e.g., from `markupsafe.Markup` in Python or `t-call`/`t-set` with body) is injected as-is without re-escaping.

**Python safe content APIs**:
- `odoo.fields.Html` -- HTML fields
- `markupsafe.escape()` / `odoo.tools.misc.html_escape()` -- escape and mark safe
- `odoo.tools.mail.html_sanitize()` -- sanitize HTML
- `markupsafe.Markup` -- assert content is safe (use with care)

**Forcing double-escaping** (printing raw markup of safe content):
- Python: `str(content)` strips the safety flag
- JavaScript: `String(content)` strips the safety flag

### t-esc (Alias)

An alias for `t-out`. Functionally identical. Not formally deprecated but `t-out` is preferred for clarity.

### t-raw (Deprecated)

Never escapes content. **Deprecated since Odoo 15.0**. Use `t-out` with `markupsafe.Markup` instead.

```xml
<!-- DEPRECATED - do not use -->
<t t-raw="html_content"/>

<!-- CORRECT replacement -->
<t t-out="markup_safe_content"/>
```

---

## Conditionals

### t-if

Evaluates an expression. If true, the element is rendered; if false, it is removed:

```xml
<div>
    <t t-if="condition">
        <p>ok</p>
    </t>
</div>
```

Result when `condition=true`:
```html
<div>
    <p>ok</p>
</div>
```

Result when `condition=false`:
```html
<div>
</div>
```

The directive applies to its bearer element:

```xml
<div>
    <p t-if="condition">ok</p>
</div>
```

### t-elif and t-else

Branching directives for multi-way conditionals:

```xml
<div>
    <p t-if="user.birthday == today()">Happy birthday!</p>
    <p t-elif="user.login == 'root'">Welcome master!</p>
    <p t-else="">Welcome!</p>
</div>
```

Rules:
- `t-elif` must immediately follow a `t-if` or another `t-elif`
- `t-else` must immediately follow a `t-if` or `t-elif`
- `t-else` takes an empty string value (`t-else=""`)
- `t-elif` takes an expression just like `t-if`

### Conditional Examples

```xml
<!-- Show field only if record is in draft state -->
<field t-if="record.state.raw_value == 'draft'" name="priority"/>

<!-- Show different icons based on value -->
<span t-if="value > 0" class="text-success">
    <i class="fa fa-arrow-up"/>
</span>
<span t-elif="value &lt; 0" class="text-danger">
    <i class="fa fa-arrow-down"/>
</span>
<span t-else="" class="text-muted">
    <i class="fa fa-minus"/>
</span>
```

---

## Loops

### t-foreach

Iterates over a collection. Takes the collection expression and `t-as` parameter for the loop variable name:

```xml
<t t-foreach="[1, 2, 3]" t-as="i">
    <p><t t-out="i"/></p>
</t>
```

Output:
```html
<p>1</p>
<p>2</p>
<p>3</p>
```

Applied to bearer element:

```xml
<p t-foreach="[1, 2, 3]" t-as="i">
    <t t-out="i"/>
</p>
```

### Iteration Types

- **Array**: current item = current value
- **Mapping/Object**: current item = current key
- **Integer** (deprecated): equivalent to array from 0 to n-1

### Context Variables

For a loop with `t-as="item"`, these variables are available inside the loop:

| Variable | Description |
|----------|-------------|
| `item` | Current item (value for arrays, key for mappings) |
| `item_value` | Current value (same as `item` for arrays; the mapped value for objects) |
| `item_index` | Current iteration index (0-based) |
| `item_size` | Size of the collection (if available) |
| `item_first` | `true` if first iteration (`item_index == 0`) |
| `item_last` | `true` if last iteration (`item_index + 1 == item_size`) |
| `item_all` | The object being iterated (JS only, deprecated) |
| `item_parity` | `"even"` or `"odd"` (deprecated) |
| `item_even` | Boolean, even index (deprecated) |
| `item_odd` | Boolean, odd index (deprecated) |

### Loop Examples

```xml
<!-- Render a list of partners -->
<ul>
    <li t-foreach="partners" t-as="partner" t-key="partner.id">
        <t t-out="partner.name"/>
    </li>
</ul>

<!-- Alternating row colors -->
<t t-foreach="records" t-as="rec" t-key="rec.id">
    <tr t-attf-class="row {{ (rec_index % 2 === 0) ? 'even' : 'odd' }}">
        <td><t t-out="rec.name"/></td>
    </tr>
</t>

<!-- Loop with first/last detection -->
<t t-foreach="items" t-as="item" t-key="item_index">
    <span t-if="!item_first">, </span>
    <t t-out="item"/>
</t>
```

### Variable Scoping in Loops

Variables created inside `foreach` are scoped to the loop. Pre-existing variables are copied back after the loop ends:

```xml
<t t-set="existing_variable" t-value="False"/>
<!-- existing_variable is False -->

<p t-foreach="[1, 2, 3]" t-as="i">
    <t t-set="existing_variable" t-value="True"/>
    <t t-set="new_variable" t-value="True"/>
    <!-- existing_variable and new_variable are True -->
</p>

<!-- existing_variable is True (copied back) -->
<!-- new_variable is undefined (scoped to loop) -->
```

---

## Attributes

QWeb can compute attributes dynamically using three forms of the `t-att` directive.

### t-att-{name} (Dynamic Attribute Value)

Creates an attribute with a computed value:

```xml
<div t-att-a="42"/>
```

Output:
```html
<div a="42"></div>
```

### t-attf-{name} (Format String Attribute)

Mixes literal and computed values using format strings:

```xml
<t t-foreach="[1, 2, 3]" t-as="item">
    <li t-attf-class="row {{ (item_index % 2 === 0) ? 'even' : 'odd' }}">
        <t t-out="item"/>
    </li>
</t>
```

Output:
```html
<li class="row even">1</li>
<li class="row odd">2</li>
<li class="row even">3</li>
```

Two equivalent syntaxes for format strings:
- **Jinja-style**: `"plain_text {{code}}"`
- **Ruby-style**: `"plain_text #{code}"`

### t-att=mapping (Multiple Attributes from Object)

Each key-value pair becomes an attribute:

```xml
<div t-att="{'a': 1, 'b': 2}"/>
```

Output:
```html
<div a="1" b="2"></div>
```

### t-att=pair (Attribute from Array)

First element = name, second = value:

```xml
<div t-att="['a', 'b']"/>
```

Output:
```html
<div a="b"></div>
```

### Common Attribute Patterns

```xml
<!-- Dynamic CSS class -->
<div t-att-class="record.is_active ? 'active' : 'inactive'"/>

<!-- Format string for class composition -->
<div t-attf-class="o_field_widget o_field_{{ widget_type }}"/>

<!-- Conditional attribute -->
<button t-att-disabled="record.readonly"/>

<!-- Dynamic style -->
<div t-attf-style="color: {{ record.color }}; font-size: {{ size }}px;"/>

<!-- Data attributes -->
<div t-att-data-id="record.id" t-att-data-model="model_name"/>
```

---

## Setting Variables

### t-set with t-value

Create variables with evaluated expressions:

```xml
<t t-set="foo" t-value="2 + 1"/>
<t t-out="foo"/>
<!-- outputs: 3 -->
```

### t-set with Body

If no `t-value`, the node's rendered body becomes the variable value:

```xml
<t t-set="foo">
    <li>ok</li>
</t>
<t t-out="foo"/>
<!-- outputs: <li>ok</li> -->
```

Body content set via `t-set` (without `t-value`) produces **safe** content that won't be re-escaped by `t-out`.

### Variable Examples

```xml
<!-- Compute and reuse -->
<t t-set="full_name" t-value="record.first_name + ' ' + record.last_name"/>
<h1><t t-out="full_name"/></h1>
<p>Welcome, <t t-out="full_name"/>!</p>

<!-- Conditional variable -->
<t t-set="status_class" t-value="record.active ? 'text-success' : 'text-muted'"/>
<span t-att-class="status_class"><t t-out="record.state"/></span>
```

---

## Sub-Templates (t-call)

### Basic Call

`t-call` renders another template within the current execution context:

```xml
<t t-call="other-template"/>
```

If `other-template` is:
```xml
<p><t t-out="var"/></p>
```

Then:
```xml
<t t-set="var" t-value="1"/>
<t t-call="other-template"/>
<!-- result: <p>1</p> -->
```

### Local Context in t-call Body

Variables set in the body of `t-call` are local to the called template:

```xml
<t t-call="other-template">
    <t t-set="var" t-value="1"/>
</t>
<!-- "var" does not exist here -->
```

### The Magic `0` Variable

The rendered body of a `t-call` is available in the called template as the variable `0`:

Template `other-template`:
```xml
<div>
    This template was called with content:
    <t t-out="0"/>
</div>
```

Call:
```xml
<t t-call="other-template">
    <em>content</em>
</t>
```

Result:
```html
<div>
    This template was called with content:
    <em>content</em>
</div>
```

### Sub-Template Example

```xml
<!-- Define a reusable card template -->
<t t-name="myaddon.Card">
    <div class="card">
        <div class="card-header">
            <t t-out="title"/>
        </div>
        <div class="card-body">
            <t t-out="0"/>
        </div>
    </div>
</t>

<!-- Use it -->
<t t-call="myaddon.Card">
    <t t-set="title" t-value="'My Card Title'"/>
    <p>This is the card body content.</p>
</t>
```

---

## Python-Only Directives

### t-field / t-options (Smart Records)

`t-field` works only with "smart" records (from `browse()`). Automatically formats based on field type and integrates with the website rich text editor:

```xml
<span t-field="record.name"/>
<span t-field="record.amount" t-options='{"widget": "monetary"}'/>
<span t-field="record.date" t-options='{"format": "long"}'/>
```

`t-options` customizes the output. The `widget` option is most common; other options are field/widget-dependent.

### t-debug (Python)

Invokes the `breakpoint()` builtin (defaults to `pdb`):

```xml
<t t-debug=""/>
```

Behavior configurable via `PYTHONBREAKPOINT` environment variable or `sys.breakpointhook`.

### Python Rendering Helpers

**Request-based rendering** (in controllers):

```python
response = http.request.render('my-template', {
    'context_value': 42
})
```

**View-based rendering** (deeper level):

```python
# Using database templates (ir.qweb)
result = env['ir.qweb']._render('template_xmlid', values)

# Public render (no database)
result = render('template_name', values, load_fn)
```

**Default context values** available in Python QWeb:
- `request` -- current `odoo.http.Request`
- `debug` -- whether in debug mode
- `quote_plus` -- URL encoding utility
- `json`, `time`, `datetime` -- standard library modules
- `relativedelta` -- dateutil
- `keep_query` -- query string helper

---

## JavaScript-Only Directives

### t-name (Template Definition)

Defines a named template. Must be a direct child of the root `<templates>` element:

```xml
<templates>
    <t t-name="template-name">
        <!-- template code -->
    </t>
</templates>
```

Convention: use dot-separated names for related templates (e.g., `myaddon.MyComponent`, `myaddon.MyComponent.row`).

### t-log (Console Logging)

Evaluates an expression and logs the result with `console.log`:

```xml
<t t-set="foo" t-value="42"/>
<t t-log="foo"/>
<!-- prints 42 to console -->
```

### t-debug (JavaScript)

Triggers a debugger breakpoint during template rendering:

```xml
<t t-if="a_test">
    <t t-debug=""/>
</t>
```

Stops execution if browser dev tools are active.

### t-js (Inline JavaScript)

Execute JavaScript code during template rendering. The `context` parameter names the rendering context variable:

```xml
<t t-set="foo" t-value="42"/>
<t t-js="ctx">
    console.log("Foo is", ctx.foo);
</t>
```

---

## Template Inheritance

Template inheritance allows modifying or extending existing templates. There are two modes.

### Extension Inheritance (In-Place Modification)

Modifies the parent template directly. All uses of the parent template see the changes:

```xml
<t t-inherit="base.template" t-inherit-mode="extension">
    <xpath expr="//tr[1]" position="after">
        <tr><td>new cell</td></tr>
    </xpath>
</t>
```

### Primary Inheritance (Child Template)

Creates a **new** template based on a parent, without modifying the parent:

```xml
<t t-name="child.template" t-inherit="base.template" t-inherit-mode="primary">
    <xpath expr="//ul" position="inside">
        <li>new element</li>
    </xpath>
</t>
```

### XPath Directives

The `<xpath>` element targets nodes in the parent template using XPath expressions:

| Attribute | Description |
|-----------|-------------|
| `expr` | XPath expression to select target node(s) |
| `position` | What to do with the content relative to the target |

**Position values**:

| Position | Effect |
|----------|--------|
| `inside` | Append content inside target (after last child) |
| `replace` | Replace the target node entirely |
| `before` | Insert content before the target |
| `after` | Insert content after the target |
| `attributes` | Modify target's attributes |

### XPath Examples

```xml
<!-- Add a field after an existing one -->
<xpath expr="//field[@name='partner_id']" position="after">
    <field name="phone"/>
</xpath>

<!-- Replace a div -->
<xpath expr="//div[hasclass('o_header')]" position="replace">
    <div class="o_header custom_header">
        <t t-out="0"/>
    </div>
</xpath>

<!-- Add content inside a group -->
<xpath expr="//group[@name='main_info']" position="inside">
    <field name="custom_field"/>
</xpath>

<!-- Modify attributes -->
<xpath expr="//field[@name='state']" position="attributes">
    <attribute name="invisible">context.get('hide_state')</attribute>
    <attribute name="class">custom_class</attribute>
</xpath>

<!-- Insert before first element -->
<xpath expr="//form//sheet" position="before">
    <header>
        <button name="action_confirm" string="Confirm" type="object"/>
    </header>
</xpath>
```

---

## Deprecated Inheritance (t-extend / t-jquery)

**Deprecated**. Use `t-inherit`/`t-inherit-mode` instead.

`t-extend` with `t-name` = primary inheritance; without = extension:

```xml
<!-- DEPRECATED: extension -->
<t t-extend="base.template">
    <t t-jquery="ul" t-operation="append">
        <li>new element</li>
    </t>
</t>
```

`t-jquery` uses CSS selectors with `t-operation`:

| Operation | Effect |
|-----------|--------|
| `append` | Add after last child of context node |
| `prepend` | Add before first child |
| `before` | Insert before context node |
| `after` | Insert after context node |
| `inner` | Replace children of context node |
| `replace` | Replace context node itself |
| `attributes` | Set attributes (uses `<attribute name="...">value</attribute>` children) |
| (none) | Execute body as JavaScript with `this` = context node |

---

## Format Strings

Used in `t-attf-*` directives. Two equivalent syntaxes:

```xml
<!-- Jinja-style -->
<div t-attf-class="base_class {{ dynamic_class }}"/>

<!-- Ruby-style -->
<div t-attf-class="base_class #{dynamic_class}"/>

<!-- Complex expressions -->
<a t-attf-href="/web#model={{ model }}&id={{ record.id }}">
    Link
</a>

<!-- Mixed static and dynamic -->
<div t-attf-style="width: {{ width }}px; height: {{ height }}px;"/>
```

---

## Complete Template Examples

### OWL Component Template (JavaScript)

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<templates xml:space="preserve">

<t t-name="myaddon.TaskList">
    <div class="task-list">
        <h2><t t-esc="props.title"/></h2>

        <ul t-if="state.tasks.length">
            <li t-foreach="state.tasks" t-as="task" t-key="task.id"
                t-attf-class="task {{ task.done ? 'done' : '' }}">
                <span t-esc="task.name"/>
                <button t-if="!task.done" t-on-click="() => this.completeTask(task.id)">
                    Complete
                </button>
            </li>
        </ul>
        <p t-else="">No tasks yet.</p>

        <div class="task-form">
            <input t-ref="autofocus" type="text"
                t-att-value="state.newTask"
                t-on-input="onInput"
                t-att-placeholder="env._t('New task...')"/>
            <button t-on-click="addTask">Add</button>
        </div>
    </div>
</t>

</templates>
```

### Website Page Template (Python)

```xml
<t t-name="myaddon.product_page">
    <t t-call="website.layout">
        <div class="container">
            <h1 t-field="product.name"/>
            <div class="row">
                <div class="col-md-6">
                    <img t-att-src="'/web/image/product.product/%s/image_1024' % product.id"
                         t-att-alt="product.name"/>
                </div>
                <div class="col-md-6">
                    <p t-field="product.description_sale"/>
                    <span t-field="product.list_price"
                          t-options='{"widget": "monetary", "display_currency": product.currency_id}'/>

                    <t t-if="product.qty_available > 0">
                        <span class="badge text-bg-success">In Stock</span>
                    </t>
                    <t t-else="">
                        <span class="badge text-bg-danger">Out of Stock</span>
                    </t>
                </div>
            </div>
        </div>
    </t>
</t>
```

### Report Template (Python)

```xml
<t t-name="myaddon.report_invoice">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Invoice <t t-out="doc.name"/></h2>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Qty</th>
                                <th>Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr t-foreach="doc.invoice_line_ids" t-as="line">
                                <td><t t-out="line.product_id.name"/></td>
                                <td><t t-out="line.quantity"/></td>
                                <td t-field="line.price_subtotal"
                                    t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
                            </tr>
                        </tbody>
                    </table>
                    <div class="text-end">
                        <strong>Total: </strong>
                        <span t-field="doc.amount_total"
                              t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
                    </div>
                </div>
            </t>
        </t>
    </t>
</t>
```

### Template Inheritance Example

Base template (defined by another module):
```xml
<t t-name="sale.order_form">
    <form>
        <sheet>
            <group name="main_info">
                <field name="partner_id"/>
                <field name="date_order"/>
            </group>
        </sheet>
    </form>
</t>
```

Extension (your module):
```xml
<t t-inherit="sale.order_form" t-inherit-mode="extension">
    <!-- Add field after partner_id -->
    <xpath expr="//field[@name='partner_id']" position="after">
        <field name="payment_term_id"/>
    </xpath>

    <!-- Add new group after main_info -->
    <xpath expr="//group[@name='main_info']" position="after">
        <group name="custom_info" string="Custom Information">
            <field name="custom_reference"/>
        </group>
    </xpath>
</t>
```

---

## QWeb JavaScript API

### QWeb2.Engine

```javascript
// The main QWeb instance with all loaded templates
const qweb = core.qweb;

// Render a template to string
const html = qweb.render("template-name", { value: 42 });

// Load additional templates
qweb.add_template(xmlString);
qweb.add_template(url);
qweb.add_template(documentOrNode);
```

Engine configuration:

| Property | Default | Description |
|----------|---------|-------------|
| `prefix` | `"t"` | Directive prefix |
| `debug` | `false` | Let exceptions propagate (no catch) |
| `jQuery` | `window.jQuery` | jQuery instance for inheritance |
| `preprocess_node` | `null` | Function called before compiling each node (used for auto-translation) |

---

## Quick Reference Table

| Directive | Context | Description |
|-----------|---------|-------------|
| `t-out` | Both | Output with auto-escaping |
| `t-esc` | Both | Alias for `t-out` |
| `t-raw` | Both | **Deprecated**. Output without escaping |
| `t-if` | Both | Conditional rendering |
| `t-elif` | Both | Else-if branch |
| `t-else` | Both | Else branch |
| `t-foreach` / `t-as` | Both | Loop iteration |
| `t-att-{name}` | Both | Dynamic attribute |
| `t-attf-{name}` | Both | Format string attribute |
| `t-att` | Both | Multiple attributes from object/pair |
| `t-set` / `t-value` | Both | Variable assignment |
| `t-call` | Both | Sub-template invocation |
| `t-field` / `t-options` | Python | Smart record field formatting |
| `t-debug` | Both | Debugger breakpoint |
| `t-name` | JS | Template definition |
| `t-log` | JS | Console.log during rendering |
| `t-js` | JS | Inline JavaScript execution |
| `t-inherit` | JS | Template inheritance (parent name) |
| `t-inherit-mode` | JS | `"primary"` or `"extension"` |
| `t-extend` | JS | **Deprecated**. Old inheritance |
| `t-jquery` | JS | **Deprecated**. CSS selector targeting |
