#!/usr/bin/env bash
# Update Azure Container App Job modules via REST API
# Uses az rest to bypass CLI argument parsing issues with --flags
set -euo pipefail

: "${RG:?RG required}"
: "${JOB_NAME:?JOB_NAME required}"
: "${MODULES:?MODULES required}"
: "${SUBSCRIPTION_ID:?SUBSCRIPTION_ID required}"
: "${ENV_ID:?ENV_ID required}"
: "${ACR_SERVER:?ACR_SERVER required}"
: "${IMAGE:?IMAGE required}"
: "${DBHOST:?DBHOST required}"
: "${DBUSER:?DBUSER required}"

# Get DB password from Key Vault (never hardcode)
DB_PASSWORD=$(az keyvault secret show --vault-name "${KV_NAME:?KV_NAME required}" \
  -n pg-admin-password --query value -o tsv)

az rest --method PUT \
  --url "https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RG}/providers/Microsoft.App/jobs/${JOB_NAME}?api-version=2024-03-01" \
  --body "{
    \"location\": \"southeastasia\",
    \"properties\": {
      \"environmentId\": \"${ENV_ID}\",
      \"configuration\": {
        \"replicaTimeout\": 600,
        \"replicaRetryLimit\": 0,
        \"triggerType\": \"Manual\",
        \"manualTriggerConfig\": {
          \"parallelism\": 1,
          \"replicaCompletionCount\": 1
        },
        \"registries\": [{
          \"server\": \"${ACR_SERVER}\",
          \"identity\": \"system\"
        }]
      },
      \"template\": {
        \"containers\": [{
          \"name\": \"odoo-install\",
          \"image\": \"${IMAGE}\",
          \"command\": [\"/bin/bash\", \"-c\"],
          \"args\": [\"odoo --db_host \$DBHOST --db_port 5432 --db_user \$DBUSER --db_password \$DBPASS -d odoo -i \$MODULES --stop-after-init --no-http\"],
          \"resources\": { \"cpu\": 1.0, \"memory\": \"2Gi\" },
          \"env\": [
            {\"name\": \"DBHOST\", \"value\": \"${DBHOST}\"},
            {\"name\": \"DBUSER\", \"value\": \"${DBUSER}\"},
            {\"name\": \"DBPASS\", \"value\": \"${DB_PASSWORD}\"},
            {\"name\": \"MODULES\", \"value\": \"${MODULES}\"}
          ]
        }]
      }
    },
    \"identity\": { \"type\": \"SystemAssigned\" }
  }"

echo "Job ${JOB_NAME} updated with modules: ${MODULES}"
