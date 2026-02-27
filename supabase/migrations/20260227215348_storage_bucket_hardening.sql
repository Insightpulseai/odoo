-- Migration: Storage Bucket Hardening
-- Date: 2026-02-27
-- Purpose: Enforce privacy boundaries, deterministic key naming, and
--          RLS-based access policies for IPAI finance pipeline buckets.
--
-- Buckets in scope:
--   receipt-images       (private, user-scoped)
--   attachments          (private, service-role write / finance read)
--   superset-bundles     (private, service-role write / finance read)
--   make-96d82b2c-receipts (private, temporary)
--   data import          → rename to data-import (private)
--   echarts-themes       (public read, admin/service write only)
--
-- Key naming convention (SSOT — see docs/runbooks/supabase/storage_buckets.md):
--   receipt-images/<company_id>/<user_id>/<yyyy>/<mm>/<expense_id>/<sha256>.<ext>
--   attachments/<company_id>/liquidations/<liquidation_id>/LIQ-YYYY-####.pdf
--   attachments/<company_id>/ocr/<expense_id>/<sha256>.json
--
-- Auth model assumed:
--   public.profiles(user_id uuid, role text, company_id uuid)
--   roles: 'employee', 'manager', 'finance', 'admin', 'service_role'
--
-- All policies use auth.uid() for employee scope and join to profiles for role.

-- ── 0. Create profiles helper view (idempotent) ───────────────────────────────

CREATE TABLE IF NOT EXISTS public.profiles (
    user_id   uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role      text NOT NULL DEFAULT 'employee',
    company_id uuid
);

COMMENT ON TABLE public.profiles IS
    'User role + company mapping for IPAI Storage RLS policies.';

-- ── 1. Lock down buckets ──────────────────────────────────────────────────────

-- receipt-images: private
UPDATE storage.buckets
SET public = false
WHERE id = 'receipt-images';

-- attachments: private
UPDATE storage.buckets
SET public = false
WHERE id = 'attachments';

-- superset-bundles: private
UPDATE storage.buckets
SET public = false
WHERE id = 'superset-bundles';

-- make-96d82b2c-receipts: private
UPDATE storage.buckets
SET public = false
WHERE id = 'make-96d82b2c-receipts';

-- echarts-themes: stays public read (intentional for embedded charts)
-- No write policy change here; admin/service write policies added below.

-- data-import: create canonical private bucket (objects migrated separately)
INSERT INTO storage.buckets (id, name, public)
VALUES ('data-import', 'data-import', false)
ON CONFLICT (id) DO UPDATE SET public = false;

-- ── 2. Drop legacy policies (idempotent cleanup) ──────────────────────────────

DO $$
DECLARE
    p record;
BEGIN
    FOR p IN
        SELECT policyname, tablename
        FROM pg_policies
        WHERE schemaname = 'storage'
          AND tablename = 'objects'
          AND policyname LIKE 'ipai_%'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON storage.objects', p.policyname);
    END LOOP;
END $$;

-- ── 3. receipt-images policies ────────────────────────────────────────────────

-- Employee: upload to their own prefix
CREATE POLICY "ipai_receipt_images_employee_insert"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'receipt-images'
    AND (storage.foldername(name))[2] = auth.uid()::text
);

-- Employee: read own receipts
CREATE POLICY "ipai_receipt_images_employee_select"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'receipt-images'
    AND (storage.foldername(name))[2] = auth.uid()::text
);

-- Finance: read all receipts in same company
CREATE POLICY "ipai_receipt_images_finance_select"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'receipt-images'
    AND EXISTS (
        SELECT 1 FROM public.profiles p
        WHERE p.user_id = auth.uid()
          AND p.role IN ('finance', 'manager', 'admin')
          AND (storage.foldername(name))[1] = p.company_id::text
    )
);

-- Service role: unrestricted (for OCR pipeline writes)
CREATE POLICY "ipai_receipt_images_service_all"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'receipt-images')
WITH CHECK (bucket_id = 'receipt-images');

-- ── 4. attachments policies ───────────────────────────────────────────────────

-- Service role: write liquidation PDFs and OCR JSON
CREATE POLICY "ipai_attachments_service_insert"
ON storage.objects FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'attachments');

CREATE POLICY "ipai_attachments_service_select"
ON storage.objects FOR SELECT
TO service_role
USING (bucket_id = 'attachments');

-- Finance: read attachments in same company
CREATE POLICY "ipai_attachments_finance_select"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'attachments'
    AND EXISTS (
        SELECT 1 FROM public.profiles p
        WHERE p.user_id = auth.uid()
          AND p.role IN ('finance', 'manager', 'admin')
          AND (storage.foldername(name))[1] = p.company_id::text
    )
);

-- Deny public access (no SELECT for anon)

-- ── 5. superset-bundles policies ──────────────────────────────────────────────

-- Service role only write
CREATE POLICY "ipai_superset_service_insert"
ON storage.objects FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'superset-bundles');

-- Finance/admin read
CREATE POLICY "ipai_superset_finance_select"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'superset-bundles'
    AND EXISTS (
        SELECT 1 FROM public.profiles p
        WHERE p.user_id = auth.uid()
          AND p.role IN ('finance', 'admin')
    )
);

-- ── 6. echarts-themes policies ────────────────────────────────────────────────

-- Public read (bucket is public, this adds explicit row-level to satisfy RLS)
CREATE POLICY "ipai_echarts_public_select"
ON storage.objects FOR SELECT
TO anon, authenticated
USING (bucket_id = 'echarts-themes');

-- Admin/service write only
CREATE POLICY "ipai_echarts_admin_insert"
ON storage.objects FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'echarts-themes');

CREATE POLICY "ipai_echarts_admin_insert_auth"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'echarts-themes'
    AND EXISTS (
        SELECT 1 FROM public.profiles p
        WHERE p.user_id = auth.uid() AND p.role = 'admin'
    )
);

-- ── 7. data-import policies ───────────────────────────────────────────────────

-- Service role and finance admins only
CREATE POLICY "ipai_data_import_service_all"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'data-import')
WITH CHECK (bucket_id = 'data-import');

CREATE POLICY "ipai_data_import_admin_select"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'data-import'
    AND EXISTS (
        SELECT 1 FROM public.profiles p
        WHERE p.user_id = auth.uid() AND p.role = 'admin'
    )
);

-- ── 8. Verification assertions ────────────────────────────────────────────────
-- Run these after migration to confirm policy intent:
--
--   1) Anon cannot list private buckets:
--      SELECT * FROM storage.objects WHERE bucket_id = 'receipt-images';
--      -- should return 0 rows when called with anon key
--
--   2) Employee cannot read another user's receipt:
--      -- Call with user A's JWT; try to SELECT object with user B's uid in path
--      -- Should return 0 rows
--
--   3) Finance user can read company receipts:
--      -- Call with finance JWT; SELECT receipt-images objects for company prefix
--      -- Should return rows
--
--   4) Service role can write OCR JSON to attachments:
--      -- INSERT into attachments/<company_id>/ocr/<expense_id>/...
--      -- Should succeed with service_role key
