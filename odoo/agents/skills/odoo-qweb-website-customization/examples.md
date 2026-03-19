# Examples — odoo-qweb-website-customization

## Example 1: New CTA snippet for website

**Input**: Create a call-to-action building block for the website

**Output** — views/snippets/s_ipai_cta.xml:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="s_ipai_cta" name="IPAI Call to Action">
        <section class="o_ipai_cta_block pt48 pb48 bg-primary text-white">
            <div class="container text-center">
                <h2 class="o_ipai_cta_title">Ready to Get Started?</h2>
                <p class="o_ipai_cta_subtitle lead">Contact us today for a free consultation.</p>
                <a href="/contactus" class="btn btn-light btn-lg o_ipai_cta_btn">Contact Us</a>
            </div>
        </section>
    </template>

    <template id="s_ipai_cta_register" inherit_id="website.snippets">
        <xpath expr="//div[@id='snippet_structure']//t[@t-snippet][last()]" position="after">
            <t t-snippet="ipai_website_ext.s_ipai_cta"
               t-thumbnail="/ipai_website_ext/static/src/images/snippets/s_cta.png"/>
        </xpath>
    </template>
</odoo>
```

- Snippet registration: PASS
- Drag-and-drop: PASS
- Editor configurability: PASS (text editable inline)

## Example 2: Extend portal with custom document section

**Input**: Add "Tax Returns" section to customer portal

**Output**:
```xml
<template id="portal_my_tax_returns" inherit_id="portal.portal_my_home">
    <xpath expr="//div[hasclass('o_portal_docs')]" position="inside">
        <t t-call="portal.portal_docs_entry">
            <t t-set="title">Tax Returns</t>
            <t t-set="url">/my/tax-returns</t>
            <t t-set="placeholder_count" t-value="tax_return_count"/>
        </t>
    </xpath>
</template>
```

- Portal access: PASS (only authenticated users see the section)

## Example 3: Rejected — core homepage template replaced

**Input**: Replace the entire `website.homepage` template

**Output**:
- Validation: FAIL (BLOCKER)
- Reason: Full template replacement breaks theme compatibility and upgrade safety
- Recommendation: Use inherited template with xpath to add/modify specific sections
