# DB Table Classification (Draft)

Status: **DRAFT** — map legacy public tables to domain schemas and suggest actions (keep/move/view/alias).

---

## Legend

- **action**: `keep` | `move` | `alias` | `deprecate`
- **domain**: canonical schema for table

---

## Expense & T&E (Priority)

| Current Location | Target | Action | Notes |
|------------------|--------|--------|-------|
| `public.expense_reports` | `expense.expense_reports` | move | Create compatibility view |
| `public.expenses` | `expense.expenses` | move | |
| `public.cash_advances` | `expense.cash_advances` | move | |
| `public.expense_receipts` | `expense.expense_receipts` | move | |
| `public.expense_categories` | `expense.expense_categories` | move | |
| `expense.*` tables | — | keep | Treat as canonical |

---

## Projects / PPM

| Current Location | Target | Action | Notes |
|------------------|--------|--------|-------|
| `public.projects` | `projects.projects` | move/alias | |
| `public.project_budget_templates` | `projects.project_budget_templates` | move | |
| `public.project_budget_lines` | `projects.project_budget_lines` | move | |

---

## Rates & Vendors

| Current Location | Target | Action | Notes |
|------------------|--------|--------|-------|
| `public.vendor_profile` | `rates.*` | move | |
| `public.vendor_rate_card` | `rates.*` | move | |
| `public.rate_card_items` | `rates.*` | move | |
| `public.vendors` | `rates` or `vendors` | move | Separate vendors schema possible |
| `public.consultants` | `rates.*` | move | |
| `rates.*` | — | keep | Canonical |

---

## Finance / BIR

| Current Location | Target | Action | Notes |
|------------------|--------|--------|-------|
| `public.bir_*` | `finance.*` | move/alias | |
| `public.finance_closing_snapshots` | `finance.*` | move/alias | |
| `finance.*` | — | keep | Canonical |

---

## AI / RAG / Agents

- `gold.`, `platinum.`, `mcp.`, `ai.` are canonical for embeddings, docs, agents.
- `public.odoo_knowledge`, `bir_documents`, `bir_chunks`: move/alias into `gold`/`mcp` as appropriate.

---

## Other

| Schema | Status |
|--------|--------|
| `core.company`, `core.app_user` | keep (cross-cutting) |
| `auth` | keep (system schema) |
| `storage`, `supabase_functions`, `realtime` | infra |

---

## Next Steps

1. Finalize mapping tables per Odoo app in `DB_ODOO_MAPPING.md`
2. Validate first-wave moves (Expense + Projects + Rates + Finance)
3. Use migration template produced for `public.expense_reports` as reference
