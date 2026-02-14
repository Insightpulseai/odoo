export const AgentFlows = {
  CMS_HOMEPAGE: "cms_homepage_pipeline",
  SUPPORT: "support_response_pipeline",
  ODOO: "odoo_workflow_pipeline",
} as const;

export type AgentFlowName = typeof AgentFlows[keyof typeof AgentFlows];

export const AgentNames = [
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
] as const;

export type AgentName = typeof AgentNames[number];
