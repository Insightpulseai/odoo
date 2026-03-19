import path from "node:path";

export function getPaths() {
  const repoRoot = process.cwd();

  const taxonomy_path =
    process.env.AGENT_ROUTER_TAXONOMY ??
    path.join(repoRoot, "spec/taxonomy/capabilities_consulting_delivery.yaml");

  const matrix_path =
    process.env.AGENT_ROUTER_MATRIX ??
    path.join(repoRoot, "spec/agents/agent_capability_matrix.yaml");

  const prompts_dir =
    process.env.AGENT_ROUTER_PROMPTS_DIR ??
    path.join(repoRoot, "agent-library");

  return { taxonomy_path, matrix_path, prompts_dir };
}
