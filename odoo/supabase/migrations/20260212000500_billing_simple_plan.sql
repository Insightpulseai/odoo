-- ============================================================================
-- Migration: Simple Pro Plan Seeding
-- Created: 2026-02-11
-- Phase: 1 - Core SaaS Primitives
-- Purpose: Seed free and pro plans for MVP launch
-- ============================================================================

-- ====================
-- SEED FREE PLAN
-- ====================

INSERT INTO plans (
  name,
  display_name,
  price_monthly_cents,
  stripe_price_id,
  limits,
  features,
  is_active
)
VALUES (
  'free',
  'Free Plan',
  0,
  NULL,  -- No Stripe price for free plan
  '{
    "ai_runs": 1000,
    "cms_items": 10,
    "users": 3,
    "storage_mb": 500,
    "api_calls_per_day": 1000
  }'::JSONB,
  '[
    "Basic AI agents",
    "Community support",
    "Public CMS content"
  ]'::JSONB,
  TRUE
)
ON CONFLICT (name) DO UPDATE SET
  display_name = EXCLUDED.display_name,
  price_monthly_cents = EXCLUDED.price_monthly_cents,
  limits = EXCLUDED.limits,
  features = EXCLUDED.features,
  is_active = EXCLUDED.is_active,
  updated_at = NOW();

-- ====================
-- SEED PRO PLAN
-- ====================

INSERT INTO plans (
  name,
  display_name,
  price_monthly_cents,
  stripe_price_id,
  limits,
  features,
  is_active
)
VALUES (
  'pro',
  'Pro Plan',
  9900,  -- $99.00/month
  'price_pro_monthly',  -- Placeholder - update after Stripe product creation
  '{
    "ai_runs": 10000,
    "cms_items": 50,
    "users": 10,
    "storage_mb": 5000,
    "api_calls_per_day": 50000,
    "overage_ai_run_cents": 10
  }'::JSONB,
  '[
    "Advanced AI agents",
    "Priority support",
    "CMS approval workflows",
    "Scheduled publishing",
    "Team collaboration",
    "API access",
    "Usage-based billing"
  ]'::JSONB,
  TRUE
)
ON CONFLICT (name) DO UPDATE SET
  display_name = EXCLUDED.display_name,
  price_monthly_cents = EXCLUDED.price_monthly_cents,
  stripe_price_id = EXCLUDED.stripe_price_id,
  limits = EXCLUDED.limits,
  features = EXCLUDED.features,
  is_active = EXCLUDED.is_active,
  updated_at = NOW();

-- ====================
-- SEED ENTERPRISE PLAN (Placeholder for Future)
-- ====================

INSERT INTO plans (
  name,
  display_name,
  price_monthly_cents,
  stripe_price_id,
  limits,
  features,
  is_active
)
VALUES (
  'enterprise',
  'Enterprise Plan',
  NULL,  -- Custom pricing
  NULL,  -- Custom Stripe setup
  '{
    "ai_runs": -1,
    "cms_items": -1,
    "users": -1,
    "storage_mb": -1,
    "api_calls_per_day": -1
  }'::JSONB,
  '[
    "Unlimited everything",
    "Dedicated support",
    "Custom integrations",
    "SLA guarantees",
    "On-premise deployment option",
    "Advanced security features"
  ]'::JSONB,
  FALSE  -- Not active for MVP
)
ON CONFLICT (name) DO UPDATE SET
  display_name = EXCLUDED.display_name,
  limits = EXCLUDED.limits,
  features = EXCLUDED.features,
  is_active = EXCLUDED.is_active,
  updated_at = NOW();

-- ====================
-- HELPER FUNCTIONS
-- ====================

-- Function to check if org usage is within limits
CREATE OR REPLACE FUNCTION check_entitlement(
  p_org_id UUID,
  p_limit_type TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_plan_limits JSONB;
  v_current_usage INTEGER;
  v_limit INTEGER;
  v_plan_name TEXT;
  v_allowed BOOLEAN;
BEGIN
  -- Get org's current plan and limits
  SELECT p.name, p.limits
  INTO v_plan_name, v_plan_limits
  FROM subscriptions s
  JOIN plans p ON s.plan_id = p.id
  WHERE s.org_id = p_org_id
    AND s.status = 'active'
  LIMIT 1;

  -- If no subscription found, deny
  IF v_plan_limits IS NULL THEN
    RETURN jsonb_build_object(
      'allowed', FALSE,
      'current', 0,
      'max', 0,
      'plan', 'none',
      'message', 'No active subscription found'
    );
  END IF;

  -- Get limit for requested type
  v_limit := (v_plan_limits->>p_limit_type)::INTEGER;

  -- If limit is -1, it's unlimited (enterprise)
  IF v_limit = -1 THEN
    RETURN jsonb_build_object(
      'allowed', TRUE,
      'current', 0,
      'max', -1,
      'plan', v_plan_name,
      'message', 'Unlimited'
    );
  END IF;

  -- Get current usage from materialized view
  CASE p_limit_type
    WHEN 'ai_runs' THEN
      SELECT ai_runs_count INTO v_current_usage
      FROM org_usage_current
      WHERE org_id = p_org_id;
    WHEN 'cms_items' THEN
      SELECT cms_items_count INTO v_current_usage
      FROM org_usage_current
      WHERE org_id = p_org_id;
    WHEN 'users' THEN
      SELECT users_count INTO v_current_usage
      FROM org_usage_current
      WHERE org_id = p_org_id;
    WHEN 'storage_mb' THEN
      SELECT storage_usage_mb INTO v_current_usage
      FROM org_usage_current
      WHERE org_id = p_org_id;
    WHEN 'api_calls_per_day' THEN
      SELECT api_calls_count INTO v_current_usage
      FROM org_usage_current
      WHERE org_id = p_org_id;
    ELSE
      RAISE EXCEPTION 'Invalid limit_type: %', p_limit_type;
  END CASE;

  -- If no usage data, default to 0
  v_current_usage := COALESCE(v_current_usage, 0);

  -- Check if allowed
  v_allowed := v_current_usage < v_limit;

  RETURN jsonb_build_object(
    'allowed', v_allowed,
    'current', v_current_usage,
    'max', v_limit,
    'plan', v_plan_name,
    'message', CASE
      WHEN v_allowed THEN 'Within limits'
      ELSE format('Monthly %s limit reached (%s/%s). Upgrade to continue.', p_limit_type, v_current_usage, v_limit)
    END
  );
END;
$$;

COMMENT ON FUNCTION check_entitlement IS 'Check if org usage is within plan limits (used before billable operations)';

-- Function to get org's current plan details
CREATE OR REPLACE FUNCTION get_org_plan(p_org_id UUID)
RETURNS JSONB
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT jsonb_build_object(
    'plan_name', p.name,
    'display_name', p.display_name,
    'price_monthly_cents', p.price_monthly_cents,
    'limits', p.limits,
    'features', p.features,
    'subscription_status', s.status,
    'current_period_start', s.current_period_start,
    'current_period_end', s.current_period_end,
    'cancel_at_period_end', s.cancel_at_period_end
  )
  FROM subscriptions s
  JOIN plans p ON s.plan_id = p.id
  WHERE s.org_id = p_org_id
  LIMIT 1;
$$;

COMMENT ON FUNCTION get_org_plan IS 'Get org''s current plan details (used in billing dashboard)';

-- ============================================================================
-- GRANT EXECUTE ON FUNCTIONS
-- ============================================================================

GRANT EXECUTE ON FUNCTION check_entitlement(UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_org_plan(UUID) TO authenticated;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
