-- ============================================================================
-- Migration: Billing Tables RLS Policies
-- Created: 2026-02-11
-- Phase: 1 - Core SaaS Primitives
-- Purpose: Multi-tenant security enforcement for billing tables
-- ============================================================================

-- ====================
-- ENABLE RLS
-- ====================

ALTER TABLE billing_customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_events ENABLE ROW LEVEL SECURITY;

-- ====================
-- BILLING_CUSTOMERS POLICIES
-- ====================

-- Users can view own org's billing customer
CREATE POLICY "Users can view own org billing customer"
  ON billing_customers FOR SELECT
  USING (
    org_id IN (
      SELECT org_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Service role can manage all billing customers
CREATE POLICY "Service role can manage all billing customers"
  ON billing_customers FOR ALL
  USING (auth.jwt()->>'role' = 'service_role');

-- Authenticated users cannot insert/update/delete billing customers
-- (Only service role via Stripe webhook)
CREATE POLICY "Block user modifications to billing customers"
  ON billing_customers FOR INSERT
  WITH CHECK (FALSE);

CREATE POLICY "Block user updates to billing customers"
  ON billing_customers FOR UPDATE
  USING (FALSE);

CREATE POLICY "Block user deletes to billing customers"
  ON billing_customers FOR DELETE
  USING (FALSE);

-- ====================
-- PLANS POLICIES
-- ====================

-- All authenticated users can view plans (public catalog)
CREATE POLICY "All users can view plans"
  ON plans FOR SELECT
  TO authenticated
  USING (is_active = TRUE);

-- Service role can manage plans
CREATE POLICY "Service role can manage all plans"
  ON plans FOR ALL
  USING (auth.jwt()->>'role' = 'service_role');

-- Block user modifications
CREATE POLICY "Block user modifications to plans"
  ON plans FOR INSERT
  WITH CHECK (FALSE);

CREATE POLICY "Block user updates to plans"
  ON plans FOR UPDATE
  USING (FALSE);

CREATE POLICY "Block user deletes to plans"
  ON plans FOR DELETE
  USING (FALSE);

-- ====================
-- SUBSCRIPTIONS POLICIES
-- ====================

-- Users can view own org's subscription
CREATE POLICY "Users can view own org subscription"
  ON subscriptions FOR SELECT
  USING (
    org_id IN (
      SELECT org_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Service role can manage all subscriptions
CREATE POLICY "Service role can manage all subscriptions"
  ON subscriptions FOR ALL
  USING (auth.jwt()->>'role' = 'service_role');

-- Block user modifications (managed via Stripe webhook)
CREATE POLICY "Block user modifications to subscriptions"
  ON subscriptions FOR INSERT
  WITH CHECK (FALSE);

CREATE POLICY "Block user updates to subscriptions"
  ON subscriptions FOR UPDATE
  USING (FALSE);

CREATE POLICY "Block user deletes to subscriptions"
  ON subscriptions FOR DELETE
  USING (FALSE);

-- ====================
-- USAGE_EVENTS POLICIES
-- ====================

-- Users can view own org's usage events
CREATE POLICY "Users can view own org usage events"
  ON usage_events FOR SELECT
  USING (
    org_id IN (
      SELECT org_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Service role can manage all usage events
CREATE POLICY "Service role can manage all usage events"
  ON usage_events FOR ALL
  USING (auth.jwt()->>'role' = 'service_role');

-- Authenticated users can insert usage events for their own org
CREATE POLICY "Users can insert usage events for own org"
  ON usage_events FOR INSERT
  WITH CHECK (
    org_id IN (
      SELECT org_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Block user updates/deletes (usage events are immutable)
CREATE POLICY "Block user updates to usage events"
  ON usage_events FOR UPDATE
  USING (FALSE);

CREATE POLICY "Block user deletes to usage events"
  ON usage_events FOR DELETE
  USING (FALSE);

-- ====================
-- SERVICE ROLE AUDIT LOG
-- ====================

CREATE TABLE IF NOT EXISTS service_role_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operation TEXT NOT NULL,
  table_name TEXT NOT NULL,
  record_id UUID,
  justification TEXT NOT NULL,
  performed_by TEXT,
  performed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE service_role_audit_log IS 'Audit trail for service role operations (security compliance)';

CREATE INDEX idx_service_role_audit_table ON service_role_audit_log(table_name);
CREATE INDEX idx_service_role_audit_performed_at ON service_role_audit_log(performed_at DESC);

-- ====================
-- RLS TESTING HELPER FUNCTIONS
-- ====================

-- Function to test cross-org access (security validation)
CREATE OR REPLACE FUNCTION test_rls_cross_org_access(
  p_user_id UUID,
  p_user_org_id UUID,
  p_other_org_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_billing_customers_count INTEGER;
  v_subscriptions_count INTEGER;
  v_usage_events_count INTEGER;
  v_result JSONB;
BEGIN
  -- Set auth context to user
  PERFORM set_config('request.jwt.claims', json_build_object('sub', p_user_id::TEXT)::TEXT, TRUE);

  -- Attempt to query other org's billing customers
  SELECT COUNT(*) INTO v_billing_customers_count
  FROM billing_customers
  WHERE org_id = p_other_org_id;

  -- Attempt to query other org's subscriptions
  SELECT COUNT(*) INTO v_subscriptions_count
  FROM subscriptions
  WHERE org_id = p_other_org_id;

  -- Attempt to query other org's usage events
  SELECT COUNT(*) INTO v_usage_events_count
  FROM usage_events
  WHERE org_id = p_other_org_id;

  v_result := jsonb_build_object(
    'test_name', 'Cross-org access test',
    'user_id', p_user_id,
    'user_org_id', p_user_org_id,
    'attempted_org_id', p_other_org_id,
    'billing_customers_visible', v_billing_customers_count,
    'subscriptions_visible', v_subscriptions_count,
    'usage_events_visible', v_usage_events_count,
    'expected_all_zero', TRUE,
    'test_passed', (v_billing_customers_count = 0 AND v_subscriptions_count = 0 AND v_usage_events_count = 0),
    'tested_at', NOW()
  );

  RETURN v_result;
END;
$$;

COMMENT ON FUNCTION test_rls_cross_org_access IS 'Security test: Verify RLS blocks cross-org access (should return all zeros)';

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant usage on tables to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT ON plans TO authenticated;
GRANT SELECT ON billing_customers TO authenticated;
GRANT SELECT ON subscriptions TO authenticated;
GRANT SELECT, INSERT ON usage_events TO authenticated;

-- Grant all on materialized view to authenticated (read-only)
GRANT SELECT ON org_usage_current TO authenticated;

-- Service role already has full access via SECURITY DEFINER functions

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
