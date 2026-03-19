# Checklist — odoo-qweb-website-customization

- [ ] Target template identified by XML ID (or new snippet created)
- [ ] Inherited templates used for page modifications (not replacement)
- [ ] No core website templates directly modified
- [ ] New snippets registered in website editor snippet panel
- [ ] Snippet has thumbnail image for editor preview
- [ ] Snippet options defined for editor configurability (if applicable)
- [ ] CSS classes use `o_<module>_` prefix (no bare class names)
- [ ] SCSS variables use `$o-*` prefix
- [ ] SCSS registered in `web.assets_frontend` bundle
- [ ] Templates registered in `__manifest__.py` data section
- [ ] Drag-and-drop works in website editor (for snippets)
- [ ] Portal pages respect access control (no unauthorized data)
- [ ] QWeb directives used correctly (t-esc, t-if, t-foreach)
- [ ] Tested on disposable DB with website editor
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-dev/odoo-qweb-website-customization/`
