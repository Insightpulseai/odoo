# odoo-qweb-website-customization

Customizes QWeb themes, website building blocks (snippets), and frontend surfaces in Odoo CE 19.

## When to use
- Website theme needs customization
- A new website building block (snippet) is required
- An existing website page needs layout changes
- Portal page customization is needed

## Key rule
Always use inherited QWeb templates to extend website pages. New snippets must be registered
in the snippet panel and work with the website editor's drag-and-drop. Never directly modify
core website templates.

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/odoo18-coding.md`
