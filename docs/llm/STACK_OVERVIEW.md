# InsightPulse AI Stack Overview

> **Purpose**: LLM-friendly documentation for AI agents working with this codebase.
> **Last Updated**: 2026-01-20
> **Source of Truth**: jgtolentino/odoo-ce repository

---

## Architecture Summary

InsightPulse AI runs a **multi-layer stack** with clear boundaries:

| Layer | Technology | Role |
|-------|------------|------|
| **ERP Core** | Odoo 18 CE + OCA | Business logic, accounting, HR, projects |
| **Memory Hub** | Supabase (Postgres + pgvector) | Knowledge graph, RAG, agent memory |
| **Analytics** | Superset | Dashboards, BI, reporting |
| **Orchestration** | n8n + MCP | Workflow automation, agent coordination |
| **Frontends** | Vercel (Next.js) | Web UIs for shelf.nu, scout, dashboards |
| **Infrastructure** | DigitalOcean + Docker | Hosting, containers, managed Postgres |

---

## Single Source of Truth (SSOT) Rules

**Critical**: These are non-negotiable boundaries.

1. **Odoo Postgres** = Business data SSOT (invoices, partners, journals, projects)
2. **Supabase** = Knowledge + Memory SSOT (KB, embeddings, agent runs, infra graph)
3. **GitHub (odoo-ce)** = Code + Config SSOT (modules, migrations, specs, docs)

**Never**:
- Write business data directly to Supabase (mirror only)
- Store secrets in code (use Vault or env)
- Modify Odoo schema outside of modules

---

## Key Identifiers

| System | Identifier | Current Value |
|--------|-----------|---------------|
| Supabase Project | `project_ref` | `spdtwktxdalcfigzeqrz` |
| GitHub Repo | `repo` | `jgtolentino/odoo-ce` |
| Odoo Database | `db_name` | `odoo_core` (prod), `odoo_dev` (dev) |
| DO Droplet | `droplet_name` | `odoo-erp-prod` |
| DO Managed DB | `cluster_name` | `odoo-db-sgp1` |

---

## Canonical Modules

Only these three modules define the platform surface:

| Module | Role |
|--------|------|
| `ipai_enterprise_bridge` | Thin glue layer: config, approvals, AI/infra integration |
| `ipai_scout_bundle` | Retail vertical: POS, inventory, sales analytics |
| `ipai_ces_bundle` | Creative services vertical: projects, timesheets |

All other `ipai_*` modules are feature modules that must be explicitly referenced by a bundle.

---

## Supabase Schemas

| Schema | Purpose | API Exposed |
|--------|---------|-------------|
| `public` | Generic tables, app data | Yes |
| `kb` | Knowledge base: documents, chunks, embeddings | Yes (RLS) |
| `kg` | Knowledge graph: nodes, edges, evidence | Yes (RLS) |
| `ops` | Jobs, runs, observability | Yes (RLS) |
| `agent_mem` | Agent memory: sessions, events, skills | Yes (RLS) |
| `docs` | RAG document storage | Yes (RLS) |
| `odoo_shadow` | Odoo mirror (read-only) | Internal only |

---

## How LLMs Should Use This Stack

### Querying Knowledge
```sql
-- Find documents about a topic
SELECT * FROM kb.artifacts
WHERE title ILIKE '%finance ppm%'
ORDER BY updated_at DESC LIMIT 10;

-- Semantic search
SELECT * FROM kg.semantic_search('month-end close process', 10);
```

### Finding Infrastructure
```sql
-- Get infrastructure nodes
SELECT * FROM kg.nodes WHERE kind = 'odoo_module';

-- Get relationships
SELECT * FROM kg.neighborhood('<node_id>', 2);
```

### Agent Memory
```sql
-- Recent agent sessions
SELECT * FROM agent_mem.sessions
ORDER BY created_at DESC LIMIT 5;
```

---

## Caveats for LLMs

1. **Odoo shadow tables are READ-ONLY** - never attempt writes
2. **RLS is enforced** - queries must include proper auth context
3. **Embeddings are 1536-dim** - OpenAI text-embedding-3-small compatible
4. **Tenant isolation** - always filter by `tenant_id` where applicable
5. **No destructive operations** - ask human before DELETE/DROP

---

## Related Documents

- [STACK_RELATIONSHIPS.md](./STACK_RELATIONSHIPS.md) - Entity relationships
- [SUPABASE_STACK.md](./SUPABASE_STACK.md) - Supabase details
- [ODOO_PLATFORM.md](./ODOO_PLATFORM.md) - Odoo module architecture
- [GLOSSARY.md](./GLOSSARY.md) - Term definitions
- [LLM_QUERY_PLAYBOOK.md](./LLM_QUERY_PLAYBOOK.md) - Query recipes
