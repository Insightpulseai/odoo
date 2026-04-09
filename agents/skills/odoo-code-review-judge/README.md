# odoo-code-review-judge

Review generated Odoo code against official Odoo 18 coding guidelines. This is the primary quality gate for all Odoo module code.

## When to use
- Code review for any Odoo module (new or modified)
- Pull request containing Odoo Python, XML, JS, or SCSS
- Module audit request
- Post-generation quality gate for implementation skill outputs

## Key rule
Every Odoo code change must pass this review before merge. The judge checks module structure,
Python style, XML conventions, transaction safety, extendability, exception handling, CSS/SCSS
prefixing, and JS/OWL patterns. A single critical violation (cr.commit without justification,
broad exception catch, direct core patching) blocks approval.

## What this is NOT
This is not a persona, not a delivery workflow, not a skill taxonomy. It is a quality gate
backed by the Odoo 18 coding guidelines benchmark.

## Cross-references
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `~/.claude/rules/odoo18-coding.md`
