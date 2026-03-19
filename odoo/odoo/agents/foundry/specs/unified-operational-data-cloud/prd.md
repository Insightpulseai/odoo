# Reverse PRD — Better Peliqan (Operaq)

## Product Name: Operaq

## Summary

All-in-one operational data cloud for business teams, analysts, and developers. One platform spanning ELT, warehouse, transforms, reverse ETL, apps, APIs, and AI — operating on one unified entity graph and one governed execution model.

## Benchmark

Peliqan: 250+ connectors, built-in/BYO warehouse, SQL + low-code Python, reverse ETL, APIs, data apps, orchestration, AI chatbot/agent features.

## Problem

All-in-one data products often become:
- Too broad to govern cleanly
- Too low-code to trust in production
- Too warehouse-centric for operational workflows
- Too app-centric for real data engineering standards

## Target Users

Mid-market ops teams, agencies managing client data stacks, fractional finance/revops teams, SaaS teams shipping internal + external data apps, analytics engineers needing lightweight app/API delivery

## Goals

1. Keep one-platform simplicity
2. Make genuinely production-grade for structured operations
3. Unify syncs, models, APIs, workflows, apps around one object model
4. AI features useful through governed semantics and permissions
5. Non-engineers operate safely without invisible low-code debt

## Non-Goals

- Full Databricks-style platform breadth
- Full enterprise app platform replacement
- Hosting arbitrary long-running custom services
- Generic notebook-first data science environment

## Product Principles

1. **One graph, not many tools** — connectors, warehouse, transforms, apps, APIs, bots all point to same entity graph
2. **Spreadsheet ease, warehouse rigor** — easy exploration that graduates to governed production
3. **Apps downstream of trusted models** — dashboards, APIs, agents sit on semantic models, not raw sync outputs
4. **AI is capability, not product island** — permissions, lineage, semantics are native
5. **Tenant isolation first-class** — multi-tenant patterns built in from day one

## Functional Requirements

- FR-1: Unified entity graph (customer, company, deal, subscription, invoice, order, campaign, employee, vendor)
- FR-2: Mode-aware modeling (raw → modeled → operational → external product)
- FR-3: Safe Python/SQL execution (scoping, dependency control, secrets isolation, test/promotion)
- FR-4: API and app publishing (internal/external APIs, embedded apps, client portals, operator workflows)
- FR-5: Object-aware reverse ETL and workflows
- FR-6: AI layer (text-to-SQL, model-aware chat, agent workflows, RAG — all permission-respecting)
- FR-7: Multi-tenant operating model (workspace isolation, customer cloud, branded access, shared templates)
- FR-8: Model-to-app lineage (source models, syncs, freshness, owners, policy, downstream consumers)

## Key Differentiators vs Peliqan

- One governed graph (not many loosely stitched tools)
- One promotion model
- One permission model
- One app/API/agent publishing contract
- One tenant-aware operating model

## IPAI Mapping

| Operaq Concept | IPAI Implementation |
|---------------|---------------------|
| Entity graph | Odoo models (SOR) + Supabase ops.* (SSOT) + Unity Catalog |
| Mode-aware modeling | Bronze → Silver → Gold → Platinum medallion |
| SQL/Python execution | Databricks notebooks + Lakeflow SDP |
| API publishing | Odoo FastAPI (OCA rest-framework) + Supabase Edge Functions |
| App publishing | Databricks Apps + web/ + ops-platform |
| Reverse ETL | n8n → Odoo/Supabase + Lakebase synced tables |
| AI layer | Foundry copilot + Azure AI Search + pgvector |
| Multi-tenant | Odoo multi-company + Supabase RLS + workspace isolation |
| Lineage | Unity Catalog lineage + ops.run_events |

## Release Thesis

If Peliqan is "an all-in-one data platform," Operaq is **an operational data cloud where syncs, models, apps, APIs, workflows, and agents all run on one governed business graph**.

## Strategic Recommendation

For IPAI:
- **Fluxrail direction** = sharper ingestion subsystem (Fivetran-parity via Lakeflow Connect + Databricks)
- **Operaq direction** = the more strategic foundation (one platform = Odoo SOR + Supabase SSOT + Databricks lakehouse + Foundry AI)

IPAI is already building Operaq without calling it that. The existing stack (Odoo + Supabase + Databricks + Foundry + n8n) is the implementation substrate.
