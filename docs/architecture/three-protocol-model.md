# The Three-Protocol Model — A2A + MCP + Agent365

**Status:** Canonical. Anchored in CLAUDE.md Cross-Repo Invariant #10a.
**Rev:** 2026-04-15

---

## TL;DR

Three industry-standard protocols, orthogonal, all mandatory for Pulser:

| Protocol | Authority | Purpose | Pulser role |
|---|---|---|---|
| **A2A** | Linux Foundation (orig. Google, April 2025) | Agent ↔ agent interop | Transport for every internal + client→supervisor call |
| **MCP** | Anthropic (open spec, industry standard) | Agent ↔ tool | Transport for every tool/retrieval/DB call |
| **Agent365 SDK** | Microsoft | Agent ↔ M365 user | Surface into Copilot Chat, Teams, Outlook only |

They **do not overlap**. You need all three to deliver a production Pulser agent.

---

## Why three, not one

- **A2A alone** would force us to re-invent the M365 discovery/auth surface.
- **MCP alone** can't describe agent-to-agent handoff, task lifecycle, or streaming between agents.
- **Agent365 alone** is M365-specific — would lock out ADO, Odoo, Slack, and partner surfaces.

Together, they **decouple the agent** from:
- its tools (MCP)
- its peers and clients (A2A)
- its human surface (Agent365 for M365, direct A2A for everything else)

---

## The stack diagram

```
┌──────────────────────────────────────────────────────────────────┐
│  Human surfaces                                                  │
│                                                                  │
│   M365 Copilot / Teams / Outlook          ADO ext / Odoo chatter │
│            │                                      │ Slack bot    │
│            ▼                                      │ Claude Code  │
│  ┌─────────────────────┐                          │              │
│  │  Agent365 SDK       │                          │              │
│  │  (discovery, auth,  │                          │              │
│  │   surface contract) │                          │              │
│  └─────────┬───────────┘                          │              │
│            │                                      │              │
│            ▼                                      ▼              │
│  ┌───────────────────────────────────────────────────────┐       │
│  │  APIM GenAI Gateway                                   │       │
│  │  (rate limit, semantic cache, cost cap, policy)       │       │
│  └───────────────────────┬───────────────────────────────┘       │
│                          │                                       │
│                          ▼ A2A                                   │
│  ┌───────────────────────────────────────────────────────┐       │
│  │  pulser_supervisor (A2A server)                       │       │
│  │  intake → plan → dispatch → judge → synthesize        │       │
│  └─┬─────────────────┬──────────────────┬────────────────┘       │
│    │ A2A             │ A2A              │ A2A                    │
│    ▼                 ▼                  ▼                        │
│  specialist       judge_*          synthesizer                   │
│  workers          (A2A servers)    (A2A server)                  │
│  (A2A servers)                                                   │
│    │                                                             │
│    │ MCP                                                         │
│    ▼                                                             │
│  Tools: Foundry/ADO/Odoo/KV/App Insights/Search/...              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Invariant:** workers never call workers. Supervisor initiates every downstream A2A call.

---

## Layer-by-layer

### A2A (Agent ↔ Agent)

- **Spec:** `https://a2a-protocol.org/latest/specification/`
- **Schema source:** `https://github.com/a2aproject/A2A` (JSON Schema)
- **Pinned version for R2:** `0.2.0`
- **Discovery:** `GET /.well-known/agent-card.json`
- **Transport:** JSON-RPC 2.0 over HTTP, with SSE streaming for long tasks
- **Key methods:** `message/send`, `message/stream`, `tasks/get`, `tasks/cancel`

**IPAI usage:**
- Every Pulser agent is an A2A server
- Every internal call (supervisor → worker, supervisor → judge) is A2A
- Every external client (ADO extension, Odoo chatter, Slack bot, Claude Code) enters via A2A to the supervisor

**Auth:** Entra Agent ID + MI. Agent Card advertises OAuth2 scheme; tokens validated by the callee.

---

### MCP (Agent ↔ Tool)

- **Spec:** `https://modelcontextprotocol.io/`
- **Schema:** JSON over stdio / HTTP / SSE
- **Pinned version for R2:** latest stable (track Anthropic release notes)

**IPAI usage:**
- Every agent tool is an MCP server
- Per-agent allowlists declared in `ssot/governance/agent-interop-matrix.yaml`
- Project-shared MCP config lives in `.mcp.json` (no secrets)

**Critical rule:** No dynamic tool acquisition at runtime. Tools are declared at agent boot.

---

### Agent365 SDK (Agent ↔ M365 user)

- **SDK source:** Microsoft 365 Agents SDK (samples at `https://learn.microsoft.com/microsoft-365/agents/`)
- **Surfaces:** M365 Copilot Chat, Teams (bot/tab/meeting), Outlook (add-in), SharePoint (webpart)
- **Language support:** TypeScript, Python, C#, NodeJS
- **Backends supported (reference samples):** MAF, OpenAI, Langchain, Claude, N8n, Perplexity, Vercel-sdk, Devin

**IPAI usage:**
- **Only** on M365 surfaces. ADO, Odoo, Slack, Claude Code bypass Agent365.
- Agent365 wraps the supervisor entry point: `M365 user → Agent365 wrapper → supervisor (A2A)`.
- Deferred to R3 (R2 ships ADO extension first).

**Manifest location:** `agents/<agent_name>/agent365/manifest.json` when adopted.

---

## Non-Pulser stack validation

This is the same pattern MS uses in `microsoft/agentic-factory-hack` and the M365 Agents Toolkit samples:

| Capability | IPAI | MS reference |
|---|---|---|
| MAF runtime | ✅ `microsoft/agent-framework` | ✅ same |
| A2A + MCP | ✅ both | ✅ both |
| APIM GenAI Gateway | 🟡 R3 scope | ✅ "Custom Engine Agent using APIM GenAI Gateway" (TS) |
| Agent365 | 🟡 R3 scope | ✅ 7+ samples |
| Supervisor-mediated | ✅ canonical | ✅ sequential chain in factory-hack |

---

## What this locks in

1. **No bespoke gateways** for agent-to-agent comms. A2A is the answer.
2. **No bespoke tool adapters** in agent code. MCP is the answer.
3. **No bespoke M365 surfaces**. Agent365 SDK is the answer.
4. **No peer-to-peer worker comms.** Supervisor mediates (see `agent-orchestration-model.md`).
5. **No model lock-in.** Same Agent Card works against Foundry cloud (team mode) or Foundry Local (solo mode).

---

## References

- Google 5-Day AI Agents Intensive (Day 2 MCP, Day 5 A2A): `https://www.kaggle.com/learn-guide/5-day-genai-intensive`
- `microsoft/agent-framework` (MIT, GA, dotnet-1.1.0): `https://github.com/microsoft/agent-framework`
- `microsoft/agentic-factory-hack` (reference hackathon): `https://github.com/microsoft/agentic-factory-hack`
- M365 Agents Toolkit sample gallery: `https://learn.microsoft.com/microsoft-365/agents/samples/`
- Anthropic "Building Effective Agents": `https://www.anthropic.com/engineering/building-effective-agents`
