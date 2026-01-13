-- Migration: IPAI Sample Metrics
-- Purpose: Mirror Odoo ipai.sample.metric model for Fluent dashboards
-- Date: 2026-01-13

-- =============================================================================
-- SCHEMA
-- =============================================================================

create schema if not exists ipai;

-- =============================================================================
-- TABLE: ipai_sample_metrics
-- Mirrors: addons/ipai/ipai_sample_metrics/models/sample_metric.py
-- =============================================================================

create table if not exists ipai.ipai_sample_metrics (
    id            bigserial primary key,
    odoo_id       bigint unique,          -- back-link to ipai.sample.metric.id
    name          text not null,
    code          text not null,
    date          date not null default current_date,
    brand_id      bigint,                 -- res.partner.id (brand)
    store_id      bigint,                 -- res.partner.id (store)
    value         double precision not null,
    unit          text not null check (unit in ('percent', 'count', 'amount')),
    is_alert      boolean not null default false,
    notes         text,
    active        boolean not null default true,
    inserted_at   timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

comment on table ipai.ipai_sample_metrics is 'Mirror of Odoo ipai.sample.metric for Fluent dashboards';
comment on column ipai.ipai_sample_metrics.odoo_id is 'Foreign key to Odoo ipai.sample.metric.id';
comment on column ipai.ipai_sample_metrics.code is 'Technical metric code, e.g. CONV_RATE';
comment on column ipai.ipai_sample_metrics.is_alert is 'Auto flag when metric looks abnormal (value <10% or >95%)';

-- =============================================================================
-- INDEXES
-- =============================================================================

create index if not exists idx_ipai_sample_metrics_code_date
    on ipai.ipai_sample_metrics (code, date desc);

create index if not exists idx_ipai_sample_metrics_brand
    on ipai.ipai_sample_metrics (brand_id)
    where brand_id is not null;

create index if not exists idx_ipai_sample_metrics_store
    on ipai.ipai_sample_metrics (store_id)
    where store_id is not null;

create index if not exists idx_ipai_sample_metrics_alert
    on ipai.ipai_sample_metrics (is_alert)
    where is_alert = true;

create index if not exists idx_ipai_sample_metrics_active
    on ipai.ipai_sample_metrics (active)
    where active = true;

-- =============================================================================
-- ROW LEVEL SECURITY
-- =============================================================================

alter table ipai.ipai_sample_metrics enable row level security;

-- Read access for authenticated users
create policy "ipai_sample_metrics_select_authenticated"
    on ipai.ipai_sample_metrics
    for select
    to authenticated
    using (active = true);

-- Full access for service role (sync scripts)
create policy "ipai_sample_metrics_all_service_role"
    on ipai.ipai_sample_metrics
    for all
    to service_role
    using (true)
    with check (true);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-update updated_at timestamp
create or replace function ipai.touch_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_ipai_sample_metrics_updated_at on ipai.ipai_sample_metrics;

create trigger trg_ipai_sample_metrics_updated_at
    before update on ipai.ipai_sample_metrics
    for each row execute function ipai.touch_updated_at();

-- =============================================================================
-- UNIQUE CONSTRAINT FOR UPSERT
-- =============================================================================

-- Enable upsert on odoo_id (primary sync key)
-- Note: odoo_id is already unique, but we add a composite for code+date fallback
create unique index if not exists idx_ipai_sample_metrics_code_date_unique
    on ipai.ipai_sample_metrics (code, date, coalesce(brand_id, 0), coalesce(store_id, 0))
    where odoo_id is null;

-- =============================================================================
-- SEED DATA (matches Odoo demo data)
-- =============================================================================

insert into ipai.ipai_sample_metrics (odoo_id, name, code, date, value, unit, is_alert, notes)
values
    (1, 'Conversion Rate', 'CONV_RATE', '2026-01-01', 42.0, 'percent', false, 'Demo metric seeded by ipai_sample_metrics.'),
    (2, 'Daily Traffic', 'TRAFFIC', '2026-01-01', 1250.0, 'count', false, 'Demo metric seeded by ipai_sample_metrics.'),
    (3, 'Revenue Target', 'REV_TARGET', '2026-01-01', 98500.0, 'amount', false, 'Demo metric seeded by ipai_sample_metrics.')
on conflict (odoo_id) do nothing;

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

grant usage on schema ipai to authenticated, service_role;
grant select on ipai.ipai_sample_metrics to authenticated;
grant all on ipai.ipai_sample_metrics to service_role;
grant usage, select on sequence ipai.ipai_sample_metrics_id_seq to service_role;
