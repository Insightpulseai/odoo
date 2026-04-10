{
    "name": "IPAI Knowledge Bridge",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": "Cited knowledge retrieval via Azure AI Search hybrid bridge",
    "description": """
        Shared grounding substrate for all IPAI copilot surfaces.

        - Knowledge source registration (policies, procedures, checklists)
        - Hybrid vector + keyword search via Azure AI Search
        - Source-cited answers with confidence threshold
        - Abstain behavior when below confidence threshold
        - Query audit log with citation records

        Consumer modules: ipai_finance_close, ipai_taxpulse_bridge,
        ipai_pulser_assistant, ipai_ppm_bridge.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
    "data": [
        "security/knowledge_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "views/knowledge_source_views.xml",
        "views/knowledge_query_log_views.xml",
        "views/res_config_settings_views.xml",
        "views/knowledge_menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
