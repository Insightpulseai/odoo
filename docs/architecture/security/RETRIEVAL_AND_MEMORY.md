# Retrieval and Memory Policy

> How each assistant surface retrieves context and manages conversational state.
> SSOT: `ssot/agents/assistant_surfaces.yaml`

---

## Retrieval Lanes (Per Surface)

### Odoo Copilot

| Lane | Source | Scope |
|------|--------|-------|
| Lane 1 | Odoo runtime context | Active record, company, user role, locale |
| Lane 2 | Curated Odoo docs KB | `odoo-docs-kb` Azure AI Search index (vector + keyword) |
| Lane 3 | Bounded web fallback | Allowed domains only (`odoo.com`), max 3 per query |

### Diva Copilot

| Lane | Source | Scope |
|------|--------|-------|
| Lane 1 | Mode-specific KB segments | Per-mode knowledge base (strategy, odoo, tax_guru, capability, governance) |
| Lane 2 | SSOT artifacts | Goal state, OKRs, governance policies |
| Lane 3 | Skill-assembled context | Skill outputs from the active mode's skill pack |

### Studio Copilot

| Lane | Source | Scope |
|------|--------|-------|
| Lane 1 | Workspace context | Active project, brand presets, asset library |
| Lane 2 | Provider capabilities | Available models/tools from the provider broker |
| Lane 3 | Campaign/brief context | Client brief, style guide, platform requirements |

### Genie

| Lane | Source | Scope |
|------|--------|-------|
| Lane 1 | Semantic layer | Databricks SQL Warehouse via governed views |
| Lane 2 | Query provenance | Citation of data sources, filters, aggregations |
| Lane 3 | Dashboard context | Active Power BI / Superset dashboard state |

### Document Intelligence

| Lane | Source | Scope |
|------|--------|-------|
| Lane 1 | Document content | Extracted pages, fields, tables from Azure Document Intelligence |
| Lane 2 | Schema mapping | Target Odoo model fields for structured extraction |
| Lane 3 | Confidence annotations | Per-field confidence scores for human review |

---

## Memory Policy

### Conversational State

| Rule | Implementation |
|------|---------------|
| Session state is external | Stored in `ipai.copilot.conversation` / `ipai.copilot.message` (Odoo models) |
| No in-memory session affinity | Stateless containers — state rehydrated from DB per request |
| Per-user, per-company scoped | Conversation access checked against user + company |
| Retention | Configurable per surface — default 90 days |

### Long-Term Memory

| Type | Storage | Access |
|------|---------|--------|
| Conversation history | Odoo DB (`ipai.copilot.conversation`) | Per-user, per-company |
| Audit trail | Odoo DB (`ipai.copilot.audit`) | Append-only, admin access |
| KB index | Azure AI Search | Per-surface index |
| Analytics state | Databricks lakehouse | Governed via Unity Catalog |

### What Is NOT Stored

- Raw provider API responses (only summaries/extractions)
- User credentials or tokens
- Cross-tenant context
- Provider-side conversation state (we do not rely on provider memory)

---

## Grounding Rules

1. Every response must cite its retrieval lane(s)
2. If no relevant context is found, say so — do not hallucinate
3. Web fallback (Lane 3) is bounded: allowed domains only, max uses per query
4. KB segments are versioned and auditable
5. Groundedness score is a deployment gate (see `AGENTOPS_DOCTRINE.md`)

---

## SSOT References

- Assistant surfaces: `ssot/agents/assistant_surfaces.yaml`
- Diva KB segments: `ssot/agents/diva_copilot.yaml#kb_segments`
- AI runtime authority: `docs/architecture/AI_RUNTIME_AUTHORITY.md`

---

*Last updated: 2026-03-24*
