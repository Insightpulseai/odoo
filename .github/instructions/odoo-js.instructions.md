---
applyTo: "addons/**/static/src/**/*.{js,xml,scss}"
---

You are editing Odoo 18 CE frontend code (JavaScript, Owl components, SCSS, QWeb templates).

## Module system

- Odoo 18 uses native ES modules with `@odoo/` namespace
- Import from `@odoo/owl` for Owl components
- Import from `@web/core/...` for core services, registries, utils
- Use `/** @odoo-module **/` comment at top of JS files

## Owl components

- Extend with class inheritance: `class MyWidget extends Component`
- Use `setup()` for initialization, not constructor
- Register in appropriate registry: `registry.category("actions")`, `registry.category("systray")`
- Templates use QWeb syntax in companion `.xml` files

## Registries and services

- `registry.category("services")` for services
- `registry.category("actions")` for client actions
- `registry.category("fields")` for field widgets
- `registry.category("view_widgets")` for view widgets
- Use `useService("service_name")` hook in components

## Patching

- Use `patch(OriginalClass.prototype, { ... })` from `@web/core/utils/patch`
- Prefer patching over full replacement
- Document what you're patching and why

## Assets

- Declare in `__manifest__.py` under `assets` key
- Use bundle names: `web.assets_backend`, `web.assets_frontend`, `web.assets_common`
- SCSS variables: prefer Odoo's Bootstrap variables over custom ones

## Do not

- Use jQuery for new code (Owl/vanilla JS only)
- Import from Enterprise asset bundles
- Create global side effects outside module registration
- Hardcode URLs or API endpoints in JS (use controllers)
