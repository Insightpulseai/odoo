# Platform Runtime State

> Version: 1.0.0
> Last updated: 2026-03-23
> Parent: `docs/runbooks/ODOO_AZURE_GENIE_GO_LIVE_CHECKLIST.md`

---

## Revised assistant runtime state

| Surface | Intended role | Current allowed role | GA blocked by |
|---------|---------------|---------------------|---------------|
| Odoo Copilot | transactional/process assistant | internal beta, read-only advisory | audit model, rate limiting, request validation, company scoping, retrieval wiring, Foundry endpoint |
| Databricks Genie | conversational analytics assistant | curated analytics beta | dataset governance, semantic acceptance, cost ownership, warehouse definition |
| Document Intelligence assistant | document extraction + review assist | human-in-the-loop beta | confidence/review rules, posting safety, evidence controls, field mapping |
| Foundry runtime | agent orchestration and serving path | partial / not fully wired | missing retrieval indexing, Search/OpenAI connections, online endpoint, gateway wiring |

---

## Surface-specific state (audited 2026-03-23)

### Odoo Copilot

| Component | State | Evidence |
|-----------|-------|----------|
| Odoo module installed | Yes | `addons/ipai/ipai_odoo_copilot/` |
| Foundry agent exists | Yes | `asst_45er4aG28tFTABadwxEhODIf` |
| System prompt | v2.1.0 (3-lane retrieval, truthfulness rules) | `agents/foundry/.../system-prompt.md` |
| Tool executor | 15 handlers (14 read-only + bounded web search) | `tool_executor.py` |
| Audit model | **Missing** | Blocker |
| Rate limiting | **Not enforced** | Blocker |
| Request validation | **Incomplete** | Blocker |
| Company scoping | **Too loose** | Blocker |
| Retrieval chain | **Unwired** (index empty, no connections) | Blocker |
| Eval corpus | 30/30 advisory, 0 retrieval | Partial |

### Databricks Genie

| Component | State | Evidence |
|-----------|-------|----------|
| Unity Catalog | Exists (`dbw_ipai_dev`) | `databricks/bundles/` |
| Gold marts | Defined (6 marts), seed data in progress | `databricks/bundles/sql_warehouse/src/sql/marts/` |
| SQL warehouse | Exists | Azure portal |
| Business definitions | **Not completed** | Blocker |
| Sample queries | **Not completed** | Blocker |
| Genie space | **Not created** | Blocker |

### Document Intelligence

| Component | State | Evidence |
|-----------|-------|----------|
| Azure resource | `docai-ipai-dev` exists | `infra/azure/` |
| Supported doc types | **Not enumerated** | Blocker |
| Review queue | **Not implemented** | Blocker |
| Field mapping | **Not defined** | Blocker |
| Confidence thresholds | **Not defined** | Blocker |

### Foundry Runtime

| Component | State | Evidence |
|-----------|-------|----------|
| Project | `data-intel-ph` exists (East US 2) | `remote-state/` |
| Agent | Exists, gpt-4.1, temp 0.4 | `remote-state/` |
| AI Search | `srch-ipai-dev` — 1 index, 331 docs; `odoo-docs` missing | `remote-state/` |
| Search connection | Connection reference exists, not wired to retrieval | `runtime-contract.md` |
| OpenAI connection | **Not created** | Blocker |
| Online endpoint | **None deployed** | Blocker |
| Gateway wiring | **Not wired** | Blocker |
| App Insights | **Not configured** | Blocker |

---

## Launch posture

**Current**: Internal beta / trusted users / read-only advisory

**Next milestone**: GROUNDED_ADVISORY_READY (per `agents/foundry/.../runtime-contract.md` §Publish Gate)

**Requirements for next milestone**:
1. Entra app roles registered and active
2. Context envelope injected in every request path
3. AI Search index populated (>= 100 chunks)
4. Retrieval injection live with security trimming
5. App Insights telemetry live and dashboard accessible

---

*Last updated: 2026-03-23*
