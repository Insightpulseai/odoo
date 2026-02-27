# Tasks — Supabase Maximization

**Spec bundle**: `spec/supabase-maximization/`
**Tracks**: `plan.md` phases

---

## Phase 1 — SSOT Docs + Policy Enforcement (This PR)

| # | Task | Files | Verify command |
|---|------|-------|----------------|
| 1.1 | Create `docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md` with feature adoption Tiers table, integration rubric, boundary diagram | CREATE | `ls docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md` → exists |
| 1.2 | Update `CLAUDE.md` Secrets Policy — replace 5-bullet block with approved stores table + Vault-first rule + "pasted once ≠ exposed" | EDIT | `grep "Vault-first" CLAUDE.md` → match |
| 1.3 | Verify `scripts/ci/check_supabase_contract.sh` has RLS coverage gate; add gate if missing | EDIT/CHECK | `grep "rls\|ROW LEVEL" scripts/ci/check_supabase_contract.sh` → match |
| 1.4 | Update `spec/odoo-receipt-digitization/plan.md` — add Supabase feature adoption table + Iceberg landing contract | EDIT | `grep "Iceberg Landing Contract" spec/odoo-receipt-digitization/plan.md` → match |
| 1.5 | Update `spec/odoo-receipt-digitization/prd.md` — add Supabase/Infrastructure acceptance criteria block | EDIT | `grep "Supabase / Infrastructure" spec/odoo-receipt-digitization/prd.md` → match |
| 1.6 | Update `spec/odoo-receipt-digitization/tasks.md` — add tasks 2.9–2.11 (ICEBERG_ registry, no-plaintext lint, datas exclusion) | EDIT | `grep "2\.9" spec/odoo-receipt-digitization/tasks.md` → match |

---

## Phase 2 — Storage + Realtime + Vault Refs (Next)

> Blocked by: Phase 1 tasks complete + T1 acceptance criteria green

| # | Task | Files | Verify command |
|---|------|-------|----------------|
| 2.1 | Create `supabase/storage/receipts/bucket.sql` — bucket + RLS policy | CREATE | `supabase storage ls` → `receipts` bucket listed |
| 2.2 | Create `supabase/storage/receipts/policies.sql` — select/insert/delete per role | CREATE | `check_supabase_contract.sh` storage RLS check passes |
| 2.3 | Update `ipai_expense_ocr`: upload OCR image to `receipts/` bucket; store URL, not binary | EDIT | `grep "store_url\|storage.from" addons/ipai/ipai_expense_ocr/` → match |
| 2.4 | Add `ssot/secrets/registry.yaml` entries: `ipai_ocr_endpoint_url`, `iceberg_access_key_id`, `iceberg_secret_access_key` | EDIT | `grep "ipai_ocr_endpoint_url" ssot/secrets/registry.yaml` → match |
| 2.5 | Update `supabase/functions/webhook-ingest/` to read OCR endpoint from Vault | EDIT | `grep "Deno.env.get('ipai_ocr" supabase/functions/` → match |
| 2.6 | Enable `ops.task_queue` Realtime in `supabase/config.toml` | EDIT | `grep "task_queue" supabase/config.toml` → match |
| 2.7 | Activate CDC pipeline: create DO App Platform worker via `supabase-etl-expense.yml` | CI | Workflow run succeeds; Iceberg snapshot advances |
| 2.8 | Integration test: Odoo INSERT → Iceberg row visible within 60s | — | `SELECT * FROM odoo_ops.expense ORDER BY id DESC LIMIT 1` returns row |

---

## Phase 3 — Vector + MCP (Later)

| # | Task | Files | Verify command |
|---|------|-------|----------------|
| 3.1 | Create migration `supabase/migrations/*_receipt_embeddings.sql` | CREATE | `\d ai.receipt_embeddings` shows `ivfflat` index |
| 3.2 | Update `supabase/functions/embed-chunk-worker/` to process OCR text | EDIT | Function deploys without error |
| 3.3 | Configure `mcp/servers/supabase/` for schema introspection + `ops.*` reads | EDIT | `mcp/servers/supabase/` server starts; schema query returns results |

---

## Phase 4 — Branching + Log Drains (Future)

| # | Task | Files | Verify command |
|---|------|-------|----------------|
| 4.1 | Add Supabase branch creation to PR workflow | `.github/workflows/` | PR workflow creates branch DB; migration tested on branch |
| 4.2 | Wire Edge Function + DB logs to observability backend | `infra/observability/supabase/` | Logs appear in observability pipeline |

---

## Commit Order (Phase 1)

```bash
git add CLAUDE.md
git commit -m "docs(secrets): expand Secrets Policy — Vault-first + approved stores"

git add docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md
git commit -m "docs(arch): add SUPABASE_FEATURES_INTEGRATIONS_ADOPTION adoption map"

git add spec/supabase-maximization/
git commit -m "feat(spec): add spec/supabase-maximization/ 4-file spec bundle"

git add spec/odoo-receipt-digitization/
git commit -m "docs(spec): upgrade receipt-digitization spec — Supabase adoption + Iceberg contract"
```
