# Examples — m365-agents-channel-delivery

## Example 1: Deploy ERP assistant to Teams

**Input**: Deploy the Odoo ERP assistant agent to Microsoft Teams channel.

**Output**:
- Target channel: Microsoft Teams — IDENTIFIED
- Activity handlers: message handler for text queries, invoke handler for adaptive card actions — CONFIGURED
- State storage: Azure Blob Storage for conversation and user state — CONFIGURED
- Auth: Entra app registration `ipai-teams-agent` with `User.Read` scope — PASS
- Foundry backend: Azure AI Foundry agent `erp-assistant` connected via endpoint — PASS
- Package: Teams app package (`manifest.json`, icons, color icon) — PRODUCED
- Test: Sent "Show my pending invoices" in Teams, received structured response with adaptive card — PASS
- Evidence: Teams test conversation screenshot + activity trace log

## Example 2: Agent logic in channel layer (violation)

**Input**: Review a Teams bot that makes direct OpenAI API calls in the message handler.

**Output**:
- Target channel: Microsoft Teams — IDENTIFIED
- Activity handlers: message handler — CONFIGURED
- Foundry backend: NOT CONNECTED — FAIL (POLICY VIOLATION)
- Finding: Message handler contains direct `openai.chat.completions.create()` call — agent logic is in the channel layer
- Blocker: Core agent logic must run in Azure AI Foundry backend, not in the channel handler
- Recommendation: Move LLM calls to Foundry agent, channel handler forwards user message and returns Foundry response

## Example 3: M365 Copilot extension

**Input**: Create an M365 Copilot declarative agent for expense report queries.

**Output**:
- Target channel: M365 Copilot — IDENTIFIED
- Declarative agent manifest: `expense-query-agent.json` with capabilities, instructions, and tool definitions — PRODUCED
- Auth: Entra app with `Sites.Read.All` for SharePoint expense data — CONFIGURED
- Foundry backend: Expense query agent with RAG over expense documents — CONNECTED
- Test: Copilot query "What were my travel expenses last quarter?" returned correct summary — PASS
- Evidence: Copilot interaction log + response accuracy validation
