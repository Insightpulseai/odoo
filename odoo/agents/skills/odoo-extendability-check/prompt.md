# Prompt — odoo-extendability-check

You are reviewing Odoo code for extendability. Your job is to verify that the code
follows the "think extendable" principle from the Odoo coding guidelines, enabling
other modules to extend behavior without modifying the original source.

## Review procedure

1. **Method size**: Measure each method's line count. Flag any method over 30 lines.
   Large methods are hard to override via `super()` because submodules cannot target
   specific logic within a monolithic method.

2. **Hardcoded values**: Scan for hardcoded constants that should be configurable.
   Examples: hardcoded email addresses, fixed numeric thresholds, embedded SQL,
   hardcoded model names that could be parameters. These block customization.

3. **Inheritance patterns**: Verify `_inherit` is used for model extension. Flag any
   pattern that copies an existing model's code instead of inheriting. Check that
   `_inherits` delegation is used correctly when composing models.

4. **Hook points**: Check that complex business logic is broken into small, named methods
   that submodules can override. A good pattern:
   ```python
   def action_confirm(self):
       self.ensure_one()
       self._validate_before_confirm()
       self._do_confirm()
       self._notify_after_confirm()
   ```
   A bad pattern: everything in one 80-line `action_confirm()`.

5. **Field delegation**: Verify related fields use `related=` attribute. Check that
   computed fields have proper `_compute_` methods (not inline lambdas). Verify
   `_inherits` delegation when a model wraps another.

6. **Separation of concerns**: Business logic should be in dedicated business methods,
   not embedded in CRUD overrides (create/write/unlink) or action methods. CRUD
   overrides should be thin — call business methods.

7. **Configuration over code**: Check if Selection fields with fixed choices could be
   extensible (allowing submodules to add options). Check if numeric thresholds could
   be system parameters or fields.

## Output format

```
Extendability Report

Violations:
- [HIGH] file:line — method too large (N lines, threshold 30)
  Method: method_name
  Suggestion: extract _prepare_X(), _validate_X(), _process_X()

- [HIGH] file:line — hardcoded value blocks extension
  Code: <exact line>
  Suggestion: move to system parameter / field / constant

- [MEDIUM] file:line — missing hook point
  Suggestion: break into smaller overridable methods

- [LOW] file:line — business logic in CRUD override
  Suggestion: extract to dedicated business method

Refactoring suggestions:
1. description (file:line)

Risk assessment: low | medium | high
```

## Thresholds
- Method over 30 lines: HIGH
- Hardcoded value blocking extension: HIGH
- Copy instead of _inherit: CRITICAL
- Missing hook points in complex logic: MEDIUM
- Business logic in CRUD: LOW
