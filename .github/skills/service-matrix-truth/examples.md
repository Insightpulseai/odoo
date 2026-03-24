# service-matrix-truth -- Worked Examples

## Example 1: Before (Gap State)

```yaml
  - id: svc_004
    name: "Auth Gateway"
    category: identity
    hosting: azure_container_apps
    edge: azure_front_door
    endpoint: "auth.insightpulseai.com"
    aca_name: ipai-auth-dev
    status: active                    # WRONG -- this is a nginx:alpine stub
    promotion_state: live             # WRONG -- not functional
    note: "Stub (nginx:alpine). Replace with Keycloak when auth requirements defined."
```

## Example 2: After (Corrected)

```yaml
  - id: svc_004
    name: "Auth Gateway"
    category: identity
    hosting: azure_container_apps
    edge: azure_front_door
    endpoint: "auth.insightpulseai.com"
    aca_name: ipai-auth-dev
    status: stub                      # Accurately reflects nginx:alpine
    promotion_state: placeholder      # Not serving real traffic
    current_image: "nginx:alpine"
    target_image: "Entra ID (no container -- decommission candidate)"
    target_date: "TBD -- pending Entra migration"
    note: "Stub (nginx:alpine). Keycloak decommission candidate. Target: Entra ID native auth."
```

## Example 3: All Stub Services to Correct

| svc_id | Name | Current Status | Corrected Status | Target |
|--------|------|---------------|-----------------|--------|
| svc_004 | Auth Gateway | active/live | stub/placeholder | Entra ID (decommission container) |
| svc_005 | MCP Coordinator | active/live | stub/placeholder | MCP gateway image |
| svc_006 | OCR Service | active/live | stub/placeholder | PaddleOCR or Azure AI Doc Intelligence |

## Example 4: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure Container Apps list revisions active image")
Result: az containerapp revision list --name <app> --resource-group <rg>
        Shows all revisions with their container image, creation date, and
        traffic weight. Active revision has traffic > 0%.

Step 2: microsoft_docs_search("Azure Resource Graph query container apps image")
Result: ARG query:
        resources
        | where type == "microsoft.app/containerapps"
        | project name, properties.template.containers[0].image
        Returns all ACA apps with their running image. Useful for bulk audit.

Step 3: microsoft_docs_search("Azure well-architected operational excellence inventory")
Result: WAF recommends: maintain accurate inventory of all workloads,
        distinguish between production and non-production, use consistent
        tagging/labeling, audit regularly against reality.
```

## Example 5: Verification Command

```bash
# Verify actual running images for all ACA apps in the runtime RG
az containerapp list \
  --resource-group rg-ipai-dev-odoo-runtime \
  --query "[].{name:name, image:properties.template.containers[0].image}" \
  --output table

# Expected output should show nginx:alpine for stub services:
# Name                  Image
# --------------------  ---------------
# ipai-odoo-dev-web     ipaiodoodevacr.azurecr.io/odoo:latest
# ipai-auth-dev         nginx:alpine    <-- STUB
# ipai-mcp-dev          nginx:alpine    <-- STUB
# ipai-ocr-dev          nginx:alpine    <-- STUB
```

## Example 6: Go-Live Checklist Service Verification Section

```markdown
## Service Inventory Verification

- [ ] Run `az containerapp list` and compare images against service-matrix.yaml
- [ ] Confirm all services with `status: active` are running their intended image
- [ ] Confirm all services with `status: stub` are excluded from SLA commitments
- [ ] Confirm no stub service is included in monitoring alert escalation
- [ ] Document any service that changed status since last review
```
