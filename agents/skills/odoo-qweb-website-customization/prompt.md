# Prompt — odoo-qweb-website-customization

You are customizing the Odoo CE 18 website for the InsightPulse AI platform.

Your job is to:
1. Identify the target QWeb template or create a new snippet
2. Create inherited templates for page modifications
3. Register new snippets in the website editor snippet panel
4. Add snippet options for editor configurability
5. Create SCSS styles with `o_<module>_` class prefix
6. Test in the website editor on a disposable database
7. Verify drag-and-drop and editing works for snippets

Platform context:
- Website templates: `views/` directory in ipai_* module
- Snippet templates: `views/snippets/` directory
- SCSS: `static/src/scss/`
- Asset bundle: `web.assets_frontend` for website pages

Snippet registration pattern:
```xml
<!-- Snippet template -->
<template id="s_ipai_feature_block" name="Feature Block">
    <section class="o_ipai_feature_block pt32 pb32">
        <div class="container">
            <h2>Feature Title</h2>
            <p>Feature description</p>
        </div>
    </section>
</template>

<!-- Register in snippet panel -->
<template id="s_ipai_feature_block_snippet" inherit_id="website.snippets">
    <xpath expr="//div[@id='snippet_structure']//t[@t-snippet]" position="before">
        <t t-snippet="ipai_module.s_ipai_feature_block"
           t-thumbnail="/ipai_module/static/src/images/snippets/s_feature_block.png"/>
    </xpath>
</template>
```

Portal page extension:
```xml
<template id="portal_my_custom_inherit" inherit_id="portal.portal_my_home">
    <xpath expr="//div[hasclass('o_portal_docs')]" position="inside">
        <t t-call="portal.portal_docs_entry">
            <t t-set="title">Custom Section</t>
            <t t-set="url">/my/custom</t>
            <t t-set="placeholder_count" t-value="custom_count"/>
        </t>
    </xpath>
</template>
```

Output format:
- Template: path and XML ID
- Snippet: registered (pass/fail)
- SCSS: path (if applicable)
- Editor test: drag-and-drop works (pass/fail)
- Portal access: respects ACL (pass/fail)
- Evidence: editor screenshot or test log

Rules:
- Never directly modify core website templates
- Follow Odoo snippet conventions for building blocks
- CSS class prefix: o_<module>_
- Portal pages must respect access control
- Prefer inherited extension over core patching
- Do not call cr.commit() unless explicitly justified
