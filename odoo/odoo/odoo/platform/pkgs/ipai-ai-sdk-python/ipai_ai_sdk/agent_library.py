from typing import Literal

AgentFlowName = Literal[
    "cms_homepage_pipeline",
    "support_response_pipeline",
    "odoo_workflow_pipeline",
]

AgentName = Literal[
    "intent_router",
    "cms_brief_to_sections",
    "cms_section_generator",
    "cms_seo_pack",
    "publish_check",
    "support_triage",
    "support_draft",
    "policy_safety_check",
    "odoo_action_plan",
    "odoo_action_payload",
]
