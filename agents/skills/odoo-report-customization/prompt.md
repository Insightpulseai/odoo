# Prompt — odoo-report-customization

You are customizing an Odoo CE 18 report for the InsightPulse AI platform.

Your job is to:
1. Identify the base report template by XML ID
2. Create an inherited QWeb template to extend it
3. Use QWeb directives (t-call, t-foreach, t-if, t-esc) for template logic
4. Create or extend a report action (ir.actions.report) binding it to the model
5. Configure paper format if custom sizing is needed
6. Test rendering with actual data on a disposable database
7. Verify PDF generation completes without error

Platform context:
- Report templates: `report/` or `views/` directory in ipai_* module
- QWeb inheritance: `t-call` for layout, xpath for modifications
- Report action: `ir.actions.report` with `report_type` and `report_name`

QWeb template inheritance:
```xml
<template id="report_custom_inherit" inherit_id="module.report_template_id">
    <xpath expr="//div[@class='page']" position="inside">
        <div class="custom_section">
            <t t-foreach="doc.line_ids" t-as="line">
                <span t-esc="line.name"/>
            </t>
        </div>
    </xpath>
</template>
```

Report action:
```xml
<record id="action_report_custom" model="ir.actions.report">
    <field name="name">Custom Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">module.report_template_id</field>
    <field name="report_file">module.report_template_id</field>
</record>
```

Output format:
- Template: path and XML ID
- Report action: XML ID and model binding
- Paper format: default or custom
- Render test: pass/fail with sample record
- Evidence: rendered PDF or error log

Rules:
- Never replace core report templates — always inherit
- Use t-esc for escaped output (t-raw only for intentional safe HTML)
- Handle empty/null data gracefully in templates
- Test with actual records, not empty renders
- Prefer inherited extension over core patching
- Do not call cr.commit() unless explicitly justified
