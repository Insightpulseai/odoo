# Data Authority Model: Odoo vs. Supabase

## Canonical Statement

**Odoo is the System of Record for transactional and regulated business data. Supabase is the Single Source of Truth for the platform control plane, integrations, evidence/audit, analytics serving layer, and AI indexes. Odoo data is mirrored one-way into Supabase for read, product, and intelligence use cases; Supabase replicas are non-authoritative for transactions.**

## Authority Matrix

| Domain            | Authority (Write) | Role                   | Examples                                |
| :---------------- | :---------------- | :--------------------- | :-------------------------------------- |
| **Financials**    | **Odoo**          | System of Record       | Invoices, Payments, Journal Entries     |
| **Operations**    | **Odoo**          | System of Record       | Stock Moves, Manufacturing Orders       |
| **Master Data**   | **Odoo**          | System of Record       | Partners, Products, Users               |
| **Control Plane** | **Supabase**      | Single Source of Truth | Deployment Status, Logs, Artifacts      |
| **AI / RAG**      | **Supabase**      | Single Source of Truth | Embeddings, Vector Stores, Chat History |
| **Analytics**     | **Supabase**      | Single Source of Truth | Aggregated metrics, Dashboards          |
| **Integrations**  | **Supabase**      | Single Source of Truth | Webhook logs, Sync cursors              |

## Mirroring Policy

1.  **Direction:** **One-way** from Odoo to Supabase.
2.  **Mechanism:** Push-based (Odoo triggers) or Pull-based (CDC), mapping to "Reflected" tables.
3.  **Mutability:** Supabase reflection tables are **Read-only** for application logic.
4.  **No Dual-Write:** Supabase MUST NOT be used to edit Odoo entities directly. All writes must go through the Odoo API.

## Governance Guardrails

- **Read-only by Policy:** Supabase Row Level Security (RLS) policies enforce non-mutability on reflected tables.
- **Explicit Write-back:** Any data flowing back to Odoo (e.g., an AI summary of a ticket) must ideally use an explicit Odoo API call, not a database sync.
- **Deterministic Keys:** Mirrored entities use `external_id` or stable UUIDs to maintain identity across systems.
