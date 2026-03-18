# Examples — azure-troubleshooting-ops

## Example 1: Container restart loop due to Key Vault access denied

**Input**: Alert — `ipai-odoo-dev-web` restarting every 30 seconds

**Output**:
- Service: `ipai-odoo-dev-web` (Microsoft.App/containerApps)
- Symptom: container exits with code 1, restarts every 30 seconds
- Timeline: started 2026-03-17T10:15:00Z, after Key Vault access policy change at 10:12
- Container logs: `ERROR: Failed to read secret 'odoo-db-password' from Key Vault: 403 Forbidden`
- Root cause: Managed identity `ipai-odoo-dev-web` lost `Key Vault Secrets User` role after RBAC policy update
- Evidence: `az role assignment list --assignee <identity-principal-id> --scope /subscriptions/.../kv-ipai-dev` shows no matching role
- Remediation: Reassign `Key Vault Secrets User` role to the Container App managed identity
- Escalation: not needed — root cause identified on check 3

## Example 2: DNS resolution failure after Front Door change

**Input**: Users report `erp.insightpulseai.com` returning DNS_PROBE_FINISHED_NXDOMAIN

**Output**:
- Service: `ipai-odoo-dev-web` via Front Door `ipai-fd-dev`
- Symptom: DNS resolution failure for `erp.insightpulseai.com`
- Timeline: started 2026-03-17T14:00:00Z, after Cloudflare DNS update at 13:55
- DNS check: `dig erp.insightpulseai.com` returns NXDOMAIN
- Root cause: CNAME record for `erp` was accidentally deleted during Cloudflare zone edit
- Evidence: Cloudflare audit log shows CNAME deletion at 13:55; `dig` output confirms NXDOMAIN
- Remediation: Recreate CNAME `erp.insightpulseai.com` pointing to `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net`
- Escalation: not needed

## Example 3: Escalation — intermittent 502 with no clear root cause

**Input**: Intermittent 502 errors on `mcp.insightpulseai.com`, no recent deployments

**Output**:
- Service: `ipai-mcp-dev` (Microsoft.App/containerApps)
- Symptom: intermittent HTTP 502, approximately 15% of requests
- Timeline: gradual onset over last 6 hours, no recent deployments or config changes
- Container logs: no crash loops, no errors — application appears healthy
- DNS check: resolves correctly — PASS
- Key Vault: accessible — PASS
- TLS: valid certificate — PASS
- App Insights: 502 errors correlate with Front Door origin timeout events
- Root cause: ESCALATION REQUIRED — 3 checks completed without definitive cause
- Hypothesis: Front Door health probe timeout may be too aggressive, or origin is intermittently slow
- Evidence: App Insights query showing 502 distribution, Front Door access logs with timeout events
- Escalation: YES — requires Front Door team review of origin timeout settings and health probe interval
