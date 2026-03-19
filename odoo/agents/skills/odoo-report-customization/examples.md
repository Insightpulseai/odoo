# Examples — odoo-report-customization

## Example 1: Add margin section to project report

**Input**: Extend project report with profitability margin section

**Output**:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="report_project_profitability_inherit"
              inherit_id="project.report_project_task_list">
        <xpath expr="//div[@class='page']" position="inside">
            <div class="o_ipai_margin_section">
                <h3>Profitability Summary</h3>
                <table class="table table-sm">
                    <tr>
                        <td>Budget</td>
                        <td><span t-esc="doc.budget_amount"
                                   t-options="{'widget': 'monetary', 'display_currency': doc.currency_id}"/></td>
                    </tr>
                    <tr>
                        <td>Actual Cost</td>
                        <td><span t-esc="doc.actual_cost"
                                   t-options="{'widget': 'monetary', 'display_currency': doc.currency_id}"/></td>
                    </tr>
                    <tr>
                        <td>Margin</td>
                        <td><span t-esc="doc.margin_pct"/> %</td>
                    </tr>
                </table>
            </div>
        </xpath>
    </template>
</odoo>
```

- Render test: PASS (tested with project record having budget data)
- PDF generation: PASS

## Example 2: New standalone report for BIR tax return

**Input**: Create PDF report for `ipai.bir.tax.return`

**Output**:
```xml
<record id="action_report_bir_tax_return" model="ir.actions.report">
    <field name="name">BIR Tax Return</field>
    <field name="model">ipai.bir.tax.return</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">ipai_bir_tax_compliance.report_bir_tax_return</field>
    <field name="report_file">ipai_bir_tax_compliance.report_bir_tax_return</field>
    <field name="print_report_name">'BIR_Return_%s' % object.name</field>
</record>
```

## Example 3: Rejected — core template replacement

**Input**: Replace the invoice report template entirely

**Output**:
- Validation: FAIL (BLOCKER)
- Reason: Full template replacement breaks upgrade safety and OCA compatibility
- Recommendation: Use inherited template with xpath to modify specific sections
