# Constitution — Odoo Copilot Agent Framework

## Non-Negotiable Rules

1. **Three agents + one router — no more.** Advisory (read-only), Ops (internal read-only), Actions (controlled writes). Router is a deterministic workflow, not an LLM agent. Never add a fourth agent.

2. **Single Foundry agent is still the runtime.** `ipai-odoo-copilot-azure` in project `data-intel-ph` remains the physical agent. The three logical agents are instruction-switched modes of the same Foundry agent. No second Foundry agent.

3. **Capability packs are not agents.** Databricks Intelligence, fal Creative Production, and Marketing Strategy packs attach inside existing agents as tool sets + prompt segments. All three packs attach to all agents (read-only access for Advisory/Ops, write access for Actions where applicable). Marketing is "light" on Actions (prompt context only, no dedicated tools). Never promote a capability pack to a standalone agent.

4. **Router is code, not LLM.** The router uses deterministic rules (regex, model name, user role, channel) to select the correct agent. No LLM inference in routing decisions.

5. **Write access is always bounded.** Only the Actions agent can write. Writes are gated by: model allowlist, field allowlist, state constraints, and approval workflow. Advisory and Ops agents have zero write access — no exceptions.

6. **Evaluation before promotion.** No agent mode ships to production without passing Foundry evaluation runs: groundedness, relevance, coherence, citation accuracy. Minimum thresholds: groundedness ≥ 0.8, relevance ≥ 0.85.

7. **Capability packs require vendor credentials.** Databricks pack requires `DATABRICKS_HOST` + `DATABRICKS_TOKEN`. fal pack requires `FAL_KEY`. Marketing pack requires web search tool only. Never hardcode credentials. Packs degrade gracefully when credentials are absent.

8. **Foundry SDK is the only integration surface.** Use `azure-ai-projects>=2.0.0` with dual-client pattern (AIProjectClient + OpenAI). No direct HTTP calls to Foundry APIs. No forking upstream repos (`microsoft/agent-framework`, `microsoft/Agents`, `github/copilot-sdk`).

9. **MCP is the canonical tool connection protocol.** Odoo-side tools register as MCP servers. OpenAPI specs are fallback. A2A is future-only. Never create bespoke RPC protocols for agent-to-Odoo communication.

10. **Telemetry is non-optional.** Every agent invocation logs to Azure App Insights: user, mode, tools called, tokens consumed, latency, safety flags. OpenTelemetry traces for multi-agent workflows.

11. **No agent sprawl from vendor references.** Smartly, Quilt.AI, LIONS, Data Intelligence, and any future vendor surfaces inform capability pack design — they never become agents or modules. Vendor intelligence is distilled into prompts + tool configurations inside existing packs.

12. **APIM is the required production front door.** All production traffic routes through APIM (`apim-ipai-dev`) for auth, quotas, throttling, and observability. Internal services may use SDK direct during development. n8n/adapters use REST direct with APIM or service auth. Foundry Playgrounds are non-production only.

13. **"Light" pack attachment means prompt context only.** When a pack attaches as "light" to an agent, it provides prompt segments and contextual knowledge but no dedicated tools or write capabilities. The agent can reference the pack's domain knowledge without executing pack-specific actions.

14. **Router implementation is Python.** The router is implemented as `copilot_router.py` inside `addons/ipai/ipai_odoo_copilot/models/`. It is deterministic Python code, not an Agent Framework graph or YAML workflow. Router groundedness evaluation does not apply (no LLM inference).

## Skill Construction Standard

Every Odoo Copilot skill must be implemented as a governed unit, not an informal prompt.

### Required components per skill
Each skill must define:
1. **Skill identity**
   - stable `skill_id`
   - display name
   - domain/category
   - owner/maintainer

2. **Contract**
   - required inputs
   - optional inputs
   - output types
   - artifact types
   - writeback targets
   - failure modes

3. **Policy**
   - allowed execution modes
   - permission requirements
   - configuration prerequisites
   - human-approval requirements
   - audit/logging requirements

4. **Runtime**
   - context-pack requirements
   - routing hints
   - tools/adapters used
   - timeout/retry behavior
   - fallback behavior

5. **UX**
   - user-visible label
   - preview behavior
   - progress states
   - approval prompts
   - blocked-state messaging

### Hard rule
No capability may be exposed in Odoo Copilot unless it resolves to a concrete skill contract and runtime path.
