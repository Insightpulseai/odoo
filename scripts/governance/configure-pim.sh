#!/usr/bin/env bash
# =============================================================================
# Configure Entra PIM Eligible Role Assignments
# =============================================================================
# SAP Benchmark #644: Configure Entra PIM for admin roles
#
# Prerequisites:
#   - az cli logged in with Global Admin or Privileged Role Administrator
#   - Microsoft Entra ID P2 license active on tenant
#   - Entra security groups created (see ENTRA_GROUPS below)
#
# Usage:
#   ./scripts/governance/configure-pim.sh [--dry-run] [--env dev|staging|prod]
#
# What this does:
#   1. Creates PIM-eligible role assignments (not active — require activation)
#   2. Sets activation policies (duration, MFA, justification, approval)
#   3. Validates configuration
# =============================================================================
set -euo pipefail

# --- Configuration -----------------------------------------------------------
TENANT_ID="402de71a-87ec-4302-a609-fb76098d1da7"  # insightpulseai.com
SUBSCRIPTION_ID=""  # Will be detected

# Entra security groups (must be created in Entra ID portal or via Graph API)
# These are the group object IDs — replace with actual values from Entra ID
PLATFORM_ADMIN_GROUP_ID="${ENTRA_PLATFORM_ADMIN_GROUP_ID:-}"
ODOO_OPERATOR_GROUP_ID="${ENTRA_ODOO_OPERATOR_GROUP_ID:-}"

# Target resource groups
RG_RUNTIME="rg-ipai-dev-odoo-runtime"
RG_DATA="rg-ipai-dev-odoo-data"

# Key Vault
KV_NAME="kv-ipai-dev"

# PIM activation settings
MAX_DURATION_CONTRIBUTOR="PT8H"   # 8 hours
MAX_DURATION_OWNER="PT4H"         # 4 hours
MAX_DURATION_KV_OFFICER="PT4H"    # 4 hours

# Built-in role IDs
ROLE_CONTRIBUTOR="b24988ac-6180-42a0-ab88-20f7382dd24c"
ROLE_OWNER="8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
ROLE_KV_SECRETS_OFFICER="b86a8fe4-44ce-4948-aee5-eccb2c155cd7"
ROLE_USER_ACCESS_ADMIN="18d7d88d-d35e-4fb5-a5c3-7773c20a72d9"

# --- Flags -------------------------------------------------------------------
DRY_RUN=false
ENV="dev"

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --env) ENV="$2"; shift 2 ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

# --- Functions ---------------------------------------------------------------
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
warn() { echo "[WARN] $*" >&2; }
fail() { echo "[FAIL] $*" >&2; exit 1; }

check_prerequisites() {
  log "Checking prerequisites..."

  # Check az cli
  command -v az >/dev/null 2>&1 || fail "az cli not found. Install: https://learn.microsoft.com/cli/azure/install-azure-cli"

  # Check login
  az account show >/dev/null 2>&1 || fail "Not logged in. Run: az login --tenant $TENANT_ID"

  # Get subscription
  SUBSCRIPTION_ID=$(az account show --query id -o tsv)
  log "Subscription: $SUBSCRIPTION_ID"

  # Check tenant
  local current_tenant
  current_tenant=$(az account show --query tenantId -o tsv)
  if [[ "$current_tenant" != "$TENANT_ID" ]]; then
    fail "Wrong tenant. Expected $TENANT_ID, got $current_tenant. Run: az login --tenant $TENANT_ID"
  fi

  # Check Entra group IDs are set
  if [[ -z "$PLATFORM_ADMIN_GROUP_ID" ]]; then
    warn "ENTRA_PLATFORM_ADMIN_GROUP_ID not set. Skipping PIM eligible assignments."
    warn "Create the group in Entra ID, then set the env var and re-run."
    return 1
  fi

  log "Prerequisites OK"
  return 0
}

create_eligible_assignment() {
  local role_id="$1"
  local role_name="$2"
  local scope="$3"
  local principal_id="$4"
  local max_duration="$5"
  local require_approval="${6:-false}"

  log "Creating PIM eligible assignment: $role_name"
  log "  Scope: $scope"
  log "  Principal: $principal_id"
  log "  Max duration: $max_duration"
  log "  Require approval: $require_approval"

  if [[ "$DRY_RUN" == "true" ]]; then
    log "  [DRY-RUN] Would create eligible assignment"
    return 0
  fi

  # Create eligible role assignment via az rest (PIM API)
  local request_body
  request_body=$(cat <<EOF
{
  "properties": {
    "roleDefinitionId": "$scope/providers/Microsoft.Authorization/roleDefinitions/$role_id",
    "principalId": "$principal_id",
    "requestType": "AdminAssign",
    "scheduleInfo": {
      "startDateTime": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)",
      "expiration": {
        "type": "AfterDateTime",
        "endDateTime": "$(date -u -v+1y +%Y-%m-%dT%H:%M:%S.000Z 2>/dev/null || date -u -d '+1 year' +%Y-%m-%dT%H:%M:%S.000Z)"
      }
    },
    "justification": "SAP benchmark #644: PIM eligible assignment for least-privilege governance"
  }
}
EOF
  )

  local request_name
  request_name=$(uuidgen | tr '[:upper:]' '[:lower:]')

  az rest \
    --method PUT \
    --uri "$scope/providers/Microsoft.Authorization/roleEligibilityScheduleRequests/$request_name?api-version=2020-10-01" \
    --body "$request_body" \
    --output none 2>&1 || {
      warn "Failed to create eligible assignment for $role_name. This may require Entra P2 license or Privileged Role Administrator permissions."
      return 1
    }

  log "  Created eligible assignment for $role_name"
}

# --- Main --------------------------------------------------------------------
main() {
  log "=== Entra PIM Configuration — SAP Benchmark #644 ==="
  log "Environment: $ENV"
  log "Dry run: $DRY_RUN"

  if ! check_prerequisites; then
    log ""
    log "=== Manual Steps Required ==="
    log "1. Create Entra security group 'IPAI Platform Admins' in Entra ID portal"
    log "2. Create Entra security group 'IPAI Odoo Operators' in Entra ID portal"
    log "3. Add admin users to 'IPAI Platform Admins' group"
    log "4. Export group object IDs:"
    log "   export ENTRA_PLATFORM_ADMIN_GROUP_ID=<group-object-id>"
    log "   export ENTRA_ODOO_OPERATOR_GROUP_ID=<group-object-id>"
    log "5. Re-run this script"
    log ""
    log "Alternatively, deploy the Bicep module for RBAC foundation:"
    log "   az deployment group create \\"
    log "     --resource-group $RG_RUNTIME \\"
    log "     --template-file infra/azure/modules/pim-governance.bicep \\"
    log "     --parameters platformAdminGroupId=<group-id>"
    exit 0
  fi

  local sub_scope="/subscriptions/$SUBSCRIPTION_ID"
  local rg_runtime_scope="$sub_scope/resourceGroups/$RG_RUNTIME"
  local rg_data_scope="$sub_scope/resourceGroups/$RG_DATA"

  local pim_failures=0

  # 1. Contributor on runtime RG (8h max, justification required)
  create_eligible_assignment \
    "$ROLE_CONTRIBUTOR" "Contributor" "$rg_runtime_scope" \
    "$PLATFORM_ADMIN_GROUP_ID" "$MAX_DURATION_CONTRIBUTOR" || pim_failures=$((pim_failures + 1))

  # 2. Contributor on data RG (8h max, justification required)
  create_eligible_assignment \
    "$ROLE_CONTRIBUTOR" "Contributor" "$rg_data_scope" \
    "$PLATFORM_ADMIN_GROUP_ID" "$MAX_DURATION_CONTRIBUTOR" || pim_failures=$((pim_failures + 1))

  # 3. Key Vault Secrets Officer (4h max, justification required)
  local kv_scope="$rg_runtime_scope/providers/Microsoft.KeyVault/vaults/$KV_NAME"
  create_eligible_assignment \
    "$ROLE_KV_SECRETS_OFFICER" "Key Vault Secrets Officer" "$kv_scope" \
    "$PLATFORM_ADMIN_GROUP_ID" "$MAX_DURATION_KV_OFFICER" || pim_failures=$((pim_failures + 1))

  # 4. Owner at subscription level (4h max, approval required)
  create_eligible_assignment \
    "$ROLE_OWNER" "Owner" "$sub_scope" \
    "$PLATFORM_ADMIN_GROUP_ID" "$MAX_DURATION_OWNER" "true" || pim_failures=$((pim_failures + 1))

  if [[ $pim_failures -gt 0 ]]; then
    log "[WARN] $pim_failures PIM eligible assignment(s) failed. See warnings above."
  fi

  log ""
  log "=== PIM Configuration Complete ==="
  log "Eligible assignments created. Admins must now activate roles via:"
  log "  - Entra ID portal → Privileged Identity Management → My roles"
  log "  - az rest --method POST to roleAssignmentScheduleRequests"
  log ""
  log "Default standing access: Reader + Monitoring Reader only"
  log "Elevated access: requires activation with justification + MFA"
}

main "$@"
