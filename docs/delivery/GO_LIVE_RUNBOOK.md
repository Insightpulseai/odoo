# Go-Live Runbook — Odoo on Azure Production

## Gate Sequence (verified 2026-03-20)

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| CP-1 | MFA readiness for admin identities | **Partial** | `admin@` enrolled; `emergency-admin@` pending interactive enrollment |
| CP-2 | Azure Files + ACA mount proof | **Done** | Previously verified |
| CP-3 | Front Door / WAF validation | **Partial** | AFD live (`x-azure-ref` confirmed on `erp.insightpulseai.com`); WAF policy needs portal verification (resource not CLI-visible) |
| CP-6 | Odoo DB tenancy hardening (dbfilter, list_db, admin_passwd) | **Open** | Not yet applied |
| CP-7 | Full production smoke run | **Open** | Pending CP-6 |
| CP-8 | Evidence pack assembly | **Open** | Pending CP-7 |

### Identity Baseline (solo-team model)

| Identity | Role | Entra Role | Subscription RBAC | MFA |
| --- | --- | --- | --- | --- |
| `admin@insightpulseai.com` | Primary admin | Global Administrator | Contributor | Enrolled |
| `emergency-admin@insightpulseai.com` | Break-glass | Global Administrator | Contributor | **Pending** |
| `ceo@insightpulseai.com` (Jake ext) | Operator | Owner (inherited) | Owner | External IdP |

### Remaining CP-1 Actions

- [ ] `emergency-admin@insightpulseai.com` completes MFA at `https://aka.ms/mfasetup`
- [ ] Enable registration campaign in Entra portal (no exclusions or exclude only emergency-admin)
- [ ] Move automation to workload identities (mandatory MFA Phase 2)

## Prerequisites

```bash
export SUBSCRIPTION_NAME="Azure subscription 1"
export RG="rg-ipai-dev"
export AFD_RG="rg-ipai-dev"
export KV="ipai-odoo-dev-kv"
export ACA_WEB="ipai-odoo-dev-web"
export ACA_WORKER="ipai-odoo-dev-worker"
export ACA_CRON="ipai-odoo-dev-cron"
export AFD_PROFILE="ipai-fd-dev"
export PROD_URL="https://erp.insightpulseai.com"
export DBFILTER="^odoo$"
```

```bash
az login
az account set --subscription "$SUBSCRIPTION_NAME"
```

---

## CP-1: MFA Readiness

### Audit current admin auth methods

```bash
export ADMIN_1="admin@insightpulseai.com"
export ADMIN_2="emergency-admin@insightpulseai.com"
GRAPH_TOKEN="$(az account get-access-token --resource-type ms-graph --query accessToken -o tsv)"

for U in "$ADMIN_1" "$ADMIN_2"; do
  echo "=== $U ==="
  curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
    "https://graph.microsoft.com/v1.0/users/$U/authentication/methods" | jq .
done
```

### Enable registration campaign

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $GRAPH_TOKEN" \
  -H "Content-Type: application/json" \
  "https://graph.microsoft.com/v1.0/policies/authenticationmethodspolicy" \
  -d '{"registrationEnforcement":{"authenticationMethodsRegistrationCampaign":{"state":"enabled","snoozeDurationInDays":1,"enforceRegistrationAfterAllowedSnoozes":true}}}'
```

**Note**: Final MFA enrollment requires interactive proof-of-possession. Automation path: move to workload identities for non-human access.

---

## CP-3: Front Door / WAF Validation

### Inspect current state

```bash
az extension add --name front-door --upgrade
az afd security-policy list --resource-group "$AFD_RG" --profile-name "$AFD_PROFILE" --output jsonc
```

### Validate live edge path

```bash
curl -Ik "$PROD_URL" | sed -n '1,40p'
curl -s "$PROD_URL" -o /dev/null -D - | grep -Ei 'x-azure-ref|x-cache|server|via'
```

---

## CP-6: Odoo DB Tenancy Hardening

### Generate and store admin password

```bash
export ODOO_ADMIN_PASSWD="$(python3 -c 'import base64,os;print(base64.b64encode(os.urandom(24)).decode())')"
az keyvault secret set --vault-name "$KV" --name "odoo-admin-passwd" --value "$ODOO_ADMIN_PASSWD"
```

### Push to ACA as Key Vault-backed secret

```bash
for APP in "$ACA_WEB" "$ACA_WORKER" "$ACA_CRON"; do
  az containerapp secret set \
    --resource-group "$RG" --name "$APP" \
    --secrets "odoo-admin-passwd=keyvaultref:https://${KV}.vault.azure.net/secrets/odoo-admin-passwd,identityref:system"
done
```

### Set tenancy env vars (creates new revision)

```bash
for APP in "$ACA_WEB" "$ACA_WORKER" "$ACA_CRON"; do
  az containerapp update \
    --resource-group "$RG" --name "$APP" \
    --set-env-vars \
      ODOO_DBFILTER="$DBFILTER" \
      ODOO_LIST_DB="False" \
      ODOO_ADMIN_PASSWD="secretref:odoo-admin-passwd"
done
```

---

## CP-7: Production Smoke Test

```bash
ODOO_BASE_URL="$PROD_URL" bash scripts/odoo/smoke_test.sh
```

### Quick health checks

```bash
curl -s -o /dev/null -w '%{http_code}\n' "$PROD_URL/web/health"
curl -s -o /dev/null -w '%{http_code}\n' "$PROD_URL/web/login"
```

---

## CP-8: Evidence Pack

```bash
export EVIDENCE_DIR="docs/delivery/evidence/poc-pack/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$EVIDENCE_DIR"
```

### Capture CP-3 evidence

```bash
az afd security-policy list --resource-group "$AFD_RG" --profile-name "$AFD_PROFILE" --output json > "$EVIDENCE_DIR/afd-security-policies.json"
curl -Ik "$PROD_URL" > "$EVIDENCE_DIR/prod-head.txt"
```

### Capture CP-6 evidence

```bash
for APP in "$ACA_WEB" "$ACA_WORKER" "$ACA_CRON"; do
  az containerapp show --resource-group "$RG" --name "$APP" --output json > "$EVIDENCE_DIR/${APP}.json"
done
az keyvault secret show --vault-name "$KV" --name "odoo-admin-passwd" \
  --query "{id:id,name:name,attributes:attributes}" --output json > "$EVIDENCE_DIR/odoo-admin-passwd-metadata.json"
```

### Capture smoke results

```bash
ODOO_BASE_URL="$PROD_URL" bash scripts/odoo/smoke_test.sh | tee "$EVIDENCE_DIR/smoke-test.txt"
```

### Pack

```bash
tar -czf "$EVIDENCE_DIR.tar.gz" -C "$(dirname "$EVIDENCE_DIR")" "$(basename "$EVIDENCE_DIR")"
```

---

## Rollback

### ACA config rollback

```bash
for APP in "$ACA_WEB" "$ACA_WORKER" "$ACA_CRON"; do
  az containerapp update --resource-group "$RG" --name "$APP" \
    --set-env-vars ODOO_DBFILTER="<previous>" ODOO_LIST_DB="<previous>" ODOO_ADMIN_PASSWD="secretref:odoo-admin-passwd"
done
```

### WAF rollback (Detection mode)

```bash
az network front-door waf-policy update --resource-group "$AFD_RG" --name "$WAF_POLICY" --mode Detection
```

---

## Go/No-Go

Do NOT flip to GO until:

- [x] CP-1a: `admin@insightpulseai.com` MFA enrolled + Global Admin + Contributor
- [ ] CP-1b: `emergency-admin@insightpulseai.com` MFA enrolled (interactive)
- [x] CP-2: Azure Files + ACA mount proof
- [x] CP-3a: AFD live on `erp.insightpulseai.com` (x-azure-ref confirmed)
- [ ] CP-3b: WAF policy bound and validated (portal verification needed)
- [ ] CP-6: dbfilter, list_db=False, strong admin_passwd all active
- [ ] CP-7: Smoke test passes
- [ ] CP-8: Evidence pack committed
