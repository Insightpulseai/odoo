# Examples — palantir-foundry-integration-assessment

## Example 1: No Palantir workload — reject

**Input**: Team proposes "Foundry integration" without specifying which Foundry.

**Output**:
- Palantir workload exists: NO — no Palantir Foundry instance in the organization
- Naming clarification: The proposal likely refers to Azure AI Foundry (Microsoft), not Palantir Foundry
- SDK recommendation: N/A — no Palantir integration needed
- Recommendation: **REJECT** for Palantir scope
- Action: Redirect to `agents/skills/m365-agents-channel-delivery/` if Azure AI Foundry integration is the actual intent
- Evidence: Organization asset inventory shows no Palantir contracts or Foundry instances

## Example 2: Real Palantir workload — proceed with Ontology SDK

**Input**: Data team has an active Palantir Foundry instance with ontology objects for supply chain data. They want to surface ontology objects in the Odoo ERP.

**Output**:
- Palantir workload exists: YES — active Foundry instance with supply chain ontology
- Naming clarification: This is Palantir Foundry (not Microsoft) — confirmed with data team
- SDK recommendation: **Ontology SDK** (ontology-based application development, per Palantir guidance)
- Integration scope: Read-only access to supply chain ontology objects, surfaced in Odoo via `ipai_palantir_bridge` module
- Data flow: Palantir -> Odoo (unidirectional read)
- Recommendation: **PROCEED** with scoped read-only integration
- Evidence: Palantir instance URL confirmed, ontology schema documented, data team sign-off

## Example 3: Naming confusion between Microsoft and Palantir

**Input**: Architecture review mentions "connect our agents to Foundry for backend processing."

**Output**:
- Naming clarification: AMBIGUOUS — "Foundry" could mean either platform
  - **Azure AI Foundry** (Microsoft): Agent backend for M365 Agents SDK — part of our core stack
  - **Palantir Foundry**: External data platform — out-of-scope by default
- Palantir workload exists: NOT CONFIRMED — requires verification
- Recommendation: **DEFER** Palantir assessment; clarify with requestor which Foundry is intended
- If Microsoft: use `agents/skills/m365-agents-channel-delivery/` (already in stack)
- If Palantir: re-run this assessment after confirming workload exists
