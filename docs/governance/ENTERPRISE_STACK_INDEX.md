# Enterprise Stack Index

## System-of-Record Matrix

| System | Role | Owned Entities | Spec Bundle |
|--------|------|---------------|-------------|
| Odoo CE 19 | ERP truth | Finance, CRM, HR, Approvals | `spec/close-orchestration/`, `spec/odoo-approval-inbox/` |
| Supabase | Control plane | Identity map, sync state, events | `spec/integration-control-plane/` |
| Databricks | Intelligence | Analytics marts, forecasts, anomalies | `spec/databricks-apps-control-room/` |
| Plane | Workspace OS | Docs, projects, coordination | `spec/odoo-workspace-os/` |
| n8n | Automation | Workflows, event routing | — |
| Azure Foundry | Agent platform | Copilot agents, tool catalog | `spec/odoo-copilot-azure/` |
| GitHub | Source control | Code, CI/CD, issues | — |

## Spec Bundle Registry

| Spec Bundle | Domain | Module | Status |
|-------------|--------|--------|--------|
| `close-orchestration` | Finance | `ipai_close_orchestration` | Spec complete |
| `bir-tax-compliance` | Finance | `ipai_finance_tax_return` | Spec complete |
| `odoo-bir-filing-control` | Finance | `ipai_finance_bir_filing` | Spec complete |
| `odoo-tne-control` | Finance | `ipai_finance_tne_control` | Spec complete |
| `odoo-ap-invoice-control` | Finance | `ipai_finance_ap_control` | Spec complete |
| `odoo-approval-inbox` | Platform | `ipai_platform_approval_inbox` | Spec complete |
| `integration-control-plane` | Platform | — (Supabase schema) | Spec complete |
| `odoo-copilot-azure` | Agent | `ipai_copilot_gateway` | Spec complete |
| `control-room-platform` | Governance | — | Spec complete |
| `odoo-workspace-os` | Platform | `ipai_workspace_core` | Spec complete |
| `azure-target-state` | Infra | — | Spec complete |
| `databricks-apps-control-room` | Analytics | — | Spec complete |
| `expense-automation` | Finance | `ipai_expense_ocr` | Spec complete |
| `ipai-copilot` | Agent | — | **Deprecated** → `odoo-copilot-azure` |

## Machine-Readable Artifacts

| Artifact | Path | Schema |
|----------|------|--------|
| Entity map | `docs/architecture/CANONICAL_ENTITY_MAP.yaml` | — |
| Repository taxonomy | `docs/governance/repository_taxonomy.yaml` | `docs/governance/repository_taxonomy.schema.json` |
| KPI contracts | `platform/data/contracts/control_room_kpis.yaml` | — |
| Event contracts | `platform/data/contracts/control_room_events.yaml` | — |
| Parity matrix | `docs/parity/PARITY_MATRIX.yaml` | — |
| EE feature gap | `docs/ENTERPRISE_FEATURE_GAP.yaml` | — |
