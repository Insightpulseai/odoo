import path from "node:path";
import { z } from "zod";
import type {
  AgentCapabilityMatrix,
  CapabilityTaxonomy,
  RouterRequest,
  RouterResponse,
} from "./types.js";
import { getPaths } from "./config.js";
import { exists, readTextFile, readYamlFile } from "./io.js";
import { renderRelayPrompt } from "./relay.js";

const ReqSchema = z.object({
  capability: z.string().min(1),
  goal: z.string().min(1),
  context: z.unknown().optional(),
  constraints: z.string().nullable().optional(),
  preferred_agents: z.array(z.string()).optional(),
  exclude_agents: z.array(z.string()).optional(),
  mode: z
    .enum(["primary_only", "primary_plus_support", "full_relay"])
    .optional(),
});

export async function listCapabilities(): Promise<
  Array<{ id: string; title: string; domain: string }>
> {
  const { taxonomy_path } = getPaths();
  const taxonomy = await readYamlFile<CapabilityTaxonomy>(taxonomy_path);

  const out: Array<{ id: string; title: string; domain: string }> = [];
  for (const d of taxonomy.domains ?? []) {
    for (const c of d.capabilities ?? []) {
      out.push({ id: c.id, title: c.title, domain: d.id });
    }
  }
  return out.sort((a, b) => a.id.localeCompare(b.id));
}

export async function listAgentsForCapability(capability: string) {
  const { matrix_path } = getPaths();
  const matrix = await readYamlFile<AgentCapabilityMatrix>(matrix_path);
  const hit = matrix.routing.find((r) => r.capability === capability);
  if (!hit) return null;
  return {
    capability,
    primary_agents: hit.primary_agents ?? [],
    support_agents: hit.support_agents ?? [],
  };
}

function pickPrimary(params: {
  primary_agents: string[];
  preferred_agents?: string[];
  exclude_agents?: string[];
}) {
  const exclude = new Set(
    (params.exclude_agents ?? []).map((s) => s.trim()).filter(Boolean),
  );
  const preferred = new Set(
    (params.preferred_agents ?? []).map((s) => s.trim()).filter(Boolean),
  );

  // 1) Prefer any preferred agent that exists in primary list
  for (const a of params.primary_agents) {
    if (preferred.has(a) && !exclude.has(a))
      return { agent: a, reason: "preferred agent matched" };
  }

  // 2) First non-excluded primary agent
  for (const a of params.primary_agents) {
    if (!exclude.has(a))
      return { agent: a, reason: "first available primary agent" };
  }

  // 3) Fallback: even if excluded, pick first (deterministic) to avoid null routing
  return {
    agent: params.primary_agents[0] ?? "unknown",
    reason: "fallback primary agent (all excluded or empty)",
  };
}

async function loadAgentPrompt(
  promptsDir: string,
  agentName: string,
): Promise<{ path: string; md: string } | null> {
  // Convention: agents/library/**/<agentName>.md
  // Deterministic search order (fixed set) to avoid costly recursion.
  // If you want true recursive discovery, add a precomputed index file later.
  const candidates = [
    path.join(promptsDir, "odoo", `${agentName}.md`),
    path.join(promptsDir, "app", `${agentName}.md`),
    path.join(promptsDir, "web", `${agentName}.md`),
    path.join(promptsDir, "uiux", `${agentName}.md`),
    path.join(promptsDir, "_shared", `${agentName}.md`),
    path.join(promptsDir, `${agentName}.md`),
  ];

  for (const p of candidates) {
    if (await exists(p)) {
      return { path: p, md: await readTextFile(p) };
    }
  }
  return null;
}

export async function route(raw: unknown): Promise<RouterResponse> {
  const req = ReqSchema.parse(raw) as RouterRequest;
  const { taxonomy_path, matrix_path, prompts_dir } = getPaths();

  const taxonomy = await readYamlFile<CapabilityTaxonomy>(taxonomy_path);
  const matrix = await readYamlFile<AgentCapabilityMatrix>(matrix_path);

  const capExists = taxonomy.domains
    .flatMap((d) => d.capabilities.map((c) => c.id))
    .includes(req.capability);

  if (!capExists) {
    throw new Error(
      `Unknown capability: ${req.capability}. Add it to taxonomy YAML or fix the request.`,
    );
  }

  const hit = matrix.routing.find((r) => r.capability === req.capability);
  if (!hit) {
    throw new Error(
      `No routing entry for capability: ${req.capability}. Add it to agent matrix YAML.`,
    );
  }

  const pick = pickPrimary({
    primary_agents: hit.primary_agents ?? [],
    preferred_agents: req.preferred_agents,
    exclude_agents: req.exclude_agents,
  });

  const supportAgents = (hit.support_agents ?? []).filter(
    (a) => !(req.exclude_agents ?? []).includes(a),
  );

  const promptLoaded = await loadAgentPrompt(prompts_dir, pick.agent);
  const promptSource = promptLoaded?.path ?? null;
  const agentPromptMd = promptLoaded?.md ?? null;

  const constraints =
    (req.constraints ?? "").trim() ||
    "No UI steps; use shell/scripts/configs/APIs; idempotent; surface unknown paths/names as TODOs.";

  const mode = req.mode ?? "full_relay";
  const relay = renderRelayPrompt({
    role: `${pick.agent} (routed by capability=${req.capability})`,
    goal: req.goal,
    constraints,
    context: req.context ?? {},
    selected_primary_agent: pick.agent,
    support_agents: mode === "primary_only" ? [] : supportAgents,
    agent_prompt_md: mode === "full_relay" ? agentPromptMd : null,
  });

  return {
    capability: req.capability,
    primary_agent: pick.agent,
    support_agents: mode === "primary_only" ? [] : supportAgents,
    prompt_source: promptSource,
    relay_prompt: relay,
    diagnostics: {
      taxonomy_path,
      matrix_path,
      prompts_dir,
      selection_reason: pick.reason,
    },
  };
}
