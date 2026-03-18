# m365-agents-channel-delivery

Package and deploy agents to M365 Copilot, Teams, and web channels using the Microsoft 365 Agents SDK.

## When to use
- New channel deployment for an existing agent
- Teams integration for agent surface
- M365 Copilot extension development
- Web widget setup for agent embedding

## Key rule
The channel layer delivers agents to users — it does not implement agent logic. Core agent functionality must come from Azure AI Foundry or from agents built with the Microsoft Agent Framework. Never implement reasoning, tool calls, or LLM interactions in the channel layer.

## Cross-references
- `agents/personas/m365-channel-agent.md`
- `agents/knowledge/benchmarks/microsoft-365-agents-sdk.md`
- `agent-platform/ssot/learning/agent_sdk_stack_map.yaml`
