// modules/security/managed-identity.bicep
// Creates: id-{prefix}-{env} (User-Assigned Managed Identity)
// All ACA containers use this MI for Azure service auth (no API keys)
//
// REFACTOR (C step 1, 2026-04-14): wraps Azure Verified Module
// `avm/res/managed-identity/user-assigned-identity@0.5.0` instead of
// hand-rolled `Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31`.
// Wrapper preserves output names (miResourceId / miPrincipalId / miClientId / miName)
// so that 9+ callers in infra/main.bicep require ZERO changes.
//
// Verified zero functional change via `az deployment group what-if` — see PR.
targetScope = 'resourceGroup'

param prefix   string
param env      string
param location string
param tags     object
@description('Reserved for backward compatibility. Not used by the AVM module.')
param deployPrincipalId string = ''

var miName = 'id-${prefix}-${env}'

// AVM module — pinned to v0.5.0 (latest at 2026-04-14)
module userAssignedIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.5.0' = {
  name: 'avm-mi-${miName}'
  params: {
    name:     miName
    location: location
    tags:     tags
    // No federatedIdentityCredentials, no lockType, no roleAssignments at this layer.
    // Those compose at the consumer layer (Key Vault RBAC, ACA app role assignments).
  }
}

// ── Outputs (preserved interface — same names as pre-AVM module) ───────────
output miResourceId  string = userAssignedIdentity.outputs.resourceId
output miPrincipalId string = userAssignedIdentity.outputs.principalId
output miClientId    string = userAssignedIdentity.outputs.clientId
output miName        string = userAssignedIdentity.outputs.name
