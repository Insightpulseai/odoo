# Knowledge Graph — Constitution

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-01-09

---

## 1. Purpose

The Knowledge Graph (KG) is the **unified organizational memory layer** that connects:
- **Infrastructure** (DigitalOcean droplets, domains, DNS records, services)
- **Code** (GitHub repos, branches, PRs, issues, workflows, Odoo modules)
- **Knowledge** (docs, decisions, chat threads, specs, READMEs)

It treats **everything as nodes and edges** — queryable via graph traversal, full-text search, and vector similarity (RAG).

---

## 2. Governing Principles

### 2.1 Graph-First Data Model

All organizational entities are modeled as:
- **Nodes**: typed entities with stable keys (e.g., `Repo:org/name`, `Droplet:do:123`)
- **Edges**: typed relationships with optional weights (e.g., `DEPENDS_ON`, `DEPLOYS_TO`)
- **Docs**: content blocks with FTS + embeddings linked via mentions

### 2.2 Supabase-Native

The KG runs entirely within Supabase:
- PostgreSQL tables for graph storage
- pgvector for embeddings
- Full-text search via tsvector
- Edge Functions for ingestion
- RLS for tenant isolation

### 2.3 Eventually Consistent

Ingestion pipelines sync from truth sources (GitHub, DigitalOcean, Odoo) with:
- Webhook-driven real-time updates
- Nightly backfill reconciliation
- Entity resolution via stable keys

### 2.4 RAG-Ready

All documents are indexed for retrieval:
- Hybrid search (FTS + vector)
- Mention extraction links docs to nodes
- Neighborhood expansion provides context

---

## 3. Node Type Registry

| Category | Node Types | Key Pattern |
|----------|-----------|-------------|
| **Organization** | `Org`, `Team` | `org:<name>`, `team:<org>/<name>` |
| **Code** | `Repo`, `Branch`, `PR`, `Issue`, `Workflow`, `Run` | `repo:<org>/<name>`, `pr:<org>/<repo>#<num>` |
| **Infrastructure** | `Service`, `Host`, `Domain`, `DNSRecord` | `droplet:<id>`, `domain:<fqdn>` |
| **Odoo** | `OdooModule`, `OdooModel`, `OdooView`, `OCARepo`, `OCAModule` | `odoo:module:<name>`, `odoo:model:<name>` |
| **Knowledge** | `Doc`, `Decision`, `ChatThread` | `doc:<source>:<ref>`, `adr:<slug>` |

---

## 4. Edge Type Registry

| Edge Type | Source → Target | Purpose |
|-----------|-----------------|---------|
| `OWNS` | Org → Repo | Ownership relationship |
| `DEPLOYS_TO` | Repo → Service/Host | Deployment mapping |
| `DEPENDS_ON` | Module → Module | Dependency graph |
| `IMPLEMENTS` | PR → Issue | Work tracking |
| `REFERENCES` | Doc → Repo/Module | Documentation links |
| `RESOLVES` | Issue → Incident | Incident management |
| `CONFIGURES` | DNSRecord → Service/Host | DNS mapping |
| `MENTIONS` | Doc/ChatThread → AnyNode | Knowledge linking (scored) |

---

## 5. Architecture Boundaries

### 5.1 KG Core (This System)

- Node/edge/doc storage
- FTS + vector indexing
- Mention extraction
- Query API (hybrid search + graph traversal)

### 5.2 Ingestion Sources (External)

- **GitHub**: Repos, PRs, issues, workflows via webhooks + GraphQL
- **DigitalOcean**: Droplets, domains, apps via API sync
- **Odoo**: Modules, models, views via XML-RPC/DB export
- **Docs**: READMEs, specs, ADRs via file system

### 5.3 Integration Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE GRAPH                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │  kg_nodes   │  │  kg_edges   │  │   kg_docs   │  │ kg_mentions│  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │
│         │               │               │                │          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    QUERY LAYER (RAG)                         │    │
│  │         FTS + Vector + Graph Traversal                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │                    │                    │
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │  GitHub  │        │    DO    │        │   Odoo   │
   │ Webhooks │        │   Sync   │        │ Exporter │
   └──────────┘        └──────────┘        └──────────┘
```

---

## 6. Governance

### 6.1 Change Control

- Schema changes require migrations in `db/migrations/`
- Node/edge type additions require constitution update
- Breaking changes require RFC + approval

### 6.2 Key Normalization

All node keys must be:
- **Stable**: Same entity always gets same key
- **Unique**: No collisions across types
- **Human-readable**: Debuggable without lookups

### 6.3 Retention

| Data Type | Retention | Reason |
|-----------|-----------|--------|
| Nodes | Indefinite | Historical graph |
| Edges | Indefinite | Relationship history |
| Docs | 7 years | Regulatory compliance |
| Mentions | Follow doc | Linked lifecycle |

---

## 7. Security & Access

### 7.1 Data Classification

- **Public**: Node types, edge types, schema
- **Internal**: Node metadata, edge weights
- **Confidential**: Doc content, embeddings
- **Restricted**: Credentials (never stored)

### 7.2 Access Control

- RLS policies enforce tenant isolation
- Service role for cross-tenant operations
- API keys for external ingestion

---

## 8. Non-Goals

This system does NOT:
- Replace Odoo's native data model
- Provide real-time streaming (batch/webhook only)
- Store application secrets
- Implement full graph database features (use Neo4j if needed)

---

## 9. Success Metrics

| Metric | Target |
|--------|--------|
| Node coverage (repos) | 100% of org repos |
| Node coverage (droplets) | 100% of DO resources |
| Node coverage (modules) | 100% of ipai_* modules |
| Query latency (hybrid) | < 200ms p95 |
| Doc freshness | < 1 hour lag |
| Mention extraction accuracy | > 90% |

---

## Appendix A: Related Documents

- `prd.md` — Product Requirements
- `plan.md` — Implementation Roadmap
- `tasks.md` — Actionable Work Items

## Appendix B: Schema Location

- Supabase migration: `db/migrations/20260109_KG.sql`
- Target project: `spdtwktxdalcfigzeqrz`
