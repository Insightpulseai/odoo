# Examples — copilot-sdk-dev-assistant

## Example 1: BYOK setup with Azure AI Foundry

**Input**: Configure Copilot SDK with Azure AI Foundry as BYOK provider for the Python SDK.

**Output**:
- Subscription/BYOK: No active Copilot subscription — BYOK mode selected
- BYOK provider: Azure AI Foundry — CONFIGURED
- API key: stored in env var `AZURE_AI_FOUNDRY_API_KEY` — PASS
- Auth constraint: BYOK does NOT support Entra ID or managed identity — DOCUMENTED
- SDK client: Python SDK configured — PASS
- JSON-RPC: communication established on localhost — PASS
- Quality: tested on 20 code generation tasks — accuracy 0.92, safety 1.0 — PASS
- Evidence: quality evaluation results with sample inputs/outputs

## Example 2: Missing subscription and no BYOK

**Input**: Initialize Copilot SDK without subscription or BYOK configuration.

**Output**:
- Subscription/BYOK: No Copilot subscription detected, no BYOK configured — FAIL (BLOCKER)
- Blocker: Copilot SDK requires either an active GitHub Copilot subscription or BYOK provider configuration
- Recommendation: Either activate Copilot subscription or configure BYOK with `COPILOT_BYOK_PROVIDER` and `COPILOT_BYOK_API_KEY` env vars

## Example 3: Attempting to use as enterprise runtime

**Input**: Proposal to use Copilot SDK as the core agent runtime for customer-facing workflows.

**Output**:
- Assessment: POLICY VIOLATION — Copilot SDK is a developer assistance tool, not an enterprise agent runtime
- Maturity: Technical preview — no GA stability guarantees
- Auth: BYOK lacks Entra/managed identity — cannot meet enterprise auth requirements
- Recommendation: Use Microsoft Agent Framework (`microsoft/agent-framework`) for enterprise agent orchestration
- Cross-reference: `agents/skills/agent-framework-core/` for the correct layer
