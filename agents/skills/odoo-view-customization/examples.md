# Examples — odoo-view-customization

## Example 1: Add margin field to project form view

**Input**: Add `margin_pct` field to `project.project` form view after `partner_id`

**Output**:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="project_project_view_form_inherit_ipai" model="ir.ui.view">
        <field name="name">project.project.form.ipai.ppm</field>
        <field name="model">project.project</field>
        <field name="inherit_id" ref="project.edit_project"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='partner_id']" position="after">
                <field name="margin_pct" widget="percentage"/>
                <field name="is_over_budget" invisible="1"/>
            </xpath>
        </field>
    </record>
</odoo>
```
- XML validation: PASS
- View rendering: PASS

## Example 2: Add menu item for new model

**Input**: Create menu entry for `ipai.finance.report` under Accounting

**Output**:
```xml
<odoo>
    <record id="ipai_finance_report_action" model="ir.actions.act_window">
        <field name="name">Finance Reports</field>
        <field name="res_model">ipai.finance.report</field>
        <field name="view_mode">list,form</field>
    </record>

    <menuitem id="ipai_finance_report_menu"
              name="Finance Reports"
              parent="account.menu_finance"
              action="ipai_finance_report_action"
              sequence="90"/>
</odoo>
```

## Example 3: Rejected — direct core view replacement

**Input**: Replace the sale order form view entirely

**Output**:
- Validation: FAIL (BLOCKER)
- Reason: View replacement breaks upgrade safety and OCA compatibility
- Recommendation: Use inherited view with xpath to modify specific elements
