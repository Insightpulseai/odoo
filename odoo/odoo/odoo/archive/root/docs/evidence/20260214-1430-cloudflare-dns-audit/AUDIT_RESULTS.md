# Cloudflare DNS Proxy Audit Results

**Date**: 2026-02-14 14:30 UTC
**Domain**: insightpulseai.com
**Method**: DNS lookup + HTTP header analysis
**SSOT**: infra/dns/subdomain-registry.yaml

## Executive Summary

**Finding**: `superset.insightpulseai.com` is DNS-only (not proxied) despite SSOT requirement for proxy.

**Security Impact**:
- Origin IP exposed (178.128.112.214)
- No DDoS protection
- No WAF protection
- Direct attack surface to Apache Superset BI on port 8088

**Recommendation**: Enable Cloudflare proxy immediately.

---

## DNS Lookup Results (Actual State)

### Proxied Records (Cloudflare Edge IPs)

| Subdomain | DNS Response | Status |
|-----------|--------------|--------|
| erp.insightpulseai.com | 104.21.56.237, 172.67.137.254 | ✅ Proxied |
| n8n.insightpulseai.com | 104.21.56.237, 172.67.137.254 | ✅ Proxied |
| www.insightpulseai.com | 104.21.56.237, 172.67.137.254 | ✅ Proxied |
| mcp.insightpulseai.com | 104.21.56.237, 172.67.137.254 | ✅ Proxied |

**Analysis**: These records correctly return Cloudflare edge IPs (104.21.x.x, 172.67.x.x), indicating proxy is enabled.

### DNS-only Records (Origin IP or Empty)

| Subdomain | DNS Response | Expected | Status |
|-----------|--------------|----------|--------|
| **superset.insightpulseai.com** | **178.128.112.214** | **Proxied** | **❌ NON-COMPLIANT** |
| ocr.insightpulseai.com | (empty) | Proxied | ⚠️ Not configured |
| auth.insightpulseai.com | (empty) | Proxied | ⚠️ Not configured |

**Critical Finding**: `superset.insightpulseai.com` returns the origin IP (178.128.112.214) instead of Cloudflare edge IPs.

### HTTP Headers Test (superset.insightpulseai.com)

```
HTTP/2 200
server: nginx/1.24.0 (Ubuntu)
date: Sat, 14 Feb 2026 11:06:32 GMT
content-type: text/html; charset=utf-8
```

**Missing Headers**:
- ❌ `cf-ray` (Cloudflare trace ID)
- ❌ `cf-cache-status` (Cloudflare cache status)
- ❌ `server: cloudflare` (Cloudflare server identification)

**Present Header**:
- ✅ `server: nginx/1.24.0 (Ubuntu)` (Direct origin server response)

**Conclusion**: HTTP headers confirm direct connection to origin server, not routed through Cloudflare proxy.

---

## SSOT Compliance Matrix

### Production Subdomains (Expected: Proxied)

| Subdomain | SSOT Config | Actual State | Compliance | Action |
|-----------|-------------|--------------|------------|--------|
| erp | `cloudflare_proxied: true` | Proxied ✅ | ✅ Compliant | None |
| n8n | `cloudflare_proxied: true` | Proxied ✅ | ✅ Compliant | None |
| ocr | `cloudflare_proxied: true` | Not configured ⚠️ | ⚠️ Needs setup | Configure DNS |
| auth | `cloudflare_proxied: true` | Not configured ⚠️ | ⚠️ Needs setup | Configure DNS |
| **superset** | **`cloudflare_proxied: true`** | **DNS-only ❌** | **❌ NON-COMPLIANT** | **Enable proxy** |
| www | `cloudflare_proxied: true` | Proxied ✅ | ✅ Compliant | None |
| api | `cloudflare_proxied: true` | Not configured (planned) | ⏳ Planned | Future setup |
| mcp | `cloudflare_proxied: true` | Proxied ✅ | ✅ Compliant | None |

**Compliance Rate**: 4/8 (50%) - excluding planned records

**Critical Issues**: 1 (superset)
**Warnings**: 2 (ocr, auth not configured)

---

## Security Risk Analysis

### superset.insightpulseai.com Risk Profile

**Asset**: Apache Superset BI (port 8088)
**Data Sensitivity**: HIGH (business intelligence, analytics, dashboards)
**Current Exposure**: Direct origin IP exposed (178.128.112.214:8088)

**Risks**:

1. **DDoS Attack** (Severity: HIGH)
   - No Cloudflare DDoS protection
   - Direct attack on origin server port 8088
   - Service disruption risk

2. **Origin IP Exposure** (Severity: MEDIUM)
   - Attackers can bypass Cloudflare entirely
   - Direct access to origin server
   - Potential for targeted attacks

3. **No WAF Protection** (Severity: MEDIUM)
   - No Web Application Firewall rules
   - No SQL injection protection
   - No XSS protection

4. **No Rate Limiting** (Severity: MEDIUM)
   - No request throttling
   - Brute force attack risk
   - API abuse risk

5. **No Caching** (Severity: LOW)
   - No edge caching
   - Higher origin server load
   - Slower response times for users

**Total Risk Score**: 8/10 (HIGH)

---

## Recommended Actions

### Immediate (Manual - Within 1 Hour)

1. **Enable Proxy for superset.insightpulseai.com**
   - Navigate to Cloudflare Dashboard > DNS > Records
   - Find: superset.insightpulseai.com (A record, 178.128.112.214)
   - Click grey cloud icon → Toggle to orange cloud (Proxied)
   - Verify change propagates (30-60 seconds)

2. **Verify Change**
   ```bash
   # DNS should now show Cloudflare IPs
   dig superset.insightpulseai.com +short

   # HTTP headers should show cf-ray
   curl -I https://superset.insightpulseai.com/health | grep -i cf-
   ```

3. **Test Service Accessibility**
   - Access: https://superset.insightpulseai.com
   - Verify login page loads
   - Test authentication
   - Verify dashboards accessible

### Short-term (Automated - Within 1 Week)

1. **Fix Cloudflare API Token**
   - Generate new API token with DNS edit permissions
   - Update environment: `TF_VAR_cloudflare_api_token`
   - Test automated scripts

2. **Configure Missing Subdomains**
   - ocr.insightpulseai.com
   - auth.insightpulseai.com
   - Verify proxy status

3. **Add CI/CD Audit**
   - Weekly audit via `.github/workflows/dns-sync-check.yml`
   - Alert on non-compliance
   - Auto-generate compliance report

### Long-term (Infrastructure - Within 1 Month)

1. **Terraform DNS Management**
   - Migrate all DNS to Terraform (if not already)
   - Enforce SSOT via IaC
   - Prevent manual drift

2. **Monitoring & Alerting**
   - Monitor proxy status changes
   - Alert on DNS record modifications
   - Track compliance metrics

3. **Security Hardening**
   - Configure WAF rules for Superset
   - Enable rate limiting
   - Configure cache rules

---

## Evidence Files

All evidence saved to: `docs/evidence/20260214-1430-cloudflare-dns-audit/`

- `dns-lookup-before.txt` - DNS response for superset (origin IP)
- `curl-test-before.txt` - HTTP headers (no cf-ray header)
- `all-dns-lookups.txt` - DNS responses for all subdomains
- `MANUAL_PROCEDURE.md` - Step-by-step manual remediation
- `SSOT_COMPLIANCE.md` - SSOT compliance analysis
- `AUDIT_RESULTS.md` - This file

---

## Next Steps

1. **User Action Required**: Enable proxy for superset.insightpulseai.com via Cloudflare UI
2. **Verification**: Run DNS and HTTP tests after change
3. **Documentation**: Save screenshots and test results to evidence directory
4. **Commit**: Add evidence to git and commit changes

**Estimated Time**: 5-10 minutes for manual change + verification
**Risk Level**: LOW (simple configuration change, rollback available)
**Impact**: HIGH (security posture improvement, DDoS protection)
