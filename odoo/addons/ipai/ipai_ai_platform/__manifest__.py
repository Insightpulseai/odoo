{
    "name": "IPAI AI Platform",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "summary": "AI Platform HTTP Client for Supabase Edge Functions",
    "description": """
        AI Platform Integration Module
        ==============================

        Provides HTTP client for calling Supabase Edge Functions from Odoo backend.

        Features:
        - OpenAI API integration (fallback when Edge Functions unavailable)
        - Configurable via system parameters
        - Audit trail logging to cms_artifacts (if exists)
        - Usage tracking for billing limits
        - Multi-org context support

        Configuration:
        - ipai.supabase.url: Supabase project URL
        - ipai.supabase.service_role_key: Service role key for backend calls
        - ipai.org.id: Default organization UUID
        - ipai.openai.api_key: OpenAI API key (fallback)

        Phase 5A: SaaS Platform Kit - AI × Odoo Integration
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/config_parameters.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
