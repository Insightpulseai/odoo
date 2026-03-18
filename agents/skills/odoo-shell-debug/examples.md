# Examples — odoo-shell-debug

## Example 1: Module not loading after deployment

**Input**: `ipai_helpdesk` shows as installed but endpoints return 404

**Output**:
- Container: `ipai-odoo-dev-web`, revision `rev-abc123`, running
- Odoo process: PID 1, uptime 2h, 4 workers
- Module state: `ipai_helpdesk` state=`installed`, but `ir.module.module` shows `latest_version=19.0.1.0.0` vs manifest `19.0.1.1.0`
- Finding: module needs `-u ipai_helpdesk` — code updated but module not upgraded
- Database: connected, PostgreSQL 16.2
- Evidence: `env['ir.module.module'].search([('name','=','ipai_helpdesk')]).read(['state','latest_version'])`

## Example 2: Database connection pool exhaustion

**Input**: Intermittent 500 errors, suspected connection pool issue

**Output**:
- Container: `ipai-odoo-dev-web`, 4 workers
- Database: pool shows 64/64 connections used, 12 waiting
- Finding: `db_maxconn` set to 64 in odoo.conf but 4 workers x 20 threads exceeds pool
- Recommendation: increase `db_maxconn` to 96 or reduce worker thread count
- Evidence: `cat /etc/odoo/odoo.conf | grep db_maxconn` and `env.cr.execute("SELECT count(*) FROM pg_stat_activity")`
