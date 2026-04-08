# Judge: migration-risk-judge

## Scope

Assesses risk of OCA module version migration (e.g. 18.0 -> 19.0).

## Verdict: PASS when

- Module manifest version matches target
- No Odoo 19 breaking change patterns detected
- Dependencies all available on target version
- No `tree` view references (must be `list`)
- No `groups_id` references (must be `group_ids`)

## Verdict: FAIL when

- Module on wrong branch
- Known breaking change patterns detected
- Missing dependencies on target version
- Module not yet ported (0 modules on target branch for that repo)

## Odoo 19 Breaking Change Patterns

- `groups_id` -> `group_ids` on `res.users`
- `tree` view type -> `list`
- Portal/Internal User mutually exclusive
- `Command` tuples required for x2many writes
- `web.assets_backend` bundle syntax changes
