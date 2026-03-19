#!/usr/bin/env bash
# =============================================================================
# Self-Hosted Supabase Deployment — Azure VM with Docker Compose
# =============================================================================
# Deploys the full Supabase stack to an Azure VM using Docker Compose.
# Idempotent: safe to run multiple times.
#
# Prerequisites:
#   - Azure CLI (az) authenticated
#   - Docker + Docker Compose on the target VM
#   - .env.supabase with all secrets populated
#   - SSH access to the target VM
#
# Usage:
#   ./deploy.sh                    # Deploy with defaults
#   ./deploy.sh --dry-run          # Validate only, no deployment
#   ./deploy.sh --vm-ip 1.2.3.4   # Deploy to specific VM IP
#
# SECRETS POLICY: Secrets are read from .env.supabase or Azure Key Vault.
# Never passed as CLI arguments. Never logged.
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration (override via environment or CLI flags)
# ---------------------------------------------------------------------------
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-rg-ipai-agents-dev}"
LOCATION="${AZURE_LOCATION:-southeastasia}"
VM_NAME="${AZURE_VM_NAME:-vm-ipai-supabase-dev}"
VM_SIZE="${AZURE_VM_SIZE:-Standard_B4ms}"
VM_IP="${AZURE_VM_IP:-}"
KEY_VAULT_NAME="${AZURE_KEY_VAULT:-kv-ipai-dev}"
COMPOSE_FILE="docker-compose.supabase.yml"
ENV_FILE=".env.supabase"
DEPLOY_DIR="/opt/supabase"
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)    DRY_RUN=true; shift ;;
    --vm-ip)      VM_IP="$2"; shift 2 ;;
    --vm-name)    VM_NAME="$2"; shift 2 ;;
    --rg)         RESOURCE_GROUP="$2"; shift 2 ;;
    --location)   LOCATION="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $0 [--dry-run] [--vm-ip IP] [--vm-name NAME] [--rg RG] [--location LOC]"
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Color output
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ---------------------------------------------------------------------------
# Step 1: Validate required environment variables
# ---------------------------------------------------------------------------
validate_env() {
  log_info "Validating environment configuration..."

  local env_path="${SCRIPT_DIR}/${ENV_FILE}"
  if [[ ! -f "$env_path" ]]; then
    log_error ".env.supabase not found at ${env_path}"
    log_error "Copy .env.supabase.example to .env.supabase and fill in all values."
    exit 1
  fi

  # Source env file to check required vars (in subshell to avoid polluting)
  local missing=()
  local required_vars=(
    POSTGRES_PASSWORD
    JWT_SECRET
    ANON_KEY
    SERVICE_ROLE_KEY
    DASHBOARD_USERNAME
    DASHBOARD_PASSWORD
    SMTP_USER
    SMTP_PASS
    SMTP_ADMIN_EMAIL
    REALTIME_DB_ENC_KEY
    REALTIME_SECRET_KEY_BASE
    LOGFLARE_API_KEY
  )

  # shellcheck disable=SC1090
  source "$env_path"

  for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]] || [[ "${!var}" == *"PLACEHOLDER"* ]] || [[ "${!var}" == *"your-"* ]] || [[ "${!var}" == *"change-me"* ]]; then
      missing+=("$var")
    fi
  done

  if [[ ${#missing[@]} -gt 0 ]]; then
    log_error "Missing or placeholder values for required environment variables:"
    for var in "${missing[@]}"; do
      log_error "  - $var"
    done
    exit 1
  fi

  # Validate JWT_SECRET length
  if [[ ${#JWT_SECRET} -lt 32 ]]; then
    log_error "JWT_SECRET must be at least 32 characters long (got ${#JWT_SECRET})"
    exit 1
  fi

  log_ok "All required environment variables present."
}

# ---------------------------------------------------------------------------
# Step 2: Ensure Azure resource group exists
# ---------------------------------------------------------------------------
ensure_resource_group() {
  log_info "Ensuring resource group '${RESOURCE_GROUP}' exists in '${LOCATION}'..."

  if az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    log_ok "Resource group '${RESOURCE_GROUP}' already exists."
  else
    if [[ "$DRY_RUN" == "true" ]]; then
      log_warn "[DRY-RUN] Would create resource group '${RESOURCE_GROUP}' in '${LOCATION}'"
    else
      az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --tags "project=insightpulseai" "service=supabase" "environment=dev" \
        --output none
      log_ok "Created resource group '${RESOURCE_GROUP}'."
    fi
  fi
}

# ---------------------------------------------------------------------------
# Step 3: Ensure Azure VM exists (or use provided IP)
# ---------------------------------------------------------------------------
ensure_vm() {
  if [[ -n "$VM_IP" ]]; then
    log_info "Using provided VM IP: ${VM_IP}"
    return
  fi

  log_info "Checking for VM '${VM_NAME}' in '${RESOURCE_GROUP}'..."

  if az vm show --name "$VM_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    VM_IP=$(az vm show \
      --name "$VM_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --show-details \
      --query "publicIps" \
      --output tsv)
    log_ok "VM '${VM_NAME}' exists at IP: ${VM_IP}"
  else
    if [[ "$DRY_RUN" == "true" ]]; then
      log_warn "[DRY-RUN] Would create VM '${VM_NAME}' (${VM_SIZE}) in '${RESOURCE_GROUP}'"
      VM_IP="<pending>"
      return
    fi

    log_info "Creating VM '${VM_NAME}' (${VM_SIZE})..."
    az vm create \
      --resource-group "$RESOURCE_GROUP" \
      --name "$VM_NAME" \
      --image "Ubuntu2204" \
      --size "$VM_SIZE" \
      --admin-username azureuser \
      --generate-ssh-keys \
      --public-ip-sku Standard \
      --nsg-rule SSH \
      --tags "project=insightpulseai" "service=supabase" "environment=dev" \
      --output none

    VM_IP=$(az vm show \
      --name "$VM_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --show-details \
      --query "publicIps" \
      --output tsv)

    # Open required ports
    az vm open-port \
      --resource-group "$RESOURCE_GROUP" \
      --name "$VM_NAME" \
      --port 80,443,8000,8443 \
      --priority 1100 \
      --output none

    log_ok "VM created at IP: ${VM_IP}"

    # Install Docker on the VM
    log_info "Installing Docker on VM..."
    ssh -o StrictHostKeyChecking=no "azureuser@${VM_IP}" << 'INSTALL_DOCKER'
      sudo apt-get update -qq
      sudo apt-get install -y -qq ca-certificates curl gnupg
      sudo install -m 0755 -d /etc/apt/keyrings
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
      sudo chmod a+r /etc/apt/keyrings/docker.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
      sudo apt-get update -qq
      sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
      sudo usermod -aG docker azureuser
INSTALL_DOCKER
    log_ok "Docker installed on VM."
  fi
}

# ---------------------------------------------------------------------------
# Step 4: Sync deployment files to VM
# ---------------------------------------------------------------------------
sync_files() {
  if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "[DRY-RUN] Would sync deployment files to ${VM_IP}:${DEPLOY_DIR}"
    return
  fi

  log_info "Syncing deployment files to VM..."

  local ssh_target="azureuser@${VM_IP}"

  # Create deploy directory
  ssh -o StrictHostKeyChecking=no "$ssh_target" "sudo mkdir -p ${DEPLOY_DIR} && sudo chown azureuser:azureuser ${DEPLOY_DIR}"

  # Sync compose file, kong config, env file
  scp -o StrictHostKeyChecking=no \
    "${SCRIPT_DIR}/${COMPOSE_FILE}" \
    "${SCRIPT_DIR}/${ENV_FILE}" \
    "${ssh_target}:${DEPLOY_DIR}/"

  # Sync volumes directory (kong config, etc.)
  ssh -o StrictHostKeyChecking=no "$ssh_target" "mkdir -p ${DEPLOY_DIR}/volumes/api ${DEPLOY_DIR}/volumes/functions ${DEPLOY_DIR}/volumes/db ${DEPLOY_DIR}/volumes/logs"

  scp -o StrictHostKeyChecking=no \
    "${SCRIPT_DIR}/volumes/api/kong.yml" \
    "${ssh_target}:${DEPLOY_DIR}/volumes/api/"

  # Sync Vector config if it exists
  if [[ -f "${SCRIPT_DIR}/volumes/logs/vector.yml" ]]; then
    scp -o StrictHostKeyChecking=no \
      "${SCRIPT_DIR}/volumes/logs/vector.yml" \
      "${ssh_target}:${DEPLOY_DIR}/volumes/logs/"
  fi

  # Sync DB init scripts if they exist
  for sql_file in "${SCRIPT_DIR}"/volumes/db/*.sql; do
    [[ -f "$sql_file" ]] || continue
    scp -o StrictHostKeyChecking=no "$sql_file" "${ssh_target}:${DEPLOY_DIR}/volumes/db/"
  done

  log_ok "Files synced to ${VM_IP}:${DEPLOY_DIR}"
}

# ---------------------------------------------------------------------------
# Step 5: Deploy with Docker Compose
# ---------------------------------------------------------------------------
deploy_stack() {
  if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "[DRY-RUN] Would deploy Supabase stack on ${VM_IP}"
    return
  fi

  log_info "Deploying Supabase stack on VM..."

  local ssh_target="azureuser@${VM_IP}"

  ssh -o StrictHostKeyChecking=no "$ssh_target" << EOF
    cd ${DEPLOY_DIR}
    docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} pull
    docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} up -d
EOF

  log_ok "Supabase stack deployed."
}

# ---------------------------------------------------------------------------
# Step 6: Health checks
# ---------------------------------------------------------------------------
run_health_checks() {
  if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "[DRY-RUN] Would run health checks against ${VM_IP}"
    return
  fi

  log_info "Waiting 30s for services to initialize..."
  sleep 30

  log_info "Running health checks..."

  local base_url="http://${VM_IP}:8000"
  local all_ok=true

  declare -A endpoints=(
    ["Kong API Gateway"]="${base_url}"
    ["Auth (GoTrue)"]="${base_url}/auth/v1/health"
    ["PostgREST"]="${base_url}/rest/v1/"
    ["Storage"]="${base_url}/storage/v1/status"
  )

  for service in "${!endpoints[@]}"; do
    local url="${endpoints[$service]}"
    local status
    status=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")

    if [[ "$status" =~ ^2[0-9][0-9]$ ]]; then
      log_ok "${service}: HTTP ${status}"
    else
      log_error "${service}: HTTP ${status} (expected 2xx)"
      all_ok=false
    fi
  done

  # Check Studio separately (different port)
  local studio_status
  studio_status=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 10 "http://${VM_IP}:54323" 2>/dev/null || echo "000")
  if [[ "$studio_status" =~ ^[23][0-9][0-9]$ ]]; then
    log_ok "Studio Dashboard: HTTP ${studio_status}"
  else
    log_warn "Studio Dashboard: HTTP ${studio_status} (may still be starting)"
  fi

  # Check PostgreSQL via SSH
  local pg_status
  pg_status=$(ssh -o StrictHostKeyChecking=no "azureuser@${VM_IP}" \
    "docker compose -f ${DEPLOY_DIR}/${COMPOSE_FILE} exec -T db pg_isready -U postgres" 2>/dev/null && echo "ok" || echo "fail")
  if [[ "$pg_status" == "ok" ]]; then
    log_ok "PostgreSQL: accepting connections"
  else
    log_error "PostgreSQL: not ready"
    all_ok=false
  fi

  if [[ "$all_ok" == "true" ]]; then
    log_ok "All health checks passed."
  else
    log_error "Some health checks failed. Check logs with:"
    log_error "  ssh azureuser@${VM_IP} 'cd ${DEPLOY_DIR} && docker compose -f ${COMPOSE_FILE} logs'"
    exit 1
  fi
}

# ---------------------------------------------------------------------------
# Step 7: Output connection details
# ---------------------------------------------------------------------------
print_summary() {
  echo ""
  echo "============================================================================="
  echo " Supabase Self-Hosted Deployment Summary"
  echo "============================================================================="
  echo ""

  if [[ "$DRY_RUN" == "true" ]]; then
    echo " MODE:           DRY RUN (no changes made)"
    echo ""
  fi

  echo " VM:             ${VM_NAME}"
  echo " IP:             ${VM_IP}"
  echo " Resource Group: ${RESOURCE_GROUP}"
  echo " Location:       ${LOCATION}"
  echo ""
  echo " Service URLs (direct, before DNS/reverse proxy):"
  echo "   API Gateway:  http://${VM_IP}:8000"
  echo "   Studio:       http://${VM_IP}:54323"
  echo "   PostgreSQL:   postgresql://postgres:***@${VM_IP}:54322/postgres"
  echo ""
  echo " Target DNS (configure in Cloudflare):"
  echo "   supabase.insightpulseai.com  ->  A  ${VM_IP}"
  echo ""
  echo " After DNS + reverse proxy setup:"
  echo "   API:          https://supabase.insightpulseai.com"
  echo "   Studio:       https://supabase.insightpulseai.com:54323"
  echo ""
  echo " Key Vault:      ${KEY_VAULT_NAME} (store secrets here for rotation)"
  echo ""
  echo " Next steps:"
  echo "   1. Add DNS A record: supabase.insightpulseai.com -> ${VM_IP}"
  echo "   2. Configure reverse proxy (nginx/caddy) for TLS termination"
  echo "   3. Store secrets in Azure Key Vault: ${KEY_VAULT_NAME}"
  echo "   4. Run Supabase migrations from the supabase/ directory"
  echo "============================================================================="
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  echo ""
  log_info "=== Self-Hosted Supabase Deployment (Azure VM) ==="
  echo ""

  validate_env
  ensure_resource_group
  ensure_vm
  sync_files
  deploy_stack
  run_health_checks
  print_summary
}

main "$@"
