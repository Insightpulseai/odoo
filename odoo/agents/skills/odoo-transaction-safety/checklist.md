# Checklist — odoo-transaction-safety

## Transaction commits
- [ ] No `cr.commit()` calls without explicit justification comment
- [ ] No `self.env.cr.commit()` calls without explicit justification comment
- [ ] No `self._cr.commit()` calls without explicit justification comment
- [ ] Justified commits have documented rollback implications

## Raw SQL
- [ ] No `cr.execute()` for operations achievable via ORM
- [ ] Raw SQL in migrations is justified and documented
- [ ] Raw SQL for performance has benchmark evidence
- [ ] SQL injection prevention: parameterized queries only (no string formatting)

## ORM usage
- [ ] Recordset methods used: `mapped()`, `filtered()`, `sorted()`
- [ ] `ensure_one()` called before single-record operations
- [ ] `search(..., limit=1)` used when expecting single record
- [ ] `env.ref()` used for known XML IDs (not search)
- [ ] `Command` tuples used for x2many writes

## Context handling
- [ ] No direct context mutation (`self.env.context['key'] = val`)
- [ ] `with_context()` used for context changes
- [ ] Context propagated correctly in method chains

## Privilege escalation
- [ ] Every `sudo()` call has inline justification comment
- [ ] `sudo()` scope is minimal (not applied to entire method chains)
- [ ] No `sudo()` that could bypass intended access controls

## Savepoints
- [ ] Batch operations that tolerate partial failure use savepoints
- [ ] Nested transactions use `self.env.cr.savepoint()` where appropriate

## Evidence
- [ ] All violations cited with exact file path and line number
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-review/transaction-safety/`
