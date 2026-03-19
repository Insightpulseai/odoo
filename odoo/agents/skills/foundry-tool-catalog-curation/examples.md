# Examples — foundry-tool-catalog-curation

## Example 1: Azure-native tool — approved

**Input**: Proposal to add Azure Cosmos DB query tool as remote MCP server. Uses managed identity.

**Output**:
- Tool: `cosmos-db-query` (remote MCP)
- Auth mode: managed identity — MEETS REQUIREMENT (preferred tier)
- Provider trust: Microsoft Azure — HIGH
- Category: data access — APPROVED CATEGORY
- Baseline check: no conflict in mcp-baseline.yaml
- Verdict: APPROVED
- Rationale: Azure-native tool with managed identity auth, trusted provider, approved category

## Example 2: External API tool — conditional

**Input**: Proposal to add Stripe payment webhook tool as remote MCP server. Currently uses API key.

**Output**:
- Tool: `stripe-webhook` (remote MCP)
- Auth mode: API key — BELOW PREFERRED (key-based is last resort)
- Provider trust: Stripe — MODERATE (external SaaS)
- Category: external API — APPROVED CATEGORY
- Baseline check: no conflict in mcp-baseline.yaml
- Verdict: CONDITIONAL
- Conditions: (1) API key must be stored in Azure Key Vault, (2) evaluate if OAuth2 is available from Stripe, (3) define trust boundary documentation
- Rationale: external provider, key-based auth is acceptable as last resort only if Key Vault stored

## Example 3: Unregistered tool — forbidden

**Input**: Developer wants to use a custom Python script as a "tool" without MCP registration.

**Output**:
- Tool: `custom-python-script` (unregistered)
- Auth mode: none — DOES NOT MEET REQUIREMENT
- Provider trust: unknown — UNASSESSED
- Category: unclassified
- Baseline check: not in mcp-baseline.yaml
- Verdict: FORBIDDEN
- Rationale: unregistered tools cannot be approved; must be registered as local or remote MCP with proper auth before evaluation

## Example 4: Duplicate tool detected

**Input**: Proposal to add a second Bing search tool when native Foundry Bing grounding already exists.

**Output**:
- Tool: `bing-search-custom` (remote MCP)
- Baseline check: DUPLICATE — native Foundry Bing grounding already in baseline
- Verdict: FORBIDDEN
- Rationale: native Foundry tool covers this capability; adding a custom remote MCP creates unnecessary complexity and auth surface
