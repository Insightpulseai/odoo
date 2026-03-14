# Constitution — Odoo Copilot Agent Framework

## Non-Negotiable Rules

1. **Three agents + one router — no more.** Advisory (read-only), Ops (internal read-only), Actions (controlled writes). Router is a deterministic workflow, not an LLM agent. Never add a fourth agent.

2. **Single Foundry agent is still the runtime.** `ipai-odoo-copilot-azure` in project `data-intel-ph` remains the physical agent. The three logical agents are instruction-switched modes of the same Foundry agent. No second Foundry agent.

3. **Capability packs are not agents.** Databricks Intelligence, fal Creative Production, and Marketing Strategy packs attach inside existing agents as tool sets + prompt segments. Never promote a capability pack to a standalone agent.

4. **Router is code, not LLM.** The router uses deterministic rules (regex, model name, user role, channel) to select the correct agent. No LLM inference in routing decisions.

5. **Write access is always bounded.** Only the Actions agent can write. Writes are gated by: model allowlist, field allowlist, state constraints, and approval workflow. Advisory and Ops agents have zero write access — no exceptions.

6. **Evaluation before promotion.** No agent mode ships to production without passing Foundry evaluation runs: groundedness, relevance, coherence, citation accuracy. Minimum thresholds: groundedness ≥ 0.8, relevance ≥ 0.85.

7. **Capability packs require vendor credentials.** Databricks pack requires `DATABRICKS_HOST` + `DATABRICKS_TOKEN`. fal pack requires `FAL_KEY`. Marketing pack requires web search tool only. Never hardcode credentials. Packs degrade gracefully when credentials are absent.

8. **Foundry SDK is the only integration surface.** Use `azure-ai-projects>=2.0.0` with dual-client pattern (AIProjectClient + OpenAI). No direct HTTP calls to Foundry APIs. No forking upstream repos (`microsoft/agent-framework`, `microsoft/Agents`, `github/copilot-sdk`).

9. **MCP is the canonical tool connection protocol.** Odoo-side tools register as MCP servers. OpenAPI specs are fallback. A2A is future-only. Never create bespoke RPC protocols for agent-to-Odoo communication.

10. **Telemetry is non-optional.** Every agent invocation logs to Azure App Insights: user, mode, tools called, tokens consumed, latency, safety flags. OpenTelemetry traces for multi-agent workflows.

11. **No agent sprawl from vendor references.** Smartly, Quilt.AI, LIONS, Data Intelligence, and any future vendor surfaces inform capability pack design — they never become agents or modules. Vendor intelligence is distilled into prompts + tool configurations inside existing packs.

12. **APIM gateway for external ingress only.** Internal services use SDK direct. n8n/adapters use REST direct. APIM (`apim-ipai-dev`) is the enterprise front door for third-party callers only.
