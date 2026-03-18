# Checklist — odoo-report-customization

- [ ] Base report template identified by XML ID
- [ ] Inherited QWeb template created (not replacement)
- [ ] Xpath expressions target correct elements in report layout
- [ ] QWeb directives used correctly (t-esc, t-if, t-foreach, t-call)
- [ ] `t-raw` used only for intentional safe HTML (t-esc preferred)
- [ ] Template handles empty/null data gracefully (no crashes on missing fields)
- [ ] Report action (ir.actions.report) created with correct model binding
- [ ] `report_type` set correctly (qweb-pdf or qweb-html)
- [ ] `report_name` matches the template XML ID
- [ ] Paper format configured if custom sizing needed
- [ ] Template file registered in `__manifest__.py` data section
- [ ] No core report templates directly modified
- [ ] Rendering tested with actual data on disposable DB
- [ ] PDF generation completes without wkhtmltopdf errors
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-dev/odoo-report-customization/`
