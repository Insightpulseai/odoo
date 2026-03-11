# Odoo QWeb Templates Guide

QWeb is Odoo's templating engine used for:

- **Backend**: Reports (PDF), emails, website pages
- **Frontend**: OWL components (JavaScript UI)

---

## QWeb Template Types

### 1. Backend QWeb (Reports & Emails)

**Location**: `views/*.xml`
**Usage**: PDF reports, email templates, website content

**Example: Invoice Report Template**

```xml
<odoo>
    <template id="report_invoice_document">
        <t t-call="web.external_layout">
            <div class="page">
                <h2>Invoice <span t-field="o.name"/></h2>

                <div class="row mt32 mb32">
                    <div class="col-6">
                        <strong>Customer:</strong>
                        <div t-field="o.partner_id"
                             t-options='{"widget": "contact", "fields": ["address", "name"], "no_marker": True}'/>
                    </div>
                    <div class="col-6">
                        <strong>Invoice Date:</strong>
                        <p t-field="o.invoice_date"/>
                    </div>
                </div>

                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th class="text-end">Quantity</th>
                            <th class="text-end">Unit Price</th>
                            <th class="text-end">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <t t-foreach="o.invoice_line_ids" t-as="line">
                            <tr>
                                <td><span t-field="line.name"/></td>
                                <td class="text-end"><span t-field="line.quantity"/></td>
                                <td class="text-end"><span t-field="line.price_unit"/></td>
                                <td class="text-end"><span t-field="line.price_subtotal"/></td>
                            </tr>
                        </t>
                    </tbody>
                </table>

                <div class="row">
                    <div class="col-6 offset-6">
                        <table class="table table-sm">
                            <tr>
                                <td><strong>Subtotal</strong></td>
                                <td class="text-end"><span t-field="o.amount_untaxed"/></td>
                            </tr>
                            <tr>
                                <td><strong>Tax</strong></td>
                                <td class="text-end"><span t-field="o.amount_tax"/></td>
                            </tr>
                            <tr class="border-top">
                                <td><strong>Total</strong></td>
                                <td class="text-end"><span t-field="o.amount_total"/></td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        </t>
    </template>
</odoo>
```

### 2. Frontend QWeb (OWL Components)

**Location**: `static/src/xml/*.xml`
**Usage**: JavaScript UI components (OWL 2.0+)

**Example: Custom Dashboard Widget**

```xml
<templates xml:space="preserve">
    <t t-name="ipai.DashboardWidget" owl="1">
        <div class="o_dashboard_widget">
            <div class="o_dashboard_widget_header">
                <h3><t t-esc="props.title"/></h3>
            </div>
            <div class="o_dashboard_widget_body">
                <t t-if="state.loading">
                    <div class="text-center">
                        <i class="fa fa-spinner fa-spin fa-2x"/>
                    </div>
                </t>
                <t t-else="">
                    <div class="row">
                        <t t-foreach="state.metrics" t-as="metric" t-key="metric.id">
                            <div class="col-md-6 mb-3">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title"><t t-esc="metric.label"/></h5>
                                        <p class="card-text display-4"><t t-esc="metric.value"/></p>
                                    </div>
                                </div>
                            </div>
                        </t>
                    </div>
                </t>
            </div>
        </div>
    </t>
</templates>
```

---

## Common QWeb Directives

### Core Directives

| Directive   | Purpose                             | Example                                             |
| ----------- | ----------------------------------- | --------------------------------------------------- |
| `t-esc`     | Escape and display value            | `<span t-esc="record.name"/>`                       |
| `t-out`     | Display raw HTML (unsafe)           | `<div t-out="record.description"/>`                 |
| `t-field`   | Display model field with formatting | `<span t-field="record.date"/>`                     |
| `t-if`      | Conditional rendering               | `<div t-if="record.active">Active</div>`            |
| `t-elif`    | Else-if condition                   | `<div t-elif="record.state == 'draft'">Draft</div>` |
| `t-else`    | Else condition                      | `<div t-else="">Other</div>`                        |
| `t-foreach` | Loop over collection                | `<t t-foreach="records" t-as="rec">`                |
| `t-set`     | Set variable                        | `<t t-set="total" t-value="0"/>`                    |
| `t-call`    | Call another template               | `<t t-call="web.external_layout"/>`                 |
| `t-att-*`   | Dynamic attribute                   | `<div t-att-class="record.state"/>`                 |

### Odoo-Specific Directives

| Directive       | Purpose                  | Example                                                              |
| --------------- | ------------------------ | -------------------------------------------------------------------- |
| `t-field`       | Render field with widget | `<span t-field="record.amount" t-options='{"widget": "monetary"}'/>` |
| `t-options`     | Widget options           | `t-options='{"widget": "contact", "fields": ["name", "phone"]}'`     |
| `t-translation` | Mark for translation     | `<span t-translation="off">No translate</span>`                      |

---

## QWeb Template Examples

### Email Template

```xml
<odoo>
    <record id="email_template_order_confirmation" model="mail.template">
        <field name="name">Order Confirmation</field>
        <field name="model_id" ref="sale.model_sale_order"/>
        <field name="subject">Order Confirmation - ${object.name}</field>
        <field name="body_html" type="html">
            <div style="font-family: Arial, sans-serif;">
                <h2>Order Confirmation</h2>
                <p>Dear ${object.partner_id.name},</p>
                <p>Thank you for your order <strong>${object.name}</strong>.</p>

                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f0f0f0;">
                            <th style="padding: 8px; border: 1px solid #ddd;">Product</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">Quantity</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        % for line in object.order_line:
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;">${line.product_id.name}</td>
                            <td style="padding: 8px; border: 1px solid #ddd;">${line.product_uom_qty}</td>
                            <td style="padding: 8px; border: 1px solid #ddd;">${line.price_subtotal}</td>
                        </tr>
                        % endfor
                    </tbody>
                </table>

                <p><strong>Total: ${object.amount_total}</strong></p>
                <p>Best regards,<br/>${object.company_id.name}</p>
            </div>
        </field>
    </record>
</odoo>
```

### Website Page Template

```xml
<odoo>
    <template id="custom_landing_page" name="Custom Landing Page">
        <t t-call="website.layout">
            <div id="wrap">
                <div class="container mt-5">
                    <div class="row">
                        <div class="col-lg-12 text-center">
                            <h1>Welcome to Our Platform</h1>
                            <p class="lead">Discover amazing features</p>
                        </div>
                    </div>

                    <div class="row mt-5">
                        <t t-foreach="features" t-as="feature">
                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <i t-att-class="'fa fa-3x mb-3 ' + feature.icon"/>
                                        <h5 class="card-title" t-esc="feature.title"/>
                                        <p class="card-text" t-esc="feature.description"/>
                                    </div>
                                </div>
                            </div>
                        </t>
                    </div>
                </div>
            </div>
        </t>
    </template>
</odoo>
```

---

## OWL Component Template (Odoo 19)

**Component JS** (`static/src/components/my_widget/my_widget.js`):

```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class MyWidget extends Component {
  static template = "ipai.MyWidget";
  static props = {
    title: { type: String, optional: true },
  };

  setup() {
    this.state = useState({
      count: 0,
      items: [],
    });
  }

  increment() {
    this.state.count++;
  }
}

registry.category("actions").add("my_widget", MyWidget);
```

**Component Template** (`static/src/components/my_widget/my_widget.xml`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="ipai.MyWidget" owl="1">
        <div class="my_widget">
            <h3><t t-esc="props.title or 'My Widget'"/></h3>

            <div class="counter">
                <p>Count: <t t-esc="state.count"/></p>
                <button class="btn btn-primary" t-on-click="increment">
                    Increment
                </button>
            </div>

            <div class="items mt-3">
                <t t-if="state.items.length === 0">
                    <p class="text-muted">No items</p>
                </t>
                <t t-else="">
                    <ul class="list-group">
                        <t t-foreach="state.items" t-as="item" t-key="item.id">
                            <li class="list-group-item">
                                <t t-esc="item.name"/>
                            </li>
                        </t>
                    </ul>
                </t>
            </div>
        </div>
    </t>
</templates>
```

---

## Best Practices

### 1. Always Use `t-esc` for User Input

```xml
<!-- ✅ Safe -->
<span t-esc="user_input"/>

<!-- ❌ Unsafe (XSS risk) -->
<span t-out="user_input"/>
```

### 2. Use `t-field` for Model Fields

```xml
<!-- ✅ Formatted with widget -->
<span t-field="record.date"/>

<!-- ❌ Raw value -->
<span t-esc="record.date"/>
```

### 3. Leverage `t-options` for Widgets

```xml
<span t-field="record.amount_total"
      t-options='{"widget": "monetary", "display_currency": record.currency_id}'/>
```

### 4. Use `t-call` for Reusability

```xml
<!-- Define reusable template -->
<template id="custom_header">
    <div class="header">
        <h1><t t-esc="title"/></h1>
    </div>
</template>

<!-- Call it -->
<t t-call="module.custom_header">
    <t t-set="title" t-value="'My Page'"/>
</t>
```

---

## Debugging QWeb Templates

### Enable Developer Mode

Settings → Activate Developer Mode

### View Template Source

In browser console:

```javascript
// Find template by name
odoo.qweb.templates["ipai.MyWidget"];
```

### Common Errors

**Error**: `QWeb2.Engine: Template not found`
**Fix**: Check template `t-name` matches exactly, ensure XML is loaded in `__manifest__.py`

**Error**: `Cannot read property 'X' of undefined`
**Fix**: Add null checks with `t-if`

```xml
<t t-if="record.partner_id">
    <span t-field="record.partner_id.name"/>
</t>
```

---

## References

- [Odoo QWeb Documentation](https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html)
- [OWL Documentation](https://github.com/odoo/owl)
- [Odoo 19 Frontend Guide](https://www.odoo.com/documentation/19.0/developer/reference/frontend.html)
