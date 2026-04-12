import type { BehaviorContext, ResolvedBehavior } from "./types";

type RolePolicy = {
  evidence_scope: string;
  allowed_mutations: string[];
  allowed_exports: string[];
};

type MatrixRule = {
  match: Partial<{
    surface: string;
    domain: string;
    expertise_mode: string;
    role_groups: string[];
  }>;
  resolve: Partial<{
    ui_mode: ResolvedBehavior["uiMode"];
    tone: ResolvedBehavior["tone"];
    allowed_tools: string[];
    allowed_mutations: string[];
    exports: string[];
    cta_mode: ResolvedBehavior["ctaMode"];
  }>;
};

type PolicyBundle = {
  roleGroups: Record<string, RolePolicy>;
  matrixRules: MatrixRule[];
};

export function resolveBehavior(
  ctx: BehaviorContext,
  bundle: PolicyBundle,
): ResolvedBehavior {
  const rolePolicies = ctx.roleGroups
    .map((group) => bundle.roleGroups[group])
    .filter(Boolean);

  const evidenceScope =
    rolePolicies[0]?.evidence_scope ??
    (ctx.surface === "public_site" ? "public_only" : "tenant_project_scoped");

  const mergedRoleMutations = Array.from(
    new Set(rolePolicies.flatMap((p) => p.allowed_mutations ?? [])),
  );

  const mergedRoleExports = Array.from(
    new Set(rolePolicies.flatMap((p) => p.allowed_exports ?? [])),
  );

  const matchingRules = bundle.matrixRules.filter((rule) => {
    const m = rule.match;

    if (m.surface && m.surface !== ctx.surface) return false;
    if (m.domain && m.domain !== ctx.domain) return false;
    if (m.expertise_mode && m.expertise_mode !== ctx.expertiseMode) return false;

    if (m.role_groups?.length) {
      const hasAny = m.role_groups.some((g) => ctx.roleGroups.includes(g));
      if (!hasAny) return false;
    }

    return true;
  });

  const merged = matchingRules.reduce(
    (acc, rule) => ({
      ...acc,
      ...rule.resolve,
      allowed_tools: Array.from(
        new Set([...(acc.allowed_tools ?? []), ...(rule.resolve.allowed_tools ?? [])]),
      ),
      allowed_mutations: Array.from(
        new Set([
          ...(acc.allowed_mutations ?? []),
          ...(rule.resolve.allowed_mutations ?? []),
        ]),
      ),
      exports: Array.from(
        new Set([...(acc.exports ?? []), ...(rule.resolve.exports ?? [])]),
      ),
    }),
    {} as MatrixRule["resolve"],
  );

  return {
    uiMode: merged.ui_mode ?? defaultUiMode(ctx),
    tone: merged.tone ?? defaultTone(ctx),
    allowedTools: merged.allowed_tools ?? [],
    evidenceScope,
    allowedMutations: Array.from(
      new Set([...(merged.allowed_mutations ?? []), ...mergedRoleMutations]),
    ),
    exports: Array.from(new Set([...(merged.exports ?? []), ...mergedRoleExports])),
    ctaMode: merged.cta_mode ?? defaultCtaMode(ctx),
  };
}

function defaultUiMode(ctx: BehaviorContext): ResolvedBehavior["uiMode"] {
  if (ctx.surface === "odoo_erp") return "cockpit";
  if (ctx.surface === "admin_control") return "operator";
  if (ctx.surface === "prisma_playground") return "workbench";
  return "wizard";
}

function defaultTone(ctx: BehaviorContext): ResolvedBehavior["tone"] {
  if (ctx.domain === "finance" || ctx.domain === "ops") return "operational";
  if (ctx.expertiseMode === "beginner") return "plain";
  if (ctx.expertiseMode === "expert") return "concise";
  return "guided";
}

function defaultCtaMode(ctx: BehaviorContext): ResolvedBehavior["ctaMode"] {
  if (ctx.surface === "odoo_erp" || ctx.surface === "admin_control") return "none";
  if (ctx.surface === "public_site") return "soft";
  return "contextual";
}
