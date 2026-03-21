{
    "name": "IPAI LLM Supabase Bridge",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "summary": "Bridge between Apexive odoo-llm and Supabase SSOT control plane",
    "description": """
Emits LLM tool calls, assistant threads, and generation events from Odoo (SOR)
to Supabase (SSOT) via signed webhooks. Provides observability, audit trails,
and governance integration for the InsightPulse AI platform.

Key features:
- Hook into llm_tool execution pipeline → emit events to Supabase ops.run_events
- Log assistant thread lifecycle (create/message/complete) to ops.runs
- Dead-letter queue for failed webhook deliveries with exponential backoff
- Configurable webhook endpoint + HMAC signing
- Cron-based retry for DLQ items
- No write-back to Odoo-owned domains (respects SSOT/SOR doctrine)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "llm",            # Apexive core
        "llm_tool",       # Apexive tool framework
        "llm_assistant",  # Apexive assistants
        "llm_thread",     # Apexive chat threads
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ipai_llm_supabase_bridge_groups.xml",
        "data/ipai_llm_supabase_bridge_data.xml",
        "views/ipai_bridge_event_views.xml",
        "views/ipai_bridge_config_views.xml",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
