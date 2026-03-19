# Bridge Platform Components (IPAI)

## Core Services (when OCA/CE cannot match EE)
1. **Ops Queue + Run Ledger** (Supabase)
   - ops.runs, ops.run_events, ops.artifacts
   - deterministic phases, replay, auditing

2. **Doc/Template Engine** (Reports parity when needed)
   - QWeb where possible
   - external renderer only if necessary (L3)

3. **OCR / Expense Capture**
   - external OCR pipeline (L3)
   - Odoo connector writes attachments + extracted fields

4. **AI / Agent Framework**
   - if Odoo AI is EE-only or limited, use external LLM router
   - Odoo side: prompts/topics stored as records; calls routed out

5. **Browser Automation / QA (Antigravity)**
   - Playwright executor + event stream
   - used for regression, dashboard checks, web tasks

6. **BI / Dashboards**
   - Superset/Metabase/Scout dashboards
   - Odoo exports stable views / read models

## Required Odoo-side Addons
- ipai_ops_connector: queues, callbacks, auth, retries
- ipai_artifacts: attachment mapping + signed URLs
- ipai_auditlog_glue: audit records + chatter summaries
