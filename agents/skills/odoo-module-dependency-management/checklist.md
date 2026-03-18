# Checklist — odoo-module-dependency-management

- [ ] Target module `__manifest__.py` parsed for `depends` list
- [ ] Full transitive dependency chain resolved
- [ ] All dependencies available in configured addons paths
- [ ] No circular dependencies detected
- [ ] OCA dependencies verified on 19.0 branch with Stable status
- [ ] No Enterprise module dependencies (hard blocker)
- [ ] No odoo.com IAP dependencies
- [ ] Module registered in `config/addons.manifest.yaml`
- [ ] Config -> OCA -> Delta philosophy respected
- [ ] No OCA source modifications — ipai_* overrides only
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-module-dependency-management/`
