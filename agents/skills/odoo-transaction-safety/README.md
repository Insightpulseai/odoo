# odoo-transaction-safety

Verify transaction safety in Odoo code — no unjustified cr.commit(), proper ORM usage,
no raw SQL without justification, correct context handling, and documented sudo() usage.

## When to use
- Code containing database operations (create, write, unlink, SQL)
- Migration scripts or data fixup scripts
- Bulk import or batch processing operations
- Queue job implementations
- Any code using cr.execute() or cr.commit()

## Key rule
The ORM manages transactions. `cr.commit()` is banned unless there is an exceptional,
documented justification (e.g., memory management in very large batch imports). Raw SQL
via `cr.execute()` requires justification — prefer ORM methods. Context must never be
mutated directly. `sudo()` must always have an inline comment explaining why.

## Cross-references
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `~/.claude/rules/odoo19-coding.md`
