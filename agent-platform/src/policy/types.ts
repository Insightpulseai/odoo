export type Surface =
  | "public_site"
  | "prisma_playground"
  | "client_workspace"
  | "odoo_erp"
  | "admin_control";

export type Domain =
  | "research"
  | "finance"
  | "project_finance"
  | "sales"
  | "ops";

export type ExpertiseMode = "beginner" | "intermediate" | "expert";

export type UiMode =
  | "wizard"
  | "workbench"
  | "queue"
  | "cockpit"
  | "vault"
  | "operator";

export type Tone = "plain" | "guided" | "concise" | "operational";

export type CtaMode = "none" | "soft" | "contextual" | "service_handoff";

export interface BehaviorContext {
  surface: Surface;
  domain: Domain;
  expertiseMode: ExpertiseMode;
  roleGroups: string[];
  approvalBands?: string[];
  taskType?: string;
  riskLevel?: "low" | "medium" | "high";
}

export interface ResolvedBehavior {
  uiMode: UiMode;
  tone: Tone;
  allowedTools: string[];
  evidenceScope: string;
  allowedMutations: string[];
  exports: string[];
  ctaMode: CtaMode;
}
