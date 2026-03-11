# Cloudflare Security Hardening Spec Bundle

**Purpose**: Secure MCP agent ingress, n8n automation, and Superset BI endpoints via Cloudflare WAF

**Status**: Phase 1 Complete (DNS Proxying), Phase 2 Next (Terraform Apply)

**Priority**: P0 (Critical Security Fix)

---

## Documents

| File | Purpose |
|------|---------|
| `prd.md` | Product Requirements Document (WHAT & WHY) |
| `firewall-rules.json` | Declarative firewall rule specification (HOW) |
| `README.md` | This file (navigation and quick start) |

---

## Quick Start

### Phase 1: DNS Proxying (COMPLETE ✅)

**What was done**:
- Updated `infra/dns/subdomain-registry.yaml` (SSOT)
- Set `cloudflare_proxied: true` for mcp, n8n, superset (production + staging)
- Regenerated Terraform artifacts
- Committed to `feat/infra-dns-ssot` branch

**Evidence**: Commit b2b74b22

### Phase 2: Terraform Apply (NEXT ⏳)

**Execute DNS changes**:

```bash
cd infra/cloudflare/envs/prod
terraform plan  # Review 6 DNS record updates
terraform apply # Apply proxying changes
```

**Validate**:

```bash
# Should return Cloudflare IPs, not 178.128.112.214
dig mcp.insightpulseai.com +short
dig n8n.insightpulseai.com +short
dig superset.insightpulseai.com +short
```

**Expected Output**: Cloudflare IP ranges (e.g., `104.21.x.x`, `172.67.x.x`)

### Phase 3: Firewall Rules Implementation (PLANNED 🔜)

**Prerequisite**: Phase 2 complete and validated

**Steps**:

1. **Create Terraform module**: `infra/cloudflare/modules/firewall-rules/`
2. **Convert JSON spec to Terraform**: Use `firewall-rules.json` as source
3. **Deploy in log-only mode**: Test for 7 days, monitor for false positives
4. **Enable blocking incrementally**: Follow 5-week rollout plan in PRD
5. **Enable managed rulesets**: OWASP Core + Cloudflare Managed

**See**: `prd.md` Section "Implementation Plan - Phase 3"

### Phase 4: Monitoring & Alerting (PLANNED 🔜)

**Configure observability**:

1. Cloudflare Analytics dashboard with firewall metrics
2. Alerting rules (>100 blocks/hour, false positive rate >1%)
3. Weekly security report (top blocked IPs, attack patterns)

---

## Firewall Rules Summary

**Total Rules**: 12 firewall rules + 2 managed rulesets + 3 rate limiting rules

### Critical Rules (Must Deploy First)

| Priority | Rule | Action | Purpose |
|----------|------|--------|---------|
| 1 | mcp-authentication-required | block | Prevent unauthorized MCP tool calls |
| 8 | superset-sql-injection-patterns | block | Prevent SQL injection attacks |
| 11 | health-check-bypass | allow | Monitoring uptime |
| 12 | common-exploit-patterns | block | Path traversal, XSS, Log4Shell |

### Optional Rules (Deploy After Testing)

| Priority | Rule | Action | Purpose | Risk |
|----------|------|--------|---------|------|
| 3 | mcp-figma-github-allowlist | allow | Whitelist known sources | Requires IP ranges |
| 5 | n8n-authentication-required | block | Session cookie enforcement | High false positive risk |
| 7 | superset-geo-restriction | block | Geo-fencing | May block remote users |
| 9 | staging-ip-restriction | block | Staging access control | Requires office/VPN IPs |

---

## Security Impact

**Before** (DNS-only):
- ❌ Direct IP exposure (`178.128.112.214`)
- ❌ No WAF protection
- ❌ Unlimited requests per IP
- ❌ No bot mitigation
- ❌ Vulnerable to credential stuffing, SQL injection, automation takeover

**After** (Cloudflare proxied + WAF):
- ✅ Origin IP concealed (Cloudflare IPs)
- ✅ OWASP Core Ruleset (SQLi, XSS, RCE protection)
- ✅ Rate limiting (per IP, per user, global)
- ✅ Bot mitigation (crawler/scraper blocking)
- ✅ Authentication enforcement (MCP, n8n)
- ✅ Geo-restrictions (optional)
- ✅ IP allowlists (optional)

---

## Terraform Implementation (TODO)

**Module Structure** (to be created):

```
infra/cloudflare/modules/firewall-rules/
├── main.tf                 # Firewall rule resources
├── variables.tf            # Rule enablement flags, thresholds
├── outputs.tf              # Rule IDs, URLs
├── README.md               # Module documentation
└── examples/
    └── production.tf       # Production usage example
```

**Usage Example**:

```hcl
module "firewall_rules" {
  source = "../../modules/firewall-rules"

  zone_id = data.cloudflare_zone.zone.id

  # Enable/disable rules via flags
  enable_mcp_auth = true
  enable_sql_injection_blocking = true
  enable_geo_restriction = false  # Optional

  # Customize thresholds
  mcp_rate_limit = 100  # req/min per IP
  n8n_rate_limit = 60
  global_rate_limit = 1000

  # IP allowlists (optional)
  mcp_allowed_ips = [
    # GitHub IP ranges
    "140.82.112.0/20",
    "143.55.64.0/20",
    # Office IPs (TBD)
  ]
}
```

---

## Validation & Testing

### DNS Proxying Validation

```bash
# Check DNS resolution (should be Cloudflare IPs)
dig mcp.insightpulseai.com +short
dig n8n.insightpulseai.com +short
dig superset.insightpulseai.com +short

# Verify TLS certificate (should be Cloudflare origin cert)
curl -I https://mcp.insightpulseai.com/healthz
curl -I https://n8n.insightpulseai.com/healthz
curl -I https://superset.insightpulseai.com/health

# Check health checks pass (200 OK)
./scripts/verify-service-health.sh
```

### Firewall Rules Validation

```bash
# Test unauthenticated MCP request (should be blocked)
curl -I https://mcp.insightpulseai.com/api/v1/status
# Expected: 403 Forbidden (if rule #1 enabled)

# Test authenticated MCP request (should succeed)
curl -H "Authorization: Bearer $MCP_TOKEN" \
  https://mcp.insightpulseai.com/api/v1/status
# Expected: 200 OK

# Test SQL injection pattern (should be blocked)
curl "https://superset.insightpulseai.com/?q=' OR 1=1"
# Expected: 403 Forbidden (if rule #8 enabled)

# Test health check bypass (should always succeed)
curl -I https://mcp.insightpulseai.com/healthz
# Expected: 200 OK (even without auth)
```

---

## Monitoring Queries

**Cloudflare GraphQL Analytics API**:

```graphql
query FirewallEvents {
  viewer {
    zones(filter: { zoneTag: $zoneId }) {
      firewallEventsAdaptive(
        filter: {
          datetime_geq: "2026-02-13T00:00:00Z"
          datetime_lt: "2026-02-14T00:00:00Z"
        }
        limit: 100
      ) {
        action
        clientIP
        clientCountryName
        ruleId
        source
        userAgent
      }
    }
  }
}
```

**Cloudflare Logs API**:

```bash
# Top blocked IPs (last 24 hours)
curl -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/firewall/events" \
  -H "X-Auth-Email: $CF_EMAIL" \
  -H "X-Auth-Key: $CF_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{
    "filter": {
      "since": "2026-02-13T00:00:00Z",
      "until": "2026-02-14T00:00:00Z",
      "action": "block"
    }
  }'
```

---

## Next Actions

### Immediate (Phase 2)

- [ ] Execute `terraform apply` to enable DNS proxying
- [ ] Validate DNS resolution returns Cloudflare IPs
- [ ] Verify health checks pass for all services
- [ ] Monitor Cloudflare Analytics for traffic patterns

### Short-term (Phase 3 - Week 1)

- [ ] Create Terraform firewall rules module
- [ ] Deploy rules in log-only mode
- [ ] Monitor for 7 days, identify false positives
- [ ] Adjust thresholds based on real traffic

### Medium-term (Phase 3 - Week 2-5)

- [ ] Enable blocking incrementally per rollout plan
- [ ] Confirm Figma and GitHub IP ranges (MCP allowlist)
- [ ] Confirm n8n cookie name (authentication rule)
- [ ] Collect office/VPN IPs (staging restriction)

### Long-term (Phase 4)

- [ ] Configure Cloudflare Analytics dashboard
- [ ] Set up alerting (>100 blocks/hour)
- [ ] Schedule weekly security reports
- [ ] Quarterly rule review and IP range updates

---

## References

- **Cloudflare Firewall Rules**: https://developers.cloudflare.com/firewall/
- **OWASP Core Ruleset**: https://coreruleset.org/
- **GitHub IP Ranges**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-githubs-ip-addresses
- **Cloudflare Analytics API**: https://developers.cloudflare.com/analytics/graphql-api/

---

**Last Updated**: 2026-02-13
**Next Review**: 2026-03-13 (30 days after Phase 2 completion)
