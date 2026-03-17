# Data authority contract

This contract defines which system is the **authoritative owner** of each entity. Only the authoritative system may create, update, or delete records for that entity. Other systems receive read-only projections or draft copies.

## Entity authority matrix

| # | Entity | Authoritative system | Replication target | Reverse ETL | Notes |
|---|--------|---------------------|-------------------|-------------|-------|
| 1 | Users (identity) | Supabase | Odoo (`res.users`) | N/A | Minimal projection: UUID, email, org, role |
| 2 | Auth sessions | Supabase | None | N/A | Session data never leaves Supabase |
| 3 | Customers / partners | Odoo | ADLS (bronze) | N/A | `res.partner` is the SSOT |
| 4 | Employees | Odoo | ADLS (bronze) | N/A | `hr.employee` is the SSOT |
| 5 | Chart of accounts | Odoo | ADLS (bronze) | N/A | `account.account` is the SSOT |
| 6 | Journal entries | Odoo | ADLS (bronze) | N/A | `account.move` -- immutable after posting |
| 7 | Invoices (non-T&E) | Odoo | ADLS (bronze) | N/A | Standard Odoo invoicing |
| 8 | Projects | Odoo | ADLS (bronze) | Forecast drafts | `project.project` is the SSOT |
| 9 | Timesheets | Odoo | ADLS (bronze) | N/A | `account.analytic.line` |
| 10 | Expense reports | SAP Concur | Odoo (draft) | N/A | Concur is T&E SSOT |
| 11 | Travel bookings | SAP Concur | Odoo (read-only) | N/A | Concur is T&E SSOT |
| 12 | T&E invoices | SAP Concur | Odoo (draft) | N/A | Concur is T&E SSOT |
| 13 | BIR filings | Odoo | ADLS (bronze) | N/A | Regulatory records |
| 14 | ML scores | ADLS (gold) | Supabase | `scoring_writeback` | Model predictions |
| 15 | Dashboard data | ADLS (gold) | Supabase | `read_model_refresh` | Pre-aggregated metrics |
| 16 | Document embeddings | Supabase (pgvector) | ADLS (gold) | N/A | Operational RAG |
| 17 | Forecasts | ADLS (gold) | Odoo (draft) | `draft_record_creation` | Requires human review |

## Hard rules

!!! danger "Data authority rules"
    1. **Single owner.** Every entity has exactly one authoritative system. No shared ownership.
    2. **No cross-writes without contract.** A system may not write to another system's owned entities unless a reverse ETL flow is classified and approved.
    3. **Posted financial records are immutable.** Never overwrite `account.move` records in posted state.
    4. **Identity stays in Supabase.** Odoo receives a minimal projection. It never writes back to `auth.users`.
    5. **Concur data is read-only in Odoo.** Odoo creates draft journal entries from Concur data but never modifies the Concur-originated records.

## Ownership transfer protocol

When an entity's authoritative system must change (rare, requires architectural review):

1. **Propose**: File a spec bundle with the transfer justification and new ownership mapping.
2. **Review**: Architecture review by at least two maintainers.
3. **Migrate**: Execute data migration with full audit trail in ADLS.
4. **Update contracts**: Modify this matrix, SSOT YAML, and all downstream consumer configurations.

!!! warning "Ownership transfer is exceptional"
    Ownership transfers indicate an architectural change. They are not routine operations. Every transfer requires a spec bundle and architecture review.
