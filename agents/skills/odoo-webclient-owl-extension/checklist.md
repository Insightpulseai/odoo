# Checklist — odoo-webclient-owl-extension

- [ ] OWL component follows Odoo 18 pattern (static template, static props, setup())
- [ ] Existing components extended via `patch()` (not monkey-patching)
- [ ] No global Composer or mail patches (ipai_ai_widget anti-pattern avoided)
- [ ] JS file uses `/** @odoo-module **/` header
- [ ] XML template created in `static/src/xml/`
- [ ] CSS class names use `o_<module>_` prefix (no bare names)
- [ ] SCSS variables use `$o-*` prefix
- [ ] No ID selectors in CSS
- [ ] No `!important` except when overriding Odoo core (documented)
- [ ] Assets registered in correct bundle (web.assets_backend or web.assets_frontend)
- [ ] Asset paths in `__manifest__.py` are correct
- [ ] No JS console errors in browser
- [ ] Component renders correctly on disposable test DB
- [ ] No core JS files modified directly
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-dev/odoo-webclient-owl-extension/`
