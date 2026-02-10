-- PHASE 2: BILLING SCHEMA
-- Tables: plans, billing_customers, subscriptions
-- Stripe integration foundation

-- ============================================================================
-- PLANS TABLE (billing tiers)
-- ============================================================================
create table if not exists public.plans (
  id text primary key,
  name text not null,
  description text,
  stripe_price_id text unique,
  max_users int,
  max_cms_items int,
  max_ai_runs int,
  created_at timestamptz default now()
);

comment on table public.plans is 'Billing plans - free, pro, enterprise';

-- ============================================================================
-- SEED PLANS
-- ============================================================================
insert into public.plans (id, name, description, stripe_price_id, max_users, max_cms_items, max_ai_runs)
values
  ('free', 'Free', 'Starter plan', null, 1, 10, 50),
  ('pro', 'Pro', 'Professional plan', 'price_PRO_PLACEHOLDER', 10, 1000, 5000),
  ('enterprise', 'Enterprise', 'Custom plan', 'price_ENT_PLACEHOLDER', 100, 100000, 100000)
on conflict (id) do nothing;

-- ============================================================================
-- BILLING CUSTOMERS TABLE (Stripe sync)
-- ============================================================================
create table if not exists public.billing_customers (
  org_id uuid primary key references public.organizations(id) on delete cascade,
  stripe_customer_id text unique not null,
  created_at timestamptz default now()
);

comment on table public.billing_customers is 'Stripe customer mapping';

-- ============================================================================
-- SUBSCRIPTIONS TABLE (Stripe sync)
-- ============================================================================
create table if not exists public.subscriptions (
  org_id uuid primary key references public.organizations(id) on delete cascade,
  plan_id text references public.plans(id),
  stripe_subscription_id text unique,
  status text check (
    status in ('active','trialing','past_due','canceled','incomplete')
  ),
  current_period_end timestamptz,
  cancel_at_period_end boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

comment on table public.subscriptions is 'Active subscriptions - synced from Stripe';

-- ============================================================================
-- UPDATED_AT TRIGGER
-- ============================================================================
create or replace function public.subscriptions_set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_subscriptions_updated_at on public.subscriptions;

create trigger trg_subscriptions_updated_at
before update on public.subscriptions
for each row
execute function public.subscriptions_set_updated_at();

-- ============================================================================
-- ORG ENTITLEMENTS VIEW
-- ============================================================================
create or replace view public.org_entitlements as
select
  o.id as org_id,
  coalesce(s.plan_id, 'free') as plan_id,
  p.max_users,
  p.max_cms_items,
  p.max_ai_runs
from public.organizations o
left join public.subscriptions s on s.org_id = o.id and s.status = 'active'
left join public.plans p on p.id = coalesce(s.plan_id, 'free');

comment on view public.org_entitlements is 'Org entitlements - defaults to free plan';
