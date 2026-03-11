# Cloudflare DNS Proxy Audit - Evidence Package

**Date**: 2026-02-14 14:30 UTC
**Scope**: DNS proxy compliance audit for insightpulseai.com
**Outcome**: Identified non-compliant record (superset subdomain)

## Quick Summary

**Finding**: `superset.insightpulseai.com` is DNS-only (not proxied) despite SSOT requirement.

**Evidence**:
- DNS lookup returns origin IP (178.128.112.214) instead of Cloudflare edge IPs
- HTTP response lacks `cf-ray` header (Cloudflare trace ID)
- SSOT requires `cloudflare_proxied: true` for superset subdomain

**Action**: Enable Cloudflare proxy via UI (manual procedure provided)

**Security Impact**: HIGH - Origin IP exposed, no DDoS/WAF protection for BI application

---

## Files in This Package

### Audit Documentation
1. **`README.md`** (this file) - Evidence package overview
2. **`AUDIT_RESULTS.md`** - Complete audit findings and risk analysis
3. **`SSOT_COMPLIANCE.md`** - SSOT compliance check against subdomain-registry.yaml
4. **`MANUAL_PROCEDURE.md`** - Step-by-step manual remediation procedure

### Evidence Data
5. **`dns-lookup-before.txt`** - DNS query result showing origin IP (178.128.112.214)
6. **`curl-test-before.txt`** - HTTP headers showing direct origin connection (no cf-ray)
7. **`all-dns-lookups.txt`** - DNS queries for all production subdomains (comparison)

### Scripts (Reference)
- `../../scripts/cloudflare-dns-audit.sh` - Automated audit script (requires API token)
- `../../scripts/cloudflare-enable-proxy.sh` - Automated proxy enablement (requires API token)

---

## Key Findings

### Compliant Records (Proxied)
✅ erp.insightpulseai.com (104.21.56.237, 172.67.137.254)
✅ n8n.insightpulseai.com (104.21.56.237, 172.67.137.254)
✅ www.insightpulseai.com (104.21.56.237, 172.67.137.254)
✅ mcp.insightpulseai.com (104.21.56.237, 172.67.137.254)

### Non-Compliant Records
❌ **superset.insightpulseai.com** (178.128.112.214) - **SHOULD BE PROXIED**

### Not Configured (Warnings)
⚠️ ocr.insightpulseai.com (empty DNS response)
⚠️ auth.insightpulseai.com (empty DNS response)

---

## Remediation Status

### Immediate Actions
- [ ] Enable proxy for superset.insightpulseai.com via Cloudflare UI
- [ ] Verify DNS propagation (dig command)
- [ ] Test HTTP headers for cf-ray presence
- [ ] Save verification evidence (dns-lookup-after.txt, curl-test-after.txt)

### Short-term Actions
- [ ] Fix Cloudflare API token for automation
- [ ] Configure missing subdomains (ocr, auth)
- [ ] Add weekly CI audit workflow

### Long-term Actions
- [ ] Migrate DNS to Terraform (if not already)
- [ ] Configure WAF rules for Superset
- [ ] Enable rate limiting and cache rules

---

## How to Use This Evidence

### For Manual Remediation
1. Read `MANUAL_PROCEDURE.md` for step-by-step instructions
2. Follow Cloudflare UI steps to enable proxy
3. Run verification commands from MANUAL_PROCEDURE.md
4. Save verification results to this directory

### For Automated Remediation (Future)
1. Fix Cloudflare API token in environment
2. Run: `./scripts/cloudflare-enable-proxy.sh superset`
3. Script will verify and save evidence automatically

### For Compliance Reporting
1. Review `SSOT_COMPLIANCE.md` for full compliance matrix
2. Review `AUDIT_RESULTS.md` for detailed findings
3. Use evidence files for audit trail

---

## Verification Commands

After enabling proxy, run these commands to verify:

```bash
# 1. DNS lookup (should show Cloudflare IPs, not origin IP)
dig superset.insightpulseai.com +short > dns-lookup-after.txt

# 2. HTTP headers (should show cf-ray header)
curl -I https://superset.insightpulseai.com/health > curl-test-after.txt 2>&1

# 3. Compare before/after
echo "=== BEFORE ==="
cat dns-lookup-before.txt
echo ""
echo "=== AFTER ==="
cat dns-lookup-after.txt
```

**Expected Results**:
- **Before**: `178.128.112.214` (origin IP)
- **After**: `104.21.x.x` and `172.67.x.x` (Cloudflare edge IPs)
- **Headers**: `cf-ray: xxxxxxxxxxxxx` header present

---

## Related Documentation

- **SSOT**: `../../infra/dns/subdomain-registry.yaml`
- **DNS Generator**: `../../scripts/generate-dns-artifacts.sh`
- **CI Workflow**: `../../.github/workflows/dns-sync-check.yml`
- **Terraform Config**: `../../infra/cloudflare/envs/prod/main.tf`

---

## Commit Message (Suggested)

```
docs(security): cloudflare dns proxy audit - superset non-compliance

Audit findings:
- superset.insightpulseai.com is DNS-only (should be proxied per SSOT)
- Origin IP exposed (178.128.112.214)
- No DDoS/WAF protection active
- Security risk: HIGH

Evidence:
- DNS lookup shows origin IP instead of Cloudflare edge IPs
- HTTP headers lack cf-ray trace ID
- SSOT requires cloudflare_proxied: true

Action: Manual proxy enablement required via Cloudflare UI

Evidence-Dir: docs/evidence/20260214-1430-cloudflare-dns-audit/
```

---

**Audit Conducted By**: Claude Code Agent (Automated)
**Review Required**: Yes (manual verification after remediation)
**Priority**: HIGH (security exposure)
