---
name: odoo_frontend
description: Odoo 19 frontend development — Owl components, assets, SCSS, client actions
category: frontend
priority: high
version: "1.0"
---

# Odoo Frontend Development

## Owl Components (Odoo 19)
- Odoo 19 uses Owl 2.x framework
- Components in static/src/js/ or static/src/components/
- Templates in static/src/xml/
- Import pattern: import { Component } from "@odoo/owl"

## Asset Bundles
- web.assets_backend: backend JS/CSS
- web.assets_frontend: website/portal JS/CSS
- web.assets_frontend_minimal: login page (minimal, critical)
- web.assets_frontend_lazy: deferred frontend assets
- Register in __manifest__.py: 'assets': {'web.assets_backend': ['module/static/src/...']}

## SCSS Conventions
- Class prefix: o_<module>_<component>
- SCSS variables: $o-[root]-[element]-[property]-[modifier]
- No :root CSS custom properties in Odoo UI
- No ID selectors — classes only
- 4-space indent, max 80 char lines
- Property order: position/layout → box model → decorative

## Client Actions
- Register via registry: registry.category("actions").add("my_action", MyComponent)
- XML action: <record model="ir.actions.client"> with tag field

## JS Module System
- Odoo 19 uses native ES modules with @web, @odoo/owl imports
- "use strict" in all JS files
- Never add minified JS libraries to static/

## Tours (Guided Steps)
- static/src/js/tours/ for end-user tours
- static/tests/tours/ for test tours

## Checklist
- [ ] Assets registered in __manifest__.py assets dict
- [ ] CSS classes use o_<module>_ prefix
- [ ] No ID selectors in CSS/SCSS
- [ ] JS uses ES module imports
- [ ] Templates in static/src/xml/
