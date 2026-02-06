# Module Completeness Policy (CE + OCA Baseline)

## Baseline Assumption
All environments must start from:
- Odoo CE 19
- OCA base stack (see `docs/stack/BASELINE_OCA_STACK.md`)

## Rule: Custom modules MUST be standalone-installable
Any `ipai_*` module must:
1) Install cleanly on a fresh DB with only the baseline installed
2) Declare all needed dependencies in `__manifest__.py`
3) Use inheritance (`_inherit`, XML view inheritance) instead of copying core/OCA logic
4) Never require manual UI steps to become functional (unless explicitly documented as unavoidable)
5) Provide deterministic install order (via dependencies, not “human memory”)

## Dependency Principles
- Prefer OCA modules over custom code
- If extending Sales or Purchase, depend on the OCA extension module explicitly
- Do NOT depend on Enterprise modules
- If an external service is required, depend on `ipai_ops_connector` and declare `ir.config_parameter` keys

## Install Verification (Required)
Each custom module must pass:
- `odoo --stop-after-init -u <module>` on a clean DB with baseline installed
- XML parse validation
- ACL presence for all non-transient models
