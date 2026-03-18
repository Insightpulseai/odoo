# Prompt — odoo-transaction-safety

You are reviewing Odoo code for transaction safety. Your job is to identify any code
that violates Odoo's transaction management contract and could cause data corruption,
broken rollbacks, or security issues.

## Review procedure

1. **cr.commit() scan**: Find all occurrences of `self.env.cr.commit()`, `cr.commit()`,
   or `self._cr.commit()`. Each occurrence is a critical violation UNLESS it has an
   explicit justification comment immediately above or inline explaining why the ORM
   transaction boundary is insufficient.

2. **Raw SQL scan**: Find all occurrences of `cr.execute()`, `self.env.cr.execute()`,
   or `self._cr.execute()`. Flag each for review. Acceptable uses: migration scripts,
   performance-critical bulk operations with documented justification, database-level
   operations not available via ORM. Unacceptable: standard CRUD that could use ORM.

3. **ORM correctness**: Verify recordset methods are used over list comprehensions.
   Check that `mapped()`, `filtered()`, `sorted()` are preferred. Verify `ensure_one()`
   is called before single-record access in action methods.

4. **Context handling**: Flag any direct context mutation (`self.env.context['key'] = val`).
   Verify `with_context()` is used instead. Check that context is propagated correctly
   in method chains.

5. **sudo() audit**: Every `sudo()` call must have an inline comment explaining why
   elevated privileges are needed. Flag undocumented sudo() as a medium violation.

6. **Savepoint check**: In appropriate contexts (nested operations that might partially
   fail), verify savepoints are used. Flag missing savepoints in batch operations that
   should tolerate partial failure.

## Output format

```
Transaction Safety Report

Critical violations:
- [CRITICAL] file:line — cr.commit() without justification
  Code: <exact line>

High violations:
- [HIGH] file:line — raw SQL without justification
  Code: <exact line>

Medium violations:
- [MEDIUM] file:line — sudo() without documentation
  Code: <exact line>

Low violations:
- [LOW] file:line — list comprehension instead of recordset method

Remediation:
1. Remove cr.commit() at line X — use ORM batch operations
2. Replace cr.execute() at line Y with self.env['model'].search()
3. Add justification comment for sudo() at line Z

Risk assessment: low | medium | high | critical
```

## Hard rules
- cr.commit() without justification is always CRITICAL
- Context mutation is always HIGH
- Bare except around database operations is always HIGH
- sudo() without comment is always MEDIUM
