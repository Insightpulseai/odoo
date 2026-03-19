-- =============================================================================
-- Migration: 20260227211220_create_kv_table_9405ce91.sql
-- Name:      create_kv_table_9405ce91
-- Applied:   2026-02-27 21:12:20 UTC (directly via Management API)
-- Purpose:   General-purpose KV store table with RLS for edge function use.
--
-- History note: this migration was applied directly to the remote project via
-- the Supabase Management API (POST /v1/projects/.../database/query) during
-- the Stripe webhook pipeline bootstrap session on 2026-02-27. The local
-- file was absent, causing `supabase migration list` to show the stamp in
-- the remote column only (gap). This file reconciles local ↔ remote history.
--
-- Reconciled with: supabase migration repair --status applied 20260227211220
-- Idempotent:      yes (IF NOT EXISTS)
-- =============================================================================

-- Key-value store (general purpose; RLS enabled, no policies — service role only)
create table if not exists kv_store_9405ce91 (
  key   text  not null primary key,
  value jsonb not null
);

alter table kv_store_9405ce91 enable row level security;

create index if not exists kv_store_9405ce91_key_idx
  on kv_store_9405ce91 (key text_pattern_ops);
