# Microsoft 365 Agents SDK

> Source: github.com/microsoft/Agents

## What it is

The Microsoft 365 Agents SDK for building multichannel agent "containers" — making agents available in Teams, M365 Copilot, and web/custom applications. This is the **channel delivery layer** — not the core orchestration framework, not a developer assistant, not an external platform connector.

## Key Capabilities

| Capability | Description |
|-----------|-------------|
| Teams channel | Deploy agents as Teams apps with rich card support, adaptive cards, task modules |
| M365 Copilot channel | Extend M365 Copilot with custom agent plugins and declarative agents |
| Web/custom app channel | Embed agents in web applications and custom frontends via Direct Line or WebSocket |
| Activity handling | Process incoming activities (messages, events, invokes) with typed handlers |
| State management | Conversation state, user state, and turn state with pluggable storage (memory, blob, cosmos) |
| Auth integration | Entra ID token validation, SSO, user identity propagation to backend services |
| Azure AI Foundry backend | Core agent functionality powered by Azure AI Foundry — the channel SDK is a delivery surface |

## Role in Our Stack

**Channel delivery/container layer for agent surfaces.**

Use this when you need to:
- Deploy an agent to Microsoft Teams
- Create an M365 Copilot extension
- Embed an agent in a web application
- Handle channel-specific activity patterns and state
- Integrate with Entra ID for user authentication

## What it is NOT

| Misuse | Correct layer |
|--------|--------------|
| Core agent orchestration (workflows, graphs) | Microsoft Agent Framework (`microsoft/agent-framework`) |
| Developer coding assistant | GitHub Copilot SDK (`github/copilot-sdk`) |
| External platform connector (Palantir) | Palantir Foundry SDK (`palantir/foundry-platform-python`) |

## Architecture Position

```
Microsoft Agent Framework    (orchestration) -- builds the agent logic
        |
        v
Microsoft 365 Agents SDK  <-- THIS (channel delivery) -- delivers to users
GitHub Copilot SDK          (developer assistance)
Palantir Foundry SDK        (external integration, optional)
```

The M365 Agents SDK is a delivery surface. The actual agent intelligence comes from Azure AI Foundry (backend) or from agents built with the Microsoft Agent Framework. The channel SDK handles activity routing, state, auth, and channel-specific packaging.

## Key Design Patterns

1. **Activity Handler**: Route incoming activities to typed handlers. Messages, events, and invokes each have distinct processing paths.
2. **State Separation**: Keep conversation state (shared across a conversation), user state (per-user across conversations), and turn state (single turn) in separate stores.
3. **Auth Flow**: Validate Entra ID tokens at the channel boundary. Propagate user identity claims to backend services via bearer tokens.
4. **Channel Packaging**: Each target channel has specific manifest and packaging requirements. Teams needs a Teams app package. M365 Copilot needs a declarative agent manifest.

## Critical Distinction

Azure AI Foundry provides the core backend agent functionality. The M365 Agents SDK is the channel container that delivers that functionality to end users. Do not implement agent logic (LLM calls, tool execution, reasoning) in the channel layer.

## Cross-References

- Persona: `agents/personas/m365-channel-agent.md`
- Skill: `agents/skills/m365-agents-channel-delivery/`
- Skill map: `agent-platform/ssot/learning/agent_sdk_stack_map.yaml`
