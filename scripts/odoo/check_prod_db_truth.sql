-- Production Database Truth Comparison
-- Run against both 'odoo' and 'odoo_prod' databases separately:
--   psql -h <host> -U <user> -d odoo -f scripts/odoo/check_prod_db_truth.sql
--   psql -h <host> -U <user> -d odoo_prod -f scripts/odoo/check_prod_db_truth.sql
-- Save outputs side by side for comparison.

SELECT '=== Database Identity ===' AS section;
SELECT current_database() AS database_name, now() AS checked_at;

SELECT '=== Core Table Counts ===' AS section;
SELECT 'res_users' AS table_name, count(*) AS row_count FROM res_users
UNION ALL SELECT 'res_company', count(*) FROM res_company
UNION ALL SELECT 'res_partner', count(*) FROM res_partner
UNION ALL SELECT 'ir_attachment', count(*) FROM ir_attachment
UNION ALL SELECT 'ir_module_module (installed)', count(*) FROM ir_module_module WHERE state = 'installed'
UNION ALL SELECT 'ir_module_module (total)', count(*) FROM ir_module_module
UNION ALL SELECT 'mail_message', count(*) FROM mail_message
UNION ALL SELECT 'ir_config_parameter', count(*) FROM ir_config_parameter
ORDER BY table_name;

SELECT '=== Business Table Counts ===' AS section;
SELECT 'account_move' AS table_name, count(*) AS row_count FROM account_move
UNION ALL SELECT 'account_move_line', count(*) FROM account_move_line
UNION ALL SELECT 'sale_order', count(*) FROM sale_order
UNION ALL SELECT 'purchase_order', count(*) FROM purchase_order
UNION ALL SELECT 'stock_picking', count(*) FROM stock_picking
UNION ALL SELECT 'project_task', count(*) FROM project_task
UNION ALL SELECT 'hr_employee', count(*) FROM hr_employee
ORDER BY table_name;

SELECT '=== Latest Write Timestamps ===' AS section;
SELECT 'res_partner' AS table_name, max(write_date) AS latest_write FROM res_partner
UNION ALL SELECT 'res_users', max(write_date) FROM res_users
UNION ALL SELECT 'ir_attachment', max(write_date) FROM ir_attachment
UNION ALL SELECT 'mail_message', max(create_date) FROM mail_message
ORDER BY table_name;

SELECT '=== Key Config Parameters ===' AS section;
SELECT key, value FROM ir_config_parameter
WHERE key IN ('web.base.url', 'database.uuid', 'database.create_date', 'base.login_cooldown_after')
ORDER BY key;
