import type { FoundryAdapterConfig, FoundryAgentEnsureResult } from '../../contracts/foundry';

type ProjectsClientLike = {
  agents: {
    getAgent?: (agentId: string) => Promise<{ id: string }>;
    createAgent?: (input: Record<string, unknown>) => Promise<{ id: string }>;
    listAgents?: () => AsyncIterable<{ id: string; name?: string }>;
  };
};

export async function ensureDesignerAgent(
  client: ProjectsClientLike,
  config: FoundryAdapterConfig
): Promise<FoundryAgentEnsureResult> {
  // Path 1: explicit agent ID — reuse directly
  if (config.agentId && client.agents.getAgent) {
    const existing = await client.agents.getAgent(config.agentId);
    return {
      agentId: existing.id,
      reused: true,
    };
  }

  // Path 2: search by name
  if (client.agents.listAgents) {
    for await (const agent of client.agents.listAgents()) {
      if (agent.name === config.agentName) {
        return {
          agentId: agent.id,
          reused: true,
        };
      }
    }
  }

  // Path 3: create new agent
  if (!client.agents.createAgent) {
    throw new Error('Foundry client does not support createAgent');
  }

  const created = await client.agents.createAgent({
    name: config.agentName,
    instructions: [
      'You are a Fluent UI Designer Agent.',
      'Return structured JSON only.',
      'Prefer Microsoft-native Fluent UI React v9 composition.',
      'Preserve accessible hierarchy and restrained enterprise tone.',
    ].join(' '),
    model: config.modelDeploymentName,
  });

  return {
    agentId: created.id,
    reused: false,
  };
}
