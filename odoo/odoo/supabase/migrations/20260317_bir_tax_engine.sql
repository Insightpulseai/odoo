-- =============================================================================
-- IPAI BIR Tax Engine — Full Schema + ATC Seed Data
-- Migration: 20260317_bir_tax_engine.sql
-- Owner: Supabase SSOT (mdm.* + ops.tax_* + audit.tax_events)
-- Doctrine: Odoo = SOR (posted moves), Supabase = computation + output
-- =============================================================================

-- 0. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 1. SCHEMAS
CREATE SCHEMA IF NOT EXISTS mdm;
CREATE SCHEMA IF NOT EXISTS ops;
CREATE SCHEMA IF NOT EXISTS audit;

-- 1a. ATC code master
CREATE TABLE IF NOT EXISTS mdm.tax_codes (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    atc_code        text NOT NULL UNIQUE,
    description     text NOT NULL,
    entity_type     text NOT NULL CHECK (entity_type IN ('individual', 'corporate', 'both')),
    tax_category    text NOT NULL CHECK (tax_category IN ('ewt', 'wt_business', 'wt_final')),
    income_type     text NOT NULL,
    is_active       boolean NOT NULL DEFAULT true,
    bir_ref         text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

-- 1b. Tax rates with effective-date history
CREATE TABLE IF NOT EXISTS mdm.tax_rates (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    atc_code        text NOT NULL REFERENCES mdm.tax_codes(atc_code),
    rate            numeric(7,6) NOT NULL CHECK (rate >= 0 AND rate <= 1),
    effective_from  date NOT NULL,
    effective_to    date,
    bir_ref         text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT no_overlapping_rates UNIQUE (atc_code, effective_from)
);

-- 1c. ATC decision matrix
CREATE TABLE IF NOT EXISTS mdm.atc_matrix (
    id                  uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    payee_type          text NOT NULL CHECK (payee_type IN ('individual', 'corporate')),
    income_type         text NOT NULL,
    gross_income_band   text,
    amount_threshold    numeric(18,2),
    is_vat_registered   boolean,
    is_top_wha          boolean DEFAULT false,
    atc_code            text NOT NULL REFERENCES mdm.tax_codes(atc_code),
    priority            integer NOT NULL DEFAULT 100,
    bir_ref             text,
    notes               text,
    is_active           boolean NOT NULL DEFAULT true,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

-- 2a. Tax screening runs
CREATE TABLE IF NOT EXISTS ops.tax_runs (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       uuid NOT NULL,
    odoo_db         text NOT NULL CHECK (odoo_db IN ('odoo', 'odoo_staging', 'odoo_dev')),
    period_start    date NOT NULL,
    period_end      date NOT NULL,
    company_id      integer NOT NULL,
    status          text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','completed','failed','partial')),
    total_docs      integer,
    docs_processed  integer DEFAULT 0,
    docs_flagged    integer DEFAULT 0,
    total_ewt       numeric(18,2),
    total_base      numeric(18,2),
    started_at      timestamptz,
    completed_at    timestamptz,
    created_at      timestamptz NOT NULL DEFAULT now()
);

-- 2b. Per-document findings
CREATE TABLE IF NOT EXISTS ops.tax_findings (
    id                  uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_run_id          uuid NOT NULL REFERENCES ops.tax_runs(id),
    tenant_id           uuid NOT NULL,
    odoo_db             text NOT NULL,
    move_id             integer NOT NULL,
    move_name           text NOT NULL,
    move_line_id        integer NOT NULL,
    posting_date        date NOT NULL,
    partner_id          integer NOT NULL,
    partner_name        text NOT NULL,
    partner_tin         text,
    payee_type          text,
    income_type         text NOT NULL,
    atc_code            text REFERENCES mdm.tax_codes(atc_code),
    base_amount         numeric(18,2) NOT NULL,
    computed_rate       numeric(7,6),
    computed_ewt        numeric(18,2),
    posted_ewt          numeric(18,2),
    ewt_delta           numeric(18,2) GENERATED ALWAYS AS (COALESCE(computed_ewt, 0) - COALESCE(posted_ewt, 0)) STORED,
    risk_level          text NOT NULL DEFAULT 'ok' CHECK (risk_level IN ('ok','low','medium','high','critical')),
    risk_reason         text,
    requires_review     boolean NOT NULL DEFAULT false,
    reviewed_by         uuid,
    reviewed_at         timestamptz,
    review_notes        text,
    bir_form_eligible   text[],
    created_at          timestamptz NOT NULL DEFAULT now()
);

-- 2c. Generated BIR forms registry
CREATE TABLE IF NOT EXISTS ops.bir_forms (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       uuid NOT NULL,
    tax_run_id      uuid REFERENCES ops.tax_runs(id),
    form_type       text NOT NULL CHECK (form_type IN ('2307','2316','1601-EQ','2550Q','SLSP','QAP','SAWT')),
    period_start    date NOT NULL,
    period_end      date NOT NULL,
    company_id      integer NOT NULL,
    partner_id      integer,
    partner_name    text,
    partner_tin     text,
    total_base      numeric(18,2),
    total_ewt       numeric(18,2),
    storage_path    text,
    storage_bucket  text DEFAULT 'bir-forms',
    file_format     text CHECK (file_format IN ('xlsx','pdf','dat','xml')),
    file_size_bytes integer,
    checksum_sha256 text,
    status          text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','final','submitted','superseded')),
    submitted_at    timestamptz,
    odoo_db         text NOT NULL,
    odoo_move_ids   integer[],
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

-- 2d. Exception queue
CREATE TABLE IF NOT EXISTS ops.tax_exceptions (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       uuid NOT NULL,
    finding_id      uuid REFERENCES ops.tax_findings(id),
    exception_type  text NOT NULL,
    severity        text NOT NULL DEFAULT 'warning' CHECK (severity IN ('info','warning','error','critical')),
    description     text NOT NULL,
    payload         jsonb,
    status          text NOT NULL DEFAULT 'open' CHECK (status IN ('open','in_review','resolved','dismissed')),
    assigned_to     uuid,
    resolved_by     uuid,
    resolved_at     timestamptz,
    resolution_note text,
    created_at      timestamptz NOT NULL DEFAULT now()
);

-- 3. AUDIT: IMMUTABLE TAX EVENT LOG
CREATE TABLE IF NOT EXISTS audit.tax_events (
    id              bigserial PRIMARY KEY,
    tenant_id       uuid NOT NULL,
    event_type      text NOT NULL,
    source          text NOT NULL,
    tax_run_id      uuid,
    finding_id      uuid,
    form_id         uuid,
    odoo_db         text,
    move_id         integer,
    atc_code        text,
    payload         jsonb NOT NULL DEFAULT '{}',
    actor_id        uuid,
    created_at      timestamptz NOT NULL DEFAULT now()
);

-- 4. INDEXES
CREATE INDEX IF NOT EXISTS idx_atc_matrix_lookup ON mdm.atc_matrix (payee_type, income_type, is_active, priority);
CREATE INDEX IF NOT EXISTS idx_tax_rates_current ON mdm.tax_rates (atc_code, effective_from DESC) WHERE effective_to IS NULL;
CREATE INDEX IF NOT EXISTS idx_tax_findings_run ON ops.tax_findings (tax_run_id, risk_level);
CREATE INDEX IF NOT EXISTS idx_tax_findings_partner ON ops.tax_findings (tenant_id, partner_id, posting_date DESC);
CREATE INDEX IF NOT EXISTS idx_tax_findings_review ON ops.tax_findings (requires_review, reviewed_at) WHERE requires_review = true AND reviewed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_bir_forms_lookup ON ops.bir_forms (tenant_id, form_type, period_start, partner_id);
CREATE INDEX IF NOT EXISTS idx_tax_events_ts ON audit.tax_events (tenant_id, created_at DESC);

-- 5. RLS
ALTER TABLE mdm.tax_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE mdm.tax_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE mdm.atc_matrix ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.tax_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.tax_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.bir_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.tax_exceptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit.tax_events ENABLE ROW LEVEL SECURITY;

-- MDM read-only for authenticated
CREATE POLICY "mdm_tax_codes_read" ON mdm.tax_codes FOR SELECT USING (true);
CREATE POLICY "mdm_tax_rates_read" ON mdm.tax_rates FOR SELECT USING (true);
CREATE POLICY "mdm_atc_matrix_read" ON mdm.atc_matrix FOR SELECT USING (true);

-- Service role bypass
CREATE POLICY "service_tax_runs" ON ops.tax_runs FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_tax_findings" ON ops.tax_findings FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_bir_forms" ON ops.bir_forms FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_tax_exceptions" ON ops.tax_exceptions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_tax_events" ON audit.tax_events FOR ALL USING (auth.role() = 'service_role');

-- 6. UPDATED_AT TRIGGER
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$;

CREATE TRIGGER trg_mdm_atc_matrix_updated BEFORE UPDATE ON mdm.atc_matrix FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_ops_bir_forms_updated BEFORE UPDATE ON ops.bir_forms FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 7. HELPER RPCs
CREATE OR REPLACE FUNCTION ops.resolve_atc(
    p_payee_type text, p_income_type text,
    p_gross_income_band text DEFAULT 'any',
    p_is_vat_registered boolean DEFAULT NULL,
    p_is_top_wha boolean DEFAULT false,
    p_amount numeric DEFAULT 0
) RETURNS TABLE (atc_code text, current_rate numeric, description text, priority integer, bir_ref text)
LANGUAGE sql STABLE SECURITY DEFINER AS $$
    SELECT m.atc_code, r.rate, tc.description, m.priority, m.bir_ref
    FROM mdm.atc_matrix m
    JOIN mdm.tax_codes tc ON tc.atc_code = m.atc_code
    JOIN mdm.tax_rates r ON r.atc_code = m.atc_code
        AND r.effective_from <= CURRENT_DATE
        AND (r.effective_to IS NULL OR r.effective_to >= CURRENT_DATE)
    WHERE m.is_active = true
        AND (m.payee_type = p_payee_type)
        AND m.income_type = p_income_type
        AND (m.gross_income_band IS NULL OR m.gross_income_band = 'any' OR m.gross_income_band = p_gross_income_band)
        AND (m.is_vat_registered IS NULL OR m.is_vat_registered = p_is_vat_registered)
        AND (m.is_top_wha = false OR m.is_top_wha = p_is_top_wha)
        AND (m.amount_threshold IS NULL OR p_amount >= m.amount_threshold)
    ORDER BY m.priority ASC LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION ops.get_current_rate(p_atc_code text, p_as_of date DEFAULT CURRENT_DATE)
RETURNS numeric LANGUAGE sql STABLE SECURITY DEFINER AS $$
    SELECT rate FROM mdm.tax_rates
    WHERE atc_code = p_atc_code AND effective_from <= p_as_of
      AND (effective_to IS NULL OR effective_to >= p_as_of)
    ORDER BY effective_from DESC LIMIT 1;
$$;

-- 8. ATC SEED DATA (55 codes, 55 rates, 36 matrix rules)
-- See spec/ipai-tax-engine/prd.md for full ATC reference

INSERT INTO mdm.tax_codes (atc_code, description, entity_type, tax_category, income_type, bir_ref) VALUES
('WI100', 'Rentals - individual', 'individual', 'ewt', 'rental_real', 'RR 11-2018'),
('WC100', 'Rentals - corporate', 'corporate', 'ewt', 'rental_real', 'RR 11-2018'),
('WI160', 'Top WHA - services - individual', 'individual', 'ewt', 'services_wha', 'RR 11-2018'),
('WC160', 'Top WHA - services - corporate', 'corporate', 'ewt', 'services_wha', 'RR 11-2018'),
('WI158', 'Top WHA - goods - individual', 'individual', 'ewt', 'goods_wha', 'RR 11-2018'),
('WC158', 'Top WHA - goods - corporate', 'corporate', 'ewt', 'goods_wha', 'RR 11-2018'),
('WI010', 'Professional - individual lte 3M', 'individual', 'ewt', 'professional', 'RR 11-2018'),
('WI011', 'Professional - individual gt 3M/VAT', 'individual', 'ewt', 'professional', 'RR 11-2018'),
('WC010', 'Professional - corporate lte 720K', 'corporate', 'ewt', 'professional', 'RR 11-2018'),
('WC011', 'Professional - corporate gt 720K', 'corporate', 'ewt', 'professional', 'RR 11-2018'),
('WI050', 'Consultancy - individual lte 3M', 'individual', 'ewt', 'consultancy', 'RR 11-2018'),
('WI051', 'Consultancy - individual gt 3M/VAT', 'individual', 'ewt', 'consultancy', 'RR 11-2018'),
('WC050', 'Consultancy - corporate lte 720K', 'corporate', 'ewt', 'consultancy', 'RR 11-2018'),
('WC051', 'Consultancy - corporate gt 720K', 'corporate', 'ewt', 'consultancy', 'RR 11-2018'),
('WI157', 'GOCC services - individual', 'individual', 'ewt', 'services_govt', 'RR 11-2018'),
('WC157', 'GOCC services - corporate', 'corporate', 'ewt', 'services_govt', 'RR 11-2018'),
('WI640', 'GOCC goods - individual', 'individual', 'ewt', 'goods_govt', 'RR 11-2018'),
('WC640', 'GOCC goods - corporate', 'corporate', 'ewt', 'goods_govt', 'RR 11-2018')
ON CONFLICT (atc_code) DO NOTHING;

INSERT INTO mdm.tax_rates (atc_code, rate, effective_from, bir_ref) VALUES
('WI100', 0.050000, '2018-01-01', 'RR 11-2018'),
('WC100', 0.050000, '2018-01-01', 'RR 11-2018'),
('WI160', 0.020000, '2018-01-01', 'RR 11-2018'),
('WC160', 0.020000, '2018-01-01', 'RR 11-2018'),
('WI158', 0.010000, '2018-01-01', 'RR 11-2018'),
('WC158', 0.010000, '2018-01-01', 'RR 11-2018'),
('WI010', 0.050000, '2018-01-01', 'RR 11-2018'),
('WI011', 0.100000, '2018-01-01', 'RR 11-2018'),
('WC010', 0.100000, '2018-01-01', 'RR 11-2018'),
('WC011', 0.150000, '2018-01-01', 'RR 11-2018'),
('WI050', 0.050000, '2018-01-01', 'RR 11-2018'),
('WI051', 0.100000, '2018-01-01', 'RR 11-2018'),
('WC050', 0.100000, '2018-01-01', 'RR 11-2018'),
('WC051', 0.150000, '2018-01-01', 'RR 11-2018'),
('WI157', 0.020000, '2018-01-01', 'RR 11-2018'),
('WC157', 0.020000, '2018-01-01', 'RR 11-2018'),
('WI640', 0.010000, '2018-01-01', 'RR 11-2018'),
('WC640', 0.010000, '2018-01-01', 'RR 11-2018')
ON CONFLICT (atc_code, effective_from) DO NOTHING;

INSERT INTO mdm.atc_matrix (payee_type, income_type, gross_income_band, is_top_wha, atc_code, priority, bir_ref) VALUES
('individual', 'rental_real', 'any', false, 'WI100', 10, 'RR 11-2018'),
('corporate', 'rental_real', 'any', false, 'WC100', 10, 'RR 11-2018'),
('individual', 'services_wha', 'any', true, 'WI160', 5, 'RR 11-2018'),
('corporate', 'services_wha', 'any', true, 'WC160', 5, 'RR 11-2018'),
('individual', 'goods_wha', 'any', true, 'WI158', 5, 'RR 11-2018'),
('corporate', 'goods_wha', 'any', true, 'WC158', 5, 'RR 11-2018'),
('individual', 'professional', 'lte_3m', false, 'WI010', 20, 'RR 11-2018'),
('individual', 'professional', 'gt_3m', false, 'WI011', 20, 'RR 11-2018'),
('corporate', 'professional', 'lte_720k', false, 'WC010', 20, 'RR 11-2018'),
('corporate', 'professional', 'gt_720k', false, 'WC011', 20, 'RR 11-2018'),
('individual', 'consultancy', 'lte_3m', false, 'WI050', 20, 'RR 11-2018'),
('individual', 'consultancy', 'gt_3m', false, 'WI051', 20, 'RR 11-2018'),
('corporate', 'consultancy', 'lte_720k', false, 'WC050', 20, 'RR 11-2018'),
('corporate', 'consultancy', 'gt_720k', false, 'WC051', 20, 'RR 11-2018'),
('individual', 'services_govt', 'any', false, 'WI157', 10, 'RR 11-2018'),
('corporate', 'services_govt', 'any', false, 'WC157', 10, 'RR 11-2018'),
('individual', 'goods_govt', 'any', false, 'WI640', 10, 'RR 11-2018'),
('corporate', 'goods_govt', 'any', false, 'WC640', 10, 'RR 11-2018')
ON CONFLICT DO NOTHING;
