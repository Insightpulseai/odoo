# Production Runtime Snapshot

Last updated: 2026-02-09
Source of truth: `runtime_identifiers.json`

## Infrastructure Overview

**Consolidation:**
- Previous: 2 droplets (159.223.75.148 + 188.166.237.231)
- Current: 1 droplet (178.128.112.214)
- Consolidation date: 2026-02-09

**Domain Policy:**
- Canonical: `insightpulseai.com`
- Deprecated: `insightpulseai.net` (all services migrated)
- DNS Provider: Cloudflare (delegated from Spacesquare registrar)

## Active Services

| Service | FQDN | Type | Target | Port | Health Check | Status |
|---------|------|------|--------|------|--------------|--------|
| ERP | erp.insightpulseai.com | A | 178.128.112.214 | 8069 | /web/login | ✅ Active |
| n8n | n8n.insightpulseai.com | A | 178.128.112.214 | 5678 | /healthz | ✅ Active |
| OCR | ocr.insightpulseai.com | A | 178.128.112.214 | 8080 | /health | ✅ Active |
| Auth | auth.insightpulseai.com | A | 178.128.112.214 | 3000 | /.well-known/openid-configuration | ✅ Active |
| MCP | mcp.insightpulseai.com | CNAME | pulse-hub-web-an645.ondigitalocean.app | - | /healthz | ⏳ Pending |
| Superset | superset.insightpulseai.com | CNAME | superset-nlavf.ondigitalocean.app | - | /health | ⏳ Pending |

## Deprecated Services

| Service | FQDN | Deprecated | Replacement | Actions Taken |
|---------|------|------------|-------------|---------------|
| Affine | affine.insightpulseai.com | 2026-02-09 | None | DNS removed, container stopped |

## DNS Configuration

**Authoritative Nameservers:**
```
(verified via: dig NS insightpulseai.com +short)
TBD - Run verification script to populate
```

**DNS Management:**
- Provider: Cloudflare
- Access: Terraform IaC + Cloudflare API
- Policy: All changes via code, no manual UI edits

## Runtime Environment

**Primary Droplet:** odoo-production (178.128.112.214)
- Region: SGP1 (Singapore)
- Size: 4GB RAM / 80GB Disk
- OS: Ubuntu 22.04 LTS

**Docker Containers:**
```
(verified via: ssh root@178.128.112.214 "docker ps --format table")
TBD - Actual container listing will be added after SSH access verification
```

## TLS/SSL Configuration

**Mode:** Full (strict)
- Origin certificates: Let's Encrypt
- Cloudflare proxy: Enabled for A records
- HSTS: Enabled
- TLS version: 1.2+

## Verification Commands

### DNS Verification
```bash
./scripts/verify-dns-baseline.sh
```

### Service Health Checks
```bash
./scripts/verify-service-health.sh
```

### JSON Validation
```bash
jq . docs/architecture/runtime_identifiers.json
```

### No Secrets Check
```bash
git grep -nE "CF_API_TOKEN|Authorization: Bearer|password|api_key.*sk-|BEGIN PRIVATE KEY" || echo "✅ No secrets found"
```

## Related Documentation

- Machine-readable registry: `docs/architecture/runtime_identifiers.json`
- DNS baseline script: `scripts/verify-dns-baseline.sh`
- Health check script: `scripts/verify-service-health.sh`
- Drift detection CI: `.github/workflows/dns-drift-detect.yml`
