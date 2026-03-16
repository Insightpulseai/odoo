-- ============================================================================
-- Migration: Billing & Usage Tracking Tables
-- Created: 2026-02-11
-- Phase: 1 - Core SaaS Primitives
-- Purpose: Stripe billing integration, usage metering, entitlement foundation
-- ============================================================================

-- ====================
-- BILLING CUSTOMERS
-- ====================

CREATE TABLE IF NOT EXISTS billing_customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  stripe_customer_id TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT billing_customers_org_id_unique UNIQUE (org_id)
);

COMMENT ON TABLE billing_customers IS 'Maps organizations to Stripe customers';
COMMENT ON COLUMN billing_customers.stripe_customer_id IS 'Stripe customer ID (cus_...)';
COMMENT ON COLUMN billing_customers.email IS 'Billing email (may differ from org email)';

CREATE INDEX idx_billing_customers_org_id ON billing_customers(org_id);
CREATE INDEX idx_billing_customers_stripe_id ON billing_customers(stripe_customer_id);

-- ====================
-- PLANS
-- ====================

CREATE TABLE IF NOT EXISTS plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  price_monthly_cents INTEGER NOT NULL DEFAULT 0,
  stripe_price_id TEXT,
  limits JSONB NOT NULL DEFAULT '{}',
  features JSONB NOT NULL DEFAULT '[]',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE plans IS 'Subscription plans (free, pro, enterprise)';
COMMENT ON COLUMN plans.limits IS 'Usage limits: { ai_runs: 1000, cms_items: 50, users: 10 }';
COMMENT ON COLUMN plans.features IS 'Feature flags: ["advanced_analytics", "priority_support"]';
COMMENT ON COLUMN plans.stripe_price_id IS 'Stripe Price ID (price_...)';

CREATE INDEX idx_plans_name ON plans(name);
CREATE INDEX idx_plans_active ON plans(is_active) WHERE is_active = TRUE;

-- ====================
-- SUBSCRIPTIONS
-- ====================

CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  plan_id UUID NOT NULL REFERENCES plans(id),
  stripe_subscription_id TEXT UNIQUE,
  stripe_customer_id TEXT NOT NULL REFERENCES billing_customers(stripe_customer_id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'active',
  current_period_start TIMESTAMPTZ NOT NULL,
  current_period_end TIMESTAMPTZ NOT NULL,
  cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
  canceled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT subscriptions_status_check CHECK (status IN ('active', 'canceled', 'past_due', 'trialing', 'unpaid')),
  CONSTRAINT subscriptions_org_id_unique UNIQUE (org_id)
);

COMMENT ON TABLE subscriptions IS 'Organization subscriptions with Stripe sync';
COMMENT ON COLUMN subscriptions.status IS 'Stripe subscription status';
COMMENT ON COLUMN subscriptions.current_period_start IS 'Billing period start (UTC)';
COMMENT ON COLUMN subscriptions.current_period_end IS 'Billing period end (UTC)';

CREATE INDEX idx_subscriptions_org_id ON subscriptions(org_id);
CREATE INDEX idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_period_end ON subscriptions(current_period_end);

-- ====================
-- USAGE EVENTS
-- ====================

CREATE TABLE IF NOT EXISTS usage_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT usage_events_type_check CHECK (event_type IN ('ai_run', 'cms_item', 'user_added', 'storage_usage', 'api_call'))
);

COMMENT ON TABLE usage_events IS 'Usage metering events (immutable log)';
COMMENT ON COLUMN usage_events.event_type IS 'Type of billable event';
COMMENT ON COLUMN usage_events.metadata IS 'Event details: { agent_id, run_duration_ms, tokens_used, etc }';

CREATE INDEX idx_usage_events_org_id ON usage_events(org_id);
CREATE INDEX idx_usage_events_created_at ON usage_events(created_at DESC);
CREATE INDEX idx_usage_events_type ON usage_events(event_type);
CREATE INDEX idx_usage_events_org_type ON usage_events(org_id, event_type);

-- Partitioning for performance (monthly partitions)
-- Note: Future enhancement - pg_partman for automated partition management
-- CREATE TABLE usage_events_y2026m02 PARTITION OF usage_events
--   FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- ====================
-- ORG USAGE CURRENT (Materialized View)
-- ====================

CREATE MATERIALIZED VIEW org_usage_current AS
SELECT
  org_id,
  COUNT(*) FILTER (WHERE event_type = 'ai_run') AS ai_runs_count,
  COUNT(*) FILTER (WHERE event_type = 'cms_item') AS cms_items_count,
  COUNT(*) FILTER (WHERE event_type = 'user_added') AS users_count,
  COUNT(*) FILTER (WHERE event_type = 'storage_usage') AS storage_usage_mb,
  COUNT(*) FILTER (WHERE event_type = 'api_call') AS api_calls_count,
  MAX(created_at) AS last_event_at
FROM usage_events
WHERE created_at >= DATE_TRUNC('month', NOW())
GROUP BY org_id;

COMMENT ON MATERIALIZED VIEW org_usage_current IS 'Aggregated usage for current billing period (refreshed every 5 min)';

CREATE UNIQUE INDEX idx_org_usage_current_org_id ON org_usage_current(org_id);

-- ====================
-- REFRESH FUNCTION
-- ====================

CREATE OR REPLACE FUNCTION refresh_org_usage()
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY org_usage_current;

  -- Log refresh execution
  INSERT INTO cron_job_runs (job_name, status, executed_at)
  VALUES ('refresh_org_usage', 'completed', NOW());

EXCEPTION
  WHEN OTHERS THEN
    -- Log failure
    INSERT INTO cron_job_runs (job_name, status, error_message, executed_at)
    VALUES ('refresh_org_usage', 'failed', SQLERRM, NOW());
    RAISE;
END;
$$;

COMMENT ON FUNCTION refresh_org_usage IS 'Refresh org_usage_current materialized view (called by pg_cron every 5 min)';

-- ====================
-- CRON JOB MONITORING
-- ====================

CREATE TABLE IF NOT EXISTS cron_job_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_name TEXT NOT NULL,
  status TEXT NOT NULL,
  error_message TEXT,
  executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT cron_job_runs_status_check CHECK (status IN ('completed', 'failed'))
);

COMMENT ON TABLE cron_job_runs IS 'pg_cron job execution history for monitoring';

CREATE INDEX idx_cron_job_runs_job_name ON cron_job_runs(job_name);
CREATE INDEX idx_cron_job_runs_executed_at ON cron_job_runs(executed_at DESC);

-- ====================
-- AUTO-UPDATED TIMESTAMPS
-- ====================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_billing_customers_updated_at
  BEFORE UPDATE ON billing_customers
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plans_updated_at
  BEFORE UPDATE ON plans
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
  BEFORE UPDATE ON subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ====================
-- DEFAULT PLAN ASSIGNMENT
-- ====================

CREATE OR REPLACE FUNCTION assign_default_plan()
RETURNS TRIGGER AS $$
DECLARE
  v_free_plan_id UUID;
BEGIN
  -- Get free plan ID
  SELECT id INTO v_free_plan_id
  FROM plans
  WHERE name = 'free'
  LIMIT 1;

  -- Create subscription with free plan
  IF v_free_plan_id IS NOT NULL THEN
    INSERT INTO subscriptions (
      org_id,
      plan_id,
      stripe_customer_id,
      status,
      current_period_start,
      current_period_end
    )
    VALUES (
      NEW.id,
      v_free_plan_id,
      'placeholder_' || NEW.id::TEXT,  -- Placeholder until Stripe customer created
      'active',
      NOW(),
      NOW() + INTERVAL '30 days'
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Note: Trigger will be created after organizations table exists
-- CREATE TRIGGER assign_default_plan_on_org_create
--   AFTER INSERT ON organizations
--   FOR EACH ROW
--   EXECUTE FUNCTION assign_default_plan();

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
