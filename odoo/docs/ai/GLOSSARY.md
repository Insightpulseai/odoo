# Glossary

> **Purpose**: Canonical term definitions for LLM consistency.
> **Usage**: Reference before using or explaining any term.

---

## Platform Terms

### CE (Community Edition)
The open-source version of Odoo. This stack uses CE only, never Enterprise.

### OCA (Odoo Community Association)
Non-profit organization maintaining vetted community Odoo modules. OCA modules are preferred over custom development.

### IPAI (InsightPulse AI)
The custom module prefix for InsightPulse-developed Odoo modules. All custom modules use `ipai_*` naming.

### ERP
Enterprise Resource Planning. Odoo serves as the ERP core for business processes.

---

## Architecture Terms

### SSOT (Single Source of Truth)
The authoritative source for a given data type:
- **Odoo Postgres** = Business data SSOT
- **Supabase** = Knowledge/memory SSOT
- **GitHub** = Code/config SSOT

### Bridge Module
`ipai_enterprise_bridge` - The thin glue layer that provides CE+OCA parity with Odoo Enterprise features.

### Bundle
A meta-module that declares dependencies on multiple feature modules without containing business logic itself. Examples: `ipai_scout_bundle`, `ipai_ces_bundle`.

### Shadow Schema
Read-only Supabase tables that mirror Odoo data. Schema: `odoo_shadow`. Never write to shadow tables.

---

## Supabase Terms

### Project Ref
Unique identifier for a Supabase project. Current: `spdtwktxdalcfigzeqrz`.

### RLS (Row Level Security)
Postgres policies that restrict data access based on user identity and tenant.

### pgvector
Postgres extension for vector similarity search. All embeddings are 1536-dimensional.

### Edge Function
Serverless functions running at edge locations. Used for RAG queries, ingestion, and integrations.

---

## Knowledge Terms

### KB (Knowledge Base)
Supabase schema (`kb`) storing documents, chunks, and embeddings for RAG.

### KG (Knowledge Graph)
Supabase schema (`kg`) storing entity nodes, relationship edges, and evidence.

### RAG (Retrieval-Augmented Generation)
Pattern of retrieving relevant documents before LLM generation. Uses vector similarity search.

### Chunk
A segment of a document optimized for embedding and retrieval. Typical size: 500-1000 tokens.

### Embedding
A 1536-dimensional vector representation of text. Model: OpenAI `text-embedding-3-small`.

---

## Agent Terms

### MCP (Model Context Protocol)
Anthropic's protocol for connecting LLMs to external tools and data sources.

### Agent Memory
Supabase schema (`agent_mem`) storing session history and events for MCP agents.

### Skill
A registered capability that an agent can invoke. Stored in `agent_mem.skills`.

---

## Ops Terms

### Ops Advisor
Supabase schema (`ops_advisor`) for Azure Advisor-style recommendations covering cost, security, reliability.

### Harvest
Process of crawling and ingesting content into the knowledge base. Tracked in `kb.harvest_state`.

### Catalog
Hierarchical taxonomy organizing knowledge sources. Tables: `kb.catalog_sources`, `kb.catalog_nodes`.

---

## Infrastructure Terms

### DO (DigitalOcean)
Cloud provider hosting Odoo droplets and managed Postgres.

### Managed Postgres
DO-managed PostgreSQL cluster. Cluster name: `odoo-db-sgp1`.

### Droplet
DO virtual machine. Odoo prod: `odoo-erp-prod`.

---

## Module Naming Conventions

| Prefix | Domain |
|--------|--------|
| `ipai_ai_*` | AI/agents |
| `ipai_finance_*` | Finance/PPM |
| `ipai_bir_*` | BIR tax compliance |
| `ipai_expense_*` | Expense management |
| `ipai_equipment` | Equipment booking |
| `ipai_ce_*` | CE branding/cleanup |
| `ipai_workos_*` | WorkOS/Notion features |
| `ipai_platform_*` | Platform infrastructure |
| `ipai_*_bundle` | Vertical bundles |

---

## Schema Prefixes

| Prefix | Purpose |
|--------|---------|
| `kb.*` | Knowledge base |
| `kg.*` | Knowledge graph |
| `ops.*` | Operations/jobs |
| `agent_mem.*` | Agent memory |
| `docs.*` | Document RAG |
| `ops_advisor.*` | Recommendations |
| `odoo_shadow.*` | Odoo mirror |

---

## File Conventions

| Pattern | Location |
|---------|----------|
| `*.dbml` | DBML schema definitions |
| `*.mmd` | Mermaid diagrams |
| `*_CANONICAL_*` | Authoritative reference |
| `*_MODULE_*` | Module-specific |
| `DEPLOY_*.md` | Deployment runbooks |
| `VERIFY_*.md` | Verification procedures |
