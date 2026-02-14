# Copilot Rules (Quick Reference)

10 rules for working in this codebase. Memorize these.

---

## 1. Supabase = Platform Truth

Supabase owns: analytics, AI data, orchestration, secrets, platform state.

## 2. Odoo = Business Truth

Odoo owns: invoices, HR, inventory, CRM, accounting, compliance records.

## 3. Never Confuse SSOT and SoR

If in doubt: business data → Odoo, everything else → Supabase.

## 4. Write to Odoo via Proxy Only

All Odoo mutations go through `supabase/functions/odoo-proxy`.
Never use direct SQL, dblink, or FDW to write to Odoo.

## 5. Secrets in Vault Only

Store all secrets in Supabase Vault.
Never commit `.env` files. Never hardcode credentials.

## 6. Schedule Jobs with pg_cron

Use Supabase `pg_cron` + Edge Functions for scheduling.
Do not use Odoo `ir.cron` for platform tasks.

## 7. AI Reads from Supabase

Agents read from Supabase by default.
Agents write to `ops.*`, `ai.*`, `analytics.*` schemas.

## 8. Mirror, Don't Duplicate

Odoo data in Supabase lives in `mirror.*` schema.
Mirror tables are read-only replicas, not canonical sources.

## 9. Fail Fast on Violations

If a task violates these rules: STOP, EXPLAIN, PROPOSE alternative.

## 10. Automate Everything

Prefer idempotent, auditable automation over manual steps.
Use Edge Functions, workflows, and cron for repeatable tasks.

---

## Quick Decision Tree

```
Is it business/financial data?
  → YES → Odoo (System of Record)
  → NO  → Supabase (Single Source of Truth)

Need to write to Odoo?
  → Use odoo-proxy Edge Function

Storing a secret?
  → Supabase Vault (vault.create_secret)

Scheduling a job?
  → pg_cron + Edge Function

AI agent output?
  → Supabase ops.* or ai.* schema
```

---

See [GOVERNANCE.md](./GOVERNANCE.md) for full documentation.
