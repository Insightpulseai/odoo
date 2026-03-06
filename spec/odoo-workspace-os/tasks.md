# Odoo Workspace OS — Task Checklist

> Module implementation status tracking.

## Module Status

| Module | Status | Phase | Owner | Notes |
|--------|--------|-------|-------|-------|
| ipai_ppm | [ ] Not Started | 1 | TBD | Portfolio management, resource planning |
| ipai_expense_ai | [ ] Not Started | 1 | TBD | OCR + policy engine + anomaly detection |
| ipai_workspace | [ ] Not Started | 2 | TBD | Semantic search + document grounding |
| ipai_copilot | [ ] Not Started | 3 | TBD | NL interface + guided workflows |
| ipai_close_control | [ ] Not Started | 1 | TBD | Close checklist + reconciliation |

## Infrastructure Tasks

| Task | Status | Dependencies |
|------|--------|-------------|
| [ ] PaddleOCR-VL service deployment | Not Started | Docker, GPU optional |
| [ ] Embedding service for semantic search | Not Started | pgvector or Databricks |
| [ ] LLM service for copilot | Not Started | API gateway, model selection |
| [ ] Databricks gold marts for analytics | In Progress | Connector SDK bundle (deployed) |
| [ ] n8n workflows for close automation | Not Started | n8n instance (running) |

## OCA Module Evaluation

| OCA Module | Purpose | Status |
|------------|---------|--------|
| project_timeline | Gantt chart for projects | [ ] Evaluate |
| project_task_dependency | Task dependencies | [ ] Evaluate |
| hr_expense_sequence | Expense numbering | [ ] Evaluate |
| account_reconcile_oca | Reconciliation tools | [ ] Evaluate |
| document_knowledge | Knowledge base | [ ] Evaluate |

## Integration Points

| Integration | Direction | Protocol | Status |
|-------------|-----------|----------|--------|
| Odoo → Databricks | Odoo PG connector | CDC/batch | Deployed |
| Odoo → n8n | Webhook/API | REST | Active |
| Odoo → Slack | Notifications | Slack API | Active |
| PaddleOCR → Odoo | Receipt data | REST API | Not Started |
| LLM → Odoo | Copilot responses | REST API | Not Started |
