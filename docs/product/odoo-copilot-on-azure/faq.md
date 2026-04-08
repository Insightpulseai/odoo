# FAQ

> Common questions about Odoo Copilot on Azure.

## Architecture

### What is the difference between prompt-only and hosted mode?

**Prompt-only** (current): Odoo sends a stateless request to Azure AI Foundry's
Responses API on each user message. Tool definitions and context are included in
every request. No durable agent exists on the Foundry side.

**Hosted** (target): A Foundry Agent is deployed with registered tools and
knowledge connections. Odoo routes messages to the agent, which manages
conversation threads, tool orchestration, and grounding server-side.

Prompt-only is simpler to operate. Hosted unlocks evaluation, tracing,
knowledge grounding, and multi-step orchestration.

### Does the copilot replace Odoo's built-in "Ask AI"?

No. Odoo 19's native Ask AI is a lightweight assistant with limited
customization. `ipai_odoo_copilot` extends it with:
- Custom tool definitions (finance, HR, inventory)
- Azure AI Foundry as the inference backend (instead of odoo.com IAP)
- Azure AI Search for document grounding
- Configurable agent profiles per role
- Audit trail for all interactions

The two can coexist. The IPAI copilot replaces the AI provider, not the UX
surface.

## Grounding

### What is the difference between search and action?

**Search** answers questions using grounding data (Odoo records + indexed
documents). It is read-only and never mutates state.

**Action** performs an operation in Odoo (create, update, workflow transition).
It requires explicit user confirmation and is logged in the audit trail.

The copilot determines intent from the user message. "What invoices are overdue?"
is a search. "Mark invoice INV/2026/0042 as paid" is an action.

### Can the copilot access data the user cannot see?

No. All Odoo data access goes through the ORM with the authenticated user's
security context. Odoo's ACL rules and record rules apply. The copilot cannot
read records the user cannot read.

### What happens when the search index has no relevant documents?

The copilot falls back to record-only grounding. If neither records nor
documents provide relevant information, the copilot states that it cannot answer
rather than guessing.

## Security

### Where are secrets stored?

All secrets (API keys, DB passwords, client secrets) are stored in Azure Key
Vault (`kv-ipai-dev`) and injected into the container as environment variables
via managed identity binding. No secrets are committed to git or stored in Odoo
configuration files.

### Does the copilot log user conversations?

Yes, but with controls:
- Audit log records tool calls, inputs (sanitized), outputs, and timing
- Prompts and model responses are logged for operational troubleshooting
- Secrets and PII are redacted before logging
- Logs are accessible only to the platform team
- Retention follows organizational policy

### Can the copilot delete records?

No. Deletion is disabled in the copilot tool layer. The copilot can archive
records (set `active=False`) but never execute `unlink()`.

## Operations

### What does "publish" mean for a Foundry Agent?

Publishing a Foundry Agent makes a specific version of the agent definition
(prompt, tools, knowledge connections, model) available as the production
endpoint. It does not mean the agent is publicly accessible on the internet.

Access is still controlled by:
1. Entra ID authentication (token required)
2. RBAC role assignment on the Foundry resource
3. Network access rules on the ACA environment

### How do I roll back a bad copilot update?

Set `ipai_copilot.enabled = False` in Odoo's `ir.config_parameter` to
immediately disable the copilot UI for all users. No module uninstall is needed.

For model rollback, update the `AZURE_OPENAI_DEPLOYMENT` env var to the
previous deployment name and restart the container revision.

### How are evaluations run?

In hosted mode, Foundry's built-in evaluation framework runs against test
datasets stored in the Foundry project. Metrics include groundedness, relevance,
coherence, and custom tool-call accuracy.

In prompt-only mode, batch evaluation scripts run against recorded interaction
logs and measure the same metrics offline.

## Integration

### Does the copilot call external APIs?

The copilot calls Azure AI Foundry and optionally Azure AI Search. It does not
call any other external APIs directly. All Odoo data access is internal via ORM.

Future integrations (e.g., bank API for reconciliation) would be exposed as
Odoo-side tools, not direct copilot-to-external-API calls.

### Can I add custom tools?

Yes. Define the tool in `ssot/odoo/odoo_copilot_finance_tools.yaml` (or a new
domain-specific YAML), implement the Odoo-side endpoint in `ipai_copilot_actions`,
and register it in the tool contract. The copilot will include it in tool
definitions sent to the model.

### Does it work with Odoo mobile?

The copilot UI is rendered in the Odoo web client. On mobile browsers and the
iOS wrapper app, it is accessible via the same web interface. There is no
native mobile copilot UI -- it uses the responsive web panel.
