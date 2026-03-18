# Integrations Evidence Index

Each active integration must have:
- connection verification evidence
- sample payload or record trace
- timestamp
- environment
- result
- operator or agent reference

Naming convention:
- `YYYY-MM-DD_<flow-id>_<env>.md`

Example:
- `2026-03-15_github_webhook_n8n_odoo_dev.md`
- `2026-03-15_n8n_supabase_task_bus_dev.md`

Required fields per evidence file:
- flow_id
- date
- environment (dev / staging / prod)
- connection test result (pass / fail)
- sample data or payload excerpt (redacted if sensitive)
- operator (human or agent ID)
- commit SHA at time of test
