# odoo-webclient-owl-extension

Extends the Odoo CE 18 web client using OWL components, JS/TS customizations, and SCSS styling.

## When to use
- A new frontend widget or OWL component is needed
- An existing webclient component needs extension via patch()
- Systray items or command palette extensions are required
- Custom SCSS styling is needed for module UI elements

## Key rule
Use `patch()` for extending existing components, never monkey-patching. CSS classes must use
`o_<module>_` prefix, SCSS variables must use `$o-*` prefix. Never create global Composer/mail
patches (learned from `ipai_ai_widget` deprecation).

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/odoo18-coding.md`
