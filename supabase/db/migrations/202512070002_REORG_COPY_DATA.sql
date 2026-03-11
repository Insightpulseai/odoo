-- Migration: Copy Data from Legacy Tables
-- Version: 202512070002
-- Description: Migrate data from public.* legacy tables to new domain schemas
-- Author: Platform Team
-- Date: 2025-12-07
--
-- IMPORTANT: Run this AFTER 202512070001_REORG_CREATE_DOMAIN_TABLES.sql
-- This migration is IDEMPOTENT - safe to run multiple times

-- ============================================================================
-- PHASE 1: MIGRATE EXPENSE DATA
-- ============================================================================

-- Migrate expense_reports if legacy table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'expense_reports') THEN
        INSERT INTO expense.expense_reports (
            id, tenant_id, employee_id, report_number, description, status,
            total_amount, currency, submitted_at, approved_at, approved_by,
            policy_flagged, created_at, updated_at
        )
        SELECT
            id, tenant_id, employee_id, report_number, description, status,
            total_amount, COALESCE(currency, 'PHP'), submitted_at, approved_at, approved_by,
            COALESCE(policy_flagged, false), created_at, updated_at
        FROM public.expense_reports
        WHERE NOT EXISTS (
            SELECT 1 FROM expense.expense_reports e WHERE e.id = public.expense_reports.id
        );
        RAISE NOTICE 'Migrated expense_reports from public schema';
    ELSE
        RAISE NOTICE 'No legacy public.expense_reports table found - skipping';
    END IF;
END $$;

-- Migrate expenses (line items) if legacy table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'expenses') THEN
        INSERT INTO expense.expenses (
            id, tenant_id, expense_report_id, line_seq, category_code, description,
            amount, currency, spend_date, receipt_document_id, policy_violation,
            created_at, updated_at
        )
        SELECT
            id, tenant_id, expense_report_id,
            COALESCE(line_seq, ROW_NUMBER() OVER (PARTITION BY expense_report_id ORDER BY id)::integer),
            category_code, description, amount, COALESCE(currency, 'PHP'), spend_date,
            receipt_document_id, policy_violation, created_at, updated_at
        FROM public.expenses
        WHERE NOT EXISTS (
            SELECT 1 FROM expense.expenses e WHERE e.id = public.expenses.id
        );
        RAISE NOTICE 'Migrated expenses from public schema';
    ELSE
        RAISE NOTICE 'No legacy public.expenses table found - skipping';
    END IF;
END $$;

-- Migrate cash_advances if legacy table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'cash_advances') THEN
        INSERT INTO expense.cash_advances (
            id, tenant_id, employee_id, advance_number, amount, currency,
            purpose, status, trip_start_date, trip_end_date, reconciled_amount,
            created_at, updated_at
        )
        SELECT
            id, tenant_id, employee_id, advance_number, amount, COALESCE(currency, 'PHP'),
            purpose, status, trip_start_date, trip_end_date, COALESCE(reconciled_amount, 0),
            created_at, updated_at
        FROM public.cash_advances
        WHERE NOT EXISTS (
            SELECT 1 FROM expense.cash_advances e WHERE e.id = public.cash_advances.id
        );
        RAISE NOTICE 'Migrated cash_advances from public schema';
    ELSE
        RAISE NOTICE 'No legacy public.cash_advances table found - skipping';
    END IF;
END $$;

-- ============================================================================
-- PHASE 2: MIGRATE PROJECT DATA
-- ============================================================================

-- Migrate projects if legacy table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects') THEN
        INSERT INTO projects.projects (
            id, tenant_id, odoo_id, project_code, name, description,
            status, start_date, end_date, budget_amount, budget_currency,
            project_manager_id, created_at, updated_at
        )
        SELECT
            id, tenant_id, odoo_id, project_code, name, description,
            COALESCE(status, 'active'), start_date, end_date, budget_amount,
            COALESCE(budget_currency, 'PHP'), project_manager_id, created_at, updated_at
        FROM public.projects
        WHERE NOT EXISTS (
            SELECT 1 FROM projects.projects p WHERE p.id = public.projects.id
        );
        RAISE NOTICE 'Migrated projects from public schema';
    ELSE
        RAISE NOTICE 'No legacy public.projects table found - skipping';
    END IF;
END $$;

-- Migrate project_members if legacy table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'project_members') THEN
        INSERT INTO projects.project_members (
            id, tenant_id, project_id, employee_id, role, allocation_percent,
            start_date, end_date, created_at, updated_at
        )
        SELECT
            id, tenant_id, project_id, employee_id, role,
            COALESCE(allocation_percent, 100), start_date, end_date,
            created_at, updated_at
        FROM public.project_members
        WHERE NOT EXISTS (
            SELECT 1 FROM projects.project_members p WHERE p.id = public.project_members.id
        );
        RAISE NOTICE 'Migrated project_members from public schema';
    ELSE
        RAISE NOTICE 'No legacy public.project_members table found - skipping';
    END IF;
END $$;

-- ============================================================================
-- PHASE 3: MIGRATE RATES DATA
-- ============================================================================

-- Migrate vendor_profile if legacy table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'vendor_profile') THEN
        INSERT INTO rates.vendor_profile (
            id, tenant_id, odoo_partner_id, vendor_code, name, category,
            status, rating, created_at, updated_at
        )
        SELECT
            id, tenant_id, odoo_partner_id, vendor_code, name, category,
            COALESCE(status, 'active'), rating, created_at, updated_at
        FROM public.vendor_profile
        WHERE NOT EXISTS (
            SELECT 1 FROM rates.vendor_profile r WHERE r.id = public.vendor_profile.id
        );
        RAISE NOTICE 'Migrated vendor_profile from public schema';
    ELSE
        RAISE NOTICE 'No legacy public.vendor_profile table found - skipping';
    END IF;
END $$;

-- Migrate rate_cards if legacy table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'rate_cards') THEN
        INSERT INTO rates.rate_cards (
            id, tenant_id, vendor_id, rate_card_code, name, effective_from,
            effective_to, status, approved_by, approved_at, created_at, updated_at
        )
        SELECT
            id, tenant_id, vendor_id, rate_card_code, name, effective_from,
            effective_to, COALESCE(status, 'draft'), approved_by, approved_at,
            created_at, updated_at
        FROM public.rate_cards
        WHERE NOT EXISTS (
            SELECT 1 FROM rates.rate_cards r WHERE r.id = public.rate_cards.id
        );
        RAISE NOTICE 'Migrated rate_cards from public schema';
    ELSE
        RAISE NOTICE 'No legacy public.rate_cards table found - skipping';
    END IF;
END $$;

-- ============================================================================
-- PHASE 4: MIGRATE DOCUMENT DATA
-- ============================================================================

-- Migrate raw_documents if legacy table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'raw_documents') THEN
        INSERT INTO doc.raw_documents (
            id, tenant_id, source_hash, file_name, file_type, file_size_bytes,
            storage_path, uploaded_by, created_at, updated_at
        )
        SELECT
            id, tenant_id, source_hash, file_name, file_type, file_size_bytes,
            storage_path, uploaded_by, created_at, updated_at
        FROM public.raw_documents
        WHERE NOT EXISTS (
            SELECT 1 FROM doc.raw_documents d WHERE d.id = public.raw_documents.id
        );
        RAISE NOTICE 'Migrated raw_documents from public schema';
    ELSE
        RAISE NOTICE 'No legacy public.raw_documents table found - skipping';
    END IF;
END $$;

-- ============================================================================
-- PHASE 5: VALIDATION QUERIES
-- ============================================================================

-- Count comparison for validation
DO $$
DECLARE
    legacy_count INTEGER;
    new_count INTEGER;
BEGIN
    -- Validate expense_reports migration
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'expense_reports') THEN
        SELECT COUNT(*) INTO legacy_count FROM public.expense_reports;
        SELECT COUNT(*) INTO new_count FROM expense.expense_reports;
        RAISE NOTICE 'expense_reports: legacy=%, new=%', legacy_count, new_count;
    END IF;

    -- Validate projects migration
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects') THEN
        SELECT COUNT(*) INTO legacy_count FROM public.projects;
        SELECT COUNT(*) INTO new_count FROM projects.projects;
        RAISE NOTICE 'projects: legacy=%, new=%', legacy_count, new_count;
    END IF;
END $$;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

COMMENT ON SCHEMA expense IS 'Data migrated from public schema on ' || now()::text;
COMMENT ON SCHEMA projects IS 'Data migrated from public schema on ' || now()::text;
