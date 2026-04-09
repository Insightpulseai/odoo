# Checklist — odoo-xml-structure-check

## File naming
- [ ] View files: `views/<model_name>_views.xml`
- [ ] Data files: `data/<descriptive_name>.xml`
- [ ] Security groups: `security/security.xml`
- [ ] ACLs: `security/ir.model.access.csv`
- [ ] Demo files: `demo/<descriptive_name>.xml`
- [ ] Report files: `report/<report_name>.xml`
- [ ] Wizard views: `wizard/<wizard_name>_views.xml`

## XML ID patterns
- [ ] Form views: `<model>_view_form`
- [ ] List views: `<model>_view_list` (not `_view_tree`)
- [ ] Search views: `<model>_view_search`
- [ ] Kanban views: `<model>_view_kanban`
- [ ] Actions: `<model>_action`
- [ ] Menu roots: `<model>_menu_root`
- [ ] Menu items: `<model>_menu`
- [ ] Security groups: `group_<name>`
- [ ] Record rules: `<model>_rule_<scope>`
- [ ] ACL IDs: `access_<model>_<group>`

## Record formatting
- [ ] One attribute per line for records with >2 attributes
- [ ] Consistent indentation (4 spaces)
- [ ] Proper XML declaration and odoo root tag

## Manifest data ordering
- [ ] Security group definitions listed first
- [ ] ACL files listed second
- [ ] Data files listed third
- [ ] View files listed last

## Odoo 18 compatibility
- [ ] No `tree` view type (must be `list`)
- [ ] No `<tree>` tags (must be `<list>`)
- [ ] No XML IDs using `_tree` pattern (must be `_list`)
- [ ] No `groups_id` references (must be `group_ids`)

## ACL CSV format
- [ ] Correct header with all columns
- [ ] All 4 CRUD columns present (perm_read, perm_write, perm_create, perm_unlink)
- [ ] Values are 0 or 1 only
- [ ] ID pattern: `access_<model>_<group>`

## Data records
- [ ] `noupdate="1"` on user-customizable configuration data
- [ ] `noupdate="0"` (or omitted) on system data that should update

## Evidence
- [ ] All violations cited with exact file path and line number
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-review/xml-structure-check/`
