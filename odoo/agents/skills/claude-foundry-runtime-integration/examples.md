# Claude Foundry Runtime Integration — Examples

## Example 1: Foundry-Hosted (Multi-Model Governance)

```
Integration path: foundry_hosted
Justification: Multiple models (Claude, GPT-4.1) coexist; Foundry manages routing, cost tracking, audit
Deployment: aifoundry-ipai-dev, claude-opus-4-6, version pinned
Runtime: temperature=0.3, max_tokens=4096
Tools: odoo-sales MCP server connected
Validation: PASS — end-to-end query returned correct results
```

## Example 2: Direct API (Simple Integration)

```
Integration path: direct_api
Justification: Single model, minimal governance needs, lowest latency priority
Deployment: N/A (direct API key via Key Vault)
Runtime: temperature=0.2, max_tokens=8192
Tools: None (context provided in prompt)
Validation: PASS — API call returns expected response
```
