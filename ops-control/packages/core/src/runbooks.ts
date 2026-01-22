import { RunbookKind, RunbookPlan, Env, Risk, Integration } from "./types";

const risksFor = (kind: RunbookKind, env: Env): Risk[] => {
  if (kind === "deploy" && env === "prod") {
    return [
      { level: "warn", code: "PROD_CHANGE", message: "Production deployment will modify live services." },
      { level: "warn", code: "DATABASE_MIGRATIONS", message: "Database migrations will be executed." },
      { level: "info", code: "POTENTIAL_DOWNTIME", message: "Brief downtime may occur during deployment." },
    ];
  }
  if (kind === "incident" && env === "prod") {
    return [
      { level: "warn", code: "PROD_INCIDENT", message: "Production incident - handle carefully." },
      { level: "info", code: "AUTO_PR", message: "Will create PR with proposed fix." },
    ];
  }
  if (kind === "schema_sync" && env === "prod") {
    return [
      { level: "block", code: "SCHEMA_DESTRUCTIVE", message: "Schema changes can be destructive." },
      { level: "warn", code: "DRY_RUN_FIRST", message: "Always dry run first." },
      { level: "warn", code: "VERIFY_MIGRATIONS", message: "Verify migrations before applying." },
    ];
  }
  return [{ level: "info", code: "IDEMPOTENT", message: "This action is designed to be safe to re-run." }];
};

const integrationsFor = (kind: RunbookKind): Integration[] => {
  switch (kind) {
    case "deploy":
      return ["GitHub", "Vercel", "Supabase"];
    case "healthcheck":
      return ["Supabase", "Vercel", "DigitalOcean"];
    case "spec":
      return ["GitHub"];
    case "incident":
      return ["Vercel", "GitHub", "Supabase"];
    case "schema_sync":
      return ["Supabase", "GitHub"];
  }
};

export function makePlan(kind: RunbookKind, { env }: { env: Env }): RunbookPlan {
  const base = {
    id: `${kind}_${Date.now()}`,
    kind,
    risks: risksFor(kind, env),
    integrations: integrationsFor(kind),
  };

  if (kind === "deploy") {
    return {
      ...base,
      title: "Deploy to production",
      summary: `Deploy ${env} environment (build, migrate, verify).`,
      inputs: [
        { key: "env", label: "Environment", type: "select", options: ["prod", "staging", "dev"], value: env },
        { key: "repo", label: "Repo", type: "text", value: "jgtolentino/odoo-ce" },
        { key: "target", label: "Target", type: "text", value: "vercel" },
        { key: "branch", label: "Branch", type: "text", value: "main" },
        { key: "runMigrations", label: "Run migrations", type: "boolean", value: true },
      ],
    };
  }

  if (kind === "healthcheck") {
    return {
      ...base,
      title: "Check prod status",
      summary: `Run health checks across all services for ${env} environment.`,
      inputs: [
        { key: "env", label: "Environment", type: "select", options: ["prod", "staging", "dev"], value: env },
      ],
    };
  }

  if (kind === "spec") {
    return {
      ...base,
      title: "Generate spec for dashboard",
      summary: "Generate Spec Kit bundle (constitution/prd/plan/tasks).",
      inputs: [
        { key: "repo", label: "Repo", type: "text", value: "jgtolentino/odoo-ce" },
        { key: "target", label: "Target", type: "text", value: "spec/ops-control-room" },
        { key: "notes", label: "Notes", type: "text", value: "Ops Control Room v1" },
      ],
    };
  }

  if (kind === "incident") {
    return {
      ...base,
      title: "Fix production error",
      summary: "Triage error, propose patch, open PR, run checks.",
      inputs: [
        { key: "env", label: "Environment", type: "select", options: ["prod", "staging", "dev"], value: env },
        { key: "notes", label: "Notes", type: "text", value: "Paste error snippet or link" },
      ],
    };
  }

  return {
    ...base,
    title: "Run schema sync",
    summary: "Introspect DB, generate ERD/DBML, create migrations.",
    inputs: [
      { key: "env", label: "Environment", type: "select", options: ["prod", "staging", "dev"], value: env },
      { key: "target", label: "Target", type: "text", value: "schema/exports" },
    ],
  };
}
