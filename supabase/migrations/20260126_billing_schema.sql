-- Billing Schema for InsightPulse AI
-- Stores customer, subscription, and invoice data from Paddle webhooks

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create billing schema
CREATE SCHEMA IF NOT EXISTS billing;

-- Customers table (synced from Paddle)
CREATE TABLE IF NOT EXISTS billing.customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paddle_customer_id TEXT UNIQUE NOT NULL,
    supabase_user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    email TEXT NOT NULL,
    name TEXT,
    company_name TEXT,
    country_code TEXT,
    vat_number TEXT,
    odoo_partner_id INTEGER, -- Foreign key to Odoo res.partner (stored as integer)
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Organizations table (for multi-tenant support)
CREATE TABLE IF NOT EXISTS billing.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    owner_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES billing.customers(id) ON DELETE SET NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Organization members
CREATE TABLE IF NOT EXISTS billing.organization_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES billing.organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, user_id)
);

-- Subscriptions table (synced from Paddle)
CREATE TABLE IF NOT EXISTS billing.subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paddle_subscription_id TEXT UNIQUE NOT NULL,
    customer_id UUID REFERENCES billing.customers(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES billing.organizations(id) ON DELETE SET NULL,
    status TEXT NOT NULL CHECK (status IN ('trialing', 'active', 'paused', 'past_due', 'canceled')),
    plan_name TEXT NOT NULL,
    price_id TEXT NOT NULL,
    product_id TEXT,
    currency_code TEXT DEFAULT 'USD',
    unit_price_amount INTEGER, -- in cents
    quantity INTEGER DEFAULT 1,
    billing_cycle_interval TEXT CHECK (billing_cycle_interval IN ('day', 'week', 'month', 'year')),
    billing_cycle_frequency INTEGER DEFAULT 1,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    canceled_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoices table (synced from Paddle)
CREATE TABLE IF NOT EXISTS billing.invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paddle_invoice_id TEXT UNIQUE,
    paddle_transaction_id TEXT UNIQUE NOT NULL,
    customer_id UUID REFERENCES billing.customers(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES billing.subscriptions(id) ON DELETE SET NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'ready', 'billed', 'paid', 'canceled', 'past_due')),
    currency_code TEXT DEFAULT 'USD',
    subtotal INTEGER, -- in cents
    tax INTEGER DEFAULT 0,
    total INTEGER NOT NULL,
    invoice_number TEXT,
    invoice_url TEXT,
    billed_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhook events log (for debugging and replay)
CREATE TABLE IF NOT EXISTS billing.webhook_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON billing.customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_supabase_user_id ON billing.customers(supabase_user_id);
CREATE INDEX IF NOT EXISTS idx_customers_paddle_customer_id ON billing.customers(paddle_customer_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer_id ON billing.subscriptions(customer_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON billing.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_invoices_customer_id ON billing.invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_event_type ON billing.webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_events_processed ON billing.webhook_events(processed) WHERE NOT processed;

-- Updated at trigger function
CREATE OR REPLACE FUNCTION billing.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to all tables
CREATE TRIGGER customers_updated_at
    BEFORE UPDATE ON billing.customers
    FOR EACH ROW EXECUTE FUNCTION billing.update_updated_at();

CREATE TRIGGER organizations_updated_at
    BEFORE UPDATE ON billing.organizations
    FOR EACH ROW EXECUTE FUNCTION billing.update_updated_at();

CREATE TRIGGER subscriptions_updated_at
    BEFORE UPDATE ON billing.subscriptions
    FOR EACH ROW EXECUTE FUNCTION billing.update_updated_at();

CREATE TRIGGER invoices_updated_at
    BEFORE UPDATE ON billing.invoices
    FOR EACH ROW EXECUTE FUNCTION billing.update_updated_at();

-- Row Level Security Policies
ALTER TABLE billing.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.webhook_events ENABLE ROW LEVEL SECURITY;

-- Customers: users can only see their own customer record
CREATE POLICY customers_select_own ON billing.customers
    FOR SELECT USING (supabase_user_id = auth.uid());

-- Organizations: members can view their organizations
CREATE POLICY organizations_select_member ON billing.organizations
    FOR SELECT USING (
        id IN (
            SELECT organization_id FROM billing.organization_members
            WHERE user_id = auth.uid()
        )
    );

-- Organization members: can view their own memberships
CREATE POLICY organization_members_select_own ON billing.organization_members
    FOR SELECT USING (user_id = auth.uid());

-- Subscriptions: users can see subscriptions for their customer or organization
CREATE POLICY subscriptions_select_own ON billing.subscriptions
    FOR SELECT USING (
        customer_id IN (
            SELECT id FROM billing.customers WHERE supabase_user_id = auth.uid()
        )
        OR organization_id IN (
            SELECT organization_id FROM billing.organization_members WHERE user_id = auth.uid()
        )
    );

-- Invoices: users can see invoices for their customer
CREATE POLICY invoices_select_own ON billing.invoices
    FOR SELECT USING (
        customer_id IN (
            SELECT id FROM billing.customers WHERE supabase_user_id = auth.uid()
        )
    );

-- Service role can do everything (for webhooks)
CREATE POLICY customers_service_all ON billing.customers
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY organizations_service_all ON billing.organizations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY organization_members_service_all ON billing.organization_members
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY subscriptions_service_all ON billing.subscriptions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY invoices_service_all ON billing.invoices
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY webhook_events_service_all ON billing.webhook_events
    FOR ALL USING (auth.role() = 'service_role');

-- Helper function to get current user's subscription
CREATE OR REPLACE FUNCTION billing.get_current_subscription()
RETURNS TABLE (
    subscription_id UUID,
    status TEXT,
    plan_name TEXT,
    current_period_end TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.status,
        s.plan_name,
        s.current_period_end
    FROM billing.subscriptions s
    JOIN billing.customers c ON s.customer_id = c.id
    WHERE c.supabase_user_id = auth.uid()
    AND s.status IN ('active', 'trialing')
    ORDER BY s.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant usage on schema to authenticated users
GRANT USAGE ON SCHEMA billing TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA billing TO authenticated;
GRANT EXECUTE ON FUNCTION billing.get_current_subscription() TO authenticated;
