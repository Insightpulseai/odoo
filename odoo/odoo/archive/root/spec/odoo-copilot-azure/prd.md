# Odoo Copilot on Azure — Product Requirements Document

## Problem

Users must navigate multiple systems and screens to complete Odoo-centered work. Common tasks such as approvals, expense handling, close monitoring, customer/account lookup, and document-grounded Q&A are fragmented across ERP screens, docs, and analytics. This creates context-switching overhead, delays in approval turnaround, and missed insights from analytics that never surface in the workflow.

## Product Vision

Deliver an Azure-native Odoo Copilot that exposes governed business capabilities through conversational interfaces, Microsoft 365 Copilot/Teams publication paths, web/API surfaces, and agent-to-agent integrations.

## Users

| Persona | Description | Key Actions |
|---------|-------------|-------------|
| **Finance Approver** | Reviews and approves expenses, invoices, close tasks | Approve/reject, view pending queue, delegate |
| **ERP Operator** | Day-to-day Odoo user across modules | Create records, lookup status, navigate to records |
| **Project/Ops Manager** | Oversees delivery, close, and operational workflows | Monitor blockers, view dashboards, reassign tasks |
| **Compliance/Tax Reviewer** | Validates BIR filings, tax computations | Review filing status, check compliance gates |
| **Executive/Business Lead** | Needs high-level summaries and exception alerts | Ask questions, view KPIs, drill into anomalies |
| **Developer/Admin** | Configures tools, manages agent policies | Register tools, manage permissions, view telemetry |

## Goals

| ID | Goal | Success Metric |
|----|------|----------------|
| G1 | Provide transactional Odoo actions through explicit approved tools | Tool success rate > 95% |
| G2 | Provide navigational assistance with deep links into Odoo, Plane, and related systems | Navigation hop reduction > 50% |
| G3 | Provide informational answers grounded in Odoo records, documents, workspace knowledge, and summarized analytics | Grounding/citation coverage > 80% |
| G4 | Use Microsoft Foundry and MCP as the standard agent/tool platform | 100% of tools registered in Foundry catalog |
| G5 | Preserve system-of-record boundaries across Odoo, Supabase, Databricks, and Plane | Zero SoR violations in audit |
| G6 | Publishable architecture for Microsoft 365 Copilot / Teams without replatforming core logic | Publication path validated end-to-end |

## Non-Goals

- Replace Odoo UI wholesale
- Move ERP truth into Foundry
- Duplicate Databricks marts into Odoo or Supabase
- Build ad-hoc tool calls with no contract or approval model

## Capability Classes

### Transactional

Actions that create, modify, or approve records in source systems.

| Capability | Target System | Tool Contract |
|-----------|---------------|---------------|
| Create expense report | Odoo (`hr.expense.sheet`) | `tool-odoo/expense/create` |
| Approve/reject expense | Odoo (`hr.expense.sheet`) | `tool-odoo/expense/approve` |
| Create lead/opportunity | Odoo (`crm.lead`) | `tool-odoo/crm/create-lead` |
| Prepare close task worklist | Odoo (`project.task`) | `tool-odoo/close/prepare-worklist` |
| Trigger compliance review | Odoo (`ipai.approval.item`) | `tool-odoo/compliance/trigger-review` |
| Create follow-up task/activity | Odoo (`mail.activity`) | `tool-odoo/activity/create` |

### Navigational

Actions that deep-link users to specific records, views, or dashboards.

| Capability | Target System | Tool Contract |
|-----------|---------------|---------------|
| Open blocked invoice | Odoo | `tool-odoo/navigate/invoice` |
| Open customer with overdue balance | Odoo | `tool-odoo/navigate/partner` |
| Show month-end close blockers | Odoo | `tool-odoo/close/blockers` |
| Navigate to Plane workspace page | Plane | `tool-plane/navigate/page` |
| Open knowledge article | Plane | `tool-plane/navigate/article` |

### Informational

Queries that retrieve, summarize, or explain data from grounded sources.

| Capability | Source Systems | Tool Contract |
|-----------|---------------|---------------|
| Summarize account status | Odoo + Databricks | `tool-odoo/account/summary` |
| Summarize project exceptions | Odoo + Databricks | `tool-databricks/project/exceptions` |
| Answer policy questions | Plane docs | `tool-plane/knowledge/query` |
| Explain workflow blocker | Odoo + Supabase | `tool-odoo/workflow/explain-blocker` |
| Show approval turnaround metrics | Databricks | `tool-databricks/approvals/metrics` |

## System Architecture

```
                  ┌─────────────────────────────────┐
                  │     Microsoft Foundry            │
                  │  ┌─────────────────────────────┐ │
                  │  │  Foundry Agents Service      │ │
                  │  │  ┌─────────────────────────┐ │ │
                  │  │  │   Agent Framework        │ │ │
                  │  │  │   - Agents               │ │ │
                  │  │  │   - Workflows            │ │ │
                  │  │  │   - MCP Client           │ │ │
                  │  │  │   - Session State        │ │ │
                  │  │  │   - Structured Output    │ │ │
                  │  │  │   - RAG/Context          │ │ │
                  │  │  │   - Observability        │ │ │
                  │  │  └────────┬────────────────┘ │ │
                  │  │           │ MCP              │ │
                  │  │  ┌───────┼────────────────┐  │ │
                  │  │  │ Tool Catalog           │  │ │
                  │  │  │ ┌──────┬──────┬──────┐ │  │ │
                  │  │  │ │Odoo  │Supa  │D.brix│ │  │ │
                  │  │  │ │Tools │Tools │Tools │ │  │ │
                  │  │  │ └──┬───┴──┬───┴──┬───┘ │  │ │
                  │  │  └────┼─────┼──────┼─────┘  │ │
                  │  └───────┼─────┼──────┼────────┘ │
                  └──────────┼─────┼──────┼──────────┘
                             │     │      │
              ┌──────────────┘     │      └──────────────┐
              ▼                    ▼                      ▼
     ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
     │  Odoo CE 19    │  │   Supabase     │  │  Databricks    │
     │  (ERP truth)   │  │ (Control Plane)│  │ (Intelligence) │
     │                │  │                │  │                │
     │ ipai_copilot_* │  │ ctrl.*         │  │ gold.*         │
     │ (thin modules) │  │ identity_map   │  │ marts          │
     └────────────────┘  │ sync_state     │  │ forecasts      │
              ▲          └────────────────┘  └────────────────┘
              │
     ┌────────────────┐
     │     Plane       │
     │  (Workspace)    │
     │  docs, SOPs     │
     └────────────────┘
```

## Publication Channels

| Channel | Priority | Description |
|---------|----------|-------------|
| Foundry (direct) | P0 | Primary agent surface |
| Web shell | P1 | Optional custom web UI |
| Microsoft 365 Copilot | P2 | Enterprise copilot integration |
| Teams | P2 | Chat-based access |
| API (external) | P3 | Programmatic access via API Management |

## Success Metrics

| Metric | Target |
|--------|--------|
| Task completion time reduction | > 40% for covered workflows |
| Approval turnaround improvement | > 30% reduction in P50 |
| Navigation hop reduction | > 50% fewer screens visited |
| Answer grounding rate | > 80% with citations |
| Tool success rate | > 95% |
| Policy-compliant action rate | 100% |

## External SSOT Dependencies

| Artifact | Path | Purpose |
|----------|------|---------|
| Target State | `ssot/azure/target-state.yaml` | Canonical platform capability matrix |
| Service Matrix | `ssot/azure/service-matrix.yaml` | Machine-readable service inventory |
| DNS Migration | `ssot/azure/dns-migration-plan.yaml` | DNS record state machine |
| Service Mapping | `docs/diagrams/mappings/azure_to_do_supabase_odoo.yaml` | Azure→DO/Supabase equivalents |

## Cross-References

- `spec/odoo-approval-inbox/` — unified approval queue (approval tools)
- `spec/odoo-tne-control/` — expense/travel lifecycle (expense tools)
- `spec/close-orchestration/` — month-end close (close tools)
- `spec/odoo-bir-filing-control/` — BIR compliance (compliance tools)
- `spec/integration-control-plane/` — Supabase ctrl.* schema
- `docs/architecture/CANONICAL_ENTITY_MAP.yaml` — entity ownership
- `spec/azure-target-state/` — Azure infrastructure baseline
