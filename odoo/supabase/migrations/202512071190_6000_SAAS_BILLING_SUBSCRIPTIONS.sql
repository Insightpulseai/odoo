-- 202512071190_6000_SAAS_BILLING_SUBSCRIPTIONS.sql
-- Family: 6000 - SaaS billing / subscriptions / plan features
-- Purpose:
--   * Multi-tenant SaaS subscription skeleton linked to core.tenant.
-- Safety:
--   * Additive and idempotent.

BEGIN;

CREATE SCHEMA IF NOT EXISTS saas;

-- TODO: SAAS TABLES
--   * saas.plan
--   * saas.plan_feature
--   * saas.subscription
--   * saas.subscription_usage
--   * saas.billing_event

-- Notes:
--   * Link saas.subscription.tenant_id → core.tenant.id
--   * Use plan_feature to toggle access to engines/modules per plan.

COMMIT;
