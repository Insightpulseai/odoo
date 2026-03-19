#!/usr/bin/env bash
# scripts/ci/check_secret_drift.sh
# Verify Odoo ACA apps use Key Vault references for db-password, not plain secrets.
# Exit: 0 if all pass, 1 if any app has a plain (non-KV) db-password secret.
set -euo pipefail

RG="${1:-rg-ipai-dev}"
APPS=("ipai-odoo-dev-web" "ipai-odoo-dev-worker" "ipai-odoo-dev-cron")
FAIL=0

echo "Checking secret-source integrity for Odoo ACA apps in ${RG}"
echo "---"

for app in "${APPS[@]}"; do
  KV_URL=$(az containerapp show -n "$app" -g "$RG" \
    --query "properties.configuration.secrets[?name=='db-password'].keyVaultUrl | [0]" -o tsv 2>/dev/null)

  if [ -z "$KV_URL" ] || [ "$KV_URL" = "None" ]; then
    echo "FAIL: ${app} -> db-password is NOT a Key Vault reference (plain secret or missing)"
    FAIL=1
  else
    echo "PASS: ${app} -> db-password -> ${KV_URL}"
  fi
done

echo "---"
if [ "$FAIL" -eq 0 ]; then
  echo "All Odoo apps use Key Vault-backed db-password."
else
  echo "SECRET DRIFT DETECTED. Fix: az containerapp secret set -n <app> -g ${RG} --secrets 'db-password=keyvaultref:<kv-url>,identityref:system'"
fi

exit $FAIL
