-- PHASE 2: BILLING RLS POLICIES
-- Security policies for plans, billing_customers, subscriptions

-- ============================================================================
-- ENABLE RLS ON BILLING TABLES
-- ============================================================================
alter table public.plans enable row level security;
alter table public.billing_customers enable row level security;
alter table public.subscriptions enable row level security;

-- ============================================================================
-- PLANS POLICIES (public read)
-- ============================================================================
drop policy if exists "public_read_plans" on public.plans;
create policy "public_read_plans"
on public.plans for select
using (true);

-- ============================================================================
-- BILLING CUSTOMERS POLICIES (org members only)
-- ============================================================================
drop policy if exists "org_members_read_billing_customers" on public.billing_customers;
create policy "org_members_read_billing_customers"
on public.billing_customers for select
using (public.is_org_member(org_id));

drop policy if exists "org_owners_manage_billing_customers" on public.billing_customers;
create policy "org_owners_manage_billing_customers"
on public.billing_customers for all
using (
  exists (
    select 1 from public.organization_members m
    where m.org_id = billing_customers.org_id
      and m.user_id = auth.uid()
      and m.role in ('owner', 'admin')
  )
);

-- ============================================================================
-- SUBSCRIPTIONS POLICIES (org members read, service role write)
-- ============================================================================
drop policy if exists "org_members_read_subscriptions" on public.subscriptions;
create policy "org_members_read_subscriptions"
on public.subscriptions for select
using (public.is_org_member(org_id));

drop policy if exists "service_role_manage_subscriptions" on public.subscriptions;
create policy "service_role_manage_subscriptions"
on public.subscriptions for all
using (auth.role() = 'service_role');

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================
grant select on public.plans to anon, authenticated;
grant select on public.billing_customers to authenticated;
grant select on public.subscriptions to authenticated;
grant all on public.billing_customers to service_role;
grant all on public.subscriptions to service_role;
grant select on public.org_entitlements to authenticated;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
create index if not exists idx_subscriptions_org_status on public.subscriptions(org_id, status);
create index if not exists idx_billing_customers_stripe on public.billing_customers(stripe_customer_id);
create index if not exists idx_subscriptions_stripe on public.subscriptions(stripe_subscription_id);
