# Checklist — odoo-view-customization

- [ ] Target view identified by XML ID (not by guessing)
- [ ] Inherited view created in `ipai_*` module (not core edit)
- [ ] `inherit_id` correctly references the parent view XML ID
- [ ] Xpath expressions use explicit position (inside/after/before/replace/attributes)
- [ ] Xpath selectors are specific enough to match exactly one element
- [ ] XML ID follows naming convention (`<model>_view_form`, `<model>_action`, etc.)
- [ ] Window actions have correct `res_model` and `view_mode`
- [ ] Menus have correct `parent` reference and `action` binding
- [ ] No core or OCA XML files directly modified
- [ ] Odoo 19 terminology used: "list" not "tree" in user-facing strings
- [ ] View XML is well-formed (valid XML syntax)
- [ ] View file listed in `__manifest__.py` data section
- [ ] View renders correctly on disposable test DB
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-dev/odoo-view-customization/`
