# Plan — Fabric + Power BI Serving Layer

> Phased implementation plan for the canonical analytics workload-allocation policy.

---

## Workstreams

### WS-1: Workload Classification

Produce the canonical workload-allocation table mapping every analytics
workload class to its target surface.

| Deliverable | Location | Owner |
|-------------|----------|-------|
| Workload allocation table | `docs/architecture/ANALYTICS_TARGET_STATE.md` | Platform architect |
| Decision rules DR-1 through DR-6 | Same file | Platform architect |
| Non-goals / prohibited-patterns table | Same file | Platform architect |

### WS-2: Serving-Model Standardization

Define the boundary between Fabric Data Warehouse and Lakehouse SQL
analytics endpoint.

| Decision | Fabric Data Warehouse | Lakehouse SQL Analytics Endpoint |
|----------|----------------------|----------------------------------|
| Write model | Full T-SQL DML (INSERT, UPDATE, DELETE, MERGE) | Read-only (views, functions, security only) |
| Schema style | Star/snowflake with referential integrity | Delta-backed; schema-on-read or schema-on-write from Spark |
| ACID scope | Multi-table transactions | Single-table Delta ACID (inherited from Spark writer) |
| Primary consumer | Power BI DirectQuery, T-SQL BI tools | Analysts, notebooks, ad-hoc SQL tools |
| Data origin | Loaded from Databricks Gold via pipeline or shortcut | Shortcutted or mirrored Delta tables from OneLake |

### WS-3: Semantic and Reporting Standardization

| Rule | Detail |
|------|--------|
| One semantic model per domain | `finance`, `projects`, `compliance`, `platform` — no duplicates |
| Authoring tool | Power BI Desktop only (`.pbip` committed to repo) |
| Publishing target | Power BI Service workspace per environment (`dev`, `staging`, `prod`) |
| Refresh | Scheduled refresh or Direct Lake — never manual import |
| RLS | Enforced in Service; role definitions in `.pbip` source |
| Distribution | Power BI apps; no share-by-link for governed datasets |

### WS-4: Governance

| Control | Mechanism |
|---------|-----------|
| Connection allow-list | Power BI gateway/connection policy: Databricks SQL, Fabric Warehouse, Lakehouse endpoint only |
| Semantic model review | PR review on `.pbip` changes in `data-intelligence/powerbi/` |
| Fabric Warehouse provisioning | Gated by architecture review; no self-service creation |
| Mirroring activation | Requires `ANALYTICS_TARGET_STATE.md` entry before enabling |

### WS-5: Delivery Model

| Phase | Scope | Gate |
|-------|-------|------|
| Phase A | Architecture codification (docs + spec) | Merge of this spec bundle |
| Phase B | Fabric workspace provisioning + first Warehouse mart | Databricks Gold tables serving ≥ 1 domain |
| Phase C | Power BI Desktop semantic model + Service publish | `.pbip` in repo, refresh running, RLS verified |
| Phase D | Governed consumption rollout | App published, alerts configured, stakeholder access |

---

## Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|-----------|
| R-1 | Fabric capacity cost exceeds budget | Medium | High | Start with dev workspace only; defer prod until cost model validated |
| R-2 | Power BI free tier limits block Service features | High | Medium | Upgrade to Pro when first semantic model is ready for distribution |
| R-3 | Teams bypass policy and connect Power BI to Odoo PG | Medium | High | Enforce via gateway allow-list; CI check on `.pbip` connection strings |
| R-4 | Semantic model proliferation across workspaces | Low | Medium | One-model-per-domain rule + PR review on `.pbip` |
| R-5 | Fabric Mirroring latency exceeds SLA for BI refresh | Low | Medium | Monitor mirroring lag; fall back to Databricks SQL if > 15 min |
| R-6 | Databricks SQL Warehouse idle cost during low usage | Medium | Low | Auto-stop after 10 min; serverless warehouse when available |

---

## Dependencies

| Dependency | Status | Blocker? |
|------------|--------|----------|
| Databricks Gold tables populated | Active — data flowing | No |
| Databricks SQL Warehouse running | Active — `e7d89eabce4c330c` | No |
| Fabric workspace provisioned | Not yet | Yes for Phase B |
| Power BI Pro or Premium license | Free tier only | Yes for Phase C (RLS, apps) |
| Fabric Mirroring activated | Ready (WAL=logical) | Yes for Lakehouse endpoint use |
| `.pbip` repo structure created | Not yet | Yes for Phase C |

---

*Last updated: 2026-03-21*
