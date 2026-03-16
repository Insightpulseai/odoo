import { RunbookPlan, Env } from "./types";
import { makePlan } from "./runbooks";

const pickEnv = (s: string): Env => {
  const t = s.toLowerCase();
  if (t.includes("prod")) return "prod";
  if (t.includes("stag")) return "staging";
  return "dev";
};

export function planFromPrompt(prompt: string): RunbookPlan {
  const p = prompt.toLowerCase().trim();
  const env = pickEnv(p);

  if (p.includes("deploy")) return makePlan("deploy", { env });
  if (p.includes("check") || p.includes("status") || p.includes("health")) return makePlan("healthcheck", { env });
  if (p.includes("spec") || p.includes("prd") || p.includes("generate")) return makePlan("spec", { env });
  if (p.includes("fix") || p.includes("error") || p.includes("incident")) return makePlan("incident", { env });
  if (p.includes("schema") || p.includes("sync") || p.includes("migration")) return makePlan("schema_sync", { env });

  // default: healthcheck (safe)
  return makePlan("healthcheck", { env });
}
