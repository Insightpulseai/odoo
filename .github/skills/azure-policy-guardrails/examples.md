# azure-policy-guardrails -- Worked Examples

## Example 1: Require Tags on Resource Groups (Bicep)

```bicep
// Built-in policy: "Require a tag on resource groups"
// Policy definition ID: /providers/Microsoft.Authorization/policyDefinitions/96670d01-0a4d-4649-9c89-2d3abc0a5025

resource policyRequireEnvTag 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'require-environment-tag'
  properties: {
    displayName: 'Require environment tag on resource groups'
    policyDefinitionId: '/providers/Microsoft.Authorization/policyDefinitions/96670d01-0a4d-4649-9c89-2d3abc0a5025'
    parameters: {
      tagName: { value: 'environment' }
    }
    enforcementMode: 'Default'    // Start with 'DoNotEnforce' for audit-only
  }
}

resource policyRequireOwnerTag 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'require-owner-tag'
  properties: {
    displayName: 'Require owner tag on resource groups'
    policyDefinitionId: '/providers/Microsoft.Authorization/policyDefinitions/96670d01-0a4d-4649-9c89-2d3abc0a5025'
    parameters: {
      tagName: { value: 'owner' }
    }
    enforcementMode: 'Default'
  }
}
```

## Example 2: Deny Public PG Access (Bicep)

```bicep
// Built-in policy: "Public network access should be disabled for PostgreSQL flexible servers"
// Policy definition ID: /providers/Microsoft.Authorization/policyDefinitions/5e1de0e3-42cb-4ebc-a86d-61d0c619ca48

resource policyDenyPublicPg 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'deny-public-pg-access'
  properties: {
    displayName: 'Deny public network access for PostgreSQL flexible servers'
    policyDefinitionId: '/providers/Microsoft.Authorization/policyDefinitions/5e1de0e3-42cb-4ebc-a86d-61d0c619ca48'
    enforcementMode: 'Default'
  }
}
```

## Example 3: Audit Key Vault Usage (Bicep)

```bicep
// Custom policy or built-in initiative: "Key vaults should have soft delete enabled"
// Use as proxy -- full KV-required-for-secrets is a custom policy.
// Built-in: /providers/Microsoft.Authorization/policyDefinitions/1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d

resource policyAuditKvSoftDelete 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'audit-kv-soft-delete'
  properties: {
    displayName: 'Audit Key Vaults without soft delete'
    policyDefinitionId: '/providers/Microsoft.Authorization/policyDefinitions/1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d'
    enforcementMode: 'Default'
  }
}
```

## Example 4: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure Policy require tag resource group built-in")
Result: Built-in policy "Require a tag on resource groups" (ID: 96670d01...).
        Effect: Deny. Parameters: tagName. Scope: subscription or RG.
        Assign once per required tag.

Step 2: microsoft_docs_search("Azure Policy deny public network access PostgreSQL")
Result: Built-in policy "Public network access should be disabled for
        PostgreSQL flexible servers" (ID: 5e1de0e3...). Effect: Audit or Deny.
        Applies to Microsoft.DBforPostgreSQL/flexibleServers.

Step 3: microsoft_docs_search("Azure Policy audit Key Vault usage secrets")
Result: Multiple built-in policies for KV: soft delete, purge protection,
        network rules. For secret management enforcement, combine with
        custom policy or use Defender for Cloud recommendation.
```

## Example 5: Audit-to-Deny Rollout Plan

```markdown
## Policy Rollout Plan

### Week 1: Audit Mode
- Deploy all policies with `enforcementMode: 'DoNotEnforce'`
- Review compliance dashboard: `az policy state summarize --subscription <id>`
- Document non-compliant resources and remediation plan

### Week 2: Remediation
- Fix non-compliant resources:
  - Add missing tags to resource groups
  - Disable public PG access (requires VNet integration first)
  - Enable KV soft delete
- Re-run compliance check

### Week 3: Enforce
- Switch `enforcementMode` to `'Default'` on tag and PG policies
- KV policy remains in Audit until all services migrate to KV refs
```
