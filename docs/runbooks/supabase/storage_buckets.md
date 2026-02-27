# Runbook: Supabase Storage Bucket Security

**Migration:** `supabase/migrations/20260227215348_storage_bucket_hardening.sql`
**Last updated:** 2026-02-27

---

## Bucket inventory

| Bucket ID | Visibility | Purpose | Key prefix pattern |
|---|---|---|---|
| `receipt-images` | **Private** | Raw receipt image uploads from employees | `<company_id>/<user_id>/<yyyy>/<mm>/<expense_id>/<sha256>.<ext>` |
| `attachments` | **Private** | Liquidation PDFs + OCR JSON (service-role writes) | `<company_id>/liquidations/<liq_id>/LIQ-YYYY-####.pdf` |
| `superset-bundles` | **Private** | Finance BI bundles — service-role only | `<bundle_name>/<version>/...` |
| `make-96d82b2c-receipts` | **Private** | Legacy (Make.com artifact) — no new writes | N/A |
| `data-import` | **Private** | CSV/XLSX import files — admin/service only | `<company_id>/<date>/<filename>` |
| `echarts-themes` | **Public read** | Chart theme JS/YAML — public read, admin write | `<theme-name>/<version>/...` |

---

## Key naming convention (SSOT)

All object paths follow: `<bucket>/<company_id>/<...>/<sha256_or_id>.<ext>`

This allows prefix-match RLS policies and avoids path enumeration attacks.

### Specific patterns

```
# Employee receipt upload
receipt-images/<company_id>/<user_id>/<yyyy>/<mm>/<expense_id>/<sha256>.<ext>

# Liquidation PDF (service-role write)
attachments/<company_id>/liquidations/<liquidation_id>/LIQ-2026-0042.pdf

# OCR JSON output (service-role write)
attachments/<company_id>/ocr/<expense_id>/<sha256>.json
```

---

## Access policy matrix

| Bucket | anon | employee (own) | finance (company) | service_role | admin |
|---|---|---|---|---|---|
| `receipt-images` | ❌ | ✅ read+write | ✅ read | ✅ all | ✅ all |
| `attachments` | ❌ | ❌ | ✅ read | ✅ all | ✅ all |
| `superset-bundles` | ❌ | ❌ | ✅ read | ✅ all | ✅ all |
| `echarts-themes` | ✅ read | ✅ read | ✅ read | ✅ all | ✅ all |
| `data-import` | ❌ | ❌ | ❌ | ✅ all | ✅ read |

---

## Auth model dependency

Policies join to `public.profiles(user_id, role, company_id)`.

Roles used:
- `employee` — basic upload + own read
- `manager` — read team data
- `finance` — read company-wide finance data
- `admin` — read all + config
- `service_role` — unrestricted (used by OCR pipeline, cron, n8n)

---

## Incident response

### Unauthorized access to private bucket
1. Immediately audit: `SELECT * FROM storage.objects WHERE bucket_id = '<bucket>';` with anon key — should return 0.
2. Check `storage.objects` for unexpected uploads.
3. If data was exposed: rotate affected keys, notify data owner.
4. Run migration again to re-apply policies.

### Employee can read another user's receipts
1. Check the `(storage.foldername(name))[2]` index — adjust if prefix depth changed.
2. Verify `public.profiles` has correct `user_id` for the affected user.
3. Re-apply policies from migration.

### Service role key exposed
1. **Rotate immediately** in Supabase dashboard → Settings → API.
2. Update `ir.config_parameter` in Odoo and all Edge Function secrets.
3. Audit `storage.objects` for unexpected inserts from that key.

---

## Verification checklist

```bash
# 1. Anon cannot list private bucket
curl -H "apikey: $SUPABASE_ANON_KEY" \
  "https://$PROJECT_REF.supabase.co/storage/v1/object/list/receipt-images"
# Expected: 400 or 0 objects returned

# 2. Employee read own object (substitute real path)
curl -H "Authorization: Bearer $USER_JWT" \
  "https://$PROJECT_REF.supabase.co/storage/v1/object/receipt-images/<company>/<user_id>/test.jpg"

# 3. Finance user can list company receipts
# (requires valid finance-role JWT)
```

Run SQL assertions from migration comments (`Step 8`) after applying.

---

## Retention (pending)
`make-96d82b2c-receipts` — no canonical data, recommend manual cleanup + bucket deletion after auditing contents.
