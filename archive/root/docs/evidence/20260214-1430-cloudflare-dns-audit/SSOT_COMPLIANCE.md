# DNS SSOT Compliance Analysis

**Date**: 2026-02-14
**SSOT Source**: `infra/dns/subdomain-registry.yaml`
**Domain**: insightpulseai.com

## Expected Configuration (from SSOT)

### Production Subdomains (cloudflare_proxied: true)

| Subdomain | Type | Service | Port | Health Check | Status |
|-----------|------|---------|------|--------------|--------|
| erp | A | odoo_ce_19 | 8069 | /web/login | active |
| n8n | A | n8n_workflow_automation | 5678 | /healthz | active |
| ocr | A | paddleocr_microservice | 8080 | /health | active |
| auth | A | authentication_service | 3000 | /.well-known/openid-configuration | active |
| **superset** | **A** | **apache_superset_bi** | **8088** | **/health** | **active** |
| www | A | website_redirect | 80 | / | active |
| api | A | api_gateway | 8000 | /api/health | planned |
| mcp | CNAME | mcp_gateway | - | /healthz | active |

**Critical Finding**: `superset` is marked as `cloudflare_proxied: true` in SSOT but is currently DNS-only in Cloudflare.

### Staging Subdomains (cloudflare_proxied: true)

| Subdomain | Type | Service | Port | Status |
|-----------|------|---------|------|--------|
| stage-erp | A | odoo_ce_19_staging | 8069 | active |
| stage-api | A | api_gateway_staging | 8000 | active |
| stage-auth | A | authentication_service_staging | 3000 | active |
| stage-mcp | A | mcp_gateway_staging | 3000 | active |
| stage-n8n | A | n8n_workflow_automation_staging | 5678 | active |
| stage-superset | A | apache_superset_bi_staging | 8088 | active |

### Staging Subdomains (cloudflare_proxied: false)

| Subdomain | Type | Service | Port | Reason |
|-----------|------|---------|------|--------|
| stage-ocr | A | paddleocr_microservice_staging | 8080 | Direct origin access for debugging |

**Note**: `stage-ocr` is intentionally DNS-only per SSOT configuration.

## Compliance Check

### Proxied Records (Expected: 13 total)

**Production (7)**:
- [ ] erp.insightpulseai.com
- [ ] n8n.insightpulseai.com
- [ ] ocr.insightpulseai.com
- [ ] auth.insightpulseai.com
- [ ] ⚠️ superset.insightpulseai.com (NON-COMPLIANT: Currently DNS-only)
- [ ] www.insightpulseai.com
- [ ] mcp.insightpulseai.com (CNAME)

**Staging (6)**:
- [ ] stage-erp.insightpulseai.com
- [ ] stage-api.insightpulseai.com
- [ ] stage-auth.insightpulseai.com
- [ ] stage-mcp.insightpulseai.com
- [ ] stage-n8n.insightpulseai.com
- [ ] stage-superset.insightpulseai.com

### DNS-only Records (Expected: 1 total)

**Staging (1)**:
- [ ] stage-ocr.insightpulseai.com (COMPLIANT: Intentionally DNS-only)

### Mail Records (Should remain DNS-only)
- [ ] MX records (mail routing - do NOT proxy)
- [ ] SPF TXT records (mail authentication - do NOT proxy)
- [ ] DKIM TXT records (mail signing - do NOT proxy)

## Non-Compliance Issue

### Issue #1: superset.insightpulseai.com Not Proxied

**SSOT Requirement**:
```yaml
- name: superset
  type: A
  service: apache_superset_bi
  port: 8088
  health_check: /health
  owner_system: "Apache Superset BI"
  cloudflare_proxied: true  # ← SSOT says TRUE
  tls_mode: "Full (strict)"
  status: active
```

**Current State**: DNS-only (grey cloud icon in Cloudflare)

**Impact**:
- Origin IP exposed (178.128.112.214)
- No DDoS protection
- No WAF protection
- No rate limiting
- Direct attack surface to origin server

**Security Implications**:
- **High**: Superset contains sensitive BI data and analytics
- **High**: Direct access to origin port 8088
- **Medium**: No Cloudflare security features active

**Remediation**: Enable proxy (orange cloud) in Cloudflare UI

## Verification After Remediation

### DNS Lookup Test

**Before (DNS-only)**:
```bash
dig superset.insightpulseai.com +short
178.128.112.214  # Origin IP exposed
```

**After (Proxied)**:
```bash
dig superset.insightpulseai.com +short
104.21.x.x       # Cloudflare edge IP
172.67.x.x       # Cloudflare edge IP (secondary)
```

### HTTP Headers Test

**Before (DNS-only)**:
```bash
curl -I https://superset.insightpulseai.com/health
# No cf-ray header
```

**After (Proxied)**:
```bash
curl -I https://superset.insightpulseai.com/health
HTTP/2 200
server: cloudflare
cf-ray: xxxxxxxxxxxxx-SIN  # ← Cloudflare trace ID present
cf-cache-status: DYNAMIC
```

## Enforcement Strategy

### Immediate (Manual)
1. Enable proxy for superset.insightpulseai.com via Cloudflare UI
2. Verify DNS propagation (30-60 seconds)
3. Test service accessibility
4. Document evidence in this directory

### Short-term (Automated)
1. Fix Cloudflare API token in environment
2. Run `./scripts/cloudflare-dns-audit.sh` to verify compliance
3. Add to CI pipeline (weekly audit)

### Long-term (Infrastructure as Code)
1. Migrate DNS to Terraform (if not already)
2. Enforce SSOT via `terraform plan` / `terraform apply`
3. Add pre-commit hook to validate SSOT changes
4. Add CI workflow to detect drift between Cloudflare and SSOT

## Related Files

- **SSOT**: `infra/dns/subdomain-registry.yaml`
- **Terraform Config**: `infra/cloudflare/envs/prod/main.tf`
- **DNS Generator**: `scripts/generate-dns-artifacts.sh`
- **Audit Script**: `scripts/cloudflare-dns-audit.sh`
- **Proxy Enabler**: `scripts/cloudflare-enable-proxy.sh`
- **CI Workflow**: `.github/workflows/dns-sync-check.yml`

## Timeline

- **2026-02-14 14:30**: Issue identified (superset not proxied)
- **2026-02-14 14:35**: Manual procedure documented
- **2026-02-14 14:40**: Awaiting manual remediation
- **2026-02-14 14:45**: (Expected) Verification complete
- **2026-02-14 15:00**: (Expected) Evidence committed to repo
