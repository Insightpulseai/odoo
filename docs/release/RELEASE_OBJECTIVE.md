# Release Objective

## Release name
Odoo 18 Finance Ops MVP with Pulser Internal Assist

## Release posture
- Internal controlled production
- Human-in-the-loop required
- Odoo remains the sole system of record for workflow, approvals, accounting, tax, expenses, and project state
- Foundry agents and tools are assistive only
- No claim of full Clarity / Concur / Joule / AvaTax parity

## Objective

By [TARGET DATE], ship the Odoo 18 Finance Ops MVP to internal controlled production with Odoo as the sole business system of record, all installed MVP IPAI modules runtime-proven, and Pulser minimally normalized in Foundry with monitoring, approval gates, and repeatable evaluation coverage.

## Success criteria

### 1. MVP module proof
- 7/7 installed MVP IPAI modules are either:
  - test-proven and runtime-proven
  - or explicitly removed from release scope

Included MVP IPAI modules:
- `ipai_odoo_copilot`
- `ipai_copilot_actions`
- `ipai_ai_agent_sources`
- `ipai_tax_intelligence`
- `ipai_hr_expense_liquidation`
- `ipai_expense_ops`
- `ipai_expense_wiring`

### 2. Install and upgrade quality
- Fresh Odoo 18 install: **PASS**
- Representative upgrade path: **PASS**
- No blocking XML/data/security load failures
- No unresolved module dependency failures

### 3. Finance workflow proof
The following critical paths must pass end-to-end in real runtime:

- Cash advance request → approval/release → liquidation → settlement: **PASS**
- Tax validation / blocker / reroute on `account.move`: **PASS**
- TBWA cash advance report rendering: **PASS**
- TBWA liquidation report rendering: **PASS**

### 4. Foundry minimum normalization
- 5/5 active Foundry agents have documented roles
- 0 stale `Odoo CE 19.0` references remain in active Foundry metadata
- Active Foundry model baseline remains bounded to:
  - `gpt-4.1`
  - `wg-pulser`
  - `text-embedding-3-small`
  unless explicit justification is documented

### 5. Foundry governance baseline
- Monitoring enabled for the active agent estate
- At least 1 repeatable evaluation suite exists
- Evaluation coverage includes:
  - relevance
  - groundedness
  - response completeness
  - safety
  - tool-call success / tool selection where applicable
- High-risk actions remain approval-gated
- Credentials are handled through managed identity or project connections
- No credentials in prompts

### 6. Scope control
The following remain explicitly out of release scope:
- OCR baseline
- corporate card feeds
- mobile native app
- Azure AI Search as a default dependency
- Cosmos DB as a default dependency
- Fabric as a default dependency
- workflow orchestration expansion without explicit need
- full sub-agent runtime
- speculative new `ipai_*` module expansion

Success criterion:
- non-MVP features silently added to release: **0**

### 7. Release governance
The following must be complete:
- `ssot/odoo/mvp_matrix.yaml` frozen
- `ssot/odoo/module_install_manifest.yaml` frozen
- `ssot/agent-platform/mcp_policy.yaml` frozen
- `ssot/agent-platform/foundry_tool_policy.yaml` frozen
- evidence pack complete
- rollback plan complete
- deferred list explicit

## Binary release gates

### Gate A -- Module and runtime proof
Pass only if:
- all installed MVP IPAI modules are proven or removed from scope
- fresh install passes
- upgrade path passes

### Gate B -- Business workflow proof
Pass only if:
- finance workflow passes
- tax blocker/reroute flow passes
- required reports render correctly

### Gate C -- Foundry operational minimum
Pass only if:
- active agents have documented roles
- stale metadata is corrected
- monitoring is enabled
- repeatable eval suite exists
- risky actions are approval-gated

### Gate D -- Governance and release readiness
Pass only if:
- SSOT manifests are frozen
- evidence pack is complete
- rollback plan exists
- deferred items remain deferred

## Done means

This release is done only when the bounded Odoo 18 finance workflow runs end-to-end in real runtime, all installed MVP IPAI modules are proven, Pulser remains assistive and approval-gated, and the Foundry estate is governed sufficiently for internal controlled production without expanding into non-MVP platform scope.

## Non-goals
This release does not aim to deliver:
- a fully mature multi-agent platform
- a fully normalized enterprise knowledge platform
- a broad workflow-orchestrated Foundry runtime
- autonomous finance/tax operations
- full vendor-parity claims

## Release statement
If all four release gates pass, the product may be shipped as:

**Internal controlled production -- Odoo 18 Finance Ops MVP with Pulser assistive alpha**
