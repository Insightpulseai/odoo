# Foundry Tool Policy

> SSOT: `ssot/agent-platform/foundry_tool_policy.yaml`
> Related: `ssot/agent-platform/mcp_policy.yaml`, `docs/architecture/MCP_POLICY.md`
> Last updated: 2026-04-10

## Purpose

This policy defines how Microsoft Foundry tools are selected, configured, and governed for the InsightPulseAI Odoo 18 MVP architecture.

Foundry tools extend agent capabilities, but they do not replace Odoo as the system of record for workflow, approvals, accounting, tax, expenses, or project state.

## Core principles

### 1. Odoo remains the source of truth
Foundry tools may assist, retrieve, analyze, summarize, or orchestrate, but they must not become the authoritative owner of ERP business state.

Prohibited:
- direct accounting truth ownership outside Odoo
- direct tax truth ownership outside Odoo
- direct approval truth ownership outside Odoo
- direct expense or liquidation truth ownership outside Odoo

### 2. Prefer built-in tools first
Use the simplest and most native Foundry tool that fits the use case.

Preferred order:
1. built-in Foundry tools
2. function calling
3. OpenAPI tools
4. MCP tools
5. A2A preview later

### 3. Use the right tool for the job
Built-in tools are preferred when Foundry already provides the capability without extra hosting or custom runtime.

Use built-in tools for:
- web grounding
- uploaded file grounding
- sandboxed code execution
- Azure AI Search grounding where explicitly justified

Use function calling for:
- small application-owned actions
- tightly controlled callbacks executed by your application

Use OpenAPI tools for:
- stable HTTP APIs you own or explicitly trust
- structured service contracts with clear auth and schema

Use MCP for:
- shared remote tool servers
- tooling maintained by another team
- browser automation / diagnostics
- platform and ops tooling
- remote tool ecosystems that fit MCP better than OpenAPI

Use A2A only later and keep it off the MVP critical path unless explicitly required.

## Built-in tools policy

### Approved built-in tools
Approved by default when justified:
- Web search
- File Search
- Code Interpreter
- Function calling
- Azure AI Search
- Azure Functions

### Built-in tool guidance

#### Web search
Use for:
- current public web information
- explicit web grounding
- recent vendor/platform facts

Do not use for:
- internal ERP truth
- internal policy truth if File Search or internal KB is the better source

#### File Search
Use for:
- uploaded files
- internal KB grounding
- document-backed answers
- policy/SOP/help grounding

Do not use for:
- replacing live Odoo state
- broad speculative retrieval when direct Odoo or service calls are more correct

#### Code Interpreter
Use for:
- calculations
- dataset analysis
- charts
- transformations
- controlled analytical workflows

Do not use for:
- hidden business-state mutation
- acting as a transaction processor

#### Azure AI Search
Use only when:
- an existing index is justified
- retrieval quality needs exceed simple File Search
- indexed enterprise knowledge is a real requirement

Do not make Azure AI Search a default MVP dependency unless explicitly required.

#### Azure Functions
Use for:
- bounded custom actions
- server-side controlled execution
- lightweight extension points

## Custom tools policy

### Function calling
Use when your application should execute the action directly and return the result to the agent.

Best for:
- tightly scoped internal actions
- deterministic application-owned callbacks
- Odoo-side or agent-platform-side controlled operations

### OpenAPI tools
Use for:
- internal or trusted HTTP APIs
- stable contracts
- explicit authentication schemes
- productized service surfaces

Prefer OpenAPI over MCP when:
- you own the API
- the schema is stable
- the action surface is well-defined
- you do not need MCP-specific tool-server behavior

### MCP tools
Use MCP when:
- the server is already MCP-native
- the tool surface is shared across multiple agents
- the tool is externally maintained
- browser or ops tooling is better exposed through MCP
- the use case benefits from remote tool discovery and tool governance

MCP requires:
- allow-listing where supported
- approvals for high-risk operations
- project connections or managed identity for auth
- audit logging for tool calls and approvals

See `docs/architecture/MCP_POLICY.md` for detailed MCP guardrails.

### A2A
Treat Agent-to-Agent as preview and keep it off the MVP critical path by default.

## Authentication policy

### Default rules
- never place credentials in prompts
- never hard-code secrets in agent definitions
- prefer project connections for external credentials
- prefer Microsoft Entra / managed identity when supported

### Preferred auth order
1. Microsoft Entra / managed identity
2. Foundry project connections
3. API key only when required by the provider

## Structured inputs policy

Use structured inputs to avoid creating unnecessary agent-version sprawl.

Structured inputs are preferred for:
- environment-specific values
- customer-specific vector store IDs
- per-request MCP endpoint details where appropriate
- per-request tool configuration overrides

Keep agent definitions stable and inject context-specific values at runtime.

## Approval and risk controls

### Require approval for high-risk operations
High-risk tool calls must require approval, especially if they:
- write data
- change resources
- perform sensitive finance/tax actions
- touch production-facing systems
- invoke powerful external tools

### Review before approval
Review:
- requested tool name
- arguments
- target system
- scope of action

### Audit requirements
Log:
- tool selection
- approval decisions
- tool arguments where safe
- execution outcomes
- failures and retries

Avoid logging secrets or sensitive prompt content.

## Preview tools policy

Preview tools are not on the MVP critical path by default.

Keep these off the critical path unless explicitly justified:
- Browser Automation (preview)
- Computer Use (preview)
- Microsoft Fabric (preview)
- SharePoint (preview)
- A2A (preview)
- any preview MCP dependency with no proven operational need

## Current Foundry baseline for this architecture

### Project baseline
- Foundry project: `ipai-copilot`
- parent resource: `ipai-copilot-resource`
- region: `eastus2`
- project endpoint: `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot`

### Confirmed connections
- AI Services
- Azure Storage Account
- Bing grounding

Do not assume other connections are present unless explicitly verified.

## Repo boundaries

### odoo
Owns:
- ERP truth
- approvals
- accounting
- tax
- expense and liquidation state
- business rules
- final write path

### agent-platform
Owns:
- Foundry runtime integration
- tool binding
- tool policy implementation
- approval and audit plumbing
- retrieval and attachment handling
- chat backend and orchestration runtime

### agents
Owns:
- tool routing metadata
- allowed tool lists
- skill contracts
- evals for tool usage
- sub-agent tool policies

### web
Owns:
- optional browser-facing shells
- companion UX
- external assistant surfaces

## Default tool mapping for the MVP

### Pulser / reverse SAP Joule
Prefer:
- File Search for policies, SOPs, help, and uploaded docs
- Web search for current public information
- Function calling or OpenAPI for controlled internal actions
- MCP only for external/shared tool servers where appropriate

### Reverse SAP Concur
Prefer:
- Odoo truth for workflows
- File Search for policy/help grounding
- Function calling / OpenAPI for bounded companion actions
- MCP only for optional browser or external tool surfaces

### Reverse AvaTax
Prefer:
- Odoo truth for tax/accounting state
- File Search for compliance reference grounding
- Function calling / OpenAPI for controlled review-plane actions
- MCP only for bounded external tools or ops workflows

### PPM
Prefer:
- Odoo CE + OCA as functional baseline
- File Search / Web search only where assistant grounding is useful
- avoid adding heavy tool complexity unless operator-assistant use is explicitly in scope

## Prohibited patterns

- using Foundry tools as ERP truth
- replacing Odoo workflows with tool-only orchestration
- using MCP when built-in tools or OpenAPI are a simpler and safer fit
- creating environment-specific agent sprawl instead of using structured inputs
- putting preview tools on the MVP critical path without explicit justification
