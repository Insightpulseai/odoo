#!/usr/bin/env bash
# infra/scripts/post-deploy.sh
# Run AFTER: azd up --environment ipai-prd
# Prereqs: az login, az account set --subscription <prd-sub-id>
# Usage:   ./infra/scripts/post-deploy.sh [step]
#   step: all | entra | pg | kv | fabric | dns | smoke
#         Default: all
set -euo pipefail
IFS=$'\n\t'

ENV="${AZURE_ENV_NAME:-ipai-prd}"
PREFIX="ipai"
REGION="southeastasia"

RG_SECURITY="rg-${PREFIX}-prd-security-sea"
RG_DATA="rg-${PREFIX}-prd-data-sea"
RG_ODOO="rg-${PREFIX}-prd-odoo-sea"
RG_NET="rg-${PREFIX}-prd-net-sea"
RG_AI_EUS2="rg-${PREFIX}-prd-ai-eus2"

KV_NAME="kv-${PREFIX}-prd-sea"
PG_NAME="pg-${PREFIX}-odoo-prd"
AFD_NAME="afd-${PREFIX}-prd"
MI_NAME="id-${PREFIX}-prd"
ACR_NAME="acr${PREFIX}prd"
FOUNDRY_NAME="aif-${PREFIX}-prd"

ODOO_FQDN="erp.insightpulseai.com"
AZURE_DNS_ZONE="insightpulseai.com"
AZURE_DNS_RG="rg-${PREFIX}-prd-net-sea"   # or wherever DNS zone lives

step="${1:-all}"
log() { echo "[$(date -u +%H:%M:%S)] $*"; }
run_step() { [[ "$step" == "all" || "$step" == "$1" ]]; }

# ────────────────────────────────────────────────────────────────
# 1. Entra ID — set PostgreSQL Entra admin to IPAI MI
# ────────────────────────────────────────────────────────────────
if run_step entra; then
  log "=== Step 1: Entra — PG Entra admin ==="
  MI_OBJECT_ID=$(az identity show \
    --name "$MI_NAME" \
    --resource-group "$RG_SECURITY" \
    --query principalId -o tsv)

  # Assign Entra admin on the PG server
  az postgres flexible-server ad-admin create \
    --resource-group "$RG_DATA" \
    --server-name "$PG_NAME" \
    --display-name "$MI_NAME" \
    --object-id "$MI_OBJECT_ID" \
    --type ServicePrincipal || true   # idempotent

  log "PG Entra admin: ${MI_NAME} (${MI_OBJECT_ID})"
fi

# ────────────────────────────────────────────────────────────────
# 2. PostgreSQL — create databases + grant MI access
# ────────────────────────────────────────────────────────────────
if run_step pg; then
  log "=== Step 2: PostgreSQL — DB init + MI grants ==="
  PG_FQDN=$(az postgres flexible-server show \
    --resource-group "$RG_DATA" \
    --name "$PG_NAME" \
    --query fullyQualifiedDomainName -o tsv)

  MI_NAME_SAFE="${MI_NAME//-/_}"  # Entra MI display name uses underscores in PG

  # Get access token for Entra-authenticated PG connection
  PG_TOKEN=$(az account get-access-token \
    --resource-type oss-rdbms \
    --query accessToken -o tsv)

  for DB in odoo odoo_staging odoo_dev; do
    log "Granting MI access to DB: $DB"
    PSQL_CMD=$(cat <<SQL
CREATE USER IF NOT EXISTS "${MI_NAME}" WITH LOGIN;
GRANT CONNECT ON DATABASE ${DB} TO "${MI_NAME}";
GRANT USAGE, CREATE ON SCHEMA public TO "${MI_NAME}";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "${MI_NAME}";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "${MI_NAME}";
SQL
)
    PGPASSWORD="$PG_TOKEN" psql \
      "host=${PG_FQDN} port=5432 dbname=${DB} user=ipaiadmin sslmode=require" \
      --command "$PSQL_CMD" 2>/dev/null || \
      log "WARN: psql unavailable — run SQL grants manually against ${DB}"
  done

  log "PG: wal_level and pgbouncer set via Bicep — verify with:"
  log "  az postgres flexible-server parameter show -g $RG_DATA -s $PG_NAME -n wal_level"
fi

# ────────────────────────────────────────────────────────────────
# 3. Key Vault — store remaining secrets
# ────────────────────────────────────────────────────────────────
if run_step kv; then
  log "=== Step 3: Key Vault — populate remaining secrets ==="

  # ADO PAT for local ADO MCP server (Claude/Pulser integration)
  if [[ -n "${AZURE_ADO_PAT:-}" ]]; then
    az keyvault secret set \
      --vault-name "$KV_NAME" \
      --name "ado-pat-ipai-platform" \
      --value "$AZURE_ADO_PAT" \
      --content-type "Azure DevOps PAT — Read/Write scope — rotate every 90 days"
    log "KV: ado-pat-ipai-platform stored"
  else
    log "WARN: AZURE_ADO_PAT not set — skipping ado-pat-ipai-platform"
    log "  Set with: azd env set AZURE_ADO_PAT <pat>"
  fi

  # Odoo admin master password (used for DB management)
  if [[ -n "${ODOO_MASTER_PASSWORD:-}" ]]; then
    az keyvault secret set \
      --vault-name "$KV_NAME" \
      --name "odoo-master-password" \
      --value "$ODOO_MASTER_PASSWORD" \
      --content-type "Odoo master password (db management) — rotate annually"
    log "KV: odoo-master-password stored"
  fi

  log "KV secrets set. List all: az keyvault secret list --vault-name $KV_NAME -o table"
fi

# ────────────────────────────────────────────────────────────────
# 4. Microsoft Fabric — enable PostgreSQL mirroring (T-003)
# ────────────────────────────────────────────────────────────────
if run_step fabric; then
  log "=== Step 4: Fabric — PostgreSQL mirroring ==="
  log "Manual steps required (Fabric portal):"
  log "  1. Navigate to: app.fabric.microsoft.com"
  log "  2. Workspace: Finance PPM"
  log "  3. New → Mirrored Database → Azure Database for PostgreSQL"
  log "  4. Host: $(az postgres flexible-server show -g $RG_DATA -n $PG_NAME -q fullyQualifiedDomainName -o tsv)"
  log "  5. Select tables: account_move, account_move_line, res_partner,"
  log "                    project_project, account_analytic_line,"
  log "                    hr_timesheet, purchase_order, stock_picking"
  log "  6. Fabric trial deadline: May 20, 2026 — convert to paid before then"
  log ""
  log "Prerequisite check — wal_level must be 'logical':"
  az postgres flexible-server parameter show \
    --resource-group "$RG_DATA" \
    --server-name "$PG_NAME" \
    --name wal_level \
    --query "value" -o tsv | grep -q "logical" && \
    log "  ✅ wal_level=logical confirmed" || \
    log "  ❌ wal_level NOT logical — Bicep param may not have applied yet"
fi

# ────────────────────────────────────────────────────────────────
# 5. DNS — create CNAME for erp.insightpulseai.com → AFD
# ────────────────────────────────────────────────────────────────
if run_step dns; then
  log "=== Step 5: DNS — CNAME erp.insightpulseai.com → AFD ==="
  AFD_ENDPOINT_FQDN=$(az afd endpoint show \
    --profile-name "$AFD_NAME" \
    --endpoint-name "ep-${PREFIX}-odoo-prd" \
    --resource-group "$RG_NET" \
    --query hostName -o tsv 2>/dev/null || echo "ENDPOINT_NOT_FOUND")

  if [[ "$AFD_ENDPOINT_FQDN" != "ENDPOINT_NOT_FOUND" ]]; then
    log "AFD endpoint: $AFD_ENDPOINT_FQDN"

    # Create/update CNAME in Azure DNS
    az network dns record-set cname set-record \
      --resource-group "$AZURE_DNS_RG" \
      --zone-name "$AZURE_DNS_ZONE" \
      --record-set-name "erp" \
      --cname "$AFD_ENDPOINT_FQDN" \
      --ttl 300 && \
      log "✅ CNAME erp.${AZURE_DNS_ZONE} → ${AFD_ENDPOINT_FQDN} created" || \
      log "WARN: CNAME creation failed — create manually in Azure DNS"

    log "AFD custom domain validation token:"
    az afd custom-domain show \
      --profile-name "$AFD_NAME" \
      --custom-domain-name "erp-insightpulseai-com" \
      --resource-group "$RG_NET" \
      --query "validationProperties.validationToken" -o tsv 2>/dev/null || \
      log "  (run az afd custom-domain show to get validation token)"
  else
    log "WARN: AFD endpoint not found — deploy networking module first"
  fi
fi

# ────────────────────────────────────────────────────────────────
# 6. Smoke test — verify all critical endpoints
# ────────────────────────────────────────────────────────────────
if run_step smoke; then
  log "=== Step 6: Smoke tests ==="

  # AFD → Odoo health
  ODOO_URL="https://${ODOO_FQDN}"
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 15 "${ODOO_URL}/web/health" 2>/dev/null || echo "000")
  [[ "$HTTP_CODE" == "200" ]] && \
    log "✅ Odoo health: ${ODOO_URL}/web/health → HTTP ${HTTP_CODE}" || \
    log "❌ Odoo health: ${ODOO_URL}/web/health → HTTP ${HTTP_CODE} (may still be starting)"

  # Key Vault accessible
  az keyvault secret list --vault-name "$KV_NAME" \
    --query "length(@)" -o tsv | \
    xargs -I{} log "✅ Key Vault: $KV_NAME — {} secrets accessible"

  # PG reachable (via az CLI)
  az postgres flexible-server show \
    --resource-group "$RG_DATA" \
    --name "$PG_NAME" \
    --query "state" -o tsv | \
    grep -q "Ready" && \
    log "✅ PostgreSQL: ${PG_NAME} — Ready" || \
    log "❌ PostgreSQL: ${PG_NAME} — not Ready"

  # Foundry accessible
  az cognitiveservices account show \
    --resource-group "$RG_AI_EUS2" \
    --name "$FOUNDRY_NAME" \
    --query "properties.provisioningState" -o tsv | \
    grep -q "Succeeded" && \
    log "✅ Foundry: ${FOUNDRY_NAME} — Succeeded" || \
    log "❌ Foundry: ${FOUNDRY_NAME} — check provisioning state"

  # ACR login server
  ACR_SERVER=$(az acr show --name "$ACR_NAME" \
    --query loginServer -o tsv 2>/dev/null || echo "NOT_FOUND")
  [[ "$ACR_SERVER" != "NOT_FOUND" ]] && \
    log "✅ ACR: ${ACR_SERVER}" || \
    log "❌ ACR: ${ACR_NAME} not found"

  log ""
  log "=== Smoke test complete ==="
  log "Next steps:"
  log "  1. Run: azd monitor --overview (requires Application Insights)"
  log "  2. Install Odoo modules: az containerapp exec --name ca-${PREFIX}-odoo-web-prd"
  log "     → odoo -d odoo --update=base,account,purchase,sale,stock,project --stop-after-init"
  log "  3. Install ipai_* modules: odoo -d odoo --update=ipai_bir_tax_compliance --stop-after-init"
  log "  4. Configure Entra SSO: Settings → Integrations → OAuth Authentication"
fi

log "=== post-deploy.sh complete (step: ${step}) ==="
