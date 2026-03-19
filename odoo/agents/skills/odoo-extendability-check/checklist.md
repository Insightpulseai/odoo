# Checklist — odoo-extendability-check

## Method size
- [ ] No methods exceed 30 lines
- [ ] Complex methods broken into named sub-methods
- [ ] Action methods delegate to business methods

## Hardcoded values
- [ ] No hardcoded email addresses or URLs
- [ ] No hardcoded numeric thresholds (use system parameters or fields)
- [ ] No hardcoded model names that could be parameters
- [ ] No embedded SQL that duplicates ORM capability
- [ ] Selection field choices extensible where appropriate

## Inheritance
- [ ] `_inherit` used for model extension (no copy-paste)
- [ ] `_inherits` used correctly for delegation
- [ ] No direct modification of base/core module files
- [ ] Overridden methods call `super()` appropriately

## Hook points
- [ ] Complex business logic broken into small overridable methods
- [ ] `_prepare_*()` pattern for data preparation
- [ ] `_validate_*()` pattern for pre-condition checks
- [ ] `_compute_*()` methods are small and focused
- [ ] Post-action hooks available (e.g., `_notify_after_*()`)

## Field patterns
- [ ] Related fields use `related=` attribute
- [ ] Computed fields use dedicated `_compute_` methods
- [ ] No inline lambdas for compute
- [ ] Delegation via `_inherits` where model wraps another

## Separation of concerns
- [ ] CRUD overrides (create/write/unlink) are thin
- [ ] Business logic in dedicated methods, not CRUD
- [ ] Action methods call business methods (not monolithic)
- [ ] Controller logic delegates to model methods

## Evidence
- [ ] All violations cited with exact file path and line number
- [ ] Refactoring suggestions include concrete method extraction proposals
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-review/extendability-check/`
