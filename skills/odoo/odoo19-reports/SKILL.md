---
name: odoo19-reports
description: Odoo 19 QWeb PDF/HTML reports, paper formats, custom report models, translatable templates, and report actions
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/reports.rst"
  extracted: "2026-02-17"
---

# Odoo 19 QWeb Reports

## Overview

Reports in Odoo are written in HTML/QWeb and rendered to PDF using wkhtmltopdf.
They use the same QWeb template engine as website views. Reports are declared
with a report action (`ir.actions.report`) and linked to a QWeb template.

---

## Report Action Declaration

Reports are declared as `ir.actions.report` records in XML data files:

```xml
<record id="action_report_my_model" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_my_model</field>
    <field name="report_file">my_module.report_my_model</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_type">report</field>
</record>
```

### Key Fields

| Field | Description |
|-------|-------------|
| `name` | Human-readable report name shown in the UI |
| `model` | The target model (e.g., `sale.order`) |
| `report_type` | `qweb-pdf` (default) or `qweb-html` |
| `report_name` | QWeb template external ID (module.template_id) |
| `report_file` | File path for the report template (usually same as report_name) |
| `binding_model_id` | Links report to model's Print menu |
| `binding_type` | Must be `report` for report actions |
| `paperformat_id` | Reference to a custom paper format record |
| `print_report_name` | Python expression for the PDF filename |
| `attachment_use` | If True, store the report as an attachment |
| `attachment` | Python expression for the attachment name |

### Custom PDF Filename

```xml
<record id="action_report_invoice" model="ir.actions.report">
    <field name="name">Invoice</field>
    <field name="model">account.move</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">account.report_invoice</field>
    <field name="print_report_name">'Invoice - %s' % (object.name)</field>
    <field name="binding_model_id" ref="account.model_account_move"/>
    <field name="binding_type">report</field>
</record>
```

---

## Report Templates

### Template Variables (Always Available)

| Variable | Description |
|----------|-------------|
| `time` | Reference to Python `time` module |
| `user` | `res.users` record for the user printing the report |
| `res_company` | Record for the current user's company |
| `website` | Current website object (may be `None`) |
| `web_base_url` | Base URL for the web server |
| `context_timestamp` | Function to convert UTC datetime to user's timezone |
| `docs` | Records for the current report (default context) |
| `doc_ids` | List of IDs for the `docs` records |
| `doc_model` | Model name for the `docs` records |

### Minimal Viable Report Template

```xml
<template id="report_my_model">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Report title</h2>
                    <p>This object's name is <span t-field="o.name"/></p>
                </div>
            </t>
        </t>
    </t>
</template>
```

Key points:
- `web.html_container` wraps the entire report content
- `t-foreach="docs"` iterates over all records selected for the report
- `web.external_layout` adds the default company header and footer
- The PDF body is the content inside `<div class="page">`
- The template `id` must match the `report_name` in the report action

### Complete Report Example

```xml
<!-- Report Action -->
<record id="action_report_business_trip" model="ir.actions.report">
    <field name="name">Business Trip Report</field>
    <field name="model">business.trip</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_business_trip</field>
    <field name="binding_model_id" ref="model_business_trip"/>
    <field name="binding_type">report</field>
    <field name="print_report_name">'Trip - %s' % (object.name)</field>
</record>

<!-- Report Template -->
<template id="report_business_trip">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2><span t-field="o.name"/></h2>

                    <div class="row mt-4">
                        <div class="col-6">
                            <strong>Responsible:</strong>
                            <span t-field="o.partner_id"/>
                        </div>
                        <div class="col-6">
                            <strong>State:</strong>
                            <span t-field="o.state"/>
                        </div>
                    </div>

                    <h3 class="mt-4">Participants</h3>
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="o.guest_ids" t-as="guest">
                                <tr>
                                    <td><span t-field="guest.name"/></td>
                                    <td><span t-field="guest.email"/></td>
                                </tr>
                            </t>
                        </tbody>
                    </table>

                    <h3 class="mt-4">Expenses</h3>
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Description</th>
                                <th class="text-end">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="o.expense_ids" t-as="expense">
                                <tr>
                                    <td><span t-field="expense.name"/></td>
                                    <td class="text-end">
                                        <span t-field="expense.amount"
                                              t-options='{"widget": "monetary",
                                                          "display_currency": o.currency_id}'/>
                                    </td>
                                </tr>
                            </t>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td><strong>Total</strong></td>
                                <td class="text-end">
                                    <strong t-field="o.total_amount"
                                            t-options='{"widget": "monetary",
                                                        "display_currency": o.currency_id}'/>
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Translatable Reports

For reports that need translation (e.g., to the partner's language), define two
templates: a main report template and a translatable document template.

### Pattern

```xml
<!-- Main template -->
<template id="report_saleorder">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="sale.report_saleorder_document" t-lang="doc.partner_id.lang"/>
        </t>
    </t>
</template>

<!-- Translatable template -->
<template id="report_saleorder_document">
    <!-- Re-browse the record with the partner's language -->
    <t t-set="doc" t-value="doc.with_context(lang=doc.partner_id.lang)"/>
    <t t-call="web.external_layout">
        <div class="page">
            <div class="row">
                <div class="col-6">
                    <strong t-if="doc.partner_shipping_id == doc.partner_invoice_id">
                        Invoice and shipping address:
                    </strong>
                    <strong t-if="doc.partner_shipping_id != doc.partner_invoice_id">
                        Invoice address:
                    </strong>
                    <div t-field="doc.partner_invoice_id"
                         t-options='{"no_marker": True}'/>
                </div>
            </div>
            <!-- ... rest of the report ... -->
        </div>
    </t>
</template>
```

Key points:
- Use `t-lang="doc.partner_id.lang"` on the `t-call` to set the language
- **Re-browse** the record with the partner's language context to translate
  translatable fields (country names, terms, etc.)
- If no translatable record fields are used, re-browsing is unnecessary and
  impacts performance

### Keep Header/Footer in Default Language

```xml
<t t-call="web.external_layout" t-lang="en_US">
```

### Translation Limitation

`t-lang` only works on `t-call` elements. You cannot translate part of a template
by setting `t-lang` on arbitrary XML nodes. If you need partial translation,
create a separate external template and call it with `t-lang`.

---

## Barcodes

Barcodes are images returned by a controller, embedded via QWeb:

```xml
<!-- Simple QR code -->
<img t-att-src="'/report/barcode/QR/%s' % 'My text in qr code'"/>

<!-- With parameters -->
<img t-att-src="'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s'
     % ('QR', 'text', 200, 200)"/>

<!-- Code128 barcode for a field value -->
<img t-att-src="'/report/barcode/Code128/%s' % o.reference"/>
```

---

## CSS and Styling

### Local CSS in Template

```xml
<template id="report_my_model">
    <t t-call="web.html_container">
        <style>
            .custom-header { color: #333; font-size: 24px; }
            .amount-cell { text-align: right; font-weight: bold; }
        </style>
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2 class="custom-header"><span t-field="o.name"/></h2>
                </div>
            </t>
        </t>
    </t>
</template>
```

### Global CSS via Report Layout Inheritance

```xml
<template id="report_saleorder_style" inherit_id="report.style">
    <xpath expr=".">
        <t>
            .example-css-class {
                background-color: red;
            }
        </t>
    </xpath>
</template>
```

### Available CSS Frameworks

- **Twitter Bootstrap** classes are available in reports
- **FontAwesome** icon classes are available in reports

---

## Paper Format

Paper formats are records of `report.paperformat`:

### Fields

| Field | Description | Default |
|-------|-------------|---------|
| `name` | Mnemonic/description (mandatory) | — |
| `description` | Short description | — |
| `format` | Predefined format (A0-A9, B0-B10, Legal, Letter, Tabloid) or `custom` | A4 |
| `dpi` | Output DPI | 90 |
| `margin_top` | Top margin in mm | — |
| `margin_bottom` | Bottom margin in mm | — |
| `margin_left` | Left margin in mm | — |
| `margin_right` | Right margin in mm | — |
| `page_height` | Page height in mm (for custom format) | — |
| `page_width` | Page width in mm (for custom format) | — |
| `orientation` | `Landscape` or `Portrait` | — |
| `header_line` | Display a header line (boolean) | — |
| `header_spacing` | Header spacing in mm | — |

**Note**: You cannot use a non-custom format if you define custom page dimensions.

### Example: Custom Paper Format

```xml
<record id="paperformat_frenchcheck" model="report.paperformat">
    <field name="name">French Bank Check</field>
    <field name="default" eval="True"/>
    <field name="format">custom</field>
    <field name="page_height">80</field>
    <field name="page_width">175</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">3</field>
    <field name="margin_bottom">3</field>
    <field name="margin_left">3</field>
    <field name="margin_right">3</field>
    <field name="header_line" eval="False"/>
    <field name="header_spacing">3</field>
    <field name="dpi">80</field>
</record>
```

### Linking Paper Format to a Report

```xml
<record id="action_report_my_model" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_my_model</field>
    <field name="paperformat_id" ref="my_module.paperformat_frenchcheck"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_type">report</field>
</record>
```

### Standard Paper Format (A4 Landscape)

```xml
<record id="paperformat_a4_landscape" model="report.paperformat">
    <field name="name">A4 Landscape</field>
    <field name="format">A4</field>
    <field name="orientation">Landscape</field>
    <field name="margin_top">20</field>
    <field name="margin_bottom">20</field>
    <field name="margin_left">7</field>
    <field name="margin_right">7</field>
    <field name="header_spacing">20</field>
    <field name="dpi">90</field>
</record>
```

---

## Custom Reports

By default, the report system uses the target model's records directly. For
custom data preparation, create an AbstractModel named `report.<module>.<report_name>`.

### Custom Report Model

```python
from odoo import api, models

class ParticularReport(models.AbstractModel):
    _name = 'report.module.report_name'
    _description = 'Particular Report'

    def _get_report_values(self, docids, data=None):
        # Get the report action for metadata
        report = self.env['ir.actions.report']._get_report_from_name(
            'module.report_name'
        )
        # Browse the records selected for this report
        records = self.env[report.model].browse(docids)

        # Return custom rendering context
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': records,
            'lines': records.mapped('line_ids'),
            'totals': self._compute_totals(records),
        }

    def _compute_totals(self, records):
        return {
            'total_amount': sum(records.mapped('amount_total')),
            'total_tax': sum(records.mapped('amount_tax')),
        }
```

**Important**: When using a custom report, the default items (`doc_ids`,
`doc_model`, `docs`) are **not** automatically included. You must provide them
yourself if needed.

### Complete Custom Report Example

```python
# models/report_trip_summary.py
from odoo import api, models

class TripSummaryReport(models.AbstractModel):
    _name = 'report.my_module.report_trip_summary'
    _description = 'Trip Summary Report'

    def _get_report_values(self, docids, data=None):
        trips = self.env['business.trip'].browse(docids)

        # Compute extra data for the template
        summary = []
        for trip in trips:
            expenses_by_category = {}
            for expense in trip.expense_ids:
                cat = expense.category_id.name or 'Uncategorized'
                expenses_by_category.setdefault(cat, 0)
                expenses_by_category[cat] += expense.amount
            summary.append({
                'trip': trip,
                'expenses_by_category': expenses_by_category,
                'total': sum(expenses_by_category.values()),
            })

        return {
            'doc_ids': docids,
            'doc_model': 'business.trip',
            'docs': trips,
            'summary': summary,
            'company': self.env.company,
        }
```

```xml
<!-- views/report_trip_summary.xml -->
<template id="report_trip_summary">
    <t t-call="web.html_container">
        <t t-foreach="summary" t-as="item">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Trip Summary: <span t-esc="item['trip'].name"/></h2>

                    <table class="table">
                        <thead>
                            <tr>
                                <th>Expense Category</th>
                                <th class="text-end">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="item['expenses_by_category'].items()"
                               t-as="cat_item">
                                <tr>
                                    <td><t t-esc="cat_item[0]"/></td>
                                    <td class="text-end">
                                        <t t-esc="'%.2f' % cat_item[1]"/>
                                    </td>
                                </tr>
                            </t>
                        </tbody>
                        <tfoot>
                            <tr class="fw-bold">
                                <td>Total</td>
                                <td class="text-end">
                                    <t t-esc="'%.2f' % item['total']"/>
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Custom Fonts

Custom fonts for reports must be added to the `web.report_assets_common` bundle.
Adding them to `web.assets_common` or `web.assets_backend` does NOT make them
available in QWeb reports.

### Register Font Assets

```xml
<template id="report_assets_common_custom_fonts"
          name="Custom QWeb fonts"
          inherit_id="web.report_assets_common">
    <xpath expr="." position="inside">
        <link href="/your_module/static/src/less/fonts.less"
              rel="stylesheet" type="text/less"/>
    </xpath>
</template>
```

### Define @font-face

Even if the font is defined in another assets bundle, you must re-define
`@font-face` in the report assets:

```css
/* your_module/static/src/less/fonts.less */
@font-face {
    font-family: 'MonixBold';
    src: local('MonixBold'), local('MonixBold'),
         url(/your_module/static/fonts/MonixBold-Regular.otf) format('opentype');
}

.h1-title-big {
    font-family: MonixBold;
    font-size: 60px;
    color: #3399cc;
}
```

### Use in Template

```xml
<div class="page">
    <h1 class="h1-title-big">Custom Font Title</h1>
</div>
```

---

## Reports as Web Pages

Reports are dynamically generated and accessible via URL:

| Format | URL Pattern |
|--------|-------------|
| HTML | `/report/html/<report_name>/<record_ids>` |
| PDF | `/report/pdf/<report_name>/<record_ids>` |

### Examples

```
# HTML version
http://<server>/report/html/sale.report_saleorder/38

# PDF version
http://<server>/report/pdf/sale.report_saleorder/38

# Multiple records
http://<server>/report/pdf/sale.report_saleorder/38,39,40
```

---

## Report Template Inheritance

Extend existing reports using template inheritance:

```xml
<!-- Add a custom section to an existing report -->
<template id="report_saleorder_custom"
          inherit_id="sale.report_saleorder_document">
    <xpath expr="//div[@class='page']" position="inside">
        <div class="mt-4">
            <h3>Custom Section</h3>
            <p t-field="doc.custom_field"/>
        </div>
    </xpath>
</template>
```

### Add Columns to Existing Tables

```xml
<template id="report_invoice_add_column"
          inherit_id="account.report_invoice_document">
    <xpath expr="//table[@name='invoice_line_table']/thead/tr" position="inside">
        <th>Custom Column</th>
    </xpath>
    <xpath expr="//table[@name='invoice_line_table']/tbody//tr" position="inside">
        <td><span t-field="line.custom_field"/></td>
    </xpath>
</template>
```

---

## Common QWeb Directives for Reports

### Field Display

```xml
<!-- Simple field -->
<span t-field="o.name"/>

<!-- Formatted date -->
<span t-field="o.date_order" t-options='{"widget": "date"}'/>

<!-- Monetary field with currency -->
<span t-field="o.amount_total"
      t-options='{"widget": "monetary",
                  "display_currency": o.currency_id}'/>

<!-- Duration -->
<span t-field="o.duration" t-options='{"widget": "duration",
                                        "unit": "hour"}'/>
```

### Conditional Display

```xml
<div t-if="o.note">
    <h3>Notes</h3>
    <p t-field="o.note"/>
</div>

<span t-if="o.state == 'done'" class="badge bg-success">Done</span>
<span t-elif="o.state == 'draft'" class="badge bg-secondary">Draft</span>
<span t-else="" class="badge bg-warning">In Progress</span>
```

### Loops

```xml
<t t-foreach="o.line_ids" t-as="line">
    <tr>
        <td><span t-field="line.name"/></td>
        <td><span t-field="line.quantity"/></td>
        <td><span t-field="line.price_unit"/></td>
        <td><span t-field="line.price_total"/></td>
    </tr>
</t>
```

### Page Breaks

```xml
<!-- Force a page break between records -->
<div class="page" style="page-break-after: always;">
    <!-- content for first page -->
</div>
<div class="page">
    <!-- content for second page -->
</div>
```

---

## Troubleshooting

### PDF Missing Styles

If your PDF report is missing CSS styles, verify:

1. CSS/LESS files are in `web.report_assets_common` (not other bundles)
2. wkhtmltopdf can access the CSS files (check URL accessibility)
3. Use inline styles as fallback for critical styling

### Report Not Appearing in Print Menu

Ensure:
- `binding_model_id` references the correct model
- `binding_type` is set to `report`
- Module is installed/updated

### wkhtmltopdf Issues

- Use a compatible wkhtmltopdf version (0.12.6+ with patched Qt)
- Check server logs for wkhtmltopdf errors
- For header/footer issues, adjust `header_spacing` in paper format
