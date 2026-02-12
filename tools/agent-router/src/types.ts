export type CapabilityTaxonomy = {
  version: number;
  kind: "capability_taxonomy";
  id: string;
  title: string;
  domains: Array<{
    id: string;
    title: string;
    capabilities: Array<{
      id: string;
      title: string;
      outcomes?: string[];
    }>;
  }>;
};

export type AgentCapabilityMatrix = {
  version: number;
  kind: "agent_capability_matrix";
  id: string;
  title: string;
  routing: Array<{
    capability: string;
    primary_agents: string[];
    support_agents?: string[];
  }>;
};

export type RouterRequest = {
  capability: string;
  goal: string;
  context?: unknown;
  constraints?: string | null;
  preferred_agents?: string[];
  exclude_agents?: string[];
  mode?: "primary_only" | "primary_plus_support" | "full_relay";
};

export type RouterResponse = {
  capability: string;
  primary_agent: string;
  support_agents: string[];
  prompt_source: string | null;
  relay_prompt: string;
  diagnostics: {
    taxonomy_path: string;
    matrix_path: string;
    prompts_dir: string;
    selection_reason: string;
    [k: string]: unknown;
  };
};
