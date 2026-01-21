-- Supabase Migration: Odoo Catalogs Schema
-- Generated: 2026-01-21
-- Purpose: Catalog tables for Odoo module/capability discovery by agents

-- =============================================================================
-- Capabilities Catalog
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.odoo_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_key TEXT NOT NULL UNIQUE,
    capability_name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    requires_modules TEXT[] DEFAULT '{}',
    requires_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_capabilities_category ON public.odoo_capabilities(category);
CREATE INDEX IF NOT EXISTS idx_capabilities_active ON public.odoo_capabilities(is_active);

COMMENT ON TABLE public.odoo_capabilities IS 'Catalog of platform capabilities for agent discovery';
COMMENT ON COLUMN public.odoo_capabilities.capability_key IS 'Unique identifier for the capability';
COMMENT ON COLUMN public.odoo_capabilities.requires_modules IS 'Odoo modules required for this capability';
COMMENT ON COLUMN public.odoo_capabilities.requires_config IS 'Configuration requirements (env vars, settings)';

-- =============================================================================
-- Module Install Catalog
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.odoo_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_name TEXT NOT NULL UNIQUE,
    display_name TEXT,
    category TEXT,
    source TEXT CHECK (source IN ('ce', 'oca', 'ipai', 'community')),
    version TEXT,
    depends TEXT[] DEFAULT '{}',
    install_command TEXT,
    ci_job TEXT,
    is_installed BOOLEAN DEFAULT false,
    installed_version TEXT,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_modules_source ON public.odoo_modules(source);
CREATE INDEX IF NOT EXISTS idx_modules_installed ON public.odoo_modules(is_installed);
CREATE INDEX IF NOT EXISTS idx_modules_category ON public.odoo_modules(category);

COMMENT ON TABLE public.odoo_modules IS 'Catalog of Odoo modules and their installation status';
COMMENT ON COLUMN public.odoo_modules.source IS 'Module source: ce=Odoo CE, oca=OCA, ipai=custom, community=other';

-- =============================================================================
-- Design System Languages Catalog
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.design_system_languages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    language_key TEXT NOT NULL UNIQUE,
    language_name TEXT NOT NULL,
    framework TEXT NOT NULL,
    tokens_url TEXT,
    css_url TEXT,
    npm_package TEXT,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_design_languages_active ON public.design_system_languages(is_active);
CREATE INDEX IF NOT EXISTS idx_design_languages_framework ON public.design_system_languages(framework);

COMMENT ON TABLE public.design_system_languages IS 'Catalog of supported design system languages for agent UI generation';

-- =============================================================================
-- Seed Design Systems
-- =============================================================================

INSERT INTO public.design_system_languages
    (language_key, language_name, framework, npm_package, config)
VALUES
    ('fluent-ui', 'Microsoft Fluent UI', 'react', '@fluentui/react-components', '{"theme": "webLight"}'),
    ('mui', 'Material UI', 'react', '@mui/material', '{"mode": "light"}'),
    ('tailwind', 'Tailwind CSS', 'utility-first', 'tailwindcss', '{"preset": "default"}'),
    ('shadcn', 'shadcn/ui', 'react', 'shadcn-ui', '{"style": "new-york"}'),
    ('ipai-tokens', 'IPAI Design Tokens', 'custom', '@ipai/design-tokens', '{"brand": "insightpulse"}'),
    ('bootstrap', 'Bootstrap', 'vanilla', 'bootstrap', '{"version": "5.3"}'),
    ('chakra', 'Chakra UI', 'react', '@chakra-ui/react', '{"colorMode": "light"}')
ON CONFLICT (language_key) DO NOTHING;

-- =============================================================================
-- Seed Capabilities
-- =============================================================================

INSERT INTO public.odoo_capabilities
    (capability_key, capability_name, description, category, requires_modules, requires_config)
VALUES
    ('email_outbound', 'Outbound Email', 'Send transactional and marketing emails', 'communication',
     ARRAY['mail', 'mass_mailing'], '{"smtp_host": "required", "smtp_user": "required"}'),
    ('email_oauth_google', 'Gmail OAuth Integration', 'Connect Gmail via OAuth for email sync', 'communication',
     ARRAY['auth_oauth', 'google_drive', 'ipai_mail_integration'], '{"google_client_id": "required"}'),
    ('email_oauth_microsoft', 'Outlook 365 OAuth Integration', 'Connect Outlook via OAuth for email sync', 'communication',
     ARRAY['auth_oauth', 'ipai_mail_integration'], '{"azure_client_id": "required", "azure_tenant_id": "required"}'),
    ('iot_printing', 'IoT Printing', 'Print to network and CUPS printers', 'hardware',
     ARRAY['base_report_to_printer', 'ipai_iot_bridge'], '{}'),
    ('iot_scale', 'IoT Scale', 'Read weight from connected scales', 'hardware',
     ARRAY['ipai_iot_bridge'], '{}'),
    ('iot_scanner', 'IoT Barcode Scanner', 'Read barcodes from connected scanners', 'hardware',
     ARRAY['ipai_iot_bridge'], '{}'),
    ('cloud_storage', 'S3 Cloud Storage', 'Store attachments in S3-compatible storage', 'storage',
     ARRAY['attachment_s3'], '{"s3_bucket": "required", "s3_access_key": "required"}'),
    ('geolocation', 'Partner Geolocation', 'Geocode partner addresses', 'integrations',
     ARRAY['base_geolocalize'], '{}'),
    ('translation', 'Auto-Translation', 'Translate content via LibreTranslate or Google', 'integrations',
     ARRAY['ipai_enterprise_bridge'], '{"translate_provider": "optional"}'),
    ('sms_gateway', 'SMS Messaging', 'Send SMS via Twilio/Vonage', 'communication',
     ARRAY['ipai_sms_gateway'], '{"twilio_account_sid": "required"}'),
    ('ocr_extraction', 'Document OCR', 'Extract data from invoices/receipts', 'ai',
     ARRAY['ipai_ocr_gateway'], '{"ocr_provider": "required"}'),
    ('helpdesk', 'Helpdesk Ticketing', 'Manage support tickets with SLA', 'service',
     ARRAY['helpdesk_mgmt'], '{}'),
    ('workos', 'WorkOS Knowledge Base', 'Notion-like collaborative workspace', 'productivity',
     ARRAY['ipai_workos_core', 'ipai_workos_blocks'], '{}'),
    ('finance_ppm', 'Finance PPM', 'Project portfolio management for finance', 'finance',
     ARRAY['ipai_finance_ppm'], '{}'),
    ('bir_compliance', 'BIR Tax Compliance', 'Philippine BIR tax reporting', 'compliance',
     ARRAY['ipai_bir_tax_compliance'], '{}'),
    ('month_end_close', 'Month-End Close', 'Automated month-end closing workflows', 'finance',
     ARRAY['ipai_close_orchestration'], '{}')
ON CONFLICT (capability_key) DO NOTHING;

-- =============================================================================
-- Row Level Security
-- =============================================================================

ALTER TABLE public.odoo_capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.odoo_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.design_system_languages ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Allow read odoo_capabilities"
    ON public.odoo_capabilities FOR SELECT USING (true);
CREATE POLICY "Allow read odoo_modules"
    ON public.odoo_modules FOR SELECT USING (true);
CREATE POLICY "Allow read design_system_languages"
    ON public.design_system_languages FOR SELECT USING (true);

-- Service role write access
CREATE POLICY "Service role write capabilities"
    ON public.odoo_capabilities FOR ALL
    USING (auth.role() = 'service_role');
CREATE POLICY "Service role write modules"
    ON public.odoo_modules FOR ALL
    USING (auth.role() = 'service_role');
CREATE POLICY "Service role write design_languages"
    ON public.design_system_languages FOR ALL
    USING (auth.role() = 'service_role');

-- =============================================================================
-- Updated At Trigger
-- =============================================================================

CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_capabilities_updated_at
    BEFORE UPDATE ON public.odoo_capabilities
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
