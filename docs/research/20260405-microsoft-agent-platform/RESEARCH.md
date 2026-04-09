# Microsoft Agent Platform Capabilities (April 2026) — Research Report

> **Purpose**: Map Microsoft's current agent platform capabilities to the IPAI Claude Code plugin architecture for an Odoo-on-Azure solo-builder stack.
> **Source classes**: `microsoft-learn-mcp` + web search (Microsoft Learn, DevBlogs, GitHub, IBM, CIO Dive)
> **Date**: 2026-04-05
> **Confidence**: HIGH (all 7 dimensions covered, primary sources verified)

---

## Executive Summary

Microsoft has consolidated its agent platform into three layers: **Microsoft Agent Framework** (open-source SDK, successor to Semantic Kernel + AutoGen), **Foundry Agent Service** (managed hosting/runtime, GA March 2026), and **Copilot Studio** (low-code autonomous agents). All three support MCP and A2A protocols. Identity governance is centralized through **Entra Agent ID** and the **Agent Registry**.

For our solo-builder Odoo-on-Azure stack running Claude Code as the primary agent runtime, the key takeaway is: **adopt the patterns and protocols (MCP, A2A, identity lifecycle, tool catalogs, guardrails), but skip the managed hosting layer** since Claude Code subagents with worktree isolation already provide equivalent orchestration without the cost/complexity of Foundry Agent Service.

---

## 1. Microsoft Foundry (formerly Azure AI Foundry)

### What It Is
Fully managed platform for building, deploying, and scaling AI agents. Handles hosting, scaling, identity, observability, and enterprise security. GA as of March 2026.

### Key Capabilities

| Feature | Status | Details |
|---------|--------|---------|
| **Agent types** | GA | Prompt agents (no-code), Workflow agents (YAML/visual, preview), Hosted agents (container-based, preview) |
| **Model support** | GA | GPT-4o, GPT-5.4-mini, Llama, DeepSeek, and Foundry model catalog |
| **Tool catalog** | GA | 1,400+ connectors via Azure Logic Apps, plus built-in: web search, file search, code interpreter, memory, MCP, A2A |
| **MCP Server** | Preview | Cloud-hosted at `mcp.ai.azure.com`, Entra auth, zero local infra |
| **A2A Tool** | Preview | Call any A2A-protocol endpoint with key/OAuth2/Entra auth |
| **Agent identity** | GA | Each agent gets a dedicated Entra identity when published |
| **Private networking** | GA | VNet isolation for prompt/workflow agents (not hosted agents yet) |
| **Observability** | GA | End-to-end tracing, Application Insights, agent metrics dashboards |
| **Publishing** | GA | Version snapshots, stable endpoints, distribution to Teams/M365 Copilot/Entra Agent Registry |

### Hosted Agent Details (Preview)
- Container-based: bring your own Docker image to ACR, Foundry manages runtime
- Frameworks: Agent Framework, LangGraph, custom code (Python + C#)
- Replica sizes: 0.25-4 vCPUs, 0.5-8 GiB memory
- 24 regions available
- No private networking during preview
- Identity: project managed identity (unpublished) or dedicated agent identity (published)

### Mapping to Our Architecture

| Foundry Capability | IPAI Plugin Equivalent | Action |
|---|---|---|
| Prompt agents | Claude Code skills (10 defined) | **Already have** — our skills are richer with domain-specific knowledge |
| Workflow agents | Subagent orchestration via `/spawn` | **Already have** — worktree isolation is more developer-friendly than YAML workflows |
| Hosted agents | Not needed for dev-time; future option for production Odoo-facing agents | **Skip for now** — evaluate when shipping user-facing AI features in Odoo UI |
| Tool catalog | Plugin skills + MCP servers | **Adopt pattern** — formalize tool discovery in plugin.json |
| MCP Server | `.mcp.json` + `foundry-routing` skill | **Already have** — expand with Odoo-specific MCP tools |
| A2A Tool | Not yet implemented | **Adopt later** — useful when agents need cross-platform communication |
| Agent identity | Entra managed identity via `foundry-copilot-operator` | **Already have** — the agent definition already specifies Entra MI |
| Observability | Evidence capture hooks (`hooks/stop/evidence-capture.json`) | **Enhance** — add OpenTelemetry trace export pattern |

---

## 2. Microsoft Agent Framework (Semantic Kernel v2)

### What It Is
Open-source SDK combining Semantic Kernel + AutoGen. The direct successor and "next generation" of both. Version 1.0 released, production-ready. Python and .NET.

### Key Capabilities

| Feature | Details |
|---------|---------|
| **Agent abstractions** | `ChatAgent` base class, tool functions (`@ai_function`), middleware |
| **Model providers** | Foundry, Azure OpenAI, OpenAI, Anthropic, Ollama, and more |
| **Orchestration patterns** | Sequential, Concurrent, Handoff, Group Chat, Magentic-One |
| **Workflows** | Graph-based, type-safe routing, checkpointing, human-in-the-loop |
| **Tools** | Function tools, MCP servers (hosted + local), code interpreter, file search |
| **Memory** | Context providers for agent memory (session-based state management) |
| **Middleware** | Intercept agent actions for logging, filtering, guardrails |
| **Telemetry** | OpenTelemetry integration built-in |

### Orchestration Pattern Comparison

| Agent Framework Pattern | IPAI Plugin Equivalent | Mapping |
|---|---|---|
| **Sequential** | `/spawn` with ordered subtasks | Skills execute in sequence naturally |
| **Concurrent** | Parallel tool calls in Claude Code | Built into Claude's multi-tool calling |
| **Handoff** | Subagent definitions with skill binding | `odoo-reviewer` hands off to `qa-evidence-runner` |
| **Group Chat** | Not implemented | **Skip** — solo builder doesn't need multi-persona debate |
| **Magentic-One** | Not applicable | Complex open-ended task orchestration; Claude Code itself fills this role |
| **Middleware** | PreToolUse/PostToolUse hooks | **Already have** — `odoo-guardrails.json` is middleware |
| **Checkpointing** | Evidence capture at stop | **Enhance** — add mid-workflow checkpoint support |

### Deprecated Planners
Semantic Kernel's explicit planners (Handlebars, Stepwise) are deprecated. Function calling is now the recommended approach. This validates our architecture: Claude Code's native function calling through skills is the correct pattern.

---

## 3. Microsoft 365 Agents SDK

### What It Is
SDK for building agents deployable to M365 Copilot, Teams, Outlook, SharePoint, Web, Email, and SMS channels.

### Key Capabilities
- Declarative agents: configure Copilot with custom instructions + knowledge + actions (no custom model needed)
- Custom engine agents: full orchestration control with Agent Framework
- Built-in MCP support for declarative agents (announced March 2026)
- Distribution: M365 Admin Center, Teams app store, Entra Agent Registry

### Mapping to Our Architecture

| M365 Agents Capability | IPAI Relevance | Action |
|---|---|---|
| Declarative agents | Not applicable — we don't run inside M365 Copilot | **Skip** |
| Teams channel publishing | Future option for Odoo-Teams notifications | **Defer** — evaluate when Teams integration needed |
| MCP in declarative agents | Validates MCP as universal tool protocol | **Adopt protocol** — continue MCP-first strategy |
| Custom engine agents | Agent Framework hosted agents (see #2) | **Skip hosting** — Claude Code is our engine |

---

## 4. Copilot Studio

### What It Is
Low-code SaaS platform for building conversational and autonomous agents. Power Platform ecosystem.

### Key Capabilities
- Autonomous agents: trigger-based, run without user prompts
- Triggers: Power Automate flows, scheduled (hourly/daily/weekly/monthly), event-driven
- Guardrails: configurable safety boundaries for autonomous execution
- Connectors: 1,400+ pre-built (Dataverse, SharePoint, SAP, Salesforce, etc.)
- A2A support: invoke any A2A agent from within Copilot Studio

### Mapping to Our Architecture

| Copilot Studio Capability | IPAI Plugin Equivalent | Action |
|---|---|---|
| Autonomous agents with triggers | Claude Code hooks (PreToolUse, PostToolUse, Stop) | **Partial match** — our hooks are reactive, not scheduled |
| Scheduled triggers | Not implemented | **Adopt pattern** — add cron/scheduled agent invocation (via Claude Code `/schedule` skill) |
| Power Automate integration | Not applicable — we use GitHub Actions + Azure DevOps | **Skip** |
| Low-code builder | Skills are declarative markdown (already low-code) | **Already have** — our skill authoring is simpler |
| Guardrails | `odoo-guardrails.json` PreToolUse hook | **Already have** — enhance with content safety patterns |

---

## 5. Azure AI Agent Service (now Foundry Agent Service)

Covered in Section 1 above. The rebrand from "Azure AI Agent Service" to "Foundry Agent Service" is complete as of March 2026. All documentation now lives under `learn.microsoft.com/en-us/azure/foundry/agents/`.

### Additional Tool Details

| Tool | GA/Preview | Function |
|------|-----------|----------|
| **Web Search** | GA | Bing grounding for real-time information |
| **File Search** | GA | Vector search over uploaded documents |
| **Code Interpreter** | GA | Sandboxed Python execution |
| **Memory** | Preview | Persistent agent memory across conversations |
| **MCP Servers** | Preview | Connect to any MCP-compliant server |
| **A2A Tool** | Preview | Inter-agent communication |
| **Azure AI Search** | GA | Enterprise search integration |
| **SharePoint** | GA | M365 document access |
| **Microsoft Fabric** | GA | Data lakehouse integration |
| **Azure Functions** | GA | Custom serverless tool execution |
| **Logic Apps** | GA | 1,400+ connector ecosystem |

---

## 6. Agent-to-Agent (A2A) Protocol

### What It Is
Open protocol by Google (April 2025) for AI agent interoperability. 150+ organizations supporting it as of 2026. Version 0.3 released.

### Protocol Details
- Transport: HTTP + SSE + JSON-RPC
- Discovery: `/.well-known/agent.json` agent card
- Auth: API keys, OAuth2, or provider-specific (Entra for Microsoft)
- Operations: task creation, status polling, streaming updates, artifact exchange
- Multi-turn: supports long-running tasks with status callbacks

### Microsoft's A2A Adoption
- A2A tool in Foundry Agent Service (preview)
- Invoke A2A agents from Copilot Studio
- Contributing to A2A spec and tooling on GitHub
- Auth options: key-based, OAuth2, or Entra Agent Identity

### Mapping to Our Architecture

| A2A Capability | IPAI Relevance | Action |
|---|---|---|
| Agent discovery (agent card) | Not yet implemented | **Adopt later** — define agent cards for our 6 subagents when they need external visibility |
| Inter-agent task delegation | Subagent orchestration via `/spawn` | **Already have** — internal only, no need for HTTP protocol overhead |
| Cross-platform agent calls | Not needed today | **Defer** — useful when integrating with external agent platforms |
| Artifact exchange | Evidence capture + output format | **Already have** — docs/evidence/ serves this purpose |

---

## 7. MCP (Model Context Protocol) in Foundry

### What It Is
Anthropic's open protocol for connecting LLMs to tools and data. Microsoft is a major adopter.

### Microsoft's MCP Implementation
- **Foundry MCP Server**: cloud-hosted at `mcp.ai.azure.com`, Entra auth, zero local infra
- **MCP in Agent Framework**: `@ai_function` + hosted MCP tools
- **MCP in M365**: declarative agents can connect to MCP servers
- **MCP Catalog**: `github.com/microsoft/mcp` — official Microsoft MCP server implementations
- **Azure DevOps MCP Server**: preview, available in Foundry tool catalog
- **Transport**: Streamable HTTP (new standard), SSE (legacy)

### Microsoft's Official MCP Servers
From the `microsoft/mcp` GitHub repo:
- Azure DevOps MCP Server
- Microsoft Foundry MCP Server
- Playwright MCP Server (browser automation)
- More being added to the catalog

### Mapping to Our Architecture

| MCP Capability | IPAI Plugin Equivalent | Action |
|---|---|---|
| Cloud-hosted MCP | `mcp/.mcp.json` in plugin | **Already have** — HTTP remote-first per our policy |
| Entra auth for MCP | Managed identity via `foundry-copilot-operator` | **Already have** |
| MCP tool discovery | Plugin `skills` array in `plugin.json` | **Enhance** — add MCP tool metadata to skill definitions |
| Azure DevOps MCP | Not yet connected | **Adopt** — connect for pipeline management from Claude Code |
| Playwright MCP | Not yet connected | **Adopt** — connect for browser QA automation |

---

## Consolidated Comparison: Microsoft vs IPAI Plugin Architecture

### Architecture Layer Map

| Layer | Microsoft Platform | IPAI Claude Code Plugin | Gap Analysis |
|-------|-------------------|------------------------|--------------|
| **Agent Runtime** | Foundry Agent Service (managed) | Claude Code CLI + subagents | No gap — Claude Code is more capable for dev-time work |
| **Orchestration SDK** | Agent Framework 1.0 (.NET/Python) | Plugin skills + `/spawn` + hooks | No gap — our markdown-based skills are simpler and sufficient |
| **Tool Protocol** | MCP (Foundry MCP Server) | MCP (`.mcp.json`) | Minor gap — formalize tool metadata |
| **Agent Protocol** | A2A (preview) | Not implemented | No urgency — internal orchestration sufficient for now |
| **Identity** | Entra Agent ID + Agent Registry | Entra MI via `foundry-copilot-operator` | Minor gap — no registry equivalent |
| **Guardrails** | Content safety + XPIA protection | PreToolUse hooks (`odoo-guardrails.json`) | Minor gap — add content safety patterns |
| **Observability** | App Insights + OpenTelemetry | Evidence capture hooks | Moderate gap — add OTel trace export |
| **Low-Code Builder** | Copilot Studio | Skill authoring template | No gap — our approach is already declarative |
| **Scheduling** | Copilot Studio triggers + Power Automate | Not implemented | Moderate gap — add scheduled agent runs |
| **Multi-Agent Patterns** | Sequential, Concurrent, Handoff, Group Chat, Magentic | Sequential (spawn), Concurrent (parallel tools) | Minor gap — add explicit handoff pattern |
| **Memory** | Context providers, session state | Not implemented | Moderate gap — add persistent agent memory |
| **Publishing** | Teams, M365 Copilot, Entra Registry | Not applicable | No gap — we don't distribute agents to end users |

### What to Adopt

| Priority | Capability | Source | Implementation Path |
|----------|-----------|--------|---------------------|
| **P0** | OpenTelemetry trace export | Agent Framework pattern | Add OTel exporter to `hooks/stop/evidence-capture.json` |
| **P0** | Azure DevOps MCP Server | Microsoft MCP catalog | Add to `.mcp.json` for pipeline management |
| **P1** | Scheduled agent runs | Copilot Studio pattern | Use Claude Code `/schedule` skill for recurring tasks |
| **P1** | Agent memory/context providers | Agent Framework pattern | Add persistent state to subagent definitions |
| **P1** | Explicit handoff pattern | Agent Framework Handoff orchestration | Define handoff rules in subagent `.md` files |
| **P2** | Playwright MCP Server | Microsoft MCP catalog | Add for browser QA automation |
| **P2** | Content safety guardrails | Foundry guardrails pattern | Enhance PreToolUse hooks with content classification |
| **P2** | Tool metadata in skill definitions | Foundry tool catalog pattern | Add MCP tool schema to `SKILL.md` frontmatter |
| **P3** | A2A agent cards | A2A protocol | Define when external agent integration is needed |
| **P3** | Agent Registry equivalent | Entra Agent Registry | Define when multi-user agent governance is needed |

### What to Skip

| Capability | Reason |
|-----------|--------|
| Foundry Agent Service hosting | Claude Code subagents with worktree isolation already provide equivalent orchestration. Cost and complexity not justified for solo builder. |
| Copilot Studio low-code builder | Our skill authoring via markdown is already simpler and more dev-friendly. |
| M365 Agents SDK | We don't run inside M365 Copilot. Not applicable. |
| Group Chat orchestration | Multi-persona debate is designed for team environments. Solo builder doesn't benefit. |
| Magentic-One pattern | Claude Code itself is the general-purpose reasoning agent. Wrapping it in another orchestrator adds no value. |
| Power Automate connectors | We use GitHub Actions + Azure DevOps for automation. Different ecosystem. |
| Agent Framework .NET SDK | Our stack is Python (Odoo) + shell (CI). No .NET surface. |

---

## Key Architectural Insight

Microsoft's agent platform is designed for **enterprise teams building user-facing AI products** — it optimizes for managed hosting, multi-tenant identity, compliance, and distribution to M365 channels.

Our architecture is a **solo-builder dev-time agent system** — it optimizes for fast iteration, domain-specific knowledge, worktree isolation, and evidence-based verification. Claude Code itself is the "agent runtime" and the plugin architecture provides the specialization layer.

The correct adoption strategy is:
1. **Protocols**: Adopt MCP and A2A as the tool/agent communication standards
2. **Patterns**: Adopt middleware/guardrails, observability, and scheduled execution patterns
3. **Infrastructure**: Skip managed hosting — Claude Code + Azure Container Apps is the runtime
4. **Identity**: Align with Entra Agent ID for any production agent that touches Azure resources

---

## Sources

- [What is Microsoft Foundry Agent Service?](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) — Microsoft Learn
- [Microsoft Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/) — Microsoft Learn
- [Hosted agents in Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents) — Microsoft Learn
- [Foundry Agent Service is GA](https://devblogs.microsoft.com/foundry/foundry-agent-service-ga/) — DevBlogs
- [Introducing Microsoft Agent Framework](https://devblogs.microsoft.com/foundry/introducing-microsoft-agent-framework-the-open-source-engine-for-agentic-ai-apps/) — DevBlogs
- [Microsoft Agent Framework Version 1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/) — DevBlogs
- [Semantic Kernel to Agent Framework Migration](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/) — Microsoft Learn
- [Workflow orchestrations in Agent Framework](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/) — Microsoft Learn
- [Agent-to-Agent Protocol (A2A)](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) — Google Developers Blog
- [Microsoft commits to Google's A2A protocol](https://www.ciodive.com/news/-Microsoft-AI-agent-standard-Google-a2a-interoperability/747593/) — CIO Dive
- [A2A Protocol v0.3 upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) — Google Cloud Blog
- [Microsoft MCP Catalog](https://github.com/microsoft/mcp) — GitHub
- [MCP and Foundry Agents](https://learn.microsoft.com/en-us/agent-framework/user-guide/model-context-protocol/) — Microsoft Learn
- [Build and register MCP server in Foundry](https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server) — Microsoft Learn
- [Foundry tool catalog](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog) — Microsoft Learn
- [Announcing Entra Agent ID](https://techcommunity.microsoft.com/blog/microsoft-entra-blog/announcing-microsoft-entra-agent-id-secure-and-manage-your-ai-agents/3827392) — Tech Community
- [Governing Agent Identities](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview) — Microsoft Learn
- [Agents for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-overview) — Microsoft Learn
- [Declarative Agents with MCP](https://devblogs.microsoft.com/microsoft365dev/build-declarative-agents-for-microsoft-365-copilot-with-mcp/) — DevBlogs
- [Copilot Studio autonomous agents](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/unlocking-autonomous-agent-capabilities-with-microsoft-copilot-studio/) — Microsoft Blog
- [What's new in Foundry Dec 2025 & Jan 2026](https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-dec-2025-jan-2026/) — DevBlogs
- [What is A2A Protocol?](https://www.ibm.com/think/topics/agent2agent-protocol) — IBM
- [Agent 365 Security Announcements](https://simoncarter.ai/posts/microsoft-s-rsac-2026-security-announcements-agent-365-zero-trust-for-ai-and-wha/) — Simon Carter
