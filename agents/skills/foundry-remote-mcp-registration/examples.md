# Examples — foundry-remote-mcp-registration

## Example 1: Internal Odoo API tool via Azure Functions

**Input**: Register Odoo ERP query tool as remote MCP server. Needs read access to sales orders and invoices.

**Output**:
- Tool: `odoo-erp-query` — read-only access to Odoo sales/invoice data
- Hosting: Azure Functions (`func-ipai-odoo-mcp-dev` in `rg-ipai-dev`)
- Auth: managed identity with RBAC — Function App identity granted Odoo API read scope
- Registration: API Center entry created with metadata (name, auth mode, trust level: internal)
- Connectivity: DNS resolves, health endpoint `/api/health` returns 200, Foundry Agent Service can reach Function App
- Trust boundary: internal Azure-native tool, read-only access, managed identity auth
- Baseline update: added `odoo-erp-query` entry to `ssot/agents/mcp-baseline.yaml`

## Example 2: External Slack notification tool

**Input**: Register Slack webhook tool for agent notifications. Uses Slack incoming webhook URL.

**Output**:
- Tool: `slack-notify` — send notifications to Slack channels
- Hosting: Azure Functions (`func-ipai-slack-mcp-dev` in `rg-ipai-dev`)
- Auth: key-based (Slack webhook URL stored in Key Vault as `slack-webhook-url`)
- Registration: API Center entry created with metadata (name, auth mode, trust level: external-SaaS)
- Connectivity: Function App can reach `hooks.slack.com`, health endpoint responds
- Trust boundary: external SaaS, write-only (notifications), webhook URL in Key Vault with 90-day rotation
- Baseline update: added `slack-notify` entry to `ssot/agents/mcp-baseline.yaml`

## Example 3: Registration blocked — missing auth

**Input**: Developer wants to register a new MCP server but auth design has not been completed.

**Output**:
- BLOCKED: auth configuration is a prerequisite for registration
- Missing: output from `foundry-mcp-auth-design` skill
- Action: complete auth design first, then proceed with registration
- Rationale: never register an MCP tool without a defined auth mode and trust boundary
