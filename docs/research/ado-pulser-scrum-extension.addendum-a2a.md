# ADO Pulser Scrum Master — A2A + MCP Interop Addendum

- Status: supersedes the bespoke-gateway framing in §A and §C of `docs/research/ado-pulser-scrum-extension.md`
- Does not change §B (failure modes), §D (marketplace path), §E (reference implementations), §F (eval)
- Effective: 2026-04-15
- Not R2-blocking: doctrine and Agent Card land now; full A2A migration lands during Phase 2 build

---

## 1. What changed and why

The original research framed the architecture as `ADO extension → bespoke REST gateway (ACA) → Pulser agent`. That framing is wrong. The correct pattern is the same one Claude Code itself uses: a **thin local client, remote compute, standard protocol**. Claude Code's CLI lives next to your files, but its reasoning runs at Anthropic's endpoints, its tools are brokered through MCP, and its wire format is a published standard — not a private RPC. The ADO extension must work the same way. It is a thin surface that renders results and hands a user intent off to a remote agent over a standard protocol, nothing more.

Bespoke REST between ADO and Pulser bifurcates the ecosystem. Every new surface (Odoo chatter, Teams bot, Foundry peer, M365 Copilot, Copilot Studio, another Pulser specialist) would need its own glue. Standardising on A2A reduces N bridges to one interop contract and lets Foundry, Copilot Studio, Teams, and Claude Code act as peers rather than forks. Microsoft's Foundry Agent Service now publishes first-party A2A tool support and an A2A authentication doc; Copilot Studio ships first-class A2A connection; the Microsoft Agent Framework ships A2A bindings for .NET, Python, and TypeScript. The protocol itself is governed by the Linux Foundation under the Apache 2.0 license, with the canonical spec at `https://a2a-protocol.org/latest/` and SDKs at `github.com/a2aproject/{a2a-python,a2a-dotnet,a2a-js}`.

## 2. A2A + MCP relationship

A2A and MCP are orthogonal and both mandatory. A2A is the **agent-to-agent** interop wire (client → agent, agent → agent). MCP is the **agent-to-tool** wire (agent → database, agent → ADO REST, agent → Key Vault, agent → internal service). The Scrum Master agent is an A2A server to its callers and an MCP client to its tools. Microsoft's own Copilot Studio documentation makes the split explicit: use A2A for agent integration, use MCP for tools/resources, use HTTP connectors only for plain APIs (`https://learn.microsoft.com/microsoft-copilot-studio/add-agent-agent-to-agent`). Pulser must honor the same split — MCP invariant #10 remains, A2A is added as a peer invariant.

## 3. Agent Card contract

Every Pulser agent publishes an Agent Card at the canonical discovery path `/.well-known/agent-card.json` (Foundry Control Plane auto-discovers it there per `https://learn.microsoft.com/azure/foundry/agents/how-to/tools/agent-to-agent#host-an-a2a-compatible-agent-endpoint`). Some older clients still probe `/.well-known/agent.json` (Copilot Studio docs show that path per `https://learn.microsoft.com/microsoft-copilot-studio/add-agent-agent-to-agent#connect-your-agent-to-another-agent-over-the-a2a-protocol`); serve both for a transition window.

Required top-level fields (per `https://a2a-protocol.org/latest/specification/` and Microsoft Agent Framework `AgentCard` docs at `https://learn.microsoft.com/agent-framework/integrations/a2a`):

- `name` — agent identifier string
- `description` — one-paragraph purpose, used by router LLMs for delegation decisions
- `url` — A2A endpoint base
- `provider` — `{ organization, url }`
- `version` — semver
- `capabilities` — `{ streaming, pushNotifications, stateTransitionHistory }` booleans
- `authentication` — `{ schemes[], credentials? }` (schemes include `bearer`, `oauth2`, `apiKey`, `none`)
- `defaultInputModes` — MIME types the agent accepts
- `defaultOutputModes` — MIME types the agent returns
- `skills[]` — each `{ id, name, description, tags[], examples[], inputModes?, outputModes? }`

Protocol endpoints (JSON-RPC over HTTP plus SSE):

- `POST /` with method `message/send` — synchronous send
- `POST /` with method `message/stream` — Server-Sent Events streaming
- `POST /` with method `tasks/get` — fetch long-running task state by `contextId` / task id
- `POST /` with method `tasks/cancel` — cancel

## 4. Revised architecture

```
+--------------------------------------------------------------+
| Thin local clients (identical class, no bespoke protocol)    |
|   ADO extension  Odoo chatter  Teams bot  Claude Code  Peer  |
+---------------------------┬----------------------------------+
                            │  A2A (message/send, stream, tasks/get)
                            │  discovery: /.well-known/agent-card.json
                            ▼
+--------------------------------------------------------------+
| A2A server: Pulser Scrum Master (ACA, Entra Agent ID, MI)    |
|   orchestrator + workers + evaluator (unchanged from §A)     |
+---------------------------┬----------------------------------+
                            │  MCP (stdio / streamable-HTTP)
                            ▼
+--------------------------------------------------------------+
| MCP tool surfaces (per-tool allowlist, zero-secret agent)    |
|   ADO REST MCP   Foundry gpt-4.1   Key Vault proxy  AppIns.  |
+--------------------------------------------------------------+
```

## 5. Identity

- **A2A server auth:** Entra Agent ID on the ACA app (agent has its own directory object per the Entra Agent ID surface already visible on the IPAI tenant). OAuth 2.0 scheme declared in the Agent Card; bearer tokens accepted.
- **Client auth from the ADO extension:** `SDK.getAppToken()` produces the ADO-issued JWT; the A2A server validates it, then swaps for an on-behalf-of Entra token for downstream MCP tool calls.
- **Backend Azure calls:** Managed Identity + Key Vault `kv-ipai-dev-sea`, not the user's token. The agent itself never holds secrets — the MCP tool server proxies ADO PAT / Foundry keys.
- **Foundry A2A tool reuse:** per `https://learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication`, prefer Entra-agent-identity; fall back to OAuth identity passthrough only for user-scoped actions.

## 6. Local-by-power-remotely invariant

The Agent Card is one contract. The backing implementation is swappable.

- Production path: A2A server on ACA SEA, backed by Foundry `ipai-copilot-resource` with `gpt-4.1` (+ `gpt-4.1-mini` routing), per R2 baseline.
- Dev / eval / edge path: identical A2A server signature, backed by Foundry Local serving `phi-4` or equivalent small model, reachable at `http://localhost:<port>`.

A client (ADO extension, Odoo chatter, Teams bot, Claude Code) never learns which backing is active. The Agent Card URL changes, the protocol does not. This makes offline dev loops, CI eval runs, and air-gapped pilots first-class surfaces rather than second-class diverges. Foundry Local's A2A story is tracked in the same Foundry Agent Service docs linked above.

## 7. Orchestrator-mediated delegation (SUPERSEDES earlier peer-delegation framing)

**Correction, 2026-04-15**: An earlier draft of this section described Pulser agents calling each other directly as peers. That framing is wrong and has been replaced. Per canonical doctrine (`docs/architecture/agent-orchestration-model.md`, CLAUDE.md invariant #10a), **workers never invoke workers directly**. All cross-agent calls go through the supervisor in `agent-platform/orchestration/`.

Example: Scrum Master's retro worker encounters an item that asks "did we misclassify BIR 2307 withholding this sprint?" The supervisor (not the worker) decides to enrich the retro with tax reasoning:

1. Retro worker returns a structured result with a `suggested_followup` field citing the tax question.
2. Judge agent validates the output and flags the tax-dependency hint.
3. **Supervisor** (not the worker) reads the judge output and dispatches a second step: a Tax Guru worker call, using the standard agent-invocation envelope. Tax Guru has no idea Scrum Master exists — it only sees a well-formed request from the supervisor.
4. Supervisor collects Tax Guru's structured result, returns to Scrum Master's synthesizer worker, which merges both into the final retro markdown.
5. Trace carries `workflow_id` spanning all steps; every call and result persisted for replay.

A2A is still the protocol on every hop (client → supervisor, supervisor → worker, supervisor → judge). What A2A does **not** authorize is free-form worker-to-worker chat. Same contract as calling a partner agent or a Microsoft-built Foundry agent — always supervisor-mediated, envelope-bound, traceable.

## 8. What this voids vs. preserves in the original research

**Voided.**

- §A framing of an "ACA gateway" as a bespoke REST service. The ACA app is still an ACA app — but it is an **A2A server**, not a private HTTP gateway.
- §C auth flow showing `ADO extension → gateway auth header`. Replaced by A2A bearer / OAuth per Agent Card.
- Any reference to a custom RPC between Pulser specialists.

**Preserved verbatim.**

- §A orchestrator-workers + evaluator-optimizer pattern, budget guard, escape hatch, stateless design (CLAUDE.md invariant #14 unchanged).
- §A `gpt-4.1` / `gpt-4.1-mini` / `gpt-4.1-nano` routing per `ssot/governance/foundry-model-routing.yaml` (R2 baseline unchanged).
- §B full failure-modes table.
- §C SDK pinning (`azure-devops-extension-sdk@4.0.2`, `azure-devops-ui@2.259.0`, `tfx-cli@0.21.1`).
- §D marketplace path (publisher `ms-pulser`, private first, BYOL gate at R4).
- §E reference-implementation patterns (SonarCloud / 7pace / Nexus).
- §F eval methodology, Safe Outputs, Batch API 50% discount.

## 9. Impact on Phase 2 deliverables

| Original ID | Change | Result |
|---|---|---|
| D2 `apps/pulser-scrum-gateway` | Rename | `apps/pulser-scrum-agent` (A2A server, ACA) |
| — | New **D2a** | `agents/pulser-scrum-master/.well-known/agent-card.json` (reference Agent Card, this addendum) |
| D1 `gatewayClient.ts` | Rename + reshape | `a2aClient.ts` speaking A2A JSON-RPC (`message/send`, `message/stream`, `tasks/get`) via the a2a-js SDK |
| D4 Bicep | Add output | `agentCardUrl` alongside `gatewayUrl` during transition; drop `gatewayUrl` once clients cut over |
| D5 Pipeline | Add gate | `scripts/validate_agent_card.py` schema-validates every `agent-card.json` against the A2A JSON schema pulled from `github.com/a2aproject/A2A` on each run |

## 10. Citations

All load-bearing claims have a URL.

- A2A protocol canonical: `https://a2a-protocol.org/latest/`
- A2A spec + JSON schema: `https://a2a-protocol.org/latest/specification/`
- A2A project repo (Linux Foundation, Apache 2.0): `https://github.com/a2aproject/A2A`
- A2A SDKs: `https://github.com/a2aproject/a2a-python`, `https://github.com/a2aproject/a2a-dotnet`, `https://github.com/a2aproject/a2a-js`
- Microsoft Foundry Agent Service A2A tool: `https://learn.microsoft.com/azure/foundry/agents/how-to/tools/agent-to-agent`
- Microsoft Foundry A2A authentication: `https://learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication`
- Microsoft Foundry Control Plane register custom agent: `https://learn.microsoft.com/azure/foundry/control-plane/register-custom-agent`
- Microsoft Agent Framework A2A integration: `https://learn.microsoft.com/agent-framework/integrations/a2a`
- Microsoft Agent Framework journey: `https://learn.microsoft.com/agent-framework/journey/agent-to-agent`
- Copilot Studio A2A connection: `https://learn.microsoft.com/microsoft-copilot-studio/add-agent-agent-to-agent`
- Linux Foundation A2A project page: `https://www.linuxfoundation.org/projects/agent-to-agent`

## Anchors

- Phase 1 research (unchanged): `docs/research/ado-pulser-scrum-extension.md`
- Reference Agent Card: `agents/pulser-scrum-master/.well-known/agent-card.json`
- Interop matrix: `ssot/governance/agent-interop-matrix.yaml`
- `CLAUDE.md` Cross-Repo Invariants #10 (MCP First) + new #10a (A2A First)
