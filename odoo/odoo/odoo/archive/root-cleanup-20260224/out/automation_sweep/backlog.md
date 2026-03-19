# Automation Backlog

Ranked by priority (P0 → P2). Tags: [ROI:H/M/L] [Risk:H/M/L] [Effort:Nd]

---

## P0 — Immediate Value, Low Risk

### Move Stray Workflows to Canonical Location

- **Move**: `notion-n8n-monthly-close/workflows/ODOO_EXPENSE_OCR.json` → `automations/n8n/workflows/ODOO_EXPENSE_OCR.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `notion-n8n-monthly-close/workflows/ODOO_KNOWLEDGE_GOV.json` → `automations/n8n/workflows/ODOO_KNOWLEDGE_GOV.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `notion-n8n-monthly-close/workflows/ODOO_BIR_PREP.json` → `automations/n8n/workflows/ODOO_BIR_PREP.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `notion-n8n-monthly-close/workflows/W150_FINANCE_HEALTH_CHECK.json` → `automations/n8n/workflows/W150_FINANCE_HEALTH_CHECK.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `notion-n8n-monthly-close/workflows/odoo/W902_OD_VIEW_HEALTHCHECK.json` → `automations/n8n/workflows/W902_OD_VIEW_HEALTHCHECK.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `notion-n8n-monthly-close/workflows/odoo/W401_CC_EXPENSE_IMPORT.json` → `automations/n8n/workflows/W401_CC_EXPENSE_IMPORT.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `notion-n8n-monthly-close/workflows/odoo/W002_OD_BIR_ALERTS.json` → `automations/n8n/workflows/W002_OD_BIR_ALERTS.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `notion-n8n-monthly-close/workflows/odoo/W501_EQ_BOOKING_SYNC.json` → `automations/n8n/workflows/W501_EQ_BOOKING_SYNC.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `notion-n8n-monthly-close/workflows/odoo/W001_OD_MNTH_CLOSE_SYNC.json` → `automations/n8n/workflows/W001_OD_MNTH_CLOSE_SYNC.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `notion-n8n-monthly-close/workflows/supabase/W101_SB_CLOSE_SNAPSHOT.json` → `automations/n8n/workflows/W101_SB_CLOSE_SNAPSHOT.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `web/platform-kit/infra/n8n/plane-odoo-sync.workflow.json` → `automations/n8n/workflows/plane-odoo-sync.workflow.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n_ocr_expense_webhook.json` → `automations/n8n/workflows/n8n_ocr_expense_webhook.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n_bir_deadline_webhook.json` → `automations/n8n/workflows/n8n_bir_deadline_webhook.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n_scout_sync_webhook.json` → `automations/n8n/workflows/n8n_scout_sync_webhook.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/finance_ppm/monthly_report.json` → `automations/n8n/workflows/monthly_report.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/finance_ppm/task_escalation.json` → `automations/n8n/workflows/task_escalation.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/finance_ppm/bir_deadline_alert.json` → `automations/n8n/workflows/bir_deadline_alert.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/odoo/W403_AP_AGING_HEATMAP.json` → `automations/n8n/workflows/W403_AP_AGING_HEATMAP.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n/git-operations-workflow.json` → `automations/n8n/workflows/git-operations-workflow.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n/expense-ocr-workflow.json` → `automations/n8n/workflows/expense-ocr-workflow.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n/expense-approval-workflow.json` → `automations/n8n/workflows/expense-approval-workflow.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n/sync-docs-changed.json` → `automations/n8n/workflows/sync-docs-changed.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n/sync-spec-changed.json` → `automations/n8n/workflows/sync-spec-changed.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n/sync-schema-changed.json` → `automations/n8n/workflows/sync-schema-changed.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `workflows/n8n/sync-complete.json` → `automations/n8n/workflows/sync-complete.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `docs/evidence/20260127-0630/platform-kit-merge/workflows/platform-kit-orchestrator.json` → `automations/n8n/workflows/platform-kit-orchestrator.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/n8n_tenant_provisioning.json` → `automations/n8n/workflows/n8n_tenant_provisioning.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/billing-subscription-created.json` → `automations/n8n/workflows/billing-subscription-created.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/github-router.json` → `automations/n8n/workflows/github-router.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/deployment-notify.json` → `automations/n8n/workflows/deployment-notify.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/github-events-handler.json` → `automations/n8n/workflows/github-events-handler.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/github-deploy-trigger.json` → `automations/n8n/workflows/github-deploy-trigger.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/chatops-hotfix.json` → `automations/n8n/workflows/chatops-hotfix.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/vercel-drain-handler.json` → `automations/n8n/workflows/vercel-drain-handler.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/integration/workspace-events-handler.json` → `automations/n8n/workflows/workspace-events-handler.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/integration/event-router.json` → `automations/n8n/workflows/event-router.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/integration/github-artifacts-mirror.json` → `automations/n8n/workflows/github-artifacts-mirror.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/control-plane/health-check-scheduler.json` → `automations/n8n/workflows/health-check-scheduler.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/control-plane/backup-scheduler.json` → `automations/n8n/workflows/backup-scheduler.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `n8n/workflows/control-plane/deploy-trigger.json` → `automations/n8n/workflows/deploy-trigger.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `_work/OCA-ai/ai_oca_bridge_document_page/static/description/RagCapabilitiesWithOdooKnowledge.json` → `automations/n8n/workflows/RagCapabilitiesWithOdooKnowledge.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **Move**: `_work/OCA-ai/ai_oca_bridge_chatter/static/description/Chat.json` → `automations/n8n/workflows/Chat.json`
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d
  - **Next action**: Run `sweep_repo.py --apply` to auto-move

- **`scripts/staging_restore_and_sanitize.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/promote.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy/do-bootstrap-odoo-prod.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/automations/sweep_repo.py`**
  - Convert to n8n workflow: fetch→transform pipeline: n8n candidate
  - Signals: fetch→transform pipeline: n8n candidate, DB query + HTTP call: event-driven n8n candidate, cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate, Slack webhook: n8n Slack node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`


## P1 — High Value, Moderate Effort

- **`infra/ops-control/odoo_modules/ipai_ask_ai/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_partner_pack/models/implementation.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_marketing_agency_pack/models/media.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_accounting_firm_pack/models/workpaper.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/tbwa_spectra_integration/models/hr_expense_advance.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/tbwa_spectra_integration/models/spectra_export.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`config/PRODUCTION_DEPLOYMENT_SCRIPT.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_sms_gateway/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_sms_gateway/models/ipai_sms_message.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_month_end/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_month_end/models/task.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_enterprise_bridge/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_bir_notifications/models/bir_alert.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ocr_gateway/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ocr_gateway/models/ipai_ocr_job.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_request/tests/test_purchase_request_procurement.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_automatic_workflow/models/automatic_workflow_job.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/rest-framework/rest_log/models/rest_log.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job/models/queue_job.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/reporting-engine/bi_sql_editor/tests/test_bi_sql_view.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_bir_tax_compliance/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_change_request.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_docflow_review/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_docflow_review/models/docflow_document.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_docflow_review/controllers/ingest.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_superset_connector/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_tbwa_finance/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_tbwa_finance/models/finance_task.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_crm_pipeline/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_crm_pipeline/models/crm_lead.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_request/tests/test_purchase_request_procurement.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/rest-framework/rest_log/models/rest_log.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/reporting-engine/bi_sql_editor/tests/test_bi_sql_view.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/configure-n8n-smtp.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/finish-n8n-setup.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/plane/infra/deploy-plane-ocr-droplet.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy-otp-auth.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/test_mcp_jobs.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/generate_go_live_checklist.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/generate_month_end_imports.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy-mailgun-mailgate.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/configure_google_oauth.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/enhanced_health_check.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/install-odoo-18-modules.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/fix_oauth_button_odoo_core.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/test_auth_bootstrap.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/bootstrap_github_issues.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/fix_oauth_button.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/configure_gmail_smtp.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ipai_full_audit.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/test_ee_parity.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/baseline-validation.sh`**
  - Convert to n8n workflow: fetch→transform pipeline: n8n candidate
  - Signals: fetch→transform pipeline: n8n candidate, cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo_smoke_close.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy/deploy-prod-e2e.sh`**
  - Convert to n8n workflow: fetch→transform pipeline: n8n candidate
  - Signals: fetch→transform pipeline: n8n candidate, polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/rotate_zoho_password.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/test_auth_flows_safe.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`ops/backup-production.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate, email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`


## P2 — Nice to Have

- **`infra/ops-control/odoo_modules/ipai_ask_ai_chatter/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`infra/databricks/notebooks/gold/control_room_status.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`infra/databricks/src/workbench/observability/alerts.py`**
  - Convert to n8n workflow: Slack webhook: n8n Slack node candidate
  - Signals: Slack webhook: n8n Slack node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`infra/do-oca-stack/scripts/oca-rollback.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`infra/nginx/setup-https.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`infra/nginx/fix-port-binding.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`infra/superset/superset_config.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`infra/superset/entrypoint.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`tools/parity/test_ee_parity.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`tools/ipai_module_gen/ipai_module_gen/generate.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_finance_ap_aging/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_finance_ap_aging/models/account_move_line.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_partner_pack/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_partner_pack/models/service_pack.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_partner_pack/models/quote_calculator.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_docs/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_docs/tests/test_workspace_visibility.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_docs/models/ipai_doc.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_idp/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_idp/models/idp_document.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_idp/services/idp_service_parser.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_finance_controller_dashboard/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_finance_controller_dashboard/tests/test_controller_kpi.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_finance_controller_dashboard/models/finance_controller_kpi.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_marketing_agency_pack/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_marketing_agency_pack/models/client_brand.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_marketing_agency_pack/models/campaign.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_marketing_agency_pack/models/creative.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_accounting_firm_pack/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_accounting_firm_pack/models/compliance.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/ipai_accounting_firm_pack/models/engagement.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`archive/addons/tbwa_spectra_integration/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`bin/import_bir_schedules.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`bin/finance-cli.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`bin/postdeploy-finance.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`notion-n8n-monthly-close/scripts/deduplicate_closing_tasks.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`docflow-agentic-finance/scripts/viber_watch_daemon.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`specs/003-ai-enrichment/odoo_automation_action.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`web/platform-kit/sandbox/dev/scripts/github/dispatch-enroll-repo.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`web/platform-kit/scripts/audit/lib.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`web/platform-kit/scripts/audit/run_integration_audit.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`web/platform-kit/scripts/audit/checks/check_mailgun.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`web/platform-kit/scripts/mailgun/mailgun-domain-setup.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`web/platform-kit/scripts/email/test_mailgun_send.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`web/platform-kit/scripts/email/verify_email_config.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ai_agent_builder/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_canvas/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_canvas/models/canvas.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_collab/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_collab/models/comment.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_platform_permissions/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_month_end/models/closing.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_ai_agent_builder/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_finance_ppm/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_finance_ppm/models/project_task_integration.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_web_fluent2/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_rest_controllers/controllers/main.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_web_theme_tbwa/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_enterprise_bridge/models/maintenance_equipment_integration.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_enterprise_bridge/models/enterprise_bridge.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_enterprise_bridge/models/ipai_job.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_enterprise_bridge/models/res_config_settings.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_enterprise_bridge/models/hr_expense_integration.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_enterprise_bridge/models/project_task_integration.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_enterprise_bridge/controllers/mailgun_mailgate.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_ops_connector/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_ops_connector/models/ops_run.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_system_config/hooks.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_system_config/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_helpdesk/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_helpdesk/models/helpdesk_stage.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_helpdesk/models/helpdesk_ticket.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_helpdesk/models/helpdesk_team.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_whatsapp_connector/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_zoho_mail/__init__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_zoho_mail/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_expense_ocr/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_finance_workflow/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_hr_payroll_ph/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_hr_payroll_ph/models/hr_payslip.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_hr_payroll_ph/models/hr_contract.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_sign/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_documents_ai/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_hr_expense_liquidation/models/hr_expense_liquidation.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai/ipai_bir_notifications/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ops_mirror/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ops_mirror/models/ops_summary.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_core/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_core/models/page.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_core/models/space.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_core/models/workspace.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ask_ai_chatter/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ask_ai_chatter/models/ask_ai_request.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ask_ai_chatter/models/mail_message.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/account-financial-tools/account_move_name_sequence/tests/test_account_incoming_supplier_invoice.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/account-financial-tools/account_move_name_sequence/models/account_move.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/product_supplier_code_purchase/tests/test_product_supplier_code_purchase.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_force_invoiced/tests/test_purchase_force_invoiced.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_order_type/tests/test_purchase_order_type.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_request/wizard/purchase_request_line_make_purchase_order.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_request/models/purchase_request.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_request/models/purchase_request_line.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_request/models/stock_move_line.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_request/models/purchase_order.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_request/models/stock_move.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/purchase-workflow/purchase_request/models/purchase_request_allocation.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-tools/base_technical_user/tests/test_sudo_tech.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-tools/base_view_inheritance_extension/tests/test_base_view_inheritance_extension.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-tools/auditlog/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-tools/auditlog/tests/test_auditlog.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-tools/auditlog/wizards/autovacuum.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/web/web_responsive/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/web/web_responsive/tests/test_res_users.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/web/web_environment_ribbon/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_stock_picking_blocking/tests/test_sale_stock_picking_blocking.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_order_line_date/tests/test_sale_order_line_date.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_stock_reference_by_line/model/sale.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_force_invoiced/tests/test_sale_force_invoiced.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_automatic_workflow/tests/test_automatic_workflow.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_automatic_workflow/models/sale_workflow_process.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_order_line_price_history/tests/test_sale_order_line_price_history.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_exception/tests/test_multi_records.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_exception/tests/test_sale_exception.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_order_disable_user_autosubscribe/tests/test_sale_order_disable_user_autosubscribe.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/sale-workflow/sale_order_disable_user_autosubscribe/models/sale_order.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/fs_storage/tests/common.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_backend_sftp/components/sftp_adapter.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_file/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_file/models/ir_actions_report.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_file/models/storage_file.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/fs_attachment/tests/common.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_image/tests/common.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_image/tests/test_storage_image.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_image/models/storage_image.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_image_product/models/product_template.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_image_product/models/product_product.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/storage/storage_backend/components/base_adapter.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/account-financial-reporting/partner_statement/tests/test_res_config_settings.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/knowledge/document_url/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/knowledge/document_url/tests/test_document_url.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/mis-builder/mis_builder_budget/models/mis_budget.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/mis-builder/mis_builder_budget/models/mis_budget_by_account.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/mis-builder/mis_builder_budget/models/mis_budget_abstract.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/mis-builder/mis_builder/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/rest-framework/fastapi/dependencies.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/rest-framework/rest_log/exceptions.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/rest-framework/rest_log/tests/common.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/rest-framework/rest_log/components/service.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-backend/base_user_role/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_batch/models/queue_job_batch.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_batch/controllers/webclient.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron/tests/test_queue_job_cron.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron/tests/__init__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron/models/__init__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron/models/ir_cron.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job/utils.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job/migrations/18.0.1.7.0/pre-migration.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron_jobrunner/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron_jobrunner/tests/test_queue_job.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron_jobrunner/models/__init__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron_jobrunner/models/queue_job.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_cron_jobrunner/models/ir_cron.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/base_import_async/tests/test_base_import_import.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/queue_job_subscribe/tests/test_job_subscribe.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/test_queue_job/tests/test_job.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/queue/test_queue_job/tests/test_autovacuum.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/timesheet/hr_timesheet_task_stage/tests/test_hr_timesheet_task_stage.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-ux/base_substate/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-ux/base_substate/tests/test_base_substate.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-ux/base_substate/tests/sale_test.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-ux/base_substate/models/base_substate_mixin.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-ux/base_substate/models/base_substate.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/server-ux/date_range/tests/test_date_range_type.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/reporting-engine/sql_request_abstract/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/reporting-engine/sql_request_abstract/models/sql_request_mixin.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/oca/reporting-engine/bi_sql_editor/models/bi_sql_view.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_bir_tax_compliance/models/bir_filing_deadline.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_bir_tax_compliance/models/bir_withholding.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_bir_tax_compliance/models/bir_tax_return.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_resource.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/okr_checkin.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/okr_initiative.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_issue.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_workstream.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_risk.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_program.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_budget.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_portfolio.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/okr_objective.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/okr_cycle.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_project_meta.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/okr_key_result.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ppm_okr/models/ppm_epic.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_grid_view/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_grid_view/models/grid_view.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_grid_view/models/grid_column.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ai_tools/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ai_tools/tools/crm_tools.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ai_tools/tools/calendar_tools.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ai_tools/tests/test_tool_execution.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_platform_approvals/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_db/models/property.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_workos_db/models/database.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ask_ai/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ask_ai/models/ask_ai_channel.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_ask_ai/models/ask_ai_service.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_platform_audit/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_platform_workflow/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_platform_workflow/models/workflow_mixin.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_superset_connector/models/superset_connection.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_superset_connector/models/superset_analytics_view.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_superset_connector/models/superset_dataset.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_tbwa_finance/models/closing_period.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_tbwa_finance/models/bir_return.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_finance_ppm_umbrella/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`addons/ipai_finance_ppm_umbrella/scripts/generate_seed_from_excel.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`runtime/docker/docker/test-ce19.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`runtime/docker/docker/run-local-ce19.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`workflows/finance_ppm/verify_deployment.sh`**
  - Convert to n8n workflow: fetch→transform pipeline: n8n candidate
  - Signals: fetch→transform pipeline: n8n candidate
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`docs/evidence/20260212-1630/ssot-validation/validate_ssot_excel.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`docs/portfolio/specs/knowledge-graph/create-issues.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`docs/templates/ipai-ops-stack/scripts/up.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`docs/tutorials/jinja2-basics/examples/04_odoo_module_example.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.devcontainer/scripts/post-create.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`pkgs/ipai-ai-sdk-python/setup.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/account-financial-tools/account_move_name_sequence/tests/test_account_incoming_supplier_invoice.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/account-financial-tools/account_move_name_sequence/models/account_move.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/product_supplier_code_purchase/tests/test_product_supplier_code_purchase.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_force_invoiced/tests/test_purchase_force_invoiced.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_order_type/tests/test_purchase_order_type.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_request/wizard/purchase_request_line_make_purchase_order.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_request/models/purchase_request.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_request/models/purchase_request_line.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_request/models/stock_move_line.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_request/models/purchase_order.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_request/models/stock_move.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/purchase-workflow/purchase_request/models/purchase_request_allocation.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-tools/base_technical_user/tests/test_sudo_tech.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-tools/base_view_inheritance_extension/tests/test_base_view_inheritance_extension.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-tools/auditlog/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-tools/auditlog/tests/test_auditlog.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-tools/auditlog/wizards/autovacuum.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/web/web_responsive/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/web/web_responsive/tests/test_res_users.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/web/web_environment_ribbon/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/account-financial-reporting/partner_statement/tests/test_res_config_settings.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/knowledge/document_url/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/knowledge/document_url/tests/test_document_url.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/mis-builder/mis_builder_budget/models/mis_budget.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/mis-builder/mis_builder_budget/models/mis_budget_by_account.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/mis-builder/mis_builder_budget/models/mis_budget_abstract.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/mis-builder/mis_builder/__manifest__.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_priority/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_priority/models/partner_priority.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_priority/models/res_partner.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_multi_relation/models/res_partner_relation.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_identification/tests/test_partner_identification.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_identification/models/res_partner_id_number.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_contact_birthdate/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_contact_personal_information_page/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/base_partner_sequence/tests/test_base_partner_sequence.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_email_check/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_email_check/tests/test_partner_email_check.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_email_check/models/res_company.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/partner-contact/partner_email_check/models/res_partner.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/rest-framework/fastapi/dependencies.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/rest-framework/rest_log/exceptions.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/rest-framework/rest_log/tests/common.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/rest-framework/rest_log/components/service.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/timesheet/hr_timesheet_task_stage/tests/test_hr_timesheet_task_stage.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-ux/base_substate/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-ux/base_substate/tests/test_base_substate.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-ux/base_substate/tests/sale_test.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-ux/base_substate/models/base_substate_mixin.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-ux/base_substate/models/base_substate.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-ux/date_range/tests/test_date_range_type.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/reporting-engine/sql_request_abstract/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/reporting-engine/sql_request_abstract/models/sql_request_mixin.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/reporting-engine/bi_sql_editor/models/bi_sql_view.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-auth/impersonate_login/hooks.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-auth/impersonate_login/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-auth/impersonate_login/models/mail_thread.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-auth/impersonate_login/models/mail_message.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-auth/auth_oidc/tests/test_auth_oidc_auth_code.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-auth/auth_oidc/models/auth_oauth_provider.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-auth/auth_user_case_insensitive/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`third_party/oca/server-auth/auth_user_case_insensitive/tests/test_res_users.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`odoo-schema-mirror/tests/test_generate_dbml.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`prototypes/ipai_fluent_web_365_copilot/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`prototypes/ipai_fluent_web_365_copilot/models/fluent_copilot_session.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/upgrade-to-odoo19.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/addons/ipai_mailgun_bridge/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/addons/ipai_mailgun_bridge/models/__init__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/addons/ipai_mailgun_bridge/models/mail_mail.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/addons/ipai_mailgun_bridge/controllers/mailgun_webhook.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/verify-n8n-setup.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/supabase/verify-integration.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/supabase/test-webhook.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/figma/verify_integration.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/dev/init-db.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/dev/start-dev.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/dev/install-mailgun-addon.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/dev/configure-mailgun-smtp.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/dev/up.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/mailgun/configure-routes.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/mailgun/verify-parity.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/scripts/mailgun/test-outbound-email.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`sandbox/dev/plane/infra/deploy-plane-droplet.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`ocr-adapter/test-ocr.sh`**
  - Convert to n8n workflow: fetch→transform pipeline: n8n candidate
  - Signals: fetch→transform pipeline: n8n candidate
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/network/download.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/network/session.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/utils/wheel.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/operations/check.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/operations/install/wheel.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/resolution/legacy/resolver.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/index/collector.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/commands/show.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/commands/list.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/metadata/_json.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/metadata/pkg_resources.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/metadata/base.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_internal/metadata/importlib/_dists.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/controller.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`.venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/heuristics.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/verify-codespaces-auth.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/verify_supabase_deploy.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/test-mailgun.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/diagnose_smtp.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo_seed_post_upgrade.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo_start_fetchmail.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/configure_zoho_smtp.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/cloudflare-dns-audit.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/db-cleanup-legacy.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/simple_deploy.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/validate_m1.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/start-odoo-tunnel.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/healthcheck_odoo.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy-bir-compliance.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/audit_oca_modules.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/verify-dns-baseline.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/convert_seed_to_xml.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/setup-mailgun-secrets.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/update_tasks_after_import.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ci_smoke_test.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/scaffold_ipai_parity.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/generate_odoo_template.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/validate_ee_iap_independence.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/recreate_odoo_prod.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/test_email_flow.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_workos_prod.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/configure_gmail_smtp.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/go_live.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/verify_smtp.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/introspect_project.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/delete_user_safe.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo_check_mail.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/validate_production.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/apply_config.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/backup_odoo.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_theme_to_production.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/run_clarity_ppm_reverse.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/worktree-setup.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/run_odoo_shell.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/sync_ipai_sample_metrics_to_supabase.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/check_go_live_manifest.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo_config_mail_ai_ocr.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/screenshot_production.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/verify_email_auth.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/diagnose_prod.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/audit_email_config.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo_configure_mail.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/fix-finance-ppm-schema.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/fix_pos_enterprise_error.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/generate_2026_schedule.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy-odoo-modules.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_with_credentials.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/bootstrap_ssot_dns_odoo_supabase.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/provision_tenant.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/validate_manifest.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/check-enterprise-modules.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/notify_slack.sh`**
  - Convert to n8n workflow: Slack webhook: n8n Slack node candidate
  - Signals: Slack webhook: n8n Slack node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/install_baseline.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/seed_companies_users.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/generate_module_health_report.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/generate_module_docs.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_production.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/test-mailgun.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_vercel_prod.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/scaffold_ipai_parity.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ipai_install_upgrade_test.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/validate_ssot_excel.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/auto_error_handler.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/setup_config_env.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/configure_sendgrid_smtp.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/test_theme_locally.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo_import_project_suite.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/configure_mailgun_smtp.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/audit_installed_modules.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_afc_rag.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/convert_csv_to_xml.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_prod.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_custom_image.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/db_verify.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/bootstrap_execution_board.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/promote_oauth_users.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy-december-2025-bir-tasks.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo_rationalization.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo_rollback_mail_ai_ocr.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/configure_smtp.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/staging_up.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_complete_fix.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase_delete_user.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/test_magic_link.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ci_odoo_run_install_upgrade.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/sync_odoo_shadow.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/force_asset_regeneration.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy_odoo_smart.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/install_all_ipai_modules.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/start_local_odoo.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ce_oca_audit.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/hotfix_production.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/finance_ppm_seed_audit.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/fixes/fix_odoo_email_config.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/prod/deploy_workos.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/auth/confirm_user.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/lakehouse/coverage_audit.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ci/deploy-ipai-modules.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ci/smoke_odoo_container.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ci/wait_for_postgres.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy/bootstrap_from_tag.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy/migrate-net-to-com.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy/diagnose_502.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/deploy/setup-insightpulseai-domain.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/health/check_all.sh`**
  - Convert to n8n workflow: fetch→transform pipeline: n8n candidate
  - Signals: fetch→transform pipeline: n8n candidate
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo/company_bootstrap.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo/verify-ce-apps.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo/purge_assets.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo/install-ce-apps.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo/company_bootstrap_xmlrpc.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo/seed_org_companies_users_integrations.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo/verify-full-parity.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo/bootstrap_companies_min.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ci_gate/module_gate.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/apply-email-events-pack.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/configure_auth_smtp_and_urls.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/configure_auth_email_templates.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/verify_auth_config.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/test_email_otp_curl.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/apply_all.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/test_magic_link_curl.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/supabase/gh_actions_secrets_apply.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/codespaces/start.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/github/create_ee_replacement_issues.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/figma/verify_dev_mode_access.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/audit/assess_opportunities.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/audit/check_mailgun.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/audit/checks/check_mailgun.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/audit/checks/check_vercel.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/audit/checks/check_digitalocean.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/seeds/generate_project_stack_xlsx.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/seeds/generate_project_stack_csv.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ops/ship_v1_1_0.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ops/test_ops.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ops/install/import_finance_data.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ops/install/import_finance_directory.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ops/install/verify_finance_ppm.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ops/install/import_november_wbs.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ops/deploy/PRODUCTION_DEPLOY_WORKOS.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/ops/deploy/install_ppm_monthly_close.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/mailgun/setup_webhooks.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/mailgun/test_smtp.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/mailgun/verify_dns.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/mailgun/verify_all.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/mailgun/send_test_email.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/stack/install_stack.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/backup/restore_backup.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/import/import_activities.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/import/validate_headers.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/import/run_import_sequence.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/import/verify_import.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/dns/migrate-dns-to-do.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/dns/setup-do-domain.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/dns/verify-do-dns.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`scripts/odoo-automation/create_project_alias.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`packages/lib/bin/lib_sync_run.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`packages/lib/tests/verify_deployment.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`ipai-platform/scripts/setup-tls.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge_extra_parameters/tests/test_ai_extra_parameter.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge/__manifest__.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge/tests/test_connection.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge/tests/test_bridge.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge/models/mail_thread.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge/models/ai_bridge.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge_chatter/tests/test_chatter.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge_chatter/models/ai_bridge_execution.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge_chatter/models/mail_channel.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`_work/OCA-ai/ai_oca_bridge_chatter/models/ai_bridge.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`templates/saas-landing/scripts/verify-org-invites.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`templates/saas-landing/scripts/complete-deployment.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`templates/saas-landing/scripts/deploy-production.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`templates/saas-landing/scripts/test-local.sh`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`templates/odooops-console/scripts/next_reset_macos.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`ops/backup/install_cron.sh`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`skills/visio-drawio-export/docker/entrypoint.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`docs-assistant/deploy/deploy.sh`**
  - Convert to n8n workflow: polling sleep: scheduled n8n workflow candidate
  - Signals: polling sleep: scheduled n8n workflow candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`docs-assistant/mcp/docs_assistant.py`**
  - Convert to n8n workflow: cron/schedule reference: n8n scheduler candidate
  - Signals: cron/schedule reference: n8n scheduler candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`apps/web/platform-kit/scripts/secrets/validate_secrets.sh`**
  - Convert to n8n workflow: Slack webhook: n8n Slack node candidate
  - Signals: Slack webhook: n8n Slack node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`

- **`services/notion-sync/notion_sync/transform.py`**
  - Convert to n8n workflow: email notification: n8n email node candidate
  - Signals: email notification: n8n email node candidate
  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 1d
  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`


## Stale Reference Cleanup

- **Fix**: `README.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `GEMINI.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `AGENTS.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `CLAUDE.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `artifacts/docs_site/search/search_index.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `tools/model-repo-scanner/scripts/adopt_model_repo.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `tools/parity/run_ee_parity.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `tools/audit/verify_expected_paths.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `tools/audit/gen_prod_snapshot.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `bin/README.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `bin/finance-cli.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `notion-n8n-monthly-close/workflows/README.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `specs/docs/readme-enhancement-v2.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/docs/evidence/20260216-1754+0800/n8n-setup/IMPLEMENTATION_SUMMARY.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/config/domains.yaml` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/config/mail/mail-stack.yaml` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/config/integrations/integration_manifest.yaml` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/docs/SUPABASE_PLATFORM_REVIEW.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/docs/PHASE1_CHECKLIST.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/docs/infra/COST_OPTIMIZATION.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/docs/architecture/EMAIL_ARCHITECTURE.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/sandbox/dev/scripts/github/dispatch-enroll-repo.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/sandbox/dev/.github/workflows/governance-enroll-repo.yml` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/scripts/audit/checks/check_domain_policy.py` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/scripts/prompts/mailgun-setup-browser-agent.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/scripts/mailgun/mailgun-domain-setup.sh` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/.github/workflows/governance-enroll-repo.yml` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `web/platform-kit/.github/workflows/ci.yml` (deprecated_domain, old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `addons/test_theme_local/__manifest__.py` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `addons/ipai_finance_closing/DEPLOYMENT_COMPLETE.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `runtime/docker/docker/build-ce19.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `runtime/docker/docker/test-ce19.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `runtime/docker/docker/run-local-ce19.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `runtime/docker/docker/push-ce19.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/CLAUDE_CODE_SETUP.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/DEPRECATED_DOCS.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/ODOO_CE_DEPLOYMENT_SUMMARY.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/GO_LIVE_CHECKLIST.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/TRACEABILITY_INDEX.yaml` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/WHAT_SHIPPED.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/GO_LIVE_MANIFEST.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/TBWA_FINOPS_INVITE_EMAIL.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/GO_LIVE_MANIFEST_prod-20260109-2219.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/TBWA_FINOPS_V1_RUNBOOK.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/WHAT_DEPLOYED_prod-20260109-2219.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/WHAT_DEPLOYED.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/ODOO_19_PARITY_ANALYSIS.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/WHAT_DEPLOYED_prod-20260109-2219.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/WHAT_SHIPPED.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/WHAT_DEPLOYED.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/prod-20260109-1642/WHAT_SHIPPED.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/prod-20260109-1642/GO_LIVE_MANIFEST.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/release_tag_prod-20260106-1741.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/deploy_run_166.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/api_release_latest.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/api_workflow_run_20867798233.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/README.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/api_workflow_runs.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/api_deployments.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/api_compare.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/deploy_run_166_jobs.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/releases/DEPLOYMENT_PROOFS/prod-20260109-2219/README.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/evidence/20260215-1200/ops-rpc-exposure/IMPLEMENTATION.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/evidence/20260130-2014/PLANE_PRODUCTION_DEPLOYMENT.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/evidence/20260211-0930/superset-db-init/verification.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/evidence/20260211-branch-cleanup/CLEANUP_SUMMARY.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/evidence/20260216-1546/subdomain-routing-fix/IMPLEMENTATION_SUMMARY.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/kb/odoo19/index/sections.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/kb/odoo19/index/index.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/audits/ipai_modules/inventory.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/ee-parity-gate/EE_PARITY_GATE_REPORT.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/claude_code/IMPLEMENTATION_SUMMARY.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/claude_code/README.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/claude_code/QUICK_REFERENCE.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/cicd/README.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/integrations/N8N.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/architecture/REPO_SSOT_MAP.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/architecture/spec.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/architecture/AUTOMATIONS_SWEEP.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/knowledge/graph_seed.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/odooops-sh/RUN_LIFECYCLE.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/odooops-sh/CICD.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/odooops-sh/DATA_BOUNDARIES.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/arch/PROD_RUNTIME_SNAPSHOT.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/arch/runtime_snapshot/20260108_013846/runtime_identifiers.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/arch/runtime_snapshot/20260108_013846/container_inspects/all_containers.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/ops/TESTING.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/issues/2026-02-07-domain-health-audit.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/pages/deployment-timeline.md` (deprecated_domain, old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/agent_instructions/SSOT.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/process/governance/ODOOSH_GRADE_PARITY_GATING.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/strategy/OKR-2026-H1.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs/strategy/okr-2026-h1.json` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `sandbox/dev/out/health/dev-test.json` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `sandbox/dev/out/health/dev-test.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `sandbox/dev/spec/databricks-integration/TRAINING_GUIDELINES.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `sandbox/dev/.claude/settings.local.json` (deprecated_domain, old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `sandbox/dev/docs/evidence/20260216-1546/subdomain-routing-fix/IMPLEMENTATION_SUMMARY.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `sandbox/dev/scripts/configure-n8n-smtp.sh` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `sandbox/dev/plane/DEPLOY.md` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/verify-codespaces-auth.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deployment-checklist.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/erp_config_cli.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy_notion_tasks.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/validate_m1.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/whats_deployed.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/build_v0.9.1.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/healthcheck_odoo.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/clean-branches.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/incident_snapshot.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/verify-dns-baseline.sh` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/setup-mailgun-secrets.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/ci_smoke_test.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/image_audit.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/recreate_odoo_prod.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy_workos_prod.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy-to-server.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/setup-codespaces-secrets.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/verify-addon-permissions.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/backup_odoo.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy_theme_to_production.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/wiki_sync.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/worktree-setup.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/inventory_config_keys.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/run_odoo_shell.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/build_v0.10.0.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/setup-codespaces-pat.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/validate_repo_config.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/screenshot_production.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/diagnose_prod.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/fix_pos_enterprise_error.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/full_deploy_sanity.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/install_baseline.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/check_secrets.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy_production.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/verify-https.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/package_image_tarball.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/create-release.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/sync_current_state.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/generate_release_docs.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/bootstrap_github_issues.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/go_no_go_check.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy_prod.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy_custom_image.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/bootstrap_execution_board.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/cleanup-branches.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/smoketest.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/start_local_odoo.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/build_and_push_version.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/odoo_update_modules.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/prod/deploy_workos.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/prod/verify_workos.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/aiux/verify_prod_health.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/memory/distill_packs.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/ci/docker-image-diff.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/ci/import-n8n-workflows.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy/bootstrap_from_tag.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy/deploy-prod-e2e.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy/migrate-net-to-com.sh` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy/diagnose_502.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy/setup-insightpulseai-domain.sh` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/deploy/do-bootstrap-odoo-prod.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/odoo/verify-ce-apps.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/parity/audit_ee_parity.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/parity/create_blocker_issues.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/status/set_status.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/docs/build_llms_full.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/codespaces/bootstrap.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/github/create_ee_replacement_issues.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/audit/check_infra_waf.py` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/sandbox/start-do-sandbox.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/sandbox/start-codespace.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/ops/verify_ppm_installation.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/ops/deploy/deploy_ppm_dashboard.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/ops/deploy/deploy_ppm_dashboard_direct.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/ops/deploy/HOTFIX_OWLERROR.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/ops/deploy/PRODUCTION_DEPLOY_WORKOS.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/ops/deploy/final_verification.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `scripts/automations/sweep_repo.py` (deprecated_domain, old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `ipai-platform/scripts/setup-tls.sh` (deprecated_domain)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `.github/workflows/repo-structure-guard.yml` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `odoo19/MIGRATION_COMPLETE.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `odoo19/CANONICAL_SETUP.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `odoo19/MIGRATION_FROM_OLD_STACK.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `odoo19/QUICK_REFERENCE.md` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `ops/backup-production.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `ops/github/apply_labels.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `ops/backup/install_cron.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs-assistant/deploy/setup-database.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains

- **Fix**: `docs-assistant/deploy/deploy.sh` (old_path)
  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d
  - **Next action**: Update references to canonical paths and domains
