# Ask AI Contract

**Version:** 1.0.0
**Status:** Authoritative
**Last Updated:** 2026-01-13

---

## 1. Purpose

This document defines the exact data surfaces that the Ask AI / Copilot layer is allowed to use. The AI layer is a **thin consumer** of existing APIs—it does NOT justify new backend modules or infrastructure.

---

## 2. Non-Negotiables

### 2.1 Backend Policy (Survivor Modules)

Only FOUR custom IPAI modules are allowed:

| Module | Purpose | Status |
|--------|---------|--------|
| `ipai_bir_compliance` | BIR 2307 & Alphalist/RELIEF for Philippines | ✅ KEEP |
| `ipai_finance_ppm` | Finance PPM (Notion parity) | ✅ KEEP |
| `ipai_theme_copilot` | Fluent-style TBWA theme | ✅ KEEP |
| `ipai_ask_ai_bridge` | External Copilot launcher | ✅ KEEP |

**All other IPAI modules** must be:
- Replaced with CE/OCA equivalents, OR
- Deprecated and removed

### 2.2 UI Layer

The Copilot UI lives in:
- **React + Fluent** for dashboards (Scout Dashboard, Control Room)
- **One minimal bridge module** (`ipai_ask_ai_bridge`) for Odoo backend—launcher only

### 2.3 AI Logic Location

AI prompts, business rules, and RAG logic **NEVER** live in Odoo modules. They belong in:
- External RAG service (Supabase Edge Functions)
- External AI gateway (Pulser)
- External prompt store (Spec Kit docs)

---

## 3. Allowed Data Surfaces

### 3.1 Odoo RPC Methods

The Copilot may call these Odoo XML-RPC / JSON-RPC methods:

| Model | Methods | Purpose |
|-------|---------|---------|
| `finance.task` | `search_read`, `read` | Read PPM tasks |
| `finance.bir.deadline` | `search_read`, `read` | Read BIR deadlines |
| `finance.person` | `search_read`, `read` | Read finance team members |
| `bir.schedule` | `search_read`, `read` | Read BIR schedule |
| `account.move` | `search_read`, `read` | Read invoices (for BIR 2307) |
| `project.task` | `search_read`, `read` | Read project tasks |

**Write operations are NOT allowed** through Copilot. If writes are needed, they go through well-defined controller endpoints with proper authorization.

### 3.2 Supabase Schemas (Read-Only)

| Schema | Purpose | Copilot Access |
|--------|---------|----------------|
| `finance` | Finance ops tables | ✅ Read via views |
| `projects` | PPM engagement data | ✅ Read via views |
| `rag` | Document chunks + embeddings | ✅ Read for RAG |
| `scout_gold` | Aggregated retail metrics | ✅ Read via views |
| `scout_silver` | Cleaned retail data | ⚠️ Limited read |
| `scout_bronze` | Raw retail data | ❌ No direct access |

### 3.3 Exposed API Schema: `scout_api`

The Copilot frontend should use **only these views** for dashboard data:

```sql
-- PPM Metrics View
scout_api.ppm_metrics           -- Key finance metrics
scout_api.finance_close_tasks   -- Month-end close tasks
scout_api.bir_deadlines         -- BIR deadline calendar
scout_api.task_summary          -- Task status summary

-- Retail Views (if applicable)
scout_api.store_daily           -- Store daily aggregates
scout_api.brand_performance     -- Brand performance metrics
```

### 3.4 Documentation Sources

The Copilot RAG engine should index:

| Source | Location | Purpose |
|--------|----------|---------|
| Spec Kit | `spec/*/` | Feature specs, PRDs, constitutions |
| Odoo Handbook | `docs/odoo-18-handbook/` | Technical guides |
| BIR SOPs | `docs/sops/bir/` | BIR compliance procedures |
| Finance Close | `docs/sops/finance/` | Month-end close procedures |

---

## 4. Forbidden Patterns

### 4.1 Never Do

- ❌ Create new Odoo modules for AI features
- ❌ Store AI prompts in Odoo database
- ❌ Implement RAG logic in Python models
- ❌ Add AI-specific tables to Odoo PostgreSQL
- ❌ Direct write to core business tables through AI

### 4.2 Never Depend On

- ❌ `ipai_ai_core` (deprecated)
- ❌ `ipai_ai_agents` (deprecated)
- ❌ `ipai_copilot_ui` (deprecated)
- ❌ Any `ipai_ai_*` module (deprecated)

---

## 5. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Ask AI / Copilot Layer                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│   │ React UI    │    │ Odoo Bridge │    │ RAG Service │             │
│   │ (Fluent)    │    │ (launcher)  │    │ (Supabase)  │             │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘             │
│          │                  │                  │                     │
│          ▼                  ▼                  ▼                     │
│   ┌─────────────────────────────────────────────────────┐           │
│   │              AI Gateway (Pulser / External)          │           │
│   └─────────────────────────────────────────────────────┘           │
│                              │                                       │
├──────────────────────────────┼───────────────────────────────────────┤
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────┐           │
│   │                 Data Layer (Read-Only)               │           │
│   ├─────────────────────────────────────────────────────┤           │
│   │                                                      │           │
│   │   Odoo RPC              Supabase Views               │           │
│   │   ─────────             ───────────────              │           │
│   │   • finance.task        • scout_api.ppm_metrics      │           │
│   │   • finance.bir.deadline • scout_api.bir_deadlines   │           │
│   │   • account.move        • rag.chunks                 │           │
│   │                                                      │           │
│   └─────────────────────────────────────────────────────┘           │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                        Survivor Modules (4 Total)                    │
│   ┌─────────────────────┐    ┌─────────────────────────┐            │
│   │ ipai_bir_compliance │    │ ipai_finance_ppm        │            │
│   │ (BIR 2307/Alphalist)│    │ (Finance PPM/Close)     │            │
│   └─────────────────────┘    └─────────────────────────┘            │
│   ┌─────────────────────┐    ┌─────────────────────────┐            │
│   │ ipai_theme_copilot  │    │ ipai_ask_ai_bridge      │            │
│   │ (Fluent Theme)      │    │ (External Launcher)     │            │
│   └─────────────────────┘    └─────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. API Contract

### 6.1 Copilot Query Endpoint

**Request:**
```json
POST /api/copilot/query
{
  "message": "When is BIR 1601-C due?",
  "context": {
    "odoo_db": "odoo_core",
    "odoo_uid": 2,
    "tenant_id": "uuid"
  }
}
```

**Response:**
```json
{
  "ok": true,
  "answer": "BIR 1601-C is due on the 10th of the following month...",
  "citations": [
    {"title": "BIR Schedule 2026", "url": "/docs/sops/bir/schedule.md"},
    {"title": "Finance PPM Task", "id": 123}
  ],
  "sources": ["rag.chunks", "finance.bir.deadline"]
}
```

### 6.2 Odoo Bridge Endpoint

**Request:**
```json
POST /copilot/launch
{
  "action": "open_panel"
}
```

**Response:**
```json
{
  "ok": true,
  "panel_url": "https://copilot.example.com/embed?tenant=..."
}
```

---

## 7. Implementation Checklist

### Phase 1: Cleanup
- [ ] Deprecate all `ipai_ai_*` modules
- [ ] Remove AI logic from Odoo
- [ ] Migrate prompts to Spec Kit

### Phase 2: Bridge Module
- [ ] Create `ipai_ask_ai_bridge` (launcher only)
- [ ] Add systray icon
- [ ] Add settings for external URL

### Phase 3: External RAG
- [ ] Set up Supabase Edge Function
- [ ] Index Spec Kit docs
- [ ] Index BIR SOPs

### Phase 4: Integration
- [ ] Connect React UI to RAG
- [ ] Connect Odoo bridge to external service
- [ ] Add citation linking

---

## 8. Governance

### Review Triggers
This contract must be reviewed when:
- New data sources are added
- New Odoo models are created
- RAG scope changes
- Write operations are requested

### Approval Required
Any change to this contract requires approval from:
- Platform Architecture
- Finance Ops Lead
- Security Review

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial contract definition |
